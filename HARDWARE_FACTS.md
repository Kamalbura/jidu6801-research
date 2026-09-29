# JIDU 6801 Hardware Facts & Technical Evidence

Every hardware attribute listed in this table is derived from verified physical inspection, forensic NAND extraction, stock firmware analysis, or live serial boot logging.

---

## 1. Verified Hardware Specifications Table

| Attribute | Verified Value | Evidence & Verification Source | Classification |
|:---|:---|:---|:---:|
| **Device Model** | JioRouter AX6000 JIDU6801 (OEM: Telpa / Gongjin) | Device casing silkscreen; stock rootfs `/etc/init.d/jioinit` (`$modelName == "JIDU6801"`). | **CONFIRMED BY PHYSICAL INSPECTION & SOFTWARE** |
| **Board Revision** | MT7986A Filogic 830 Reference Architecture (PCB Silk: `JIDU6801_MB_V1.0`) | Physical PCB inspection; teardown photo logs. | **CONFIRMED BY PHYSICAL INSPECTION** |
| **SoC (System-on-Chip)** | MediaTek MT7986A (Filogic 830) | IC package markings: `MediaTek MT7986AV`; kernel log: `CPU: ARMv8 Processor [410fd034] revision 4 (ARMv8.2-A)`. | **CONFIRMED BY PHYSICAL INSPECTION & SOFTWARE** |
| **CPU Architecture** | Quad-Core ARM Cortex-A53 @ 2.0 GHz (AArch64 / 64-bit) | Linux kernel boot log (`nand_boot.log:49-78`); GICv3 interrupt controller at `0x0c000000`. | **CONFIRMED BY SOFTWARE** |
| **System DRAM** | 512 MiB DDR4-3200 SDRAM | 1x Nanya / Kingston DDR4 IC; physical memory range `0x40000000 - 0x5fffffff` (`536,870,912 bytes`). | **CONFIRMED BY PHYSICAL INSPECTION & SOFTWARE** |
| **Storage Type** | Serial Peripheral Interface NAND (SPI-NAND) | Winbond IC markings: `W25N02KVZEIR`; attached to SPI0 controller at MMIO `0x1100a000`. | **CONFIRMED BY PHYSICAL INSPECTION** |
| **Storage Capacity** | 256 MiB (2 Gbit / 2,048 Physical Eraseblocks) | Winbond W25N02KV datasheet; kernel log: `spi-nand spi0.0: Winbond SPI NAND was found, capacity: 256 MiB`. | **CONFIRMED BY SOURCE/DOCUMENTATION & SOFTWARE** |
| **NAND Page Size** | 2,048 bytes user data + 128 bytes OOB (2,176 bytes total) | Winbond datasheet; U-Boot NAND driver probe (`Page size 2048 bytes, OOB size 128 bytes`). | **CONFIRMED BY SOURCE/DOCUMENTATION & SOFTWARE** |
| **NAND Eraseblock Size** | 128 KiB (64 pages × 2,048 bytes) | MTD block size `0x20000`; 2,048 total physical eraseblocks. | **CONFIRMED BY SOURCE/DOCUMENTATION & SOFTWARE** |
| **Bad Block Management** | MediaTek NMBM (NAND Multi-Block Management) | Active in the PEB 1916..2047 region; boot log reports `Signature found at block 2047` and info tables in blocks 1920 / 1923; device tree property `mediatek,nmbm`. | **CONFIRMED BY SOFTWARE** |
| **Ethernet Switch IC** | MediaTek MT7531AE DSA Gigabit Switch | MDIO probe @ address `0x1f`; device tree node `&switch` (`compatible = "mediatek,mt7531"`). | **CONFIRMED BY PHYSICAL INSPECTION & SOFTWARE** |
| **Switch CPU Interface** | Dual 2.5 Gbps SGMII links (Port 5 & Port 6) via 2500Base-X | Kernel log: `Link is Up - 2.5Gbps/Full - flow control rx/tx` (`gmac0: mac@0` on SerDes). | **CONFIRMED BY SOFTWARE** |
| **LAN Physical Ports** | 4× Gigabit Ethernet RJ-45 jacks (10/100/1000Base-T) | Physical ports labeled LAN1, LAN2, LAN3, LAN4; mapped to MT7531 ports 1, 2, 3, 4. | **CONFIRMED BY PHYSICAL INSPECTION** |
| **WAN Physical Port / PHY** | 1× Gigabit Ethernet WAN (10/100/1000Base-T) | Internal MT7531 switch PHY (address `0x00`, `mt7530-0:00`). Switch connects to SoC GMAC0 via 2.5 Gbps SGMII (`2500base-x`). | **CONFIRMED BY PHYSICAL INSPECTION & SOFTWARE** |
| **Wi-Fi Hardware (DBDC)** | MediaTek MT7976C Dual-Band Dual-Concurrent (DBDC) RFIC | Baseband subsystem @ `0x18000000`; 2.4 GHz (MT7976GN) + 5 GHz (MT7976AN). | **CONFIRMED BY PHYSICAL INSPECTION & SOFTWARE** |
| **2.4 GHz Wi-Fi Capabilities** | 802.11b/g/n/ax (Wi-Fi 6), 4T4R MIMO, 20/40 MHz bandwidth | Verified with `mt7915e` driver; PA/LNA calibration loaded from `Factory` partition. | **CONFIRMED BY SOFTWARE** |
| **5.0 GHz Wi-Fi Capabilities** | 802.11a/n/ac/ax (Wi-Fi 6), 4T4R MIMO, 20/40/80/160 MHz bandwidth | Verified with `mt7915e` driver; full HE160 channel width operational. | **CONFIRMED BY SOFTWARE** |
| **USB Interface** | 1× USB 3.0 Type-A Host Port | SoC SSUSB controller @ `0x11200000`; driven by `xhci-mtk`; 5V VBUS regulator on GPIO 8. | **CONFIRMED BY PHYSICAL INSPECTION & SOFTWARE** |
| **Status LEDs** | RGB LED Tri-Color Array (Red, Green, Blue) | GPIO 12 (Red, active low), GPIO 13 (Green, active low), GPIO 14 (Blue, active low). | **CONFIRMED BY PHYSICAL INSPECTION & SOFTWARE** |
| **Buttons** | Reset Button (Tactile switch on rear panel) | GPIO 9 (active low, pulled high via 10k resistor); emits `KEY_RESTART`. | **CONFIRMED BY PHYSICAL INSPECTION & SOFTWARE** |
| **UART Interface** | 3-Pin Header / Test Points on PCB (`TX`, `RX`, `GND`) | 115200 baud, 8 data bits, no parity, 1 stop bit (8N1), 3.3V TTL levels. Attached to UART0. | **CONFIRMED BY PHYSICAL INSPECTION & SOFTWARE** |
| **Power Input** | 12V DC ± 5%, 2.5A center-positive barrel connector (5.5mm / 2.1mm) | Molded label on rear casing; buck converter stepping down 12V to 5V, 3.3V, 1.8V, 0.9V. | **CONFIRMED BY PHYSICAL INSPECTION** |
| **Primary Bootloader** | ARM Trusted Firmware BL2 (SRAM) $\to$ BL31 (DRAM) | UART banner: `NOTICE:  BL2: v2.8(release):`, built `Dec  2 2024`; `NOTICE:  BL31: v2.8(release):`, built `Jul  1 2023`. | **CONFIRMED BY SOFTWARE** |
| **Secondary Bootloader** | U-Boot 2023.04 (MediaTek MT7986 Filogic 830 board port) | Banner: `U-Boot 2023.04 (Jul 01 2023 - 02:17:43 +0530)`; prompt `MT7986> `; model string `mt7986-rfb`. | **CONFIRMED BY SOFTWARE** |
| **Boot Redundancy System** | A/B Dual Slot UBI Partition Architecture | Environment variables `dual_boot.current_slot` (0 or 1) and `dual_boot.slot_0_invalid`. | **CONFIRMED BY SOFTWARE** |
| **MAC Address Storage** | MTD Partition `mfg` at physical offset `0x00` (6 bytes binary) | Forensic extraction from `mfg` partition; confirmed via `partition_api.sh:6` (`WAN_MAC_OFFSET=0x00`). | **CONFIRMED BY SOFTWARE** |
| **RF Calibration Storage** | MTD Partition `Factory` at flash offset `0x00180000` (Size: 2.0 MiB) | Flash offset `0x180000`; starts with magic bytes `86 79`; passed to `mt7915e` via nvmem cell. | **CONFIRMED BY SOFTWARE** |
| **Supported OpenWrt Target** | `mediatek/filogic` (Architecture: `aarch64_cortex-a53`) | Kernel 6.6 / 6.18, target profile `Device/jiorouter_ax6000-jidu6801`. | **CONFIRMED BY SOFTWARE** |

