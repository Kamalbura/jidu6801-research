# Partition Layout & Flash Storage Architecture

## 1. Physical MTD Partition Layout

The 256 MiB Winbond W25N02KV SPI-NAND flash is partitioned into **8** fixed MTD
regions by the device tree. MediaTek NMBM manages a further bad-block region
which is not exposed as a partition.

| Partition Label | Physical Eraseblocks | Flash Offset Range | Size | Filesystem / Role | Critical Protection Rule |
|:---|:---|:---|:---|:---|:---|
| **`BL2`** | PEB 0000..0007 | `0x00000000 - 0x000FFFFF` | 1.0 MiB | Raw Preloader Binary | Read-Only. Validated by BootROM. Do not overwrite. |
| **`u-boot-env`** | PEB 0008..0011 | `0x00100000 - 0x0017FFFF` | 512 KiB | MTD Key-Value Storage | Read-Only. Holds the factory MAC; the live U-Boot environment lives in a UBI volume. |
| **`Factory`** | PEB 0012..0027 | `0x00180000 - 0x0037FFFF` | 2.0 MiB | Raw RF Calibration Data | **CRITICAL: NEVER ERASE.** Contains factory RF matrix. |
| **`FIP`** | PEB 0028..0043 | `0x00380000 - 0x0057FFFF` | 2.0 MiB | FIP (BL31 + U-Boot) | Read-Only. 1024 physical pages. Do not corrupt. |
| **`ubi`** | PEB 0044..1163 | `0x00580000 - 0x0917FFFF` | 140.0 MiB | UBI Container (Slot 0) | Production OpenWrt target partition. |
| **`ubi2`** | PEB 1164..1883 | `0x09180000 - 0x0EB7FFFF` | 90.0 MiB | UBI Container (Slot 1) | Fallback / secondary factory image container. |
| **`MFG`** | PEB 1884..1899 | `0x0EB80000 - 0x0ED7FFFF` | 2.0 MiB | Raw Manufacturing Data | Contains factory base MAC address at offset `0x00`. |
| **`Reserved`** | PEB 1900..1915 | `0x0ED80000 - 0x0EF7FFFF` | 2.0 MiB | Reserved Storage | Read-Only vendor reserved area. |
| *(NMBM region)* | PEB 1916..2047 | `0x0EF80000 - 0x10000000` | 16.5 MiB | NMBM Bad Block Pool | Driver-managed. Not a partition; do not format. |

The `ubi` figure is taken from the kernel log, which reports
`ubi0: attached mtd4 (name "ubi", size 140 MiB)`, and matches the device tree
(`reg = <0x580000 0x8c00000>` = 146,931,712 bytes). A verbatim capture is in
[`../analysis/bootlogs/partition-layout.log`](../analysis/bootlogs/partition-layout.log).

---

## 2. Production UBI Volume Layout (Slot 0)

When OpenWrt is installed into the active `ubi` partition (`0x00580000 - 0x0917FFFF`), UBI structures the space into three dynamic volumes:

```
ubi (140 MiB MTD Partition)
├── Volume 0: "kernel"      (FIT Image: Linux Kernel + DTB) ~ 5 MiB
├── Volume 1: "rootfs"      (Read-Only SquashFS filesystem)  ~ 25-35 MiB
└── Volume 2: "rootfs_data" (Read-Write UBIFS overlay)       ~ Remaining free space
```

### Volume Details:
* **`kernel`:** Staged Flattened Image Tree. Read by U-Boot via `ubi read 0x46000000 kernel`.
* **`rootfs`:** Compressed SquashFS image mounted as the root filesystem.
* **`rootfs_data`:** Formatted automatically as UBIFS on first boot; mounted via `overlayfs` over `/overlay` to store user settings persistently.

---

## 3. Base MAC Address Extraction (`mfg` Partition)

The device base MAC address is stored inside the `MFG` partition at byte offset `0x00`:
* **Offset:** `0x00`
* **Length:** 6 bytes (binary)
* **LAN / WAN Allocation:**
  - `WAN MAC` = Base MAC (Offset `0x00`)
  - `LAN MAC` = Base MAC + 1
* OpenWrt extracts it automatically at boot through
  `/etc/board.d/02_network`. The `jiorouter,ax6000-jidu6j01` case in the
  upstream `mediatek/filogic` `02_network` script already handles this board
  family and reads offset `0` of the `MFG` character device, so no board
  specific change is required:

  ```sh
  *)
      label_mac=$(get_mac_binary "$mfg_dev" 0)
      ;;
  ```
