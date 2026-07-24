-- Telegram destination for channel push (nullable = no TG notify).
ALTER TABLE users
  ADD COLUMN telegram_chat_id VARCHAR(64) NULL
  COMMENT 'Telegram chat_id for order progress push'
  AFTER phone;
