"""
bon_printer.py
==============
Module phụ trách DỰNG NỘI DUNG bon và GỬI TỚI máy in nhiệt.

Tách thành 2 việc riêng:
  1. build_bon()  — tạo ra bytes ESC/POS (không biết gì về máy in)
  2. print_bon()  — gửi bytes đó tới đúng máy in qua IP:Port

Tại sao tách? Vì khi test bạn chỉ cần gọi build_bon() mà không cần máy in thật.
Đây là nguyên tắc "separation of concerns" — mỗi hàm làm đúng một việc.
"""

import socket
import unicodedata
from datetime import datetime


# ─── CẤU HÌNH MÁY IN ──────────────────────────────────────────────────────────
# Đổi IP này khi bạn đặt IP tĩnh cho máy in trong router.
PRINTER_CONFIG = {
    "bep":   {"ip": "192.168.1.101", "port": 9100},
    "sushi": {"ip": "192.168.1.102", "port": 9100},
    # Mở rộng sau: "bar": {"ip": "192.168.1.103", "port": 9100},
}

# Timeout kết nối máy in (giây). Đủ dài cho giờ cao điểm, không chờ mãi nếu máy tắt.
PRINT_TIMEOUT = 3


# ─── ESC/POS CONSTANTS ─────────────────────────────────────────────────────────
# Đây là "ngôn ngữ" của máy in nhiệt. Byte đặc biệt ra lệnh cho máy in.
ESC  = b'\x1b'
GS   = b'\x1d'

INIT         = ESC + b'@'           # Reset máy in về trạng thái ban đầu
BOLD_ON      = ESC + b'E\x01'      # Bật chữ đậm
BOLD_OFF     = ESC + b'E\x00'      # Tắt chữ đậm
ALIGN_LEFT   = ESC + b'a\x00'
ALIGN_CENTER = ESC + b'a\x01'
DOUBLE_SIZE  = GS  + b'!\x11'      # Chữ to x2 (tiêu đề)
NORMAL_SIZE  = GS  + b'!\x00'
CUT          = GS  + b'V\x41\x03'  # Cắt giấy (nếu máy có dao cắt)
FEED_LINES   = lambda n: ESC + b'd' + bytes([n])  # Cuộn n dòng trắng


def strip_accents(text: str) -> str:
    """
    Bỏ dấu tiếng Việt vì máy in nhiệt rẻ thường dùng bảng mã ASCII,
    không render được Unicode. Ví dụ: 'Phở bò' → 'Pho bo'.

    Nếu máy in của bạn hỗ trợ UTF-8, bỏ hàm này và encode thẳng utf-8.
    """
    nfkd = unicodedata.normalize('NFKD', text)
    return ''.join(c for c in nfkd if not unicodedata.combining(c))


def encode(text: str) -> bytes:
    """Chuyển chuỗi → bytes để gửi vào máy in."""
    return strip_accents(text).encode('ascii', errors='replace')


def _divider(char: str = '-', width: int = 32) -> bytes:
    """In một đường kẻ ngang."""
    return encode(char * width + '\n')


