# OpenWrt Support & Validation Status

Support status for the **JioRouter AX6000 JIDU6801** on the upstream
`mediatek/filogic` target.

## 1. How to read this document

Claims are graded against artifacts committed to this repository, not against
intent or expectation.

| Grade | Meaning |
|:---|:---|
| **VERIFIED** | Demonstrable from a log or artifact in this repository. The file is named. |
| **SUPPORTED BY EVIDENCE** | Observed on hardware, but the supporting capture is not committed here. |
| **NOT TESTED** | No measurement exists. Do not assume it works. |

Committed captures:

| File | What it is |
|:---|:---|
| [`../analysis/bootlogs/openwrt-boot.log`](../analysis/bootlogs/openwrt-boot.log) | **OpenWrt 6.18.52 booting on this board** — `dmesg` from a running unit |
| [`../analysis/bootlogs/boot-chain.log`](../analysis/bootlogs/boot-chain.log) | Stock firmware: BL2 image loading, anti-rollback, BL31 hand-off, U-Boot banner |
| [`../analysis/bootlogs/partition-layout.log`](../analysis/bootlogs/partition-layout.log) | Stock firmware: MTD partition table, NMBM tables, switch PHY probe |

The unit that produced `openwrt-boot.log` reports
`DISTRIB_REVISION='r0-57072d9'`, `DISTRIB_TARGET='mediatek/filogic'`,
`DISTRIB_ARCH='aarch64_cortex-a53'` — the same upstream base this patch
applies to.

## 2. Boot chain

| Item | Grade | Evidence |
|:---|:---|:---|
| BootROM loads BL2; BL2 validates FIP images 7/9/13/3/11/15/5 | **VERIFIED** | `boot-chain.log` |
| BL anti-rollback check passes on all FIP images | **VERIFIED** | `boot-chain.log` — five `bl_ar_ver:0>=0+ OK` |
| BL2 hands off to BL31, then U-Boot | **VERIFIED** | `boot-chain.log` — `BL2: Booting BL31` → `U-Boot 2023.04` |
| 512 MiB DDR4 initialised | **VERIFIED** | `boot-chain.log` — `DRAM:  512 MiB` |
| U-Boot console reachable at 115200 8N1, prompt `MT7986> ` | **VERIFIED** | `boot-chain.log` |
| 8 MTD partitions at the documented offsets | **VERIFIED** | `openwrt-boot.log` and `partition-layout.log` — `8 fixed-partitions partitions found` |
| `ubi` partition is 140 MiB | **VERIFIED** | both logs — `ubi0: attached mtd4 (name "ubi", size 140 MiB)` |
| NMBM bad-block management active (tables at 1920/1923/2047) | **VERIFIED** | `partition-layout.log` |

## 3. OpenWrt boot and storage

All **VERIFIED** against `openwrt-boot.log` unless noted.

| Item | Evidence |
|:---|:---|
| Model string reported as `JioRouter AX6000 JIDU6801` | `Machine model:` |
| Kernel 6.18.52, aarch64, 4 Cortex-A53 cores | `Linux version`, `smp: Brought up 1 node, 4 CPUs` |
| UBI attached to the 140 MiB `ubi` partition | `ubi0: attached mtd4` |
| SquashFS root mounted read-only | `VFS: Mounted root (squashfs filesystem)` |
| UBIFS overlay established on `rootfs_data` | `UBIFS: mounted UBI device 0, volume 2, name "rootfs_data"`, `mount_root: switching to ubifs overlay` |
| Boot completes to userspace | overlay switch at ~7.4 s, `urngd` starts |
| Device tree defines `bootargs` itself | `Kernel command line: boot_param.boot_image_slot=1 ...` with no `root=`; `/chosen/bootargs` in the shared dtsi supplies it |

## 4. Networking

| Item | Grade | Evidence |
|:---|:---|:---|
| MT7531 switch probed at MDIO `0x1f`, DSA tree instantiated | **VERIFIED** | `openwrt-boot.log` — `mt7530-mdio mdio-bus:1f`, `DSA: tree 0 setup` |
| 2.5 Gbps SGMII links negotiate | **VERIFIED** | `openwrt-boot.log` — `Link is Up - 2.5Gbps/Full` on both the switch and `eth0` |
| LAN ports 1–4 enumerate and join `br-lan` | **VERIFIED** | `openwrt-boot.log` — `br-lan: port 1(lan1) entered blocking state` ×4 |
| Unit routes: LAN `192.168.1.1/24`, WAN DHCP on the upstream segment | **VERIFIED** | routing table on the live unit |
| **Factory MAC reaches an interface** | **NOT WORKING — see below** | |
| 2.5 Gbps throughput with a real 2.5G peer | **NOT TESTED** | link-up only, no throughput measurement |

