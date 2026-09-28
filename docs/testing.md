# Comprehensive Hardware Verification & Testing Matrix

## 1. Test Environment & Build Artifacts

* **OpenWrt Revision:** OpenWrt snapshot `25.12-SNAPSHOT` (`r36304-0f8cceb469`)
* **Toolchain:** `aarch64-openwrt-linux-musl-gcc` 14.4.0, GNU Binutils 2.46.1
* **Target / Subtarget:** `mediatek/filogic` (ARM Cortex-A53)
* **Kernel Version:** Linux 6.6 / 6.18 SMP
* **Tested Board Profile:** `jiorouter_ax6000-jidu6801`
* **Test Image Types** (as actually emitted by the build):
  - `openwrt-mediatek-filogic-jiorouter_ax6000-jidu6801-initramfs-kernel.bin`
  - `openwrt-mediatek-filogic-jiorouter_ax6000-jidu6801-squashfs-sysupgrade.bin`

---

## 2. Subsystem Test Results

### 2.1 Boot & Serial Console
* **Test:** Attach USB-TTL adapter @ 115200 8N1; power on router; observe TF-A BL2, BL31, U-Boot, and Linux kernel initialization.
* **Result:** **PASSED.** Clean serial output with zero character corruption. Interactive shell available at `root@OpenWrt:/#`.

### 2.2 Storage & Flash Subsystem
* **Test:** Probe Winbond W25N02KV SPI-NAND; verify MTD partitions and NMBM bad-block translation layer.
* **Kernel Log:**
  ```text
  spi-nand spi0.0: Winbond SPI NAND was found, capacity: 256 MiB
  9 fixed-partitions partitions found on MTD device spi0.0
  Creating 9 MTD partitions on "spi0.0":
  0x000000000000-0x000000100000 : "BL2"
  0x000000100000-0x000000180000 : "u-boot-env"
  0x000000180000-0x000000380000 : "Factory"
  0x000000380000-0x000000580000 : "FIP"
  0x000000580000-0x000009180000 : "ubi"
  0x000009180000-0x00000eb80000 : "ubi2"
  0x00000eb80000-0x00000ed80000 : "mfg"
  0x00000ed80000-0x00000ef80000 : "Reserved"
  0x00000ef80000-0x000010000000 : "NMBM"
  ```
* **Result:** **PASSED.**

### 2.3 Ethernet Switch & WAN/LAN Ports
* **Test:** Connect 1 Gbps client to LAN1, LAN2, LAN3, LAN4; connect 2.5 Gbps gateway to WAN.
* **Kernel Log:**
  ```text
  mtk_soc_eth 15100000.ethernet eth0: mediatek frame engine at 0xffffffc081b40000, irq 120
  mtk_soc_eth 15100000.ethernet eth0: Link is Up - 2.5Gbps/Full - flow control rx/tx
  mtk_soc_eth 15100000.ethernet eth1: Link is Up - 2.5Gbps/Full
  ```
* **Link Status & Verification:**
  - LAN Ports 1..4: Auto-negotiate 10/100/1000 Mbps line rates with client endpoints.
  - WAN Port: Auto-negotiates 2.5 Gbps with upstream 2.5G multi-gigabit gateways.
  - CPU GMAC: Dual 2.5 Gbps SGMII links verified active via `gmac0` and `gmac1`.
  - Formal synthetic iperf3 multi-stream throughput testing was not formally recorded in lab logs and is marked **NOT FORMALLY BENCHMARKED**.
* **Result:** **PASSED (Link Negotiation & Packet Forwarding)**; Throughput benchmarks **NOT FORMALLY BENCHMARKED**.

### 2.4 Wireless Radios (2.4 GHz & 5.0 GHz Wi-Fi 6)
* **Test:** Initialize `radio0` (2.4 GHz) and `radio1` (5.0 GHz) under `mt7915e`. Test association with Wi-Fi 6 client.
* **Verified Evidence:**
  - Both `phy0` (2.4 GHz) and `phy1` (5.0 GHz) initialize cleanly under `mt7915e` driver.
  - 5.0 GHz radio supports up to 160 MHz channel width (HE160).
  - Client device successfully associates and acquires IP via DHCP on both bands.
  - RF calibration: Factory EEPROM verified loaded from `Factory` partition.
* **Result:** **PASSED (Driver Init, Calibration & Client Association)**.

### 2.5 LEDs & Buttons
* **Test:** Trigger LED states in `/sys/class/leds/`; monitor `evtest /dev/input/event0` on reset button press.
* **Result:** **PASSED.** Red, Green, and Blue LEDs activate as expected. Pressing reset button triggers `KEY_RESTART` and enters OpenWrt failsafe when held during boot.

### 2.6 Sysupgrade & Power-Cycle Persistence
* **Test:** Flash sysupgrade image via `sysupgrade -n`; execute software `reboot`; perform cold power cycle.
* **Result:** **PASSED.** Settings persist in UBIFS overlay; system cleanly boots back to OpenWrt.
