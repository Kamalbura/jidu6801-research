# JioRouter AX6000 (JIDU6801) — Hardware Research & OpenWrt Support

Reverse-engineering notes, hardware documentation and upstream OpenWrt device
support for the **JioRouter AX6000 JIDU6801** Wi-Fi 6 router.

The goal is to let owners of this hardware run current, open-source OpenWrt
instead of unmaintained vendor firmware, and to document the hardware well
enough that the port can be reproduced or maintained by someone else.

---

## Hardware at a glance

| Subsystem | Specification |
|:---|:---|
| **SoC** | MediaTek MT7986A (Filogic 830), 4x Cortex-A53 @ 2.0 GHz |
| **RAM** | 512 MiB DDR4 |
| **Flash** | 256 MiB Winbond W25N02KV SPI-NAND, MediaTek NMBM, 2048 PEBs of 128 KiB |
| **Switch** | MediaTek MT7531AE DSA — port 0 = 2.5G WAN (MaxLinear GPY211 PHY), ports 1–4 = 1G LAN, port 6 = 2.5G SGMII CPU link |
| **Wireless** | MediaTek MT7976C DBDC, 4x4 at 2.4 GHz + 4x4 at 5 GHz (AX6000), `mt7915e` |
| **LEDs** | Red GPIO 12, Green GPIO 13, Blue GPIO 14 |
| **Button** | Reset, GPIO 9, active low |
| **USB** | 1x USB 3.0 Type-A host |
| **Console** | UART0, 115200 8N1, 3.3 V TTL on PCB test pads |
| **Flash layout** | `BL2` 1 MiB · `u-boot-env` 512 KiB · `Factory` 2 MiB · `FIP` 2 MiB · `ubi` 140 MiB · `ubi2` 90 MiB · `MFG` 2 MiB · `Reserved` 2 MiB |

Full detail, with the evidence behind each figure, is in
[`HARDWARE_FACTS.md`](HARDWARE_FACTS.md).

---

## Repository layout

```
HARDWARE_FACTS.md          verified silicon facts, GPIO map, partition geometry
docs/                      how the board actually behaves
hardware/                  board photos, pinout, component locations
analysis/                  captured logs, checksums, UBI volume table
tools/                     NAND parsers and the log redaction script
openwrt/                   the upstream support patch
```

### Documentation

| Document | Covers |
|:---|:---|
| [`HARDWARE_FACTS.md`](HARDWARE_FACTS.md) | SoC, memory, flash geometry, switch/RF inventory, GPIO map |
| [`docs/partition-layout.md`](docs/partition-layout.md) | The 8 MTD partitions, NMBM region, UBI volume layout, MAC storage |
| [`docs/uart.md`](docs/uart.md) | Console wiring, baud, how to reach the U-Boot prompt |
| [`docs/boot-process.md`](docs/boot-process.md) | BootROM → BL2 → BL31 → U-Boot → kernel, A/B slots, RAM boot |
| [`docs/nand.md`](docs/nand.md) | SPI-NAND geometry and bad-block handling |
| [`docs/esp32s3-nand.md`](docs/esp32s3-nand.md) | In-circuit SPI-NAND acquisition and programming |
| [`docs/stm32f1-boot-companion.md`](docs/stm32f1-boot-companion.md) | External MCU for unattended cold boot |
| [`docs/openwrt-port.md`](docs/openwrt-port.md) | The port: DTS, image definition, MAC handling, build, flashing |
| [`docs/openwrt-status.md`](docs/openwrt-status.md) | **What is verified, what is not** — read this before trusting a claim |
| [`docs/hardware.md`](docs/hardware.md) | Physical teardown and component identification |
| [`docs/testing.md`](docs/testing.md) | Test environment and procedures |
| [`docs/recovery.md`](docs/recovery.md) | Recovering a bricked or boot-looping unit |
| [`docs/security-notes.md`](docs/security-notes.md) | Scope boundaries, and what is deliberately not published |

### Evidence

* [`analysis/bootlogs/openwrt-boot.log`](analysis/bootlogs/openwrt-boot.log) —
  OpenWrt 6.18.52 on this board: UBI attach, SquashFS root, UBIFS overlay, DSA
  switch, 2.5 Gbps link-up, both Wi-Fi PHYs.
* [`analysis/bootlogs/boot-chain.log`](analysis/bootlogs/boot-chain.log) —
  BL2 image loading, anti-rollback checks, BL31 hand-off, U-Boot banner.
* [`analysis/bootlogs/partition-layout.log`](analysis/bootlogs/partition-layout.log) —
  the 8 MTD partitions, NMBM tables and switch PHY probe as printed on hardware.
* [`analysis/hashes/sha256sums.txt`](analysis/hashes/sha256sums.txt) —
  checksums for reference artifacts and built images.
* [`analysis/partition-map/ubi_volume_table.txt`](analysis/partition-map/ubi_volume_table.txt) —
  UBI volume inventory.

`openwrt-boot.log` is `dmesg` from a unit actually running
`OpenWrt SNAPSHOT r0-57072d9` / kernel 6.18.52 on this board. The other two
are captures of the **stock** firmware, which is the authoritative on-hardware
record of the partition layout and switch inventory.

