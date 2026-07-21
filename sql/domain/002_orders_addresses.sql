-- Store client/recipient street addresses for locker matching and driver routing.
ALTER TABLE orders
  ADD COLUMN from_address varchar(512) NULL AFTER parcel_type,
  ADD COLUMN to_address varchar(512) NULL AFTER from_address;
