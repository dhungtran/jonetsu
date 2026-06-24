"""
app.py
======
Web service nhận order từ Glide/n8n qua HTTP POST,
rồi gọi bon_printer để in ra đúng trạm.

Đây là "backend" của hệ thống — cầu nối giữa giao diện (Glide)
và phần cứng (máy in nhiệt).

Chạy server:
    uvicorn app:app --host 0.0.0.0 --port 8000 --reload

Test nhanh bằng curl (xem README):
    curl -X POST http://localhost:8000/order ...
"""

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
from typing import List
import logging

from bon_printer import print_bon

# ─── LOGGING ───────────────────────────────────────────────────────────────────
# Ghi lại mọi request để debug khi có lỗi giờ cao điểm
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s  %(levelname)s  %(message)s",
    datefmt="%H:%M:%S",
)
log = logging.getLogger(__name__)


# ─── APP ───────────────────────────────────────────────────────────────────────
app = FastAPI(
    title="Restaurant Bon Printer",
    description="Nhận order → tự chia trạm → in bon bếp/sushi/bar",
    version="1.0.0",
)


# ─── DATA MODELS (Pydantic) ────────────────────────────────────────────────────
# Pydantic tự validate dữ liệu đầu vào. Nếu thiếu field hoặc sai kiểu,
# FastAPI trả lỗi 422 với mô tả rõ ràng — không cần bạn viết if/else kiểm tra.

class OrderItem(BaseModel):
    ten: str = Field(..., description="Tên món", example="Ramen bo")
    so_luong: int = Field(1, ge=1, description="Số lượng, tối thiểu 1")
    tram: str = Field(..., description="bep | sushi | bar")

class Order(BaseModel):
    ban: str = Field(..., description="Số bàn", example="5")
    thoi_gian: str = Field(None, description="HH:MM, tự tạo nếu bỏ trống")
    items: List[OrderItem] = Field(..., min_items=1)

    # Cho phép dry_run=true khi test mà không cần máy in thật
    dry_run: bool = Field(False, description="True = in ra terminal, không gửi máy in")


# ─── ENDPOINTS ─────────────────────────────────────────────────────────────────

@app.get("/health")
def health_check():
    """Kiểm tra service đang chạy. n8n hoặc monitoring có thể ping endpoint này."""
    return {"status": "ok", "service": "bon-printer"}


@app.post("/order")
def receive_order(order: Order):
    """
    Nhận một order, tự phân loại theo trạm, in bon tới từng trạm.

    Flow:
        1. Nhóm items theo trạm
        2. Với mỗi trạm có món → gọi print_bon()
        3. Trả về kết quả tổng hợp

    Nếu MỌI trạm đều in thất bại → trả 503 để n8n có thể retry.
    Nếu CHỈ MỘT SỐ trạm thất bại → trả 207 (partial success).
    """
    order_dict = order.dict()
    log.info(f"Order nhận được — Bàn {order.ban} — {len(order.items)} món")

    # Xác định các trạm cần in
    tram_can_in = set(item.tram for item in order.items)
    valid_trams = {"bep", "sushi", "bar"}
    invalid = tram_can_in - valid_trams
    if invalid:
        raise HTTPException(
            status_code=400,
            detail=f"Trạm không hợp lệ: {invalid}. Chỉ chấp nhận: {valid_trams}"
        )

    # In tới từng trạm
    results = {}
    for tram in tram_can_in:
        result = print_bon(order_dict, tram, dry_run=order.dry_run)
        results[tram] = result
        if result["ok"]:
            log.info(f"  [{tram}] ✓ {result['message']}")
        else:
            log.error(f"  [{tram}] ✗ {result['message']}")

    # Tổng hợp kết quả
    all_ok     = all(r["ok"] for r in results.values())
    any_ok     = any(r["ok"] for r in results.values())
    failed     = [t for t, r in results.items() if not r["ok"]]

    if not any_ok:
        # Tất cả thất bại — n8n nên retry
        raise HTTPException(status_code=503, detail={"results": results})

    status_code = 200 if all_ok else 207  # 207 = Multi-Status (partial success)
    return {
        "ban": order.ban,
        "status": "ok" if all_ok else "partial",
        "failed_trams": failed,
        "results": results,
    }


@app.get("/")
def root():
    return {
        "message": "Restaurant Bon Printer v1.0",
        "docs": "/docs",      # FastAPI tự tạo trang docs tại đây
        "health": "/health",
    }
