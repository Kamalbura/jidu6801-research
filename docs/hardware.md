# Hardware Architecture Reference

## 1. System-on-Chip (SoC) Overview

The JioRouter AX6000 JIDU6801 is built on the **MediaTek MT7986A (Filogic 830)** networking processor.

### SoC Specifications
* **CPU Cluster:** Quad-Core ARM Cortex-A53
* **Instruction Set:** ARMv8-A (64-bit / AArch64)
* **Frequency:** 2.0 GHz nominal core clock
* **L1 Cache:** 32 KiB I-Cache + 32 KiB D-Cache per core
* **L2 Cache:** 512 KiB shared unified cache
* **Interrupt Controller:** ARM GICv3 (`0x0c000000`)
* **Hardware Crypto Accelerator:** Inside Secure SafeXcel EIP-97 (AES, SHA, 3DES, IPsec offload, 4 rings)
* **Packet Processing Engine (PPE):** Dual Hardware Flow Offload Engines (HNAT v4) capable of wire-speed 2.5 Gbps packet routing
* **Wireless Ethernet Dispatcher (WED):** Offloads Wi-Fi ring descriptors directly to hardware DMA queues, bypassing host CPU softirqs

---

## 2. Memory Subsystem

* **System DRAM:** 512 MiB DDR4-3200 SDRAM
* **Physical Address Range:** `0x40000000` to `0x5fffffff`
* **Bus Width:** 16-bit DDR4 interface
* **Memory Carveouts:**
  - `0x42ff0000 - 0x42ffffff`: Ramoops persistent console logging (64 KiB)
  - `0x43000000 - 0x4303ffff`: ARM Trusted Firmware BL31 Secure Monitor (256 KiB)
  - `0x4fc00000 - 0x4fffffff`: Wireless Offload CPU (WO-CPU) firmware and shared DMA rings (4 MiB)

---

## 3. Storage Subsystem

* **Flash Controller:** MediaTek Serial NAND Flash Interface (SNFI) at MMIO `0x11005000`
* **Flash Chip:** Winbond W25N02KVZEIR (256 MiB / 2 Gbit SPI-NAND)
* **Package:** WSON-8 (8mm × 6mm)
* **Bus Interface:** SPI Quad-IO @ 52 MHz
* **Geometry:** 2,048 Physical Eraseblocks (128 KiB per PEB), 64 pages per block, 2,048 bytes data + 128 bytes OOB per page
* **Bad Block Translation:** MediaTek NMBM (NAND Multi-Block Management) hardware abstraction layer

---

## 4. Networking & Switch Topology

```
                  ┌──────────────────────────────────────────────┐
                  │          MediaTek MT7986A (Filogic 830)      │
                  │                     (GMAC0)                  │
                  └───────────────────────┬──────────────────────┘
                                          │ 2500Base-X SerDes
                                          ▼
                            ┌──────────────────────────┐
                            │     MT7531AE Switch      │
                            │       (MDIO 0x1f)        │
                            └─┬───┬───┬───┬───┬────────┘
                              │   │   │   │   │
                             WAN LAN1 LAN2 LAN3 LAN4
                             (1G)(1G) (1G) (1G) (1G)
```

* **Ethernet Switch:** MediaTek MT7531AE distributed switch architecture (DSA) chip linked to SoC GMAC0 via a 2.5 Gbps SGMII/2500Base-X CPU link. Provides 5 Gigabit Ethernet (10/100/1000Base-T) RJ-45 jacks: 1 WAN port (Port 0) and 4 LAN ports (Ports 1 to 4).

---

## 5. Wireless Subsystem (Wi-Fi 6 / 802.11ax)

* **RF Transceiver:** MediaTek MT7976C Dual-Band Dual-Concurrent (DBDC) RFIC
* **2.4 GHz Band (MT7976GN):**
  - 4 Transmit × 4 Receive (4T4R) MIMO
  - Channel Bandwidth: 20 MHz / 40 MHz (HE40)
  - Maximum Physical Link Rate: Up to 1,148 Mbps
* **5.0 GHz Band (MT7976AN):**
  - 4 Transmit × 4 Receive (4T4R) MIMO
  - Channel Bandwidth: 20 MHz / 40 MHz / 80 MHz / 160 MHz contiguous (HE160)
  - Maximum Physical Link Rate: Up to 4,804 Mbps
  - Full DFS radar detection and Dynamic Frequency Selection support
* **Calibration:** Individual per-device RF calibration matrix loaded from MTD partition `Factory` (`0x180000`).

---

## 6. Power & Peripherals

* **Power Supply:** External 12V DC, 2.5A power adapter (barrel connector, 5.5mm outer, 2.1mm inner, center-positive).
* **Power Conversion:** On-board buck regulators generating 5.0V (USB VBUS), 3.3V (I/O, flash, switch), 1.8V (DDR4 VDDQ, analog PHYs), and 0.9V (core VDD).
* **USB:** 1× USB 3.0 Type-A host port (xHCI controller @ `0x11200000`).
* **LEDs:** 1× RGB tri-color status indicator (Red: GPIO 12, Green: GPIO 13, Blue: GPIO 14).
* **Reset Button:** Momentary tactile push switch on rear I/O panel (GPIO 9, active low).
