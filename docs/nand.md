# SPI-NAND Flash Geometry & NMBM Bad Block Architecture

## 1. Physical Flash Silicon Specifications

The JioRouter AX6000 JIDU6801 uses a single **Winbond W25N02KVZEIR** Serial NAND flash memory device.

| Parameter | Specification | Hex / Decimal Value |
|:---|:---|:---|
| **Manufacturer** | Winbond Electronics | JEDEC ID: `0xEF`, Device ID: `0xAA 0x22` |
| **Part Number** | W25N02KVZEIR | 2 Gbit (256 MiB) 3.3V SPI-NAND |
| **Package** | WSON-8 (8mm × 6mm) | Surface mount with exposed ground pad |
| **Total Physical Capacity** | 256 MiB | 268,435,456 bytes user data |
| **Total Physical Eraseblocks**| 2,048 blocks | Physical Eraseblocks (PEB 0 to 2047) |
| **Eraseblock Size** | 128 KiB | `0x20000` bytes (64 pages) |
| **Pages per Block** | 64 pages | Pages 0 to 63 per eraseblock |
| **Page Data Size** | 2,048 bytes | Standard user data payload |
| **Spare / OOB Size** | 128 bytes | Out-Of-Band (OOB) spare area per page |
| **Total Page Size** | 2,176 bytes | `2048 + 128` bytes physical framing |
| **Internal On-Die ECC** | 8-bit ECC per 512 bytes | Hardware Reed-Solomon / BCH engine |

---

## 2. MediaTek NMBM (NAND Multi-Block Management)

Because raw NAND flash exhibits factory bad blocks and may develop runtime bad blocks through wear, MediaTek platforms employ **NMBM (NAND Multi-Block Management)**.

### NMBM Structure:
* **Reserved Pool:** PEB 1920 to PEB 2047 (`0x0EF80000 - 0x10000000`, 16.5 MiB) are reserved exclusively for NMBM translation tables and replacement blocks.
* **Bad Block Remapping:** When a bad eraseblock is detected in user space (PEB 0 to 1919), NMBM remaps all operations targeting that block to a healthy block allocated from the replacement pool.
* **Driver Integration:**
  - In U-Boot: Enabled via `CONFIG_MEDIATEK_NMBM`.
  - In Linux: Enabled via the `mediatek,nmbm` device tree property on the SPI flash node.
  - The upper MTD layers (`ubi`, `kernel`) operate over a continuous, virtualized block space with zero concern for physical bad block gaps.

---

## 3. Flash Protection Registers (SR-1)

The Winbond W25N02KV incorporates non-volatile and volatile Protection Bits inside Status Register 1 (`SR-1`):

* **BP0, BP1, BP2, BP3 (Bits 3..6):** Block Protection bits controlling write/erase locking.
* **TB (Bit 2):** Top/Bottom selection bit.
* **SRP0 / WP-E (Bit 7):** Status Register Protect bit.

### Hardware Protection Behavior:
During factory programming, vendor firmware often sets `SR-1` to `0x7C` (locking blocks from write/erase operations). To program the flash via an external SPI flasher (e.g. ESP32-S3), the protection bits must be cleared by issuing:
```text
Write Enable (0x06) -> Write Status Register 1 (0x1F 0xA0 0x00)
```
In normal OpenWrt operation, the Linux MTD SPI-NAND driver handles register unprotection automatically during initialization.
