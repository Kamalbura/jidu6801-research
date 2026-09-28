# Hardware Pinout & Wiring Specifications

## 1. UART Console Pinout (J8)

Located adjacent to the SoC and main heatsink:

```text
Pad Number   Label    Signal Description         Voltage Level
──────────────────────────────────────────────────────────────
Pad 1        TX       MT7986A UART0 TX (Output)  3.3V TTL
Pad 2        RX       MT7986A UART0 RX (Input)   3.3V TTL
Pad 3        GND      System Ground              0.0V Reference
```

*Connection Rule:*
* Connect **TX** to USB-TTL **RX**.
* Connect **RX** to USB-TTL **TX**.
* Connect **GND** to USB-TTL **GND**.
* **Leave VCC unconnected.**

---

## 2. Push Buttons & Status LEDs

| Peripheral | Controller Pin | Active Logic | Circuit Design |
|:---|:---|:---|:---|
| **Reset Button** | GPIO 9 | Low (0V when pressed) | Pulled up to 3.3V via 10k resistor; pulled to GND when pressed |
| **Status Red** | GPIO 12 | Low (0V turns LED ON) | Open-drain / low-side drive with current-limiting resistor |
| **Status Green** | GPIO 13 | Low (0V turns LED ON) | Open-drain / low-side drive with current-limiting resistor |
| **Status Blue** | GPIO 14 | Low (0V turns LED ON) | Open-drain / low-side drive with current-limiting resistor |

---

## 3. SPI-NAND WSON-8 Pin Mapping (Winbond W25N02KV)

For bench recovery or external chip programmer attachment:

```text
       ┌───┬───┐
  /CS  │ 1 █ 8 │  VCC (3.3V)
   DO  │ 2   7 │  /HOLD (IO3)
  /WP  │ 3   6 │  CLK
  GND  │ 4   5 │  DI (IO0)
       └───┴───┘
```

* **Pin 1 (/CS):** Chip Select (GPIO / SNFI CS0)
* **Pin 2 (DO / IO1):** Data Out / IO1
* **Pin 3 (/WP / IO2):** Write Protect / IO2
* **Pin 4 (GND):** System Ground
* **Pin 5 (DI / IO0):** Data In / IO0
* **Pin 6 (CLK):** Serial Clock (up to 52 MHz)
* **Pin 7 (/HOLD / IO3):** Hold / IO3
* **Pin 8 (VCC):** 3.3V Power Rail

---

## 4. Hardware Solder & Wiring Photography

* **[UART Console Header](images/02_pcb_angled_uart.jpg):** Shows wired connection to `3.3V`, `TX`, `RX`, `GND` pads with damping resistor.
* **[NAND Solder Tap Points](images/06_esp32s3_nand_wiring_detail.jpg):** Shows flying leads soldered directly to the Winbond WSON-8 pads (VCC, GND, CS, CLK, DI, DO).
* **[ESP32-S3 Hardware Programmer Overview](images/05_esp32s3_flasher_overview.jpg):** Complete programmer assembly mounted to router chassis.
* **[Laboratory Testbench Setup](images/07_workbench_stm32_uart_setup.jpg):** Complete hardware setup with external STM32 companion, USB-UART, and active router.
* **[Internal Companion Modchip](images/08_internal_modchip_installed.jpg):** Autonomous HK32/STM32 microcontroller mounted permanently inside the router chassis.

