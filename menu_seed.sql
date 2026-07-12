-- ============================================================
-- BƯỚC 1: Tạo bảng (chạy trong Supabase SQL Editor)
-- ============================================================
CREATE TABLE menu (
    id BIGINT PRIMARY KEY GENERATED ALWAYS AS IDENTITY,
    ten TEXT NOT NULL,
    gia FLOAT4 NOT NULL,
    category TEXT NOT NULL,
    tram TEXT NOT NULL CHECK (tram IN ('bep', 'sushi', 'bar')),
    available BOOLEAN DEFAULT TRUE
);

-- ============================================================
-- BƯỚC 2: Insert toàn bộ menu
-- ============================================================

-- STARTERS (tram: bep)
INSERT INTO menu (ten, gia, category, tram) VALUES
('Edamame', 4.50, 'Starters', 'bep'),
('Miso', 4.50, 'Starters', 'bep'),
('Miso Salmon', 5.50, 'Starters', 'bep'),
('Smashed Cucumber Salad', 4.50, 'Starters', 'bep'),
('Kimchi', 4.50, 'Starters', 'bep'),
('Crunch Bites', 5.00, 'Starters', 'bep'),
('Gyoza - Chicken', 5.50, 'Starters', 'bep'),
('Gyoza - Vegan', 5.00, 'Starters', 'bep'),
('Tempura - Prawns', 7.00, 'Starters', 'bep'),
('Cheesy Fried Roll', 5.50, 'Starters', 'bep'),
('Harumaki', 5.50, 'Starters', 'bep'),
('Wantan in Chiliöl', 6.00, 'Starters', 'bep'),
('Okonomiyaki', 10.00, 'Starters', 'bep'),
('Karaage', 6.00, 'Starters', 'bep'),
('Fish''N''Crunch ohne Cheese', 6.00, 'Starters', 'bep'),
('Fish''N''Crunch mit Cheese', 6.50, 'Starters', 'bep'),
('Yakitori', 6.00, 'Starters', 'bep'),
('Cornmelt', 5.50, 'Starters', 'bep');

-- MAINS (tram: bep)
INSERT INTO menu (ten, gia, category, tram) VALUES
('Niku Udon - Tofu', 14.00, 'Mains', 'bep'),
('Niku Udon - Shrimp Tempura', 15.50, 'Mains', 'bep'),
('Niku Udon - Beef', 15.50, 'Mains', 'bep'),
('Curry Udon - Tofu', 14.00, 'Mains', 'bep'),
('Curry Udon - Shrimp Tempura', 15.50, 'Mains', 'bep'),
('Curry Udon - Beef', 15.50, 'Mains', 'bep'),
('Oyakadon', 14.50, 'Mains', 'bep'),
('Katsu Don', 15.00, 'Mains', 'bep'),
('Ten Don', 15.50, 'Mains', 'bep'),
('Yakisoba - Tofu', 14.00, 'Mains', 'bep'),
('Yakisoba - Karaage', 14.50, 'Mains', 'bep'),
('Yakisoba - Prawns', 15.50, 'Mains', 'bep'),
('Yakisoba - Beef', 15.50, 'Mains', 'bep'),
('Chahan - Tofu', 14.00, 'Mains', 'bep'),
('Chahan - Karaage', 14.50, 'Mains', 'bep'),
('Chahan - Prawns', 15.50, 'Mains', 'bep'),
('Chahan - Beef', 15.50, 'Mains', 'bep');

-- RAMEN (tram: bep)
INSERT INTO menu (ten, gia, category, tram) VALUES
('Ramen - Chicken Broth', 16.50, 'Ramen', 'bep'),
('Ramen - Pork Broth', 16.50, 'Ramen', 'bep');

-- SASHIMI (tram: sushi)
INSERT INTO menu (ten, gia, category, tram) VALUES
('Sashimi - Salmon Ponzu (4 pcs)', 10.40, 'Sashimi', 'sushi'),
('Sashimi - Tuna Ponzu (4 pcs)', 12.40, 'Sashimi', 'sushi');

