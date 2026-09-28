# ESP32-S3 SPI-NAND Acquisition & Programming Workflow

## 1. Overview & Tool Selection

When researching or recovering the **JioRouter AX6000 JIDU6801**, an external hardware flasher is required to inspect or restore the SPI-NAND flash if the bootloader becomes unbootable or corrupted.

An **Espressif ESP32-S3** (specifically the ESP32-S3-DevKitC-1) was selected because:
1. **High-Speed Hardware SPI Master:** The ESP32-S3 features dedicated SPI peripherals (`SPI2_HOST` / FSPI) capable of running at 10 MHz to 40 MHz with hardware DMA.
2. **Native USB OTG / High-Speed CDC:** The on-chip USB controller allows streaming raw flash data directly over USB CDC-ACM at high throughput, avoiding FTDI UART baud rate bottlenecks.
3. **Dual-Core 240 MHz Xtensa LX7:** Ample processing power to handle on-the-fly CRC32 calculation, frame packaging, and USB transaction scheduling without buffer underruns.

---

## 2. Existing Espressif Capabilities vs. Project Contribution

To ensure clear and honest attribution, the boundary between upstream Espressif software and project-specific work is defined below:

| Feature / Layer | Source / Attribution | Implementation Details |
|:---|:---|:---|
| **SPI-NAND Driver Architecture** | **Existing Espressif Upstream** | Component `espressif/spi_nand_flash` (v1.4.4) via ESP Component Registry. |
| **Winbond W25N02KV Chip Support** | **Existing Espressif Upstream** | `nand_winbond.c` explicitly identifies Device ID `0xAA22` (`WINBOND_DI_AA22`) and defines 2,048 blocks. |
| **USB CDC-ACM Stack** | **Existing Espressif Upstream** | `espressif/esp_tinyusb` component wrapping TinyUSB. |
| **SPI Master Peripheral Driver** | **Existing Espressif Upstream** | ESP-IDF `driver/spi_master.h` with DMA channel auto-allocation. |
| **JIDU In-Circuit Wiring Specification** | **Project Contribution** | 3.3V logic level validation, flying lead inductance mitigation ($\le 10\text{ cm}$), power isolation. |
| **Flash Unprotection Sequence** | **Project Contribution** | Identification that JIDU factory flash sets SR-1 to `0x7C` (full array locked) and implementation of `unprotect_chip()` clearing `0xA0` register. |
| **Framed CDC Protocol (`NDMP`)** | **Project Contribution** | Binary streaming protocol with magic markers, per-page CRC32, bounded retries, and error frames. |
| **Safety Region Clamping** | **Project Contribution** | Hardware boundary protection restricting writes strictly to the FIP partition (blocks 28..43 / pages 1792..2815). |
| **Host Tooling & Verification** | **Project Contribution** | Python flasher and raw NAND acquisition script with byte-exact verification. See the note below on repository contents. |

### Potential Upstream Contribution to Espressif:
Espressif's upstream `spi_nand_flash` component does not automatically clear Status Register 1 write protection bits (`BP0..BP3` in register `0xA0`) if a chip powers on with factory protection latched. Adding an explicit `spi_nand_flash_unlock()` or auto-unprotect API to `espressif/spi_nand_flash` represents a reusable upstream improvement.

---

## 3. Hardware Interconnect & Wiring

Programming the Winbond W25N02KV in-circuit requires wiring the ESP32-S3 DevKit-C to the router's WSON-8 flash footprint:

```text
ESP32-S3 DevKit-C Pin         W25N02KV WSON-8 Pin        Signal Name
────────────────────────────────────────────────────────────────────
GPIO 10                ───►   Pin 1                      /CS (Chip Select)
GPIO 13                ◄───   Pin 2                      DO / IO1 (MISO)
3.3V Output Rail       ───►   Pin 3                      /WP / IO2 (Write Protect pull-up)
GND (Common Ground)    ───►   Pin 4                      VSS (Ground Reference)
GPIO 11                ───►   Pin 5                      DI / IO0 (MOSI)
GPIO 12                ───►   Pin 6                      CLK (SPI Clock)
3.3V Output Rail       ───►   Pin 7                      /HOLD / IO3 (Hold pull-up)
3.3V Output Rail       ───►   Pin 8                      VCC (Power Supply)
```

