#!/usr/bin/env python3
"""
sanitize-log.py - redact device identifiers from serial and boot logs

Removes values that are unique to one physical unit so a log can be
published, while leaving the technical content (version strings, build
dates, sizes, timings, register values) exactly as it appeared on the wire.

Redacted:
  * MAC addresses
  * serial numbers / device SNs
  * vendor build tags and their git hashes
  * IPv4 addresses
  * build-host identifiers (e.g. the host part of `builder@<hex>`)

Deliberately preserved:
  * TF-A / U-Boot version numbers and build dates
  * memory sizes, partition offsets, timings, register values
"""

import re
import sys

MAC_RE = re.compile(r'\b([0-9a-fA-F]{2}[:-]){5}[0-9a-fA-F]{2}\b')
IPV4_RE = re.compile(r'\b(\d{1,3}\.){3}\d{1,3}\b')
SN_RE = re.compile(
    r'\b(SN|RSN|rsn|Serial|serial|SerialNumber|DeviceId|DeviceID)'
    r'([:= ]+)'
    r'([A-Za-z0-9][A-Za-z0-9_-]{7,24})'
)

# Vendor build identifiers. The version number that follows (e.g. "v2.8")
# is deliberately left intact -- only the organisation tag and commit hash go.
VENDOR_TAGS = [
    re.compile(r'MTKJIO_ATF_U-Boot_[0-9a-f]+(?:-[0-9]+-g[0-9a-f]+)?-dirty'),
    re.compile(r'MTKJIO_ATF_U-Boot_[0-9a-f]+(?:-[0-9]+-g[0-9a-f]+)?'),
    re.compile(r'ATF-[0-9.]+-[0-9]{8}-[0-9a-f]+_Uboot-upstream-[0-9-]+'
               r'(?:-[0-9]+-g[0-9a-f]+)?-dirty'),
    re.compile(r'Uboot-upstream-[0-9-]+(?:-[0-9]+-g[0-9a-f]+)?-dirty'),
]

REDACT_VENDOR = '[VENDOR_TAG]'
REDACT_HOST = '[BUILD_HOST]'

# Build-host identifiers left in compiler banners, e.g.
# "(builder@3c872a6b86b6)" or "user@buildhost.example".
BUILDER_RE = re.compile(r'\(([A-Za-z0-9_.-]+)@[A-Za-z0-9_.-]{6,}\)')


def sanitize_line(line: str) -> str:
    line = SN_RE.sub(lambda m: f"{m.group(1)}{m.group(2)}[REDACTED_SERIAL]", line)
    line = MAC_RE.sub('XX:XX:XX:XX:XX:XX', line)
    line = IPV4_RE.sub('[IP]', line)
    for pat in VENDOR_TAGS:
        line = pat.sub(REDACT_VENDOR, line)
    line = BUILDER_RE.sub(lambda m: f'({m.group(1)}@{REDACT_HOST})', line)
    return line


def sanitize_file(src: str, dst: str) -> None:
    with open(src, 'r', encoding='utf-8', errors='replace') as fh:
        lines = fh.readlines()
    with open(dst, 'w', encoding='utf-8') as out:
        out.writelines(sanitize_line(ln) for ln in lines)
    print(f"sanitized {len(lines)} lines: {src} -> {dst}")


if __name__ == '__main__':
    if len(sys.argv) != 3:
        print(f"usage: {sys.argv[0]} <input.log> <output.log>")
        sys.exit(1)
    sanitize_file(sys.argv[1], sys.argv[2])