-- NIGIRI (tram: sushi)
INSERT INTO menu (ten, gia, category, tram) VALUES
('Nigiri - Sake/Salmon (2 pcs)', 6.00, 'Nigiri', 'sushi'),
('Nigiri - Flamed Salmon (2 pcs)', 6.50, 'Nigiri', 'sushi'),
('Nigiri - Maguro/Tuna (2 pcs)', 6.50, 'Nigiri', 'sushi'),
('Nigiri - Ebi/Prawns (2 pcs)', 6.00, 'Nigiri', 'sushi'),
('Nigiri - Unagi/Eel (2 pcs)', 6.50, 'Nigiri', 'sushi'),
('Nigiri - Mango (2 pcs)', 5.50, 'Nigiri', 'sushi'),
('Nigiri - Avocado (2 pcs)', 5.50, 'Nigiri', 'sushi'),
('Nigiri - Kani/Surimi (2 pcs)', 5.50, 'Nigiri', 'sushi'),
('Nigiri - Inari/Tofu Pocket (2 pcs)', 5.50, 'Nigiri', 'sushi'),
('Nigiri - Tamago/Egg (2 pcs)', 5.50, 'Nigiri', 'sushi');

-- MAKI (tram: sushi)
INSERT INTO menu (ten, gia, category, tram) VALUES
('Maki - Sake (8 pcs)', 5.50, 'Maki', 'sushi'),
('Maki - Sake + Avocado (8 pcs)', 6.00, 'Maki', 'sushi'),
('Maki - Tuna (8 pcs)', 6.00, 'Maki', 'sushi'),
('Maki - Spicy Tuna (8 pcs)', 6.50, 'Maki', 'sushi'),
('Maki - Ebi (8 pcs)', 6.00, 'Maki', 'sushi'),
('Maki - Ebi + Cream Cheese (8 pcs)', 6.50, 'Maki', 'sushi'),
('Maki - California (8 pcs)', 5.50, 'Maki', 'sushi'),
('Maki - Avocado (8 pcs)', 5.50, 'Maki', 'sushi'),
('Maki - Kappa/Cucumber (8 pcs)', 5.00, 'Maki', 'sushi'),
('Maki - Tamago (8 pcs)', 5.50, 'Maki', 'sushi'),
('Maki - Inari/Tofu Pocket (8 pcs)', 5.00, 'Maki', 'sushi'),
('Maki - New York (8 pcs)', 6.00, 'Maki', 'sushi'),
('Maki - Unagi (8 pcs)', 6.50, 'Maki', 'sushi');

-- SPECIALS (tram: sushi)
INSERT INTO menu (ten, gia, category, tram) VALUES
('Caterpillar (8 pcs)', 15.50, 'Specials', 'sushi'),
('Sriracha Dragon (8 pcs)', 16.00, 'Specials', 'sushi'),
('Shrimpin'' Ain''t Easy (8 pcs)', 15.00, 'Specials', 'sushi'),
('Wicked Spicy Salmon (8 pcs)', 15.50, 'Specials', 'sushi'),
('Salmon Flame Bite (8 pcs)', 15.90, 'Specials', 'sushi'),
('Rainbow (8 pcs)', 15.50, 'Specials', 'sushi'),
('Green Dragon Roll (8 pcs)', 14.50, 'Specials', 'sushi'),
('Forest Spirit Roll (8 pcs)', 14.50, 'Specials', 'sushi'),
('Avocado Dream Roll (8 pcs)', 14.50, 'Specials', 'sushi'),
('Futo Salmon Roll', 9.50, 'Specials', 'sushi'),
('Futo Veggie Roll', 8.50, 'Specials', 'sushi');

-- INSIDE OUT (tram: sushi)
INSERT INTO menu (ten, gia, category, tram) VALUES
('Inside Out - Sake (8 pcs)', 10.90, 'Inside Out', 'sushi'),
('Inside Out - Tuna (8 pcs)', 12.90, 'Inside Out', 'sushi'),
('Inside Out - Ebi (8 pcs)', 10.90, 'Inside Out', 'sushi'),
('Inside Out - California (8 pcs)', 9.90, 'Inside Out', 'sushi'),
('Inside Out - New York (8 pcs)', 11.90, 'Inside Out', 'sushi'),
('Inside Out - Chicken (8 pcs)', 9.90, 'Inside Out', 'sushi'),
('Inside Out - Veggy (8 pcs)', 8.90, 'Inside Out', 'sushi'),
('Inside Out - Veggy Avocado/Cucumber (8 pcs)', 8.90, 'Inside Out', 'sushi');

