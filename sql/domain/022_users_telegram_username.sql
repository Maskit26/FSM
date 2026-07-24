-- Username пользователя Telegram (без @); chat_id привязывается на /start.
ALTER TABLE users
  ADD COLUMN telegram_username VARCHAR(64) NULL
  COMMENT 'Telegram @username without @; bind chat_id on /start'
  AFTER telegram_chat_id;

CREATE INDEX idx_users_telegram_username ON users (telegram_username);