Every claim in the documentation is graded against these artifacts in
[`docs/openwrt-status.md`](docs/openwrt-status.md), which also records the
things that were *not* tested and one open defect: the factory base MAC is
read correctly from `MFG` but does not currently reach any network interface.

---

## OpenWrt support

The board is added to the upstream `mediatek/filogic` target as
`jiorouter_ax6000-jidu6801`. The patch is in
[`openwrt/`](openwrt/) and touches three files, 69 added lines:

| File | Change |
|:---|:---|
| `target/linux/mediatek/dts/mt7986a-jiorouter-ax6000-jidu6801.dts` | new, 53 lines |
| `target/linux/mediatek/image/filogic.mk` | 15-line `Device/...` block |
| `target/linux/mediatek/filogic/base-files/etc/board.d/02_network` | 1 line: add the board to an existing case label |

The device tree is short because `mt7986a-jiorouter-common.dtsi` — shared
with the existing `jiorouter_ax6000-jidu6j01` target — already provides the
memory node, LEDs, reset key, regulators, SPI-NAND controller, the full
partition table, USB, UART and the Wi-Fi EEPROM binding. Only the switch port
layout and the model strings are board-specific. The image definition
deliberately mirrors the sibling targets rather than inventing a new pattern.

### Build

```bash
git clone https://github.com/openwrt/openwrt.git
cd openwrt
git am /path/to/openwrt/0001-mediatek-filogic-add-support-for-JioRouter-AX6000-JIDU6801.patch
./scripts/feeds update -a && ./scripts/feeds install -a
make menuconfig
#   Target System:  MediaTek Ralink ARM
#   Subtarget:       MediaTek Filogic 830 (MT7986)
#   Target Profile:  JioRouter AX6000 JIDU6801
make -j"$(nproc)"
```

If your GNU tar is 1.35 or newer it refuses members whose names contain a
colon, which some OpenWrt sources use. Work around it with:

```
TAR_OPTIONS += --exclude='*:*'
```

in `include/unpack.mk`, **locally only** — it is not part of the patch.

### Before you flash

* Set the A/B slot flags in U-Boot (`dual_boot.current_slot`,
  `dual_boot.slot_0_invalid`, `dual_boot.slot_1_invalid`) or the bootloader
  will fail over immediately.
* **Never erase `Factory`** (`0x180000`–`0x37ffff`). It holds the factory RF
  calibration and the Wi-Fi EEPROM. There is no public replacement.
* The stock FIP cannot be patched — BL2 validates it against a hardcoded
  root-of-trust hash.

### Getting a userspace without touching flash

The stock bootloader is a FIT loader: its `mtkboardboot` path expects a
Flattened Image Tree and checks a vendor signature node in its control DTB.
This repository's build emits
`openwrt-mediatek-filogic-jiorouter_ax6000-jidu6801-initramfs-kernel.bin`
(a bare arm64 `Image` with a separate DTB), **not** a `.itb`. There are two
ways to get a RAM boot — build a real `.itb` and use `bootm` after
`fdt rm /signature`, or load the raw kernel and DTB and use `booti`. Neither
is verified in this repository. Both are written out in
[`docs/openwrt-port.md`](docs/openwrt-port.md).

---

## Two hardware efforts

### In-circuit SPI-NAND access

Because the bootloader chain is not writable, a small ESP32-S3 board is used to
read and write the SPI-NAND over flying leads. This gives a full chip dump, a
Status Register 1 unprotect routine, block erase and page programming with
byte-exact readback verification. See
[`docs/esp32s3-nand.md`](docs/esp32s3-nand.md).

### External boot companion

The stock bootloader overwrites `bootcmd` in RAM and refuses an unsigned
kernel FIT, so a U-Boot environment variable alone cannot deliver unattended
cold boot. A low-cost STM32F1-class MCU (HK32F103 / STM32F103, ~₹150) sits on
the console pads, answers the console challenge, strips the signature node
from the control DTB in RAM, and releases the line once Linux is up. It never
writes to router flash. See
[`docs/stm32f1-boot-companion.md`](docs/stm32f1-boot-companion.md).

---

## What this repository does not contain

Vendor firmware images, raw NAND dumps and the stock root filesystem are not
distributed here — only their SHA-256 values, so a reader who already holds a
dump can verify it. Bootloader credential material and the tooling that
derived it are withheld; the OpenWrt port does not need them. Per-unit
identifiers are stripped from every published log by
[`tools/sanitize-log.py`](tools/sanitize-log.py). The full list and the
reasoning is in [`docs/security-notes.md`](docs/security-notes.md).

**The ESP32-S3 and STM32F1 firmware sources are also not part of this
repository.** The two hardware efforts above are documented and their results
are reported, but the firmware is not published here, so those two sections
are not reproducible from this repository alone.

---

## Independence

This is an independent project. It is not affiliated with, sponsored by or
endorsed by Reliance Jio Infocomm, Telpa, MediaTek, Gongjin, Espressif
Systems, STMicroelectronics or the OpenWrt project. The hardware analysed was
personally acquired. Testing was done in an isolated private environment; no
telecommunications infrastructure, subscriber account or carrier management
system was accessed or targeted.

Modifying bootloader or flash contents carries real risk of rendering a device
unusable. Confirm your exact hardware revision before proceeding.

---

## License

GNU General Public License v2.0, matching the Linux kernel and OpenWrt. See
[`LICENSE`](LICENSE).
