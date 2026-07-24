-- Fix: POST4 = полный набор ячеек; POST1–3 = по 3×P.
-- Идемпотентно (NOT EXISTS по locker_id + cell_code).

-- POST1, POST2, POST3: P-01 / P-02 / P-03
INSERT INTO locker_cells (locker_id, cell_code, cell_type, status, current_order_id, created_at, updated_at)
SELECT l.id, v.cell_code, 'P', 'locker_free', NULL, UTC_TIMESTAMP(), UTC_TIMESTAMP()
FROM lockers l
CROSS JOIN (
    SELECT 'P-01' AS cell_code UNION ALL
    SELECT 'P-02' UNION ALL
    SELECT 'P-03'
) v
WHERE l.locker_code IN ('POST1', 'POST2', 'POST3')
  AND NOT EXISTS (
      SELECT 1 FROM locker_cells lc
      WHERE lc.locker_id = l.id AND lc.cell_code = v.cell_code
  );

-- POST4: 3×S, 3×M, 3×L, 3×P
INSERT INTO locker_cells (locker_id, cell_code, cell_type, status, current_order_id, created_at, updated_at)
SELECT l.id, v.cell_code, v.cell_type, 'locker_free', NULL, UTC_TIMESTAMP(), UTC_TIMESTAMP()
FROM lockers l
CROSS JOIN (
    SELECT 'S-01' AS cell_code, 'S' AS cell_type UNION ALL
    SELECT 'S-02', 'S' UNION ALL
    SELECT 'S-03', 'S' UNION ALL
    SELECT 'M-01', 'M' UNION ALL
    SELECT 'M-02', 'M' UNION ALL
    SELECT 'M-03', 'M' UNION ALL
    SELECT 'L-01', 'L' UNION ALL
    SELECT 'L-02', 'L' UNION ALL
    SELECT 'L-03', 'L' UNION ALL
    SELECT 'P-01', 'P' UNION ALL
    SELECT 'P-02', 'P' UNION ALL
    SELECT 'P-03', 'P'
) v
WHERE l.locker_code = 'POST4'
  AND NOT EXISTS (
      SELECT 1 FROM locker_cells lc
      WHERE lc.locker_id = l.id AND lc.cell_code = v.cell_code
  );
