# STM32F1 Persistent Boot Companion Reference

## 1. Executive Summary & Purpose

When repurposing or recovering carrier-provisioned embedded networking hardware such as the **JioRouter AX6000 JIDU6801**, stock bootloaders may enforce authentication challenges, restrictive boot countdown timers, or proprietary memory checks that impede autonomous cold rebooting.

To establish a 100% reliable, hands-free, autonomous cold boot mechanism without modifying proprietary preloader partitions or relying on external host computers, this project developed an **external persistent boot-control companion** based on a low-cost STM32F1-class microcontroller.

---

## 2. Hardware Architecture & Specification

| Specification | Technical Value | Notes |
|:---|:---|:---|
| **Microcontroller Core** | ARM Cortex-M3 @ 8 MHz (Internal HSI) | Low-power, deterministic timing |
| **Silicon Implementation**| STM32F103C8T6 / HK32F103C8T6 | Standard "Blue Pill" development board (~₹150 / $2 USD) |
| **Flash Memory** | 64 KiB On-Chip Flash (`0x08000000`) | Independent of router NAND / UBI storage |
| **SRAM** | 20 KiB Internal SRAM (`0x20000000`) | Volatile execution space |
| **UART Peripheral** | USART1 (PA9 = TX, PA10 = RX) | 115,200 baud, 8N1 with RXNE hardware interrupt |
| **Status Indicator** | PC13 Active-Low LED | Visual heartbeat and state indication |
| **Power Supply** | 3.3V DC (drawn from router internal regulator) | Consumes < 15 mA during active negotiation |

---

## 3. Hardware Interconnect & Wiring Diagram

The companion microcontroller is soldered inside the router enclosure, interfacing directly with the router PCB's internal UART and 3.3V power rails:

```text
    ┌──────────────────────────────┐              ┌──────────────────────────────┐
    │     JIDU6801 Router PCB      │              │   STM32F103 / HK32F103 MCU   │
    │                              │              │                              │
    │  [ 3.3V Power Rail ] ────────┼──────────────┼────► [ VDD / 3.3V Pin ]      │
    │  [ Ground Plane    ] ────────┼──────────────┼────► [ GND / VSS Pin  ]      │
    │  [ MT7986 UART0 RX ] ◄───────┼──────────────┼───── [ PA9  / USART1 TX ]    │
    │  [ MT7986 UART0 TX ] ────────┼──────────────┼────► [ PA10 / USART1 RX ]    │
    │                              │              │                              │
    │                              │              │      [ BOOT0 -> GND ]        │
    └──────────────────────────────┘              └──────────────────────────────┘
```

### Critical Electrical Principles:
1. **Direct 3.3V Power Sharing:** Both the router SoC and the companion MCU power on simultaneously from the router's on-board 3.3V DC-DC switching regulator.
2. **Short Flying Leads ($\le 8\text{ cm}$):** Prevents signal degradation and ringing on high-speed serial edges (115200 baud).
3. **Common Ground Reference:** Ensures identical logic threshold levels between the MT7986A SoC I/O pads and STM32 GPIOs.

---

## 4. Firmware Implementation & State Machine

The companion firmware executes bare-metal C without an operating system, structured as an event-driven finite state machine (FSM):

