# OpenWrt Target Porting & Architectural Guide

## 1. Upstream Relationship & Closest Existing Target

The **JioRouter AX6000 JIDU6801** is added to OpenWrt under the `mediatek/filogic` target.

### Closest Upstream Target:
The closest existing target is **`jiorouter,ax6000-jidu6j01`** (`mt7986a-jiorouter-ax6000-jidu6j01.dts`), which also groups `JIDU6201`, `JIDU6401`, `JIDU6601`, and `JIDU6701` as alternative models.

### Hardware Delta:
| Property | JIDU6J01 / JIDU6601 Family | JIDU6801 | Reusability Classification |
|:---|:---|:---|:---|
| **SoC** | MediaTek MT7986A Filogic 830 | MediaTek MT7986A Filogic 830 | **COMMON** (Reuses `mt7986a.dtsi`) |
| **DRAM** | 512 MiB DDR4-3200 | 512 MiB DDR4-3200 | **COMMON** (Reuses `mt7986a-jiorouter-common.dtsi`) |
| **Flash** | 256 MiB Winbond W25N02KV (NMBM) | 256 MiB Winbond W25N02KV (NMBM) | **COMMON** (Reuses `mt7986a-jiorouter-common.dtsi`) |
| **Switch** | MediaTek MT7531AE DSA | MediaTek MT7531AE DSA | **COMMON** (Reuses `mt7986a-jiorouter-common.dtsi`) |
| **Switch Ports** | Port 0 WAN, Ports 1–4 LAN 1–4 | Port 0 WAN, Ports 1–4 LAN 1–4 | **COMMON** (Identical port layout) |
| **Switch Ports** (6101 for contrast) | `lan2`, `lan3`, `lan4`, `lan1` | `lan1`–`lan4` in order | differs from `jiorouter_ax6000-jidu6101`, which reorders them |
| **WAN PHY** | MaxLinear GPY211 (2.5 Gbps) | MaxLinear GPY211 (2.5 Gbps) | **COMMON** |
| **Wi-Fi** | MediaTek MT7976C DBDC AX6000 | MediaTek MT7976C DBDC AX6000 | **COMMON** (Reuses `mt7915e`) |
| **LEDs / Reset** | Red (12), Green (13), Blue (14), Reset (9)| Red (12), Green (13), Blue (14), Reset (9)| **COMMON** |
| **Model String** | `JioRouter AX6000 JIDU6J01` | `JioRouter AX6000 JIDU6801` | **6801-SPECIFIC** |
| **Compatible** | `jiorouter,ax6000-jidu6j01` | `jiorouter,ax6000-jidu6801` | **6801-SPECIFIC** |
| **Base MAC Location**| Model-dependent in `MFG` (0x20 / 0x1d0 / named field) | Offset `0x00` in `MFG` | Resolved by the existing upstream default — no new code |

---

## 2. Why a Dedicated Board Profile

Two shapes were considered:

1. **A dedicated `Device/jiorouter_ax6000-jidu6801` profile** (what this patch
   does), or
2. **An extra `DEVICE_ALT3_VENDOR` / `DEVICE_ALT4_*` variant listed under the
   existing `jiorouter_ax6000-jidu6j01` profile.**

Option 2 is fewer lines, and it is how `JIDU6201`, `JIDU6401`, `JIDU6601` and
`JIDU6701` are handled — but those are all the *same physical board* under
different model strings, and they share one DTS because their switch layout,
storage and RF are identical.

This board is different in a way that a `DEVICE_ALT*` alias hides: it
carries a distinct `compatible` string and a distinct device-tree node, and
`sysext`/`sysupgrade` images are named from `DEVICE_VENDOR`/`DEVICE_MODEL`/
`DEVICE_VARIANT`. Registering it as its own target means the build, the
`profiles.json` entry, the generated image filenames and the upgrade path all
reflect the real product name, instead of a `JIDU6801` image appearing under
a `jidu6j01` profile where a maintainer would have to work out why.

The cost is one extra `Device/...` block and one extra `.dts`. Given that the
board already needs its own `.dts` regardless, the alias buys nothing.

