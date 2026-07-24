-- Domain DB: POST4 (СПб) + ENUM P.
-- Полный набор ячеек POST4 и 3×P на POST1–3 — см. 016_lockers_post4_full_and_p3.sql

ALTER TABLE locker_cells
  MODIFY COLUMN cell_type ENUM('S', 'M', 'L', 'P') NOT NULL;

INSERT INTO lockers (
    id, model_id, locker_code, city, location_address,
    latitude, longitude, status, created_at
)
SELECT
    4, 1, 'POST4', 'Санкт-Петербург',
    'Санкт-Петербург, Лиговский пр., д. 1',
    NULL, NULL, 'locker_active', UTC_TIMESTAMP()
WHERE NOT EXISTS (SELECT 1 FROM lockers WHERE id = 4 OR locker_code = 'POST4');

INSERT INTO lockers (
    model_id, locker_code, city, location_address,
    latitude, longitude, status, created_at
)
SELECT
    1, 'POST4', 'Санкт-Петербург',
    'Санкт-Петербург, Лиговский пр., д. 1',
    NULL, NULL, 'locker_active', UTC_TIMESTAMP()
WHERE NOT EXISTS (SELECT 1 FROM lockers WHERE locker_code = 'POST4');
