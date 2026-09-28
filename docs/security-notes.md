# Security Notes & Responsible Disclosure Policy

## 1. Ethical Research Principles

This project focuses on **hardware interoperability, educational documentation, and e-waste reduction**. Our goal is to enable users to run modern, secure, open-source software (OpenWrt) on personally owned hardware.

### Non-Goals:
* We do **not** publish exploit payloads, brute-force utilities, or attack scripts.
* We do **not** target, inspect, or intercept telecommunications provider infrastructure or other users' devices.
* We do **not** disclose or redistribute private cryptographic keys, certificates, or subscriber credentials.

---

## 2. Threat Modeling & Boundary Analysis

During embedded hardware analysis of carrier-provisioned CPEs, several security boundaries were observed:

### 2.1 Boot Chain Security (Secure Boot / TBBR)
* The MediaTek MT7986A SoC incorporates one-time programmable (OTP) eFuses storing a 256-bit Root of Trust Public Key (ROTPK) hash.
* ARM Trusted Firmware BL2 validates the Firmware Image Package (FIP) against Certificate 7 before loading BL31 and U-Boot.
* Any unauthorized modification of the FIP partition on flash causes BL2 to halt boot and trigger a hardware watchdog reset.
* **OpenWrt Upstream Scope:** Upstream OpenWrt does not modify the vendor FIP partition or bypass hardware root-of-trust checks. OpenWrt installs cleanly into the standard user partitions (`ubi`) managed by the bootloader.

### 2.2 Console Access Boundaries
* The vendor bootloader implements a serial console password challenge.
* While the password derivation formulas or static keys were analyzed during lab recovery, weaponized auto-login scripts and internal credential extraction tools are **intentionally withheld** from the upstream OpenWrt patch set.

---

## 3. What This Repository Deliberately Does Not Contain

Some findings are useful to the maintainer but are not distributed here,
either because they are not the project's to publish or because publishing
them would create risk without adding engineering value.

| Withheld | Reason |
|:---|:---|
| Raw NAND dumps and full-chip images | Contain the vendor's proprietary firmware. Large, and not the project's to redistribute. |
| FIP / bootloader binaries and the stock root filesystem | Vendor proprietary images. Only their **SHA-256** is published, so a reader can verify a dump they already hold. See [`../analysis/hashes/sha256sums.txt`](../analysis/hashes/sha256sums.txt). |
| Bootloader console credential material and auto-login tooling | Useful only for bypassing an access control the vendor put in place. The OpenWrt device support does not need it. |
| Escalation or persistence tooling for the stock firmware | Out of scope for interoperability work. |
| Subscriber, ISP or TR-069 account data | Not collected, not needed, and not this project's to hold. |
| Per-unit identifiers (MAC addresses, serial numbers) in published logs | Stripped by [`../tools/sanitize-log.py`](../tools/sanitize-log.py). Only their *offsets* and *lengths* are documented. |

The published captures in [`../analysis/bootlogs/`](../analysis/bootlogs/) are
redacted with that tool. It removes MAC addresses, serial numbers, IPv4
addresses and vendor build tags, and it deliberately **preserves** version
strings, build dates, sizes, offsets and timings, because those are the parts
a reader needs in order to check a claim. If you add a log, re-run the tool
rather than hand-editing.

---

## 4. Responsible Disclosure Statement

If any genuine security vulnerability in vendor software, hardware architecture, or network protocols is discovered during research:
1. It is documented privately.
2. It is reported directly to the affected vendor and relevant security coordination bodies (e.g. CERT / vendor security contacts) with a standard 90-day coordinated disclosure period.
3. It is **never** included in public OpenWrt device-support commits or pull requests.
