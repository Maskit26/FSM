-- Deep-link /start bind uses users.id + signed payload; username column unused.
DROP INDEX idx_users_telegram_username ON users;
ALTER TABLE users DROP COLUMN telegram_username;
