# UART Serial Console Reference & Pinout Guide

## 1. Electrical Specifications

The serial console on the JioRouter AX6000 JIDU6801 is connected directly to MediaTek MT7986A **UART0**.

| Parameter | Specification | Warning / Safety Note |
|:---|:---|:---|
| **Signaling Level** | **3.3V TTL Logic** | **DO NOT connect RS-232 levels (±12V) or 5V logic directly.** Doing so will damage the SoC I/O pads. |
| **Baud Rate** | **115,200 baud** | Standard high-speed console rate. |
| **Data Bits** | 8 | Standard byte width. |
| **Parity** | None | No parity bit. |
| **Stop Bits** | 1 | 1 stop bit (8N1). |
| **Flow Control** | None (Disabled) | RTS/CTS and XON/XOFF are not connected. |

---

## 2. Physical Pinout & Header Location

On the top side of the primary PCB near the MT7986A SoC and heatsink assembly, locate the 3-pin serial console testpads / through-holes:

```
PCB Test Points:
   ┌───────┐
   │ ( ) 1 │  TX   (MT7986A UART0 TX - Connect to USB Adapter RX)
   │ ( ) 2 │  RX   (MT7986A UART0 RX - Connect to USB Adapter TX)
   │ ( ) 3 │  GND  (System Ground     - Connect to USB Adapter GND)
   └───────┘
```

### Wiring Diagram to USB-to-TTL Adapter:
```text
Router PCB Pad 1 (TX)   ──────►  USB-TTL Adapter RX Pin
Router PCB Pad 2 (RX)   ◄──────  USB-TTL Adapter TX Pin
Router PCB Pad 3 (GND)  ───────  USB-TTL Adapter GND Pin
                         [DO NOT CONNECT VCC / 3.3V / 5V]
```

*Important Safety Rule:* Never connect the VCC / 3.3V pin from your USB-TTL adapter to the router. The router powers its own rails from its 12V DC input. Connecting an external power rail to the 3.3V bus risks ground loops and voltage contention.

---

## 3. Terminal Emulator Configuration

### Using Minicom (Linux):
```bash
minicom -D /dev/ttyUSB0 -b 115200
```

### Using Picocom (Linux):
```bash
picocom -b 115200 /dev/ttyUSB0
```

### Halting the Bootloader:
When the router powers on, the following banner will appear in your terminal
(verbatim excerpt, identifiers redacted — see
[`../analysis/bootlogs/boot-chain.log`](../analysis/bootlogs/boot-chain.log):
```text
NOTICE:  BL2: v2.8(release):[VENDOR_TAG]
NOTICE:  BL2: Built : 14:02:23, Dec  2 2024
...
NOTICE:  BL2: Booting BL31
NOTICE:  BL31: v2.8(release):[VENDOR_TAG]
NOTICE:  BL31: Built : 02:19:47, Jul  1 2023
...
U-Boot 2023.04 (Jul 01 2023 - 02:17:43 +0530)

CPU:   MediaTek MT7986
Model: mt7986-rfb
DRAM:  512 MiB
```
Press **Enter** during the autoboot countdown to drop into the interactive
`MT7986> ` bootloader shell. The countdown is short (about 2 seconds), so a key
press must be timed; a scripted `Enter` spammer is more reliable than manual
typing.
