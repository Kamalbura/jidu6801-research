#!/usr/bin/env python3
"""
parse-ubi-vt.py - Standalone UBI Volume Table Scanner
Parses UBI Erase Counter (EC) headers and Volume Identifier (VID) tables
from a standard NAND dump or MTD slice.
"""

import sys
import struct

def parse_ubi_slice(filepath, page_size=2048, oob_size=0, pages_per_block=64):
    stride = (page_size + oob_size) * pages_per_block
    with open(filepath, "rb") as f:
        data = f.read()

    total_blocks = len(data) // stride
    print(f"Scanning file: {filepath}")
    print(f"Total size: {len(data):,} bytes ({total_blocks} blocks of {stride} bytes)\n")

    found_volumes = 0
    for block_num in range(total_blocks):
        base = block_num * stride
        if base + 64 > len(data):
            break

        magic = data[base:base+4]
        if magic != b'UBI#':
            continue

        ec = struct.unpack(">Q", data[base+8:base+16])[0]
        vid_hdr_offset = struct.unpack(">I", data[base+16:base+20])[0]
        data_offset = struct.unpack(">I", data[base+20:base+24])[0]

        vid_base = base + vid_hdr_offset
        if vid_base + 32 <= len(data) and data[vid_base:vid_base+4] == b'UBI!':
            vol_id = struct.unpack(">I", data[vid_base+8:vid_base+12])[0]
            # UBI Layout Volume Table Volume ID is 0x7FFFFFFF
            if vol_id == 0x7FFFFFFF:
                print(f"[*] Found UBI Layout Volume Table at PEB {block_num} (Erase Counter: {ec})")
                tab = data[base + data_offset:]
                for i in range(0, 128 * 64, 64):
                    rec = tab[i:i+64]
                    if len(rec) >= 64 and rec[:4] == b'UBI!':
                        rvol = struct.unpack(">I", rec[4:8])[0]
                        rres = struct.unpack(">I", rec[8:12])[0]
                        rtype = rec[20]
                        rname = rec[24:56].split(b'\x00')[0].decode(errors='replace')
                        vol_type = "Dynamic" if rtype == 1 else "Static"
                        print(f"    Volume ID: {rvol:<3} | Name: {rname:<16} | Reserved LEBs: {rres:<5} | Type: {vol_type}")
                        found_volumes += 1
                print()

    if found_volumes == 0:
        print("No active UBI Layout Volume tables detected in the scanned image.")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print(f"Usage: {sys.argv[0]} <ubi_or_nand_image.bin>")
        sys.exit(1)
    parse_ubi_slice(sys.argv[1])
