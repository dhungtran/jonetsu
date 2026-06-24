# Restaurant Bon Printer

Tự động in bon bếp / sushi / bar khi nhận order từ Glide hoặc n8n.

---

## Cấu trúc project

```
restaurant-bon-printer/
├── bon_printer.py   # Logic dựng + gửi bon ESC/POS
├── app.py           # FastAPI web service (backend)
├── requirements.txt # Dependencies Python
├── .gitignore       # File nào không commit lên GitHub
└── README.md        # File này
```

---

## BƯỚC 0 — Git setup (bài tập hiện tại của bạn)

Đây là các lệnh Git đầu tiên bạn chạy trên một project thật.
Chạy lần lượt trong terminal (WSL hoặc Linux):

```bash
# 1. Tạo thư mục project và vào trong
mkdir restaurant-bon-printer
cd restaurant-bon-printer

# 2. Copy 4 file vào thư mục này (bon_printer.py, app.py, requirements.txt, .gitignore)

# 3. Khởi tạo Git repo
git init

# 4. Kiểm tra trạng thái — sẽ thấy 4 file "untracked"
git status

# 5. Stage tất cả file (thêm vào "vùng chuẩn bị commit")
git add .

# 6. Xem lại lần nữa — giờ file sẽ màu xanh (staged)
git status

# 7. Commit đầu tiên — message rõ ràng, viết ở thì hiện tại
git commit -m "feat: add bon printer service with FastAPI endpoint"

# 8. Xem lịch sử commit
git log --oneline
```

Tiếp theo, push lên GitHub:

```bash
# Tạo repo mới trên github.com (đặt tên: restaurant-bon-printer, để Private)
# Sau đó chạy lệnh GitHub gợi ý, dạng:

git remote add origin https://github.com/YOUR_USERNAME/restaurant-bon-printer.git
git branch -M main
git push -u origin main
```

**Checkpoint:** Vào github.com, vào repo của bạn, thấy 4 file ở đó = bạn đã hoàn thành bước này.

---

## BƯỚC 1 — Test offline (không cần máy in)

```bash
# Cài dependencies
pip install -r requirements.txt

# Chạy test dry_run — in mô phỏng ra terminal
python bon_printer.py
```

Bạn sẽ thấy 3 bon hiện ra trên màn hình cho bàn 5.

---

## BƯỚC 2 — Chạy web service

```bash
uvicorn app:app --host 0.0.0.0 --port 8000 --reload
```

Mở trình duyệt: http://localhost:8000/docs
→ FastAPI tự tạo trang test API tại đây (Swagger UI).

Test bằng curl:

```bash
curl -X POST http://localhost:8000/order \
  -H "Content-Type: application/json" \
  -d '{
    "ban": "5",
    "dry_run": true,
    "items": [
      {"ten": "Edamame",       "so_luong": 1, "tram": "bep"},
      {"ten": "Ramen bo",      "so_luong": 2, "tram": "bep"},
      {"ten": "Salmon nigiri", "so_luong": 4, "tram": "sushi"},
      {"ten": "Tra xanh",      "so_luong": 2, "tram": "bar"}
    ]
  }'
```

---

## BƯỚC 3 — Cắm máy in thật

1. Mua máy in nhiệt có cổng LAN (khuyên dùng Xprinter XP-C300H ~2.2 triệu)
2. Cắm vào router, vào trang admin router đặt IP tĩnh cho máy in
3. Sửa `PRINTER_CONFIG` trong `bon_printer.py`:
   ```python
   PRINTER_CONFIG = {
       "bep":   {"ip": "192.168.1.101", "port": 9100},
       "sushi": {"ip": "192.168.1.102", "port": 9100},
   }
   ```
4. Test kết nối:
   ```bash
   # Nếu có phản hồi = máy in đang online
   nc -zv 192.168.1.101 9100
   ```
5. Chạy lại curl trên với `"dry_run": false`

---

## Lộ trình học qua project này

| Giai đoạn   | Bạn học gì         | Áp dụng vào project                          |
|-------------|---------------------|----------------------------------------------|
| **Hiện tại**| Git & GitHub        | Init repo, commit, push lên GitHub           |
| Giai đoạn 3 | Python + SQL        | Thêm database lưu order theo bàn, tính bill  |
| Giai đoạn 4 | Backend + REST API  | Thêm auth, menu CRUD endpoint, kết nối Glide |
| Giai đoạn 5 | Claude Code         | Dùng AI để viết test, refactor, debug        |
| Giai đoạn 6 | AI Agents           | Agent tự suggest upsell, detect thất thoát   |

Mỗi giai đoạn bạn sẽ mở branch mới, làm xong merge vào main — đúng workflow Git thật.
