# Boot Process & Execution Chain

## 1. System Boot Stages Overview

The JioRouter AX6000 JIDU6801 executes a multi-stage ARMv8 boot sequence based on ARM Trusted Board Boot Requirements (TBBR):

```mermaid
sequenceDiagram
    participant ROM as MT7986A Mask BootROM
    participant BL2 as TF-A BL2 (SRAM)
    participant BL31 as TF-A BL31 (EL3 DRAM)
    participant BL33 as U-Boot 2023.04 (EL2 DRAM)
    participant Linux as OpenWrt Kernel (EL1 DRAM)

    ROM->>BL2: Read PEB 0 from SPI-NAND; Verify GFH Header
    Note over BL2: Executes in 256KB on-chip SRAM<br/>Initializes DDR4 DRAM & NMBM Driver
    BL2->>BL31: Read FIP @ 0x380000; Load BL31 to 0x43000000
    BL2->>BL33: Load U-Boot binary to 0x41E00000
    BL2->>BL31: Issue SMC to enter EL3 Secure Monitor
    BL31->>BL33: Drop Exception Level to EL2; Jump to U-Boot
    Note over BL33: Serial Console Active @ 115200 8N1<br/>Check Dual-Boot Environment & TFTP
    BL33->>Linux: Load FIT Image to 0x46000000; Jump to Kernel
```

---

## 2. Boot Stage Technical Details

### Stage 1: Mask BootROM (Silicon Hardcoded)
* Located in internal read-only memory (`0x00000000 - 0x0001ffff`).
* Initializes the primary SPI controller and reads the Golden Flash Header (GFH Type 3) from Physical Eraseblock 0 (Page 1) of the SPI-NAND flash.
* Loads the ARM Trusted Firmware BL2 preloader into internal on-chip SRAM (`0x00100000`).

### Stage 2: TF-A BL2 Preloader (Internal SRAM)
* Executes in SRAM prior to system DRAM initialization.
* Performs DDR4 memory training and enables the 512 MiB DDR4 address space (`0x40000000 - 0x5fffffff`).
* Mounts the MediaTek NMBM bad block translation driver to access the NAND flash.
* Reads the Firmware Image Package (FIP) partition located at physical flash offset `0x00380000`.
* Decompresses and loads:
  - **BL31 (TF-A Secure Monitor):** Staged into DRAM at `0x43000000`.
  - **BL33 (U-Boot):** Staged into DRAM at `0x41e00000`.
* Transfers execution to BL31 via an ARM `smc` (Secure Monitor Call).

### Stage 3: TF-A BL31 (Secure Monitor - EL3)
* Remains resident in protected DRAM memory (`0x43000000 - 0x4303ffff`).
* Provides runtime ARM Power State Coordination Interface (PSCI v0.2) services for multi-core management.
* Drops the CPU execution privilege from EL3 to EL2 and jumps to the U-Boot entry point.

### Stage 4: U-Boot 2023.04 (Bootloader - EL2)
* Initializes board peripherals: UART0 serial console, MT7531 switch MDIO bus, and SPI-NAND driver.
* Reads boot environment variables stored in the active U-Boot environment volume.
* Implements the A/B dual-slot fallback mechanism.
* Checks for user interruption on the serial console (115200 8N1).

---

## 3. A/B Dual-Boot Redundancy Architecture

The bootloader manages two independent system firmware slots:
* **Slot 0 (`ubi` partition):** Physical flash offset `0x00580000 - 0x0917FFFF` (Size: 60 MiB).
* **Slot 1 (`ubi2` partition):** Physical flash offset `0x09180000 - 0x0EB7FFFF` (Size: 90 MiB).

### Boot Control Environment Variables:
```text
dual_boot.current_slot=0      # Active boot slot (0 = ubi, 1 = ubi2)
dual_boot.slot_0_invalid=0    # Mark slot 0 as healthy (0) or corrupt (1)
dual_boot.slot_1_invalid=0    # Mark slot 1 as healthy (0) or corrupt (1)
```

If the watchdog timer expires during kernel boot or if an image checksum fails, the bootloader automatically sets `dual_boot.slot_0_invalid=1` and fails over to Slot 1.

---

## 4. In-RAM Boot Execution (Zero Flash Wear)

The stock boot path on this board is a **FIT loader**: `mtkboardboot` reads a
Flattened Image Tree from the `kernel` UBI volume and hands it to `bootm`. A
RAM boot therefore needs a real `.itb`, and the device definition in this
repository does **not** produce one — it emits
`openwrt-mediatek-filogic-jiorouter_ax6000-jidu6801-initramfs-kernel.bin`,
which is a bare arm64 `Image` with the DTB as a separate file. `bootm` on
that blob will not work.

Two routes exist; neither is verified in this repository:

**A. Build a FIT first.** Add a `.itb` image target to the device definition
(as other `mediatek/filogic` devices do), then:

1. Host the resulting `.itb` on a TFTP server at `192.168.1.254`.
2. Connect an Ethernet cable to LAN Port 1.
3. In U-Boot:
   ```uboot
   setenv ipaddr 192.168.1.1
   setenv serverip 192.168.1.254
   fdt addr ${fdtcontroladdr}
   fdt rm /signature
   tftpboot 0x46000000 openwrt-mediatek-filogic-jiorouter_ax6000-jidu6801-initramfs.itb
   bootm 0x46000000
   ```
   The `fdt rm /signature` step is required: the stock boot path expects a
   vendor signature node in its control DTB, and an upstream OpenWrt FIT
   does not carry the matching OEM signature.

**B. Skip the FIT.** `tftpboot` the raw `-initramfs-kernel.bin` and the DTB
separately, then use `booti <kernel> <dtb>` — which boots a bare `Image`
plus a standalone DTB and does not go through the signature check. Whether
this vendor U-Boot build provides `booti` is unverified.

Once a userspace is up by either route, flash permanently with `sysupgrade`.