---

## 3. DTS Architecture & Rationale

Rather than duplicating the entire device tree, OpenWrt utilizes `mt7986a-jiorouter-common.dtsi` for all shared peripherals. That shared file already provides the memory node, the RGB LED GPIOs, the reset key, the regulators, the SPI-NAND controller with NMBM parameters, the full fixed-partition table, `ssusb`, `uart0`, and the Wi-Fi EEPROM `nvmem` cell.

The 6801-specific device tree `target/linux/mediatek/dts/mt7986a-jiorouter-ax6000-jidu6801.dts` is 53 lines and does two things:
   ```dts
   compatible = "jiorouter,ax6000-jidu6801", "mediatek,mt7986a";
   model = "JioRouter AX6000 JIDU6801";
   ```
2. Labels the MT7531 switch ports:
   - `port@0`: `"wan"`
   - `port@1`: `"lan1"`
   - `port@2`: `"lan2"`
   - `port@3`: `"lan3"`
   - `port@4`: `"lan4"`
   - `port@6`: CPU link attached to `&gmac0` via `2500base-x` SerDes.

Because the switch ports are labeled with standard OpenWrt names, the network configuration subsystem automatically assigns the ports to `br-lan` and `wan` without requiring board-specific interface rules in `02_network`.

---

## 4. Image Definition (`filogic.mk`)

In `target/linux/mediatek/image/filogic.mk`:
```makefile
define Device/jiorouter_ax6000-jidu6801
  DEVICE_VENDOR := JioRouter
  DEVICE_MODEL := AX6000
  DEVICE_VARIANT := JIDU6801
  DEVICE_DTS := mt7986a-jiorouter-ax6000-jidu6801
  DEVICE_DTS_DIR := ../dts
  DEVICE_PACKAGES := kmod-usb3 kmod-mt7915e kmod-mt7986-firmware mt7986-wo-firmware
  UBINIZE_OPTS := -E 5
  UBOOTENV_IN_UBI := 1
  BLOCKSIZE := 128k
  PAGESIZE := 2048
  IMAGE/sysupgrade.bin := sysupgrade-tar | append-metadata
endef
TARGET_DEVICES += jiorouter_ax6000-jidu6801
```

* **`UBINIZE_OPTS := -E 5`:** Sets the UBI erase counter header padding to 5.
* **`BLOCKSIZE := 128k` / `PAGESIZE := 2048`:** Matches the physical geometry of the Winbond W25N02KV SPI-NAND chip.
* **`UBOOTENV_IN_UBI := 1`:** Generates UBI volume allocations compatible with U-Boot's dynamic environment handling.

---

## 5. MAC Address Handling (`02_network`)

The factory manufacturing partition (the `MFG` region at flash offset
`0xEB80000`) stores the 6-byte binary base MAC at offset `0x00`.

Upstream `mediatek/filogic` already implements this for the JioRouter
family. `mediatek_setup_macs()` in
`target/linux/mediatek/filogic/base-files/etc/board.d/02_network` has a case
label for `jiorouter,ax6000-jidu6j01` that locates the `MFG` character
device and, after probing the model string, falls through to:

```sh
*)
        label_mac=$(get_mac_binary "$mfg_dev" 0)
        ;;
```

That default already reads offset `0`, which is exactly where this board
keeps its base MAC. So the only change needed is to add this board to the
existing case label — **one line**:

```diff
+	jiorouter,ax6000-jidu6801|\
 	jiorouter,ax6000-jidu6j01)
```

A dedicated `JIDU6801)` arm inside the inner `case` is deliberately *not*
included. It would read `get_mac_binary "$mfg_dev" 0x0`, which is
byte-for-byte the same call as the default — dead code that adds a
maintainer question without changing behaviour.

**Open item.** The extraction itself works: on a running unit the base MAC
from `MFG` offset `0` is read and written to UCI. But it does not currently
reach an interface — the MAC lands on a `config device` named `eth1`, and the
shared dtsi defines only one GMAC (`gmac0`, netif `eth0`), so the assignment
is discarded and the kernel falls back to a generated address. See
[`openwrt-status.md`](openwrt-status.md) §4.1. That is a pre-existing
naming mismatch in the shared board files, not something this patch
introduces, so it is reported rather than fixed here.

