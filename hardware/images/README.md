# JIDU6801 Hardware Photography & Verification Gallery

This directory contains high-resolution physical hardware photographs documenting the JioRouter AX6000 JIDU6801 PCB, component identification, SPI-NAND hardware programmer wiring, and the autonomous boot companion installation.

All images are verified free of barcodes, MAC address stickers, serial numbers, and carrier provisioning QR codes.

---

## Photographic Catalog

| File | Description & Technical Focus | Relevant Documentation |
|---|---|---|
| [`01_pcb_overview_top.jpg`](01_pcb_overview_top.jpg) | **Mainboard Top Overview:** Shows the MediaTek MT7986A Filogic 830 SoC heatsink, MT7531 switch heatsink, 4x Gigabit LAN ports (yellow), 1x 2.5G SGMII WAN port (blue), Winbond SPI-NAND location, and 4-pin UART pads. | [`hardware/board-overview.md`](../board-overview.md) |
| [`02_pcb_angled_uart.jpg`](02_pcb_angled_uart.jpg) | **UART Routing Detail:** Angled board view showing the 4-pin UART pads (`3.3V`, `TX`, `RX`, `GND`) wired with flying leads and inline series damping resistor on the RX line. | [`docs/uart.md`](../../docs/uart.md) |
| [`03_nand_and_uart_macro.jpg`](03_nand_and_uart_macro.jpg) | **NAND & UART Header Macro:** Close-up of the Winbond W25N02KV WSON-8 package (`U9040`), surrounding decoupling caps, test pads, and the labeled UART header silkscreen (`3.3V`, `RX`, `TX`, `GND`). | [`docs/nand.md`](../../docs/nand.md) |
| [`04_winbond_w25n02kv_chip_macro.jpg`](04_winbond_w25n02kv_chip_macro.jpg) | **Winbond W25N02KV Package Macro:** Extreme macro showing package markings `winbond 25N02KVZEIR 2417 635110800`, Pin 1 index dot, and adjacent PCB pads (`U9040`). | [`HARDWARE_FACTS.md`](../../HARDWARE_FACTS.md) |
| [`05_esp32s3_flasher_overview.jpg`](05_esp32s3_flasher_overview.jpg) | **ESP32-S3 Hardware Programmer:** ESP32-S3 DevKit-C mounted on a terminal breakout board resting on the router heatsink, with SPI flying leads connected to the NAND chip. | [`docs/esp32s3-nand.md`](../../docs/esp32s3-nand.md) |
| [`06_esp32s3_nand_wiring_detail.jpg`](06_esp32s3_nand_wiring_detail.jpg) | **SPI-NAND Solder Tap Points:** Detailed view of the flying leads (VCC, GND, CS, CLK, MOSI, MISO) soldered directly to the Winbond WSON-8 pads and adjacent test pads. | [`hardware/pinout.md`](../pinout.md) |
| [`07_workbench_stm32_uart_setup.jpg`](07_workbench_stm32_uart_setup.jpg) | **Laboratory Testbench:** Full research workbench showing the host development PC, USB-UART adapter, ST-Link V2, external STM32F103 boot companion, and router with active Ethernet links. | [`docs/testing.md`](../../docs/testing.md) |
| [`08_internal_modchip_installed.jpg`](08_internal_modchip_installed.jpg) | **Autonomous Modchip Internal Installation:** The companion microcontroller mounted internally inside the router enclosure, secured over the heatsink with live WAN/LAN cables connected. | [`docs/stm32f1-boot-companion.md`](../../docs/stm32f1-boot-companion.md) |

---

## Visual Verification Notes

1. **Silicon Markings:** Confirms 256MB SPI-NAND (`25N02KVZEIR`) manufactured in week 17 of 2024 (`2417`).
2. **UART Signals:** Standard 3.3V TTL levels. Pad order from left to right: `TX`, `RX`, `3.3V`, `GND` (as labeled on silkscreen).
3. **SPI Tap Points:** Taps into standard SPI bus lines (CS, CLK, DI, DO, VCC, GND) without desoldering the WSON-8 IC from the PCB.