### Critical Safety Rules:
1. **Router DC Supply Disconnected:** The router's 12V DC power brick MUST remain disconnected. Applying 12V while the programmer is attached can destroy both the programmer and the SoC.
2. **Lead Length $\le 10\text{ cm}$:** Flying leads longer than 10–12 cm introduce parasitic capacitance and inductance that cause reflection-induced bitflips at 10 MHz.
3. **Power Sequencing:** Connect GND, CS, MOSI, CLK, MISO first. Connect the 3.3V VCC line last.

---

## 4. Winbond W25N02KV Geometry & Register Behavior

* **Capacity:** 256 MiB (2 Gbit)
* **Blocks:** 2,048 Physical Eraseblocks (PEBs)
* **Pages per Block:** 64 pages
* **Page Size:** 2,048 bytes user data + 128 bytes OOB/spare area = 2,176 bytes total
* **Total Pages:** 131,072 pages

### Status Register 1 (Protection Register `0xA0`):
* **Default Power-On Value:** `0x7C` (`01111100b`)
* **Effect:** Blocks 0 to 2047 are locked against program and erase commands.
* **Unlock Procedure:**
  1. Send `0x06` (Write Enable).
  2. Send `0x1F 0xA0 0x00` (Write Status Register 1 = `0x00`).
  3. Verify reading register `0xA0` returns `0x00`.

---

## 5. Acquisition (Read) & Programming (Write) Workflow

### 5.1 Full NAND Acquisition (Read):
Host command `G` or `R + <start_page>` triggers the ESP32-S3 to stream 2176-byte pages packaged in `NDMP` binary frames:
* **Frame Header (17 bytes):** Magic `NDMP`, Version `0x01`, Status, SR-3 status, Page Number (uint32 LE), Payload Length (`2176`), CRC-32 (uint32 LE).
* **Payload (2176 bytes):** 2048 bytes data + 128 bytes OOB.
* **Integrity Guarantee:** If a page fails after 3 retries, an `NDMF` failure frame is emitted and streaming halts. No fake or placeholder data is ever generated.

### 5.2 FIP Flashing (Write & Erase):
1. **Safety Clamping:** Firmware checks that the requested erase/program addresses fall strictly within the FIP partition range:
   - Erase: Blocks 28 to 43 inclusive.
   - Program: Pages 1792 to 2815 inclusive.
   - Writes targeting any page outside this range are rejected with NAK.
2. **Execution:**
   - Host sends `E + start_page + count` $\to$ ESP32-S3 issues `0x06` (Write Enable) $\to$ `0xD8` (Block Erase).
   - Host sends `W + page_number + 2176 bytes` $\to$ ESP32-S3 issues `0x84` (Program Load) $\to$ `0x10` (Program Execute).
3. **Verification:**
   - Immediately after programming, all 1,024 pages are read back via `R + 1792` and verified byte-for-byte against the input binary.

---

## 6. Two-Device Validation Summary

The ESP32-S3 SPI-NAND hardware workflow was evaluated across two independent router units:

| Validation Step | Device A (JIDU6601) | Device B (JIDU6801) |
|:---|:---|:---|
| **NAND Detection (JEDEC ID)** | **CONFIRMED** (`EF AA 22 00`) | **CONFIRMED** (`EF AA 22 00`) |
| **Register Status Readback** | **CONFIRMED** (SR1: `0x7C`, SR2: `0x19`) | **CONFIRMED** (SR1: `0x7C`, SR2: `0x19`) |
| **NAND Acquisition (Read)** | **CONFIRMED** (Full MTD3 FIP dump) | **CONFIRMED** (Full 285 MB raw NAND dump) |
| **Array Unprotect (`0xA0` $\to$ `0x00`)**| NOT TESTED (Working router) | **CONFIRMED** (SR1 cleared to `0x00`) |
| **Block Erase (Blocks 28..43)** | NOT TESTED (Working router) | **CONFIRMED** (16 blocks erased) |
| **Page Program (Pages 1792..2815)** | NOT TESTED (Working router) | **CONFIRMED** (1,024 pages programmed) |
| **Readback & Byte Verification** | CONFIRMED for Read | **CONFIRMED** (1024/1024 pages, 0 mismatches) |
| **Post-Programming Boot** | NOT APPLICABLE (Not flashed) | **CONFIRMED** (Booted to U-Boot & OpenWrt) |
