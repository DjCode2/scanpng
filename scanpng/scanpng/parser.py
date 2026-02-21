#!/usr/bin/env python3
import zlib
from colorama import Fore, Style, init
import argparse

init()  # Colorama Windows-friendly

SIGNATURE_HEX = "89504e470d0a1a0a"

PNG_CHUNKS_HEX = {
    "ihdr": "49484452",
    "plte": "504c5445",
    "trns": "74524e53",
    "chrm": "6348524d",
    "gama": "67414d41",
    "iccp": "69434350",
    "sbit": "73424954",
    "srgb": "73524742",
    "bkgd": "624b4744",
    "hist": "68495354",
    "phys": "70485973",
    "splt": "73504c54",
    "time": "74494d45",
    "text": "74455874",
    "ztxt": "7a545874",
    "itxt": "69545874",
    "idat": "49444154",
    "iend": "49454e44",
}

def hex_data(path):
    with open(path, "rb") as f:
        data = f.read()
    return data.hex(), data

def pretty_hex(data, max_len=32):
    h = data.hex()
    if len(h) <= max_len:
        return h
    return h[:max_len//2] + "[…]" + h[-max_len//2:]

def compute_crc(chunk_type_bytes, chunk_data):
    crc_value = zlib.crc32(chunk_type_bytes + chunk_data) & 0xffffffff
    return crc_value.to_bytes(4, "big")

def parse_png_chunks(data_bytes):
    chunks = []

    if data_bytes[:8].hex() != SIGNATURE_HEX:
        print(Fore.RED + "[-] Signature PNG invalide" + Style.RESET_ALL)
        return chunks, 8

    print(Fore.CYAN + "[+] Signature PNG valide" + Style.RESET_ALL)
    offset = 8

    while offset + 8 <= len(data_bytes):

        length = int.from_bytes(data_bytes[offset:offset+4], "big")
        ctype_bytes = data_bytes[offset+4:offset+8]

        try:
            ctype = ctype_bytes.decode("ascii")
        except UnicodeDecodeError:
            print(Fore.RED + "[-] Type chunk non ASCII → stop" + Style.RESET_ALL)
            break

        data_start = offset + 8
        data_end = data_start + length
        crc_start = data_end
        crc_end = crc_start + 4

        if crc_end > len(data_bytes):
            print(Fore.RED + "[-] Chunk tronqué → stop" + Style.RESET_ALL)
            break

        chunk_data = data_bytes[data_start:data_end]
        crc_file = data_bytes[data_end:crc_end]
        crc_calc = compute_crc(ctype_bytes, chunk_data)

        ok = (crc_calc == crc_file)
        color = Fore.GREEN if ok else Fore.RED
        status = "OK" if ok else "BAD"

        print(f"""
{color}[+] {ctype}{Style.RESET_ALL}
    octets : {length}
    data   : {pretty_hex(chunk_data)}
    CRC    : fichier={crc_file.hex()} | calculé={crc_calc.hex()} [{color}{status}{Style.RESET_ALL}]
    offset : {offset}
""")

        chunks.append({
            "type": ctype,
            "length": length,
            "data": chunk_data,
            "crc_file": crc_file,
            "crc_calc": crc_calc,
            "offset": offset,
        })

        offset = crc_end

        if ctype == "IEND":
            print(Fore.GREEN + "[+] IEND atteint → fin logique PNG" + Style.RESET_ALL)
            break

    return chunks, offset

def build_chunk_dict(chunks):
    ordered = {name.upper(): [] for name in PNG_CHUNKS_HEX.keys()}

    for ch in chunks:
        t = ch["type"].upper()
        if t in ordered:
            ordered[t].append(ch)
        else:
            ordered.setdefault("OTHER", []).append(ch)

    return ordered

def get_chunk_content(chunk_dict, name):
    name = name.upper()
    if name not in chunk_dict or not chunk_dict[name]:
        return None
    return chunk_dict[name][0]["data"].hex()

def run_png_scan(): #anciennement le main
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "-path",
        type=str,
        required=True,
        help="Chemin vers le PNG"
    )
    args = parser.parse_args()

    data_hex, data_bytes = hex_data(args.path)
    chunks, end_offset = parse_png_chunks(data_bytes)
    chunk_dict = build_chunk_dict(chunks)

    if end_offset < len(data_bytes):
        extra = len(data_bytes) - end_offset
        print(Fore.YELLOW + f"\n[!] {extra} octets présents après IEND (données appendées)." + Style.RESET_ALL)

    gama = get_chunk_content(chunk_dict, "GAMA")
    if gama:
        print(Fore.CYAN + "\n[+] Contenu du chunk gAMA :" + Style.RESET_ALL, gama)