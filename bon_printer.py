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
# Change this IP once you set a static IP for the printer on the router.
PRINTER_CONFIG = {
    "bep":   {"ip": "192.168.1.101", "port": 9100},
    "sushi": {"ip": "192.168.1.102", "port": 9100},
    # Add later: "bar": {"ip": "192.168.1.103", "port": 9100},
}

# Printer connection timeout (seconds). Long enough for rush hour, but won't
# hang forever if the printer is off.
PRINT_TIMEOUT = 3


# ─── ESC/POS CONSTANTS ─────────────────────────────────────────────────────────
# This is the thermal printer's "language" — special bytes are commands.
ESC  = b'\x1b'
GS   = b'\x1d'

INIT         = ESC + b'@'           # Reset printer to its initial state
BOLD_ON      = ESC + b'E\x01'      # Turn on bold text
BOLD_OFF     = ESC + b'E\x00'      # Turn off bold text
ALIGN_LEFT   = ESC + b'a\x00'
ALIGN_CENTER = ESC + b'a\x01'
DOUBLE_SIZE  = GS  + b'!\x11'      # Double-size text (headers)
NORMAL_SIZE  = GS  + b'!\x00'
CUT          = GS  + b'V\x41\x03'  # Cut paper (if the printer has a cutter)
FEED_LINES   = lambda n: ESC + b'd' + bytes([n])  # Feed n blank lines


def strip_accents(text: str) -> str:
    """
    Strip Vietnamese diacritics since cheap thermal printers usually only
    support ASCII and can't render Unicode. Example: 'Phở bò' → 'Pho bo'.

    If your printer supports UTF-8, drop this function and encode as utf-8
    directly.
    """
    nfkd = unicodedata.normalize('NFKD', text)
    return ''.join(c for c in nfkd if not unicodedata.combining(c))


def encode(text: str) -> bytes:
    """Convert a string to bytes to send to the printer."""
    return strip_accents(text).encode('ascii', errors='replace')


def _divider(char: str = '-', width: int = 32) -> bytes:
    """Print a horizontal divider line."""
    return encode(char * width + '\n')


def build_bon(order: dict, tram: str) -> bytes:
    """
    Build the ticket content as ESC/POS bytes.

    Params:
        order (dict): {
            "ban": "5",
            "thoi_gian": "14:32",   # optional, auto-generated if missing
            "items": [
                {"ten": "Ramen bo", "so_luong": 2, "tram": "bep"},
                {"ten": "Salmon nigiri", "so_luong": 4, "tram": "sushi"},
                {"ten": "Tra xanh", "so_luong": 1, "tram": "bar"},
            ]
        }
        tram (str): "bep" | "sushi" | "bar" — only print items for this station

    Returns:
        bytes: content ready to send to the printer
    """
    # Keep only the items belonging to this station
    mon_cua_tram = [item for item in order["items"] if item["tram"] == tram]

    if not mon_cua_tram:
        raise ValueError(f"No items for station '{tram}' in this order.")

    thoi_gian = order.get("thoi_gian", datetime.now().strftime("%H:%M"))
    ten_tram  = {"bep": "BEP", "sushi": "SUSHI", "bar": "BAR"}.get(tram, tram.upper())

    buf = b""
    buf += INIT
    buf += ALIGN_CENTER

    # Header: station name, large and bold
    buf += DOUBLE_SIZE
    buf += BOLD_ON
    buf += encode(f"--- {ten_tram} ---\n")
    buf += BOLD_OFF
    buf += NORMAL_SIZE

    # Table + time info
    buf += encode(f"Ban: {order['ban']}          {thoi_gian}\n")
    buf += _divider()
    buf += ALIGN_LEFT

    # Item list
    for item in mon_cua_tram:
        so_luong = item.get("so_luong", 1)
        ten      = item["ten"]
        buf += BOLD_ON + encode(f"x{so_luong}") + BOLD_OFF
        buf += encode(f"  {ten}\n")

    buf += _divider()
    buf += ALIGN_CENTER
    buf += encode(f"Total: {len(mon_cua_tram)} mon\n")

    # Extra feed so it's easy to tear off, then cut
    buf += FEED_LINES(3)
    buf += CUT

    return buf


def print_bon(order: dict, tram: str, dry_run: bool = False) -> dict:
    """
    Call build_bon() then send the result to the station's printer.

    Params:
        dry_run (bool): If True, print to the terminal instead of sending to a
                        real printer. Use this for testing or when there's no
                        printer yet.

    Returns:
        dict: {"ok": True/False, "message": "..."}
    """
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

    # Send to the real printer over a TCP socket
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
# When you run `python bon_printer.py`, this block executes.
# When the module is imported by app.py, this block is skipped.
if __name__ == "__main__":
    sample_order = {
        "ban": "5",
        "thoi_gian": "19:45",
        "items": [
            {"ten": "Edamame",       "so_luong": 1, "tram": "bep"},
            {"ten": "Ramen bo",      "so_luong": 2, "tram": "bep"},
            {"ten": "Com sushi",     "so_luong": 1, "tram": "bep"},
            {"ten": "Salmon nigiri", "so_luong": 4, "tram": "sushi"},
            {"ten": "Dragon roll",   "so_luong": 1, "tram": "sushi"},
            {"ten": "Tra xanh",      "so_luong": 2, "tram": "bar"},
        ]
    }

    print("Test printing tickets for all stations (dry_run=True):\n")
    for tram in ["bep", "sushi", "bar"]:
        result = print_bon(sample_order, tram, dry_run=True)
        print(f"Result [{tram}]: {result}\n")
