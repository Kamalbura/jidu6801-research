# Hardware Board Overview & Component Layout

## 1. PCB Silkscreen & Identification

* **Board Model:** `JIDU6801_MB_V1.0`
* **Form Factor:** Desktop Wi-Fi 6 Router with internal antennas and large aluminum heatsink
* **OEM Manufacturer:** Telpa / Gongjin
* **Main Silicon:** MediaTek MT7986A (Filogic 830)

---

## 2. Component Placement & IC Inventory

| Component Reference | Part Number | Manufacturer | Function |
|:---|:---|:---|:---|
| **U1 (SoC)** | MT7986AV | MediaTek | Quad-Core ARM Cortex-A53 @ 2.0 GHz SoC |
| **U2 (DRAM)** | DDR4-3200 | Nanya / Kingston | 512 MiB DDR4 System Memory |
| **U3 (Flash)** | W25N02KVZEIR | Winbond | 256 MiB 3.3V SPI-NAND Flash (WSON-8) |
| **U4 (Switch)** | MT7531AE | MediaTek | 5-Port Gigabit Ethernet Switch Core (1 WAN + 4 LAN) |
| **U6 (RFIC)** | MT7976C | MediaTek | Dual-Band Wi-Fi 6 DBDC Transceiver (4x4 2.4G + 4x4 5G) |
| **J1 (Power)** | 2.1mm DC Jack | Generic | 12V DC, 2.5A Power Input |
| **J2 (WAN)** | RJ-45 (1G) | Generic | Gigabit Ethernet WAN Port (MT7531 internal PHY) |
| **J3..J6 (LAN)**| 4x RJ-45 (1G) | Generic | Gigabit Ethernet LAN Ports 1 to 4 |
| **J7 (USB)** | USB 3.0 Type-A | Generic | SuperSpeed 5 Gbps USB Host Port |
| **SW1 (Reset)** | Tactile Switch | Generic | Factory Reset Button (GPIO 9) |
| **LED1 (Status)**| 3-Die RGB LED | Generic | Tri-Color Status Indicator (GPIO 12, 13, 14) |
| **J8 (UART)** | 3-Pad Test Header | N/A | Serial Console Header (TX, RX, GND) |

---

## 3. Physical Board Photography

High-resolution photographs documenting the physical board layout:

* **[PCB Top Overview](images/01_pcb_overview_top.jpg):** Shows the full router assembly, MT7986A SoC heatsink, MT7531 switch heatsink, 4x Gigabit LAN, 1x Gigabit WAN, Winbond SPI-NAND, and UART pads.
* **[Angled UART & Coax Detail](images/02_pcb_angled_uart.jpg):** Shows UART wiring with series resistor and RF antenna cabling.
* **[NAND & UART Macro](images/03_nand_and_uart_macro.jpg):** Detailed macro showing component placement between the Winbond WSON-8 chip and the labeled UART header.
* **[Winbond W25N02KV Package](images/04_winbond_w25n02kv_chip_macro.jpg):** Ultra-macro close-up confirming IC package markings `winbond 25N02KVZEIR 2417 635110800`.
* **[Complete Photography Catalog](images/README.md):** Complete indexed gallery including programmer setup and modchip installation.