-- HOT ROLLS (tram: sushi)
INSERT INTO menu (ten, gia, category, tram) VALUES
('Small Roll - Salmon (8 pcs)', 6.40, 'Hot Rolls', 'sushi'),
('Small Roll - Shrimp (8 pcs)', 6.70, 'Hot Rolls', 'sushi'),
('Small Roll - Spicy Salmon (8 pcs)', 6.50, 'Hot Rolls', 'sushi'),
('Small Roll - Spinach (8 pcs)', 6.00, 'Hot Rolls', 'sushi'),
('Small Roll - Tofu Pocket (8 pcs)', 6.00, 'Hot Rolls', 'sushi'),
('Big Roll - Salmon (6 pcs)', 11.00, 'Hot Rolls', 'sushi'),
('Big Roll - Chicken (6 pcs)', 10.00, 'Hot Rolls', 'sushi'),
('Big Roll Veggy (6 pcs)', 9.00, 'Hot Rolls', 'sushi');

-- PARTY PLATES (tram: sushi)
INSERT INTO menu (ten, gia, category, tram) VALUES
('Party Plate 1', 13.90, 'Party Plates', 'sushi'),
('Party Plate 2', 17.50, 'Party Plates', 'sushi'),
('Party Plate 3', 19.00, 'Party Plates', 'sushi'),
('Party Plate 4', 35.90, 'Party Plates', 'sushi'),
('Party Plate 5', 12.90, 'Party Plates', 'sushi'),
('Party Plate 6', 23.90, 'Party Plates', 'sushi'),
('Party Plate 7', 17.90, 'Party Plates', 'sushi'),
('Party Plate 8', 45.90, 'Party Plates', 'sushi');

-- SOFT DRINKS (tram: bar)
INSERT INTO menu (ten, gia, category, tram) VALUES
('Cola 0.2L', 2.70, 'Soft Drinks', 'bar'),
('Cola Zero 0.2L', 2.70, 'Soft Drinks', 'bar'),
('Apple Spritzer 0.2L', 2.70, 'Soft Drinks', 'bar'),
('Ginger Ale 0.2L', 2.90, 'Soft Drinks', 'bar'),
('Water 0.25L', 2.70, 'Soft Drinks', 'bar'),
('Water 0.75L', 5.50, 'Soft Drinks', 'bar');

-- LEMONADE (tram: bar)
INSERT INTO menu (ten, gia, category, tram) VALUES
('Lemonade - Yuzu', 5.50, 'Lemonade', 'bar'),
('Lemonade - Strawberry', 5.50, 'Lemonade', 'bar'),
('Lemonade - Mango', 5.50, 'Lemonade', 'bar'),
('Calpico Matcha', 6.00, 'Lemonade', 'bar');

-- BEER (tram: bar)
INSERT INTO menu (ten, gia, category, tram) VALUES
('Asahi 0.33L', 3.90, 'Beer', 'bar'),
('Asahi Alcohol-Free 0.33L', 3.90, 'Beer', 'bar'),
('Kirin 0.33L', 3.90, 'Beer', 'bar'),
('Berliner Pilsner', 3.90, 'Beer', 'bar'),
('Radler 0.33L', 3.90, 'Beer', 'bar');

-- HOT DRINKS (tram: bar)
INSERT INTO menu (ten, gia, category, tram) VALUES
('Tea - Sencha', 4.20, 'Hot Drinks', 'bar'),
('Tea - Ginger', 4.20, 'Hot Drinks', 'bar'),
('Tea - Genmaicha', 4.20, 'Hot Drinks', 'bar'),
('Tea - Yuzu', 4.20, 'Hot Drinks', 'bar');

-- HIGHBALL (tram: bar)
INSERT INTO menu (ten, gia, category, tram) VALUES
('Highball - Classic', 7.90, 'Highball', 'bar'),
('Highball - Yuzu', 8.50, 'Highball', 'bar');

-- WINE (tram: bar)
INSERT INTO menu (ten, gia, category, tram) VALUES
('Wine - White/Grauburgunder', 7.00, 'Wine', 'bar'),
('Wine - Red/Merlot', 7.00, 'Wine', 'bar'),
('Umeshu Soda 0.3L', 7.00, 'Wine', 'bar');

-- SAKE (tram: bar)
INSERT INTO menu (ten, gia, category, tram) VALUES
('Sake 0.15L', 5.50, 'Sake', 'bar');

-- SIGNATURE DRINKS (tram: bar)
INSERT INTO menu (ten, gia, category, tram) VALUES
('Der Japanische Cocktail', 8.50, 'Signature Drinks', 'bar'),
('Midori Sour', 8.50, 'Signature Drinks', 'bar'),
('Grapefruit-Honig-Sake', 8.50, 'Signature Drinks', 'bar');
