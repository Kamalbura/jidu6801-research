# Recovery & Unbricking Guide

## 1. General Safety Principles

The JioRouter AX6000 JIDU6801 features robust hardware partitioning that isolates the bootloader preloader (`BL2`), the secondary bootloader (`FIP`), and the RF calibration partition (`Factory`) from the user-writable firmware partitions (`ubi` and `ubi2`).

As long as `BL2`, `FIP`, and `Factory` remain intact, the router can always be recovered via the serial console and TFTP without desoldering components.

---

## 2. In-RAM TFTP Recovery (Zero Risk)

If an invalid firmware image is flashed or if userspace fails to boot:

### Step 1: Connect Serial Console
Attach a 3.3V USB-TTL adapter to the UART pads (115200 8N1). Connect an Ethernet cable between your computer and LAN Port 1.

### Step 2: Prepare an Image You Can Actually Boot
Set your computer's Ethernet adapter to a static IPv4 address:
* **IP Address:** `192.168.1.254`
* **Subnet Mask:** `255.255.255.0`

Put an image in your TFTP root. The build in this repository emits
`openwrt-mediatek-filogic-jiorouter_ax6000-jidu6801-initramfs-kernel.bin` (a
bare arm64 `Image`, DTB separate) — **not** a `.itb`. The stock bootloader is a
FIT loader, so `bootm` needs a real `.itb`. See
[`boot-process.md`](boot-process.md) for the two routes and the required
`fdt rm /signature` step.

### Step 3: Interrupt Boot & Load the Kernel
Power cycle the router and press **Enter** to reach the `MT7986> ` prompt,
then clear the slot flags so the bootloader does not immediately fail over:
```uboot
setenv dual_boot.current_slot 0
setenv dual_boot.slot_0_invalid 0
setenv dual_boot.slot_1_invalid 0
setenv ipaddr 192.168.1.1
setenv serverip 192.168.1.254
```
Then load the kernel, either from a FIT:
```uboot
fdt addr ${fdtcontroladdr}
fdt rm /signature
tftpboot 0x46000000 <your-image>.itb
bootm 0x46000000
```
or raw, without a FIT:
```uboot
tftpboot 0x46000000 <your-image>-initramfs-kernel.bin
tftpboot 0x4f000000 <your-dtb>.dtb
booti 0x46000000 0x4f000000
```
The router will execute OpenWrt directly from DRAM, giving you a shell to
re-flash a clean sysupgrade image with.

---

## 3. Resetting Dual-Boot Slots in U-Boot

If the router repeatedly bootloops because the bootloader flagged Slot 0 as corrupt:
```uboot
setenv dual_boot.current_slot 0
setenv dual_boot.slot_0_invalid 0
setenv dual_boot.slot_1_invalid 0
saveenv
```
Restart the boot sequence with:
```uboot
boot
```

---

## 4. Backing Up the Critical Factory Partition

Before performing any destructive flash operations, it is strongly recommended to back up your device's unique `Factory` partition from OpenWrt userspace:

```bash
# Locate the Factory partition
cat /proc/mtd | grep Factory
# Example output: mtd2: 00200000 00020000 "Factory"

# Dump the partition
dd if=/dev/mtd2 of=/tmp/factory_backup.bin bs=128k count=16

# Copy off the router to your local machine
scp root@192.168.1.1:/tmp/factory_backup.bin ./
```
Keep this backup safe. It contains your unique RF power calibration tables.