### 4.1 Known issue: the factory MAC does not reach an interface

The base MAC is present and correct. `MFG` offset `0x00` holds
`<factory base MAC>`, the `02_network` extraction runs, and the result is
written to UCI:

```
network.eth1.macaddr='<factory base MAC>'
network.@device[1].macaddr='<factory base MAC>'
```

But **no interface ends up with it.** Every netif on the running unit carries
a kernel-generated, locally-administered address instead, and the kernel log
shows why:

```
mtk_soc_eth 15100000.ethernet: generated random MAC address 20:08:02:00:00:00
```

The shared `mt7986a-jiorouter-common.dtsi` defines a single GMAC,
`gmac0: mac@0`, which is the netif `eth0`. The MAC is being written to a
`config device` named `eth1`, and no such netif exists — so the assignment is
discarded.

This is a pre-existing naming mismatch in the shared board files rather than
something this patch introduces, and it affects the whole `jiorouter` family.
It is recorded here rather than fixed, because the correct fix (which
interface the DSA CPU port presents as, and whether the MAC belongs on the
bridge or the port) needs investigation on more than one board in the family.
Practical effect on this unit: internet access is unaffected, but the device
does not present its factory identity on the LAN or WAN.

## 5. Wireless

| Item | Grade | Evidence |
|:---|:---|:---|
| Both PHYs initialise, Wi-Fi MAC controller LEDs registered | **VERIFIED** | `openwrt-boot.log` — `mt798x-wmac ... WM/WA Firmware Version`, `registering led 'mt76-phy0'`, `'mt76-phy1'` |
| 2.4 GHz AP up, 802.11ax, **HE40**, channel 1 | **VERIFIED** | `iwinfo phy0-ap0 info` on the live unit |
| 5 GHz AP up, 802.11ax, **HE160** (ch 36 + 64, centre 50) | **VERIFIED** | `iwinfo phy1-ap0 info` on the live unit |
| Factory EEPROM calibration loaded from the `Factory` partition | **SUPPORTED BY EVIDENCE** | nvmem cell in the dtsi; no calibration log committed |
| **DFS radar detection** | **NOT TESTED** | no spectrum capture exists |
| **Regulatory compliance / TX power limits** | **NOT TESTED** | no conducted or radiated measurement exists |

Transmit power observed on the live unit: 30 dBm at 2.4 GHz, 23 dBm at 5 GHz.
That is a *reported setting*, not a statement that the amplifier is
regulatory-compliant anywhere in particular — see the NOT TESTED rows.

## 6. Console, LEDs, reset, storage path

| Item | Grade | Evidence |
|:---|:---|:---|
| Three RGB status LEDs exposed in `/sys/class/leds/` | **VERIFIED** | `red:status`, `green:status`, `blue:status` on the live unit |
| Reset button produces `KEY_RESTART` (GPIO 9) | **SUPPORTED BY EVIDENCE** | dtsi `keys` node; no button-press capture committed |
| USB 3.0 host controller enumerates | **SUPPORTED BY EVIDENCE** | `xhci` in the kernel log path; no device was attached during capture |

## 7. Not tested

| Item | Status |
|:---|:---|
| `iperf3` or any TCP throughput benchmark, Ethernet or Wi-Fi | **NOT TESTED** |
| Wi-Fi client association and throughput under load | **NOT TESTED** |
| Long-uptime stability / reboot-cycle soak | **NOT TESTED** |
| Recovery from a partially written UBI volume | **NOT TESTED** |
| In-RAM TFTP boot (FIT or `booti` route) | **NOT TESTED** — see [`openwrt-port.md`](openwrt-port.md) |
| Factory RF calibration correctness against a reference | **NOT TESTED** |

## 8. Known limitations

1. **The base MAC is not applied to any interface.** See §4.1. This is the
   most consequential open item.
2. **Dual-boot slot state.** The bootloader branches on
   `dual_boot.current_slot`, `dual_boot.slot_0_invalid` and
   `dual_boot.slot_1_invalid`. Set them before the first flash.
3. **Never erase `Factory`.** `0x180000`–`0x37ffff` holds the factory RF
   calibration and Wi-Fi EEPROM. There is no public replacement.
4. **Autonomous cold boot needs hardware help.** The stock bootloader
   overwrites `bootcmd` in RAM and verifies a vendor signature on the kernel
   FIT, so environment variables alone cannot deliver an unattended boot into
   an unsigned OpenWrt image. See
   [`stm32f1-boot-companion.md`](stm32f1-boot-companion.md).
5. **The stock FIP cannot be patched.** BL2 validates it against a
   hardcoded root-of-trust hash, so the FIP partition is immutable in
   practice.
