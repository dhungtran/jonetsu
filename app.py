from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel, Field
from typing import List
from supabase import create_client
from dotenv import load_dotenv
import os
import logging
import uuid
from bon_printer import print_bon


load_dotenv()

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
log = logging.getLogger(__name__)

app = FastAPI()

supabase = create_client(os.getenv("SUPABASE_URL"), os.getenv("SUPABASE_KEY"))

app.mount("/static", StaticFiles(directory="static"), name="static")

class OrderItem(BaseModel):
    mon_id: int
    so_luong: int = Field(1, ge=1)

class Order(BaseModel):
    ban: int
    items: List[OrderItem]
    dry_run: bool = False
    ghi_chu: str = ""


@app.get("/")
def root():
    return FileResponse("static/role.html")

@app.get("/health")
def health():
    return {"status": "ok"}

@app.get("/menu")
def get_menu():
    data = supabase.table("menu").select("*").order("ten", desc=False).execute()
    return data.data

@app.post("/order")
def receive_order(order: Order):
    # Tra Supabase để lấy tên món và trạm
    order_items = []
    order_id = str(uuid.uuid4())
    for item in order.items:
        result = supabase.table("menu").select("*").eq("id", item.mon_id).execute()
        if not result.data:
            raise HTTPException(status_code=404, detail=f"Không tìm thấy món id {item.mon_id}")
        menu_item = result.data[0]
        order_items.append({
            "ten": menu_item["ten"],
            "so_luong": item.so_luong,
            "tram": menu_item["tram"]
        })
       
        supabase.table("orders").insert({
            "ban": order.ban,
            "ten": menu_item["ten"],
            "so_luong": item.so_luong,
            "tram": menu_item["tram"],
            "order_id": order_id,
            "ghi_chu": order.ghi_chu,
            "category": menu_item["category"],
            "gia": menu_item["gia"],
        }).execute()

    order_dict = {"ban": str(order.ban), "items": order_items}
    tram_can_in = set(i["tram"] for i in order_items)

    results = {}
    for tram in tram_can_in:
        results[tram] = print_bon(order_dict, tram, dry_run=order.dry_run)

    all_ok = all(r["ok"] for r in results.values())
    any_ok = any(r["ok"] for r in results.values())

    if not any_ok:
        raise HTTPException(status_code=503, detail=results)

    return {
        "ban": order.ban,
        "status": "ok" if all_ok else "partial",
        "results": results
    }

@app.get("/orders")
def get_orders(tram: str = None):
    query = supabase.table("orders").select("*").order("thoi_gian", desc=False)
    if tram:
        query = query.eq("tram", tram)
    data = query.execute()
    return data.data

@app.patch("/orders/{id}/done")
def mark_done(id: int):
    supabase.table("orders").update({"trang_thai": "xong"}).eq("id", id).execute()
    return {"status": "ok"}

@app.patch("/menu/{item_id}/available")
def toggle_available(item_id: int):
    item = supabase.table("menu").select("available").eq("id", item_id).execute().data[0]
    new_status = not item["available"]
    supabase.table("menu").update({"available": new_status}).eq("id", item_id).execute()
    return {"available": new_status}

@app.get("/tables")
def get_tables():
    data = supabase.table("orders").select("*").neq("trang_thai", "paid").order("thoi_gian", desc=False).execute()
    return data.data

@app.patch("/tables/{ban}/paid")
def mark_table_paid(ban: int):
    supabase.table("orders").update({"trang_thai": "paid"}).eq("ban", ban).neq("trang_thai", "paid").execute()
    return {"status": "ok"}

@app.patch("/orders/{id}/undo")
def mark_undo(id: int):
    supabase.table("orders").update({"trang_thai": "cho"}).eq("id", id).execute()
    return {"status": "ok"}