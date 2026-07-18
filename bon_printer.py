"""
bon_printer.py
==============
Module responsible for BUILDING the ticket content and SENDING it to the
thermal printer.

Split into 2 separate jobs:
  1. build_bon()  — produces ESC/POS bytes (knows nothing about the printer)
  2. print_bon()  — sends those bytes to the correct printer via IP:Port

Why split them? So during testing you only need to call build_bon() without
needing a real printer. This follows the "separation of concerns" principle —
each function does exactly one thing.
"""

import socket
import unicodedata
from datetime import datetime


# ─── PRINTER CONFIG ────────────────────────────────────────────────────────────
PRINTER_CONFIG = {
    "bep":   {"ip": "192.168.1.101", "port": 9100},
    "sushi": {"ip": "192.168.1.102", "port": 9100},
    # Add later: "bar": {"ip": "192.168.1.103", "port": 9100},
}

PRINT_TIMEOUT = 3


# ─── ESC/POS CONSTANTS ─────────────────────────────────────────────────────────
ESC  = b'\x1b'
GS   = b'\x1d'

INIT         = ESC + b'@'
BOLD_ON      = ESC + b'E\x01'
BOLD_OFF     = ESC + b'E\x00'
ALIGN_LEFT   = ESC + b'a\x00'
ALIGN_CENTER = ESC + b'a\x01'
DOUBLE_SIZE  = GS  + b'!\x11'
NORMAL_SIZE  = GS  + b'!\x00'
CUT          = GS  + b'V\x41\x03'
FEED_LINES   = lambda n: ESC + b'd' + bytes([n])


def strip_accents(text: str) -> str:
    nfkd = unicodedata.normalize('NFKD', text)
    return ''.join(c for c in nfkd if not unicodedata.combining(c))


def encode(text: str) -> bytes:
    return strip_accents(text).encode('ascii', errors='replace')


def _divider(char: str = '-', width: int = 32) -> bytes:
    return encode(char * width + '\n')


def build_bon(order: dict, tram: str) -> bytes:
    mon_cua_tram = [item for item in order["items"] if item["tram"] == tram]
    if not mon_cua_tram:
        raise ValueError(f"No items for station '{tram}' in this order.")

    other_items = [item for item in order["items"] if item["tram"] != tram]
    thoi_gian   = order.get("thoi_gian", datetime.now().strftime("%H:%M"))
    ghi_chu     = order.get("ghi_chu", "").strip()
    ten_tram    = {"bep": "BEP", "sushi": "SUSHI", "bar": "BAR"}.get(tram, tram.upper())

    # Cross-station tags
    tags = []
    if tram == "bep":
        if any(i["tram"] == "sushi" for i in other_items):
            tags.append(">> CO SUSHI")
    elif tram == "sushi":
        if any(i.get("category") == "Starters" for i in other_items):
            tags.append(">> CO VOR (Starters)")
        if any(i.get("category") in ("Mains", "Ramen") for i in other_items):
            tags.append(">> CO DO NONG (Mains/Ramen)")

    buf = b""
    buf += INIT
    buf += ALIGN_CENTER

    # Header
    buf += DOUBLE_SIZE + BOLD_ON
    buf += encode(f"--- {ten_tram} ---\n")
    buf += BOLD_OFF + NORMAL_SIZE

    # Table + time
    buf += encode(f"Ban: {order['ban']}          {thoi_gian}\n")
    buf += _divider()
    buf += ALIGN_LEFT

    # Items
    for item in mon_cua_tram:
        buf += BOLD_ON + encode(f"x{item.get('so_luong', 1)}") + BOLD_OFF
        buf += encode(f"  {item['ten']}\n")

    buf += _divider()

    # Note
    if ghi_chu:
        buf += BOLD_ON + encode(f"GHI CHU: {ghi_chu}\n") + BOLD_OFF
        buf += _divider()

    # Cross-station tags
    for tag in tags:
        buf += BOLD_ON + encode(f"{tag}\n") + BOLD_OFF

    buf += FEED_LINES(3)
    buf += CUT

    return buf


def print_bon(order: dict, tram: str, dry_run: bool = False) -> dict:
    if tram not in PRINTER_CONFIG and not dry_run:
        return {"ok": False, "message": f"No config found for station '{tram}'"}

    try:
        bon_bytes = build_bon(order, tram)
    except ValueError as e:
        return {"ok": False, "message": str(e)}

    if dry_run:
        print(f"\n{'='*40}")
        print(f"[DRY RUN] BON for station: {tram.upper()}")
        print(f"{'='*40}")
        print(f"Ban: {order['ban']}")
        mon_cua_tram = [i for i in order["items"] if i["tram"] == tram]
        for item in mon_cua_tram:
            print(f"  x{item.get('so_luong',1)}  {item['ten']}")
        print(f"{'='*40}")
        print(f"[{len(bon_bytes)} ESC/POS bytes would be sent to the printer]\n")
        return {"ok": True, "message": f"Dry run OK — {len(bon_bytes)} bytes"}

    cfg = PRINTER_CONFIG[tram]
    try:
        with socket.create_connection((cfg["ip"], cfg["port"]), timeout=PRINT_TIMEOUT) as sock:
            sock.sendall(bon_bytes)
        return {"ok": True, "message": f"Printed successfully to {cfg['ip']}:{cfg['port']}"}
    except socket.timeout:
        return {"ok": False, "message": f"Timeout connecting to printer {tram} ({cfg['ip']})"}
    except ConnectionRefusedError:
        return {"ok": False, "message": f"Printer {tram} refused connection — check IP and power"}
    except OSError as e:
        return {"ok": False, "message": f"Network error: {e}"}


# ─── RUN DIRECTLY FOR TESTING ───────────────────────────────────────────────────
if __name__ == "__main__":
    sample_order = {
        "ban": "5",
        "thoi_gian": "19:45",
        "ghi_chu": "khong hanh",
        "items": [
            {"ten": "Edamame",       "so_luong": 1, "tram": "bep", "category": "Starters"},
            {"ten": "Ramen bo",      "so_luong": 2, "tram": "bep", "category": "Ramen"},
            {"ten": "Salmon nigiri", "so_luong": 4, "tram": "sushi", "category": "Sushi"},
            {"ten": "Dragon roll",   "so_luong": 1, "tram": "sushi", "category": "Sushi"},
            {"ten": "Tra xanh",      "so_luong": 2, "tram": "bar", "category": "Drinks"},
        ]
    }

    print("Test printing tickets for all stations (dry_run=True):\n")
    for tram in ["bep", "sushi"]:
        result = print_bon(sample_order, tram, dry_run=True)
        print(f"Result [{tram}]: {result}\n")