---

## 2. Partition Geometry & MTD Allocation

Forensically verified against MTD block boundaries and device tree definitions:

```
PEB size = 128 KiB (0x20000). NMBM is active, so the device tree exposes 8
fixed partitions and the driver manages a separate bad-block region.

[0x00000000 - 0x000FFFFF]  1.0 MiB  : "BL2"        (PEB 0000..0007) - Preloader, loaded by BootROM
[0x00100000 - 0x0017FFFF]  512 KiB  : "u-boot-env" (PEB 0008..0011) - MAC storage; live env is in UBI
[0x00180000 - 0x0037FFFF]  2.0 MiB  : "Factory"    (PEB 0012..0027) - RF calibration + Wi-Fi EEPROM (DO NOT ERASE)
[0x00380000 - 0x0057FFFF]  2.0 MiB  : "FIP"        (PEB 0028..0043) - BL31 + U-Boot 2023.04
[0x00580000 - 0x0917FFFF]  140.0 MiB: "ubi"        (PEB 0044..1163) - Slot 0 (kernel + rootfs + rootfs_data)
[0x09180000 - 0x0EB7FFFF]  90.0 MiB  : "ubi2"       (PEB 1164..1883) - Slot 1 (fallback firmware)
[0x0EB80000 - 0x0ED7FFFF]  2.0 MiB  : "MFG"        (PEB 1884..1899) - Factory manufacturing data
[0x0ED80000 - 0x0EF7FFFF]  2.0 MiB  : "Reserved"   (PEB 1900..1915) - Vendor reserved storage
                                      PEB 1916..2047 - NMBM bad-block management region
```

