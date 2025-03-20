-- MySQL初期化スクリプト

-- 文字コードとcollationの設定
SET NAMES utf8mb4;
SET character_set_client = utf8mb4;

-- データベースの作成（既に存在する場合は作成しない）
CREATE DATABASE IF NOT EXISTS political_feed_db
  CHARACTER SET utf8mb4
  COLLATE utf8mb4_unicode_ci;

-- ユーザーの作成と権限付与
CREATE USER IF NOT EXISTS 'political_user'@'%' IDENTIFIED BY 'political_password';
GRANT ALL PRIVILEGES ON political_feed_db.* TO 'political_user'@'%';
FLUSH PRIVILEGES;

-- political_feed_dbデータベースを使用
USE political_feed_db;

-- 初期設定（必要に応じて）
SET GLOBAL time_zone = '+09:00';
SET SESSION time_zone = '+09:00';