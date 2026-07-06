"""
app.py
======
Web service that receives orders from Glide/n8n over HTTP POST,
then calls bon_printer to print to the correct station.

This is the system's "backend" — the bridge between the UI (Glide)
and the hardware (thermal printers).

Run the server:
    uvicorn app:app --host 0.0.0.0 --port 8000 --reload

Quick test with curl (see README):
    curl -X POST http://localhost:8000/order ...
"""

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
from typing import List
import logging

from bon_printer import print_bon

# ─── LOGGING ───────────────────────────────────────────────────────────────────
# Log every request so we can debug issues during rush hour
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s  %(levelname)s  %(message)s",
    datefmt="%H:%M:%S",
)
log = logging.getLogger(__name__)


# ─── APP ───────────────────────────────────────────────────────────────────────
app = FastAPI(
    title="Restaurant Bon Printer",
    description="Receives orders → auto-splits by station → prints kitchen/sushi/bar tickets",
    version="1.0.0",
)


# ─── DATA MODELS (Pydantic) ────────────────────────────────────────────────────
# Pydantic validates incoming data automatically. If a field is missing or has
# the wrong type, FastAPI returns a clear 422 error — no need to write your
# own if/else checks.

class OrderItem(BaseModel):
    ten: str = Field(..., description="Item name", example="Ramen bo")
    so_luong: int = Field(1, ge=1, description="Quantity, minimum 1")
    tram: str = Field(..., description="bep | sushi | bar")

class Order(BaseModel):
    ban: str = Field(..., description="Table number", example="5")
    thoi_gian: str = Field(None, description="HH:MM, auto-generated if left blank")
    items: List[OrderItem] = Field(..., min_items=1)

    # Allows dry_run=true for testing without a real printer
    dry_run: bool = Field(False, description="True = print to terminal, don't send to printer")


# ─── ENDPOINTS ─────────────────────────────────────────────────────────────────

@app.get("/health")
def health_check():
    """Check that the service is running. n8n or monitoring can ping this endpoint."""
    return {"status": "ok", "service": "bon-printer"}


@app.post("/order")
def receive_order(order: Order):
    """
    Receive an order, group it by station, print a ticket to each station.

    Flow:
        1. Group items by station
        2. For each station with items → call print_bon()
        3. Return the aggregated result

    If EVERY station fails to print → return 503 so n8n can retry.
    If ONLY SOME stations fail → return 207 (partial success).
    """
    order_dict = order.dict()
    log.info(f"Order received — Table {order.ban} — {len(order.items)} items")

    # Determine which stations need to print
    tram_can_in = set(item.tram for item in order.items)
    valid_trams = {"bep", "sushi", "bar"}
    invalid = tram_can_in - valid_trams
    if invalid:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid station(s): {invalid}. Only accepted: {valid_trams}"
        )

    # Print to each station
    results = {}
    for tram in tram_can_in:
        result = print_bon(order_dict, tram, dry_run=order.dry_run)
        results[tram] = result
        if result["ok"]:
            log.info(f"  [{tram}] ✓ {result['message']}")
        else:
            log.error(f"  [{tram}] ✗ {result['message']}")

    # Aggregate results
    all_ok     = all(r["ok"] for r in results.values())
    any_ok     = any(r["ok"] for r in results.values())
    failed     = [t for t, r in results.items() if not r["ok"]]

    if not any_ok:
        # Everything failed — n8n should retry
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
        "docs": "/docs",      # FastAPI auto-generates the docs page here
        "health": "/health",
    }