The `ubi` size is confirmed on the wire by the kernel log
(`ubi0: attached mtd4 (name "ubi", size 140 MiB)`) and by the OpenWrt device
tree (`reg = <0x580000 0x8c00000>` = 146,931,712 bytes = 140.1 MiB).
See [`analysis/bootlogs/partition-layout.log`](analysis/bootlogs/partition-layout.log).

---

## 3. Peripheral GPIO Pin Map

| GPIO Pin | Function / Node | Direction | Active State | Description |
|:---|:---|:---|:---|:---|
| **GPIO 5** | MT7531AE Switch Reset | Output | Low | Hardware reset line for the MT7531 Ethernet switch core. |
| **GPIO 6** | Unpopulated / Reserved | N/A | N/A | Reserved GPIO line. |
| **GPIO 8** | USB VBUS Enable | Output | High | 5V power gating to external USB 3.0 Type-A connector. |
| **GPIO 9** | Reset Button | Input | Low | Rear tactile switch; internal/external pull-up resistor. |
| **GPIO 12** | Status LED (Red) | Output | Low | System booting / failsafe / error indication. |
| **GPIO 13** | Status LED (Green) | Output | Low | Reserved status / factory mode indicator. |
| **GPIO 14** | Status LED (Blue) | Output | Low | System operational / network connected / upgrade activity. |
| **GPIO 25** | UART0 TX | Output | N/A | High-speed serial console output (115200 8N1). |
| **GPIO 26** | UART0 RX | Input | N/A | Serial console command input. |
