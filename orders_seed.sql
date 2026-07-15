-- ============================================================
-- orders table (Supabase SQL Editor)
-- Ghi lại từng món trong 1 lần gửi order (1 row = 1 món).
-- Nhiều row có thể cùng order_id nếu được gửi chung 1 lần từ
-- màn hình waiter (xem app.py -> receive_order()).
-- ============================================================
CREATE TABLE orders (
    id BIGINT PRIMARY KEY GENERATED ALWAYS AS IDENTITY,
    order_id TEXT NOT NULL,               -- uuid nhóm các món gửi cùng 1 lần
    ban INTEGER NOT NULL,                 -- số bàn
    ten TEXT NOT NULL,                    -- tên món (copy từ menu tại thời điểm order)
    so_luong INTEGER NOT NULL DEFAULT 1,
    tram TEXT NOT NULL CHECK (tram IN ('bep', 'sushi', 'bar')),
    category TEXT,                        -- copy từ menu.category (vd: Starters, Mains)
    ghi_chu TEXT,                         -- ghi chú của khách (dị ứng, không hành...)
    trang_thai TEXT NOT NULL DEFAULT 'cho' CHECK (trang_thai IN ('cho', 'xong')),
    thoi_gian TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- Query phổ biến nhất là lọc theo trạm + trạng thái đang chờ
-- (kitchen.html gọi GET /orders?tram=... mỗi 5 giây)
CREATE INDEX idx_orders_tram_trang_thai ON orders (tram, trang_thai);
CREATE INDEX idx_orders_order_id ON orders (order_id);