```text
 [ State 0: POWER_ON_INIT ]
        │
        ├── Configure SysTick timer (1 ms interval)
        ├── Configure USART1 @ 115200 8N1 with NVIC RXNE interrupt
        └── 3 quick LED flashes on PC13 (Startup confirmation)
        │
        ▼
 [ State 1: PASSIVE_LISTEN ]
        │
        ├── Interrupt pushes incoming serial bytes into ring buffer: match_buf[256]
        ├── Gently toggles PC13 LED (150 ms period)
        └── Pattern matchers evaluate buffer contents
        │
        └── Pattern: Detects bootloader interactive prompt
               └── Transitions to State 3 (AUTOMATED_BOOT_SEQUENCE)
        │
        ▼
 [ State 3: AUTOMATED_BOOT_SEQUENCE ]
        │
        ├── Configures boot parameters in volatile memory
        ├── Attaches primary UBI storage volume (`ubi part ubi`)
        ├── Reads kernel FIT image into DRAM staging buffer (`ubi read 46000000 kernel`)
        └── Triggers kernel execution (`bootm 0x46000000`)
        │
        ▼
 [ State 4: WAIT_FOR_KERNEL ]
        │
        └── Polls serial buffer for "Linux", "OpenWrt", or "Starting kernel"
        │
        ▼
 [ State 5: AUTO_TRISTATE_AND_SLEEP ]
        │
        ├── Turns PC13 LED solidly ON (Boot success confirmed)
        ├── Reconfigures PA9 (TX) to Floating Input (High-Z)
        └── Enters infinite WFI (Wait-For-Interrupt) ultra-low-power sleep
```

---

## 5. Critical Engineering Detail: High-Z Bus Tri-Stating

In embedded hardware development, wiring an external microcontroller's TX line directly to a system's RX line creates a significant vulnerability: **bus contention**.

* If the MCU holds PA9 high or low in push-pull mode after Linux boots, an external technician plugging a USB-UART dongle into the router cannot type into the console because the MCU's output driver fights the dongle.
* If noise or an MCU reset occurs during router operation, spurious characters could be injected into the running Linux shell.

### High-Z Implementation in Firmware:
The moment the Linux kernel boot banner is detected, the firmware executes:

```c
/* Reconfigure PA9 (TX) from Alternate Function Push-Pull into Floating Input (High-Z) */
GPIOA_CRH &= ~(0xFu << 4);
GPIOA_CRH |=  (0x4u << 4); /* Floating Input Mode */

/* Enter ultra-low-power sleep */
while (1) {
    __asm__ volatile ("wfi");
}
```

By floating PA9, the companion microcontroller **electrically disconnects itself from the UART bus**. The serial console becomes immediately and completely available for external debugging or monitoring.

---

## 6. Empirical Validation & Test Evidence

| Test Case | Verification Methodology | Empirical Evidence | Result |
|:---|:---|:---|:---:|
| **Independent Power-On** | Power applied to 3.3V rail; monitor SysTick and PC13 LED | 3 distinct 80ms LED pulses observe on power application | **PASS** |
| **Boot Interface Detection** | Host serial monitoring harness | Boot prompt detected reliably within 500ms of bootloader init | **PASS** |
| **Command Dispatch Accuracy** | Monitor serial bus with UART logger | Kernel load commands dispatched sequentially with proper inter-command delays | **PASS** |
| **Rootfs Independence** | Repeatedly re-flash OpenWrt rootfs in NAND | Modchip execution remains unaffected (firmware in MCU flash `0x08000000`) | **PASS** |
| **Cold Power-Cycle Behavior** | Physical DC 12V barrel disconnect / reconnect (3 trials) | Trial 1: 18.4s, Trial 2: 18.2s, Trial 3: 18.5s to live OpenWrt | **PASS** |
| **UART Bus Release (High-Z)** | Attach USB-UART dongle after boot; interact with Linux shell | Bi-directional interactive root shell responsive; 0 bus contention | **PASS** |

---

## 7. Project Contribution vs. Prior Art

| Layer | Existing Prior Art | Project Contribution |
|:---|:---|:---|
| **MCU Silicon** | Generic ARM Cortex-M3 (STM32F103 / HK32F103) | Application as an embedded companion co-pilot for carrier router liberation |
| **Boot Mechanism** | Manual serial console operator typing commands | Automated event-driven state machine with zero human intervention |
| **Bus Safety** | Permanent output drivers causing line contention | Dynamic High-Z tri-stating after kernel detection |
| **Cost Profile** | Expensive commercial JTAG/UART programmers ($20–$100) | Ultra-low-cost (~₹150 / $2 USD) persistent solution |