---

## 6. Build, Flashing & Recovery Instructions

### 6.1 Building from Source
```bash
git clone https://github.com/openwrt/openwrt.git
cd openwrt
git apply /path/to/0001-mediatek-filogic-add-support-for-JioRouter-AX6000-JIDU6801.patch
./scripts/feeds update -a && ./scripts/feeds install -a
make menuconfig
# Select: MediaTek Ralink ARM -> MediaTek Filogic 830 -> JioRouter AX6000 JIDU6801
make -j$(nproc) target/linux/compile
```

### 6.2 Bringing the device up without touching flash

The device definition in `filogic.mk` follows the pattern already used by
`jiorouter_ax6000-jidu6j01` and `jiorouter_ax6000-jidu6101`, so the build
emits:

```
openwrt-mediatek-filogic-jiorouter_ax6000-jidu6801-initramfs-kernel.bin
openwrt-mediatek-filogic-jiorouter_ax6000-jidu6801-squashfs-sysupgrade.bin
```

There is **no `.itb`**. `-initramfs-kernel.bin` is a bare arm64 `Image`; the
matching DTB is a separate file under `build_dir/target-*/linux-*/`.

This matters because the stock bootloader on this board is a FIT loader: its
`mtkboardboot` path reads a Flattened Image Tree out of the `kernel` UBI
volume, and `bootm` on a bare `Image` blob will not work. So the following
is **not** a working recipe, and is recorded here only so that nobody
repeats the mistake:

```uboot
tftpboot 0x46000000 openwrt-mediatek-filogic-jiorouter_ax6000-jidu6801-initramfs.itb   # file does not exist
```

There are two ways to get a RAM boot, and **neither is verified in this
repository** — there is no committed record of either having been run:

1. **Build a FIT and use `bootm`.** Add to the device definition
   `KERNEL_INITRAMFS_SUFFIX := .itb` and `IMAGES := sysupgrade.itb` with an
   `IMAGE/sysupgrade.itb := append-kernel | fit gzip ...` rule, as other
   `mediatek/filogic` devices do. That produces a real `.itb`. The stock
   boot path additionally expects a `/signature` node in its control DTB;
   the established workaround is to remove it in RAM before `bootm`:
   ```uboot
   fdt addr ${fdtcontroladdr}
   fdt rm /signature
   ```
2. **Use `booti` with a raw kernel and separate DTB.** Load both files over
   TFTP and call `booti <kernel> <dtb>`. This avoids the FIT requirement
   entirely, but whether the vendor's U-Boot build exposes `booti` is
   unverified.

Once a userspace is up by any route, the permanent install is the ordinary
one:

```bash
sysupgrade -n /tmp/openwrt-mediatek-filogic-jiorouter_ax6000-jidu6801-squashfs-sysupgrade.bin
```

Before the first flash, make the A/B slot state sane, because the stock
bootloader branches on it:

```uboot
setenv dual_boot.current_slot 0
setenv dual_boot.slot_0_invalid 0
setenv dual_boot.slot_1_invalid 0
saveenv
```

**Whichever route you take, do not erase `Factory`.** It holds the factory RF
calibration and the Wi-Fi EEPROM.

---

## 7. Validation Results & Limitations

Validation is graded and recorded in one place only:
**[`openwrt-status.md`](openwrt-status.md)**. It distinguishes what is
demonstrable from a committed artifact, what rests on reported on-device
testing, and what has not been tested at all. Read that rather than a
summary here, so there is a single source of truth.

Two things worth repeating, because they are the usual failure modes:

* The `Factory` partition must never be erased. It holds the factory RF
  calibration and the Wi-Fi EEPROM, and there is no public replacement.
* The stock FIP is effectively immutable. BL2 validates it against a
  hardcoded root-of-trust hash, so bootloader patching is not an option.