def build_bon(order: dict, tram: str) -> bytes:
    """
    Dựng nội dung bon thành bytes ESC/POS.

    Params:
        order (dict): {
            "ban": "5",
            "thoi_gian": "14:32",   # tuỳ chọn, tự tạo nếu thiếu
            "items": [
                {"ten": "Ramen bò", "so_luong": 2, "tram": "bep"},
                {"ten": "Salmon nigiri", "so_luong": 4, "tram": "sushi"},
                {"ten": "Trà xanh", "so_luong": 1, "tram": "bar"},
            ]
        }
        tram (str): "bep" | "sushi" | "bar" — chỉ in món thuộc trạm này

    Returns:
        bytes: nội dung sẵn sàng gửi tới máy in
    """
    # Lọc chỉ lấy món của trạm này
    mon_cua_tram = [item for item in order["items"] if item["tram"] == tram]

    if not mon_cua_tram:
        raise ValueError(f"Không có món nào cho trạm '{tram}' trong order này.")

    thoi_gian = order.get("thoi_gian", datetime.now().strftime("%H:%M"))
    ten_tram  = {"bep": "BEP", "sushi": "SUSHI", "bar": "BAR"}.get(tram, tram.upper())

    buf = b""
    buf += INIT
    buf += ALIGN_CENTER

    # Header: tên trạm to, rõ
    buf += DOUBLE_SIZE
    buf += BOLD_ON
    buf += encode(f"--- {ten_tram} ---\n")
    buf += BOLD_OFF
    buf += NORMAL_SIZE

    # Thông tin bàn + giờ
    buf += encode(f"Ban: {order['ban']}          {thoi_gian}\n")
    buf += _divider()
    buf += ALIGN_LEFT

    # Danh sách món
    for item in mon_cua_tram:
        so_luong = item.get("so_luong", 1)
        ten      = item["ten"]
        buf += BOLD_ON + encode(f"x{so_luong}") + BOLD_OFF
        buf += encode(f"  {ten}\n")

    buf += _divider()
    buf += ALIGN_CENTER
    buf += encode(f"Total: {len(mon_cua_tram)} mon\n")

    # Cuộn thêm để dễ xé, cắt giấy
    buf += FEED_LINES(3)
    buf += CUT

    return buf


def print_bon(order: dict, tram: str, dry_run: bool = False) -> dict:
    """
    Gọi build_bon() rồi gửi tới máy in của trạm.

    Params:
        dry_run (bool): Nếu True, chỉ in ra terminal thay vì gửi máy in thật.
                        Dùng khi test hoặc khi chưa có máy in.

    Returns:
        dict: {"ok": True/False, "message": "..."}
    """
    if tram not in PRINTER_CONFIG and not dry_run:
        return {"ok": False, "message": f"Không tìm thấy config cho trạm '{tram}'"}

    try:
        bon_bytes = build_bon(order, tram)
    except ValueError as e:
        return {"ok": False, "message": str(e)}

    if dry_run:
        print(f"\n{'='*40}")
        print(f"[DRY RUN] BON cho tram: {tram.upper()}")
        print(f"{'='*40}")
        print(f"Ban: {order['ban']}")
        mon_cua_tram = [i for i in order["items"] if i["tram"] == tram]
        for item in mon_cua_tram:
            print(f"  x{item.get('so_luong',1)}  {item['ten']}")
        print(f"{'='*40}")
        print(f"[{len(bon_bytes)} bytes ESC/POS se duoc gui toi may in]\n")
        return {"ok": True, "message": f"Dry run OK — {len(bon_bytes)} bytes"}

    # Gửi tới máy in thật qua TCP socket
    cfg = PRINTER_CONFIG[tram]
    try:
        with socket.create_connection((cfg["ip"], cfg["port"]), timeout=PRINT_TIMEOUT) as sock:
            sock.sendall(bon_bytes)
        return {"ok": True, "message": f"In thanh cong toi {cfg['ip']}:{cfg['port']}"}
    except socket.timeout:
        return {"ok": False, "message": f"Timeout khi ket noi may in {tram} ({cfg['ip']})"}
    except ConnectionRefusedError:
        return {"ok": False, "message": f"May in {tram} tu choi ket noi — kiem tra IP va nguon dien"}
    except OSError as e:
        return {"ok": False, "message": f"Loi mang: {e}"}


# ─── CHẠY TRỰC TIẾP ĐỂ TEST ────────────────────────────────────────────────────
# Khi bạn chạy `python bon_printer.py`, đoạn này thực thi.
# Khi module được import vào app.py, đoạn này bị bỏ qua.
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

    print("Test in bon cho tat ca tram (dry_run=True):\n")
    for tram in ["bep", "sushi", "bar"]:
        result = print_bon(sample_order, tram, dry_run=True)
        print(f"Ket qua [{tram}]: {result}\n")
