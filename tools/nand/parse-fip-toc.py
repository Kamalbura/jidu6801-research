#!/usr/bin/env python3
"""
parse-fip-toc.py - ARM Trusted Firmware Firmware Image Package (FIP) TOC Parser
Inspects the Table of Contents of a standard ARM TF-A FIP container.
"""

import sys
import struct
import uuid

FIP_UUID_MAP = {
    uuid.UUID("47d4086f-4c21-11e4-be78-3fcdc5a0c4f8"): "BL31 (TF-A Secure Monitor EL3)",
    uuid.UUID("d6d0eea7-fcea-d54b-9782-9934f234b6e4"): "BL33 (U-Boot Bootloader EL2)",
    uuid.UUID("033aeab6-4c22-11e4-8ee8-27fe480d192a"): "TBBR Trusted Key Certificate (Cert 7)",
    uuid.UUID("07d036ff-4c22-11e4-8025-7b563da08767"): "TBBR SoC Firmware Content Cert (Cert 9)",
    uuid.UUID("179d6722-4c22-11e4-b6c7-7380fb401b41"): "TBBR Non-Trusted Key Cert (Cert 11)",
    uuid.UUID("1b13137d-4c22-11e4-ac18-27dc53712966"): "TBBR Trusted Key Certificate (Cert 13)",
    uuid.UUID("261e96d1-4c22-11e4-a735-391f1bcf77f1"): "TBBR Non-Trusted Content Cert (Cert 15)",
}

TOC_HEADER_MAGIC = 0xAA640001

def parse_fip(filepath):
    with open(filepath, "rb") as f:
        data = f.read()

    if len(data) < 16:
        print("Error: File is too small to be a FIP image.")
        return 1

    name, serial, flags, flags2 = struct.unpack_from("<IIII", data, 0)
    if name != TOC_HEADER_MAGIC:
        print(f"Warning: Unexpected FIP TOC magic 0x{name:08X} (expected 0x{TOC_HEADER_MAGIC:08X})")

    print(f"FIP Container Header:")
    print(f"  Magic:     0x{name:08X}")
    print(f"  Serial:    0x{serial:08X}")
    print(f"  File Size: {len(data):,} bytes\n")
    print(f"{'Entry':<6} {'Offset':<12} {'Size (Bytes)':<14} {'UUID':<38} {'Known Image Role'}")
    print("-" * 90)

    offset = 16
    entry_idx = 0
    while offset + 40 <= len(data):
        raw_uuid = data[offset:offset+16]
        if raw_uuid == b'\x00' * 16:
            break

        u = uuid.UUID(bytes=raw_uuid)
        offset_addr, size, eflags = struct.unpack_from("<QQQ", data, offset + 16)
        role = FIP_UUID_MAP.get(u, "Unknown Component")

        print(f"{entry_idx:<6} 0x{offset_addr:<10X} {size:<14,} {str(u):<38} {role}")
        offset += 40
        entry_idx += 1

    print("\nEnd of Table of Contents.")
    return 0

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print(f"Usage: {sys.argv[0]} <fip_image.bin>")
        sys.exit(1)
    sys.exit(parse_fip(sys.argv[1]))
