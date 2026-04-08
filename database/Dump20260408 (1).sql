CREATE DATABASE  IF NOT EXISTS `testdb` /*!40100 DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci */ /*!80016 DEFAULT ENCRYPTION='N' */;
USE `testdb`;
-- MySQL dump 10.13  Distrib 8.0.44, for Win64 (x86_64)
--
-- Host: localhost    Database: testdb
-- ------------------------------------------------------
-- Server version	8.0.45-0ubuntu0.24.04.1

/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!50503 SET NAMES utf8 */;
/*!40103 SET @OLD_TIME_ZONE=@@TIME_ZONE */;
/*!40103 SET TIME_ZONE='+00:00' */;
/*!40014 SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0 */;
/*!40014 SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0 */;
/*!40101 SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='NO_AUTO_VALUE_ON_ZERO' */;
/*!40111 SET @OLD_SQL_NOTES=@@SQL_NOTES, SQL_NOTES=0 */;

--
-- Table structure for table `button_states`
--

DROP TABLE IF EXISTS `button_states`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `button_states` (
  `id` int NOT NULL AUTO_INCREMENT,
  `button_name` varchar(50) NOT NULL,
  `button_label` varchar(100) NOT NULL,
  `user_role` varchar(50) NOT NULL,
  `entity_state` varchar(50) NOT NULL,
  `is_enabled` enum('active','inactive') DEFAULT 'inactive',
  PRIMARY KEY (`id`),
  UNIQUE KEY `unique_button_state` (`button_name`,`user_role`,`entity_state`)
) ENGINE=InnoDB AUTO_INCREMENT=90 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `button_states`
--

INSERT  IGNORE INTO `button_states` VALUES (1,'create_order','Создать заказ','client','order_created','active');
INSERT  IGNORE INTO `button_states` VALUES (2,'create_order','Создать заказ','client','order_parcel_submitted','inactive');
INSERT  IGNORE INTO `button_states` VALUES (3,'open_cell','Открыть ячейку','client','locker_reserved','active');
INSERT  IGNORE INTO `button_states` VALUES (4,'open_cell','Открыть ячейку','client','locker_opened','inactive');
INSERT  IGNORE INTO `button_states` VALUES (5,'open_cell','Открыть ячейку','client','locker_free','inactive');
INSERT  IGNORE INTO `button_states` VALUES (6,'close_cell','Закрыть ячейку','client','locker_opened','active');
INSERT  IGNORE INTO `button_states` VALUES (7,'close_cell','Закрыть ячейку','client','locker_parcel_confirmed','active');
INSERT  IGNORE INTO `button_states` VALUES (8,'close_cell','Закрыть ячейку','client','locker_parcel_submitted','inactive');
INSERT  IGNORE INTO `button_states` VALUES (9,'cancel_order','Отменить заказ','client','order_created','active');
INSERT  IGNORE INTO `button_states` VALUES (10,'cancel_order','Отменить заказ','client','order_courier_reserved_post1_and_post2','active');
INSERT  IGNORE INTO `button_states` VALUES (11,'cancel_order','Отменить заказ','client','order_completed','inactive');
INSERT  IGNORE INTO `button_states` VALUES (12,'pickup_order','Забрать заказ','recipient','order_parcel_submitted','active');
INSERT  IGNORE INTO `button_states` VALUES (13,'pickup_order','Забрать заказ','recipient','order_delivered_to_client','inactive');
INSERT  IGNORE INTO `button_states` VALUES (14,'open_cell','Открыть ячейку','recipient','locker_parcel_submitted','active');
INSERT  IGNORE INTO `button_states` VALUES (15,'open_cell','Открыть ячейку','recipient','locker_opened','inactive');
INSERT  IGNORE INTO `button_states` VALUES (16,'close_cell','Закрыть ячейку','recipient','locker_opened','active');
INSERT  IGNORE INTO `button_states` VALUES (17,'close_cell','Закрыть ячейку','recipient','locker_free','inactive');
INSERT  IGNORE INTO `button_states` VALUES (18,'confirm_pickup','Подтвердить получение','recipient','order_delivered_to_client','active');
INSERT  IGNORE INTO `button_states` VALUES (19,'confirm_pickup','Подтвердить получение','recipient','order_completed','inactive');
INSERT  IGNORE INTO `button_states` VALUES (20,'take_order','Взять заказ','courier','order_courier_reserved_post1_and_post2','active');
INSERT  IGNORE INTO `button_states` VALUES (21,'take_order','Взять заказ','courier','order_courier1_assigned','inactive');
INSERT  IGNORE INTO `button_states` VALUES (22,'pickup_from_client','Забрал у клиента','courier','order_courier1_assigned','active');
INSERT  IGNORE INTO `button_states` VALUES (23,'pickup_from_client','Забрал у клиента','courier','order_courier_has_parcel','inactive');
INSERT  IGNORE INTO `button_states` VALUES (24,'arrived_at_recipient','Прибыл к получателю','courier','order_courier_has_parcel','active');
INSERT  IGNORE INTO `button_states` VALUES (25,'arrived_at_recipient','Прибыл к получателю','courier','order_parcel_delivered','inactive');
INSERT  IGNORE INTO `button_states` VALUES (26,'open_cell','Открыть ячейку','courier','locker_parcel_submitted','active');
INSERT  IGNORE INTO `button_states` VALUES (27,'open_cell','Открыть ячейку','courier','locker_opened','inactive');
INSERT  IGNORE INTO `button_states` VALUES (28,'close_cell','Закрыть ячейку','courier','locker_opened','active');
INSERT  IGNORE INTO `button_states` VALUES (29,'close_cell','Закрыть ячейку','courier','locker_parcel_confirmed','active');
INSERT  IGNORE INTO `button_states` VALUES (30,'cancel_order','Отменить заказ','courier','order_courier1_assigned','active');
INSERT  IGNORE INTO `button_states` VALUES (31,'cancel_order','Отменить заказ','courier','order_completed','inactive');
INSERT  IGNORE INTO `button_states` VALUES (32,'take_trip','Взять рейс','driver','trip_created','active');
INSERT  IGNORE INTO `button_states` VALUES (33,'take_trip','Взять рейс','driver','trip_assigned','inactive');
INSERT  IGNORE INTO `button_states` VALUES (34,'arrived_at_locker','Прибыл к постамату','driver','trip_assigned','active');
INSERT  IGNORE INTO `button_states` VALUES (35,'arrived_at_locker','Прибыл к постамату','driver','trip_ready_for_pickup','inactive');
INSERT  IGNORE INTO `button_states` VALUES (36,'start_trip','Начал путь','driver','trip_ready_for_pickup','active');
INSERT  IGNORE INTO `button_states` VALUES (37,'start_trip','Начал путь','driver','trip_in_progress','inactive');
INSERT  IGNORE INTO `button_states` VALUES (38,'arrived_destination','Прибыл','driver','trip_in_progress','active');
INSERT  IGNORE INTO `button_states` VALUES (39,'arrived_destination','Прибыл','driver','trip_arrived_at_destination','inactive');
INSERT  IGNORE INTO `button_states` VALUES (40,'open_cell','Открыть ячейку','driver','locker_reserved','active');
INSERT  IGNORE INTO `button_states` VALUES (41,'open_cell','Открыть ячейку','driver','locker_opened','inactive');
INSERT  IGNORE INTO `button_states` VALUES (42,'close_cell','Закрыть ячейку','driver','locker_opened','active');
INSERT  IGNORE INTO `button_states` VALUES (43,'close_cell','Закрыть ячейку','driver','locker_parcel_submitted','inactive');
INSERT  IGNORE INTO `button_states` VALUES (44,'cancel_trip','Отменить рейс','driver','trip_assigned','active');
INSERT  IGNORE INTO `button_states` VALUES (45,'cancel_trip','Отменить рейс','driver','trip_completed','inactive');
INSERT  IGNORE INTO `button_states` VALUES (46,'assign_courier','Назначить','operator','order_created','active');
INSERT  IGNORE INTO `button_states` VALUES (47,'assign_courier','Назначить','operator','order_courier1_assigned','inactive');
INSERT  IGNORE INTO `button_states` VALUES (48,'remove_assignment','Снять','operator','order_courier1_assigned','active');
INSERT  IGNORE INTO `button_states` VALUES (49,'remove_assignment','Снять','operator','order_created','inactive');
INSERT  IGNORE INTO `button_states` VALUES (50,'block_cell','Заблокировать ячейку','operator','locker_free','active');
INSERT  IGNORE INTO `button_states` VALUES (51,'block_cell','Заблокировать ячейку','operator','locker_blocked','inactive');
INSERT  IGNORE INTO `button_states` VALUES (52,'reserve_cell','Забронировать ячейку','operator','locker_free','active');
INSERT  IGNORE INTO `button_states` VALUES (53,'reserve_cell','Забронировать ячейку','operator','locker_reserved','inactive');
INSERT  IGNORE INTO `button_states` VALUES (54,'reset_reservation','Снять бронь ячейки (reset)','operator','locker_reserved','active');
INSERT  IGNORE INTO `button_states` VALUES (55,'reset_reservation','Снять бронь ячейки (reset)','operator','locker_free','inactive');
INSERT  IGNORE INTO `button_states` VALUES (56,'open_cell','Открыть ячейку','operator','locker_reserved','active');
INSERT  IGNORE INTO `button_states` VALUES (57,'open_cell','Открыть ячейку','operator','locker_opened','inactive');
INSERT  IGNORE INTO `button_states` VALUES (58,'close_cell','Закрыть ячейку','operator','locker_opened','active');
INSERT  IGNORE INTO `button_states` VALUES (59,'close_cell','Закрыть ячейку','operator','locker_parcel_submitted','inactive');
INSERT  IGNORE INTO `button_states` VALUES (60,'to_maintenance','В ремонт ячейку','operator','locker_free','active');
INSERT  IGNORE INTO `button_states` VALUES (61,'to_maintenance','В ремонт ячейку','operator','locker_maintenance','inactive');
INSERT  IGNORE INTO `button_states` VALUES (62,'from_maintenance','Снять с ремонта ячейку','operator','locker_maintenance','active');
INSERT  IGNORE INTO `button_states` VALUES (63,'from_maintenance','Снять с ремонта ячейку','operator','locker_free','inactive');
INSERT  IGNORE INTO `button_states` VALUES (64,'confirm_pickup','','recipient','order_courier2_parcel_delivered','active');
INSERT  IGNORE INTO `button_states` VALUES (65,'take_order','Взять заказ','courier','order_created','active');
INSERT  IGNORE INTO `button_states` VALUES (66,'report_error','Сообщить об ошибке','driver','locker_reserved','active');
INSERT  IGNORE INTO `button_states` VALUES (67,'report_error','Сообщить об ошибке','driver','locker_opened','active');
INSERT  IGNORE INTO `button_states` VALUES (68,'report_error','Сообщить об ошибке','courier','locker_reserved','active');
INSERT  IGNORE INTO `button_states` VALUES (69,'report_error','Сообщить об ошибке','courier','locker_opened','active');
INSERT  IGNORE INTO `button_states` VALUES (70,'report_error','Сообщить об ошибке','client','locker_reserved','active');
INSERT  IGNORE INTO `button_states` VALUES (71,'report_error','Сообщить об ошибке','client','locker_opened','active');
INSERT  IGNORE INTO `button_states` VALUES (72,'report_error','Сообщить об ошибке','recipient','locker_parcel_submitted','active');
INSERT  IGNORE INTO `button_states` VALUES (73,'report_error','Сообщить об ошибке','recipient','locker_opened','active');
INSERT  IGNORE INTO `button_states` VALUES (74,'report_error','Сообщить об ошибке','operator','locker_free','active');
INSERT  IGNORE INTO `button_states` VALUES (75,'report_error','Сообщить об ошибке','operator','locker_error','active');
INSERT  IGNORE INTO `button_states` VALUES (76,'report_error','Сообщить об ошибке','operator','locker_maintenance','active');
INSERT  IGNORE INTO `button_states` VALUES (77,'confirm_delivery_with_code','Доставил заказ','courier','order_courier2_parcel_delivered','active');
INSERT  IGNORE INTO `button_states` VALUES (78,'reserve_slot','Vzyat slot','driver','direction_open','active');
INSERT  IGNORE INTO `button_states` VALUES (79,'reserve_slot','Vzyat slot','driver','direction_slot_taken','inactive');
INSERT  IGNORE INTO `button_states` VALUES (81,'start_loading','Nachat zagruzku','driver','direction_loading','inactive');
INSERT  IGNORE INTO `button_states` VALUES (82,'complete_loading','Zavershit pogruzku','driver','direction_loading','active');
INSERT  IGNORE INTO `button_states` VALUES (83,'complete_loading','Zavershit pogruzku','driver','direction_open','inactive');
INSERT  IGNORE INTO `button_states` VALUES (84,'reserve_slot','Vzyat slot','driver','direction_loading','inactive');
INSERT  IGNORE INTO `button_states` VALUES (85,'reserve_slot','Vzyat slot','driver','direction_loading_finished','inactive');
INSERT  IGNORE INTO `button_states` VALUES (89,'start_loading','Nachat zagruzku','driver','direction_open','active');

--
-- Table structure for table `cell_access_tokens`
--

DROP TABLE IF EXISTS `cell_access_tokens`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `cell_access_tokens` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `order_id` int NOT NULL,
  `leg` enum('pickup','delivery') NOT NULL,
  `cell_id` int NOT NULL,
  `actor_user_id` int NOT NULL,
  `pin_hash` char(64) NOT NULL COMMENT 'SHA256(PIN + salt)',
  `pin_encrypted` varchar(255) DEFAULT NULL,
  `status` enum('ACTIVE','USED','EXPIRED','REVOKED') DEFAULT 'ACTIVE',
  `expires_at` datetime NOT NULL,
  `failed_attempts` tinyint DEFAULT '0',
  `created_at` datetime DEFAULT CURRENT_TIMESTAMP,
  `used_at` datetime DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `actor_user_id` (`actor_user_id`),
  KEY `idx_order_leg` (`order_id`,`leg`),
  KEY `idx_cell_active` (`cell_id`,`status`),
  KEY `idx_expires_at` (`expires_at`),
  CONSTRAINT `cell_access_tokens_ibfk_1` FOREIGN KEY (`order_id`) REFERENCES `orders` (`id`) ON DELETE CASCADE,
  CONSTRAINT `cell_access_tokens_ibfk_2` FOREIGN KEY (`cell_id`) REFERENCES `locker_cells` (`id`),
  CONSTRAINT `cell_access_tokens_ibfk_3` FOREIGN KEY (`actor_user_id`) REFERENCES `users` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=88 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `cell_access_tokens`
--

INSERT  IGNORE INTO `cell_access_tokens` VALUES (1,1510,'pickup',31,1005,'490a6b4f6dc249bf934da7bf548b9dcaf12dc9b0fd286e5b67f08622a1f51777',NULL,'ACTIVE','2026-02-11 18:35:47',0,'2026-02-11 18:20:46',NULL);
INSERT  IGNORE INTO `cell_access_tokens` VALUES (2,1510,'pickup',31,1005,'d60ec2ef2d0fe1a779ba88272fbf3db22d4fd179ef759270535a4f1cd72f58df',NULL,'ACTIVE','2026-02-12 10:06:24',0,'2026-02-12 09:51:23',NULL);
INSERT  IGNORE INTO `cell_access_tokens` VALUES (3,1510,'pickup',31,1005,'736773fd5d112b0f3f87c7439b6c105f468cfb0e6b7dcf69b8fbfc1430492fe0',NULL,'ACTIVE','2026-02-12 10:34:41',0,'2026-02-12 10:19:41',NULL);
INSERT  IGNORE INTO `cell_access_tokens` VALUES (4,1510,'pickup',31,1005,'1870472713a81a194e9547b279d83a6ed8aff8c4e6704fa4b126c4ce52db5c00',NULL,'ACTIVE','2026-02-12 10:55:35',0,'2026-02-12 10:40:34',NULL);
INSERT  IGNORE INTO `cell_access_tokens` VALUES (5,1525,'delivery',38,2004,'3d1f5dafbca3352bdd2a0a4b2522aac02bb026823a2191a835e901ae3efa2120',NULL,'ACTIVE','2026-02-28 06:22:08',0,'2026-02-28 06:07:08',NULL);
INSERT  IGNORE INTO `cell_access_tokens` VALUES (6,1525,'delivery',38,2004,'609c99ff4ca1c73d9cdadf58ccd8fb21486d74f5d00b875c297837a4c83e70dd',NULL,'USED','2026-02-28 07:55:43',0,'2026-02-28 07:40:42','2026-02-28 07:42:17');
INSERT  IGNORE INTO `cell_access_tokens` VALUES (7,1526,'pickup',1,1001,'fb7ae4cbcfc4c1e0ed94fee4af07e712b0fcd9399991a2572cf15116e06dc0de',NULL,'REVOKED','2026-03-02 09:19:36',0,'2026-03-02 09:04:36',NULL);
INSERT  IGNORE INTO `cell_access_tokens` VALUES (8,1526,'pickup',1,1001,'1f95027e91bed79a507bba3f1af0f4c86a2c053fff2779c2e94626fd88d4de72','496219','REVOKED','2026-03-02 10:53:06',0,'2026-03-02 10:38:05',NULL);
INSERT  IGNORE INTO `cell_access_tokens` VALUES (9,1526,'pickup',1,1001,'ae0f8336b9ca1c53ca1f3ea5184b54cc0de67740ffec36be10dcbe03a47d0fe7','935209','REVOKED','2026-03-02 11:20:57',0,'2026-03-02 11:05:57',NULL);
INSERT  IGNORE INTO `cell_access_tokens` VALUES (10,1527,'pickup',5,1001,'e7b11a011b67eee1af0bbad10610c47be264f733483d59bbcbdffd7a0218b796','768347','ACTIVE','2026-03-15 13:47:06',0,'2026-03-15 13:32:06',NULL);
INSERT  IGNORE INTO `cell_access_tokens` VALUES (11,1528,'pickup',6,1001,'87260ad86b07080225a45fc525d8f9216e787ac7be936a3e3c8f01c01505bc50','338651','REVOKED','2026-03-15 14:01:22',0,'2026-03-15 13:46:22',NULL);
INSERT  IGNORE INTO `cell_access_tokens` VALUES (12,1526,'pickup',1,1001,'358ae78ce1ec07fb29fad70aec3dea08d783ba578627774a86a5e1ad3435afb5','622978','REVOKED','2026-03-16 10:20:13',0,'2026-03-16 10:05:13',NULL);
INSERT  IGNORE INTO `cell_access_tokens` VALUES (13,1526,'pickup',1,1001,'b5739df3c75eb839804a035176a601c349caa155534c6aa6469d2838fee6228c','354676','REVOKED','2026-03-16 10:25:08',0,'2026-03-16 10:10:08',NULL);
INSERT  IGNORE INTO `cell_access_tokens` VALUES (14,1526,'pickup',1,1001,'bf1c61bcd21d5eed7461f824ba0ac454f00e226e8288fe9184ba17d48053f40d','876479','REVOKED','2026-03-16 12:51:11',0,'2026-03-16 12:36:11',NULL);
INSERT  IGNORE INTO `cell_access_tokens` VALUES (15,1527,'pickup',5,200,'e4811170113d75d2bb119d1517bce68ba1f34c7cb0bd94d394fcb45c6a1b91ca','964884','ACTIVE','2026-03-18 15:48:42',0,'2026-03-18 15:33:41',NULL);
INSERT  IGNORE INTO `cell_access_tokens` VALUES (16,1527,'delivery',15,200,'07e9990358d298fef75ab696bcf49faeecb9b2d8459d713da12858881e18b601','793243','REVOKED','2026-03-19 13:32:13',0,'2026-03-19 13:17:12',NULL);
INSERT  IGNORE INTO `cell_access_tokens` VALUES (17,1527,'delivery',15,200,'778d14dc42cc54797c8b307f82a0b0abeca0e257b9ea59a8090a1b71144cf303','896353','ACTIVE','2026-03-19 14:08:03',0,'2026-03-19 13:53:03',NULL);
INSERT  IGNORE INTO `cell_access_tokens` VALUES (18,1534,'pickup',45,1004,'e1f541bfa29c2048983c30bde147e582afbdb55f13328ebd6843da5b249f243a','428691','ACTIVE','2026-03-22 09:59:25',0,'2026-03-22 09:44:24',NULL);
INSERT  IGNORE INTO `cell_access_tokens` VALUES (19,1526,'pickup',1,1001,'57023250aa6daee1df30537fb3da1d2bccba772a470a42b52cb0c38e9f84ac91','239669','REVOKED','2026-03-23 06:38:10',0,'2026-03-23 06:23:09',NULL);
INSERT  IGNORE INTO `cell_access_tokens` VALUES (20,1528,'pickup',6,1001,'eb2fb81be2bed568dd3599c1f97320e8e55b029e82b4224bb6147e5204fddcea','154105','REVOKED','2026-03-23 06:38:10',0,'2026-03-23 06:23:09',NULL);
INSERT  IGNORE INTO `cell_access_tokens` VALUES (21,1528,'pickup',6,1001,'a5186e2e20fb0af88302e41c265a9162415536e453b90bf20423112aac9811f1','488015','ACTIVE','2026-03-23 09:41:19',0,'2026-03-23 09:26:19',NULL);
INSERT  IGNORE INTO `cell_access_tokens` VALUES (22,1534,'pickup',45,200,'adb7b01d41f4dca276f206271c3d0a9330d9ad89525ccde3d6606cb0e9872900','119477','REVOKED','2026-03-23 09:43:00',0,'2026-03-23 09:27:59',NULL);
INSERT  IGNORE INTO `cell_access_tokens` VALUES (23,1528,'pickup',6,200,'a9406d746293babadd01c3dba88cf9334acae369fc30d5880862383bb48886f4','588553','REVOKED','2026-03-23 09:56:56',0,'2026-03-23 09:41:55',NULL);
INSERT  IGNORE INTO `cell_access_tokens` VALUES (24,1528,'pickup',6,200,'5963dad52bd6be617e39b3b9016ea719f5ad522cc230c748d288b3fe2982fa06','810513','REVOKED','2026-03-23 11:02:58',0,'2026-03-23 10:47:58',NULL);
INSERT  IGNORE INTO `cell_access_tokens` VALUES (25,1528,'pickup',6,200,'e46427307d874befef3354a4644b1100317a3f2e41dad4dff90e7b34ac97e6ec','436412','ACTIVE','2026-03-23 16:01:33',0,'2026-03-23 15:46:32',NULL);
INSERT  IGNORE INTO `cell_access_tokens` VALUES (26,1534,'pickup',45,200,'2906db3c63df250c02809e0bc9158f72093f8b459d09946dc99ec68939cf8b7f','763548','REVOKED','2026-03-23 18:11:16',0,'2026-03-23 17:56:16',NULL);
INSERT  IGNORE INTO `cell_access_tokens` VALUES (27,1534,'pickup',45,200,'c2f15c5faf3562ed6da52d450c394822cbb19cf6e714db516fff5cb418e6428f','907301','REVOKED','2026-03-24 14:47:33',0,'2026-03-24 14:32:32',NULL);
INSERT  IGNORE INTO `cell_access_tokens` VALUES (28,1534,'pickup',45,200,'22bda68b54d5e98efaf9944bcc339eb12f08abbfbcc83f2c7cd8db75a718413b','158081','REVOKED','2026-03-24 16:30:23',0,'2026-03-24 16:15:22',NULL);
INSERT  IGNORE INTO `cell_access_tokens` VALUES (29,1534,'pickup',45,200,'0719a7c1cd2def03f970ba5857af58721c4ed323d91dc0450735d743e48b0b61','333462','REVOKED','2026-03-24 16:30:43',0,'2026-03-24 16:15:42',NULL);
INSERT  IGNORE INTO `cell_access_tokens` VALUES (30,1534,'pickup',45,200,'4fd58387208b076280e1d34adbb27daca79981324a44d7ce79229e80e11c26bd','795630','REVOKED','2026-03-24 16:31:38',0,'2026-03-24 16:16:37',NULL);
INSERT  IGNORE INTO `cell_access_tokens` VALUES (31,1534,'pickup',45,200,'f76ce0b3becca9f371b5399fdd726ac92bf887ab7ec70b6d53a763fd85c64230','250478','REVOKED','2026-03-24 16:50:54',0,'2026-03-24 16:35:54',NULL);
INSERT  IGNORE INTO `cell_access_tokens` VALUES (32,1534,'pickup',45,200,'b1718197c0a2e2dbfc63cc89fa7d84592f814632ea4fa0691db59352a6cbaf75','651617','REVOKED','2026-03-24 16:51:14',0,'2026-03-24 16:36:14',NULL);
INSERT  IGNORE INTO `cell_access_tokens` VALUES (33,1534,'pickup',45,200,'1ceba10f281f0f5ea0e12c4f6efd975ebdcf8dc4903d523d4241e771f8641bf0','569031','REVOKED','2026-03-24 16:55:29',0,'2026-03-24 16:40:29',NULL);
INSERT  IGNORE INTO `cell_access_tokens` VALUES (34,1534,'pickup',45,200,'931ea79ef1473a5cfc580e948d0a0b49df3c447099524c8529a27dd920f2fd9b','773253','REVOKED','2026-03-24 18:52:35',0,'2026-03-24 18:37:35',NULL);
INSERT  IGNORE INTO `cell_access_tokens` VALUES (35,1534,'pickup',45,200,'5498b3ed55256772f582c83189a783b7fbda4a45a5cf7559777222510ca02e73','234352','REVOKED','2026-03-25 02:53:03',0,'2026-03-25 02:38:02',NULL);
INSERT  IGNORE INTO `cell_access_tokens` VALUES (36,1534,'pickup',45,200,'26fdb6c5c0f94676fff1d746d93460b9c753c8a85b2af29246424aa77431d620','759692','REVOKED','2026-03-25 06:59:07',0,'2026-03-25 06:44:07',NULL);
INSERT  IGNORE INTO `cell_access_tokens` VALUES (37,1534,'pickup',45,200,'d214577561e71867fd35c44e41c5e286b4a8151e49ef625733b3d5ffc01f3663','901902','ACTIVE','2026-03-25 10:28:07',0,'2026-03-25 10:13:07',NULL);
INSERT  IGNORE INTO `cell_access_tokens` VALUES (38,1508,'pickup',16,100,'fdceb5e269c575f108525f58210b0b3914a5d13305a9728e997d5f13b8828e60','596864','REVOKED','2026-03-25 12:45:44',0,'2026-03-25 12:30:43',NULL);
INSERT  IGNORE INTO `cell_access_tokens` VALUES (39,1506,'pickup',2,100,'a391ca835fd542094ab7fd3d411633377fab8fc537d5b41293c76737fc7ca8f2','834708','REVOKED','2026-03-25 13:06:10',0,'2026-03-25 12:51:10',NULL);
INSERT  IGNORE INTO `cell_access_tokens` VALUES (40,1508,'pickup',16,100,'52702b4fdb7233df144d1e4514dfa39f376fb5ee8409bcb9c91b8085f6268c1c','299128','REVOKED','2026-03-25 13:06:45',0,'2026-03-25 12:51:45',NULL);
INSERT  IGNORE INTO `cell_access_tokens` VALUES (41,5,'pickup',2,777,'5d0fd43fcc5026227f498a72cdbb00bf2175cd93d4b25a1ae40f9f2b837ea4be','632493','REVOKED','2026-03-30 06:13:59',0,'2026-03-30 05:58:58',NULL);
INSERT  IGNORE INTO `cell_access_tokens` VALUES (42,5,'pickup',2,777,'02044df058339727da4b808a95085df5ce61a2164c5fa6384f717dd14133883e','386069','REVOKED','2026-03-30 06:14:09',0,'2026-03-30 05:59:08',NULL);
INSERT  IGNORE INTO `cell_access_tokens` VALUES (43,5,'pickup',2,777,'e5d9554aeaf54746139fd848c07f5c839077526972de973bd925986a7453a2bb','375039','ACTIVE','2026-03-30 06:15:44',0,'2026-03-30 06:00:43',NULL);
INSERT  IGNORE INTO `cell_access_tokens` VALUES (44,1536,'pickup',3,100,'6bc54e83df518a33d89a37fb78900394e91d0dcd252dd4fde227a34e81a23e95','207573','ACTIVE','2026-03-30 14:11:30',0,'2026-03-30 13:56:30',NULL);
INSERT  IGNORE INTO `cell_access_tokens` VALUES (45,1536,'pickup',3,200,'eb5fcb698faa5e50cfb9921453830e87280337cc93756d2f62de48cd44c658c9','860008','ACTIVE','2026-03-30 14:19:16',0,'2026-03-30 14:04:16',NULL);
INSERT  IGNORE INTO `cell_access_tokens` VALUES (46,1536,'delivery',13,200,'a8a7cff0dcb9d682fa876ff79902f8d0f00c49ce9317137158f4fbaf9479eb66','319419','ACTIVE','2026-03-30 17:07:14',0,'2026-03-30 16:52:13',NULL);
INSERT  IGNORE INTO `cell_access_tokens` VALUES (47,1536,'delivery',13,103,'8c141a2bbbb478a800056e728d2fca45033c20e488b7b12b85910792c07d0801','598012','REVOKED','2026-03-30 17:32:19',0,'2026-03-30 17:17:19',NULL);
INSERT  IGNORE INTO `cell_access_tokens` VALUES (48,1536,'delivery',13,103,'7603827409f338945da92001b795cf4bfd2be7971e271ef560807952e4abfd65','182388','REVOKED','2026-03-30 17:33:05',0,'2026-03-30 17:18:04',NULL);
INSERT  IGNORE INTO `cell_access_tokens` VALUES (49,1531,'pickup',10,100,'a91ef7c262a32395fd30bddb5e272eb4a862b67bd899608af6a9aecdc1559907','558396','REVOKED','2026-04-01 03:15:42',0,'2026-04-01 03:00:42',NULL);
INSERT  IGNORE INTO `cell_access_tokens` VALUES (50,1508,'pickup',16,100,'04f2ac8ee1cd926bccc7aa054eb32e51e66d4099ebe966741c029cd84515560e','132472','REVOKED','2026-04-01 03:21:57',0,'2026-04-01 03:06:57',NULL);
INSERT  IGNORE INTO `cell_access_tokens` VALUES (51,1507,'pickup',3,100,'f176278490bcd09bf0ba92b0568052d7292dd4fdc75581ebcd0f99bf6eef11c1','489998','REVOKED','2026-04-01 03:23:13',0,'2026-04-01 03:08:12',NULL);
INSERT  IGNORE INTO `cell_access_tokens` VALUES (52,1363,'pickup',1,100,'396ecbe1ef281445f706ffa4da7fb104fae19c4222aa6dca96b1db46afb242c1','830935','REVOKED','2026-04-01 03:25:53',0,'2026-04-01 03:10:52',NULL);
INSERT  IGNORE INTO `cell_access_tokens` VALUES (53,1536,'delivery',13,777,'fe336ed738d98bc39118375b6863a51fec631fad8c81baa0a7c5f2c5d82e90cd','794343','ACTIVE','2026-04-01 03:26:53',0,'2026-04-01 03:11:52',NULL);
INSERT  IGNORE INTO `cell_access_tokens` VALUES (54,1363,'pickup',1,100,'9ce8ceffa3806f5d4bc180fa4595888b866779fa10714a0684cdc131cbdb2ece','508591','REVOKED','2026-04-01 03:41:18',0,'2026-04-01 03:26:18',NULL);
INSERT  IGNORE INTO `cell_access_tokens` VALUES (55,1502,'pickup',43,100,'47528ae541af307571e966867760b9c68575fb852cc7fc997773fb7de83ba909','149582','REVOKED','2026-04-01 09:06:17',0,'2026-04-01 08:51:16',NULL);
INSERT  IGNORE INTO `cell_access_tokens` VALUES (56,1531,'pickup',10,100,'fbd00f126c6f61ade5ef435726d6d494e49350ddb487e7e151af76cc7fbe1eba','468450','REVOKED','2026-04-01 09:13:43',0,'2026-04-01 08:58:42',NULL);
INSERT  IGNORE INTO `cell_access_tokens` VALUES (57,1363,'pickup',1,100,'91f5d4334a83a80738d8455d8d7a12e148db075fa3f0c66b96c2aaf2516d88ef','882173','REVOKED','2026-04-01 09:14:53',0,'2026-04-01 08:59:52',NULL);
INSERT  IGNORE INTO `cell_access_tokens` VALUES (58,1502,'pickup',43,100,'d82bf2cf0247ca77f4ee1d181910e771636af0e3df5614fc0ec5e0b8c6ed18aa','718420','REVOKED','2026-04-01 09:47:40',0,'2026-04-01 09:32:40',NULL);
INSERT  IGNORE INTO `cell_access_tokens` VALUES (59,1363,'pickup',1,100,'30823f31a7b4b8a9672b7b885351fb2ff535c9edbcb12097d34a0810b4a73101','645964','REVOKED','2026-04-01 09:48:40',0,'2026-04-01 09:33:40',NULL);
INSERT  IGNORE INTO `cell_access_tokens` VALUES (60,1526,'pickup',1,1001,'5ba93d3d844fd04b1b84532551c0b4662e7becf8b29028e81ec0fe011e022625','485152','ACTIVE','2026-04-01 10:00:32',0,'2026-04-01 09:45:31',NULL);
INSERT  IGNORE INTO `cell_access_tokens` VALUES (61,1531,'pickup',10,100,'185243eebe50cfce77aa98e5af62ab37370dab86f823a0ae5a878d65935dd68c','478624','ACTIVE','2026-04-01 10:00:52',0,'2026-04-01 09:45:51',NULL);
INSERT  IGNORE INTO `cell_access_tokens` VALUES (62,1531,'pickup',10,200,'35bf4df740025e566aa6dcce9f2a44137717d509580748baf0cd6f4e8a660866','687901','ACTIVE','2026-04-01 10:10:54',0,'2026-04-01 09:55:53',NULL);
INSERT  IGNORE INTO `cell_access_tokens` VALUES (63,1508,'pickup',16,100,'2909f342b5d4a1a56a272a58c6f01a02b0d90e4bb5340fdcde511d8b7cf8c3bd','761586','REVOKED','2026-04-01 10:28:36',0,'2026-04-01 10:13:35',NULL);
INSERT  IGNORE INTO `cell_access_tokens` VALUES (64,1507,'pickup',3,100,'165da73063a767aef2faf445395ab089487314aeb41f1ce878eec7c35cee3250','261805','REVOKED','2026-04-01 10:28:36',0,'2026-04-01 10:13:36',NULL);
INSERT  IGNORE INTO `cell_access_tokens` VALUES (65,1506,'pickup',2,100,'a408d80ffcfc30b604a007a53703cb45c34f728796c5c7df5054a5368bee8910','287152','REVOKED','2026-04-01 10:28:36',0,'2026-04-01 10:13:36',NULL);
INSERT  IGNORE INTO `cell_access_tokens` VALUES (66,1363,'pickup',1,100,'da863fc5c39adaf236f4985beec36818ef7c946c01180f61810ea37426b2937c','776050','REVOKED','2026-04-01 10:29:41',0,'2026-04-01 10:14:41',NULL);
INSERT  IGNORE INTO `cell_access_tokens` VALUES (67,1502,'pickup',43,100,'c9dbdb907c9a9c5cd584466bd9a07c07de54b5eb0649c9c407bddea68a197ac4','656910','REVOKED','2026-04-01 10:30:02',0,'2026-04-01 10:15:01',NULL);
INSERT  IGNORE INTO `cell_access_tokens` VALUES (68,1506,'pickup',2,100,'81fcb891fe28f324d4c30ca29b8301c9f0fd274e56d82f3e7fc04757ee543ce4','545255','REVOKED','2026-04-01 10:30:27',0,'2026-04-01 10:15:26',NULL);
INSERT  IGNORE INTO `cell_access_tokens` VALUES (69,1363,'pickup',1,100,'c0dea4a8586749d65aa1b6a8efd3491a504872acc5b1c5d3f7a5f65a516db68b','162520','ACTIVE','2026-04-01 10:32:07',0,'2026-04-01 10:17:06',NULL);
INSERT  IGNORE INTO `cell_access_tokens` VALUES (70,1502,'pickup',43,100,'caa9b61dbac1945afb38d588955a54718523cc0914304f258298fadc12a96748','599366','REVOKED','2026-04-01 10:32:07',0,'2026-04-01 10:17:07',NULL);
INSERT  IGNORE INTO `cell_access_tokens` VALUES (71,1508,'pickup',16,100,'b16c439d2725b436b8253edc65764c035efdedb04fc5f6de7ca7f4b033670216','948091','REVOKED','2026-04-01 10:32:12',0,'2026-04-01 10:17:12',NULL);
INSERT  IGNORE INTO `cell_access_tokens` VALUES (72,1507,'pickup',3,100,'32e361a1eb2b9dbfba8c450a21f2f8671eb15dc83dbe6c25cab32081c6e37776','721917','REVOKED','2026-04-01 10:32:12',0,'2026-04-01 10:17:12',NULL);
INSERT  IGNORE INTO `cell_access_tokens` VALUES (73,1506,'pickup',2,100,'681db3a1eab902f692042d3a0dc2c3a1441ec6aa3095ffecbf14c7eb7fd90246','576781','ACTIVE','2026-04-01 10:32:12',0,'2026-04-01 10:17:12',NULL);
INSERT  IGNORE INTO `cell_access_tokens` VALUES (74,1514,'pickup',21,100,'f43a10bd3899ab312e8b97a57302234c5692d48a46acc17d2ae628cb27deb932','611781','ACTIVE','2026-04-01 10:32:17',0,'2026-04-01 10:17:17',NULL);
INSERT  IGNORE INTO `cell_access_tokens` VALUES (75,1508,'pickup',16,100,'591bb385ef7d950c49f7937f93de8ca4b0db6a5f798f1207dfc59182c352556c','867753','REVOKED','2026-04-02 14:39:13',0,'2026-04-02 14:24:12',NULL);
INSERT  IGNORE INTO `cell_access_tokens` VALUES (76,1536,'delivery',13,103,'0cf70bf2fec02e31264cd27ee59a8257235ce6be2aef3358a31f367924be0d13','383912','REVOKED','2026-04-02 17:51:46',0,'2026-04-02 17:36:46',NULL);
INSERT  IGNORE INTO `cell_access_tokens` VALUES (77,1536,'delivery',13,103,'40bab825378c69fbae2d6e948457d33f71e9cdeb7d0ec5d9fab301108d12f42c','784943','ACTIVE','2026-04-02 17:51:56',0,'2026-04-02 17:36:56',NULL);
INSERT  IGNORE INTO `cell_access_tokens` VALUES (78,1508,'pickup',16,100,'c99c6d3e3fedd22c35ecbf4bf7d410ff16a12aea0ca44cc2e7838bd97d4c8bca','753381','ACTIVE','2026-04-04 15:34:10',0,'2026-04-04 15:19:10',NULL);
INSERT  IGNORE INTO `cell_access_tokens` VALUES (79,1507,'pickup',3,100,'1cbc8860a74b779ddf57ca968f6ef1422ab3a0a5a0ba60435146270de679d5b8','960148','REVOKED','2026-04-04 15:34:15',0,'2026-04-04 15:19:15',NULL);
INSERT  IGNORE INTO `cell_access_tokens` VALUES (80,1507,'pickup',3,100,'132076eb6dc6e741686e413b678cb401a8ec5e03fb515c3aaf7d8a1fdc21d848','260194','REVOKED','2026-04-04 16:01:17',0,'2026-04-04 15:46:17',NULL);
INSERT  IGNORE INTO `cell_access_tokens` VALUES (81,1507,'pickup',3,100,'c15425ccc851ca7899a32c0a6f46cc1eee84eb9b66daa30e248d63615f22b766','698174','REVOKED','2026-04-04 17:11:10',0,'2026-04-04 16:56:09',NULL);
INSERT  IGNORE INTO `cell_access_tokens` VALUES (82,1502,'pickup',43,100,'54eb77ac1a6f190d494299c086b320d53053a47b204c06edfcff31a6fb0de032','177464','ACTIVE','2026-04-06 11:40:02',0,'2026-04-06 11:25:02',NULL);
INSERT  IGNORE INTO `cell_access_tokens` VALUES (83,1507,'pickup',3,100,'1a3e672d0d33f6689b0538416441dbe5ccd332e76d4cfc49e05c90d01f007e7e','286055','ACTIVE','2026-04-06 11:41:13',0,'2026-04-06 11:26:12',NULL);
INSERT  IGNORE INTO `cell_access_tokens` VALUES (84,1367,'pickup',42,100,'0c9ac9fbe796c76c6b86f91ec1a5ef270740bd3ed247320c78a7355ddf4ed93b','488387','ACTIVE','2026-04-06 11:42:18',0,'2026-04-06 11:27:17',NULL);
INSERT  IGNORE INTO `cell_access_tokens` VALUES (85,1364,'pickup',41,100,'d523374b5fb0ef9d84037319b27ab7732b6508c038b27345c4ac2b52ad574e89','706649','ACTIVE','2026-04-06 11:50:58',0,'2026-04-06 11:35:58',NULL);
INSERT  IGNORE INTO `cell_access_tokens` VALUES (86,1365,'pickup',42,100,'2dace993323f3228e77cca635dea21f52c7a0fefad071c1560d841ae5ccab605','488989','REVOKED','2026-04-06 11:51:39',0,'2026-04-06 11:36:38',NULL);
INSERT  IGNORE INTO `cell_access_tokens` VALUES (87,1365,'pickup',42,100,'ae5ee74558c1fbf25e76cd35e5fb02940f89b628ae36d05ae29424d939409c6e','340951','ACTIVE','2026-04-06 14:37:29',0,'2026-04-06 14:22:29',NULL);

--
-- Table structure for table `core_entity_mapping`
--

DROP TABLE IF EXISTS `core_entity_mapping`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `core_entity_mapping` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `local_entity_type` varchar(50) COLLATE utf8mb4_unicode_ci NOT NULL,
  `local_entity_id` int NOT NULL,
  `core_entity_type` varchar(50) COLLATE utf8mb4_unicode_ci NOT NULL,
  `core_entity_id` int NOT NULL,
  `sync_status` enum('success','failed') COLLATE utf8mb4_unicode_ci DEFAULT 'success',
  `last_sync_at` datetime DEFAULT NULL,
  `error_message` text COLLATE utf8mb4_unicode_ci,
  `created_at` datetime DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  UNIQUE KEY `uk_local` (`local_entity_type`,`local_entity_id`),
  UNIQUE KEY `uk_core` (`core_entity_type`,`core_entity_id`)
) ENGINE=InnoDB AUTO_INCREMENT=4 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `core_entity_mapping`
--

INSERT  IGNORE INTO `core_entity_mapping` VALUES (1,'order',1539,'order',1568,'success','2026-04-08 09:26:10',NULL,'2026-04-08 09:26:10');
INSERT  IGNORE INTO `core_entity_mapping` VALUES (2,'order',1540,'order',1569,'success','2026-04-08 12:57:55',NULL,'2026-04-08 12:57:55');
INSERT  IGNORE INTO `core_entity_mapping` VALUES (3,'order',1541,'order',1570,'success','2026-04-08 13:05:06',NULL,'2026-04-08 13:05:06');

--
-- Table structure for table `core_user_mapping`
--

DROP TABLE IF EXISTS `core_user_mapping`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `core_user_mapping` (
  `local_user_id` int NOT NULL,
  `core_u_id` int NOT NULL,
  `core_role` int NOT NULL COMMENT '1=client, 2=performer, 3=admin',
  `performer_type` enum('driver','courier','client') DEFAULT NULL,
  `transport_type` varchar(50) DEFAULT NULL COMMENT 'car|bike|foot',
  `capabilities` json DEFAULT NULL COMMENT '["delivery", "cargo"]',
  `registered_at` datetime DEFAULT CURRENT_TIMESTAMP,
  `last_sync_at` datetime DEFAULT NULL,
  `sync_status` enum('success','failed') DEFAULT 'success',
  `error_message` text,
  `token` varchar(255) DEFAULT NULL,
  `u_hash` varchar(255) DEFAULT NULL,
  PRIMARY KEY (`local_user_id`),
  UNIQUE KEY `uk_core` (`core_u_id`),
  KEY `idx_performer_type` (`performer_type`),
  KEY `idx_transport_type` (`transport_type`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `core_user_mapping`
--

INSERT  IGNORE INTO `core_user_mapping` VALUES (1000006,972,2,'driver','car','[\"delivery\"]','2026-04-03 09:15:56','2026-04-03 09:15:56','success',NULL,NULL,NULL);
INSERT  IGNORE INTO `core_user_mapping` VALUES (1000007,973,1,'driver','',NULL,'2026-04-03 12:31:32','2026-04-03 12:31:32','success',NULL,NULL,NULL);
INSERT  IGNORE INTO `core_user_mapping` VALUES (1000008,974,1,'driver','',NULL,'2026-04-03 13:15:57','2026-04-03 13:15:57','success',NULL,NULL,NULL);
INSERT  IGNORE INTO `core_user_mapping` VALUES (1000009,975,1,'driver','',NULL,'2026-04-03 13:26:11','2026-04-03 13:26:11','success',NULL,NULL,NULL);
INSERT  IGNORE INTO `core_user_mapping` VALUES (1000010,976,1,'driver','',NULL,'2026-04-03 13:32:02','2026-04-03 13:32:02','success',NULL,NULL,NULL);
INSERT  IGNORE INTO `core_user_mapping` VALUES (1000011,977,1,'driver','',NULL,'2026-04-03 13:35:30','2026-04-03 13:35:30','success',NULL,NULL,NULL);
INSERT  IGNORE INTO `core_user_mapping` VALUES (1000012,980,1,'driver','',NULL,'2026-04-03 14:03:17','2026-04-03 14:03:17','success',NULL,NULL,NULL);
INSERT  IGNORE INTO `core_user_mapping` VALUES (1000013,981,1,'driver','',NULL,'2026-04-03 14:03:48','2026-04-08 07:53:20','success',NULL,'3652bad322370b9e57db8d3126de75bd','GLhpZSvjhquCg8L7vvqUq8xzyvF6VMaqJfoLioHXvjiiG5B8R9Ott4a3mWE/KpCnuvv6aYpR0t28cURQrB3ElU/onQS/+4AemQKG76s8i6Z98b3sZk0FZZWbRqqa4u7r');
INSERT  IGNORE INTO `core_user_mapping` VALUES (1000014,982,1,'driver','',NULL,'2026-04-03 15:08:34','2026-04-03 15:08:34','success',NULL,NULL,NULL);
INSERT  IGNORE INTO `core_user_mapping` VALUES (1000015,983,2,'driver','bike','[\"delivery\"]','2026-04-03 15:54:03','2026-04-03 15:54:03','success',NULL,NULL,NULL);
INSERT  IGNORE INTO `core_user_mapping` VALUES (1000016,984,2,'driver','bike','[\"delivery\"]','2026-04-03 16:46:11','2026-04-03 16:46:11','success',NULL,NULL,NULL);
INSERT  IGNORE INTO `core_user_mapping` VALUES (1000017,985,2,'driver',NULL,'[\"delivery\"]','2026-04-03 17:27:01','2026-04-03 17:27:01','success',NULL,NULL,NULL);
INSERT  IGNORE INTO `core_user_mapping` VALUES (1000018,986,2,'driver','bike','[\"delivery\"]','2026-04-03 17:34:17','2026-04-03 17:34:17','success',NULL,NULL,NULL);
INSERT  IGNORE INTO `core_user_mapping` VALUES (1000019,987,1,NULL,'',NULL,'2026-04-03 17:45:14','2026-04-03 17:45:14','success',NULL,NULL,NULL);
INSERT  IGNORE INTO `core_user_mapping` VALUES (1000020,994,1,NULL,'',NULL,'2026-04-07 20:38:14','2026-04-07 20:38:14','success',NULL,NULL,NULL);
INSERT  IGNORE INTO `core_user_mapping` VALUES (1000021,995,1,NULL,'',NULL,'2026-04-08 06:16:44','2026-04-08 06:52:12','success',NULL,'61b95264b30a0d0df8c3ba96ef748237','UfLwb6zSRhQzEL9qvVyga4DBdbmVu0o8Ux8ky4oGMMPFtAqlchy8AwuKyrjRTEguF5ErYD9/ZeXpvoSyr6/CO47G4Jrvj0pChok3L5h1hHEGQ18tK/llMDKHbaq98wd9');
INSERT  IGNORE INTO `core_user_mapping` VALUES (1000022,996,2,'driver','bike','[\"delivery\"]','2026-04-08 06:39:27','2026-04-08 06:47:44','success',NULL,'6d63de23f73c8891401053dbfb0104fd','F5SqVbTlqRMCWB7o869oLJtk0g2jKjz141XiSo9VhLoKDun6wsjFMV1uVM3qApyq5XmGWeeFISsQXfe8ZR4gpljNUm7bo51VmVaE7y9ArWjbdKQUftQZpXiaHrclpwI3');
INSERT  IGNORE INTO `core_user_mapping` VALUES (1000023,997,2,'driver','bike','[\"delivery\"]','2026-04-08 07:16:39','2026-04-08 07:16:39','success',NULL,'5a6dbc5b09ff04c0e0754df93653eeeb','cep4Jf3YKqwN2xLBNRwPBW9CXfi9kxMp2tRTIOBWLlp++EXmtLigNf0I54yajDbFYp1NU5PZZ8bViwXee9ghLREucO00S9h2DB2z5RskJj/jvqr/6MClt9FvUmzqdll9');
INSERT  IGNORE INTO `core_user_mapping` VALUES (1000024,998,2,'driver','bike','[\"delivery\"]','2026-04-08 07:44:32','2026-04-08 07:44:32','success',NULL,'cfca686c02f0055bb462a7f0b7f43394','DSao0OYmOERyV3Cil/FwRmV1mKDNojsarOWZJWW1g1MSBHXaEGX3oQMNMpehBV5FFpG2oNcVEcla1uLaOUhNmOx+CyC+gdsjrqq5rlJ3l5Y+9rdXgy3youc+TQdRgWsu');

--
-- Table structure for table `directions`
--

DROP TABLE IF EXISTS `directions`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `directions` (
  `id` int NOT NULL AUTO_INCREMENT,
  `from_city` varchar(100) NOT NULL,
  `to_city` varchar(100) NOT NULL,
  `pickup_locker_id` int NOT NULL,
  `delivery_locker_id` int NOT NULL,
  `orders_available` int DEFAULT '0',
  `orders_reserved` int DEFAULT '0',
  PRIMARY KEY (`id`),
  UNIQUE KEY `unique_route` (`from_city`,`to_city`,`pickup_locker_id`,`delivery_locker_id`)
) ENGINE=InnoDB AUTO_INCREMENT=3 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `directions`
--

INSERT  IGNORE INTO `directions` VALUES (1,'МСК','СПБ',1,2,0,0);
INSERT  IGNORE INTO `directions` VALUES (2,'СПБ','МСК',2,1,0,1);

--
-- Table structure for table `driver_reservations`
--

DROP TABLE IF EXISTS `driver_reservations`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `driver_reservations` (
  `id` int NOT NULL AUTO_INCREMENT,
  `driver_user_id` int NOT NULL,
  `direction_id` int NOT NULL,
  `reserved_count` int NOT NULL,
  `requested_count` int NOT NULL,
  `reserved_at` datetime DEFAULT CURRENT_TIMESTAMP,
  `expires_at` datetime NOT NULL,
  `status` varchar(50) DEFAULT 'reservation_active',
  PRIMARY KEY (`id`),
  KEY `driver_id` (`driver_user_id`),
  KEY `direction_id` (`direction_id`),
  CONSTRAINT `fk_res_dir` FOREIGN KEY (`direction_id`) REFERENCES `directions` (`id`) ON DELETE CASCADE,
  CONSTRAINT `fk_reservations_driver` FOREIGN KEY (`driver_user_id`) REFERENCES `users` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=27 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `driver_reservations`
--

INSERT  IGNORE INTO `driver_reservations` VALUES (1,200,1,1,1,'2026-03-15 13:51:32','2026-03-15 14:21:33','reservation_completed');
INSERT  IGNORE INTO `driver_reservations` VALUES (3,200,1,1,1,'2026-03-17 09:43:03','2026-03-17 10:13:04','reservation_completed');
INSERT  IGNORE INTO `driver_reservations` VALUES (5,200,1,1,1,'2026-03-18 14:23:34','2026-03-18 14:53:35','reservation_completed');
INSERT  IGNORE INTO `driver_reservations` VALUES (6,200,1,1,2,'2026-03-19 16:03:52','2026-03-19 16:33:53','reservation_cancelled');
INSERT  IGNORE INTO `driver_reservations` VALUES (7,200,1,1,1,'2026-03-21 12:21:29','2026-03-21 12:51:29','reservation_expired');
INSERT  IGNORE INTO `driver_reservations` VALUES (8,200,1,1,1,'2026-03-21 13:00:50','2026-03-21 13:30:51','reservation_expired');
INSERT  IGNORE INTO `driver_reservations` VALUES (9,200,1,1,1,'2026-03-21 13:41:02','2026-03-21 14:11:02','reservation_expired');
INSERT  IGNORE INTO `driver_reservations` VALUES (10,200,1,1,1,'2026-03-21 16:32:09','2026-03-21 17:02:10','reservation_expired');
INSERT  IGNORE INTO `driver_reservations` VALUES (11,200,1,1,20,'2026-03-21 18:14:48','2026-03-21 18:44:48','reservation_expired');
INSERT  IGNORE INTO `driver_reservations` VALUES (12,200,1,1,1,'2026-03-22 07:33:45','2026-03-22 08:03:46','reservation_completed');
INSERT  IGNORE INTO `driver_reservations` VALUES (13,200,2,1,20,'2026-03-22 09:53:15','2026-03-22 10:23:15','reservation_expired');
INSERT  IGNORE INTO `driver_reservations` VALUES (14,200,2,1,10,'2026-03-22 11:29:46','2026-03-22 11:59:46','reservation_cancelled');
INSERT  IGNORE INTO `driver_reservations` VALUES (15,200,1,1,1,'2026-03-22 15:17:20','2026-03-22 15:47:20','reservation_completed');
INSERT  IGNORE INTO `driver_reservations` VALUES (16,200,2,1,1,'2026-03-23 06:23:09','2026-03-23 06:53:10','reservation_expired');
INSERT  IGNORE INTO `driver_reservations` VALUES (17,200,1,1,1,'2026-03-23 09:13:18','2026-03-23 09:43:19','reservation_cancelled');
INSERT  IGNORE INTO `driver_reservations` VALUES (18,200,2,1,1,'2026-03-23 09:22:54','2026-03-23 09:52:54','reservation_cancelled');
INSERT  IGNORE INTO `driver_reservations` VALUES (19,200,1,1,1,'2026-03-23 09:41:20','2026-03-23 10:11:20','reservation_completed');
INSERT  IGNORE INTO `driver_reservations` VALUES (20,200,1,1,1,'2026-03-23 09:46:50','2026-03-23 10:16:51','reservation_expired');
INSERT  IGNORE INTO `driver_reservations` VALUES (21,200,1,1,1,'2026-03-23 10:47:43','2026-03-23 11:17:43','reservation_completed');
INSERT  IGNORE INTO `driver_reservations` VALUES (22,200,1,1,10,'2026-03-23 15:45:37','2026-03-23 16:15:37','reservation_completed');
INSERT  IGNORE INTO `driver_reservations` VALUES (23,200,2,1,1,'2026-03-23 17:54:51','2026-03-23 18:24:51','reservation_cancelled');
INSERT  IGNORE INTO `driver_reservations` VALUES (24,200,2,1,1,'2026-03-24 16:42:29','2026-03-24 17:12:30','reservation_completed');
INSERT  IGNORE INTO `driver_reservations` VALUES (25,200,1,1,10,'2026-03-30 14:03:51','2026-03-30 14:33:51','reservation_completed');
INSERT  IGNORE INTO `driver_reservations` VALUES (26,200,1,1,1,'2026-04-01 09:55:18','2026-04-01 10:25:18','reservation_completed');

--
-- Table structure for table `fsm_action_logs`
--

DROP TABLE IF EXISTS `fsm_action_logs`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `fsm_action_logs` (
  `id` int NOT NULL AUTO_INCREMENT,
  `entity_type` varchar(50) DEFAULT NULL,
  `entity_id` int DEFAULT NULL,
  `action_name` varchar(100) DEFAULT NULL,
  `from_state` varchar(50) DEFAULT NULL,
  `to_state` varchar(50) DEFAULT NULL,
  `user_id` int DEFAULT NULL,
  `created_at` datetime DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=1231 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `fsm_action_logs`
--

INSERT  IGNORE INTO `fsm_action_logs` VALUES (1069,'order',1527,'order_client_deliv_post1','order_created','order_client_post1',1001,'2026-03-15 13:35:51');
INSERT  IGNORE INTO `fsm_action_logs` VALUES (1070,'locker',5,'locker_open_locker','locker_reserved','locker_opened',1001,'2026-03-15 13:35:51');
INSERT  IGNORE INTO `fsm_action_logs` VALUES (1071,'order',1527,'order_confirm_parcel_in','order_client_post1','order_parcel_confirmed',1001,'2026-03-15 13:36:36');
INSERT  IGNORE INTO `fsm_action_logs` VALUES (1072,'locker',5,'locker_close_locker','locker_opened','locker_occupied',1001,'2026-03-15 13:36:36');
INSERT  IGNORE INTO `fsm_action_logs` VALUES (1073,'order',1528,'order_client_deliv_post1','order_created','order_client_post1',1001,'2026-03-15 13:47:02');
INSERT  IGNORE INTO `fsm_action_logs` VALUES (1074,'locker',6,'locker_open_locker','locker_reserved','locker_opened',1001,'2026-03-15 13:47:02');
INSERT  IGNORE INTO `fsm_action_logs` VALUES (1075,'order',1528,'order_confirm_parcel_in','order_client_post1','order_parcel_confirmed',1001,'2026-03-15 13:47:22');
INSERT  IGNORE INTO `fsm_action_logs` VALUES (1076,'locker',6,'locker_close_locker','locker_opened','locker_occupied',1001,'2026-03-15 13:47:22');
INSERT  IGNORE INTO `fsm_action_logs` VALUES (1077,'direction',1,'direction_reserve_slot','direction_open','direction_slot_taken',200,'2026-03-15 13:51:32');
INSERT  IGNORE INTO `fsm_action_logs` VALUES (1078,'order',1529,'order_assign_courier1_to_order','order_created','order_courier1_assigned',100,'2026-03-16 08:43:55');
INSERT  IGNORE INTO `fsm_action_logs` VALUES (1079,'direction',1,'direction_reserve_slot','direction_open','direction_open',200,'2026-03-17 09:43:03');
INSERT  IGNORE INTO `fsm_action_logs` VALUES (1082,'order',1527,'order_parcel_submitted','order_parcel_confirmed','order_parcel_submitted',200,'2026-03-17 09:49:29');
INSERT  IGNORE INTO `fsm_action_logs` VALUES (1083,'direction',1,'direction_start_loading','direction_open','direction_loading',200,'2026-03-17 09:49:29');
INSERT  IGNORE INTO `fsm_action_logs` VALUES (1084,'direction',1,'direction_complete_loading','direction_loading','direction_loading_finished',200,'2026-03-17 16:14:50');
INSERT  IGNORE INTO `fsm_action_logs` VALUES (1085,'driver_reservations',5,'driver_reservation_start_loading','reservation_active','reservation_loading',200,'2026-03-18 14:26:20');
INSERT  IGNORE INTO `fsm_action_logs` VALUES (1086,'locker',5,'locker_open_locker','locker_occupied','locker_opened',200,'2026-03-18 15:38:21');
INSERT  IGNORE INTO `fsm_action_logs` VALUES (1087,'order',1527,'order_parcel_submitted','order_parcel_confirmed','order_parcel_submitted',200,'2026-03-18 15:38:21');
INSERT  IGNORE INTO `fsm_action_logs` VALUES (1088,'locker',5,'locker_close_pickup','locker_opened','locker_closed_empty',200,'2026-03-18 16:15:32');
INSERT  IGNORE INTO `fsm_action_logs` VALUES (1089,'driver_reservations',5,'driver_reservation_complete_loading','reservation_loading','reservation_completed',200,'2026-03-18 16:26:08');
INSERT  IGNORE INTO `fsm_action_logs` VALUES (1090,'order',1530,'order_cancel_reservation','order_created','order_cancelled',1001,'2026-03-19 07:43:40');
INSERT  IGNORE INTO `fsm_action_logs` VALUES (1091,'locker',10,'locker_cancel_reservation','locker_reserved','locker_free',1001,'2026-03-19 07:43:40');
INSERT  IGNORE INTO `fsm_action_logs` VALUES (1092,'locker',20,'locker_cancel_reservation','locker_reserved','locker_free',1001,'2026-03-19 07:43:40');
INSERT  IGNORE INTO `fsm_action_logs` VALUES (1093,'trip',38,'trip_start_trip','trip_assigned','trip_in_progress',200,'2026-03-19 10:11:13');
INSERT  IGNORE INTO `fsm_action_logs` VALUES (1094,'order',1527,'order_start_transit','order_picked_up_from_post1','order_in_transit_to_post2',200,'2026-03-19 10:11:13');
INSERT  IGNORE INTO `fsm_action_logs` VALUES (1095,'locker',15,'locker_open_locker','locker_reserved','locker_opened',200,'2026-03-19 14:01:01');
INSERT  IGNORE INTO `fsm_action_logs` VALUES (1096,'order',1527,'order_arrive_at_post2','order_in_transit_to_post2','order_arrived_at_post2',200,'2026-03-19 14:01:01');
INSERT  IGNORE INTO `fsm_action_logs` VALUES (1097,'order',1527,'order_confirm_post2','order_arrived_at_post2','order_parcel_confirmed_post2',200,'2026-03-19 14:07:28');
INSERT  IGNORE INTO `fsm_action_logs` VALUES (1098,'locker',15,'locker_close_locker','locker_opened','locker_occupied',200,'2026-03-19 14:07:28');
INSERT  IGNORE INTO `fsm_action_logs` VALUES (1099,'order',5,'order_assign_courier1_to_order','order_created','order_courier1_assigned',100,'2026-03-19 14:33:54');
INSERT  IGNORE INTO `fsm_action_logs` VALUES (1100,'order',1529,'order_courier1_cancel','order_courier1_assigned','order_created',100,'2026-03-19 14:37:24');
INSERT  IGNORE INTO `fsm_action_logs` VALUES (1101,'order',1363,'order_assign_courier1_to_order','order_created','order_courier1_assigned',100,'2026-03-19 14:45:55');
INSERT  IGNORE INTO `fsm_action_logs` VALUES (1102,'trip',38,'trip_complete_trip','trip_in_progress','trip_completed',200,'2026-03-19 14:58:14');
INSERT  IGNORE INTO `fsm_action_logs` VALUES (1103,'driver_reservations',6,'driver_reservation_cancel','reservation_active','reservation_cancelled',200,'2026-03-19 16:11:04');
INSERT  IGNORE INTO `fsm_action_logs` VALUES (1104,'order',1531,'order_assign_courier1_to_order','order_created','order_courier1_assigned',100,'2026-03-20 12:55:03');
INSERT  IGNORE INTO `fsm_action_logs` VALUES (1105,'driver_reservations',7,'driver_reservation_expire','reservation_active','reservation_expired',999999,'2026-03-21 12:54:30');
INSERT  IGNORE INTO `fsm_action_logs` VALUES (1106,'driver_reservations',8,'driver_reservation_expire','reservation_active','reservation_expired',999999,'2026-03-21 13:34:32');
INSERT  IGNORE INTO `fsm_action_logs` VALUES (1107,'driver_reservations',9,'driver_reservation_expire','reservation_active','reservation_expired',999999,'2026-03-21 14:14:33');
INSERT  IGNORE INTO `fsm_action_logs` VALUES (1108,'driver_reservations',10,'driver_reservation_expire','reservation_active','reservation_expired',999999,'2026-03-21 17:04:40');
INSERT  IGNORE INTO `fsm_action_logs` VALUES (1109,'driver_reservations',11,'driver_reservation_expire','reservation_active','reservation_expired',999999,'2026-03-21 18:45:43');
INSERT  IGNORE INTO `fsm_action_logs` VALUES (1110,'driver_reservations',12,'driver_reservation_start_loading','reservation_active','reservation_loading',200,'2026-03-22 07:55:16');
INSERT  IGNORE INTO `fsm_action_logs` VALUES (1111,'order',1534,'order_client_deliv_post1','order_created','order_client_post1',1004,'2026-03-22 09:50:19');
INSERT  IGNORE INTO `fsm_action_logs` VALUES (1112,'locker',45,'locker_open_locker','locker_reserved','locker_opened',1004,'2026-03-22 09:50:19');
INSERT  IGNORE INTO `fsm_action_logs` VALUES (1113,'order',1534,'order_confirm_parcel_in','order_client_post1','order_parcel_confirmed',1004,'2026-03-22 09:50:44');
INSERT  IGNORE INTO `fsm_action_logs` VALUES (1114,'locker',45,'locker_close_locker','locker_opened','locker_occupied',1004,'2026-03-22 09:50:44');
INSERT  IGNORE INTO `fsm_action_logs` VALUES (1115,'driver_reservations',13,'driver_reservation_expire','reservation_active','reservation_expired',999999,'2026-03-22 10:27:50');
INSERT  IGNORE INTO `fsm_action_logs` VALUES (1116,'driver_reservations',14,'driver_reservation_start_loading','reservation_active','reservation_loading',200,'2026-03-22 11:32:31');
INSERT  IGNORE INTO `fsm_action_logs` VALUES (1117,'driver_reservations',14,'driver_reservation_cancel','reservation_loading','reservation_cancelled',200,'2026-03-22 15:09:24');
INSERT  IGNORE INTO `fsm_action_logs` VALUES (1118,'driver_reservations',12,'driver_reservation_complete_loading','reservation_loading','reservation_completed',200,'2026-03-22 15:16:50');
INSERT  IGNORE INTO `fsm_action_logs` VALUES (1119,'driver_reservations',15,'driver_reservation_start_loading','reservation_active','reservation_loading',200,'2026-03-22 15:22:45');
INSERT  IGNORE INTO `fsm_action_logs` VALUES (1120,'driver_reservations',15,'driver_reservation_complete_loading','reservation_loading','reservation_completed',200,'2026-03-23 06:23:09');
INSERT  IGNORE INTO `fsm_action_logs` VALUES (1121,'driver_reservations',16,'driver_reservation_expire','reservation_active','reservation_expired',999999,'2026-03-23 06:54:34');
INSERT  IGNORE INTO `fsm_action_logs` VALUES (1122,'driver_reservations',17,'driver_reservation_start_loading','reservation_active','reservation_loading',200,'2026-03-23 09:13:28');
INSERT  IGNORE INTO `fsm_action_logs` VALUES (1123,'driver_reservations',17,'driver_reservation_cancel','reservation_loading','reservation_cancelled',200,'2026-03-23 09:22:49');
INSERT  IGNORE INTO `fsm_action_logs` VALUES (1124,'driver_reservations',18,'driver_reservation_start_loading','reservation_active','reservation_loading',200,'2026-03-23 09:23:14');
INSERT  IGNORE INTO `fsm_action_logs` VALUES (1125,'driver_reservations',18,'driver_reservation_cancel','reservation_loading','reservation_cancelled',200,'2026-03-23 09:41:20');
INSERT  IGNORE INTO `fsm_action_logs` VALUES (1126,'driver_reservations',19,'driver_reservation_start_loading','reservation_active','reservation_loading',200,'2026-03-23 09:41:50');
INSERT  IGNORE INTO `fsm_action_logs` VALUES (1127,'driver_reservations',19,'driver_reservation_complete_loading','reservation_loading','reservation_completed',200,'2026-03-23 09:46:15');
INSERT  IGNORE INTO `fsm_action_logs` VALUES (1128,'driver_reservations',20,'driver_reservation_expire','reservation_active','reservation_expired',999999,'2026-03-23 10:19:25');
INSERT  IGNORE INTO `fsm_action_logs` VALUES (1129,'locker',5,'locker_reset','locker_closed_empty','locker_free',999999,'2026-03-23 10:47:43');
INSERT  IGNORE INTO `fsm_action_logs` VALUES (1130,'driver_reservations',21,'driver_reservation_start_loading','reservation_active','reservation_loading',200,'2026-03-23 10:47:53');
INSERT  IGNORE INTO `fsm_action_logs` VALUES (1131,'driver_reservations',21,'driver_reservation_complete_loading','reservation_loading','reservation_completed',200,'2026-03-23 15:40:57');
INSERT  IGNORE INTO `fsm_action_logs` VALUES (1132,'driver_reservations',22,'driver_reservation_start_loading','reservation_active','reservation_loading',200,'2026-03-23 15:46:02');
INSERT  IGNORE INTO `fsm_action_logs` VALUES (1133,'locker',6,'locker_open_locker','locker_occupied','locker_opened',200,'2026-03-23 15:54:43');
INSERT  IGNORE INTO `fsm_action_logs` VALUES (1134,'order',1528,'order_parcel_submitted','order_parcel_confirmed','order_parcel_submitted',200,'2026-03-23 15:54:43');
INSERT  IGNORE INTO `fsm_action_logs` VALUES (1135,'locker',6,'locker_close_pickup','locker_opened','locker_closed_empty',200,'2026-03-23 16:03:09');
INSERT  IGNORE INTO `fsm_action_logs` VALUES (1136,'order',1528,'order_pickup_by_voditel','order_parcel_submitted','order_picked_up_from_post1',200,'2026-03-23 16:03:09');
INSERT  IGNORE INTO `fsm_action_logs` VALUES (1137,'driver_reservations',22,'driver_reservation_complete_loading','reservation_loading','reservation_completed',200,'2026-03-23 16:05:15');
INSERT  IGNORE INTO `fsm_action_logs` VALUES (1138,'trip',43,'trip_start_trip','trip_assigned','trip_in_progress',200,'2026-03-23 17:19:46');
INSERT  IGNORE INTO `fsm_action_logs` VALUES (1139,'order',1528,'order_start_transit','order_picked_up_from_post1','order_in_transit_to_post2',200,'2026-03-23 17:19:46');
INSERT  IGNORE INTO `fsm_action_logs` VALUES (1140,'locker',6,'locker_reset','locker_closed_empty','locker_free',999999,'2026-03-23 17:19:46');
INSERT  IGNORE INTO `fsm_action_logs` VALUES (1141,'driver_reservations',23,'driver_reservation_start_loading','reservation_active','reservation_loading',200,'2026-03-23 17:55:41');
INSERT  IGNORE INTO `fsm_action_logs` VALUES (1142,'driver_reservations',23,'driver_reservation_cancel','reservation_loading','reservation_cancelled',200,'2026-03-24 16:41:14');
INSERT  IGNORE INTO `fsm_action_logs` VALUES (1143,'driver_reservations',24,'driver_reservation_start_loading','reservation_active','reservation_loading',200,'2026-03-24 16:42:34');
INSERT  IGNORE INTO `fsm_action_logs` VALUES (1144,'locker',45,'locker_open_locker','locker_occupied','locker_opened',200,'2026-03-25 10:13:17');
INSERT  IGNORE INTO `fsm_action_logs` VALUES (1145,'order',1534,'order_parcel_submitted','order_parcel_confirmed','order_parcel_submitted',200,'2026-03-25 10:13:17');
INSERT  IGNORE INTO `fsm_action_logs` VALUES (1146,'locker',45,'locker_close_pickup','locker_opened','locker_closed_empty',200,'2026-03-25 10:13:22');
INSERT  IGNORE INTO `fsm_action_logs` VALUES (1147,'order',1534,'order_pickup_by_voditel','order_parcel_submitted','order_picked_up_from_post1',200,'2026-03-25 10:13:22');
INSERT  IGNORE INTO `fsm_action_logs` VALUES (1148,'driver_reservations',24,'driver_reservation_complete_loading','reservation_loading','reservation_completed',200,'2026-03-25 10:13:32');
INSERT  IGNORE INTO `fsm_action_logs` VALUES (1149,'locker',45,'locker_reset','locker_closed_empty','locker_free',999999,'2026-03-25 10:48:43');
INSERT  IGNORE INTO `fsm_action_logs` VALUES (1150,'trip',34,'trip_reassign_driver','trip_failed','trip_assigned',200,'2026-03-26 08:24:30');
INSERT  IGNORE INTO `fsm_action_logs` VALUES (1151,'locker',2,'locker_open_locker','locker_reserved','locker_opened',777,'2026-03-30 06:00:03');
INSERT  IGNORE INTO `fsm_action_logs` VALUES (1152,'locker',2,'locker_close_locker','locker_opened','locker_occupied',777,'2026-03-30 06:00:28');
INSERT  IGNORE INTO `fsm_action_logs` VALUES (1153,'order',1536,'order_assign_courier1_to_order','order_created','order_courier1_assigned',100,'2026-03-30 13:41:24');
INSERT  IGNORE INTO `fsm_action_logs` VALUES (1154,'order',1536,'order_courier_pickup_parcel','order_courier1_assigned','order_courier_has_parcel',100,'2026-03-30 14:01:15');
INSERT  IGNORE INTO `fsm_action_logs` VALUES (1155,'locker',3,'locker_open_locker','locker_reserved','locker_opened',100,'2026-03-30 14:01:15');
INSERT  IGNORE INTO `fsm_action_logs` VALUES (1156,'order',1536,'order_confirm_parcel_in','order_courier_has_parcel','order_parcel_confirmed',100,'2026-03-30 14:03:15');
INSERT  IGNORE INTO `fsm_action_logs` VALUES (1157,'locker',3,'locker_close_locker','locker_opened','locker_occupied',100,'2026-03-30 14:03:15');
INSERT  IGNORE INTO `fsm_action_logs` VALUES (1158,'driver_reservations',25,'driver_reservation_start_loading','reservation_active','reservation_loading',200,'2026-03-30 14:04:06');
INSERT  IGNORE INTO `fsm_action_logs` VALUES (1159,'locker',3,'locker_open_locker','locker_occupied','locker_opened',200,'2026-03-30 14:04:26');
INSERT  IGNORE INTO `fsm_action_logs` VALUES (1160,'order',1536,'order_parcel_submitted','order_parcel_confirmed','order_parcel_submitted',200,'2026-03-30 14:04:26');
INSERT  IGNORE INTO `fsm_action_logs` VALUES (1161,'locker',3,'locker_close_pickup','locker_opened','locker_closed_empty',200,'2026-03-30 14:04:31');
INSERT  IGNORE INTO `fsm_action_logs` VALUES (1162,'order',1536,'order_pickup_by_voditel','order_parcel_submitted','order_picked_up_from_post1',200,'2026-03-30 14:04:31');
INSERT  IGNORE INTO `fsm_action_logs` VALUES (1163,'driver_reservations',25,'driver_reservation_complete_loading','reservation_loading','reservation_completed',200,'2026-03-30 14:16:32');
INSERT  IGNORE INTO `fsm_action_logs` VALUES (1164,'trip',44,'trip_start_trip','trip_assigned','trip_in_progress',200,'2026-03-30 16:16:50');
INSERT  IGNORE INTO `fsm_action_logs` VALUES (1165,'order',1536,'order_start_transit','order_picked_up_from_post1','order_in_transit_to_post2',200,'2026-03-30 16:16:50');
INSERT  IGNORE INTO `fsm_action_logs` VALUES (1166,'locker',3,'locker_reset','locker_closed_empty','locker_free',999999,'2026-03-30 16:16:50');
INSERT  IGNORE INTO `fsm_action_logs` VALUES (1167,'locker',13,'locker_open_locker','locker_reserved','locker_opened',200,'2026-03-30 16:57:13');
INSERT  IGNORE INTO `fsm_action_logs` VALUES (1168,'order',1536,'order_arrive_at_post2','order_in_transit_to_post2','order_arrived_at_post2',200,'2026-03-30 16:57:13');
INSERT  IGNORE INTO `fsm_action_logs` VALUES (1169,'order',1536,'order_confirm_post2','order_arrived_at_post2','order_parcel_confirmed_post2',200,'2026-03-30 16:57:48');
INSERT  IGNORE INTO `fsm_action_logs` VALUES (1170,'locker',13,'locker_close_locker','locker_opened','locker_occupied',200,'2026-03-30 16:57:48');
INSERT  IGNORE INTO `fsm_action_logs` VALUES (1171,'order',1536,'order_assign_courier2_to_order','order_parcel_confirmed_post2','order_courier2_assigned',103,'2026-03-30 17:10:08');
INSERT  IGNORE INTO `fsm_action_logs` VALUES (1172,'order',1536,'order_courier2_pickup_parcel','order_courier2_assigned','order_courier2_has_parcel',103,'2026-03-30 17:18:59');
INSERT  IGNORE INTO `fsm_action_logs` VALUES (1173,'locker',13,'locker_open_locker','locker_occupied','locker_opened',103,'2026-03-30 17:18:59');
INSERT  IGNORE INTO `fsm_action_logs` VALUES (1174,'order',1536,'order_courier2_delivered_parcel','order_courier2_has_parcel','order_courier2_parcel_delivered',103,'2026-03-30 17:19:29');
INSERT  IGNORE INTO `fsm_action_logs` VALUES (1175,'locker',13,'locker_close_pickup','locker_opened','locker_closed_empty',103,'2026-03-30 17:19:29');
INSERT  IGNORE INTO `fsm_action_logs` VALUES (1176,'locker',13,'locker_reset','locker_closed_empty','locker_free',999999,'2026-03-31 08:54:24');
INSERT  IGNORE INTO `fsm_action_logs` VALUES (1177,'order',1537,'order_cancel_reservation','order_created','order_cancelled',1004,'2026-03-31 08:54:49');
INSERT  IGNORE INTO `fsm_action_logs` VALUES (1178,'locker',45,'locker_cancel_reservation','locker_reserved','locker_free',1004,'2026-03-31 08:54:49');
INSERT  IGNORE INTO `fsm_action_logs` VALUES (1179,'locker',5,'locker_cancel_reservation','locker_reserved','locker_free',1004,'2026-03-31 08:54:49');
INSERT  IGNORE INTO `fsm_action_logs` VALUES (1180,'order',1538,'order_assign_courier1_to_order','order_created','order_courier1_assigned',103,'2026-03-31 08:59:10');
INSERT  IGNORE INTO `fsm_action_logs` VALUES (1181,'order',1538,'order_courier1_cancel','order_courier1_assigned','order_created',103,'2026-03-31 09:00:10');
INSERT  IGNORE INTO `fsm_action_logs` VALUES (1182,'order',1502,'order_courier_pickup_parcel','order_courier1_assigned','order_courier_has_parcel',100,'2026-04-01 09:32:55');
INSERT  IGNORE INTO `fsm_action_logs` VALUES (1183,'locker',43,'locker_open_locker','locker_reserved','locker_opened',100,'2026-04-01 09:32:55');
INSERT  IGNORE INTO `fsm_action_logs` VALUES (1184,'order',1502,'order_confirm_parcel_in','order_courier_has_parcel','order_parcel_confirmed',100,'2026-04-01 09:33:15');
INSERT  IGNORE INTO `fsm_action_logs` VALUES (1185,'locker',43,'locker_close_locker','locker_opened','locker_occupied',100,'2026-04-01 09:33:15');
INSERT  IGNORE INTO `fsm_action_logs` VALUES (1186,'order',1363,'order_courier_pickup_parcel','order_courier1_assigned','order_courier_has_parcel',100,'2026-04-01 09:34:05');
INSERT  IGNORE INTO `fsm_action_logs` VALUES (1187,'locker',1,'locker_open_locker','locker_reserved','locker_opened',100,'2026-04-01 09:34:05');
INSERT  IGNORE INTO `fsm_action_logs` VALUES (1188,'order',1363,'order_confirm_parcel_in','order_courier_has_parcel','order_parcel_confirmed',100,'2026-04-01 09:35:00');
INSERT  IGNORE INTO `fsm_action_logs` VALUES (1189,'locker',1,'locker_close_locker','locker_opened','locker_occupied',100,'2026-04-01 09:35:00');
INSERT  IGNORE INTO `fsm_action_logs` VALUES (1190,'order',1531,'order_courier_pickup_parcel','order_courier1_assigned','order_courier_has_parcel',100,'2026-04-01 09:46:01');
INSERT  IGNORE INTO `fsm_action_logs` VALUES (1191,'locker',10,'locker_open_locker','locker_reserved','locker_opened',100,'2026-04-01 09:46:01');
INSERT  IGNORE INTO `fsm_action_logs` VALUES (1192,'order',1531,'order_confirm_parcel_in','order_courier_has_parcel','order_parcel_confirmed',100,'2026-04-01 09:46:42');
INSERT  IGNORE INTO `fsm_action_logs` VALUES (1193,'locker',10,'locker_close_locker','locker_opened','locker_occupied',100,'2026-04-01 09:46:42');
INSERT  IGNORE INTO `fsm_action_logs` VALUES (1194,'driver_reservations',26,'driver_reservation_start_loading','reservation_active','reservation_loading',200,'2026-04-01 09:55:43');
INSERT  IGNORE INTO `fsm_action_logs` VALUES (1195,'locker',10,'locker_open_locker','locker_occupied','locker_opened',200,'2026-04-01 09:56:03');
INSERT  IGNORE INTO `fsm_action_logs` VALUES (1196,'order',1531,'order_parcel_submitted','order_parcel_confirmed','order_parcel_submitted',200,'2026-04-01 09:56:03');
INSERT  IGNORE INTO `fsm_action_logs` VALUES (1197,'locker',10,'locker_close_pickup','locker_opened','locker_closed_empty',200,'2026-04-01 09:56:19');
INSERT  IGNORE INTO `fsm_action_logs` VALUES (1198,'order',1531,'order_pickup_by_voditel','order_parcel_submitted','order_picked_up_from_post1',200,'2026-04-01 09:56:19');
INSERT  IGNORE INTO `fsm_action_logs` VALUES (1199,'driver_reservations',26,'driver_reservation_complete_loading','reservation_loading','reservation_completed',200,'2026-04-01 09:56:29');
INSERT  IGNORE INTO `fsm_action_logs` VALUES (1200,'trip',45,'trip_start_trip','trip_assigned','trip_in_progress',200,'2026-04-01 09:59:14');
INSERT  IGNORE INTO `fsm_action_logs` VALUES (1201,'order',1531,'order_start_transit','order_picked_up_from_post1','order_in_transit_to_post2',200,'2026-04-01 09:59:14');
INSERT  IGNORE INTO `fsm_action_logs` VALUES (1202,'order',1508,'order_courier_pickup_parcel','order_courier1_assigned','order_courier_has_parcel',100,'2026-04-01 10:13:46');
INSERT  IGNORE INTO `fsm_action_logs` VALUES (1203,'locker',16,'locker_open_locker','locker_reserved','locker_opened',100,'2026-04-01 10:13:46');
INSERT  IGNORE INTO `fsm_action_logs` VALUES (1204,'order',1508,'order_confirm_parcel_in','order_courier_has_parcel','order_parcel_confirmed',100,'2026-04-01 10:13:56');
INSERT  IGNORE INTO `fsm_action_logs` VALUES (1205,'locker',16,'locker_close_locker','locker_opened','locker_occupied',100,'2026-04-01 10:13:56');
INSERT  IGNORE INTO `fsm_action_logs` VALUES (1207,'order',1506,'order_courier_pickup_parcel','order_courier1_assigned','order_courier_has_parcel',100,'2026-04-01 10:14:06');
INSERT  IGNORE INTO `fsm_action_logs` VALUES (1208,'locker',2,'locker_open_locker','locker_occupied','locker_opened',100,'2026-04-01 10:14:06');
INSERT  IGNORE INTO `fsm_action_logs` VALUES (1209,'order',1506,'order_confirm_parcel_in','order_courier_has_parcel','order_parcel_confirmed',100,'2026-04-01 10:14:11');
INSERT  IGNORE INTO `fsm_action_logs` VALUES (1210,'locker',2,'locker_close_locker','locker_opened','locker_occupied',100,'2026-04-01 10:14:11');
INSERT  IGNORE INTO `fsm_action_logs` VALUES (1212,'locker',10,'locker_reset','locker_closed_empty','locker_free',999999,'2026-04-02 14:24:12');
INSERT  IGNORE INTO `fsm_action_logs` VALUES (1213,'order',1364,'order_assign_courier1_to_order','order_created','order_courier1_assigned',100,'2026-04-04 16:38:27');
INSERT  IGNORE INTO `fsm_action_logs` VALUES (1214,'order',1365,'order_assign_courier1_to_order','order_created','order_courier1_assigned',100,'2026-04-04 16:45:28');
INSERT  IGNORE INTO `fsm_action_logs` VALUES (1215,'order',1535,'order_assign_courier1_to_order','order_created','order_courier1_assigned',100,'2026-04-04 17:26:36');
INSERT  IGNORE INTO `fsm_action_logs` VALUES (1216,'order',1367,'order_assign_courier1_to_order','order_created','order_courier1_assigned',100,'2026-04-04 17:36:12');
INSERT  IGNORE INTO `fsm_action_logs` VALUES (1225,'order',1539,'order_cancel_reservation','order_created','order_cancelled',1000013,'2026-04-08 11:47:23');
INSERT  IGNORE INTO `fsm_action_logs` VALUES (1226,'locker',13,'locker_cancel_reservation','locker_reserved','locker_free',1000013,'2026-04-08 11:47:23');
INSERT  IGNORE INTO `fsm_action_logs` VALUES (1227,'locker',3,'locker_cancel_reservation','locker_reserved','locker_free',1000013,'2026-04-08 11:47:23');
INSERT  IGNORE INTO `fsm_action_logs` VALUES (1228,'order',1540,'order_cancel_reservation','order_created','order_cancelled',1000013,'2026-04-08 13:01:40');
INSERT  IGNORE INTO `fsm_action_logs` VALUES (1229,'locker',13,'locker_cancel_reservation','locker_reserved','locker_free',1000013,'2026-04-08 13:01:40');
INSERT  IGNORE INTO `fsm_action_logs` VALUES (1230,'locker',3,'locker_cancel_reservation','locker_reserved','locker_free',1000013,'2026-04-08 13:01:40');

--
-- Table structure for table `fsm_actions`
--

DROP TABLE IF EXISTS `fsm_actions`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `fsm_actions` (
  `id` int NOT NULL AUTO_INCREMENT,
  `name` varchar(50) NOT NULL,
  `label` varchar(100) DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=124 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `fsm_actions`
--

INSERT  IGNORE INTO `fsm_actions` VALUES (1,'locker_reserve_cell','Zabronirovat yacheyku');
INSERT  IGNORE INTO `fsm_actions` VALUES (2,'trip_assign_voditel','Naznachit voditelya');
INSERT  IGNORE INTO `fsm_actions` VALUES (3,'trip_start_trip','Nachat poyezdku');
INSERT  IGNORE INTO `fsm_actions` VALUES (4,'trip_complete_trip','Zavershit poyezdku');
INSERT  IGNORE INTO `fsm_actions` VALUES (5,'locker_open_locker','Otkryt yacheyku');
INSERT  IGNORE INTO `fsm_actions` VALUES (6,'locker_close_locker','Zakryt yacheyku');
INSERT  IGNORE INTO `fsm_actions` VALUES (7,'order_timeout_reservation','Taymaut rezervirovaniya');
INSERT  IGNORE INTO `fsm_actions` VALUES (8,'locker_confirm_parcel_in','Podtverdit posylku vnutri');
INSERT  IGNORE INTO `fsm_actions` VALUES (49,'order_assign_courier1_to_order','Naznachit Kurer1 na zakaz');
INSERT  IGNORE INTO `fsm_actions` VALUES (61,'order_timeout_confirmation','Taymaut podtverzhdeniya');
INSERT  IGNORE INTO `fsm_actions` VALUES (68,'order_client_will_deliver','Klient sam sdast posylku');
INSERT  IGNORE INTO `fsm_actions` VALUES (69,'order_confirm_parcel_in','Подтвердить посылку (Order)');
INSERT  IGNORE INTO `fsm_actions` VALUES (70,'order_parcel_submitted','Посылка сдана (Order)');
INSERT  IGNORE INTO `fsm_actions` VALUES (71,'order_courier_pickup_parcel','Kurer zabral posilku');
INSERT  IGNORE INTO `fsm_actions` VALUES (72,'locker_reset','sbros yacheiki');
INSERT  IGNORE INTO `fsm_actions` VALUES (73,'locker_set_locker_to_maintenance','perevesti v obsluzhivanie');
INSERT  IGNORE INTO `fsm_actions` VALUES (74,'order_cancel_reservation','otmenit rezervatsiyu');
INSERT  IGNORE INTO `fsm_actions` VALUES (75,'locker_confirm_parcel_not_found','posylka_ne_naidena');
INSERT  IGNORE INTO `fsm_actions` VALUES (76,'locker_cancel_reservation','otmena rezervatsii yacheiki');
INSERT  IGNORE INTO `fsm_actions` VALUES (77,'trip_start_pickup','nachat_zabir');
INSERT  IGNORE INTO `fsm_actions` VALUES (78,'trip_confirm_pickup','podtverdit_zabir');
INSERT  IGNORE INTO `fsm_actions` VALUES (79,'trip_confirm_delivery','podtverdit_dostavku');
INSERT  IGNORE INTO `fsm_actions` VALUES (81,'order_reserve_for_client_A_to_B','zarezervirovat_dlya_klienta_A_to_B');
INSERT  IGNORE INTO `fsm_actions` VALUES (82,'order_reserve_for_courier_A_to_B','zarezervirovat_dlya_kurera_A_to_B');
INSERT  IGNORE INTO `fsm_actions` VALUES (83,'order_pickup_by_voditel','voditel_zabral_posylku');
INSERT  IGNORE INTO `fsm_actions` VALUES (84,'order_start_transit','nachat_perevozku');
INSERT  IGNORE INTO `fsm_actions` VALUES (85,'order_arrive_at_post2','pridyal_k_post2');
INSERT  IGNORE INTO `fsm_actions` VALUES (86,'locker_confirm_parcel_out','Podtverdit poluchenie posylki iz yacheiki');
INSERT  IGNORE INTO `fsm_actions` VALUES (87,'locker_dont_closed','Yacheika ne zakryta posle raboty');
INSERT  IGNORE INTO `fsm_actions` VALUES (88,'order_pickup_poluchatel','Klient poluchil posylku');
INSERT  IGNORE INTO `fsm_actions` VALUES (89,'order_delivered_parcel','Zavershit zakaz posle polucheniya');
INSERT  IGNORE INTO `fsm_actions` VALUES (90,'order_assign_courier2_to_order','Naznachit kurera2');
INSERT  IGNORE INTO `fsm_actions` VALUES (91,'order_courier2_pickup_parcel','Kurer2 zabral iz post2');
INSERT  IGNORE INTO `fsm_actions` VALUES (92,'order_courier2_delivered_parcel','Kurer2 zavershil dostavku');
INSERT  IGNORE INTO `fsm_actions` VALUES (93,'order_report_parcel_missing','Posylka ne naidena v yacheike');
INSERT  IGNORE INTO `fsm_actions` VALUES (94,'order_report_delivery_failed','Soobshchit o neudache dostavki');
INSERT  IGNORE INTO `fsm_actions` VALUES (95,'order_request_manual_intervention','Zaprosit ruchnoe vmeshatelstvo');
INSERT  IGNORE INTO `fsm_actions` VALUES (96,'trip_report_driver_not_found','Soobshchit: voditel ne naiden');
INSERT  IGNORE INTO `fsm_actions` VALUES (97,'trip_report_failure','Soobshchit o sbue poezdki');
INSERT  IGNORE INTO `fsm_actions` VALUES (98,'trip_request_manual_intervention','Zaprosit ruchnoe vmeshatelstvo');
INSERT  IGNORE INTO `fsm_actions` VALUES (99,'order_courier1_cancel','Kurer1 otmenil do zabora');
INSERT  IGNORE INTO `fsm_actions` VALUES (100,'order_courier2_cancel','Kurer2 otmenil do zabora iz post2');
INSERT  IGNORE INTO `fsm_actions` VALUES (101,'order_timeout_no_pickup','Taymaut: kurer ne zabral posylku');
INSERT  IGNORE INTO `fsm_actions` VALUES (102,'trip_vzyat_reis','Vzyat reis');
INSERT  IGNORE INTO `fsm_actions` VALUES (103,'locker_confirm_parcel_out_recipient','Podtverdit vydachu poluchatelyu iz yacheiki');
INSERT  IGNORE INTO `fsm_actions` VALUES (104,'order_recipient_confirmed','Klient podtverdil poluchenie');
INSERT  IGNORE INTO `fsm_actions` VALUES (105,'locker_close_pickup',NULL);
INSERT  IGNORE INTO `fsm_actions` VALUES (106,'locker_failed_to_open','Ne otkrilas yacheika');
INSERT  IGNORE INTO `fsm_actions` VALUES (107,'order_confirm_post2','voditel polozhil posilku v post2');
INSERT  IGNORE INTO `fsm_actions` VALUES (108,'order_client_deliv_post1','client polozhil posilku v post1');
INSERT  IGNORE INTO `fsm_actions` VALUES (113,'driver_reservation_start_loading','Начать погрузку');
INSERT  IGNORE INTO `fsm_actions` VALUES (114,'driver_reservation_complete_loading','Завершить погрузку');
INSERT  IGNORE INTO `fsm_actions` VALUES (115,'driver_reservation_expire','Истёк таймаут');
INSERT  IGNORE INTO `fsm_actions` VALUES (116,'driver_reservation_cancel','Отменить резерв');
INSERT  IGNORE INTO `fsm_actions` VALUES (117,'trip_cancel','Отменить рейс');
INSERT  IGNORE INTO `fsm_actions` VALUES (123,'trip_reassign_driver','Переназначить водителя');

--
-- Table structure for table `fsm_errors_log`
--

DROP TABLE IF EXISTS `fsm_errors_log`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `fsm_errors_log` (
  `id` int NOT NULL AUTO_INCREMENT,
  `error_time` datetime DEFAULT NULL,
  `error_message` text,
  `entity_type` varchar(50) DEFAULT NULL,
  `entity_id` int DEFAULT NULL,
  `action_name` varchar(100) DEFAULT NULL,
  `user_id` int DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=363 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `fsm_errors_log`
--

INSERT  IGNORE INTO `fsm_errors_log` VALUES (2,'2026-03-20 12:47:32','FSM order_confirm_parcel_in failed: 1644 (45000): Invalid transition for order: no matching fsm_transitions','order',1531,'close_cell',1001);
INSERT  IGNORE INTO `fsm_errors_log` VALUES (3,'2026-03-20 12:47:42','FSM order_confirm_parcel_in failed: 1644 (45000): Invalid transition for order: no matching fsm_transitions','order',1531,'close_cell',1001);
INSERT  IGNORE INTO `fsm_errors_log` VALUES (4,'2026-03-20 13:50:10','USER_NOT_AUTHORIZED','order',1531,'request_locker_access_code',1001);
INSERT  IGNORE INTO `fsm_errors_log` VALUES (5,'2026-03-20 14:00:40','NO_FREE_CELLS','order_request',265,'order_creation',NULL);
INSERT  IGNORE INTO `fsm_errors_log` VALUES (6,'2026-03-20 14:19:08','NO_FREE_CELLS','order_request',266,'order_creation',NULL);
INSERT  IGNORE INTO `fsm_errors_log` VALUES (7,'2026-03-20 14:47:29','MISSING_PIN_IN_METADATA','order',1531,'open_cell',1001);
INSERT  IGNORE INTO `fsm_errors_log` VALUES (8,'2026-03-20 14:47:39','FSM order_confirm_parcel_in failed: 1644 (45000): Invalid transition for order: no matching fsm_transitions','order',1531,'close_cell',1001);
INSERT  IGNORE INTO `fsm_errors_log` VALUES (9,'2026-03-20 14:47:54','MISSING_METADATA','order',1531,'request_locker_access_code',1001);
INSERT  IGNORE INTO `fsm_errors_log` VALUES (10,'2026-03-20 15:23:26','MISSING_PIN_IN_METADATA','order',1386,'open_cell',2001);
INSERT  IGNORE INTO `fsm_errors_log` VALUES (11,'2026-03-20 15:23:36','FSM order_delivered_parcel failed: 1644 (45000): Invalid transition for order: no matching fsm_transitions','order',1386,'close_cell',2001);
INSERT  IGNORE INTO `fsm_errors_log` VALUES (12,'2026-03-20 15:23:46','MISSING_METADATA','order',1386,'request_locker_access_code',2001);
INSERT  IGNORE INTO `fsm_errors_log` VALUES (13,'2026-03-21 13:48:37','MISSING_PIN_IN_METADATA','order',1531,'open_cell',100);
INSERT  IGNORE INTO `fsm_errors_log` VALUES (14,'2026-03-21 13:48:52','FSM order_confirm_parcel_in failed: 1644 (45000): Invalid transition for order: no matching fsm_transitions','order',1531,'close_cell',100);
INSERT  IGNORE INTO `fsm_errors_log` VALUES (15,'2026-03-21 13:49:07','MISSING_PIN_IN_METADATA','order',1514,'open_cell',100);
INSERT  IGNORE INTO `fsm_errors_log` VALUES (16,'2026-03-21 13:49:12','Неизвестный статус курьера: order_created','order',1514,'close_cell',100);
INSERT  IGNORE INTO `fsm_errors_log` VALUES (17,'2026-03-21 13:49:47','MISSING_PIN_IN_METADATA','order',1531,'open_cell',100);
INSERT  IGNORE INTO `fsm_errors_log` VALUES (18,'2026-03-21 13:50:17','Неизвестный статус курьера: order_parcel_confirmed','order',1515,'close_cell',103);
INSERT  IGNORE INTO `fsm_errors_log` VALUES (19,'2026-03-21 13:50:17','MISSING_PIN_IN_METADATA','order',1525,'open_cell',103);
INSERT  IGNORE INTO `fsm_errors_log` VALUES (20,'2026-03-21 13:50:17','Неизвестный статус курьера: order_completed','order',1525,'close_cell',103);
INSERT  IGNORE INTO `fsm_errors_log` VALUES (21,'2026-03-21 13:50:22','MISSING_PIN_IN_METADATA','order',1513,'open_cell',103);
INSERT  IGNORE INTO `fsm_errors_log` VALUES (22,'2026-03-21 13:50:22','Неизвестный статус курьера: order_parcel_confirmed','order',1513,'close_cell',103);
INSERT  IGNORE INTO `fsm_errors_log` VALUES (23,'2026-03-21 13:50:38','MISSING_PIN_IN_METADATA','order',1524,'open_cell',104);
INSERT  IGNORE INTO `fsm_errors_log` VALUES (24,'2026-03-21 13:50:38','Неизвестный статус курьера: order_parcel_confirmed','order',1524,'close_cell',104);
INSERT  IGNORE INTO `fsm_errors_log` VALUES (25,'2026-03-22 08:30:37','START_LOADING_FAILED: FSM driver_reservation_start_loading failed: 1644 (45000): Invalid transition for driver_reservations: no matching fsm_transitions','direction',1,'direction_start_loading',200);
INSERT  IGNORE INTO `fsm_errors_log` VALUES (26,'2026-03-22 08:35:23','CANCEL_RESERVATION_FAILED: FSM driver_reservation_cancel failed: 1644 (45000): Invalid transition for driver_reservations: no matching fsm_transitions','driver_reservations',12,'driver_reservation_cancel',200);
INSERT  IGNORE INTO `fsm_errors_log` VALUES (27,'2026-03-22 08:48:44','CANCEL_RESERVATION_FAILED: FSM driver_reservation_cancel failed: 1644 (45000): Invalid transition for driver_reservations: no matching fsm_transitions','driver_reservations',12,'driver_reservation_cancel',200);
INSERT  IGNORE INTO `fsm_errors_log` VALUES (28,'2026-03-22 09:45:14','MISSING_PIN_IN_METADATA','order',1534,'open_cell',1004);
INSERT  IGNORE INTO `fsm_errors_log` VALUES (29,'2026-03-22 09:54:05','UNKNOWN_PROCESS: driver_reservation_start_loading','driver_reservations',13,'driver_reservation_start_loading',200);
INSERT  IGNORE INTO `fsm_errors_log` VALUES (30,'2026-03-22 09:58:04','NO_ACTIVE_RESERVATIONS','driver_reservations',13,'driver_reservation_start_loading',200);
INSERT  IGNORE INTO `fsm_errors_log` VALUES (31,'2026-03-22 10:17:09','USER_NOT_AUTHORIZED','order',1531,'request_locker_access_code',1001);
INSERT  IGNORE INTO `fsm_errors_log` VALUES (32,'2026-03-22 11:30:21','name \'direction_id\' is not defined','driver_reservations',14,'driver_reservation_start_loading',200);
INSERT  IGNORE INTO `fsm_errors_log` VALUES (33,'2026-03-22 14:04:37','CANCEL_RESERVATION_FAILED: validate_reservation_for_cancellation failed: DatabaseLayer.get_orders_by_reservation() missing 1 required positional argument: \'driver_user_id\'','driver_reservations',12,'driver_reservation_cancel',200);
INSERT  IGNORE INTO `fsm_errors_log` VALUES (34,'2026-03-22 14:28:12','CANCEL_RESERVATION_FAILED: validate_reservation_for_cancellation failed: \'bool\' object is not subscriptable','driver_reservations',14,'driver_reservation_cancel',200);
INSERT  IGNORE INTO `fsm_errors_log` VALUES (35,'2026-03-22 14:45:09','Нельзя начать погрузку: статус резерва \'reservation_loading\' (требуется \'reservation_active\')','driver_reservations',14,'driver_reservation_cancel',200);
INSERT  IGNORE INTO `fsm_errors_log` VALUES (36,'2026-03-22 15:04:02','CANCEL_RESERVATION_FAILED: FSM driver_reservation_cancel failed: 1644 (45000): Invalid transition for driver_reservations: no matching fsm_transitions','driver_reservations',14,'driver_reservation_cancel',200);
INSERT  IGNORE INTO `fsm_errors_log` VALUES (37,'2026-03-23 06:23:09','MISSING_PIN_IN_METADATA','order',1527,'open_cell',1001);
INSERT  IGNORE INTO `fsm_errors_log` VALUES (38,'2026-03-23 06:23:09','USER_NOT_AUTHORIZED','order',1531,'request_locker_access_code',1001);
INSERT  IGNORE INTO `fsm_errors_log` VALUES (39,'2026-03-23 06:23:09','NO_FREE_CELLS','order_request',268,'order_creation',NULL);
INSERT  IGNORE INTO `fsm_errors_log` VALUES (40,'2026-03-23 06:23:09','NO_FREE_CELLS','order_request',269,'order_creation',NULL);
INSERT  IGNORE INTO `fsm_errors_log` VALUES (41,'2026-03-23 06:23:09','Нельзя начать погрузку: статус резерва \'reservation_completed\' (требуется \'reservation_active\')','driver_reservations',15,'driver_reservation_cancel',200);
INSERT  IGNORE INTO `fsm_errors_log` VALUES (42,'2026-03-23 08:19:22','User 3 has no city','order_request',270,'order_creation',NULL);
INSERT  IGNORE INTO `fsm_errors_log` VALUES (43,'2026-03-23 09:23:29','INVALID_LEG_IN_METADATA','order',1534,'open_cell',200);
INSERT  IGNORE INTO `fsm_errors_log` VALUES (44,'2026-03-23 09:25:59','MISSING_METADATA','order',1534,'request_locker_access_code',200);
INSERT  IGNORE INTO `fsm_errors_log` VALUES (45,'2026-03-23 09:27:24','FSM order_confirm_parcel_in failed: 1644 (45000): Invalid transition for order: no matching fsm_transitions','order',1527,'close_cell',1001);
INSERT  IGNORE INTO `fsm_errors_log` VALUES (46,'2026-03-23 09:40:25','INVALID_LEG_IN_METADATA','order',1528,'open_cell',1001);
INSERT  IGNORE INTO `fsm_errors_log` VALUES (47,'2026-03-23 09:47:00','COMPLETE_LOADING_FAILED: FSM driver_reservation_complete_loading failed: 1644 (45000): Invalid transition for driver_reservations: no matching fsm_transitions','direction',1,'direction_complete_loading',200);
INSERT  IGNORE INTO `fsm_errors_log` VALUES (48,'2026-03-23 15:33:51','COMPLETE_LOADING_FAILED: name \'has_open_cells\' is not defined ','direction',1,'direction_complete_loading',200);
INSERT  IGNORE INTO `fsm_errors_log` VALUES (49,'2026-03-23 15:40:26','COMPLETE_LOADING_FAILED: name \'has_open_cells\' is not defined ','direction',1,'direction_complete_loading',200);
INSERT  IGNORE INTO `fsm_errors_log` VALUES (50,'2026-03-23 15:47:57','INVALID_LEG_IN_METADATA','order',1528,'open_cell',200);
INSERT  IGNORE INTO `fsm_errors_log` VALUES (51,'2026-03-23 15:49:02','INVALID_LEG_IN_METADATA','order',1528,'open_cell',200);
INSERT  IGNORE INTO `fsm_errors_log` VALUES (52,'2026-03-23 15:50:22','INVALID_LEG_IN_METADATA','order',1528,'open_cell',200);
INSERT  IGNORE INTO `fsm_errors_log` VALUES (53,'2026-03-23 15:52:23','ROLE_NOT_SUPPORTED_driver','order',1528,'open_cell',200);
INSERT  IGNORE INTO `fsm_errors_log` VALUES (54,'2026-03-23 17:19:46','UNKNOWN_PROCESS: order_start_transit','order',1528,'order_start_transit',200);
INSERT  IGNORE INTO `fsm_errors_log` VALUES (55,'2026-03-23 17:58:01','INVALID_LEG_IN_METADATA','order',1534,'open_cell',200);
INSERT  IGNORE INTO `fsm_errors_log` VALUES (56,'2026-03-24 08:36:08','CANNOT_CANCEL_FROM_trip_in_progress','trip',43,'cancel_trip',200);
INSERT  IGNORE INTO `fsm_errors_log` VALUES (57,'2026-03-24 13:46:00','START_LOADING_FAILED: FSM driver_reservation_start_loading failed: 1644 (45000): Invalid transition for driver_reservations: no matching fsm_transitions','driver_reservations',23,'driver_reservation_start_loading',200);
INSERT  IGNORE INTO `fsm_errors_log` VALUES (58,'2026-03-24 13:46:05','UNSUPPORTED_ENTITY_TYPE','locker',1534,'request_locker_access_code',200);
INSERT  IGNORE INTO `fsm_errors_log` VALUES (59,'2026-03-24 13:46:25','UNSUPPORTED_ENTITY_TYPE','locker',1534,'request_locker_access_code',200);
INSERT  IGNORE INTO `fsm_errors_log` VALUES (60,'2026-03-24 13:47:30','UNSUPPORTED_ENTITY_TYPE','locker',1534,'request_locker_access_code',200);
INSERT  IGNORE INTO `fsm_errors_log` VALUES (61,'2026-03-24 13:49:25','CELL_NOT_LINKED_TO_ORDER','locker',1534,'open_cell',200);
INSERT  IGNORE INTO `fsm_errors_log` VALUES (62,'2026-03-24 13:49:40','UNSUPPORTED_ENTITY_TYPE','locker',1534,'request_locker_access_code',200);
INSERT  IGNORE INTO `fsm_errors_log` VALUES (63,'2026-03-24 14:25:57','CODE_NOT_ALLOWED_IN_order_in_transit_to_post2','order',1528,'request_locker_access_code',1001);
INSERT  IGNORE INTO `fsm_errors_log` VALUES (64,'2026-03-24 14:26:22','CODE_NOT_ALLOWED_IN_order_in_transit_to_post2','order',1528,'request_locker_access_code',1001);
INSERT  IGNORE INTO `fsm_errors_log` VALUES (65,'2026-03-24 14:33:02','CELL_NOT_LINKED_TO_ORDER','locker',1534,'open_cell',200);
INSERT  IGNORE INTO `fsm_errors_log` VALUES (66,'2026-03-24 14:33:12','FSM locker_close_locker failed: 1644 (45000): Unknown from_state for locker in fsm_states','locker',1534,'close_cell',200);
INSERT  IGNORE INTO `fsm_errors_log` VALUES (67,'2026-03-24 14:33:32','NO_ORDERS_PICKED: Невозможно создать рейс с 0 заказов','direction',2,'direction_complete_loading',200);
INSERT  IGNORE INTO `fsm_errors_log` VALUES (68,'2026-03-24 14:33:57','NO_ORDERS_PICKED: Невозможно создать рейс с 0 заказов','direction',2,'direction_complete_loading',200);
INSERT  IGNORE INTO `fsm_errors_log` VALUES (69,'2026-03-24 14:34:12','CELL_NOT_LINKED_TO_ORDER','locker',1534,'open_cell',200);
INSERT  IGNORE INTO `fsm_errors_log` VALUES (70,'2026-03-24 14:34:12','FSM locker_close_locker failed: 1644 (45000): Unknown from_state for locker in fsm_states','locker',1534,'close_cell',200);
INSERT  IGNORE INTO `fsm_errors_log` VALUES (71,'2026-03-24 14:34:17','FSM locker_close_locker failed: 1644 (45000): Unknown from_state for locker in fsm_states','locker',1534,'close_cell',200);
INSERT  IGNORE INTO `fsm_errors_log` VALUES (72,'2026-03-24 14:34:23','NO_ORDERS_PICKED: Невозможно создать рейс с 0 заказов','direction',2,'direction_complete_loading',200);
INSERT  IGNORE INTO `fsm_errors_log` VALUES (73,'2026-03-24 15:03:39','Рейс 305 не найден','locker',305,'complete_trip',200);
INSERT  IGNORE INTO `fsm_errors_log` VALUES (74,'2026-03-24 16:13:57','START_LOADING_FAILED: FSM driver_reservation_start_loading failed: 1644 (45000): Invalid transition for driver_reservations: no matching fsm_transitions','driver_reservations',23,'driver_reservation_start_loading',200);
INSERT  IGNORE INTO `fsm_errors_log` VALUES (75,'2026-03-24 16:15:52','CELL_NOT_LINKED_TO_ORDER','locker',1534,'open_cell',200);
INSERT  IGNORE INTO `fsm_errors_log` VALUES (76,'2026-03-24 16:15:57','CELL_NOT_LINKED_TO_ORDER','locker',1534,'open_cell',200);
INSERT  IGNORE INTO `fsm_errors_log` VALUES (77,'2026-03-24 16:16:02','FSM locker_close_locker failed: 1644 (45000): Unknown from_state for locker in fsm_states','locker',1534,'close_cell',200);
INSERT  IGNORE INTO `fsm_errors_log` VALUES (78,'2026-03-24 16:16:32','START_LOADING_FAILED: FSM driver_reservation_start_loading failed: 1644 (45000): Invalid transition for driver_reservations: no matching fsm_transitions','driver_reservations',23,'driver_reservation_start_loading',200);
INSERT  IGNORE INTO `fsm_errors_log` VALUES (79,'2026-03-24 16:16:47','CELL_NOT_LINKED_TO_ORDER','locker',1534,'open_cell',200);
INSERT  IGNORE INTO `fsm_errors_log` VALUES (80,'2026-03-24 16:16:52','FSM locker_close_locker failed: 1644 (45000): Unknown from_state for locker in fsm_states','locker',1534,'close_cell',200);
INSERT  IGNORE INTO `fsm_errors_log` VALUES (81,'2026-03-24 16:16:57','NO_ORDERS_PICKED: Невозможно создать рейс с 0 заказов','direction',2,'direction_complete_loading',200);
INSERT  IGNORE INTO `fsm_errors_log` VALUES (82,'2026-03-24 16:21:38','NO_ORDERS_PICKED: Невозможно создать рейс с 0 заказов','direction',2,'direction_complete_loading',200);
INSERT  IGNORE INTO `fsm_errors_log` VALUES (83,'2026-03-24 16:25:43','NO_ORDERS_PICKED: Невозможно создать рейс с 0 заказов','direction',2,'direction_complete_loading',200);
INSERT  IGNORE INTO `fsm_errors_log` VALUES (84,'2026-03-24 16:25:53','TOO_MANY_CODE_REQUESTS','order',1534,'request_locker_access_code',200);
INSERT  IGNORE INTO `fsm_errors_log` VALUES (85,'2026-03-24 16:25:58','CELL_NOT_LINKED_TO_ORDER','locker',1534,'open_cell',200);
INSERT  IGNORE INTO `fsm_errors_log` VALUES (86,'2026-03-24 16:26:03','FSM locker_close_locker failed: 1644 (45000): Unknown from_state for locker in fsm_states','locker',1534,'close_cell',200);
INSERT  IGNORE INTO `fsm_errors_log` VALUES (87,'2026-03-24 16:26:08','NO_ORDERS_PICKED: Невозможно создать рейс с 0 заказов','direction',2,'direction_complete_loading',200);
INSERT  IGNORE INTO `fsm_errors_log` VALUES (88,'2026-03-24 16:26:13','NO_AVAILABLE_ORDERS','direction',1,'direction_reserve_slot',200);
INSERT  IGNORE INTO `fsm_errors_log` VALUES (89,'2026-03-24 16:34:03','CELL_NOT_LINKED_TO_ORDER','locker',1534,'open_cell',200);
INSERT  IGNORE INTO `fsm_errors_log` VALUES (90,'2026-03-24 16:34:03','FSM locker_close_locker failed: 1644 (45000): Unknown from_state for locker in fsm_states','locker',1534,'close_cell',200);
INSERT  IGNORE INTO `fsm_errors_log` VALUES (91,'2026-03-24 16:34:08','START_LOADING_FAILED: FSM driver_reservation_start_loading failed: 1644 (45000): Invalid transition for driver_reservations: no matching fsm_transitions','driver_reservations',23,'driver_reservation_start_loading',200);
INSERT  IGNORE INTO `fsm_errors_log` VALUES (92,'2026-03-24 16:36:14','START_LOADING_FAILED: FSM driver_reservation_start_loading failed: 1644 (45000): Invalid transition for driver_reservations: no matching fsm_transitions','driver_reservations',23,'driver_reservation_start_loading',200);
INSERT  IGNORE INTO `fsm_errors_log` VALUES (93,'2026-03-24 16:40:39','CELL_NOT_LINKED_TO_ORDER','locker',1534,'open_cell',200);
INSERT  IGNORE INTO `fsm_errors_log` VALUES (94,'2026-03-24 16:40:44','FSM locker_close_locker failed: 1644 (45000): Unknown from_state for locker in fsm_states','locker',1534,'close_cell',200);
INSERT  IGNORE INTO `fsm_errors_log` VALUES (95,'2026-03-24 16:40:44','NO_ORDERS_PICKED: Невозможно создать рейс с 0 заказов','direction',2,'direction_complete_loading',200);
INSERT  IGNORE INTO `fsm_errors_log` VALUES (96,'2026-03-24 16:41:09','TOO_MANY_CODE_REQUESTS','order',1534,'request_locker_access_code',200);
INSERT  IGNORE INTO `fsm_errors_log` VALUES (97,'2026-03-24 16:41:19','NO_AVAILABLE_ORDERS','direction',1,'direction_reserve_slot',200);
INSERT  IGNORE INTO `fsm_errors_log` VALUES (98,'2026-03-24 16:41:49','NO_AVAILABLE_ORDERS','direction',1,'direction_reserve_slot',200);
INSERT  IGNORE INTO `fsm_errors_log` VALUES (99,'2026-03-24 16:42:09','NO_AVAILABLE_ORDERS','direction',1,'direction_reserve_slot',200);
INSERT  IGNORE INTO `fsm_errors_log` VALUES (100,'2026-03-24 16:42:14','NO_AVAILABLE_ORDERS','direction',1,'direction_reserve_slot',200);
INSERT  IGNORE INTO `fsm_errors_log` VALUES (101,'2026-03-24 16:42:39','TOO_MANY_CODE_REQUESTS','order',1534,'request_locker_access_code',200);
INSERT  IGNORE INTO `fsm_errors_log` VALUES (102,'2026-03-24 16:42:44','CELL_NOT_LINKED_TO_ORDER','locker',1534,'open_cell',200);
INSERT  IGNORE INTO `fsm_errors_log` VALUES (103,'2026-03-24 16:42:49','FSM locker_close_locker failed: 1644 (45000): Unknown from_state for locker in fsm_states','locker',1534,'close_cell',200);
INSERT  IGNORE INTO `fsm_errors_log` VALUES (104,'2026-03-24 16:42:54','NO_ORDERS_PICKED: Невозможно создать рейс с 0 заказов','direction',2,'direction_complete_loading',200);
INSERT  IGNORE INTO `fsm_errors_log` VALUES (105,'2026-03-24 16:42:59','NO_ORDERS_PICKED: Невозможно создать рейс с 0 заказов','direction',2,'direction_complete_loading',200);
INSERT  IGNORE INTO `fsm_errors_log` VALUES (106,'2026-03-24 16:43:09','CELL_NOT_LINKED_TO_ORDER','locker',1534,'open_cell',200);
INSERT  IGNORE INTO `fsm_errors_log` VALUES (107,'2026-03-24 16:43:14','FSM locker_close_locker failed: 1644 (45000): Unknown from_state for locker in fsm_states','locker',1534,'close_cell',200);
INSERT  IGNORE INTO `fsm_errors_log` VALUES (108,'2026-03-24 16:43:14','NO_ORDERS_PICKED: Невозможно создать рейс с 0 заказов','direction',2,'direction_complete_loading',200);
INSERT  IGNORE INTO `fsm_errors_log` VALUES (109,'2026-03-24 16:43:29','NO_ORDERS_PICKED: Невозможно создать рейс с 0 заказов','direction',2,'direction_complete_loading',200);
INSERT  IGNORE INTO `fsm_errors_log` VALUES (110,'2026-03-24 16:43:34','CELL_NOT_LINKED_TO_ORDER','locker',1534,'open_cell',200);
INSERT  IGNORE INTO `fsm_errors_log` VALUES (111,'2026-03-24 16:43:34','START_LOADING_FAILED: FSM driver_reservation_start_loading failed: 1644 (45000): Invalid transition for driver_reservations: no matching fsm_transitions','driver_reservations',24,'driver_reservation_start_loading',200);
INSERT  IGNORE INTO `fsm_errors_log` VALUES (112,'2026-03-24 16:43:39','CELL_NOT_LINKED_TO_ORDER','locker',1534,'open_cell',200);
INSERT  IGNORE INTO `fsm_errors_log` VALUES (113,'2026-03-24 16:43:39','FSM locker_close_locker failed: 1644 (45000): Unknown from_state for locker in fsm_states','locker',1534,'close_cell',200);
INSERT  IGNORE INTO `fsm_errors_log` VALUES (114,'2026-03-24 16:43:44','NO_ORDERS_PICKED: Невозможно создать рейс с 0 заказов','direction',2,'direction_complete_loading',200);
INSERT  IGNORE INTO `fsm_errors_log` VALUES (115,'2026-03-24 18:31:59','NO_ORDERS_PICKED: Невозможно создать рейс с 0 заказов','direction',2,'direction_complete_loading',200);
INSERT  IGNORE INTO `fsm_errors_log` VALUES (116,'2026-03-24 18:37:35','START_LOADING_FAILED: FSM driver_reservation_start_loading failed: 1644 (45000): Invalid transition for driver_reservations: no matching fsm_transitions','driver_reservations',24,'driver_reservation_start_loading',200);
INSERT  IGNORE INTO `fsm_errors_log` VALUES (117,'2026-03-24 18:37:50','CELL_NOT_LINKED_TO_ORDER','locker',1534,'open_cell',200);
INSERT  IGNORE INTO `fsm_errors_log` VALUES (118,'2026-03-24 18:38:15','FSM locker_close_locker failed: 1644 (45000): Unknown from_state for locker in fsm_states','locker',1534,'close_cell',200);
INSERT  IGNORE INTO `fsm_errors_log` VALUES (119,'2026-03-24 18:38:30','NO_ORDERS_PICKED: Невозможно создать рейс с 0 заказов','direction',2,'direction_complete_loading',200);
INSERT  IGNORE INTO `fsm_errors_log` VALUES (120,'2026-03-25 02:38:02','START_LOADING_FAILED: FSM driver_reservation_start_loading failed: 1644 (45000): Invalid transition for driver_reservations: no matching fsm_transitions','driver_reservations',24,'driver_reservation_start_loading',200);
INSERT  IGNORE INTO `fsm_errors_log` VALUES (121,'2026-03-25 02:38:17','CELL_NOT_LINKED_TO_ORDER','locker',1534,'open_cell',200);
INSERT  IGNORE INTO `fsm_errors_log` VALUES (122,'2026-03-25 02:38:27','FSM locker_close_locker failed: 1644 (45000): Unknown from_state for locker in fsm_states','locker',1534,'close_cell',200);
INSERT  IGNORE INTO `fsm_errors_log` VALUES (123,'2026-03-25 02:38:42','NO_ORDERS_PICKED: Невозможно создать рейс с 0 заказов','direction',2,'direction_complete_loading',200);
INSERT  IGNORE INTO `fsm_errors_log` VALUES (124,'2026-03-25 06:42:01','START_LOADING_FAILED: FSM driver_reservation_start_loading failed: 1644 (45000): Invalid transition for driver_reservations: no matching fsm_transitions','driver_reservations',24,'driver_reservation_start_loading',200);
INSERT  IGNORE INTO `fsm_errors_log` VALUES (125,'2026-03-25 06:42:17','START_LOADING_FAILED: FSM driver_reservation_start_loading failed: 1644 (45000): Invalid transition for driver_reservations: no matching fsm_transitions','driver_reservations',24,'driver_reservation_start_loading',200);
INSERT  IGNORE INTO `fsm_errors_log` VALUES (126,'2026-03-25 06:44:27','CELL_NOT_LINKED_TO_ORDER','locker',1534,'open_cell',200);
INSERT  IGNORE INTO `fsm_errors_log` VALUES (127,'2026-03-25 10:06:56','FSM locker_close_locker failed: 1644 (45000): Unknown from_state for locker in fsm_states','locker',1534,'close_cell',200);
INSERT  IGNORE INTO `fsm_errors_log` VALUES (128,'2026-03-25 10:06:56','START_LOADING_FAILED: FSM driver_reservation_start_loading failed: 1644 (45000): Invalid transition for driver_reservations: no matching fsm_transitions','driver_reservations',24,'driver_reservation_start_loading',200);
INSERT  IGNORE INTO `fsm_errors_log` VALUES (129,'2026-03-25 10:12:06','START_LOADING_FAILED: FSM driver_reservation_start_loading failed: 1644 (45000): Invalid transition for driver_reservations: no matching fsm_transitions','driver_reservations',24,'driver_reservation_start_loading',200);
INSERT  IGNORE INTO `fsm_errors_log` VALUES (130,'2026-03-25 10:12:27','START_LOADING_FAILED: FSM driver_reservation_start_loading failed: 1644 (45000): Invalid transition for driver_reservations: no matching fsm_transitions','driver_reservations',24,'driver_reservation_start_loading',200);
INSERT  IGNORE INTO `fsm_errors_log` VALUES (131,'2026-03-25 10:15:57','NO_AVAILABLE_ORDERS','direction',1,'direction_reserve_slot',200);
INSERT  IGNORE INTO `fsm_errors_log` VALUES (132,'2026-03-25 10:18:07','NO_AVAILABLE_ORDERS','direction',1,'direction_reserve_slot',200);
INSERT  IGNORE INTO `fsm_errors_log` VALUES (133,'2026-03-25 10:18:47','NO_AVAILABLE_ORDERS','direction',1,'direction_reserve_slot',200);
INSERT  IGNORE INTO `fsm_errors_log` VALUES (134,'2026-03-25 10:21:27','NO_AVAILABLE_ORDERS','direction',1,'direction_reserve_slot',200);
INSERT  IGNORE INTO `fsm_errors_log` VALUES (135,'2026-03-25 10:24:02','NO_AVAILABLE_ORDERS','direction',1,'direction_reserve_slot',200);
INSERT  IGNORE INTO `fsm_errors_log` VALUES (136,'2026-03-25 10:35:43','NO_AVAILABLE_ORDERS','direction',1,'direction_reserve_slot',200);
INSERT  IGNORE INTO `fsm_errors_log` VALUES (137,'2026-03-25 10:37:53','NO_AVAILABLE_ORDERS','direction',1,'direction_reserve_slot',200);
INSERT  IGNORE INTO `fsm_errors_log` VALUES (138,'2026-03-25 10:48:43','NO_AVAILABLE_ORDERS','direction',1,'direction_reserve_slot',200);
INSERT  IGNORE INTO `fsm_errors_log` VALUES (139,'2026-03-25 10:49:28','NO_AVAILABLE_ORDERS','direction',1,'direction_reserve_slot',200);
INSERT  IGNORE INTO `fsm_errors_log` VALUES (140,'2026-03-25 11:05:24','NO_AVAILABLE_ORDERS','direction',1,'direction_reserve_slot',200);
INSERT  IGNORE INTO `fsm_errors_log` VALUES (141,'2026-03-25 11:32:10','CODE_NOT_ALLOWED_IN_order_courier1_assigned','order',1531,'request_locker_access_code',100);
INSERT  IGNORE INTO `fsm_errors_log` VALUES (142,'2026-03-25 11:32:35','CODE_NOT_ALLOWED_IN_order_in_transit_to_post2','order',1528,'request_locker_access_code',1001);
INSERT  IGNORE INTO `fsm_errors_log` VALUES (143,'2026-03-25 11:32:50','CODE_NOT_ALLOWED_IN_order_courier1_assigned','order',1531,'request_locker_access_code',100);
INSERT  IGNORE INTO `fsm_errors_log` VALUES (144,'2026-03-25 11:33:20','CODE_NOT_ALLOWED_IN_order_created','order',1514,'request_locker_access_code',100);
INSERT  IGNORE INTO `fsm_errors_log` VALUES (145,'2026-03-25 11:33:30','CODE_NOT_ALLOWED_IN_order_courier1_assigned','order',1508,'request_locker_access_code',100);
INSERT  IGNORE INTO `fsm_errors_log` VALUES (146,'2026-03-25 11:38:16','CODE_NOT_ALLOWED_IN_order_courier1_assigned','order',1507,'request_locker_access_code',100);
INSERT  IGNORE INTO `fsm_errors_log` VALUES (147,'2026-03-25 11:41:01','\'dict\' object has no attribute \'courier_user_id\'','order',1514,'request_locker_access_code',100);
INSERT  IGNORE INTO `fsm_errors_log` VALUES (148,'2026-03-25 11:41:11','CODE_NOT_ALLOWED_IN_order_courier1_assigned','order',1508,'request_locker_access_code',100);
INSERT  IGNORE INTO `fsm_errors_log` VALUES (149,'2026-03-25 11:44:11','CODE_NOT_ALLOWED_IN_order_courier1_assigned','order',1506,'request_locker_access_code',100);
INSERT  IGNORE INTO `fsm_errors_log` VALUES (150,'2026-03-25 11:52:42','\'dict\' object has no attribute \'courier_user_id\'','order',1508,'request_locker_access_code',100);
INSERT  IGNORE INTO `fsm_errors_log` VALUES (151,'2026-03-25 12:54:15','CODE_NOT_ALLOWED_IN_order_courier1_assigned','order',1506,'request_locker_access_code',100);
INSERT  IGNORE INTO `fsm_errors_log` VALUES (152,'2026-03-25 12:55:15','CODE_NOT_ALLOWED_IN_order_courier1_assigned','order',1506,'request_locker_access_code',100);
INSERT  IGNORE INTO `fsm_errors_log` VALUES (153,'2026-03-25 13:00:20','INVALID_LEG_IN_METADATA','order',1508,'open_cell',100);
INSERT  IGNORE INTO `fsm_errors_log` VALUES (154,'2026-03-25 13:00:20','FSM order_confirm_parcel_in failed: 1644 (45000): Invalid transition for order: no matching fsm_transitions','order',1508,'close_cell',100);
INSERT  IGNORE INTO `fsm_errors_log` VALUES (155,'2026-03-25 13:03:10','CODE_NOT_ALLOWED_IN_order_courier1_assigned','order',1531,'request_locker_access_code',100);
INSERT  IGNORE INTO `fsm_errors_log` VALUES (156,'2026-03-25 13:06:00','INVALID_LEG_IN_METADATA','order',1508,'open_cell',100);
INSERT  IGNORE INTO `fsm_errors_log` VALUES (157,'2026-03-25 13:06:05','FSM order_confirm_parcel_in failed: 1644 (45000): Invalid transition for order: no matching fsm_transitions','order',1508,'close_cell',100);
INSERT  IGNORE INTO `fsm_errors_log` VALUES (158,'2026-03-25 13:08:40','INVALID_LEG_IN_METADATA','order',1508,'open_cell',100);
INSERT  IGNORE INTO `fsm_errors_log` VALUES (159,'2026-03-25 13:08:45','FSM order_confirm_parcel_in failed: 1644 (45000): Invalid transition for order: no matching fsm_transitions','order',1508,'close_cell',100);
INSERT  IGNORE INTO `fsm_errors_log` VALUES (160,'2026-03-25 14:38:01','ASSIGNMENT_FAILED','trip',16,'trip_assign_driver',777);
INSERT  IGNORE INTO `fsm_errors_log` VALUES (161,'2026-03-25 14:46:16','ASSIGNMENT_FAILED','trip',1,'trip_assign_driver',777);
INSERT  IGNORE INTO `fsm_errors_log` VALUES (162,'2026-03-25 14:54:17','ASSIGNMENT_FAILED','trip',29,'trip_assign_driver',777);
INSERT  IGNORE INTO `fsm_errors_log` VALUES (163,'2026-03-26 13:40:21','ASSIGNMENT_FAILED','trip',34,'trip_assign_driver',777);
INSERT  IGNORE INTO `fsm_errors_log` VALUES (164,'2026-03-27 11:13:28','ASSIGNMENT_FAILED','trip',1,'trip_assign_driver',777);
INSERT  IGNORE INTO `fsm_errors_log` VALUES (165,'2026-03-27 11:19:14','REMOVE_EXECUTOR_FAILED','trip',29,'trip_remove_driver',777);
INSERT  IGNORE INTO `fsm_errors_log` VALUES (166,'2026-03-27 12:46:25','ASSIGNMENT_FAILED','trip',1,'trip_assign_driver',777);
INSERT  IGNORE INTO `fsm_errors_log` VALUES (167,'2026-03-28 05:38:43','USER_NOT_AUTHORIZED','order',5,'request_locker_access_code',777);
INSERT  IGNORE INTO `fsm_errors_log` VALUES (168,'2026-03-28 05:39:18','FSM locker_close_locker failed: 1644 (45000): Invalid transition for locker: no matching fsm_transitions','order',5,'close_cell',777);
INSERT  IGNORE INTO `fsm_errors_log` VALUES (169,'2026-03-28 05:41:48','USER_NOT_AUTHORIZED','order',5,'request_locker_access_code',777);
INSERT  IGNORE INTO `fsm_errors_log` VALUES (170,'2026-03-28 06:11:54','CODE_NOT_ALLOWED_IN_order_in_transit_to_post2','order',1528,'request_locker_access_code',1001);
INSERT  IGNORE INTO `fsm_errors_log` VALUES (171,'2026-03-28 06:18:30','MISSING_METADATA','order',1528,'request_locker_access_code',1001);
INSERT  IGNORE INTO `fsm_errors_log` VALUES (172,'2026-03-28 06:26:00','ORDER_NOT_FOUND','order',30,'request_locker_access_code',777);
INSERT  IGNORE INTO `fsm_errors_log` VALUES (173,'2026-03-28 06:26:10','ORDER_NOT_FOUND','order',30,'request_locker_access_code',777);
INSERT  IGNORE INTO `fsm_errors_log` VALUES (174,'2026-03-28 06:27:15','INVALID_LEG','order',5,'request_locker_access_code',777);
INSERT  IGNORE INTO `fsm_errors_log` VALUES (175,'2026-03-28 06:31:10','USER_NOT_AUTHORIZED','order',5,'request_locker_access_code',777);
INSERT  IGNORE INTO `fsm_errors_log` VALUES (176,'2026-03-28 06:34:36','USER_NOT_AUTHORIZED','order',5,'request_locker_access_code',777);
INSERT  IGNORE INTO `fsm_errors_log` VALUES (177,'2026-03-28 06:35:11','ORDER_NOT_FOUND','order',30,'request_locker_access_code',777);
INSERT  IGNORE INTO `fsm_errors_log` VALUES (178,'2026-03-28 06:35:46','USER_NOT_AUTHORIZED','order',5,'request_locker_access_code',777);
INSERT  IGNORE INTO `fsm_errors_log` VALUES (179,'2026-03-28 06:35:56','USER_NOT_AUTHORIZED','order',5,'request_locker_access_code',777);
INSERT  IGNORE INTO `fsm_errors_log` VALUES (180,'2026-03-28 06:45:26','USER_NOT_AUTHORIZED','order',5,'request_locker_access_code',777);
INSERT  IGNORE INTO `fsm_errors_log` VALUES (181,'2026-03-30 13:54:00','CODE_NOT_ALLOWED_IN_order_courier1_assigned','order',1536,'request_locker_access_code',100);
INSERT  IGNORE INTO `fsm_errors_log` VALUES (182,'2026-03-30 14:00:10','INVALID_LEG_IN_METADATA','order',1536,'open_cell',100);
INSERT  IGNORE INTO `fsm_errors_log` VALUES (183,'2026-03-30 16:16:50','UNKNOWN_PROCESS: order_start_transit','order',1536,'order_start_transit',200);
INSERT  IGNORE INTO `fsm_errors_log` VALUES (184,'2026-03-30 16:24:55','CODE_NOT_ALLOWED_IN_order_in_transit_to_post2','order',1536,'request_locker_access_code',200);
INSERT  IGNORE INTO `fsm_errors_log` VALUES (185,'2026-03-30 16:30:36','USER_NOT_AUTHORIZED','order',1536,'request_locker_access_code',200);
INSERT  IGNORE INTO `fsm_errors_log` VALUES (186,'2026-03-30 17:18:24','INVALID_ACCESS_CODE: ACCESS_CODE_INVALID','order',1536,'open_cell',103);
INSERT  IGNORE INTO `fsm_errors_log` VALUES (187,'2026-03-31 08:55:34','CODE_NOT_ALLOWED_IN_order_cancelled','order',1537,'request_locker_access_code',1004);
INSERT  IGNORE INTO `fsm_errors_log` VALUES (188,'2026-04-01 02:46:11','USER_NOT_AUTHORIZED','order',1536,'request_locker_access_code',100);
INSERT  IGNORE INTO `fsm_errors_log` VALUES (189,'2026-04-01 02:46:16','CODE_NOT_ALLOWED_IN_order_courier1_assigned','order',1531,'request_locker_access_code',100);
INSERT  IGNORE INTO `fsm_errors_log` VALUES (190,'2026-04-01 02:56:06','USER_NOT_AUTHORIZED','order',1536,'request_locker_access_code',100);
INSERT  IGNORE INTO `fsm_errors_log` VALUES (191,'2026-04-01 02:56:51','CODE_NOT_ALLOWED_IN_order_courier1_assigned','order',1531,'request_locker_access_code',100);
INSERT  IGNORE INTO `fsm_errors_log` VALUES (192,'2026-04-01 03:06:27','USER_NOT_AUTHORIZED','order',1536,'request_locker_access_code',100);
INSERT  IGNORE INTO `fsm_errors_log` VALUES (193,'2026-04-01 03:06:42','CODE_NOT_ALLOWED_IN_order_completed','order',1525,'request_locker_access_code',100);
INSERT  IGNORE INTO `fsm_errors_log` VALUES (194,'2026-04-01 03:26:28','INVALID_LEG_IN_METADATA','order',1363,'open_cell',100);
INSERT  IGNORE INTO `fsm_errors_log` VALUES (195,'2026-04-01 03:26:33','FSM order_confirm_parcel_in failed: 1644 (45000): Invalid transition for order: no matching fsm_transitions','order',1363,'close_cell',100);
INSERT  IGNORE INTO `fsm_errors_log` VALUES (196,'2026-04-01 03:26:43','FSM order_confirm_parcel_in failed: 1644 (45000): Invalid transition for order: no matching fsm_transitions','order',1363,'close_cell',100);
INSERT  IGNORE INTO `fsm_errors_log` VALUES (197,'2026-04-01 06:52:08','CODE_NOT_ALLOWED_IN_order_courier1_assigned','order',1363,'request_locker_access_code',100);
INSERT  IGNORE INTO `fsm_errors_log` VALUES (198,'2026-04-01 06:54:59','CODE_NOT_ALLOWED_IN_order_courier1_assigned','order',1363,'request_locker_access_code',100);
INSERT  IGNORE INTO `fsm_errors_log` VALUES (199,'2026-04-01 08:51:31','INVALID_LEG_IN_METADATA','order',1502,'open_cell',100);
INSERT  IGNORE INTO `fsm_errors_log` VALUES (200,'2026-04-01 08:52:22','FSM order_confirm_parcel_in failed: 1644 (45000): Invalid transition for order: no matching fsm_transitions','order',1502,'close_cell',100);
INSERT  IGNORE INTO `fsm_errors_log` VALUES (201,'2026-04-01 08:58:52','INVALID_LEG_IN_METADATA','order',1531,'open_cell',100);
INSERT  IGNORE INTO `fsm_errors_log` VALUES (202,'2026-04-01 08:59:12','FSM order_confirm_parcel_in failed: 1644 (45000): Invalid transition for order: no matching fsm_transitions','order',1531,'close_cell',100);
INSERT  IGNORE INTO `fsm_errors_log` VALUES (203,'2026-04-01 09:39:05','NO_FREE_CELLS','order_request',275,'order_creation',NULL);
INSERT  IGNORE INTO `fsm_errors_log` VALUES (204,'2026-04-01 09:54:17','Неизвестный статус курьера: order_parcel_confirmed','order',1531,'open_cell',100);
INSERT  IGNORE INTO `fsm_errors_log` VALUES (205,'2026-04-01 09:59:14','UNKNOWN_PROCESS: order_start_transit','order',1531,'order_start_transit',200);
INSERT  IGNORE INTO `fsm_errors_log` VALUES (206,'2026-04-01 10:02:44','USER_NOT_AUTHORIZED','order',10,'request_locker_access_code',200);
INSERT  IGNORE INTO `fsm_errors_log` VALUES (207,'2026-04-01 10:03:15','FSM order_confirm_parcel_in failed: 1644 (45000): Invalid transition for order: no matching fsm_transitions','order',1506,'close_cell',100);
INSERT  IGNORE INTO `fsm_errors_log` VALUES (208,'2026-04-01 10:04:20','Неизвестный статус курьера: order_courier2_parcel_delivered','order',1536,'close_cell',100);
INSERT  IGNORE INTO `fsm_errors_log` VALUES (209,'2026-04-01 10:13:15','USER_NOT_AUTHORIZED','order',1531,'request_locker_access_code',100);
INSERT  IGNORE INTO `fsm_errors_log` VALUES (210,'2026-04-01 10:13:56','FSM locker_open_locker failed: 1644 (45000): Invalid transition for locker: no matching fsm_transitions','order',1507,'open_cell',100);
INSERT  IGNORE INTO `fsm_errors_log` VALUES (211,'2026-04-01 10:14:06','FSM order_confirm_parcel_in failed: 1644 (45000): Invalid transition for order: no matching fsm_transitions','order',1507,'close_cell',100);
INSERT  IGNORE INTO `fsm_errors_log` VALUES (212,'2026-04-01 10:14:51','Неизвестный статус курьера: order_parcel_confirmed','order',1363,'open_cell',100);
INSERT  IGNORE INTO `fsm_errors_log` VALUES (213,'2026-04-01 10:14:56','Неизвестный статус курьера: order_parcel_confirmed','order',1363,'close_cell',100);
INSERT  IGNORE INTO `fsm_errors_log` VALUES (214,'2026-04-01 10:15:16','Неизвестный статус курьера: order_parcel_confirmed','order',1502,'open_cell',100);
INSERT  IGNORE INTO `fsm_errors_log` VALUES (215,'2026-04-01 10:15:21','Неизвестный статус курьера: order_parcel_confirmed','order',1502,'close_cell',100);
INSERT  IGNORE INTO `fsm_errors_log` VALUES (216,'2026-04-01 10:15:36','Неизвестный статус курьера: order_parcel_confirmed','order',1506,'open_cell',100);
INSERT  IGNORE INTO `fsm_errors_log` VALUES (217,'2026-04-01 10:15:41','Неизвестный статус курьера: order_parcel_confirmed','order',1506,'close_cell',100);
INSERT  IGNORE INTO `fsm_errors_log` VALUES (218,'2026-04-01 10:17:17','CODE_NOT_ALLOWED_IN_order_completed','order',1525,'request_locker_access_code',100);
INSERT  IGNORE INTO `fsm_errors_log` VALUES (219,'2026-04-01 10:18:07','Неизвестный статус курьера: order_parcel_confirmed','order',1363,'open_cell',100);
INSERT  IGNORE INTO `fsm_errors_log` VALUES (220,'2026-04-01 10:18:07','Неизвестный статус курьера: order_parcel_confirmed','order',1502,'open_cell',100);
INSERT  IGNORE INTO `fsm_errors_log` VALUES (221,'2026-04-01 10:18:12','Неизвестный статус курьера: order_parcel_confirmed','order',1508,'open_cell',100);
INSERT  IGNORE INTO `fsm_errors_log` VALUES (222,'2026-04-01 10:18:12','FSM locker_open_locker failed: 1644 (45000): Invalid transition for locker: no matching fsm_transitions','order',1507,'open_cell',100);
INSERT  IGNORE INTO `fsm_errors_log` VALUES (223,'2026-04-01 10:18:12','Неизвестный статус курьера: order_parcel_confirmed','order',1506,'open_cell',100);
INSERT  IGNORE INTO `fsm_errors_log` VALUES (224,'2026-04-01 10:18:17','Неизвестный статус курьера: order_created','order',1514,'open_cell',100);
INSERT  IGNORE INTO `fsm_errors_log` VALUES (225,'2026-04-01 10:18:27','Неизвестный статус курьера: order_parcel_confirmed','order',1363,'close_cell',100);
INSERT  IGNORE INTO `fsm_errors_log` VALUES (226,'2026-04-01 10:18:32','Неизвестный статус курьера: order_parcel_confirmed','order',1502,'close_cell',100);
INSERT  IGNORE INTO `fsm_errors_log` VALUES (227,'2026-04-01 10:18:32','Неизвестный статус курьера: order_parcel_confirmed','order',1506,'close_cell',100);
INSERT  IGNORE INTO `fsm_errors_log` VALUES (228,'2026-04-01 10:18:37','Неизвестный статус курьера: order_created','order',1514,'close_cell',100);
INSERT  IGNORE INTO `fsm_errors_log` VALUES (229,'2026-04-01 10:18:37','Неизвестный статус курьера: order_parcel_confirmed','order',1508,'close_cell',100);
INSERT  IGNORE INTO `fsm_errors_log` VALUES (230,'2026-04-01 10:18:37','FSM order_confirm_parcel_in failed: 1644 (45000): Invalid transition for order: no matching fsm_transitions','order',1507,'close_cell',100);
INSERT  IGNORE INTO `fsm_errors_log` VALUES (231,'2026-04-02 14:24:37','Неизвестный статус курьера: order_parcel_confirmed','order',1508,'open_cell',100);
INSERT  IGNORE INTO `fsm_errors_log` VALUES (232,'2026-04-02 14:25:17','Неизвестный статус курьера: order_parcel_confirmed','order',1508,'close_cell',100);
INSERT  IGNORE INTO `fsm_errors_log` VALUES (233,'2026-04-02 14:40:43','MISSING_METADATA','order',1531,'request_locker_access_code',100);
INSERT  IGNORE INTO `fsm_errors_log` VALUES (234,'2026-04-02 14:40:53','MISSING_METADATA','order',1531,'request_locker_access_code',100);
INSERT  IGNORE INTO `fsm_errors_log` VALUES (235,'2026-04-02 14:41:09','CODE_NOT_ALLOWED_IN_order_completed','order',1525,'request_locker_access_code',100);
INSERT  IGNORE INTO `fsm_errors_log` VALUES (236,'2026-04-02 14:41:39','MISSING_METADATA','order',1528,'request_locker_access_code',1001);
INSERT  IGNORE INTO `fsm_errors_log` VALUES (237,'2026-04-02 14:54:09','MISSING_METADATA','order',1528,'request_locker_access_code',1001);
INSERT  IGNORE INTO `fsm_errors_log` VALUES (238,'2026-04-02 14:54:50','MISSING_ORDER_ID_IN_METADATA','order',1536,'report_error',100);
INSERT  IGNORE INTO `fsm_errors_log` VALUES (239,'2026-04-02 15:17:26','MISSING_ORDER_ID_IN_METADATA','order',1528,'report_error',1001);
INSERT  IGNORE INTO `fsm_errors_log` VALUES (240,'2026-04-02 15:42:48','Неизвестный статус курьера: order_completed','order',1525,'close_cell',100);
INSERT  IGNORE INTO `fsm_errors_log` VALUES (241,'2026-04-02 17:30:40','USER_NOT_AUTHORIZED','order',1536,'request_locker_access_code',100);
INSERT  IGNORE INTO `fsm_errors_log` VALUES (242,'2026-04-02 17:37:16','Неизвестный статус курьера: order_courier2_parcel_delivered','order',1536,'open_cell',103);
INSERT  IGNORE INTO `fsm_errors_log` VALUES (243,'2026-04-02 17:37:21','Неизвестный статус курьера: order_courier2_parcel_delivered','order',1536,'close_cell',103);
INSERT  IGNORE INTO `fsm_errors_log` VALUES (244,'2026-04-02 17:37:21','INVALID_CODE: Код подтверждения не найден для этого заказа','order',1536,'confirm_courier2_delivery',103);
INSERT  IGNORE INTO `fsm_errors_log` VALUES (245,'2026-04-02 17:40:26','INVALID_CODE: Код подтверждения не найден для этого заказа','order',1536,'confirm_courier2_delivery',103);
INSERT  IGNORE INTO `fsm_errors_log` VALUES (246,'2026-04-02 17:41:01','CODE_NOT_ALLOWED_IN_order_courier2_parcel_delivered','order',1536,'request_locker_access_code',2001);
INSERT  IGNORE INTO `fsm_errors_log` VALUES (247,'2026-04-02 17:47:22','USER_NOT_AUTHORIZED','order',1536,'request_locker_access_code',2001);
INSERT  IGNORE INTO `fsm_errors_log` VALUES (248,'2026-04-02 18:06:53','USER_NOT_AUTHORIZED','order',1524,'request_locker_access_code',2002);
INSERT  IGNORE INTO `fsm_errors_log` VALUES (249,'2026-04-03 07:26:19','FSM order_confirm_parcel_in failed: 1644 (45000): Invalid transition for order: no matching fsm_transitions','order',1528,'close_cell',1001);
INSERT  IGNORE INTO `fsm_errors_log` VALUES (250,'2026-04-03 07:26:39','FSM order_confirm_parcel_in failed: 1644 (45000): Invalid transition for order: no matching fsm_transitions','order',1528,'close_cell',1001);
INSERT  IGNORE INTO `fsm_errors_log` VALUES (251,'2026-04-03 07:30:49','FSM order_confirm_parcel_in failed: 1644 (45000): Invalid transition for order: no matching fsm_transitions','order',1528,'close_cell',1001);
INSERT  IGNORE INTO `fsm_errors_log` VALUES (252,'2026-04-03 07:33:19','FSM order_confirm_parcel_in failed: 1644 (45000): Invalid transition for order: no matching fsm_transitions','order',1528,'close_cell',1001);
INSERT  IGNORE INTO `fsm_errors_log` VALUES (253,'2026-04-03 07:33:39','FSM order_confirm_parcel_in failed: 1644 (45000): Invalid transition for order: no matching fsm_transitions','order',1528,'close_cell',1001);
INSERT  IGNORE INTO `fsm_errors_log` VALUES (254,'2026-04-03 07:34:39','FSM order_confirm_parcel_in failed: 1644 (45000): Invalid transition for order: no matching fsm_transitions','order',1528,'close_cell',1001);
INSERT  IGNORE INTO `fsm_errors_log` VALUES (255,'2026-04-03 07:51:07','FSM order_confirm_parcel_in failed: 1644 (45000): Invalid transition for order: no matching fsm_transitions','order',1527,'close_cell',1001);
INSERT  IGNORE INTO `fsm_errors_log` VALUES (256,'2026-04-03 08:00:23','FSM order_confirm_parcel_in failed: 1644 (45000): Invalid transition for order: no matching fsm_transitions','order',1528,'close_cell',1001);
INSERT  IGNORE INTO `fsm_errors_log` VALUES (257,'2026-04-03 08:02:58','FSM order_confirm_parcel_in failed: 1644 (45000): Invalid transition for order: no matching fsm_transitions','order',1527,'close_cell',1001);
INSERT  IGNORE INTO `fsm_errors_log` VALUES (258,'2026-04-03 08:03:18','FSM order_confirm_parcel_in failed: 1644 (45000): Invalid transition for order: no matching fsm_transitions','order',1527,'close_cell',1001);
INSERT  IGNORE INTO `fsm_errors_log` VALUES (259,'2026-04-03 08:07:33','FSM order_confirm_parcel_in failed: 1644 (45000): Invalid transition for order: no matching fsm_transitions','order',1528,'close_cell',1001);
INSERT  IGNORE INTO `fsm_errors_log` VALUES (260,'2026-04-03 08:08:03','FSM order_confirm_parcel_in failed: 1644 (45000): Invalid transition for order: no matching fsm_transitions','order',1527,'close_cell',1001);
INSERT  IGNORE INTO `fsm_errors_log` VALUES (261,'2026-04-03 08:21:44','Неизвестный статус курьера: order_courier2_parcel_delivered','order',1536,'close_cell',100);
INSERT  IGNORE INTO `fsm_errors_log` VALUES (262,'2026-04-03 08:22:04','Неизвестный статус курьера: order_parcel_confirmed','order',1508,'close_cell',100);
INSERT  IGNORE INTO `fsm_errors_log` VALUES (263,'2026-04-03 08:22:19','FSM order_confirm_parcel_in failed: 1644 (45000): Invalid transition for order: no matching fsm_transitions','order',1507,'close_cell',100);
INSERT  IGNORE INTO `fsm_errors_log` VALUES (264,'2026-04-03 08:22:54','Неизвестный статус курьера: order_parcel_confirmed','order',1506,'close_cell',100);
INSERT  IGNORE INTO `fsm_errors_log` VALUES (265,'2026-04-03 08:25:34','FSM order_confirm_parcel_in failed: 1644 (45000): Invalid transition for order: no matching fsm_transitions','order',1527,'close_cell',1001);
INSERT  IGNORE INTO `fsm_errors_log` VALUES (266,'2026-04-03 08:27:50','FSM order_confirm_parcel_in failed: 1644 (45000): Invalid transition for order: no matching fsm_transitions','order',1528,'close_cell',1001);
INSERT  IGNORE INTO `fsm_errors_log` VALUES (267,'2026-04-04 14:50:02','Нет source_cell_id для заказа 13','order',13,'close_cell',777);
INSERT  IGNORE INTO `fsm_errors_log` VALUES (268,'2026-04-04 14:52:28','Нет source_cell_id для заказа 13','order',13,'close_cell',777);
INSERT  IGNORE INTO `fsm_errors_log` VALUES (269,'2026-04-04 14:53:03','Нет source_cell_id для заказа 13','order',13,'close_cell',777);
INSERT  IGNORE INTO `fsm_errors_log` VALUES (270,'2026-04-04 14:55:38','Нет source_cell_id для заказа 13','order',13,'close_cell',777);
INSERT  IGNORE INTO `fsm_errors_log` VALUES (271,'2026-04-04 15:13:09','FSM locker_close_locker failed: 1644 (45000): Invalid transition for locker: no matching fsm_transitions','order',1536,'close_cell',777);
INSERT  IGNORE INTO `fsm_errors_log` VALUES (272,'2026-04-04 15:13:29','FSM locker_close_locker failed: 1644 (45000): Invalid transition for locker: no matching fsm_transitions','order',1536,'close_cell',777);
INSERT  IGNORE INTO `fsm_errors_log` VALUES (273,'2026-04-04 15:14:04','FSM locker_close_locker failed: 1644 (45000): Invalid transition for locker: no matching fsm_transitions','order',5,'close_cell',777);
INSERT  IGNORE INTO `fsm_errors_log` VALUES (274,'2026-04-04 15:14:49','FSM locker_close_locker failed: 1644 (45000): Invalid transition for locker: no matching fsm_transitions','order',1536,'close_cell',777);
INSERT  IGNORE INTO `fsm_errors_log` VALUES (275,'2026-04-04 15:19:04','USER_NOT_AUTHORIZED','order',1531,'request_locker_access_code',100);
INSERT  IGNORE INTO `fsm_errors_log` VALUES (276,'2026-04-04 15:19:30','Неизвестный статус курьера: order_parcel_confirmed','order',1508,'open_cell',100);
INSERT  IGNORE INTO `fsm_errors_log` VALUES (277,'2026-04-04 15:19:50','Неизвестный статус курьера: order_parcel_confirmed','order',1508,'close_cell',100);
INSERT  IGNORE INTO `fsm_errors_log` VALUES (278,'2026-04-04 15:34:26','FSM locker_close_locker failed: 1644 (45000): Invalid transition for locker: no matching fsm_transitions','order',1536,'close_cell',777);
INSERT  IGNORE INTO `fsm_errors_log` VALUES (279,'2026-04-04 15:34:41','FSM locker_close_locker failed: 1644 (45000): Invalid transition for locker: no matching fsm_transitions','order',1536,'close_cell',777);
INSERT  IGNORE INTO `fsm_errors_log` VALUES (280,'2026-04-04 15:41:31','FSM locker_close_locker failed: 1644 (45000): Invalid transition for locker: no matching fsm_transitions','order',1536,'close_cell',777);
INSERT  IGNORE INTO `fsm_errors_log` VALUES (281,'2026-04-04 15:45:07','FSM locker_close_locker failed: 1644 (45000): Invalid transition for locker: no matching fsm_transitions','order',1536,'close_cell',777);
INSERT  IGNORE INTO `fsm_errors_log` VALUES (282,'2026-04-04 15:45:22','FSM locker_close_locker failed: 1644 (45000): Invalid transition for locker: no matching fsm_transitions','order',5,'close_cell',777);
INSERT  IGNORE INTO `fsm_errors_log` VALUES (283,'2026-04-04 15:45:32','FSM locker_close_locker failed: 1644 (45000): Invalid transition for locker: no matching fsm_transitions','order',5,'close_cell',777);
INSERT  IGNORE INTO `fsm_errors_log` VALUES (284,'2026-04-04 15:46:27','FSM order_confirm_parcel_in failed: 1644 (45000): Invalid transition for order: no matching fsm_transitions','order',1507,'close_cell',100);
INSERT  IGNORE INTO `fsm_errors_log` VALUES (285,'2026-04-04 15:46:42','FSM order_confirm_parcel_in failed: 1644 (45000): Invalid transition for order: no matching fsm_transitions','order',1528,'close_cell',1001);
INSERT  IGNORE INTO `fsm_errors_log` VALUES (286,'2026-04-04 15:56:58','FSM order_confirm_parcel_in failed: 1644 (45000): Invalid transition for order: no matching fsm_transitions','order',1528,'close_cell',1001);
INSERT  IGNORE INTO `fsm_errors_log` VALUES (287,'2026-04-04 15:57:13','Неизвестный статус курьера: order_in_transit_to_post2','order',1531,'close_cell',100);
INSERT  IGNORE INTO `fsm_errors_log` VALUES (288,'2026-04-04 15:57:18','Неизвестный статус курьера: order_completed','order',1525,'close_cell',100);
INSERT  IGNORE INTO `fsm_errors_log` VALUES (289,'2026-04-04 15:58:48','Неизвестный статус курьера: order_in_transit_to_post2','order',1531,'close_cell',100);
INSERT  IGNORE INTO `fsm_errors_log` VALUES (290,'2026-04-04 15:59:33','Неизвестный статус курьера: order_parcel_confirmed','order',1502,'close_cell',100);
INSERT  IGNORE INTO `fsm_errors_log` VALUES (291,'2026-04-04 15:59:43','Неизвестный статус курьера: order_courier2_parcel_delivered','order',1536,'close_cell',100);
INSERT  IGNORE INTO `fsm_errors_log` VALUES (292,'2026-04-04 16:06:14','Неизвестный статус курьера: order_created','order',1514,'close_cell',100);
INSERT  IGNORE INTO `fsm_errors_log` VALUES (293,'2026-04-04 16:06:34','FSM order_confirm_parcel_in failed: 1644 (45000): Invalid transition for order: no matching fsm_transitions','order',1528,'close_cell',1001);
INSERT  IGNORE INTO `fsm_errors_log` VALUES (294,'2026-04-04 16:06:44','Неизвестный статус курьера: order_in_transit_to_post2','order',1531,'close_cell',100);
INSERT  IGNORE INTO `fsm_errors_log` VALUES (295,'2026-04-04 16:07:54','FSM locker_close_locker failed: 1644 (45000): Invalid transition for locker: no matching fsm_transitions','order',1536,'close_cell',777);
INSERT  IGNORE INTO `fsm_errors_log` VALUES (296,'2026-04-04 16:22:50','Неизвестный статус курьера: order_in_transit_to_post2','order',1531,'close_cell',100);
INSERT  IGNORE INTO `fsm_errors_log` VALUES (297,'2026-04-04 16:23:45','Неизвестный статус курьера: order_courier2_parcel_delivered','order',1536,'close_cell',100);
INSERT  IGNORE INTO `fsm_errors_log` VALUES (298,'2026-04-04 16:27:21','Неизвестный статус курьера: order_courier2_parcel_delivered','order',1536,'close_cell',100);
INSERT  IGNORE INTO `fsm_errors_log` VALUES (299,'2026-04-04 16:27:26','USER_NOT_AUTHORIZED','order',1531,'request_locker_access_code',100);
INSERT  IGNORE INTO `fsm_errors_log` VALUES (300,'2026-04-04 16:27:31','MISSING_PIN_IN_METADATA','order',1531,'open_cell',100);
INSERT  IGNORE INTO `fsm_errors_log` VALUES (301,'2026-04-04 16:27:36','Неизвестный статус курьера: order_in_transit_to_post2','order',1531,'close_cell',100);
INSERT  IGNORE INTO `fsm_errors_log` VALUES (302,'2026-04-04 16:29:46','FSM order_confirm_parcel_in failed: 1644 (45000): Invalid transition for order: no matching fsm_transitions','order',1528,'close_cell',1001);
INSERT  IGNORE INTO `fsm_errors_log` VALUES (303,'2026-04-04 16:38:07','Неизвестный статус курьера: order_courier2_parcel_delivered','order',1536,'close_cell',100);
INSERT  IGNORE INTO `fsm_errors_log` VALUES (304,'2026-04-04 16:38:17','USER_NOT_AUTHORIZED','order',1536,'request_locker_access_code',100);
INSERT  IGNORE INTO `fsm_errors_log` VALUES (305,'2026-04-04 16:44:53','Неизвестный статус курьера: order_in_transit_to_post2','order',1531,'close_cell',100);
INSERT  IGNORE INTO `fsm_errors_log` VALUES (306,'2026-04-04 16:45:08','Неизвестный статус курьера: order_courier2_parcel_delivered','order',1536,'close_cell',100);
INSERT  IGNORE INTO `fsm_errors_log` VALUES (307,'2026-04-04 16:45:13','USER_NOT_AUTHORIZED','order',1536,'request_locker_access_code',100);
INSERT  IGNORE INTO `fsm_errors_log` VALUES (308,'2026-04-04 16:45:18','MISSING_PIN_IN_METADATA','order',1536,'open_cell',100);
INSERT  IGNORE INTO `fsm_errors_log` VALUES (309,'2026-04-04 16:55:59','FSM order_confirm_parcel_in failed: 1644 (45000): Invalid transition for order: no matching fsm_transitions','order',1507,'close_cell',100);
INSERT  IGNORE INTO `fsm_errors_log` VALUES (310,'2026-04-04 16:56:04','FSM order_confirm_parcel_in failed: 1644 (45000): Invalid transition for order: no matching fsm_transitions','order',1507,'close_cell',100);
INSERT  IGNORE INTO `fsm_errors_log` VALUES (311,'2026-04-04 16:56:14','MISSING_PIN_IN_METADATA','order',1507,'open_cell',100);
INSERT  IGNORE INTO `fsm_errors_log` VALUES (312,'2026-04-04 17:00:54','MISSING_PIN_IN_METADATA','order',1536,'open_cell',100);
INSERT  IGNORE INTO `fsm_errors_log` VALUES (313,'2026-04-04 17:00:59','MISSING_PIN_IN_METADATA','order',1536,'open_cell',100);
INSERT  IGNORE INTO `fsm_errors_log` VALUES (314,'2026-04-04 17:01:04','Неизвестный статус курьера: order_courier2_parcel_delivered','order',1536,'close_cell',100);
INSERT  IGNORE INTO `fsm_errors_log` VALUES (315,'2026-04-04 17:01:40','Неизвестный статус курьера: order_in_transit_to_post2','order',1531,'close_cell',100);
INSERT  IGNORE INTO `fsm_errors_log` VALUES (316,'2026-04-04 17:13:50','Неизвестный статус курьера: order_courier2_parcel_delivered','order',1536,'close_cell',100);
INSERT  IGNORE INTO `fsm_errors_log` VALUES (317,'2026-04-04 17:14:00','Неизвестный статус курьера: order_in_transit_to_post2','order',1531,'close_cell',100);
INSERT  IGNORE INTO `fsm_errors_log` VALUES (318,'2026-04-04 17:26:41','Неизвестный статус курьера: order_courier2_parcel_delivered','order',1536,'close_cell',100);
INSERT  IGNORE INTO `fsm_errors_log` VALUES (319,'2026-04-04 17:34:27','Неизвестный статус курьера: order_courier2_parcel_delivered','order',1536,'close_cell',100);
INSERT  IGNORE INTO `fsm_errors_log` VALUES (320,'2026-04-04 17:34:42','Неизвестный статус курьера: order_courier2_parcel_delivered','order',1536,'close_cell',100);
INSERT  IGNORE INTO `fsm_errors_log` VALUES (321,'2026-04-04 17:35:07','Неизвестный статус курьера: order_courier2_parcel_delivered','order',1536,'close_cell',100);
INSERT  IGNORE INTO `fsm_errors_log` VALUES (322,'2026-04-04 17:35:12','FSM order_confirm_parcel_in failed: 1644 (45000): Invalid transition for order: no matching fsm_transitions','order',1535,'close_cell',100);
INSERT  IGNORE INTO `fsm_errors_log` VALUES (323,'2026-04-04 17:37:07','FSM order_confirm_parcel_in failed: 1644 (45000): Invalid transition for order: no matching fsm_transitions','order',1528,'close_cell',1001);
INSERT  IGNORE INTO `fsm_errors_log` VALUES (324,'2026-04-04 17:38:17','FSM locker_close_locker failed: 1644 (45000): Invalid transition for locker: no matching fsm_transitions','order',5,'close_cell',777);
INSERT  IGNORE INTO `fsm_errors_log` VALUES (325,'2026-04-04 17:40:23','Неизвестный статус курьера: order_courier2_parcel_delivered','order',1536,'close_cell',100);
INSERT  IGNORE INTO `fsm_errors_log` VALUES (326,'2026-04-06 11:24:42','FSM order_confirm_parcel_in failed: 1644 (45000): Invalid transition for order: no matching fsm_transitions','order',1535,'close_cell',100);
INSERT  IGNORE INTO `fsm_errors_log` VALUES (327,'2026-04-06 11:25:12','Неизвестный статус курьера: order_parcel_confirmed','order',1502,'open_cell',100);
INSERT  IGNORE INTO `fsm_errors_log` VALUES (328,'2026-04-06 11:25:17','Неизвестный статус курьера: order_parcel_confirmed','order',1502,'close_cell',100);
INSERT  IGNORE INTO `fsm_errors_log` VALUES (329,'2026-04-06 11:26:22','FSM locker_open_locker failed: 1644 (45000): Invalid transition for locker: no matching fsm_transitions','order',1507,'open_cell',100);
INSERT  IGNORE INTO `fsm_errors_log` VALUES (330,'2026-04-06 11:26:27','FSM order_confirm_parcel_in failed: 1644 (45000): Invalid transition for order: no matching fsm_transitions','order',1507,'close_cell',100);
INSERT  IGNORE INTO `fsm_errors_log` VALUES (331,'2026-04-06 11:27:27','FSM locker_open_locker failed: 1644 (45000): Invalid transition for locker: no matching fsm_transitions','order',1367,'open_cell',100);
INSERT  IGNORE INTO `fsm_errors_log` VALUES (332,'2026-04-06 11:31:23','FSM locker_open_locker failed: 1644 (45000): Invalid transition for locker: no matching fsm_transitions','order',1367,'open_cell',100);
INSERT  IGNORE INTO `fsm_errors_log` VALUES (333,'2026-04-06 11:32:43','Неизвестный статус курьера: order_parcel_confirmed','order',1502,'close_cell',100);
INSERT  IGNORE INTO `fsm_errors_log` VALUES (334,'2026-04-06 11:35:38','FSM locker_open_locker failed: 1644 (45000): Invalid transition for locker: no matching fsm_transitions','order',1367,'open_cell',100);
INSERT  IGNORE INTO `fsm_errors_log` VALUES (335,'2026-04-06 11:36:08','FSM locker_open_locker failed: 1644 (45000): Invalid transition for locker: no matching fsm_transitions','order',1364,'open_cell',100);
INSERT  IGNORE INTO `fsm_errors_log` VALUES (336,'2026-04-06 11:36:48','FSM locker_open_locker failed: 1644 (45000): Invalid transition for locker: no matching fsm_transitions','order',1365,'open_cell',100);
INSERT  IGNORE INTO `fsm_errors_log` VALUES (337,'2026-04-06 11:37:08','FSM locker_open_locker failed: 1644 (45000): Invalid transition for locker: no matching fsm_transitions','order',1365,'open_cell',100);
INSERT  IGNORE INTO `fsm_errors_log` VALUES (338,'2026-04-06 11:37:28','FSM order_confirm_parcel_in failed: 1644 (45000): Invalid transition for order: no matching fsm_transitions','order',1365,'close_cell',100);
INSERT  IGNORE INTO `fsm_errors_log` VALUES (339,'2026-04-06 11:37:48','FSM order_confirm_parcel_in failed: 1644 (45000): Invalid transition for order: no matching fsm_transitions','order',1365,'close_cell',100);
INSERT  IGNORE INTO `fsm_errors_log` VALUES (340,'2026-04-06 11:39:24','FSM order_confirm_parcel_in failed: 1644 (45000): Invalid transition for order: no matching fsm_transitions','order',1527,'close_cell',1001);
INSERT  IGNORE INTO `fsm_errors_log` VALUES (341,'2026-04-06 14:22:39','FSM locker_open_locker failed: 1644 (45000): Invalid transition for locker: no matching fsm_transitions','order',1365,'open_cell',100);
INSERT  IGNORE INTO `fsm_errors_log` VALUES (342,'2026-04-06 14:41:35','FSM order_confirm_parcel_in failed: 1644 (45000): Invalid transition for order: no matching fsm_transitions','order',1365,'close_cell',100);
INSERT  IGNORE INTO `fsm_errors_log` VALUES (343,'2026-04-07 20:28:08','MISSING_TEST_AUTH_HASH','order_request',276,'order_creation',NULL);
INSERT  IGNORE INTO `fsm_errors_log` VALUES (344,'2026-04-07 20:54:18','EXCEPTION: name \'CoreAuthError\' is not defined','order_request',277,'order_creation',NULL);
INSERT  IGNORE INTO `fsm_errors_log` VALUES (345,'2026-04-07 21:08:16','CORE_ERROR: Core returned error: {\'code\': \'404\', \'status\': \'error\', \'message\': \'unauthorized access\', \'data\': []}','order_request',278,'order_creation',NULL);
INSERT  IGNORE INTO `fsm_errors_log` VALUES (346,'2026-04-08 07:48:14','CLIENT_NOT_MAPPED_TO_CORE','order_request',279,'order_creation',NULL);
INSERT  IGNORE INTO `fsm_errors_log` VALUES (347,'2026-04-08 07:49:04','MISSING_CORE_TOKENS','order_request',280,'order_creation',NULL);
INSERT  IGNORE INTO `fsm_errors_log` VALUES (348,'2026-04-08 07:54:10','CORE_ERROR: Create drive order failed: name \'json\' is not defined','order_request',281,'order_creation',NULL);
INSERT  IGNORE INTO `fsm_errors_log` VALUES (349,'2026-04-08 08:07:14','CORE_ERROR: Create drive order failed: RetryError[<Future at 0x7255c8f1fe50 state=finished raised CoreUnavailableError>]','order_request',282,'order_creation',NULL);
INSERT  IGNORE INTO `fsm_errors_log` VALUES (350,'2026-04-08 08:35:11','CORE_ERROR: Create drive order failed: RetryError[<Future at 0x70b3429b4c10 state=finished raised CoreUnavailableError>]','order_request',283,'order_creation',NULL);
INSERT  IGNORE INTO `fsm_errors_log` VALUES (351,'2026-04-08 08:38:40','CORE_ERROR: Core returned error: wrong b_options keys: parcel_type,cell_size,sender_delivery,recipient_delivery,client_user_id,recipient_user_id,description,pickup_type,delivery_type','order_request',284,'order_creation',NULL);
INSERT  IGNORE INTO `fsm_errors_log` VALUES (352,'2026-04-08 08:53:02','CORE_ERROR: Core returned error: database insert failed','order_request',285,'order_creation',NULL);
INSERT  IGNORE INTO `fsm_errors_log` VALUES (353,'2026-04-08 09:00:37','NO_FREE_CELLS','order_request',286,'order_creation',NULL);
INSERT  IGNORE INTO `fsm_errors_log` VALUES (354,'2026-04-08 09:00:57','NO_FREE_CELLS','order_request',287,'order_creation',NULL);
INSERT  IGNORE INTO `fsm_errors_log` VALUES (355,'2026-04-08 09:07:09','CORE_ERROR: Core returned error: database insert failed','order_request',288,'order_creation',NULL);
INSERT  IGNORE INTO `fsm_errors_log` VALUES (356,'2026-04-08 09:09:33','CORE_ERROR: Core returned error: database insert failed','order_request',289,'order_creation',NULL);
INSERT  IGNORE INTO `fsm_errors_log` VALUES (357,'2026-04-08 11:47:23','CORE_CANCEL_FAILED: CORE_ERROR: Core returned error: wrong booking state','order',1539,'cancel_order',1000013);
INSERT  IGNORE INTO `fsm_errors_log` VALUES (358,'2026-04-08 11:56:23','CORE_CANCEL_FAILED: CORE_ERROR: Core returned error: wrong booking state','order',1539,'cancel_order',1000013);
INSERT  IGNORE INTO `fsm_errors_log` VALUES (359,'2026-04-08 11:56:34','CORE_CANCEL_FAILED: CORE_ERROR: Core returned error: wrong booking state','order',1539,'cancel_order',1000013);
INSERT  IGNORE INTO `fsm_errors_log` VALUES (360,'2026-04-08 12:13:47','CORE_CANCEL_FAILED: CORE_ERROR: Core returned error: wrong booking state','order',1539,'cancel_order',1000013);
INSERT  IGNORE INTO `fsm_errors_log` VALUES (361,'2026-04-08 12:17:32','CORE_CANCEL_FAILED: CORE_ERROR: Core returned error: wrong booking state','order',1539,'cancel_order',1000013);
INSERT  IGNORE INTO `fsm_errors_log` VALUES (362,'2026-04-08 14:47:52','CODE_NOT_ALLOWED_IN_order_cancelled','order',1540,'request_locker_access_code',1000013);

--
-- Table structure for table `fsm_states`
--

DROP TABLE IF EXISTS `fsm_states`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `fsm_states` (
  `id` int NOT NULL AUTO_INCREMENT,
  `name` varchar(50) NOT NULL,
  `label` varchar(100) DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=115 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `fsm_states`
--

INSERT  IGNORE INTO `fsm_states` VALUES (1,'order_created','Sozdan');
INSERT  IGNORE INTO `fsm_states` VALUES (3,'trip_assigned','Naznachen');
INSERT  IGNORE INTO `fsm_states` VALUES (4,'trip_in_progress','V puti');
INSERT  IGNORE INTO `fsm_states` VALUES (5,'trip_completed','Zavershon');
INSERT  IGNORE INTO `fsm_states` VALUES (6,'locker_reserved','Yacheika zarezervirovana');
INSERT  IGNORE INTO `fsm_states` VALUES (7,'locker_opened','Yacheika otkryta');
INSERT  IGNORE INTO `fsm_states` VALUES (8,'order_parcel_submitted','Posylka sdana');
INSERT  IGNORE INTO `fsm_states` VALUES (49,'order_courier1_assigned','Kurer1 naznachen');
INSERT  IGNORE INTO `fsm_states` VALUES (60,'order_parcel_confirmed','Posylka podtverzhdena');
INSERT  IGNORE INTO `fsm_states` VALUES (61,'order_parcel_missing','Posylka ne naidena');
INSERT  IGNORE INTO `fsm_states` VALUES (68,'locker_free','Yacheika svobodna');
INSERT  IGNORE INTO `fsm_states` VALUES (69,'locker_occupied','Yacheika zanyata');
INSERT  IGNORE INTO `fsm_states` VALUES (70,'locker_error','Oshibka yacheiki');
INSERT  IGNORE INTO `fsm_states` VALUES (71,'locker_maintenance','Na obsluzhivanii');
INSERT  IGNORE INTO `fsm_states` VALUES (72,'locker_parcel_submitted','Posylka sdana');
INSERT  IGNORE INTO `fsm_states` VALUES (73,'locker_parcel_confirmed','Posylka podtverzhdena');
INSERT  IGNORE INTO `fsm_states` VALUES (74,'locker_parcel_missing','Posylka ne naidena');
INSERT  IGNORE INTO `fsm_states` VALUES (75,'order_courier_has_parcel','Kurer zabral posilku');
INSERT  IGNORE INTO `fsm_states` VALUES (76,'order_reservation_expired','rezervatsiya zavershena po taymautu');
INSERT  IGNORE INTO `fsm_states` VALUES (77,'order_courier_failed','kurer ne podtverdil zabir');
INSERT  IGNORE INTO `fsm_states` VALUES (78,'order_cancelled','zakaz otmenen klientom');
INSERT  IGNORE INTO `fsm_states` VALUES (79,'locker_closed_empty','yacheyka zakryta pustaya');
INSERT  IGNORE INTO `fsm_states` VALUES (80,'trip_ready_for_pickup','gotov_zabrat');
INSERT  IGNORE INTO `fsm_states` VALUES (81,'trip_parcel_picked_up','posylka_zabirana');
INSERT  IGNORE INTO `fsm_states` VALUES (82,'trip_arrived_at_destination','pridyal_k_meste');
INSERT  IGNORE INTO `fsm_states` VALUES (83,'trip_parcel_delivered','posylka_sdana');
INSERT  IGNORE INTO `fsm_states` VALUES (84,'order_client_reserved_post1_and_post2','klient_zarezerviroval_1_i_2');
INSERT  IGNORE INTO `fsm_states` VALUES (85,'order_courier_reserved_post1_and_post2','kurer_zarezerviroval_1_i_2');
INSERT  IGNORE INTO `fsm_states` VALUES (87,'order_picked_up_from_post1','posylka_zabrana_iz_post1');
INSERT  IGNORE INTO `fsm_states` VALUES (88,'order_in_transit_to_post2','v_perevozke_k_post2');
INSERT  IGNORE INTO `fsm_states` VALUES (89,'order_arrived_at_post2','dostavlena_v_post2');
INSERT  IGNORE INTO `fsm_states` VALUES (90,'order_delivered_to_client','Posylka poluchena klientom');
INSERT  IGNORE INTO `fsm_states` VALUES (91,'order_courier2_assigned','Kurer2 naznachen');
INSERT  IGNORE INTO `fsm_states` VALUES (92,'order_courier2_has_parcel','Kurer2 zabral posylku');
INSERT  IGNORE INTO `fsm_states` VALUES (93,'order_completed','Zakaz zavershon');
INSERT  IGNORE INTO `fsm_states` VALUES (94,'order_delivery_failed','Dostavka ne udalas');
INSERT  IGNORE INTO `fsm_states` VALUES (95,'order_manual_intervention_required','Trebuetsya ruchnoe vmeshatelstvo');
INSERT  IGNORE INTO `fsm_states` VALUES (96,'trip_driver_not_found','Voditel ne naiden');
INSERT  IGNORE INTO `fsm_states` VALUES (97,'trip_failed','Poezdka prervana');
INSERT  IGNORE INTO `fsm_states` VALUES (98,'trip_manual_intervention_required','Trebuetsya ruchnoe vmeshatelstvo');
INSERT  IGNORE INTO `fsm_states` VALUES (99,'trip_created','Reis sozdan');
INSERT  IGNORE INTO `fsm_states` VALUES (100,'locker_parcel_pickup_driver','posilku zabral voditel');
INSERT  IGNORE INTO `fsm_states` VALUES (101,'locker_parcel_pickup_recipient','Poluchatel zabral posilku');
INSERT  IGNORE INTO `fsm_states` VALUES (102,'order_courier2_parcel_delivered','Kurer2 dostavil klientu, ojidaem podtverzhdeniya');
INSERT  IGNORE INTO `fsm_states` VALUES (103,'order_parcel_confirmed_post2','Posylka podtverzhdena v postamate2');
INSERT  IGNORE INTO `fsm_states` VALUES (104,'order_client_post1','posilka v post1');
INSERT  IGNORE INTO `fsm_states` VALUES (109,'reservation_active','Резерв активен');
INSERT  IGNORE INTO `fsm_states` VALUES (110,'reservation_loading','Водитель загружает');
INSERT  IGNORE INTO `fsm_states` VALUES (111,'reservation_completed','Погрузка завершена');
INSERT  IGNORE INTO `fsm_states` VALUES (112,'reservation_expired','Резерв истёк');
INSERT  IGNORE INTO `fsm_states` VALUES (113,'reservation_cancelled','Резерв отменён');
INSERT  IGNORE INTO `fsm_states` VALUES (114,'trip_canceled','Рейс отменён');

--
-- Table structure for table `fsm_transitions`
--

DROP TABLE IF EXISTS `fsm_transitions`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `fsm_transitions` (
  `id` int NOT NULL AUTO_INCREMENT,
  `from_state_id` int NOT NULL,
  `action_id` int NOT NULL,
  `to_state_id` int NOT NULL,
  PRIMARY KEY (`id`),
  KEY `from_state_id` (`from_state_id`),
  KEY `action_id` (`action_id`),
  KEY `to_state_id` (`to_state_id`),
  CONSTRAINT `fsm_transitions_ibfk_1` FOREIGN KEY (`from_state_id`) REFERENCES `fsm_states` (`id`),
  CONSTRAINT `fsm_transitions_ibfk_2` FOREIGN KEY (`action_id`) REFERENCES `fsm_actions` (`id`),
  CONSTRAINT `fsm_transitions_ibfk_3` FOREIGN KEY (`to_state_id`) REFERENCES `fsm_states` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=156 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `fsm_transitions`
--

INSERT  IGNORE INTO `fsm_transitions` VALUES (29,60,70,8);
INSERT  IGNORE INTO `fsm_transitions` VALUES (30,68,1,6);
INSERT  IGNORE INTO `fsm_transitions` VALUES (31,6,5,7);
INSERT  IGNORE INTO `fsm_transitions` VALUES (36,75,69,60);
INSERT  IGNORE INTO `fsm_transitions` VALUES (38,49,71,75);
INSERT  IGNORE INTO `fsm_transitions` VALUES (42,49,61,77);
INSERT  IGNORE INTO `fsm_transitions` VALUES (47,70,72,68);
INSERT  IGNORE INTO `fsm_transitions` VALUES (48,71,72,68);
INSERT  IGNORE INTO `fsm_transitions` VALUES (49,79,72,68);
INSERT  IGNORE INTO `fsm_transitions` VALUES (50,74,6,79);
INSERT  IGNORE INTO `fsm_transitions` VALUES (51,68,73,71);
INSERT  IGNORE INTO `fsm_transitions` VALUES (52,7,75,74);
INSERT  IGNORE INTO `fsm_transitions` VALUES (53,6,76,68);
INSERT  IGNORE INTO `fsm_transitions` VALUES (54,70,73,71);
INSERT  IGNORE INTO `fsm_transitions` VALUES (55,3,2,80);
INSERT  IGNORE INTO `fsm_transitions` VALUES (56,80,78,81);
INSERT  IGNORE INTO `fsm_transitions` VALUES (57,3,3,4);
INSERT  IGNORE INTO `fsm_transitions` VALUES (58,82,79,83);
INSERT  IGNORE INTO `fsm_transitions` VALUES (59,83,4,5);
INSERT  IGNORE INTO `fsm_transitions` VALUES (61,73,6,69);
INSERT  IGNORE INTO `fsm_transitions` VALUES (62,69,5,7);
INSERT  IGNORE INTO `fsm_transitions` VALUES (63,79,76,68);
INSERT  IGNORE INTO `fsm_transitions` VALUES (74,8,83,87);
INSERT  IGNORE INTO `fsm_transitions` VALUES (75,87,84,88);
INSERT  IGNORE INTO `fsm_transitions` VALUES (76,88,85,89);
INSERT  IGNORE INTO `fsm_transitions` VALUES (77,89,107,103);
INSERT  IGNORE INTO `fsm_transitions` VALUES (79,7,87,70);
INSERT  IGNORE INTO `fsm_transitions` VALUES (80,103,88,90);
INSERT  IGNORE INTO `fsm_transitions` VALUES (81,90,89,93);
INSERT  IGNORE INTO `fsm_transitions` VALUES (82,103,90,91);
INSERT  IGNORE INTO `fsm_transitions` VALUES (83,91,91,92);
INSERT  IGNORE INTO `fsm_transitions` VALUES (84,92,92,102);
INSERT  IGNORE INTO `fsm_transitions` VALUES (85,60,93,61);
INSERT  IGNORE INTO `fsm_transitions` VALUES (86,75,94,94);
INSERT  IGNORE INTO `fsm_transitions` VALUES (87,88,94,94);
INSERT  IGNORE INTO `fsm_transitions` VALUES (88,92,94,94);
INSERT  IGNORE INTO `fsm_transitions` VALUES (89,1,95,95);
INSERT  IGNORE INTO `fsm_transitions` VALUES (90,49,95,95);
INSERT  IGNORE INTO `fsm_transitions` VALUES (91,60,95,95);
INSERT  IGNORE INTO `fsm_transitions` VALUES (92,75,95,95);
INSERT  IGNORE INTO `fsm_transitions` VALUES (93,84,95,95);
INSERT  IGNORE INTO `fsm_transitions` VALUES (94,85,95,95);
INSERT  IGNORE INTO `fsm_transitions` VALUES (95,87,95,95);
INSERT  IGNORE INTO `fsm_transitions` VALUES (96,88,95,95);
INSERT  IGNORE INTO `fsm_transitions` VALUES (97,89,95,95);
INSERT  IGNORE INTO `fsm_transitions` VALUES (98,90,95,95);
INSERT  IGNORE INTO `fsm_transitions` VALUES (99,91,95,95);
INSERT  IGNORE INTO `fsm_transitions` VALUES (100,92,95,95);
INSERT  IGNORE INTO `fsm_transitions` VALUES (101,3,96,96);
INSERT  IGNORE INTO `fsm_transitions` VALUES (102,3,97,97);
INSERT  IGNORE INTO `fsm_transitions` VALUES (103,4,97,97);
INSERT  IGNORE INTO `fsm_transitions` VALUES (104,80,97,97);
INSERT  IGNORE INTO `fsm_transitions` VALUES (105,81,97,97);
INSERT  IGNORE INTO `fsm_transitions` VALUES (106,82,97,97);
INSERT  IGNORE INTO `fsm_transitions` VALUES (109,3,98,98);
INSERT  IGNORE INTO `fsm_transitions` VALUES (110,4,98,98);
INSERT  IGNORE INTO `fsm_transitions` VALUES (111,80,98,98);
INSERT  IGNORE INTO `fsm_transitions` VALUES (112,81,98,98);
INSERT  IGNORE INTO `fsm_transitions` VALUES (113,82,98,98);
INSERT  IGNORE INTO `fsm_transitions` VALUES (114,83,98,98);
INSERT  IGNORE INTO `fsm_transitions` VALUES (116,49,99,1);
INSERT  IGNORE INTO `fsm_transitions` VALUES (117,49,101,1);
INSERT  IGNORE INTO `fsm_transitions` VALUES (118,91,100,89);
INSERT  IGNORE INTO `fsm_transitions` VALUES (119,91,101,89);
INSERT  IGNORE INTO `fsm_transitions` VALUES (120,99,102,3);
INSERT  IGNORE INTO `fsm_transitions` VALUES (121,7,86,100);
INSERT  IGNORE INTO `fsm_transitions` VALUES (122,100,6,79);
INSERT  IGNORE INTO `fsm_transitions` VALUES (123,7,103,101);
INSERT  IGNORE INTO `fsm_transitions` VALUES (124,101,6,79);
INSERT  IGNORE INTO `fsm_transitions` VALUES (125,102,104,93);
INSERT  IGNORE INTO `fsm_transitions` VALUES (126,7,6,69);
INSERT  IGNORE INTO `fsm_transitions` VALUES (127,7,105,79);
INSERT  IGNORE INTO `fsm_transitions` VALUES (128,103,93,61);
INSERT  IGNORE INTO `fsm_transitions` VALUES (129,103,95,95);
INSERT  IGNORE INTO `fsm_transitions` VALUES (130,1,49,49);
INSERT  IGNORE INTO `fsm_transitions` VALUES (131,6,106,70);
INSERT  IGNORE INTO `fsm_transitions` VALUES (132,1,74,78);
INSERT  IGNORE INTO `fsm_transitions` VALUES (133,3,97,99);
INSERT  IGNORE INTO `fsm_transitions` VALUES (134,69,106,70);
INSERT  IGNORE INTO `fsm_transitions` VALUES (135,4,4,5);
INSERT  IGNORE INTO `fsm_transitions` VALUES (136,1,108,104);
INSERT  IGNORE INTO `fsm_transitions` VALUES (137,104,69,60);
INSERT  IGNORE INTO `fsm_transitions` VALUES (145,109,113,110);
INSERT  IGNORE INTO `fsm_transitions` VALUES (146,110,114,111);
INSERT  IGNORE INTO `fsm_transitions` VALUES (147,109,115,112);
INSERT  IGNORE INTO `fsm_transitions` VALUES (148,110,115,112);
INSERT  IGNORE INTO `fsm_transitions` VALUES (149,109,116,113);
INSERT  IGNORE INTO `fsm_transitions` VALUES (150,110,116,113);
INSERT  IGNORE INTO `fsm_transitions` VALUES (151,4,117,114);
INSERT  IGNORE INTO `fsm_transitions` VALUES (152,3,117,114);
INSERT  IGNORE INTO `fsm_transitions` VALUES (153,97,123,3);
INSERT  IGNORE INTO `fsm_transitions` VALUES (154,95,49,49);
INSERT  IGNORE INTO `fsm_transitions` VALUES (155,95,90,91);

--
-- Table structure for table `locker_cells`
--

DROP TABLE IF EXISTS `locker_cells`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `locker_cells` (
  `id` int NOT NULL AUTO_INCREMENT,
  `locker_id` int NOT NULL,
  `cell_code` varchar(50) NOT NULL,
  `cell_type` enum('S','M','L','P') NOT NULL,
  `status` varchar(50) NOT NULL DEFAULT 'locker_free',
  `current_order_id` int DEFAULT NULL,
  `created_at` datetime DEFAULT CURRENT_TIMESTAMP,
  `updated_at` datetime DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  UNIQUE KEY `locker_id` (`locker_id`,`cell_code`),
  CONSTRAINT `locker_cells_ibfk_1` FOREIGN KEY (`locker_id`) REFERENCES `lockers` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=46 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `locker_cells`
--

INSERT  IGNORE INTO `locker_cells` VALUES (1,1,'S-01','S','locker_occupied',1526,'2025-11-22 15:23:13','2026-04-01 09:35:00');
INSERT  IGNORE INTO `locker_cells` VALUES (2,1,'S-02','S','locker_occupied',1535,'2025-11-22 15:23:13','2026-04-01 10:14:11');
INSERT  IGNORE INTO `locker_cells` VALUES (3,1,'S-03','S','locker_reserved',1541,'2025-11-22 15:23:13','2026-04-08 13:05:06');
INSERT  IGNORE INTO `locker_cells` VALUES (4,1,'S-04','S','locker_free',NULL,'2025-11-22 15:23:13','2026-03-02 09:02:49');
INSERT  IGNORE INTO `locker_cells` VALUES (5,1,'M-01','M','locker_reserved',1538,'2025-11-22 15:23:13','2026-03-31 08:58:05');
INSERT  IGNORE INTO `locker_cells` VALUES (6,1,'M-02','M','locker_free',1528,'2025-11-22 15:23:13','2026-03-23 17:19:46');
INSERT  IGNORE INTO `locker_cells` VALUES (7,1,'L-01','L','locker_free',NULL,'2025-11-22 15:23:13','2026-03-02 09:02:49');
INSERT  IGNORE INTO `locker_cells` VALUES (8,1,'L-02','L','locker_free',NULL,'2025-11-22 15:23:13','2026-03-02 09:02:49');
INSERT  IGNORE INTO `locker_cells` VALUES (9,1,'P-01','P','locker_reserved',1529,'2025-11-22 15:23:13','2026-03-16 08:43:25');
INSERT  IGNORE INTO `locker_cells` VALUES (10,1,'P-02','P','locker_free',1531,'2025-11-22 15:23:13','2026-04-02 14:24:12');
INSERT  IGNORE INTO `locker_cells` VALUES (11,2,'S-01','S','locker_reserved',1526,'2025-11-22 15:23:13','2026-03-02 09:03:01');
INSERT  IGNORE INTO `locker_cells` VALUES (12,2,'S-02','S','locker_reserved',1535,'2025-11-22 15:23:13','2026-03-28 12:07:59');
INSERT  IGNORE INTO `locker_cells` VALUES (13,2,'S-03','S','locker_reserved',1541,'2025-11-22 15:23:13','2026-04-08 13:05:06');
INSERT  IGNORE INTO `locker_cells` VALUES (14,2,'S-04','S','locker_free',NULL,'2025-11-22 15:23:13','2026-03-02 09:02:49');
INSERT  IGNORE INTO `locker_cells` VALUES (15,2,'M-01','M','locker_occupied',1527,'2025-11-22 15:23:13','2026-03-19 14:07:28');
INSERT  IGNORE INTO `locker_cells` VALUES (16,2,'M-02','M','locker_occupied',1528,'2025-11-22 15:23:13','2026-04-01 10:13:56');
INSERT  IGNORE INTO `locker_cells` VALUES (17,2,'L-01','L','locker_free',NULL,'2025-11-22 15:23:13','2026-03-02 09:02:49');
INSERT  IGNORE INTO `locker_cells` VALUES (18,2,'L-02','L','locker_free',NULL,'2025-11-22 15:23:13','2026-03-02 09:02:49');
INSERT  IGNORE INTO `locker_cells` VALUES (19,2,'P-01','P','locker_reserved',1529,'2025-11-22 15:23:13','2026-03-16 08:43:25');
INSERT  IGNORE INTO `locker_cells` VALUES (20,2,'P-02','P','locker_reserved',1531,'2025-11-22 15:23:13','2026-03-19 07:44:10');
INSERT  IGNORE INTO `locker_cells` VALUES (21,3,'S-01','S','locker_free',NULL,'2025-11-22 15:23:13','2026-03-02 09:02:49');
INSERT  IGNORE INTO `locker_cells` VALUES (22,3,'S-02','S','locker_free',NULL,'2025-11-22 15:23:13','2026-03-02 09:02:49');
INSERT  IGNORE INTO `locker_cells` VALUES (23,3,'S-03','S','locker_free',NULL,'2025-11-22 15:23:13','2026-03-02 09:02:49');
INSERT  IGNORE INTO `locker_cells` VALUES (24,3,'S-04','S','locker_free',NULL,'2025-11-22 15:23:13','2025-11-22 15:23:13');
INSERT  IGNORE INTO `locker_cells` VALUES (25,3,'M-01','M','locker_free',NULL,'2025-11-22 15:23:13','2026-03-02 09:02:49');
INSERT  IGNORE INTO `locker_cells` VALUES (26,3,'M-02','M','locker_free',NULL,'2025-11-22 15:23:13','2026-03-02 09:02:49');
INSERT  IGNORE INTO `locker_cells` VALUES (27,3,'L-01','L','locker_free',NULL,'2025-11-22 15:23:13','2026-03-02 09:02:49');
INSERT  IGNORE INTO `locker_cells` VALUES (28,3,'L-02','L','locker_free',NULL,'2025-11-22 15:23:13','2026-03-02 09:02:49');
INSERT  IGNORE INTO `locker_cells` VALUES (29,3,'P-01','P','locker_reserved',1532,'2025-11-22 15:23:13','2026-03-19 07:55:11');
INSERT  IGNORE INTO `locker_cells` VALUES (30,3,'P-02','P','locker_reserved',1533,'2025-11-22 15:23:13','2026-03-19 08:02:36');
INSERT  IGNORE INTO `locker_cells` VALUES (31,4,'S-01','S','locker_free',NULL,'2025-11-22 15:23:13','2026-03-02 09:02:49');
INSERT  IGNORE INTO `locker_cells` VALUES (32,4,'S-02','S','locker_free',NULL,'2025-11-22 15:23:13','2026-03-02 09:02:49');
INSERT  IGNORE INTO `locker_cells` VALUES (33,4,'S-03','S','locker_free',NULL,'2025-11-22 15:23:13','2026-03-02 09:02:49');
INSERT  IGNORE INTO `locker_cells` VALUES (34,4,'S-04','S','locker_free',NULL,'2025-11-22 15:23:13','2026-03-02 09:02:49');
INSERT  IGNORE INTO `locker_cells` VALUES (35,4,'M-01','M','locker_free',NULL,'2025-11-22 15:23:13','2026-03-02 09:02:49');
INSERT  IGNORE INTO `locker_cells` VALUES (36,4,'M-02','M','locker_free',NULL,'2025-11-22 15:23:13','2026-03-02 09:02:49');
INSERT  IGNORE INTO `locker_cells` VALUES (37,4,'L-01','L','locker_free',NULL,'2025-11-22 15:23:13','2026-03-02 09:02:49');
INSERT  IGNORE INTO `locker_cells` VALUES (38,4,'L-02','L','locker_free',NULL,'2025-11-22 15:23:13','2026-03-02 09:02:49');
INSERT  IGNORE INTO `locker_cells` VALUES (39,4,'P-01','P','locker_reserved',1532,'2025-11-22 15:23:13','2026-03-19 07:55:11');
INSERT  IGNORE INTO `locker_cells` VALUES (40,4,'P-02','P','locker_reserved',1533,'2025-11-22 15:23:13','2026-03-19 08:02:36');
INSERT  IGNORE INTO `locker_cells` VALUES (41,1,'A01','S','locker_free',NULL,'2025-11-23 20:39:10','2026-03-02 09:02:49');
INSERT  IGNORE INTO `locker_cells` VALUES (42,1,'A02','S','locker_free',NULL,'2025-11-23 20:39:10','2026-03-02 09:02:49');
INSERT  IGNORE INTO `locker_cells` VALUES (43,1,'A03','M','locker_occupied',1534,'2025-11-23 20:39:10','2026-04-01 09:33:15');
INSERT  IGNORE INTO `locker_cells` VALUES (44,2,'B01','S','locker_free',NULL,'2025-11-23 20:39:10','2026-03-02 09:02:49');
INSERT  IGNORE INTO `locker_cells` VALUES (45,2,'B02','M','locker_reserved',1538,'2025-11-23 20:39:10','2026-03-31 08:58:05');
/*!50003 SET @saved_cs_client      = @@character_set_client */ ;
/*!50003 SET @saved_cs_results     = @@character_set_results */ ;
/*!50003 SET @saved_col_connection = @@collation_connection */ ;
/*!50003 SET character_set_client  = utf8mb4 */ ;
/*!50003 SET character_set_results = utf8mb4 */ ;
/*!50003 SET collation_connection  = utf8mb4_0900_ai_ci */ ;
/*!50003 SET @saved_sql_mode       = @@sql_mode */ ;
/*!50003 SET sql_mode              = 'ONLY_FULL_GROUP_BY,STRICT_TRANS_TABLES,NO_ZERO_IN_DATE,NO_ZERO_DATE,ERROR_FOR_DIVISION_BY_ZERO,NO_ENGINE_SUBSTITUTION' */ ;
DELIMITER ;;
/*!50003 CREATE*/ /*!50017 DEFINER=`fsm`@`localhost`*/ /*!50003 TRIGGER `trg_locker_cell_status_check` BEFORE UPDATE ON `locker_cells` FOR EACH ROW BEGIN
    IF NEW.status NOT IN (SELECT name FROM fsm_states) THEN
        SIGNAL SQLSTATE '45000'
        SET MESSAGE_TEXT = 'Invalid locker cell status: not in fsm_states';
    END IF;
END */;;
DELIMITER ;
/*!50003 SET sql_mode              = @saved_sql_mode */ ;
/*!50003 SET character_set_client  = @saved_cs_client */ ;
/*!50003 SET character_set_results = @saved_cs_results */ ;
/*!50003 SET collation_connection  = @saved_col_connection */ ;

--
-- Table structure for table `locker_models`
--

DROP TABLE IF EXISTS `locker_models`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `locker_models` (
  `id` int NOT NULL AUTO_INCREMENT,
  `model_name` varchar(100) NOT NULL,
  `description` text,
  `cell_count_s` int DEFAULT '0',
  `cell_count_m` int DEFAULT '0',
  `cell_count_l` int DEFAULT '0',
  `cell_count_p` int DEFAULT '0',
  `created_at` datetime DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=4 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `locker_models`
--

INSERT  IGNORE INTO `locker_models` VALUES (1,'Model-Post1',NULL,10,5,2,1,'2025-10-29 17:20:54');
INSERT  IGNORE INTO `locker_models` VALUES (2,'Model-2',NULL,10,5,2,1,'2025-11-21 13:37:49');
INSERT  IGNORE INTO `locker_models` VALUES (3,'Model-3',NULL,10,5,2,1,'2025-11-21 13:37:49');

--
-- Table structure for table `lockers`
--

DROP TABLE IF EXISTS `lockers`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `lockers` (
  `id` int NOT NULL AUTO_INCREMENT,
  `model_id` int NOT NULL,
  `locker_code` varchar(50) NOT NULL,
  `city` varchar(100) NOT NULL DEFAULT '',
  `location_address` varchar(255) DEFAULT NULL,
  `latitude` decimal(10,6) DEFAULT NULL,
  `longitude` decimal(10,6) DEFAULT NULL,
  `status` enum('locker_active','locker_inactive','locker_maintenance') DEFAULT 'locker_inactive',
  `created_at` datetime DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  UNIQUE KEY `locker_code` (`locker_code`),
  KEY `model_id` (`model_id`),
  CONSTRAINT `lockers_ibfk_1` FOREIGN KEY (`model_id`) REFERENCES `locker_models` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=5 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `lockers`
--

INSERT  IGNORE INTO `lockers` VALUES (1,1,'POST1','Москва','Москва, ул. Тверская, д. 1',NULL,NULL,'locker_inactive','2025-11-22 15:22:48');
INSERT  IGNORE INTO `lockers` VALUES (2,1,'POST2','Санкт-Петербург','Санкт-Петербург, Невский пр., д. 1',NULL,NULL,'locker_inactive','2025-11-22 15:22:48');
INSERT  IGNORE INTO `lockers` VALUES (3,1,'POST3','Москва','Москва, Ленинградский проспект, д. 1',NULL,NULL,'locker_inactive','2025-11-22 15:22:48');
INSERT  IGNORE INTO `lockers` VALUES (4,1,'POST4','Санкт-Петербург','Санкт-Петербург, Московский проспект, д. 1',NULL,NULL,'locker_inactive','2025-11-22 15:22:48');

--
-- Table structure for table `order_requests`
--

DROP TABLE IF EXISTS `order_requests`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `order_requests` (
  `id` int NOT NULL AUTO_INCREMENT,
  `client_user_id` int NOT NULL,
  `parcel_type` varchar(50) NOT NULL,
  `cell_size` varchar(10) NOT NULL,
  `sender_delivery` varchar(50) NOT NULL,
  `recipient_delivery` varchar(50) NOT NULL,
  `status` enum('PENDING','COMPLETED','FAILED') NOT NULL DEFAULT 'PENDING',
  `order_id` int DEFAULT NULL,
  `error_code` varchar(100) DEFAULT NULL,
  `error_message` text,
  `created_at` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `recipient_user_id` int DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `recipient_user_id` (`recipient_user_id`),
  CONSTRAINT `order_requests_ibfk_1` FOREIGN KEY (`recipient_user_id`) REFERENCES `users` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=293 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `order_requests`
--

INSERT  IGNORE INTO `order_requests` VALUES (1,0,'string','string','string','string','FAILED',NULL,'NOT_IMPLEMENTED','order_creation handler not implemented yet','2025-12-07 13:53:25',NULL);
INSERT  IGNORE INTO `order_requests` VALUES (2,0,'string','string','string','string','FAILED',NULL,'NO_FREE_CELLS','Не найдены свободные ячейки нужного размера','2025-12-07 16:37:12',NULL);
INSERT  IGNORE INTO `order_requests` VALUES (3,1005,'test','S','courier','courier','COMPLETED',6,NULL,NULL,'2025-12-07 16:45:30',NULL);
INSERT  IGNORE INTO `order_requests` VALUES (4,1006,'test','L','courier','courier','COMPLETED',7,NULL,NULL,'2025-12-07 16:54:49',NULL);
INSERT  IGNORE INTO `order_requests` VALUES (5,1007,'test','M','courier','courier','COMPLETED',8,NULL,NULL,'2025-12-07 17:08:22',NULL);
INSERT  IGNORE INTO `order_requests` VALUES (6,1008,'test','M','courier','courier','COMPLETED',9,NULL,NULL,'2025-12-07 17:17:26',NULL);
INSERT  IGNORE INTO `order_requests` VALUES (7,1009,'test','L','courier','courier','COMPLETED',10,NULL,NULL,'2025-12-07 17:19:20',NULL);
INSERT  IGNORE INTO `order_requests` VALUES (8,402,'documents','M','courier','courier','FAILED',NULL,'NO_FREE_CELLS','Не найдены свободные ячейки нужного размера','2025-12-11 09:43:29',NULL);
INSERT  IGNORE INTO `order_requests` VALUES (9,391,'documents','S','courier','courier','COMPLETED',660,NULL,NULL,'2025-12-12 08:32:33',NULL);
INSERT  IGNORE INTO `order_requests` VALUES (10,491,'documents','M','courier','courier','FAILED',NULL,'NO_FREE_CELLS','Не найдены свободные ячейки нужного размера','2025-12-12 09:38:45',NULL);
INSERT  IGNORE INTO `order_requests` VALUES (11,471,'documents','L','courier','courier','FAILED',NULL,'NO_FREE_CELLS','Не найдены свободные ячейки нужного размера','2025-12-12 09:39:44',NULL);
INSERT  IGNORE INTO `order_requests` VALUES (12,461,'documents','S','courier','courier','FAILED',NULL,'NO_FREE_CELLS','Не найдены свободные ячейки нужного размера','2025-12-12 09:46:20',NULL);
INSERT  IGNORE INTO `order_requests` VALUES (13,467,'documents','P','courier','courier','COMPLETED',661,NULL,NULL,'2025-12-12 09:55:53',NULL);
INSERT  IGNORE INTO `order_requests` VALUES (14,463,'documents','А','courier','courier','FAILED',NULL,'NO_FREE_CELLS','Не найдены свободные ячейки нужного размера','2025-12-12 10:16:43',NULL);
INSERT  IGNORE INTO `order_requests` VALUES (15,493,'documents','P','courier','courier','COMPLETED',662,NULL,NULL,'2025-12-12 10:50:14',NULL);
INSERT  IGNORE INTO `order_requests` VALUES (16,589,'documents','P','courier','courier','FAILED',NULL,'NO_FREE_CELLS','Не найдены свободные ячейки нужного размера','2025-12-12 12:40:43',NULL);
INSERT  IGNORE INTO `order_requests` VALUES (17,559,'documents','P','courier','courier','FAILED',NULL,'NO_FREE_CELLS','Не найдены свободные ячейки нужного размера','2025-12-12 13:32:58',NULL);
INSERT  IGNORE INTO `order_requests` VALUES (18,584,'documents','P','courier','courier','FAILED',NULL,'NO_FREE_CELLS','Не найдены свободные ячейки нужного размера','2025-12-12 14:22:45',NULL);
INSERT  IGNORE INTO `order_requests` VALUES (19,544,'documents','S','courier','courier','FAILED',NULL,'NO_FREE_CELLS','Не найдены свободные ячейки нужного размера','2025-12-12 16:06:43',NULL);
INSERT  IGNORE INTO `order_requests` VALUES (20,591,'documents','S','courier','courier','FAILED',NULL,'NO_FREE_CELLS','Не найдены свободные ячейки нужного размера','2025-12-12 16:21:18',NULL);
INSERT  IGNORE INTO `order_requests` VALUES (21,1,'Документы','S','courier','courier','COMPLETED',1361,NULL,NULL,'2025-12-15 17:31:14',NULL);
INSERT  IGNORE INTO `order_requests` VALUES (22,1,'Финальный тест','S','courier','courier','COMPLETED',1362,NULL,NULL,'2025-12-15 19:20:14',NULL);
INSERT  IGNORE INTO `order_requests` VALUES (23,1,'Заказ A','S','courier','courier','FAILED',NULL,'TEST_CLEANUP','Не найдены свободные ячейки нужного размера','2025-12-15 19:41:42',NULL);
INSERT  IGNORE INTO `order_requests` VALUES (24,1,'Заказ B','S','courier','courier','FAILED',NULL,'TEST_CLEANUP','Не найдены свободные ячейки нужного размера','2025-12-15 19:41:42',NULL);
INSERT  IGNORE INTO `order_requests` VALUES (25,1,'Заказ A','S','courier','courier','FAILED',NULL,'NO_FREE_CELLS','Не найдены свободные ячейки нужного размера','2025-12-15 19:50:09',NULL);
INSERT  IGNORE INTO `order_requests` VALUES (26,1,'Заказ B','S','courier','courier','FAILED',NULL,'NO_FREE_CELLS','Не найдены свободные ячейки нужного размера','2025-12-15 19:50:09',NULL);
INSERT  IGNORE INTO `order_requests` VALUES (27,1,'Заказ 1','S','courier','courier','FAILED',1364,NULL,NULL,'2025-12-15 19:56:56',NULL);
INSERT  IGNORE INTO `order_requests` VALUES (28,1,'Заказ 2','S','courier','courier','FAILED',1365,NULL,NULL,'2025-12-15 19:56:56',NULL);
INSERT  IGNORE INTO `order_requests` VALUES (29,1,'Тест А','S','courier','courier','COMPLETED',1366,NULL,NULL,'2025-12-15 20:33:22',NULL);
INSERT  IGNORE INTO `order_requests` VALUES (30,1,'Тест Б','S','courier','courier','COMPLETED',1367,NULL,NULL,'2025-12-15 20:33:22',NULL);
INSERT  IGNORE INTO `order_requests` VALUES (31,1,'Проверка trip 2','S','courier','courier','COMPLETED',1368,NULL,NULL,'2025-12-15 20:46:10',NULL);
INSERT  IGNORE INTO `order_requests` VALUES (32,1,'Debug test','S','courier','courier','COMPLETED',1369,NULL,NULL,'2025-12-16 06:00:28',NULL);
INSERT  IGNORE INTO `order_requests` VALUES (33,1,'Test trip 3','S','courier','courier','COMPLETED',1370,NULL,NULL,'2025-12-16 06:04:57',NULL);
INSERT  IGNORE INTO `order_requests` VALUES (34,1,'Тест 1','S','courier','courier','PENDING',NULL,NULL,NULL,'2025-12-16 06:48:21',NULL);
INSERT  IGNORE INTO `order_requests` VALUES (35,1,'Тест 2','S','courier','courier','COMPLETED',1371,NULL,NULL,'2025-12-16 06:48:21',NULL);
INSERT  IGNORE INTO `order_requests` VALUES (36,1,'Тест 3','S','courier','courier','COMPLETED',1372,NULL,NULL,'2025-12-16 06:48:21',NULL);
INSERT  IGNORE INTO `order_requests` VALUES (37,1,'Тест 4','S','courier','courier','COMPLETED',1373,NULL,NULL,'2025-12-16 06:48:21',NULL);
INSERT  IGNORE INTO `order_requests` VALUES (38,1,'Тест 5','S','courier','courier','FAILED',NULL,'NO_FREE_CELLS','Не найдены свободные ячейки нужного размера','2025-12-16 06:48:21',NULL);
INSERT  IGNORE INTO `order_requests` VALUES (39,1,'Тест 1→2 A','S','courier','courier','PENDING',NULL,NULL,NULL,'2025-12-16 10:00:14',NULL);
INSERT  IGNORE INTO `order_requests` VALUES (40,1,'Тест 1→2 B','S','courier','courier','PENDING',NULL,NULL,NULL,'2025-12-16 10:00:14',NULL);
INSERT  IGNORE INTO `order_requests` VALUES (41,1,'Тест локер A','S','courier','courier','COMPLETED',1374,NULL,NULL,'2025-12-16 10:02:26',NULL);
INSERT  IGNORE INTO `order_requests` VALUES (42,1,'Тест локер B','S','courier','courier','COMPLETED',1375,NULL,NULL,'2025-12-16 10:02:26',NULL);
INSERT  IGNORE INTO `order_requests` VALUES (43,1,'документы','S','courier','courier','COMPLETED',1377,NULL,NULL,'2025-12-19 09:45:06',NULL);
INSERT  IGNORE INTO `order_requests` VALUES (44,1,'документы','S','courier','courier','COMPLETED',1378,NULL,NULL,'2025-12-19 09:53:15',NULL);
INSERT  IGNORE INTO `order_requests` VALUES (45,1,'документы','M','courier','courier','COMPLETED',1379,NULL,NULL,'2025-12-19 12:04:27',NULL);
INSERT  IGNORE INTO `order_requests` VALUES (46,1001,'parcel','S','courier','courier','COMPLETED',1380,NULL,NULL,'2025-12-23 16:35:09',NULL);
INSERT  IGNORE INTO `order_requests` VALUES (47,1001,'parcel','S','courier','courier','COMPLETED',1381,NULL,NULL,'2025-12-24 11:50:30',NULL);
INSERT  IGNORE INTO `order_requests` VALUES (48,1001,'parcel','S','courier','courier','COMPLETED',1382,NULL,NULL,'2025-12-24 11:52:18',NULL);
INSERT  IGNORE INTO `order_requests` VALUES (49,1001,'parcel','S','courier','courier','COMPLETED',1383,NULL,NULL,'2025-12-24 11:54:15',NULL);
INSERT  IGNORE INTO `order_requests` VALUES (50,1001,'parcel','S','courier','courier','FAILED',NULL,'NO_FREE_CELLS','Не найдены свободные ячейки нужного размера','2025-12-24 12:00:31',NULL);
INSERT  IGNORE INTO `order_requests` VALUES (51,1001,'parcel','M','courier','courier','COMPLETED',1384,NULL,NULL,'2025-12-24 12:04:50',NULL);
INSERT  IGNORE INTO `order_requests` VALUES (52,1001,'parcel','M','courier','courier','COMPLETED',1385,NULL,NULL,'2025-12-24 12:05:22',NULL);
INSERT  IGNORE INTO `order_requests` VALUES (53,1001,'parcel','S','courier','courier','FAILED',NULL,'NO_FREE_CELLS','Не найдены свободные ячейки нужного размера','2025-12-24 12:21:46',NULL);
INSERT  IGNORE INTO `order_requests` VALUES (54,1001,'parcel','S','courier','self','FAILED',NULL,'NO_FREE_CELLS','Не найдены свободные ячейки нужного размера','2025-12-24 12:24:07',NULL);
INSERT  IGNORE INTO `order_requests` VALUES (55,1001,'letter','P','courier','self','COMPLETED',1386,NULL,NULL,'2025-12-24 12:24:20',NULL);
INSERT  IGNORE INTO `order_requests` VALUES (56,1001,'parcel','S','courier','courier','FAILED',NULL,'NO_FREE_CELLS','Не найдены свободные ячейки нужного размера','2025-12-24 12:31:53',NULL);
INSERT  IGNORE INTO `order_requests` VALUES (57,1001,'parcel','S','courier','courier','FAILED',NULL,'NO_FREE_CELLS','Не найдены свободные ячейки нужного размера','2025-12-24 12:32:29',NULL);
INSERT  IGNORE INTO `order_requests` VALUES (58,1001,'parcel','S','courier','courier','FAILED',NULL,'NO_FREE_CELLS','Не найдены свободные ячейки нужного размера','2025-12-24 12:32:50',NULL);
INSERT  IGNORE INTO `order_requests` VALUES (59,1001,'parcel','S','courier','courier','FAILED',NULL,'NO_FREE_CELLS','Не найдены свободные ячейки нужного размера','2025-12-24 12:35:26',NULL);
INSERT  IGNORE INTO `order_requests` VALUES (60,1001,'letter','P','courier','courier','COMPLETED',1387,NULL,NULL,'2025-12-24 12:35:33',NULL);
INSERT  IGNORE INTO `order_requests` VALUES (61,1001,'parcel','S','courier','courier','FAILED',NULL,'NO_FREE_CELLS','Не найдены свободные ячейки нужного размера','2025-12-24 12:37:24',NULL);
INSERT  IGNORE INTO `order_requests` VALUES (62,1001,'parcel','S','courier','courier','FAILED',NULL,'NO_FREE_CELLS','Не найдены свободные ячейки нужного размера','2025-12-24 12:37:39',NULL);
INSERT  IGNORE INTO `order_requests` VALUES (63,1001,'letter','P','courier','courier','FAILED',NULL,'NO_FREE_CELLS','Не найдены свободные ячейки нужного размера','2025-12-24 12:37:53',NULL);
INSERT  IGNORE INTO `order_requests` VALUES (64,1001,'parcel','S','courier','courier','FAILED',NULL,'NO_FREE_CELLS','Не найдены свободные ячейки нужного размера','2025-12-24 12:44:17',NULL);
INSERT  IGNORE INTO `order_requests` VALUES (65,1001,'parcel','S','courier','courier','FAILED',NULL,'NO_FREE_CELLS','Не найдены свободные ячейки нужного размера','2025-12-24 12:50:17',NULL);
INSERT  IGNORE INTO `order_requests` VALUES (66,1001,'parcel','L','courier','self','COMPLETED',1388,NULL,NULL,'2025-12-24 12:53:55',NULL);
INSERT  IGNORE INTO `order_requests` VALUES (67,1001,'parcel','M','courier','courier','FAILED',NULL,'NO_FREE_CELLS','Не найдены свободные ячейки нужного размера','2025-12-24 14:27:35',NULL);
INSERT  IGNORE INTO `order_requests` VALUES (68,1001,'parcel','M','courier','courier','COMPLETED',1389,NULL,NULL,'2025-12-24 15:36:48',NULL);
INSERT  IGNORE INTO `order_requests` VALUES (69,1001,'parcel','M','courier','courier','COMPLETED',1390,NULL,NULL,'2025-12-24 15:40:47',NULL);
INSERT  IGNORE INTO `order_requests` VALUES (70,1001,'parcel','M','courier','courier','COMPLETED',1391,NULL,NULL,'2025-12-24 15:40:59',NULL);
INSERT  IGNORE INTO `order_requests` VALUES (71,1001,'parcel','L','courier','courier','COMPLETED',1392,NULL,NULL,'2025-12-24 15:42:42',NULL);
INSERT  IGNORE INTO `order_requests` VALUES (72,1001,'parcel','S','courier','courier','COMPLETED',1393,NULL,NULL,'2025-12-25 15:18:01',NULL);
INSERT  IGNORE INTO `order_requests` VALUES (73,1001,'parcel','S','courier','courier','COMPLETED',1394,NULL,NULL,'2025-12-25 15:20:26',NULL);
INSERT  IGNORE INTO `order_requests` VALUES (74,1001,'parcel','S','courier','courier','COMPLETED',1395,NULL,NULL,'2025-12-25 15:23:40',NULL);
INSERT  IGNORE INTO `order_requests` VALUES (75,1001,'parcel','S','courier','courier','COMPLETED',1396,NULL,NULL,'2025-12-25 15:26:12',NULL);
INSERT  IGNORE INTO `order_requests` VALUES (76,1001,'parcel','S','courier','courier','COMPLETED',1397,NULL,NULL,'2025-12-25 15:28:13',NULL);
INSERT  IGNORE INTO `order_requests` VALUES (77,1001,'parcel','S','courier','courier','FAILED',NULL,'NO_FREE_CELLS','Не найдены свободные ячейки нужного размера','2025-12-26 10:11:33',NULL);
INSERT  IGNORE INTO `order_requests` VALUES (78,1001,'parcel','S','courier','courier','FAILED',NULL,'NO_FREE_CELLS','Не найдены свободные ячейки нужного размера','2025-12-26 10:14:03',NULL);
INSERT  IGNORE INTO `order_requests` VALUES (79,1001,'parcel','S','courier','courier','FAILED',NULL,'NO_FREE_CELLS','Не найдены свободные ячейки нужного размера','2025-12-26 10:34:33',NULL);
INSERT  IGNORE INTO `order_requests` VALUES (80,1002,'parcel','L','courier','self','COMPLETED',1398,NULL,NULL,'2025-12-26 12:26:18',NULL);
INSERT  IGNORE INTO `order_requests` VALUES (81,1,'documents','S','courier','self','COMPLETED',1399,NULL,NULL,'2025-12-26 13:18:51',NULL);
INSERT  IGNORE INTO `order_requests` VALUES (82,1,'documents','M','courier','self','COMPLETED',1400,NULL,NULL,'2025-12-26 13:38:36',NULL);
INSERT  IGNORE INTO `order_requests` VALUES (83,3,'documents','M','courier','self','COMPLETED',1401,NULL,NULL,'2025-12-26 16:14:27',NULL);
INSERT  IGNORE INTO `order_requests` VALUES (84,1002,'parcel','S','courier','self','COMPLETED',1402,NULL,NULL,'2025-12-26 16:45:47',NULL);
INSERT  IGNORE INTO `order_requests` VALUES (85,1001,'parcel','S','courier','courier','COMPLETED',1403,NULL,NULL,'2025-12-26 17:11:36',NULL);
INSERT  IGNORE INTO `order_requests` VALUES (86,1001,'parcel','S','courier','courier','COMPLETED',1404,NULL,NULL,'2025-12-27 15:09:28',NULL);
INSERT  IGNORE INTO `order_requests` VALUES (87,1001,'parcel','S','courier','courier','COMPLETED',1405,NULL,NULL,'2025-12-27 15:13:30',NULL);
INSERT  IGNORE INTO `order_requests` VALUES (88,1001,'parcel','S','courier','courier','COMPLETED',1406,NULL,NULL,'2025-12-27 15:14:23',NULL);
INSERT  IGNORE INTO `order_requests` VALUES (89,1001,'parcel','S','self','courier','FAILED',NULL,'NO_FREE_CELLS','Не найдены свободные ячейки нужного размера','2025-12-27 15:29:29',NULL);
INSERT  IGNORE INTO `order_requests` VALUES (90,1001,'parcel','S','courier','courier','FAILED',NULL,'NO_FREE_CELLS','Не найдены свободные ячейки нужного размера','2025-12-27 15:30:18',NULL);
INSERT  IGNORE INTO `order_requests` VALUES (91,1001,'parcel','M','courier','courier','COMPLETED',1407,NULL,NULL,'2025-12-27 16:55:39',NULL);
INSERT  IGNORE INTO `order_requests` VALUES (92,1001,'parcel','S','courier','courier','FAILED',NULL,'NO_FREE_CELLS','Не найдены свободные ячейки нужного размера','2025-12-29 17:34:49',NULL);
INSERT  IGNORE INTO `order_requests` VALUES (93,1001,'parcel','S','courier','courier','FAILED',NULL,'NO_FREE_CELLS','Не найдены свободные ячейки нужного размера','2025-12-29 17:34:49',NULL);
INSERT  IGNORE INTO `order_requests` VALUES (94,1001,'parcel','S','courier','courier','FAILED',NULL,'NO_FREE_CELLS','Не найдены свободные ячейки нужного размера','2025-12-29 17:34:50',NULL);
INSERT  IGNORE INTO `order_requests` VALUES (95,1001,'parcel','S','courier','self','FAILED',NULL,'NO_FREE_CELLS','Не найдены свободные ячейки нужного размера','2025-12-30 14:03:58',NULL);
INSERT  IGNORE INTO `order_requests` VALUES (96,1002,'parcel','S','courier','self','FAILED',NULL,'NO_FREE_CELLS','Не найдены свободные ячейки нужного размера','2025-12-30 17:00:52',NULL);
INSERT  IGNORE INTO `order_requests` VALUES (97,1001,'parcel','S','courier','courier','FAILED',NULL,'NO_FREE_CELLS','Не найдены свободные ячейки нужного размера','2025-12-30 17:03:17',NULL);
INSERT  IGNORE INTO `order_requests` VALUES (98,1001,'parcel','S','courier','self','FAILED',NULL,'NO_FREE_CELLS','Не найдены свободные ячейки нужного размера','2025-12-30 17:09:41',NULL);
INSERT  IGNORE INTO `order_requests` VALUES (99,1001,'parcel','S','courier','courier','FAILED',NULL,'NO_FREE_CELLS','Не найдены свободные ячейки нужного размера','2025-12-30 17:10:22',NULL);
INSERT  IGNORE INTO `order_requests` VALUES (100,1001,'parcel','S','courier','courier','FAILED',NULL,'NO_FREE_CELLS','Не найдены свободные ячейки нужного размера','2025-12-30 17:49:29',NULL);
INSERT  IGNORE INTO `order_requests` VALUES (101,1001,'parcel','S','courier','courier','FAILED',NULL,'NO_FREE_CELLS','Не найдены свободные ячейки нужного размера','2025-12-30 17:52:06',NULL);
INSERT  IGNORE INTO `order_requests` VALUES (102,1001,'parcel','S','courier','self','FAILED',NULL,'NO_FREE_CELLS','Не найдены свободные ячейки нужного размера','2025-12-30 19:43:43',NULL);
INSERT  IGNORE INTO `order_requests` VALUES (103,1001,'parcel','S','courier','self','FAILED',NULL,'NO_FREE_CELLS','Не найдены свободные ячейки нужного размера','2025-12-30 19:49:57',NULL);
INSERT  IGNORE INTO `order_requests` VALUES (104,1001,'parcel_small','M','courier','courier','FAILED',NULL,'NO_FREE_CELLS','Не найдены свободные ячейки нужного размера','2025-12-31 09:50:17',NULL);
INSERT  IGNORE INTO `order_requests` VALUES (105,1001,'parcel','S','courier','courier','FAILED',NULL,'NO_FREE_CELLS','Не найдены свободные ячейки нужного размера','2025-12-31 11:09:27',NULL);
INSERT  IGNORE INTO `order_requests` VALUES (106,1001,'parcel','S','courier','courier','COMPLETED',1408,NULL,NULL,'2025-12-31 11:19:12',NULL);
INSERT  IGNORE INTO `order_requests` VALUES (107,1001,'parcel','S','courier','courier','COMPLETED',1409,NULL,NULL,'2026-01-01 13:22:50',NULL);
INSERT  IGNORE INTO `order_requests` VALUES (108,1001,'parcel','S','courier','courier','COMPLETED',1410,NULL,NULL,'2026-01-01 13:23:50',NULL);
INSERT  IGNORE INTO `order_requests` VALUES (109,1001,'parcel','S','courier','courier','COMPLETED',1411,NULL,NULL,'2026-01-02 10:48:14',NULL);
INSERT  IGNORE INTO `order_requests` VALUES (110,1001,'parcel','S','courier','courier','COMPLETED',1412,NULL,NULL,'2026-01-02 11:09:22',NULL);
INSERT  IGNORE INTO `order_requests` VALUES (111,1002,'parcel','S','courier','courier','FAILED',NULL,'NO_FREE_CELLS','Не найдены свободные ячейки нужного размера','2026-01-02 11:09:34',NULL);
INSERT  IGNORE INTO `order_requests` VALUES (112,1001,'parcel','S','courier','courier','FAILED',NULL,'NO_FREE_CELLS','Не найдены свободные ячейки нужного размера','2026-01-02 11:54:29',NULL);
INSERT  IGNORE INTO `order_requests` VALUES (113,1001,'parcel','S','courier','courier','FAILED',NULL,'NO_FREE_CELLS','Не найдены свободные ячейки нужного размера','2026-01-02 11:55:42',NULL);
INSERT  IGNORE INTO `order_requests` VALUES (114,1001,'parcel','S','courier','courier','FAILED',NULL,'NO_FREE_CELLS','Не найдены свободные ячейки нужного размера','2026-01-02 13:58:06',NULL);
INSERT  IGNORE INTO `order_requests` VALUES (115,1001,'parcel','S','courier','courier','FAILED',NULL,'NO_FREE_CELLS','Не найдены свободные ячейки нужного размера','2026-01-02 14:15:23',NULL);
INSERT  IGNORE INTO `order_requests` VALUES (116,1003,'parcel','M','courier','courier','PENDING',NULL,NULL,NULL,'2026-01-06 13:15:59',NULL);
INSERT  IGNORE INTO `order_requests` VALUES (117,1003,'parcel','L','courier','courier','COMPLETED',1413,NULL,NULL,'2026-01-06 15:00:13',NULL);
INSERT  IGNORE INTO `order_requests` VALUES (118,1001,'parcel','S','courier','courier','COMPLETED',1414,NULL,NULL,'2026-01-09 17:03:26',NULL);
INSERT  IGNORE INTO `order_requests` VALUES (119,0,'string','string','string','string','FAILED',NULL,'NO_FREE_CELLS','Не найдены свободные ячейки нужного размера','2026-01-09 17:41:53',NULL);
INSERT  IGNORE INTO `order_requests` VALUES (120,1001,'parcel','S','courier','courier','COMPLETED',1415,NULL,NULL,'2026-01-09 18:09:14',NULL);
INSERT  IGNORE INTO `order_requests` VALUES (121,1001,'parcel','S','courier','courier','COMPLETED',1416,NULL,NULL,'2026-01-09 18:09:48',NULL);
INSERT  IGNORE INTO `order_requests` VALUES (122,1001,'parcel','S','courier','courier','COMPLETED',1417,NULL,NULL,'2026-01-09 18:15:57',NULL);
INSERT  IGNORE INTO `order_requests` VALUES (123,1001,'parcel','S','courier','courier','COMPLETED',1418,NULL,NULL,'2026-01-09 18:17:30',NULL);
INSERT  IGNORE INTO `order_requests` VALUES (124,0,'string','string','string','string','FAILED',NULL,'NO_FREE_CELLS','Не найдены свободные ячейки нужного размера','2026-01-10 08:42:22',NULL);
INSERT  IGNORE INTO `order_requests` VALUES (125,1001,'parcel','S','courier','courier','FAILED',NULL,'NO_FREE_CELLS','Не найдены свободные ячейки нужного размера','2026-01-10 08:53:37',NULL);
INSERT  IGNORE INTO `order_requests` VALUES (126,1001,'parcel','S','self','courier','FAILED',NULL,'NO_FREE_CELLS','Не найдены свободные ячейки нужного размера','2026-01-10 08:55:10',NULL);
INSERT  IGNORE INTO `order_requests` VALUES (127,1001,'parcel','S','self','courier','FAILED',NULL,'NO_FREE_CELLS','Не найдены свободные ячейки нужного размера','2026-01-10 08:56:04',NULL);
INSERT  IGNORE INTO `order_requests` VALUES (128,1001,'parcel','S','self','courier','FAILED',NULL,'NO_FREE_CELLS','Не найдены свободные ячейки нужного размера','2026-01-10 08:59:02',NULL);
INSERT  IGNORE INTO `order_requests` VALUES (129,1002,'parcel','M','courier','courier','COMPLETED',1419,NULL,NULL,'2026-01-11 11:45:15',NULL);
INSERT  IGNORE INTO `order_requests` VALUES (130,1003,'parcel','L','courier','courier','COMPLETED',1420,NULL,NULL,'2026-01-11 12:34:50',NULL);
INSERT  IGNORE INTO `order_requests` VALUES (131,1001,'parcel','M','courier','courier','COMPLETED',1421,NULL,NULL,'2026-01-11 12:40:09',NULL);
INSERT  IGNORE INTO `order_requests` VALUES (132,1001,'parcel','M','courier','courier','COMPLETED',1422,NULL,NULL,'2026-01-11 14:14:40',NULL);
INSERT  IGNORE INTO `order_requests` VALUES (133,1001,'parcel','S','courier','courier','FAILED',NULL,'NO_FREE_CELLS','Не найдены свободные ячейки нужного размера','2026-01-12 10:14:59',NULL);
INSERT  IGNORE INTO `order_requests` VALUES (134,1001,'parcel','S','courier','courier','FAILED',NULL,'NO_FREE_CELLS','Не найдены свободные ячейки нужного размера','2026-01-12 10:15:56',NULL);
INSERT  IGNORE INTO `order_requests` VALUES (135,1001,'string','string','string','string','FAILED',NULL,'NO_FREE_CELLS','Не найдены свободные ячейки нужного размера','2026-01-12 10:17:22',NULL);
INSERT  IGNORE INTO `order_requests` VALUES (136,1001,'parcel','S','courier','courier','FAILED',NULL,'NO_FREE_CELLS','Не найдены свободные ячейки нужного размера','2026-01-12 11:50:29',NULL);
INSERT  IGNORE INTO `order_requests` VALUES (137,1001,'parcel','S','courier','courier','FAILED',NULL,'NO_FREE_CELLS','Не найдены свободные ячейки нужного размера','2026-01-12 11:50:48',NULL);
INSERT  IGNORE INTO `order_requests` VALUES (138,1001,'parcel','S','courier','courier','FAILED',NULL,'NO_FREE_CELLS','Не найдены свободные ячейки нужного размера','2026-01-12 11:56:06',NULL);
INSERT  IGNORE INTO `order_requests` VALUES (139,1001,'parcel','S','courier','courier','FAILED',NULL,'NO_FREE_CELLS','Не найдены свободные ячейки нужного размера','2026-01-12 12:00:26',NULL);
INSERT  IGNORE INTO `order_requests` VALUES (140,1001,'parcel','S','courier','courier','FAILED',NULL,'NO_FREE_CELLS','Не найдены свободные ячейки нужного размера','2026-01-12 12:01:18',NULL);
INSERT  IGNORE INTO `order_requests` VALUES (141,1002,'parcel','S','courier','courier','FAILED',NULL,'NO_FREE_CELLS','Не найдены свободные ячейки нужного размера','2026-01-12 12:02:52',NULL);
INSERT  IGNORE INTO `order_requests` VALUES (142,1003,'parcel','M','self','courier','FAILED',NULL,'NO_FREE_CELLS','Не найдены свободные ячейки нужного размера','2026-01-12 12:08:20',NULL);
INSERT  IGNORE INTO `order_requests` VALUES (143,1003,'parcel','S','self','courier','COMPLETED',1423,NULL,NULL,'2026-01-12 12:13:19',NULL);
INSERT  IGNORE INTO `order_requests` VALUES (144,1003,'parcel','S','self','courier','COMPLETED',1424,NULL,NULL,'2026-01-12 14:47:07',NULL);
INSERT  IGNORE INTO `order_requests` VALUES (145,1003,'parcel','M','self','courier','COMPLETED',1425,NULL,NULL,'2026-01-12 14:47:45',NULL);
INSERT  IGNORE INTO `order_requests` VALUES (146,1004,'parcel','M','self','courier','COMPLETED',1426,NULL,NULL,'2026-01-12 14:49:24',NULL);
INSERT  IGNORE INTO `order_requests` VALUES (147,1004,'parcel','XL','self','courier','FAILED',NULL,'NO_FREE_CELLS','Не найдены свободные ячейки нужного размера','2026-01-12 14:49:49',NULL);
INSERT  IGNORE INTO `order_requests` VALUES (148,1002,'parcel','S','courier','courier','COMPLETED',1427,NULL,NULL,'2026-01-12 15:50:00',NULL);
INSERT  IGNORE INTO `order_requests` VALUES (149,1002,'parcel','S','courier','courier','COMPLETED',1428,NULL,NULL,'2026-01-12 15:50:37',NULL);
INSERT  IGNORE INTO `order_requests` VALUES (150,1004,'parcel','S','courier','courier','COMPLETED',1429,NULL,NULL,'2026-01-12 15:52:46',NULL);
INSERT  IGNORE INTO `order_requests` VALUES (151,1001,'parcel','S','courier','courier','FAILED',NULL,'NO_FREE_CELLS','Не найдены свободные ячейки нужного размера','2026-01-12 16:15:26',NULL);
INSERT  IGNORE INTO `order_requests` VALUES (152,1001,'parcel','S','courier','courier','FAILED',NULL,'NO_FREE_CELLS','Не найдены свободные ячейки нужного размера','2026-01-12 16:15:29',NULL);
INSERT  IGNORE INTO `order_requests` VALUES (153,1003,'parcel','M','courier','courier','COMPLETED',1435,NULL,NULL,'2026-01-12 16:18:37',NULL);
INSERT  IGNORE INTO `order_requests` VALUES (154,1004,'parcel','S','courier','courier','FAILED',NULL,'NO_FREE_CELLS','Не найдены свободные ячейки нужного размера','2026-01-12 16:21:59',NULL);
INSERT  IGNORE INTO `order_requests` VALUES (155,1004,'parcel','S','courier','courier','FAILED',NULL,'NO_FREE_CELLS','Не найдены свободные ячейки нужного размера','2026-01-12 16:23:16',NULL);
INSERT  IGNORE INTO `order_requests` VALUES (156,1003,'parcel','S','courier','courier','COMPLETED',1434,NULL,NULL,'2026-01-13 07:54:40',NULL);
INSERT  IGNORE INTO `order_requests` VALUES (157,1003,'parcel','S','courier','courier','COMPLETED',1433,NULL,NULL,'2026-01-13 07:55:58',NULL);
INSERT  IGNORE INTO `order_requests` VALUES (158,1003,'parcel','S','courier','courier','FAILED',NULL,'NO_FREE_CELLS','Не найдены свободные ячейки нужного размера','2026-01-13 07:58:59',NULL);
INSERT  IGNORE INTO `order_requests` VALUES (159,0,'string','string','string','string','FAILED',NULL,'NO_FREE_CELLS','Не найдены свободные ячейки нужного размера','2026-01-13 08:00:47',NULL);
INSERT  IGNORE INTO `order_requests` VALUES (160,1004,'string','string','string','string','FAILED',NULL,'NO_FREE_CELLS','Не найдены свободные ячейки нужного размера','2026-01-13 08:01:29',NULL);
INSERT  IGNORE INTO `order_requests` VALUES (161,1005,'parcel','S','courier','courier','FAILED',NULL,'NO_FREE_CELLS','Не найдены свободные ячейки нужного размера','2026-01-13 08:22:44',NULL);
INSERT  IGNORE INTO `order_requests` VALUES (162,1003,'parcel','M','courier','courier','COMPLETED',1432,NULL,NULL,'2026-01-13 08:47:16',NULL);
INSERT  IGNORE INTO `order_requests` VALUES (163,1003,'parcel','L','courier','courier','COMPLETED',1431,NULL,NULL,'2026-01-13 09:23:48',NULL);
INSERT  IGNORE INTO `order_requests` VALUES (164,1004,'parcel','M','courier','courier','FAILED',NULL,'NO_FREE_CELLS','Не найдены свободные ячейки нужного размера','2026-01-13 15:27:13',NULL);
INSERT  IGNORE INTO `order_requests` VALUES (165,1004,'parcel','M','self','courier','FAILED',NULL,'NO_FREE_CELLS','Не найдены свободные ячейки нужного размера','2026-01-13 15:34:52',NULL);
INSERT  IGNORE INTO `order_requests` VALUES (166,1004,'parcel','P','courier','courier','COMPLETED',1436,NULL,NULL,'2026-01-13 15:53:22',NULL);
INSERT  IGNORE INTO `order_requests` VALUES (167,1004,'parcel','M','courier','courier','FAILED',NULL,'NO_FREE_CELLS','Не найдены свободные ячейки нужного размера','2026-01-13 18:15:03',NULL);
INSERT  IGNORE INTO `order_requests` VALUES (168,1004,'parcel','M','courier','courier','FAILED',NULL,'NO_FREE_CELLS','Не найдены свободные ячейки нужного размера','2026-01-13 18:17:13',NULL);
INSERT  IGNORE INTO `order_requests` VALUES (169,1004,'parcel','M','courier','courier','FAILED',NULL,'NO_FREE_CELLS','Не найдены свободные ячейки нужного размера','2026-01-13 18:18:02',NULL);
INSERT  IGNORE INTO `order_requests` VALUES (170,1004,'parcel','S','courier','courier','FAILED',NULL,'NO_FREE_CELLS','Не найдены свободные ячейки нужного размера','2026-01-15 07:50:36',NULL);
INSERT  IGNORE INTO `order_requests` VALUES (171,1004,'letter','P','courier','courier','COMPLETED',1437,NULL,NULL,'2026-01-15 07:50:51',NULL);
INSERT  IGNORE INTO `order_requests` VALUES (172,1001,'parcel','M','courier','courier','COMPLETED',1438,NULL,NULL,'2026-01-15 08:01:09',NULL);
INSERT  IGNORE INTO `order_requests` VALUES (173,1001,'letter','P','courier','courier','COMPLETED',1439,NULL,NULL,'2026-01-15 10:28:35',NULL);
INSERT  IGNORE INTO `order_requests` VALUES (174,1004,'parcel','P','courier','courier','COMPLETED',1440,NULL,NULL,'2026-01-15 12:46:44',NULL);
INSERT  IGNORE INTO `order_requests` VALUES (175,1004,'parcel','P','courier','courier','FAILED',NULL,'NO_FREE_CELLS','Не найдены свободные ячейки нужного размера','2026-01-15 12:50:36',NULL);
INSERT  IGNORE INTO `order_requests` VALUES (176,1004,'parcel','L','courier','courier','COMPLETED',1441,NULL,NULL,'2026-01-15 12:50:51',NULL);
INSERT  IGNORE INTO `order_requests` VALUES (177,1003,'parcel','L','courier','courier','FAILED',NULL,'NO_FREE_CELLS','Не найдены свободные ячейки нужного размера','2026-01-15 20:50:58',NULL);
INSERT  IGNORE INTO `order_requests` VALUES (178,1004,'parcel','L','courier','courier','FAILED',NULL,'NO_FREE_CELLS','Не найдены свободные ячейки нужного размера','2026-01-15 20:51:16',NULL);
INSERT  IGNORE INTO `order_requests` VALUES (179,1005,'parcel','L','courier','courier','FAILED',NULL,'NO_FREE_CELLS','Не найдены свободные ячейки нужного размера','2026-01-15 20:51:28',NULL);
INSERT  IGNORE INTO `order_requests` VALUES (180,1001,'parcel','L','courier','courier','FAILED',NULL,'NO_FREE_CELLS','Не найдены свободные ячейки нужного размера','2026-01-15 20:51:38',NULL);
INSERT  IGNORE INTO `order_requests` VALUES (181,1002,'parcel','L','courier','courier','FAILED',NULL,'NO_FREE_CELLS','Не найдены свободные ячейки нужного размера','2026-01-15 20:51:51',NULL);
INSERT  IGNORE INTO `order_requests` VALUES (182,1005,'parcel','M','courier','courier','COMPLETED',1442,NULL,NULL,'2026-01-15 20:52:10',NULL);
INSERT  IGNORE INTO `order_requests` VALUES (183,1003,'parcel','S','courier','courier','COMPLETED',1443,NULL,NULL,'2026-01-27 14:17:24',NULL);
INSERT  IGNORE INTO `order_requests` VALUES (184,1004,'parcel','L','courier','courier','PENDING',NULL,NULL,NULL,'2026-01-27 14:19:54',NULL);
INSERT  IGNORE INTO `order_requests` VALUES (185,1004,'parcel','S','courier','courier','PENDING',NULL,NULL,NULL,'2026-01-27 14:20:38',NULL);
INSERT  IGNORE INTO `order_requests` VALUES (186,1004,'parcel','M','courier','courier','COMPLETED',1444,NULL,NULL,'2026-01-27 14:21:01',NULL);
INSERT  IGNORE INTO `order_requests` VALUES (187,1004,'parcel','M','courier','courier','PENDING',NULL,NULL,NULL,'2026-01-28 08:14:19',NULL);
INSERT  IGNORE INTO `order_requests` VALUES (188,1004,'parcel','M','courier','courier','PENDING',NULL,NULL,NULL,'2026-01-28 08:38:04',NULL);
INSERT  IGNORE INTO `order_requests` VALUES (189,1004,'parcel','M','courier','courier','PENDING',NULL,NULL,NULL,'2026-01-28 09:49:33',NULL);
INSERT  IGNORE INTO `order_requests` VALUES (190,1004,'parcel','M','courier','courier','PENDING',NULL,NULL,NULL,'2026-01-28 11:38:08',NULL);
INSERT  IGNORE INTO `order_requests` VALUES (191,1004,'parcel','M','courier','courier','COMPLETED',1446,NULL,NULL,'2026-01-28 11:48:06',NULL);
INSERT  IGNORE INTO `order_requests` VALUES (192,1005,'parcel','S','courier','self','COMPLETED',1447,NULL,NULL,'2026-01-28 14:55:21',NULL);
INSERT  IGNORE INTO `order_requests` VALUES (193,1005,'parcel','X','self','self','FAILED',NULL,'NO_FREE_CELLS','No free cells of type \'X\' found for request 193.','2026-01-28 14:58:30',NULL);
INSERT  IGNORE INTO `order_requests` VALUES (194,1005,'parcel','S','self','self','COMPLETED',1448,NULL,NULL,'2026-01-29 08:12:39',NULL);
INSERT  IGNORE INTO `order_requests` VALUES (195,1004,'parcel','S','self','self','COMPLETED',1449,NULL,NULL,'2026-02-04 15:52:57',NULL);
INSERT  IGNORE INTO `order_requests` VALUES (196,1004,'parcel','M','courier','self','COMPLETED',1502,NULL,NULL,'2026-02-05 07:54:07',NULL);
INSERT  IGNORE INTO `order_requests` VALUES (197,1004,'parcel','S','courier','courier','COMPLETED',1503,NULL,NULL,'2026-02-05 08:00:37',NULL);
INSERT  IGNORE INTO `order_requests` VALUES (198,1005,'parsel','M','self','self','COMPLETED',1504,NULL,NULL,'2026-02-05 09:06:16',NULL);
INSERT  IGNORE INTO `order_requests` VALUES (199,1005,'parsel','F','self','self','FAILED',NULL,'NO_FREE_CELLS','NO_FREE_CELLS','2026-02-05 09:06:50',NULL);
INSERT  IGNORE INTO `order_requests` VALUES (200,1003,'parcel','S','courier','courier','COMPLETED',1505,NULL,NULL,'2026-02-06 05:52:47',NULL);
INSERT  IGNORE INTO `order_requests` VALUES (201,1003,'parcel','S','courier','courier','COMPLETED',1506,NULL,NULL,'2026-02-06 05:53:08',NULL);
INSERT  IGNORE INTO `order_requests` VALUES (202,1003,'parcel','S','courier','courier','COMPLETED',1507,NULL,NULL,'2026-02-06 05:53:28',NULL);
INSERT  IGNORE INTO `order_requests` VALUES (203,1003,'parcel','S','courier','courier','FAILED',NULL,'NO_FREE_CELLS','NO_FREE_CELLS','2026-02-06 05:53:40',NULL);
INSERT  IGNORE INTO `order_requests` VALUES (204,1003,'parcel','S','courier','courier','FAILED',NULL,'NO_FREE_CELLS','NO_FREE_CELLS','2026-02-06 05:53:43',NULL);
INSERT  IGNORE INTO `order_requests` VALUES (205,1003,'parcel','S','courier','courier','FAILED',NULL,'NO_FREE_CELLS','NO_FREE_CELLS','2026-02-06 05:53:49',NULL);
INSERT  IGNORE INTO `order_requests` VALUES (206,1001,'parcel','S','courier','courier','FAILED',NULL,'NO_FREE_CELLS','NO_FREE_CELLS','2026-02-06 16:31:36',NULL);
INSERT  IGNORE INTO `order_requests` VALUES (207,1004,'parcel','M','courier','courier','FAILED',NULL,'List argument must consist only of tuples or dictionaries','List argument must consist only of tuples or dictionaries','2026-02-08 12:08:59',NULL);
INSERT  IGNORE INTO `order_requests` VALUES (208,1004,'parcel','M','courier','courier','FAILED',NULL,'List argument must consist only of tuples or dictionaries','List argument must consist only of tuples or dictionaries','2026-02-08 12:38:24',NULL);
INSERT  IGNORE INTO `order_requests` VALUES (209,1004,'parcel','M','courier','courier','FAILED',NULL,'List argument must consist only of tuples or dictionaries','List argument must consist only of tuples or dictionaries','2026-02-08 12:50:37',NULL);
INSERT  IGNORE INTO `order_requests` VALUES (210,1004,'parcel','M','courier','courier','FAILED',NULL,'List argument must consist only of tuples or dictionaries','List argument must consist only of tuples or dictionaries','2026-02-08 12:56:31',NULL);
INSERT  IGNORE INTO `order_requests` VALUES (211,1004,'parcel','M','courier','courier','FAILED',NULL,'List argument must consist only of tuples or dictionaries','List argument must consist only of tuples or dictionaries','2026-02-08 13:03:35',NULL);
INSERT  IGNORE INTO `order_requests` VALUES (212,1004,'parcel','M','courier','courier','FAILED',NULL,'List argument must consist only of tuples or dictionaries','List argument must consist only of tuples or dictionaries','2026-02-08 13:11:13',NULL);
INSERT  IGNORE INTO `order_requests` VALUES (213,1004,'parcel','M','courier','courier','COMPLETED',1508,NULL,NULL,'2026-02-08 13:22:41',NULL);
INSERT  IGNORE INTO `order_requests` VALUES (214,1005,'parcel','M','courier','self','COMPLETED',1509,NULL,NULL,'2026-02-10 15:14:02',NULL);
INSERT  IGNORE INTO `order_requests` VALUES (215,1005,'parcel','S','self','self','COMPLETED',1510,NULL,NULL,'2026-02-10 17:07:27',2001);
INSERT  IGNORE INTO `order_requests` VALUES (216,1005,'parcel','S','courier','self','COMPLETED',1511,NULL,NULL,'2026-02-14 13:39:16',2001);
INSERT  IGNORE INTO `order_requests` VALUES (217,1005,'parcel','S','courier','self','COMPLETED',1512,NULL,NULL,'2026-02-14 13:41:02',2001);
INSERT  IGNORE INTO `order_requests` VALUES (218,1005,'parcel','M','courier','self','COMPLETED',1513,NULL,NULL,'2026-02-14 14:13:45',2001);
INSERT  IGNORE INTO `order_requests` VALUES (219,1001,'parcel','S','courier','courier','COMPLETED',1514,NULL,NULL,'2026-02-16 11:35:01',2001);
INSERT  IGNORE INTO `order_requests` VALUES (220,1005,'parcel','L','courier','courier','COMPLETED',1515,NULL,NULL,'2026-02-17 09:33:02',2001);
INSERT  IGNORE INTO `order_requests` VALUES (221,1004,'parcel','L','courier','courier','COMPLETED',1516,NULL,NULL,'2026-02-17 14:24:51',2001);
INSERT  IGNORE INTO `order_requests` VALUES (222,1004,'parcel','S','courier','courier','COMPLETED',1517,NULL,NULL,'2026-02-17 14:25:02',2001);
INSERT  IGNORE INTO `order_requests` VALUES (223,1004,'parcel','M','courier','courier','COMPLETED',1518,NULL,NULL,'2026-02-17 14:44:18',2001);
INSERT  IGNORE INTO `order_requests` VALUES (224,1004,'parcel','M','courier','courier','FAILED',NULL,'NO_FREE_CELLS','NO_FREE_CELLS','2026-02-17 14:50:21',2002);
INSERT  IGNORE INTO `order_requests` VALUES (225,1004,'parcel','P','courier','courier','COMPLETED',1519,NULL,NULL,'2026-02-17 14:50:50',2002);
INSERT  IGNORE INTO `order_requests` VALUES (226,1004,'parcel','P','courier','courier','COMPLETED',1520,NULL,NULL,'2026-02-17 14:51:04',2002);
INSERT  IGNORE INTO `order_requests` VALUES (227,1004,'parcel','P','courier','courier','COMPLETED',1521,NULL,NULL,'2026-02-17 15:07:30',2002);
INSERT  IGNORE INTO `order_requests` VALUES (228,1004,'parcel','P','courier','courier','COMPLETED',1522,NULL,NULL,'2026-02-17 15:07:30',2002);
INSERT  IGNORE INTO `order_requests` VALUES (229,1004,'parcel','P','courier','courier','FAILED',NULL,'NO_FREE_CELLS','NO_FREE_CELLS','2026-02-17 15:12:42',2002);
INSERT  IGNORE INTO `order_requests` VALUES (230,1004,'parcel','S','courier','courier','COMPLETED',1523,NULL,NULL,'2026-02-17 15:12:54',2002);
INSERT  IGNORE INTO `order_requests` VALUES (231,1004,'parcel','S','courier','courier','FAILED',NULL,'NO_FREE_CELLS','NO_FREE_CELLS','2026-02-17 18:04:21',2002);
INSERT  IGNORE INTO `order_requests` VALUES (232,1004,'parcel','M','courier','courier','FAILED',NULL,'NO_FREE_CELLS','NO_FREE_CELLS','2026-02-17 18:04:49',2002);
INSERT  IGNORE INTO `order_requests` VALUES (233,1004,'parcel','L','courier','courier','COMPLETED',1524,NULL,NULL,'2026-02-17 18:05:53',2002);
INSERT  IGNORE INTO `order_requests` VALUES (234,1001,'letter','P','courier','self','PENDING',NULL,NULL,NULL,'2026-02-21 10:03:37',2001);
INSERT  IGNORE INTO `order_requests` VALUES (235,1001,'letter','P','courier','courier','PENDING',NULL,NULL,NULL,'2026-02-21 10:04:36',2001);
INSERT  IGNORE INTO `order_requests` VALUES (236,1001,'letter','P','courier','self','PENDING',NULL,NULL,NULL,'2026-02-21 10:05:23',2001);
INSERT  IGNORE INTO `order_requests` VALUES (237,1004,'letter','P','self','courier','PENDING',NULL,NULL,NULL,'2026-02-21 10:10:36',2001);
INSERT  IGNORE INTO `order_requests` VALUES (238,1002,'parcel','M','courier','courier','PENDING',NULL,NULL,NULL,'2026-02-25 07:00:51',1003);
INSERT  IGNORE INTO `order_requests` VALUES (239,1004,'parcel','M','courier','courier','PENDING',NULL,NULL,NULL,'2026-02-25 08:30:55',2004);
INSERT  IGNORE INTO `order_requests` VALUES (240,1002,'parcel','S','courier','courier','PENDING',NULL,NULL,NULL,'2026-02-25 10:15:22',2004);
INSERT  IGNORE INTO `order_requests` VALUES (241,1002,'parcel','M','courier','courier','PENDING',NULL,NULL,NULL,'2026-02-25 10:15:36',2004);
INSERT  IGNORE INTO `order_requests` VALUES (242,1002,'parcel','L','courier','courier','COMPLETED',1525,NULL,NULL,'2026-02-25 10:16:15',2004);
INSERT  IGNORE INTO `order_requests` VALUES (243,1001,'letter','P','courier','courier','PENDING',NULL,NULL,NULL,'2026-02-27 15:25:52',2001);
INSERT  IGNORE INTO `order_requests` VALUES (244,1001,'parcel','L','self','self','PENDING',NULL,NULL,NULL,'2026-03-02 09:01:05',2004);
INSERT  IGNORE INTO `order_requests` VALUES (245,1001,'parcel','P','self','self','PENDING',NULL,NULL,NULL,'2026-03-02 09:01:22',2004);
INSERT  IGNORE INTO `order_requests` VALUES (246,1001,'parcel','S','self','self','PENDING',NULL,NULL,NULL,'2026-03-02 09:01:49',2004);
INSERT  IGNORE INTO `order_requests` VALUES (247,1001,'parcel','S','self','self','COMPLETED',1526,NULL,NULL,'2026-03-02 09:02:59',2004);
INSERT  IGNORE INTO `order_requests` VALUES (248,1001,'parcel','M','self','self','COMPLETED',1527,NULL,NULL,'2026-03-15 13:26:11',2004);
INSERT  IGNORE INTO `order_requests` VALUES (249,1001,'parcel','M','self','self','COMPLETED',1528,NULL,NULL,'2026-03-15 13:44:10',2004);
INSERT  IGNORE INTO `order_requests` VALUES (250,1001,'letter','P','courier','courier','COMPLETED',1529,NULL,NULL,'2026-03-16 08:43:24',2004);
INSERT  IGNORE INTO `order_requests` VALUES (251,1001,'letter','P','courier','courier','COMPLETED',1530,NULL,NULL,'2026-03-19 07:24:35',2004);
INSERT  IGNORE INTO `order_requests` VALUES (252,1001,'letter','P','courier','courier','COMPLETED',1531,NULL,NULL,'2026-03-19 07:44:09',2004);
INSERT  IGNORE INTO `order_requests` VALUES (253,1002,'letter','P','courier','courier','COMPLETED',1532,NULL,NULL,'2026-03-19 07:55:10',2004);
INSERT  IGNORE INTO `order_requests` VALUES (254,1002,'letter','P','courier','courier','COMPLETED',1533,NULL,NULL,'2026-03-19 08:02:31',2004);
INSERT  IGNORE INTO `order_requests` VALUES (255,1002,'letter','P','courier','courier','PENDING',NULL,NULL,NULL,'2026-03-19 08:02:37',2004);
INSERT  IGNORE INTO `order_requests` VALUES (256,1002,'letter','P','courier','courier','PENDING',NULL,NULL,NULL,'2026-03-19 08:02:37',2004);
INSERT  IGNORE INTO `order_requests` VALUES (257,1002,'letter','P','courier','courier','PENDING',NULL,NULL,NULL,'2026-03-19 08:02:37',2004);
INSERT  IGNORE INTO `order_requests` VALUES (258,1002,'letter','P','courier','courier','PENDING',NULL,NULL,NULL,'2026-03-19 08:02:38',2004);
INSERT  IGNORE INTO `order_requests` VALUES (259,1002,'letter','P','courier','courier','PENDING',NULL,NULL,NULL,'2026-03-19 08:02:38',2004);
INSERT  IGNORE INTO `order_requests` VALUES (260,1002,'letter','P','courier','courier','PENDING',NULL,NULL,NULL,'2026-03-19 08:02:50',2004);
INSERT  IGNORE INTO `order_requests` VALUES (261,1002,'letter','P','courier','courier','PENDING',NULL,NULL,NULL,'2026-03-19 08:02:50',2004);
INSERT  IGNORE INTO `order_requests` VALUES (262,1002,'letter','P','courier','courier','PENDING',NULL,NULL,NULL,'2026-03-19 08:02:50',2004);
INSERT  IGNORE INTO `order_requests` VALUES (263,1002,'letter','P','courier','courier','PENDING',NULL,NULL,NULL,'2026-03-19 08:02:54',2004);
INSERT  IGNORE INTO `order_requests` VALUES (264,1002,'letter','P','courier','courier','PENDING',NULL,NULL,NULL,'2026-03-19 08:02:54',2004);
INSERT  IGNORE INTO `order_requests` VALUES (265,1001,'letter','P','self','self','PENDING',NULL,NULL,NULL,'2026-03-20 14:00:40',2004);
INSERT  IGNORE INTO `order_requests` VALUES (266,1001,'letter','P','self','courier','PENDING',NULL,NULL,NULL,'2026-03-20 14:19:07',2004);
INSERT  IGNORE INTO `order_requests` VALUES (267,1004,'parcel','M','self','self','COMPLETED',1534,NULL,NULL,'2026-03-22 09:43:58',2001);
INSERT  IGNORE INTO `order_requests` VALUES (268,1001,'letter','P','self','self','PENDING',NULL,NULL,NULL,'2026-03-22 15:36:47',2004);
INSERT  IGNORE INTO `order_requests` VALUES (269,1001,'letter','P','self','self','PENDING',NULL,NULL,NULL,'2026-03-22 15:37:09',2004);
INSERT  IGNORE INTO `order_requests` VALUES (270,3,'letter','P','courier','courier','PENDING',NULL,NULL,NULL,'2026-03-23 08:19:20',4);
INSERT  IGNORE INTO `order_requests` VALUES (271,1002,'parcel','S','courier','courier','COMPLETED',1535,NULL,NULL,'2026-03-28 12:07:57',2004);
INSERT  IGNORE INTO `order_requests` VALUES (272,1002,'parcel','S','courier','courier','COMPLETED',1536,NULL,NULL,'2026-03-30 13:40:34',2004);
INSERT  IGNORE INTO `order_requests` VALUES (273,1004,'parcel','M','self','self','COMPLETED',1537,NULL,NULL,'2026-03-31 08:54:21',2001);
INSERT  IGNORE INTO `order_requests` VALUES (274,1004,'parcel','M','courier','courier','COMPLETED',1538,NULL,NULL,'2026-03-31 08:58:04',2001);
INSERT  IGNORE INTO `order_requests` VALUES (275,1001,'letter','P','courier','self','PENDING',NULL,NULL,NULL,'2026-04-01 09:39:01',2004);
INSERT  IGNORE INTO `order_requests` VALUES (276,1001,'parcel','S','courier','courier','PENDING',NULL,NULL,NULL,'2026-04-07 19:57:59',2004);
INSERT  IGNORE INTO `order_requests` VALUES (277,1001,'parcel','S','courier','courier','PENDING',NULL,NULL,NULL,'2026-04-07 20:54:17',2004);
INSERT  IGNORE INTO `order_requests` VALUES (278,1001,'parcel','S','courier','courier','PENDING',NULL,NULL,NULL,'2026-04-07 21:08:14',2004);
INSERT  IGNORE INTO `order_requests` VALUES (279,1001,'parcel','S','courier','courier','PENDING',NULL,NULL,NULL,'2026-04-08 07:48:10',2004);
INSERT  IGNORE INTO `order_requests` VALUES (280,1000007,'parcel','S','courier','courier','PENDING',NULL,NULL,NULL,'2026-04-08 07:49:02',2004);
INSERT  IGNORE INTO `order_requests` VALUES (281,1000013,'parcel','S','courier','courier','PENDING',NULL,NULL,NULL,'2026-04-08 07:54:05',2001);
INSERT  IGNORE INTO `order_requests` VALUES (282,1000013,'parcel','S','courier','courier','PENDING',NULL,NULL,NULL,'2026-04-08 08:07:09',2001);
INSERT  IGNORE INTO `order_requests` VALUES (283,1000013,'parcel','S','courier','courier','PENDING',NULL,NULL,NULL,'2026-04-08 08:35:05',2001);
INSERT  IGNORE INTO `order_requests` VALUES (284,1000013,'parcel','S','courier','courier','PENDING',NULL,NULL,NULL,'2026-04-08 08:38:39',2001);
INSERT  IGNORE INTO `order_requests` VALUES (285,1000013,'parcel','S','courier','courier','PENDING',NULL,NULL,NULL,'2026-04-08 08:53:01',2001);
INSERT  IGNORE INTO `order_requests` VALUES (286,1000013,'parcel','S','courier','courier','PENDING',NULL,NULL,NULL,'2026-04-08 09:00:33',2001);
INSERT  IGNORE INTO `order_requests` VALUES (287,1000013,'parcel','M','courier','courier','PENDING',NULL,NULL,NULL,'2026-04-08 09:00:56',2001);
INSERT  IGNORE INTO `order_requests` VALUES (288,1000013,'parcel','S','courier','courier','PENDING',NULL,NULL,NULL,'2026-04-08 09:07:04',2001);
INSERT  IGNORE INTO `order_requests` VALUES (289,1000013,'parcel','S','courier','courier','PENDING',NULL,NULL,NULL,'2026-04-08 09:09:29',2001);
INSERT  IGNORE INTO `order_requests` VALUES (290,1000013,'parcel','S','courier','courier','COMPLETED',1539,NULL,NULL,'2026-04-08 09:26:08',2001);
INSERT  IGNORE INTO `order_requests` VALUES (291,1000013,'parcel','S','self','self','COMPLETED',1540,NULL,NULL,'2026-04-08 12:57:54',2002);
INSERT  IGNORE INTO `order_requests` VALUES (292,1000013,'parcel','S','courier','courier','COMPLETED',1541,NULL,NULL,'2026-04-08 13:05:03',2002);

--
-- Table structure for table `orders`
--

DROP TABLE IF EXISTS `orders`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `orders` (
  `id` int NOT NULL AUTO_INCREMENT,
  `status` varchar(50) DEFAULT 'order_created',
  `description` varchar(255) DEFAULT NULL,
  `delivery_type` enum('self','courier') DEFAULT NULL,
  `parcel_type` varchar(50) DEFAULT NULL,
  `pickup_type` enum('self','courier') DEFAULT 'courier',
  `source_cell_id` int DEFAULT NULL,
  `dest_cell_id` int DEFAULT NULL,
  `updated_at` datetime DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  `created_at` datetime DEFAULT CURRENT_TIMESTAMP,
  `client_user_id` int NOT NULL,
  `recipient_user_id` int DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `source_cell_id` (`source_cell_id`),
  KEY `dest_cell_id` (`dest_cell_id`),
  KEY `idx_orders_client_user_id` (`client_user_id`),
  KEY `recipient_user_id` (`recipient_user_id`),
  CONSTRAINT `orders_ibfk_1` FOREIGN KEY (`source_cell_id`) REFERENCES `locker_cells` (`id`),
  CONSTRAINT `orders_ibfk_2` FOREIGN KEY (`dest_cell_id`) REFERENCES `locker_cells` (`id`),
  CONSTRAINT `orders_ibfk_3` FOREIGN KEY (`recipient_user_id`) REFERENCES `users` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=1542 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `orders`
--

INSERT  IGNORE INTO `orders` VALUES (1,'order_courier_failed','Timeout Order','courier',NULL,'courier',2,12,'2025-12-16 09:46:53','2025-11-24 16:33:51',0,NULL);
INSERT  IGNORE INTO `orders` VALUES (2,'order_reservation_expired','Trip Order 1','courier',NULL,'courier',3,13,'2025-11-24 16:36:07','2025-11-24 16:33:51',0,NULL);
INSERT  IGNORE INTO `orders` VALUES (3,'order_reservation_expired','Trip Order 2','courier',NULL,'courier',4,14,'2025-11-24 16:36:08','2025-11-24 16:33:51',0,NULL);
INSERT  IGNORE INTO `orders` VALUES (4,'order_reservation_expired','Trip Order 3','courier',NULL,'courier',5,15,'2025-11-24 16:36:08','2025-11-24 16:33:52',0,NULL);
INSERT  IGNORE INTO `orders` VALUES (5,'order_courier1_assigned','Order','courier',NULL,'courier',2,5,'2026-03-19 14:33:54','2025-11-26 16:25:34',0,NULL);
INSERT  IGNORE INTO `orders` VALUES (6,'order_created','test (S)','courier','test','courier',41,44,'2026-01-28 15:49:35','2025-12-07 17:02:57',1005,NULL);
INSERT  IGNORE INTO `orders` VALUES (7,'order_created','test (L)','courier','test','courier',7,17,'2025-12-25 10:42:59','2025-12-07 17:02:58',0,NULL);
INSERT  IGNORE INTO `orders` VALUES (8,'order_created','test (M)','courier','test','courier',43,45,'2025-12-25 10:42:59','2025-12-07 17:17:06',0,NULL);
INSERT  IGNORE INTO `orders` VALUES (9,'order_created','test (M)','courier','test','courier',6,16,'2025-12-25 10:42:59','2025-12-07 17:18:55',0,NULL);
INSERT  IGNORE INTO `orders` VALUES (10,'order_created','test (L)','courier','test','courier',8,18,'2025-12-25 10:42:59','2025-12-07 17:19:25',0,NULL);
INSERT  IGNORE INTO `orders` VALUES (660,'order_created','documents (S)','courier','documents','courier',42,11,'2025-12-25 10:42:59','2025-12-12 09:26:46',0,NULL);
INSERT  IGNORE INTO `orders` VALUES (661,'order_created','documents (P)','courier','documents','courier',9,19,'2025-12-25 10:42:59','2025-12-12 09:55:55',0,NULL);
INSERT  IGNORE INTO `orders` VALUES (662,'order_created','documents (P)','courier','documents','courier',10,20,'2025-12-25 10:42:59','2025-12-12 10:50:17',0,NULL);
INSERT  IGNORE INTO `orders` VALUES (1361,'order_courier_failed','Документы (S)','courier','Документы','courier',41,44,'2025-12-25 10:42:59','2025-12-15 18:43:45',0,NULL);
INSERT  IGNORE INTO `orders` VALUES (1362,'order_courier_failed','Финальный тест (S)','courier','Финальный тест','courier',42,11,'2025-12-25 10:42:59','2025-12-15 19:20:44',0,NULL);
INSERT  IGNORE INTO `orders` VALUES (1363,'order_parcel_confirmed','Заказ A (S)','courier',NULL,'courier',1,12,'2026-04-01 09:35:00','2025-12-15 19:42:02',0,NULL);
INSERT  IGNORE INTO `orders` VALUES (1364,'order_courier1_assigned','Заказ 1 (S)','courier','Заказ 1','courier',41,44,'2026-04-04 16:38:27','2025-12-15 19:57:16',0,NULL);
INSERT  IGNORE INTO `orders` VALUES (1365,'order_courier1_assigned','Заказ 2 (S)','courier','Заказ 2','courier',42,11,'2026-04-04 16:45:28','2025-12-15 19:57:16',0,NULL);
INSERT  IGNORE INTO `orders` VALUES (1366,'order_created','Тест А (S)','courier','Тест А','courier',41,44,'2025-12-25 10:42:59','2025-12-15 20:33:36',0,NULL);
INSERT  IGNORE INTO `orders` VALUES (1367,'order_courier1_assigned','Тест Б (S)','courier','Тест Б','courier',42,11,'2026-04-04 17:36:12','2025-12-15 20:33:36',0,NULL);
INSERT  IGNORE INTO `orders` VALUES (1368,'order_created','Проверка trip 2 (S)','courier','Проверка trip 2','courier',41,44,'2025-12-25 10:42:59','2025-12-15 20:46:12',0,NULL);
INSERT  IGNORE INTO `orders` VALUES (1369,'order_created','Debug test (S)','courier','Debug test','courier',41,44,'2025-12-25 10:42:59','2025-12-16 06:00:46',0,NULL);
INSERT  IGNORE INTO `orders` VALUES (1370,'order_created','Test trip 3 (S)','courier','Test trip 3','courier',42,11,'2025-12-25 10:42:59','2025-12-16 06:05:01',0,NULL);
INSERT  IGNORE INTO `orders` VALUES (1371,'order_created','Тест 2 (S)','courier','Тест 2','courier',1,12,'2025-12-25 10:42:59','2025-12-16 06:50:03',0,NULL);
INSERT  IGNORE INTO `orders` VALUES (1372,'order_created','Тест 3 (S)','courier','Тест 3','courier',2,13,'2025-12-25 10:42:59','2025-12-16 06:50:03',0,NULL);
INSERT  IGNORE INTO `orders` VALUES (1373,'order_courier_failed','Тест 4 (S)','courier','Тест 4','courier',3,14,'2025-12-25 10:42:59','2025-12-16 06:50:04',0,NULL);
INSERT  IGNORE INTO `orders` VALUES (1374,'order_created','Тест локер A (S)','courier','Тест локер A','courier',41,44,'2025-12-25 10:42:59','2025-12-16 10:03:20',0,NULL);
INSERT  IGNORE INTO `orders` VALUES (1375,'order_created','Тест локер B (S)','courier','Тест локер B','courier',42,11,'2025-12-25 10:42:59','2025-12-16 10:03:20',0,NULL);
INSERT  IGNORE INTO `orders` VALUES (1376,'order_created','Тест 2→1','courier',NULL,'courier',45,43,'2025-12-16 10:11:32','2025-12-16 10:11:32',0,NULL);
INSERT  IGNORE INTO `orders` VALUES (1377,'order_created','документы (S)','courier','документы','courier',1,12,'2025-12-25 10:42:59','2025-12-19 09:45:10',0,NULL);
INSERT  IGNORE INTO `orders` VALUES (1378,'order_parcel_confirmed','документы (S)','courier','документы','courier',41,44,'2025-12-25 10:42:59','2025-12-19 09:56:26',0,NULL);
INSERT  IGNORE INTO `orders` VALUES (1379,'order_courier_has_parcel','документы (M)','courier','документы','courier',43,45,'2025-12-25 10:42:59','2025-12-19 12:04:31',0,NULL);
INSERT  IGNORE INTO `orders` VALUES (1380,'order_cancelled','parcel (S)','courier','parcel','courier',42,11,'2026-02-13 14:24:45','2025-12-23 16:35:14',1001,NULL);
INSERT  IGNORE INTO `orders` VALUES (1381,'order_cancelled','parcel (S)','courier','parcel','courier',1,12,'2026-02-13 14:24:55','2025-12-24 11:50:31',1001,NULL);
INSERT  IGNORE INTO `orders` VALUES (1382,'order_created','parcel (S)','courier','parcel','courier',2,13,'2026-01-28 15:50:17','2025-12-24 11:52:21',1001,NULL);
INSERT  IGNORE INTO `orders` VALUES (1383,'order_created','parcel (S)','courier','parcel','courier',3,14,'2026-01-28 15:50:17','2025-12-24 11:54:17',1001,NULL);
INSERT  IGNORE INTO `orders` VALUES (1384,'order_cancelled','parcel (M)','courier','parcel','courier',5,15,'2026-02-13 14:24:35','2025-12-24 12:04:52',1001,NULL);
INSERT  IGNORE INTO `orders` VALUES (1385,'order_created','parcel (M)','courier','parcel','courier',6,16,'2026-01-28 15:50:17','2025-12-24 12:05:22',1001,NULL);
INSERT  IGNORE INTO `orders` VALUES (1386,'order_created','letter (P)','self','letter','courier',9,19,'2026-01-28 15:50:17','2025-12-24 12:24:23',1001,NULL);
INSERT  IGNORE INTO `orders` VALUES (1387,'order_created','letter (P)','courier','letter','courier',10,20,'2026-01-28 15:50:17','2025-12-24 12:35:38',1001,NULL);
INSERT  IGNORE INTO `orders` VALUES (1388,'order_created','parcel (L)','self','parcel','courier',7,17,'2026-01-28 15:50:17','2025-12-24 12:53:59',1001,NULL);
INSERT  IGNORE INTO `orders` VALUES (1389,'order_created','parcel (M)','courier','parcel','courier',43,45,'2026-01-28 15:50:17','2025-12-24 15:36:49',1001,NULL);
INSERT  IGNORE INTO `orders` VALUES (1390,'order_created','parcel (M)','courier','parcel','courier',5,15,'2026-01-28 15:50:17','2025-12-24 15:40:49',1001,NULL);
INSERT  IGNORE INTO `orders` VALUES (1391,'order_created','parcel (M)','courier','parcel','courier',6,16,'2026-01-28 15:50:17','2025-12-24 15:40:59',1001,NULL);
INSERT  IGNORE INTO `orders` VALUES (1392,'order_created','parcel (L)','courier','parcel','courier',7,17,'2026-01-28 15:50:17','2025-12-24 15:42:45',1001,NULL);
INSERT  IGNORE INTO `orders` VALUES (1393,'order_created','parcel (S)','courier','parcel','courier',41,44,'2026-01-28 15:50:17','2025-12-25 15:18:03',1001,NULL);
INSERT  IGNORE INTO `orders` VALUES (1394,'order_created','parcel (S)','courier','parcel','courier',42,11,'2026-01-28 15:50:17','2025-12-25 15:20:29',1001,NULL);
INSERT  IGNORE INTO `orders` VALUES (1395,'order_created','parcel (S)','courier','parcel','courier',1,12,'2026-01-28 15:50:17','2025-12-25 15:23:44',1001,NULL);
INSERT  IGNORE INTO `orders` VALUES (1396,'order_created','parcel (S)','courier','parcel','courier',2,13,'2026-01-28 15:50:17','2025-12-25 15:26:14',1001,NULL);
INSERT  IGNORE INTO `orders` VALUES (1397,'order_created','parcel (S)','courier','parcel','courier',3,14,'2026-01-28 15:50:17','2025-12-25 15:28:14',1001,NULL);
INSERT  IGNORE INTO `orders` VALUES (1398,'order_courier_has_parcel','parcel (L)','self','parcel','courier',8,18,'2026-01-28 15:50:10','2025-12-26 12:26:22',1002,NULL);
INSERT  IGNORE INTO `orders` VALUES (1399,'order_parcel_confirmed','documents (S)','self',NULL,'courier',41,44,'2025-12-26 13:29:22','2025-12-26 13:18:51',0,NULL);
INSERT  IGNORE INTO `orders` VALUES (1400,'order_created','documents (M)','self',NULL,'courier',43,45,'2025-12-26 13:38:37','2025-12-26 13:38:37',0,NULL);
INSERT  IGNORE INTO `orders` VALUES (1401,'order_cancelled','documents (M)','self',NULL,'courier',5,15,'2025-12-26 16:32:13','2025-12-26 16:14:32',0,NULL);
INSERT  IGNORE INTO `orders` VALUES (1402,'order_created','parcel (S)','self',NULL,'courier',42,11,'2026-01-28 15:50:10','2025-12-26 16:45:51',1002,NULL);
INSERT  IGNORE INTO `orders` VALUES (1403,'order_cancelled','parcel (S)','courier',NULL,'courier',1,12,'2026-01-28 15:50:17','2025-12-26 17:11:36',1001,NULL);
INSERT  IGNORE INTO `orders` VALUES (1404,'order_created','parcel (S)','courier',NULL,'courier',1,12,'2026-01-28 15:50:17','2025-12-27 15:09:30',1001,NULL);
INSERT  IGNORE INTO `orders` VALUES (1405,'order_created','parcel (S)','courier',NULL,'courier',2,13,'2026-01-28 15:50:17','2025-12-27 15:13:30',1001,NULL);
INSERT  IGNORE INTO `orders` VALUES (1406,'order_created','parcel (S)','courier',NULL,'courier',3,14,'2026-01-28 15:50:17','2025-12-28 15:09:47',1001,NULL);
INSERT  IGNORE INTO `orders` VALUES (1407,'order_cancelled','parcel (M)','courier',NULL,'courier',6,16,'2026-01-28 15:50:17','2025-12-29 06:58:01',1001,NULL);
INSERT  IGNORE INTO `orders` VALUES (1408,'order_created','parcel (S)','courier',NULL,'courier',41,44,'2026-01-28 15:50:17','2025-12-31 11:19:13',1001,NULL);
INSERT  IGNORE INTO `orders` VALUES (1409,'order_created','parcel (S)','courier',NULL,'courier',42,11,'2026-01-28 15:50:17','2026-01-01 13:22:51',1001,NULL);
INSERT  IGNORE INTO `orders` VALUES (1410,'order_created','parcel (S)','courier',NULL,'courier',1,12,'2026-01-28 15:50:17','2026-01-01 13:23:52',1001,NULL);
INSERT  IGNORE INTO `orders` VALUES (1411,'order_created','parcel (S)','courier',NULL,'courier',2,13,'2026-01-28 15:50:17','2026-01-02 10:48:17',1001,NULL);
INSERT  IGNORE INTO `orders` VALUES (1412,'order_created','parcel (S)','courier',NULL,'courier',3,14,'2026-01-28 15:50:17','2026-01-02 13:23:12',1001,NULL);
INSERT  IGNORE INTO `orders` VALUES (1413,'order_courier_failed','parcel (L)','courier',NULL,'courier',7,17,'2026-01-28 15:50:03','2026-01-06 15:00:17',1003,NULL);
INSERT  IGNORE INTO `orders` VALUES (1414,'order_created','parcel (S)','courier',NULL,'courier',41,44,'2026-01-28 15:50:17','2026-01-09 17:03:28',1001,NULL);
INSERT  IGNORE INTO `orders` VALUES (1415,'order_created','parcel (S)','courier',NULL,'courier',42,11,'2026-01-28 15:50:17','2026-01-09 18:09:15',1001,NULL);
INSERT  IGNORE INTO `orders` VALUES (1416,'order_created','parcel (S)','courier',NULL,'courier',1,12,'2026-01-28 15:50:17','2026-01-09 18:09:50',1001,NULL);
INSERT  IGNORE INTO `orders` VALUES (1417,'order_cancelled','parcel (S)','courier',NULL,'courier',2,13,'2026-01-28 15:50:17','2026-01-09 18:16:00',1001,NULL);
INSERT  IGNORE INTO `orders` VALUES (1418,'order_created','parcel (S)','courier',NULL,'courier',3,14,'2026-01-28 15:50:17','2026-01-09 18:17:30',1001,NULL);
INSERT  IGNORE INTO `orders` VALUES (1419,'order_created','parcel (M)','courier',NULL,'courier',43,45,'2026-01-28 15:50:10','2026-01-11 11:45:19',1002,NULL);
INSERT  IGNORE INTO `orders` VALUES (1420,'order_created','parcel (L)','courier',NULL,'courier',8,18,'2026-01-28 15:50:03','2026-01-11 12:34:54',1003,NULL);
INSERT  IGNORE INTO `orders` VALUES (1421,'order_cancelled','parcel (M)','courier',NULL,'courier',5,15,'2026-01-28 15:50:17','2026-01-11 12:40:09',1001,NULL);
INSERT  IGNORE INTO `orders` VALUES (1422,'order_cancelled','parcel (M)','courier',NULL,'courier',6,16,'2026-01-28 15:50:17','2026-01-11 14:14:42',1001,NULL);
INSERT  IGNORE INTO `orders` VALUES (1423,'order_created','parcel (S)','courier',NULL,'self',41,44,'2026-01-28 15:50:03','2026-01-12 12:13:23',1003,NULL);
INSERT  IGNORE INTO `orders` VALUES (1424,'order_created','parcel (S)','courier',NULL,'self',42,11,'2026-01-28 15:50:03','2026-01-12 14:47:09',1003,NULL);
INSERT  IGNORE INTO `orders` VALUES (1425,'order_cancelled','parcel (M)','courier',NULL,'self',43,45,'2026-01-28 15:50:03','2026-01-12 14:47:50',1003,NULL);
INSERT  IGNORE INTO `orders` VALUES (1426,'order_cancelled','parcel (M)','courier',NULL,'self',5,15,'2026-01-28 15:30:33','2026-01-12 14:49:28',1004,NULL);
INSERT  IGNORE INTO `orders` VALUES (1427,'order_created','parcel (S)','courier',NULL,'courier',1,12,'2026-01-28 15:50:10','2026-01-12 15:50:04',1002,NULL);
INSERT  IGNORE INTO `orders` VALUES (1428,'order_cancelled','parcel (S)','courier',NULL,'courier',2,13,'2026-01-28 15:50:10','2026-01-12 15:50:39',1002,NULL);
INSERT  IGNORE INTO `orders` VALUES (1429,'order_cancelled','parcel (S)','courier',NULL,'courier',3,14,'2026-01-28 15:30:33','2026-01-12 15:52:49',1004,NULL);
INSERT  IGNORE INTO `orders` VALUES (1431,'order_created','parcel (L)','courier',NULL,'courier',7,17,'2026-01-28 15:50:03','2026-01-13 11:40:52',1003,NULL);
INSERT  IGNORE INTO `orders` VALUES (1432,'order_created','parcel (M)','courier',NULL,'courier',6,16,'2026-01-28 15:50:03','2026-01-13 12:42:27',1003,NULL);
INSERT  IGNORE INTO `orders` VALUES (1433,'order_created','parcel (S)','courier',NULL,'courier',2,13,'2026-01-28 15:50:03','2026-01-13 14:16:28',1003,NULL);
INSERT  IGNORE INTO `orders` VALUES (1434,'order_created','parcel (S)','courier',NULL,'courier',3,14,'2026-01-28 15:50:03','2026-01-13 15:24:59',1003,NULL);
INSERT  IGNORE INTO `orders` VALUES (1435,'order_cancelled','parcel (M)','courier',NULL,'courier',43,45,'2026-01-28 15:50:03','2026-01-13 15:25:01',1003,NULL);
INSERT  IGNORE INTO `orders` VALUES (1436,'order_cancelled','parcel (P)','courier',NULL,'courier',9,19,'2026-01-28 15:30:33','2026-01-13 15:53:23',1004,NULL);
INSERT  IGNORE INTO `orders` VALUES (1437,'order_cancelled','letter (P)','courier',NULL,'courier',9,19,'2026-01-28 15:30:33','2026-01-15 07:50:55',1004,NULL);
INSERT  IGNORE INTO `orders` VALUES (1438,'order_cancelled','parcel (M)','courier',NULL,'courier',5,15,'2026-01-28 15:50:17','2026-01-15 08:01:11',1001,NULL);
INSERT  IGNORE INTO `orders` VALUES (1439,'order_created','letter (P)','courier',NULL,'courier',9,19,'2026-01-28 15:50:17','2026-01-15 10:28:36',1001,NULL);
INSERT  IGNORE INTO `orders` VALUES (1440,'order_created','parcel (P)','courier',NULL,'courier',10,20,'2026-01-28 15:30:33','2026-01-15 12:46:48',1004,NULL);
INSERT  IGNORE INTO `orders` VALUES (1441,'order_created','parcel (L)','courier',NULL,'courier',8,18,'2026-01-28 15:30:33','2026-01-15 12:50:53',1004,NULL);
INSERT  IGNORE INTO `orders` VALUES (1442,'order_created','parcel (M)','courier',NULL,'courier',43,45,'2026-01-28 15:49:35','2026-01-15 20:52:14',1005,NULL);
INSERT  IGNORE INTO `orders` VALUES (1443,'order_created','parcel (S)','courier',NULL,'courier',2,13,'2026-01-28 15:50:03','2026-01-27 14:17:24',1003,NULL);
INSERT  IGNORE INTO `orders` VALUES (1444,'order_created','parcel (M)','courier',NULL,'courier',5,15,'2026-01-28 15:30:33','2026-01-27 14:21:05',1004,NULL);
INSERT  IGNORE INTO `orders` VALUES (1445,'order_created','parcel (M)','courier',NULL,'courier',6,16,'2026-01-28 09:49:34','2026-01-28 09:49:34',1004,NULL);
INSERT  IGNORE INTO `orders` VALUES (1446,'order_cancelled','parcel (M)','courier',NULL,'courier',43,45,'2026-01-28 15:12:59','2026-01-28 11:48:06',1004,NULL);
INSERT  IGNORE INTO `orders` VALUES (1447,'order_cancelled','parcel (S)','self',NULL,'courier',41,44,'2026-01-28 15:12:44','2026-01-28 14:55:23',1005,NULL);
INSERT  IGNORE INTO `orders` VALUES (1448,'order_created','parcel (S)','self',NULL,'self',41,44,'2026-01-29 08:12:40','2026-01-29 08:12:40',1005,NULL);
INSERT  IGNORE INTO `orders` VALUES (1449,'order_created','parcel (S)','self',NULL,'self',42,11,'2026-02-04 15:52:58','2026-02-04 15:52:58',1004,NULL);
INSERT  IGNORE INTO `orders` VALUES (1502,'order_parcel_confirmed','parcel (M)','self',NULL,'courier',43,45,'2026-04-01 09:33:15','2026-02-05 07:58:29',1004,NULL);
INSERT  IGNORE INTO `orders` VALUES (1503,'order_cancelled','parcel (S)','courier',NULL,'courier',1,12,'2026-02-05 08:25:26','2026-02-05 08:00:39',1004,NULL);
INSERT  IGNORE INTO `orders` VALUES (1504,'order_created','parsel (M)','self',NULL,'self',5,15,'2026-02-05 09:06:17','2026-02-05 09:06:17',1005,NULL);
INSERT  IGNORE INTO `orders` VALUES (1505,'order_created','parcel (S)','courier',NULL,'courier',1,12,'2026-02-06 05:52:52','2026-02-06 05:52:52',1003,NULL);
INSERT  IGNORE INTO `orders` VALUES (1506,'order_parcel_confirmed','parcel (S)','courier',NULL,'courier',2,13,'2026-04-01 10:14:11','2026-02-06 05:53:12',1003,NULL);
INSERT  IGNORE INTO `orders` VALUES (1507,'order_courier1_assigned','parcel (S)','courier',NULL,'courier',3,14,'2026-02-13 13:21:22','2026-02-06 05:53:32',1003,NULL);
INSERT  IGNORE INTO `orders` VALUES (1508,'order_parcel_confirmed','parcel (M)','courier',NULL,'courier',16,6,'2026-04-01 10:13:56','2026-02-08 13:22:43',1004,NULL);
INSERT  IGNORE INTO `orders` VALUES (1509,'order_created','parcel (M)','self',NULL,'courier',35,25,'2026-02-10 15:14:05','2026-02-10 15:14:05',1005,NULL);
INSERT  IGNORE INTO `orders` VALUES (1510,'order_created','parcel (S)','self',NULL,'self',31,4,'2026-02-10 17:07:30','2026-02-10 17:07:30',1005,2001);
INSERT  IGNORE INTO `orders` VALUES (1511,'order_created','parcel (S)','self',NULL,'courier',11,1,'2026-02-14 13:39:19','2026-02-14 13:39:19',1005,2001);
INSERT  IGNORE INTO `orders` VALUES (1512,'order_created','parcel (S)','self',NULL,'courier',12,42,'2026-02-14 13:41:06','2026-02-14 13:41:06',1005,2001);
INSERT  IGNORE INTO `orders` VALUES (1513,'order_parcel_confirmed','parcel (M)','self',NULL,'courier',15,5,'2026-02-16 09:00:24','2026-02-14 14:13:47',1005,2001);
INSERT  IGNORE INTO `orders` VALUES (1514,'order_created','parcel (S)','courier',NULL,'courier',21,32,'2026-02-16 11:35:02','2026-02-16 11:35:02',1001,2001);
INSERT  IGNORE INTO `orders` VALUES (1515,'order_parcel_confirmed','parcel (L)','courier',NULL,'courier',17,7,'2026-02-17 09:47:28','2026-02-17 09:39:07',1005,2001);
INSERT  IGNORE INTO `orders` VALUES (1516,'order_manual_intervention_required','parcel (L)','courier',NULL,'courier',18,8,'2026-02-24 14:40:52','2026-02-17 14:24:51',1004,2001);
INSERT  IGNORE INTO `orders` VALUES (1517,'order_in_transit_to_post2','parcel (S)','courier',NULL,'courier',33,22,'2026-02-20 14:51:32','2026-02-17 14:25:06',1004,2001);
INSERT  IGNORE INTO `orders` VALUES (1518,'order_in_transit_to_post2','parcel (M)','courier',NULL,'courier',36,26,'2026-02-20 14:51:32','2026-02-17 14:44:22',1004,2001);
INSERT  IGNORE INTO `orders` VALUES (1519,'order_in_transit_to_post2','parcel (P)','courier',NULL,'courier',19,9,'2026-02-25 07:27:34','2026-02-17 14:50:52',1004,2002);
INSERT  IGNORE INTO `orders` VALUES (1520,'order_in_transit_to_post2','parcel (P)','courier',NULL,'courier',20,10,'2026-02-25 07:27:34','2026-02-17 14:51:07',1004,2002);
INSERT  IGNORE INTO `orders` VALUES (1521,'order_in_transit_to_post2','parcel (P)','courier',NULL,'courier',39,29,'2026-02-20 14:51:32','2026-02-17 15:07:33',1004,2002);
INSERT  IGNORE INTO `orders` VALUES (1522,'order_in_transit_to_post2','parcel (P)','courier',NULL,'courier',40,30,'2026-02-20 14:51:32','2026-02-17 15:07:33',1004,2002);
INSERT  IGNORE INTO `orders` VALUES (1523,'order_in_transit_to_post2','parcel (S)','courier',NULL,'courier',34,23,'2026-02-20 14:51:32','2026-02-17 15:12:56',1004,2002);
INSERT  IGNORE INTO `orders` VALUES (1524,'order_parcel_confirmed','parcel (L)','courier',NULL,'courier',37,27,'2026-02-17 18:08:13','2026-02-17 18:05:53',1004,2002);
INSERT  IGNORE INTO `orders` VALUES (1525,'order_completed','parcel (L)','courier',NULL,'courier',28,38,'2026-02-28 07:42:17','2026-02-25 10:16:17',1002,2004);
INSERT  IGNORE INTO `orders` VALUES (1526,'order_created','parcel (S)','self',NULL,'self',1,11,'2026-03-02 09:03:01','2026-03-02 09:03:01',1001,2004);
INSERT  IGNORE INTO `orders` VALUES (1527,'order_parcel_confirmed_post2','parcel (M)','self',NULL,'self',5,15,'2026-03-19 14:07:28','2026-03-15 13:26:16',1001,2004);
INSERT  IGNORE INTO `orders` VALUES (1528,'order_in_transit_to_post2','parcel (M)','self',NULL,'self',6,16,'2026-03-23 17:19:46','2026-03-15 13:44:12',1001,2004);
INSERT  IGNORE INTO `orders` VALUES (1529,'order_created','letter (P)','courier',NULL,'courier',9,19,'2026-03-19 14:37:24','2026-03-16 08:43:25',1001,2004);
INSERT  IGNORE INTO `orders` VALUES (1530,'order_cancelled','letter (P)','courier',NULL,'courier',10,20,'2026-03-19 07:43:40','2026-03-19 07:24:40',1001,2004);
INSERT  IGNORE INTO `orders` VALUES (1531,'order_in_transit_to_post2','letter (P)','courier',NULL,'courier',10,20,'2026-04-01 09:59:14','2026-03-19 07:44:10',1001,2004);
INSERT  IGNORE INTO `orders` VALUES (1532,'order_created','letter (P)','courier',NULL,'courier',29,39,'2026-03-19 07:55:11','2026-03-19 07:55:11',1002,2004);
INSERT  IGNORE INTO `orders` VALUES (1533,'order_created','letter (P)','courier',NULL,'courier',30,40,'2026-03-19 08:02:36','2026-03-19 08:02:36',1002,2004);
INSERT  IGNORE INTO `orders` VALUES (1534,'order_picked_up_from_post1','parcel (M)','self',NULL,'self',45,43,'2026-03-25 10:13:22','2026-03-22 09:43:59',1004,2001);
INSERT  IGNORE INTO `orders` VALUES (1535,'order_courier1_assigned','parcel (S)','courier',NULL,'courier',2,12,'2026-04-04 17:26:36','2026-03-28 12:07:59',1002,2004);
INSERT  IGNORE INTO `orders` VALUES (1536,'order_courier2_parcel_delivered','parcel (S)','courier',NULL,'courier',3,13,'2026-03-30 17:19:29','2026-03-30 13:40:39',1002,2004);
INSERT  IGNORE INTO `orders` VALUES (1537,'order_cancelled','parcel (M)','self',NULL,'self',45,5,'2026-03-31 08:54:49','2026-03-31 08:54:24',1004,2001);
INSERT  IGNORE INTO `orders` VALUES (1538,'order_created','parcel (M)','courier',NULL,'courier',45,5,'2026-03-31 09:00:10','2026-03-31 08:58:05',1004,2001);
INSERT  IGNORE INTO `orders` VALUES (1539,'order_cancelled','parcel (S)','courier',NULL,'courier',13,3,'2026-04-08 11:47:23','2026-04-08 09:26:10',1000013,2001);
INSERT  IGNORE INTO `orders` VALUES (1540,'order_cancelled','parcel (S)','self',NULL,'self',13,3,'2026-04-08 13:01:40','2026-04-08 12:57:55',1000013,2002);
INSERT  IGNORE INTO `orders` VALUES (1541,'order_created','parcel (S)','courier',NULL,'courier',13,3,'2026-04-08 13:05:06','2026-04-08 13:05:06',1000013,2002);
/*!50003 SET @saved_cs_client      = @@character_set_client */ ;
/*!50003 SET @saved_cs_results     = @@character_set_results */ ;
/*!50003 SET @saved_col_connection = @@collation_connection */ ;
/*!50003 SET character_set_client  = utf8mb4 */ ;
/*!50003 SET character_set_results = utf8mb4 */ ;
/*!50003 SET collation_connection  = utf8mb4_0900_ai_ci */ ;
/*!50003 SET @saved_sql_mode       = @@sql_mode */ ;
/*!50003 SET sql_mode              = 'ONLY_FULL_GROUP_BY,STRICT_TRANS_TABLES,NO_ZERO_IN_DATE,NO_ZERO_DATE,ERROR_FOR_DIVISION_BY_ZERO,NO_ENGINE_SUBSTITUTION' */ ;
DELIMITER ;;
/*!50003 CREATE*/ /*!50017 DEFINER=`fsm`@`localhost`*/ /*!50003 TRIGGER `trg_order_status_check` BEFORE UPDATE ON `orders` FOR EACH ROW BEGIN
    IF NEW.status NOT IN (SELECT name FROM fsm_states) THEN
        SIGNAL SQLSTATE '45000'
        SET MESSAGE_TEXT = 'Invalid order status: not in fsm_states';
    END IF;
END */;;
DELIMITER ;
/*!50003 SET sql_mode              = @saved_sql_mode */ ;
/*!50003 SET character_set_client  = @saved_cs_client */ ;
/*!50003 SET character_set_results = @saved_cs_results */ ;
/*!50003 SET collation_connection  = @saved_col_connection */ ;
/*!50003 SET @saved_cs_client      = @@character_set_client */ ;
/*!50003 SET @saved_cs_results     = @@character_set_results */ ;
/*!50003 SET @saved_col_connection = @@collation_connection */ ;
/*!50003 SET character_set_client  = utf8mb4 */ ;
/*!50003 SET character_set_results = utf8mb4 */ ;
/*!50003 SET collation_connection  = utf8mb4_0900_ai_ci */ ;
/*!50003 SET @saved_sql_mode       = @@sql_mode */ ;
/*!50003 SET sql_mode              = 'ONLY_FULL_GROUP_BY,STRICT_TRANS_TABLES,NO_ZERO_IN_DATE,NO_ZERO_DATE,ERROR_FOR_DIVISION_BY_ZERO,NO_ENGINE_SUBSTITUTION' */ ;
DELIMITER ;;
/*!50003 CREATE*/ /*!50017 DEFINER=`fsm`@`localhost`*/ /*!50003 TRIGGER `trg_order_courier_assignment_check` AFTER UPDATE ON `orders` FOR EACH ROW BEGIN
    DECLARE has_courier1 INT DEFAULT 0;
    DECLARE has_courier2 INT DEFAULT 0;

    -- Проверка для order_courier1_assigned
    IF NEW.status = 'order_courier1_assigned'
       AND OLD.status <> 'order_courier1_assigned' THEN

        SELECT COUNT(*)
        INTO has_courier1
        FROM stage_orders so
        WHERE so.order_id = NEW.id
          AND so.leg = 'pickup'
          AND so.courier_user_id IS NOT NULL;

        IF has_courier1 = 0 THEN
            SIGNAL SQLSTATE '45000'
            SET MESSAGE_TEXT =
                'Transition to order_courier1_assigned requires pickup courier in stage_orders';
        END IF;
    END IF;

    -- Проверка для order_courier2_assigned
    IF NEW.status = 'order_courier2_assigned'
       AND OLD.status <> 'order_courier2_assigned' THEN

        SELECT COUNT(*)
        INTO has_courier2
        FROM stage_orders so
        WHERE so.order_id = NEW.id
          AND so.leg = 'delivery'
          AND so.courier_user_id IS NOT NULL;

        IF has_courier2 = 0 THEN
            SIGNAL SQLSTATE '45000'
            SET MESSAGE_TEXT =
                'Transition to order_courier2_assigned requires delivery courier in stage_orders';
        END IF;
    END IF;
END */;;
DELIMITER ;
/*!50003 SET sql_mode              = @saved_sql_mode */ ;
/*!50003 SET character_set_client  = @saved_cs_client */ ;
/*!50003 SET character_set_results = @saved_cs_results */ ;
/*!50003 SET collation_connection  = @saved_col_connection */ ;

--
-- Table structure for table `report_issues`
--

DROP TABLE IF EXISTS `report_issues`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `report_issues` (
  `id` int NOT NULL AUTO_INCREMENT,
  `order_id` int DEFAULT NULL,
  `trip_id` int DEFAULT NULL,
  `user_id` int NOT NULL,
  `user_role` varchar(50) DEFAULT NULL,
  `issue_type` enum('locker_failed_to_open','locker_failed_to_close','locker_not_closed','parcel_missing','parcel_damaged','wrong_parcel','cancelled_by_client','trip_breakdown','trip_delayed','trip_route_issue','trip_manual_intervention','manual_override','other') DEFAULT NULL,
  `description` text,
  `created_at` datetime DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  KEY `user_id` (`user_id`),
  KEY `idx_order_id` (`order_id`),
  KEY `idx_trip_id` (`trip_id`),
  KEY `idx_issue_type` (`issue_type`),
  KEY `idx_created_at` (`created_at`),
  CONSTRAINT `report_issues_ibfk_1` FOREIGN KEY (`order_id`) REFERENCES `orders` (`id`) ON DELETE CASCADE,
  CONSTRAINT `report_issues_ibfk_2` FOREIGN KEY (`trip_id`) REFERENCES `trips` (`id`) ON DELETE SET NULL,
  CONSTRAINT `report_issues_ibfk_3` FOREIGN KEY (`user_id`) REFERENCES `users` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=7 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `report_issues`
--

INSERT  IGNORE INTO `report_issues` VALUES (1,1516,33,200,NULL,'locker_failed_to_open','Driver reported: locker_failed_to_open','2026-02-24 14:40:52');
INSERT  IGNORE INTO `report_issues` VALUES (3,NULL,34,200,NULL,'trip_breakdown','Driver reported: trip_breakdown','2026-02-24 16:16:13');
INSERT  IGNORE INTO `report_issues` VALUES (4,NULL,29,777,NULL,'manual_override','Водитель 200 снят с рейса оператором','2026-03-27 11:16:53');
INSERT  IGNORE INTO `report_issues` VALUES (5,5,NULL,777,NULL,'manual_override','Курьер 100 снят с заказа pickup оператором','2026-03-27 11:40:50');
INSERT  IGNORE INTO `report_issues` VALUES (6,NULL,30,777,NULL,'manual_override','Водитель 200 снят с рейса оператором','2026-04-04 14:57:53');

--
-- Table structure for table `server_fsm_instances`
--

DROP TABLE IF EXISTS `server_fsm_instances`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `server_fsm_instances` (
  `id` int NOT NULL AUTO_INCREMENT,
  `entity_type` varchar(50) NOT NULL,
  `entity_id` int NOT NULL,
  `process_name` varchar(100) NOT NULL,
  `fsm_state` varchar(100) NOT NULL,
  `next_timer_at` datetime DEFAULT NULL,
  `attempts_count` int NOT NULL DEFAULT '0',
  `last_error` text,
  `created_at` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `updated_at` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  `requested_by_user_id` int DEFAULT NULL,
  `requested_user_role` varchar(50) DEFAULT NULL,
  `target_user_id` int DEFAULT NULL,
  `target_role` varchar(50) DEFAULT NULL,
  `metadata_json` json DEFAULT NULL COMMENT 'Дополнительные параметры процесса',
  PRIMARY KEY (`id`),
  UNIQUE KEY `ux_fsm_entity_process` (`entity_type`,`entity_id`,`process_name`),
  KEY `idx_fsm_process_state` (`process_name`,`fsm_state`),
  KEY `idx_fsm_next_timer` (`next_timer_at`),
  KEY `idx_fsm_requested_by` (`requested_by_user_id`),
  KEY `idx_fsm_target_user` (`target_user_id`)
) ENGINE=InnoDB AUTO_INCREMENT=1420 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `server_fsm_instances`
--

INSERT  IGNORE INTO `server_fsm_instances` VALUES (1,'order_request',1,'order_creation','FAILED',NULL,1,'NOT_IMPLEMENTED','2025-12-07 13:53:25','2025-12-07 14:17:02',NULL,NULL,NULL,NULL,NULL);
INSERT  IGNORE INTO `server_fsm_instances` VALUES (2,'order_request',2,'order_creation','FAILED',NULL,1,'NO_FREE_CELLS','2025-12-07 16:37:12','2025-12-07 16:38:43',NULL,NULL,NULL,NULL,NULL);
INSERT  IGNORE INTO `server_fsm_instances` VALUES (3,'order_request',3,'order_creation','COMPLETED',NULL,1,NULL,'2025-12-07 16:45:30','2025-12-07 17:02:57',NULL,NULL,NULL,NULL,NULL);
INSERT  IGNORE INTO `server_fsm_instances` VALUES (4,'order_request',4,'order_creation','COMPLETED',NULL,1,NULL,'2025-12-07 16:54:49','2025-12-07 17:02:58',NULL,NULL,NULL,NULL,NULL);
INSERT  IGNORE INTO `server_fsm_instances` VALUES (5,'order_request',5,'order_creation','COMPLETED',NULL,1,NULL,'2025-12-07 17:08:22','2025-12-07 17:17:06',NULL,NULL,NULL,NULL,NULL);
INSERT  IGNORE INTO `server_fsm_instances` VALUES (6,'order_request',6,'order_creation','COMPLETED',NULL,1,NULL,'2025-12-07 17:17:26','2025-12-07 17:18:55',NULL,NULL,NULL,NULL,NULL);
INSERT  IGNORE INTO `server_fsm_instances` VALUES (7,'order_request',7,'order_creation','COMPLETED',NULL,1,NULL,'2025-12-07 17:19:20','2025-12-07 17:19:25',NULL,NULL,NULL,NULL,NULL);
INSERT  IGNORE INTO `server_fsm_instances` VALUES (8,'order_request',8,'order_creation','FAILED',NULL,1,'NO_FREE_CELLS','2025-12-11 09:43:29','2025-12-11 09:43:34',NULL,NULL,NULL,NULL,NULL);
INSERT  IGNORE INTO `server_fsm_instances` VALUES (9,'order_request',9,'order_creation','COMPLETED',NULL,1,NULL,'2025-12-12 08:32:33','2025-12-12 09:26:46',NULL,NULL,NULL,NULL,NULL);
INSERT  IGNORE INTO `server_fsm_instances` VALUES (10,'order_request',10,'order_creation','FAILED',NULL,1,'NO_FREE_CELLS','2025-12-12 09:38:45','2025-12-12 09:38:46',NULL,NULL,NULL,NULL,NULL);
INSERT  IGNORE INTO `server_fsm_instances` VALUES (11,'order_request',11,'order_creation','FAILED',NULL,1,'NO_FREE_CELLS','2025-12-12 09:39:44','2025-12-12 09:39:46',NULL,NULL,NULL,NULL,NULL);
INSERT  IGNORE INTO `server_fsm_instances` VALUES (12,'order_request',12,'order_creation','FAILED',NULL,1,'NO_FREE_CELLS','2025-12-12 09:46:20','2025-12-12 09:46:21',NULL,NULL,NULL,NULL,NULL);
INSERT  IGNORE INTO `server_fsm_instances` VALUES (13,'order_request',13,'order_creation','COMPLETED',NULL,1,NULL,'2025-12-12 09:55:53','2025-12-12 09:55:55',NULL,NULL,NULL,NULL,NULL);
INSERT  IGNORE INTO `server_fsm_instances` VALUES (14,'order_request',14,'order_creation','FAILED',NULL,1,'NO_FREE_CELLS','2025-12-12 10:16:43','2025-12-12 10:16:46',NULL,NULL,NULL,NULL,NULL);
INSERT  IGNORE INTO `server_fsm_instances` VALUES (15,'order_request',15,'order_creation','COMPLETED',NULL,1,NULL,'2025-12-12 10:50:14','2025-12-12 10:50:17',NULL,NULL,NULL,NULL,NULL);
INSERT  IGNORE INTO `server_fsm_instances` VALUES (16,'order_request',16,'order_creation','FAILED',NULL,1,'NO_FREE_CELLS','2025-12-12 12:40:43','2025-12-12 12:40:48',NULL,NULL,NULL,NULL,NULL);
INSERT  IGNORE INTO `server_fsm_instances` VALUES (17,'order_request',17,'order_creation','FAILED',NULL,1,'NO_FREE_CELLS','2025-12-12 13:32:58','2025-12-12 13:33:00',NULL,NULL,NULL,NULL,NULL);
INSERT  IGNORE INTO `server_fsm_instances` VALUES (18,'order_request',18,'order_creation','FAILED',NULL,1,'NO_FREE_CELLS','2025-12-12 14:22:45','2025-12-12 14:22:48',NULL,NULL,NULL,NULL,NULL);
INSERT  IGNORE INTO `server_fsm_instances` VALUES (19,'order_request',19,'order_creation','FAILED',NULL,1,'NO_FREE_CELLS','2025-12-12 16:06:43','2025-12-12 16:11:51',NULL,NULL,NULL,NULL,NULL);
INSERT  IGNORE INTO `server_fsm_instances` VALUES (20,'order_request',20,'order_creation','FAILED',NULL,1,'NO_FREE_CELLS','2025-12-12 16:21:18','2025-12-12 16:21:22',NULL,NULL,NULL,NULL,NULL);
INSERT  IGNORE INTO `server_fsm_instances` VALUES (21,'order',1,'order_assign_courier1','FAILED',NULL,1,'ASSIGNMENT_FAILED','2025-12-15 07:42:38','2025-12-15 16:40:04',1,'driver',2,'courier',NULL);
INSERT  IGNORE INTO `server_fsm_instances` VALUES (24,'order',6,'order_assign_courier1','FAILED',NULL,1,'ASSIGNMENT_FAILED','2025-12-15 16:49:32','2026-01-23 09:58:03',100,'courier',100,NULL,NULL);
INSERT  IGNORE INTO `server_fsm_instances` VALUES (26,'order_request',21,'order_creation','COMPLETED',NULL,1,NULL,'2025-12-15 17:31:35','2025-12-15 18:43:45',NULL,NULL,NULL,NULL,NULL);
INSERT  IGNORE INTO `server_fsm_instances` VALUES (27,'order',1361,'order_assign_courier1','FAILED',NULL,1,'ASSIGNMENT_FAILED','2025-12-15 18:47:30','2025-12-15 18:47:35',1,'driver',2,'courier',NULL);
INSERT  IGNORE INTO `server_fsm_instances` VALUES (28,'order_request',22,'order_creation','COMPLETED',NULL,1,NULL,'2025-12-15 19:20:40','2025-12-15 19:20:44',NULL,NULL,NULL,NULL,NULL);
INSERT  IGNORE INTO `server_fsm_instances` VALUES (29,'order',1362,'order_assign_courier1','COMPLETED',NULL,1,NULL,'2025-12-15 19:24:05','2025-12-15 19:24:09',1,'driver',2,'courier',NULL);
INSERT  IGNORE INTO `server_fsm_instances` VALUES (32,'order_request',25,'order_creation','FAILED',NULL,1,'NO_FREE_CELLS','2025-12-15 19:50:38','2025-12-15 19:50:42',NULL,NULL,NULL,NULL,NULL);
INSERT  IGNORE INTO `server_fsm_instances` VALUES (33,'order_request',26,'order_creation','FAILED',NULL,1,'NO_FREE_CELLS','2025-12-15 19:50:38','2025-12-15 19:50:42',NULL,NULL,NULL,NULL,NULL);
INSERT  IGNORE INTO `server_fsm_instances` VALUES (36,'order_request',29,'order_creation','COMPLETED',NULL,1,NULL,'2025-12-15 20:33:34','2025-12-15 20:33:36',NULL,NULL,NULL,NULL,NULL);
INSERT  IGNORE INTO `server_fsm_instances` VALUES (37,'order_request',30,'order_creation','COMPLETED',NULL,1,NULL,'2025-12-15 20:33:34','2025-12-15 20:33:36',NULL,NULL,NULL,NULL,NULL);
INSERT  IGNORE INTO `server_fsm_instances` VALUES (38,'order_request',31,'order_creation','COMPLETED',NULL,1,NULL,'2025-12-15 20:46:10','2025-12-15 20:46:12',NULL,NULL,NULL,NULL,NULL);
INSERT  IGNORE INTO `server_fsm_instances` VALUES (39,'order_request',32,'order_creation','COMPLETED',NULL,1,NULL,'2025-12-16 06:00:45','2025-12-16 06:00:46',NULL,NULL,NULL,NULL,NULL);
INSERT  IGNORE INTO `server_fsm_instances` VALUES (40,'order_request',33,'order_creation','COMPLETED',NULL,1,NULL,'2025-12-16 06:04:57','2025-12-16 06:05:01',NULL,NULL,NULL,NULL,NULL);
INSERT  IGNORE INTO `server_fsm_instances` VALUES (41,'order_request',35,'order_creation','COMPLETED',NULL,1,NULL,'2025-12-16 06:49:59','2025-12-16 06:50:03',NULL,NULL,NULL,NULL,NULL);
INSERT  IGNORE INTO `server_fsm_instances` VALUES (42,'order_request',36,'order_creation','COMPLETED',NULL,1,NULL,'2025-12-16 06:49:59','2025-12-16 06:50:04',NULL,NULL,NULL,NULL,NULL);
INSERT  IGNORE INTO `server_fsm_instances` VALUES (43,'order_request',37,'order_creation','COMPLETED',NULL,1,NULL,'2025-12-16 06:49:59','2025-12-16 06:50:04',NULL,NULL,NULL,NULL,NULL);
INSERT  IGNORE INTO `server_fsm_instances` VALUES (44,'order_request',38,'order_creation','FAILED',NULL,1,'NO_FREE_CELLS','2025-12-16 06:49:59','2025-12-16 06:50:04',NULL,NULL,NULL,NULL,NULL);
INSERT  IGNORE INTO `server_fsm_instances` VALUES (45,'order_request',39,'order_creation','FAILED',NULL,1,'ORDER_REQUEST_NOT_FOUND','2025-12-16 06:49:59','2025-12-16 06:50:04',NULL,NULL,NULL,NULL,NULL);
INSERT  IGNORE INTO `server_fsm_instances` VALUES (46,'order',1373,'order_assign_courier1','COMPLETED',NULL,1,NULL,'2025-12-16 07:21:59','2025-12-16 07:22:00',1,'driver',2,'courier',NULL);
INSERT  IGNORE INTO `server_fsm_instances` VALUES (51,'order_request',41,'order_creation','COMPLETED',NULL,1,NULL,'2025-12-16 10:03:17','2025-12-16 10:03:20',NULL,NULL,NULL,NULL,NULL);
INSERT  IGNORE INTO `server_fsm_instances` VALUES (52,'order_request',42,'order_creation','COMPLETED',NULL,1,NULL,'2025-12-16 10:03:17','2025-12-16 10:03:20',NULL,NULL,NULL,NULL,NULL);
INSERT  IGNORE INTO `server_fsm_instances` VALUES (53,'locker',1,'locker_cell_session','COMPLETED',NULL,3,NULL,'2025-12-18 16:26:36','2025-12-18 16:44:21',2,'courier',0,'string',NULL);
INSERT  IGNORE INTO `server_fsm_instances` VALUES (55,'order_request',43,'order_creation','COMPLETED',NULL,1,NULL,'2025-12-19 09:45:06','2025-12-19 09:45:10',NULL,NULL,NULL,NULL,NULL);
INSERT  IGNORE INTO `server_fsm_instances` VALUES (56,'order_request',44,'order_creation','COMPLETED',NULL,1,NULL,'2025-12-19 09:53:15','2025-12-19 09:56:26',NULL,NULL,NULL,NULL,NULL);
INSERT  IGNORE INTO `server_fsm_instances` VALUES (57,'order',1378,'order_assign_courier1','COMPLETED',NULL,1,NULL,'2025-12-19 10:05:28','2025-12-19 10:05:32',1,'driver',2,NULL,NULL);
INSERT  IGNORE INTO `server_fsm_instances` VALUES (58,'order',1378,'courier_open_cell','FAILED',NULL,1,'FSM locker_open_locker: 1644 (45000): Invalid transition for locker: no matching fsm_transitions','2025-12-19 10:21:23','2025-12-19 11:40:25',2,'courier',NULL,NULL,NULL);
INSERT  IGNORE INTO `server_fsm_instances` VALUES (61,'order',1378,'courier_close_cell','COMPLETED',NULL,1,NULL,'2025-12-19 11:46:06','2025-12-19 11:46:06',2,'courier',NULL,NULL,NULL);
INSERT  IGNORE INTO `server_fsm_instances` VALUES (62,'order_request',45,'order_creation','COMPLETED',NULL,1,NULL,'2025-12-19 12:04:27','2025-12-19 12:04:31',NULL,NULL,NULL,NULL,NULL);
INSERT  IGNORE INTO `server_fsm_instances` VALUES (63,'order',1379,'order_assign_courier1','COMPLETED',NULL,1,NULL,'2025-12-19 12:33:56','2025-12-19 12:48:22',2,'courier',2,'courier',NULL);
INSERT  IGNORE INTO `server_fsm_instances` VALUES (66,'order',1379,'courier_open_cell','COMPLETED',NULL,1,NULL,'2025-12-19 12:59:26','2025-12-19 12:59:28',2,'courier',NULL,NULL,NULL);
INSERT  IGNORE INTO `server_fsm_instances` VALUES (67,'order_request',46,'order_creation','COMPLETED',NULL,1,NULL,'2025-12-23 16:35:09','2025-12-23 16:35:14',NULL,NULL,NULL,NULL,NULL);
INSERT  IGNORE INTO `server_fsm_instances` VALUES (68,'order_request',47,'order_creation','COMPLETED',NULL,1,NULL,'2025-12-24 11:50:30','2025-12-24 11:50:31',NULL,NULL,NULL,NULL,NULL);
INSERT  IGNORE INTO `server_fsm_instances` VALUES (69,'order_request',48,'order_creation','COMPLETED',NULL,1,NULL,'2025-12-24 11:52:18','2025-12-24 11:52:21',NULL,NULL,NULL,NULL,NULL);
INSERT  IGNORE INTO `server_fsm_instances` VALUES (70,'order_request',49,'order_creation','COMPLETED',NULL,1,NULL,'2025-12-24 11:54:15','2025-12-24 11:54:17',NULL,NULL,NULL,NULL,NULL);
INSERT  IGNORE INTO `server_fsm_instances` VALUES (71,'order_request',50,'order_creation','FAILED',NULL,1,'NO_FREE_CELLS','2025-12-24 12:00:31','2025-12-24 12:00:32',NULL,NULL,NULL,NULL,NULL);
INSERT  IGNORE INTO `server_fsm_instances` VALUES (72,'order_request',51,'order_creation','COMPLETED',NULL,1,NULL,'2025-12-24 12:04:50','2025-12-24 12:04:52',NULL,NULL,NULL,NULL,NULL);
INSERT  IGNORE INTO `server_fsm_instances` VALUES (73,'order_request',52,'order_creation','COMPLETED',NULL,1,NULL,'2025-12-24 12:05:22','2025-12-24 12:05:22',NULL,NULL,NULL,NULL,NULL);
INSERT  IGNORE INTO `server_fsm_instances` VALUES (74,'order_request',53,'order_creation','FAILED',NULL,1,'NO_FREE_CELLS','2025-12-24 12:21:46','2025-12-24 12:21:48',NULL,NULL,NULL,NULL,NULL);
INSERT  IGNORE INTO `server_fsm_instances` VALUES (75,'order_request',54,'order_creation','FAILED',NULL,1,'NO_FREE_CELLS','2025-12-24 12:24:07','2025-12-24 12:24:08',NULL,NULL,NULL,NULL,NULL);
INSERT  IGNORE INTO `server_fsm_instances` VALUES (76,'order_request',55,'order_creation','COMPLETED',NULL,1,NULL,'2025-12-24 12:24:20','2025-12-24 12:24:23',NULL,NULL,NULL,NULL,NULL);
INSERT  IGNORE INTO `server_fsm_instances` VALUES (77,'order_request',56,'order_creation','FAILED',NULL,1,'NO_FREE_CELLS','2025-12-24 12:31:53','2025-12-24 12:31:58',NULL,NULL,NULL,NULL,NULL);
INSERT  IGNORE INTO `server_fsm_instances` VALUES (78,'order_request',57,'order_creation','FAILED',NULL,1,'NO_FREE_CELLS','2025-12-24 12:32:29','2025-12-24 12:32:33',NULL,NULL,NULL,NULL,NULL);
INSERT  IGNORE INTO `server_fsm_instances` VALUES (79,'order_request',58,'order_creation','FAILED',NULL,1,'NO_FREE_CELLS','2025-12-24 12:32:50','2025-12-24 12:32:53',NULL,NULL,NULL,NULL,NULL);
INSERT  IGNORE INTO `server_fsm_instances` VALUES (80,'order_request',59,'order_creation','FAILED',NULL,1,'NO_FREE_CELLS','2025-12-24 12:35:26','2025-12-24 12:35:28',NULL,NULL,NULL,NULL,NULL);
INSERT  IGNORE INTO `server_fsm_instances` VALUES (81,'order_request',60,'order_creation','COMPLETED',NULL,1,NULL,'2025-12-24 12:35:33','2025-12-24 12:35:38',NULL,NULL,NULL,NULL,NULL);
INSERT  IGNORE INTO `server_fsm_instances` VALUES (82,'order_request',61,'order_creation','FAILED',NULL,1,'NO_FREE_CELLS','2025-12-24 12:37:24','2025-12-24 12:37:28',NULL,NULL,NULL,NULL,NULL);
INSERT  IGNORE INTO `server_fsm_instances` VALUES (83,'order_request',62,'order_creation','FAILED',NULL,1,'NO_FREE_CELLS','2025-12-24 12:37:39','2025-12-24 12:37:43',NULL,NULL,NULL,NULL,NULL);
INSERT  IGNORE INTO `server_fsm_instances` VALUES (84,'order_request',63,'order_creation','FAILED',NULL,1,'NO_FREE_CELLS','2025-12-24 12:37:53','2025-12-24 12:37:53',NULL,NULL,NULL,NULL,NULL);
INSERT  IGNORE INTO `server_fsm_instances` VALUES (85,'order_request',64,'order_creation','FAILED',NULL,1,'NO_FREE_CELLS','2025-12-24 12:44:17','2025-12-24 12:44:18',NULL,NULL,NULL,NULL,NULL);
INSERT  IGNORE INTO `server_fsm_instances` VALUES (86,'order_request',65,'order_creation','FAILED',NULL,1,'NO_FREE_CELLS','2025-12-24 12:50:17','2025-12-24 12:50:19',NULL,NULL,NULL,NULL,NULL);
INSERT  IGNORE INTO `server_fsm_instances` VALUES (87,'order_request',66,'order_creation','COMPLETED',NULL,1,NULL,'2025-12-24 12:53:55','2025-12-24 12:53:59',NULL,NULL,NULL,NULL,NULL);
INSERT  IGNORE INTO `server_fsm_instances` VALUES (88,'order_request',67,'order_creation','FAILED',NULL,1,'NO_FREE_CELLS','2025-12-24 14:27:35','2025-12-24 14:27:37',NULL,NULL,NULL,NULL,NULL);
INSERT  IGNORE INTO `server_fsm_instances` VALUES (89,'order_request',68,'order_creation','COMPLETED',NULL,1,NULL,'2025-12-24 15:36:48','2025-12-24 15:36:49',NULL,NULL,NULL,NULL,NULL);
INSERT  IGNORE INTO `server_fsm_instances` VALUES (90,'order_request',69,'order_creation','COMPLETED',NULL,1,NULL,'2025-12-24 15:40:47','2025-12-24 15:40:49',NULL,NULL,NULL,NULL,NULL);
INSERT  IGNORE INTO `server_fsm_instances` VALUES (91,'order_request',70,'order_creation','COMPLETED',NULL,1,NULL,'2025-12-24 15:40:59','2025-12-24 15:40:59',NULL,NULL,NULL,NULL,NULL);
INSERT  IGNORE INTO `server_fsm_instances` VALUES (92,'order_request',71,'order_creation','COMPLETED',NULL,1,NULL,'2025-12-24 15:42:42','2025-12-24 15:42:45',NULL,NULL,NULL,NULL,NULL);
INSERT  IGNORE INTO `server_fsm_instances` VALUES (93,'order_request',72,'order_creation','COMPLETED',NULL,1,NULL,'2025-12-25 15:18:01','2025-12-25 15:18:03',NULL,NULL,NULL,NULL,NULL);
INSERT  IGNORE INTO `server_fsm_instances` VALUES (94,'order_request',73,'order_creation','COMPLETED',NULL,1,NULL,'2025-12-25 15:20:26','2025-12-25 15:20:29',NULL,NULL,NULL,NULL,NULL);
INSERT  IGNORE INTO `server_fsm_instances` VALUES (95,'order_request',74,'order_creation','COMPLETED',NULL,1,NULL,'2025-12-25 15:23:40','2025-12-25 15:23:44',NULL,NULL,NULL,NULL,NULL);
INSERT  IGNORE INTO `server_fsm_instances` VALUES (96,'order_request',75,'order_creation','COMPLETED',NULL,1,NULL,'2025-12-25 15:26:12','2025-12-25 15:26:14',NULL,NULL,NULL,NULL,NULL);
INSERT  IGNORE INTO `server_fsm_instances` VALUES (97,'order_request',76,'order_creation','COMPLETED',NULL,1,NULL,'2025-12-25 15:28:13','2025-12-25 15:28:14',NULL,NULL,NULL,NULL,NULL);
INSERT  IGNORE INTO `server_fsm_instances` VALUES (98,'order_request',77,'order_creation','FAILED',NULL,1,'NO_FREE_CELLS','2025-12-26 10:11:33','2025-12-26 10:11:38',NULL,NULL,NULL,NULL,NULL);
INSERT  IGNORE INTO `server_fsm_instances` VALUES (99,'order_request',78,'order_creation','FAILED',NULL,1,'NO_FREE_CELLS','2025-12-26 10:14:03','2025-12-26 10:14:03',NULL,NULL,NULL,NULL,NULL);
INSERT  IGNORE INTO `server_fsm_instances` VALUES (100,'order_request',79,'order_creation','FAILED',NULL,1,'NO_FREE_CELLS','2025-12-26 10:34:33','2025-12-26 10:34:38',NULL,NULL,NULL,NULL,NULL);
INSERT  IGNORE INTO `server_fsm_instances` VALUES (101,'order_request',80,'order_creation','COMPLETED',NULL,1,NULL,'2025-12-26 12:26:18','2025-12-26 12:26:22',NULL,NULL,NULL,NULL,NULL);
INSERT  IGNORE INTO `server_fsm_instances` VALUES (102,'order',1398,'order_assign_courier1','COMPLETED',NULL,1,NULL,'2025-12-26 12:53:32','2025-12-26 12:58:45',2,'courier',2,NULL,NULL);
INSERT  IGNORE INTO `server_fsm_instances` VALUES (104,'order',1398,'open_cell','FAILED',NULL,1,'FSM locker_open_locker: 1644 (45000): Invalid transition for locker: no matching fsm_transitions','2025-12-26 13:00:28','2025-12-26 13:00:31',2,'courier',NULL,NULL,NULL);
INSERT  IGNORE INTO `server_fsm_instances` VALUES (105,'order_request',81,'order_creation','COMPLETED',NULL,1,NULL,'2025-12-26 13:18:51','2025-12-26 13:18:51',NULL,NULL,NULL,NULL,NULL);
INSERT  IGNORE INTO `server_fsm_instances` VALUES (106,'order',1399,'order_assign_courier1','COMPLETED',NULL,1,NULL,'2025-12-26 13:22:13','2025-12-26 13:23:21',2,'courier',2,NULL,NULL);
INSERT  IGNORE INTO `server_fsm_instances` VALUES (108,'order',1399,'open_cell','COMPLETED',NULL,1,NULL,'2025-12-26 13:24:54','2025-12-26 13:24:56',2,'courier',NULL,NULL,NULL);
INSERT  IGNORE INTO `server_fsm_instances` VALUES (109,'order',1399,'close_cell','COMPLETED',NULL,1,NULL,'2025-12-26 13:29:17','2025-12-26 13:29:22',2,'courier',NULL,NULL,NULL);
INSERT  IGNORE INTO `server_fsm_instances` VALUES (110,'order',1399,'cancel_order','FAILED',NULL,1,'CANNOT_CANCEL_FROM_order_parcel_confirmed','2025-12-26 13:31:15','2025-12-26 13:31:17',2,'courier',NULL,NULL,NULL);
INSERT  IGNORE INTO `server_fsm_instances` VALUES (111,'order_request',82,'order_creation','COMPLETED',NULL,1,NULL,'2025-12-26 13:38:36','2025-12-26 13:38:37',NULL,NULL,NULL,NULL,NULL);
INSERT  IGNORE INTO `server_fsm_instances` VALUES (112,'order',1400,'cancel_order','FAILED',NULL,1,'FSM order_cancel_reservation: 1644 (45000): Invalid transition for order: no matching fsm_transitions','2025-12-26 13:43:35','2025-12-26 15:52:11',3,'client',NULL,NULL,NULL);
INSERT  IGNORE INTO `server_fsm_instances` VALUES (114,'order_request',83,'order_creation','COMPLETED',NULL,1,NULL,'2025-12-26 16:14:28','2025-12-26 16:14:32',NULL,NULL,NULL,NULL,NULL);
INSERT  IGNORE INTO `server_fsm_instances` VALUES (115,'order',1401,'cancel_order','FAILED',NULL,1,'name \'order\' is not defined','2025-12-26 16:18:47','2025-12-26 16:32:13',3,'client',NULL,NULL,NULL);
INSERT  IGNORE INTO `server_fsm_instances` VALUES (117,'order_request',84,'order_creation','COMPLETED',NULL,1,NULL,'2025-12-26 16:45:47','2025-12-26 16:45:51',NULL,NULL,NULL,NULL,NULL);
INSERT  IGNORE INTO `server_fsm_instances` VALUES (118,'order_request',85,'order_creation','COMPLETED',NULL,1,NULL,'2025-12-26 17:11:36','2025-12-26 17:11:36',NULL,NULL,NULL,NULL,NULL);
INSERT  IGNORE INTO `server_fsm_instances` VALUES (119,'order',1403,'cancel_order','COMPLETED',NULL,1,NULL,'2025-12-26 17:13:12','2025-12-26 17:13:17',1001,'client',NULL,NULL,NULL);
INSERT  IGNORE INTO `server_fsm_instances` VALUES (120,'order_request',86,'order_creation','COMPLETED',NULL,1,NULL,'2025-12-27 15:09:28','2025-12-27 15:09:30',NULL,NULL,NULL,NULL,NULL);
INSERT  IGNORE INTO `server_fsm_instances` VALUES (121,'order_request',87,'order_creation','COMPLETED',NULL,1,NULL,'2025-12-27 15:13:30','2025-12-27 15:13:30',NULL,NULL,NULL,NULL,NULL);
INSERT  IGNORE INTO `server_fsm_instances` VALUES (123,'order_request',88,'order_creation','COMPLETED',NULL,1,NULL,'2025-12-27 15:14:23','2025-12-28 15:09:47',NULL,NULL,NULL,NULL,NULL);
INSERT  IGNORE INTO `server_fsm_instances` VALUES (125,'order_request',89,'order_creation','FAILED',NULL,1,'NO_FREE_CELLS','2025-12-27 15:29:29','2025-12-28 15:09:47',NULL,NULL,NULL,NULL,NULL);
INSERT  IGNORE INTO `server_fsm_instances` VALUES (127,'order_request',90,'order_creation','FAILED',NULL,1,'NO_FREE_CELLS','2025-12-27 15:30:18','2025-12-29 06:58:01',NULL,NULL,NULL,NULL,NULL);
INSERT  IGNORE INTO `server_fsm_instances` VALUES (139,'order_request',91,'order_creation','COMPLETED',NULL,1,NULL,'2025-12-27 16:55:39','2025-12-29 06:58:01',NULL,NULL,NULL,NULL,NULL);
INSERT  IGNORE INTO `server_fsm_instances` VALUES (140,'order_request',93,'order_creation','FAILED',NULL,1,'NO_FREE_CELLS','2025-12-29 17:34:49','2025-12-31 09:47:42',NULL,NULL,NULL,NULL,NULL);
INSERT  IGNORE INTO `server_fsm_instances` VALUES (141,'order_request',92,'order_creation','FAILED',NULL,1,'NO_FREE_CELLS','2025-12-29 17:34:49','2025-12-31 09:47:42',NULL,NULL,NULL,NULL,NULL);
INSERT  IGNORE INTO `server_fsm_instances` VALUES (142,'order_request',94,'order_creation','FAILED',NULL,1,'NO_FREE_CELLS','2025-12-29 17:34:50','2025-12-31 09:47:42',NULL,NULL,NULL,NULL,NULL);
INSERT  IGNORE INTO `server_fsm_instances` VALUES (143,'trip',301,'trip_assign_driver','FAILED',NULL,1,'TARGET_USER_ID_NOT_SET','2025-12-29 18:36:41','2025-12-31 09:47:42',200,'driver',NULL,NULL,NULL);
INSERT  IGNORE INTO `server_fsm_instances` VALUES (144,'order',304,'cancel_order','FAILED',NULL,1,'CANCEL_NOT_ALLOWED_FOR_driver','2025-12-29 18:36:44','2026-01-17 09:17:39',200,'driver',NULL,NULL,NULL);
INSERT  IGNORE INTO `server_fsm_instances` VALUES (145,'trip',305,'arrive_at_destination','FAILED',NULL,1,'FSM trip_end_delivery: 1644 (45000): Unsupported entity_type in fsm_perform_action','2025-12-29 18:36:46','2026-01-01 17:48:43',200,'driver',NULL,NULL,NULL);
INSERT  IGNORE INTO `server_fsm_instances` VALUES (146,'order',305,'cancel_order','FAILED',NULL,1,'CANCEL_NOT_ALLOWED_FOR_driver','2025-12-29 18:36:56','2026-01-17 09:18:14',200,'driver',NULL,NULL,NULL);
INSERT  IGNORE INTO `server_fsm_instances` VALUES (147,'trip',305,'trip_assign_driver','FAILED',NULL,1,'TARGET_USER_ID_NOT_SET','2025-12-29 18:36:59','2025-12-31 09:47:42',200,'driver',NULL,NULL,NULL);
INSERT  IGNORE INTO `server_fsm_instances` VALUES (148,'order',201,'open_cell','FAILED',NULL,1,'ROLE_NOT_SUPPORTED_driver','2025-12-29 18:37:11','2026-02-25 06:07:51',1,'driver',1,NULL,NULL);
INSERT  IGNORE INTO `server_fsm_instances` VALUES (149,'order',203,'open_cell','FAILED',NULL,1,'ROLE_NOT_SUPPORTED_driver','2025-12-29 18:37:27','2026-02-25 06:07:56',1,'driver',1,NULL,NULL);
INSERT  IGNORE INTO `server_fsm_instances` VALUES (150,'order',306,'cancel_order','FAILED',NULL,1,'CANCEL_NOT_ALLOWED_FOR_driver','2025-12-29 18:37:37','2025-12-31 09:47:42',200,'driver',NULL,NULL,NULL);
INSERT  IGNORE INTO `server_fsm_instances` VALUES (151,'trip',302,'trip_assign_driver','FAILED',NULL,1,'TARGET_USER_ID_NOT_SET','2025-12-29 18:37:40','2025-12-31 09:47:42',200,'driver',NULL,NULL,NULL);
INSERT  IGNORE INTO `server_fsm_instances` VALUES (152,'trip',306,'trip_assign_driver','FAILED',NULL,1,'TARGET_USER_ID_NOT_SET','2025-12-29 18:37:49','2025-12-31 09:47:42',200,'driver',NULL,NULL,NULL);
INSERT  IGNORE INTO `server_fsm_instances` VALUES (153,'trip',304,'trip_assign_driver','FAILED',NULL,1,'TARGET_USER_ID_NOT_SET','2025-12-30 13:40:40','2025-12-31 09:47:42',200,'driver',NULL,NULL,NULL);
INSERT  IGNORE INTO `server_fsm_instances` VALUES (163,'order_request',95,'order_creation','FAILED',NULL,1,'NO_FREE_CELLS','2025-12-30 14:03:58','2025-12-31 09:47:42',NULL,NULL,NULL,NULL,NULL);
INSERT  IGNORE INTO `server_fsm_instances` VALUES (168,'order_request',96,'order_creation','FAILED',NULL,1,'NO_FREE_CELLS','2025-12-30 17:00:52','2025-12-31 09:47:42',NULL,NULL,NULL,NULL,NULL);
INSERT  IGNORE INTO `server_fsm_instances` VALUES (169,'order_request',97,'order_creation','FAILED',NULL,1,'NO_FREE_CELLS','2025-12-30 17:03:17','2025-12-31 09:47:42',NULL,NULL,NULL,NULL,NULL);
INSERT  IGNORE INTO `server_fsm_instances` VALUES (171,'order_request',98,'order_creation','FAILED',NULL,1,'NO_FREE_CELLS','2025-12-30 17:09:41','2025-12-31 09:47:42',NULL,NULL,NULL,NULL,NULL);
INSERT  IGNORE INTO `server_fsm_instances` VALUES (172,'order_request',99,'order_creation','FAILED',NULL,1,'NO_FREE_CELLS','2025-12-30 17:10:22','2025-12-31 09:47:42',NULL,NULL,NULL,NULL,NULL);
INSERT  IGNORE INTO `server_fsm_instances` VALUES (175,'order_request',100,'order_creation','FAILED',NULL,1,'NO_FREE_CELLS','2025-12-30 17:49:29','2025-12-31 09:47:42',NULL,NULL,NULL,NULL,NULL);
INSERT  IGNORE INTO `server_fsm_instances` VALUES (176,'order_request',101,'order_creation','FAILED',NULL,1,'NO_FREE_CELLS','2025-12-30 17:52:06','2025-12-31 09:47:42',NULL,NULL,NULL,NULL,NULL);
INSERT  IGNORE INTO `server_fsm_instances` VALUES (183,'order',202,'open_cell','FAILED',NULL,1,'ROLE_NOT_SUPPORTED_driver','2025-12-30 17:54:22','2026-02-25 06:08:06',1,'driver',1,NULL,NULL);
INSERT  IGNORE INTO `server_fsm_instances` VALUES (188,'trip',301,'start_trip','FAILED',NULL,1,'\'DatabaseLayer\' object has no attribute \'trip_start_trip\'','2025-12-30 17:54:44','2025-12-31 09:47:43',200,'driver',NULL,NULL,NULL);
INSERT  IGNORE INTO `server_fsm_instances` VALUES (190,'order',302,'cancel_order','FAILED',NULL,1,'CANCEL_NOT_ALLOWED_FOR_driver','2025-12-30 17:55:02','2025-12-31 09:47:43',200,'driver',NULL,NULL,NULL);
INSERT  IGNORE INTO `server_fsm_instances` VALUES (193,'order',301,'cancel_order','FAILED',NULL,1,'CANCEL_NOT_ALLOWED_FOR_driver','2025-12-30 17:55:13','2025-12-31 09:47:43',200,'driver',NULL,NULL,NULL);
INSERT  IGNORE INTO `server_fsm_instances` VALUES (195,'order_request',102,'order_creation','FAILED',NULL,1,'NO_FREE_CELLS','2025-12-30 19:43:43','2025-12-31 09:47:43',NULL,NULL,NULL,NULL,NULL);
INSERT  IGNORE INTO `server_fsm_instances` VALUES (196,'order_request',103,'order_creation','FAILED',NULL,1,'NO_FREE_CELLS','2025-12-30 19:49:57','2025-12-31 09:47:43',NULL,NULL,NULL,NULL,NULL);
INSERT  IGNORE INTO `server_fsm_instances` VALUES (197,'order_request',104,'order_creation','FAILED',NULL,1,'NO_FREE_CELLS','2025-12-31 09:50:17','2025-12-31 09:58:08',NULL,NULL,NULL,NULL,NULL);
INSERT  IGNORE INTO `server_fsm_instances` VALUES (198,'order_request',105,'order_creation','FAILED',NULL,1,'NO_FREE_CELLS','2025-12-31 11:09:27','2025-12-31 11:15:58',NULL,NULL,NULL,NULL,NULL);
INSERT  IGNORE INTO `server_fsm_instances` VALUES (199,'order_request',106,'order_creation','COMPLETED',NULL,1,NULL,'2025-12-31 11:19:12','2025-12-31 11:19:13',NULL,NULL,NULL,NULL,NULL);
INSERT  IGNORE INTO `server_fsm_instances` VALUES (200,'order_request',107,'order_creation','COMPLETED',NULL,1,NULL,'2026-01-01 13:22:50','2026-01-01 13:22:52',NULL,NULL,NULL,NULL,NULL);
INSERT  IGNORE INTO `server_fsm_instances` VALUES (201,'order_request',108,'order_creation','COMPLETED',NULL,1,NULL,'2026-01-01 13:23:50','2026-01-01 13:23:52',NULL,NULL,NULL,NULL,NULL);
INSERT  IGNORE INTO `server_fsm_instances` VALUES (205,'order_request',109,'order_creation','COMPLETED',NULL,1,NULL,'2026-01-02 10:48:14','2026-01-02 10:48:17',NULL,NULL,NULL,NULL,NULL);
INSERT  IGNORE INTO `server_fsm_instances` VALUES (208,'order_request',110,'order_creation','COMPLETED',NULL,1,NULL,'2026-01-02 11:09:22','2026-01-02 13:23:12',NULL,NULL,NULL,NULL,NULL);
INSERT  IGNORE INTO `server_fsm_instances` VALUES (209,'order_request',111,'order_creation','FAILED',NULL,1,'NO_FREE_CELLS','2026-01-02 11:09:34','2026-01-02 13:23:12',NULL,NULL,NULL,NULL,NULL);
INSERT  IGNORE INTO `server_fsm_instances` VALUES (210,'order',5,'trip_assign_driver','FAILED',NULL,1,'ASSIGNMENT_FAILED','2026-01-02 11:53:44','2026-02-06 10:49:43',200,'driver',200,NULL,NULL);
INSERT  IGNORE INTO `server_fsm_instances` VALUES (211,'order_request',112,'order_creation','FAILED',NULL,1,'NO_FREE_CELLS','2026-01-02 11:54:29','2026-01-02 13:23:12',NULL,NULL,NULL,NULL,NULL);
INSERT  IGNORE INTO `server_fsm_instances` VALUES (212,'order_request',113,'order_creation','FAILED',NULL,1,'NO_FREE_CELLS','2026-01-02 11:55:42','2026-01-02 13:23:12',NULL,NULL,NULL,NULL,NULL);
INSERT  IGNORE INTO `server_fsm_instances` VALUES (213,'order_request',114,'order_creation','FAILED',NULL,1,'NO_FREE_CELLS','2026-01-02 13:58:06','2026-01-06 13:10:03',NULL,NULL,NULL,NULL,NULL);
INSERT  IGNORE INTO `server_fsm_instances` VALUES (214,'order_request',115,'order_creation','FAILED',NULL,1,'NO_FREE_CELLS','2026-01-02 14:15:23','2026-01-06 13:10:03',NULL,NULL,NULL,NULL,NULL);
INSERT  IGNORE INTO `server_fsm_instances` VALUES (215,'order_request',116,'order_creation','FAILED',NULL,0,'STUCK_TIMEOUT','2026-01-06 13:15:59','2026-01-06 14:47:45',NULL,NULL,NULL,NULL,NULL);
INSERT  IGNORE INTO `server_fsm_instances` VALUES (216,'order_request',117,'order_creation','COMPLETED',NULL,1,NULL,'2026-01-06 15:00:13','2026-01-06 15:00:17',NULL,NULL,NULL,NULL,NULL);
INSERT  IGNORE INTO `server_fsm_instances` VALUES (217,'order',1413,'order_assign_courier1','COMPLETED',NULL,1,NULL,'2026-01-06 15:32:18','2026-01-06 15:32:23',1003,'client',1003,NULL,NULL);
INSERT  IGNORE INTO `server_fsm_instances` VALUES (218,'order_request',118,'order_creation','COMPLETED',NULL,1,NULL,'2026-01-09 17:03:26','2026-01-09 17:03:28',NULL,NULL,NULL,NULL,NULL);
INSERT  IGNORE INTO `server_fsm_instances` VALUES (219,'order_request',119,'order_creation','FAILED',NULL,1,'NO_FREE_CELLS','2026-01-09 17:41:53','2026-01-09 17:41:54',NULL,NULL,NULL,NULL,NULL);
INSERT  IGNORE INTO `server_fsm_instances` VALUES (220,'order',1411,'trip_assign_driver','FAILED',NULL,1,'TARGET_USER_ID_NOT_SET','2026-01-09 18:08:32','2026-01-09 18:08:35',200,'driver',NULL,NULL,NULL);
INSERT  IGNORE INTO `server_fsm_instances` VALUES (221,'order',1414,'trip_assign_driver','FAILED',NULL,1,'TARGET_USER_ID_NOT_SET','2026-01-09 18:08:37','2026-01-09 18:08:40',200,'driver',NULL,NULL,NULL);
INSERT  IGNORE INTO `server_fsm_instances` VALUES (222,'order_request',120,'order_creation','COMPLETED',NULL,1,NULL,'2026-01-09 18:09:14','2026-01-09 18:09:15',NULL,NULL,NULL,NULL,NULL);
INSERT  IGNORE INTO `server_fsm_instances` VALUES (223,'order_request',121,'order_creation','COMPLETED',NULL,1,NULL,'2026-01-09 18:09:48','2026-01-09 18:09:50',NULL,NULL,NULL,NULL,NULL);
INSERT  IGNORE INTO `server_fsm_instances` VALUES (224,'order_request',122,'order_creation','COMPLETED',NULL,1,NULL,'2026-01-09 18:15:57','2026-01-09 18:16:00',NULL,NULL,NULL,NULL,NULL);
INSERT  IGNORE INTO `server_fsm_instances` VALUES (225,'order_request',123,'order_creation','COMPLETED',NULL,1,NULL,'2026-01-09 18:17:30','2026-01-09 18:17:30',NULL,NULL,NULL,NULL,NULL);
INSERT  IGNORE INTO `server_fsm_instances` VALUES (226,'order_request',124,'order_creation','FAILED',NULL,1,'NO_FREE_CELLS','2026-01-10 08:42:22','2026-01-10 08:42:25',NULL,NULL,NULL,NULL,NULL);
INSERT  IGNORE INTO `server_fsm_instances` VALUES (227,'order_request',125,'order_creation','FAILED',NULL,1,'NO_FREE_CELLS','2026-01-10 08:53:37','2026-01-10 08:53:40',NULL,NULL,NULL,NULL,NULL);
INSERT  IGNORE INTO `server_fsm_instances` VALUES (228,'order_request',126,'order_creation','FAILED',NULL,1,'NO_FREE_CELLS','2026-01-10 08:55:10','2026-01-10 08:55:11',NULL,NULL,NULL,NULL,NULL);
INSERT  IGNORE INTO `server_fsm_instances` VALUES (229,'order_request',127,'order_creation','FAILED',NULL,1,'NO_FREE_CELLS','2026-01-10 08:56:04','2026-01-10 08:56:06',NULL,NULL,NULL,NULL,NULL);
INSERT  IGNORE INTO `server_fsm_instances` VALUES (230,'order_request',128,'order_creation','FAILED',NULL,1,'NO_FREE_CELLS','2026-01-10 08:59:02','2026-01-10 08:59:06',NULL,NULL,NULL,NULL,NULL);
INSERT  IGNORE INTO `server_fsm_instances` VALUES (231,'order_request',129,'order_creation','COMPLETED',NULL,1,NULL,'2026-01-11 11:45:15','2026-01-11 11:45:19',NULL,NULL,NULL,NULL,NULL);
INSERT  IGNORE INTO `server_fsm_instances` VALUES (232,'order_request',130,'order_creation','COMPLETED',NULL,1,NULL,'2026-01-11 12:34:50','2026-01-11 12:34:54',NULL,NULL,NULL,NULL,NULL);
INSERT  IGNORE INTO `server_fsm_instances` VALUES (233,'order_request',131,'order_creation','COMPLETED',NULL,1,NULL,'2026-01-11 12:40:09','2026-01-11 12:40:09',NULL,NULL,NULL,NULL,NULL);
INSERT  IGNORE INTO `server_fsm_instances` VALUES (234,'order_request',132,'order_creation','COMPLETED',NULL,1,NULL,'2026-01-11 14:14:40','2026-01-11 14:14:42',NULL,NULL,NULL,NULL,NULL);
INSERT  IGNORE INTO `server_fsm_instances` VALUES (235,'order_request',133,'order_creation','FAILED',NULL,1,'NO_FREE_CELLS','2026-01-12 10:14:59','2026-01-12 10:15:00',NULL,NULL,NULL,NULL,NULL);
INSERT  IGNORE INTO `server_fsm_instances` VALUES (236,'order_request',134,'order_creation','FAILED',NULL,1,'NO_FREE_CELLS','2026-01-12 10:15:56','2026-01-12 10:16:00',NULL,NULL,NULL,NULL,NULL);
INSERT  IGNORE INTO `server_fsm_instances` VALUES (237,'order_request',135,'order_creation','FAILED',NULL,1,'NO_FREE_CELLS','2026-01-12 10:17:22','2026-01-12 10:17:25',NULL,NULL,NULL,NULL,NULL);
INSERT  IGNORE INTO `server_fsm_instances` VALUES (238,'order_request',136,'order_creation','FAILED',NULL,1,'NO_FREE_CELLS','2026-01-12 11:50:29','2026-01-12 11:50:33',NULL,NULL,NULL,NULL,NULL);
INSERT  IGNORE INTO `server_fsm_instances` VALUES (239,'order_request',137,'order_creation','FAILED',NULL,1,'NO_FREE_CELLS','2026-01-12 11:50:48','2026-01-12 11:50:53',NULL,NULL,NULL,NULL,NULL);
INSERT  IGNORE INTO `server_fsm_instances` VALUES (240,'order_request',138,'order_creation','FAILED',NULL,1,'NO_FREE_CELLS','2026-01-12 11:56:06','2026-01-12 11:56:08',NULL,NULL,NULL,NULL,NULL);
INSERT  IGNORE INTO `server_fsm_instances` VALUES (241,'order_request',139,'order_creation','FAILED',NULL,1,'NO_FREE_CELLS','2026-01-12 12:00:26','2026-01-12 12:00:28',NULL,NULL,NULL,NULL,NULL);
INSERT  IGNORE INTO `server_fsm_instances` VALUES (242,'order_request',140,'order_creation','FAILED',NULL,1,'NO_FREE_CELLS','2026-01-12 12:01:18','2026-01-12 12:01:23',NULL,NULL,NULL,NULL,NULL);
INSERT  IGNORE INTO `server_fsm_instances` VALUES (243,'order_request',141,'order_creation','FAILED',NULL,1,'NO_FREE_CELLS','2026-01-12 12:02:52','2026-01-12 12:02:53',NULL,NULL,NULL,NULL,NULL);
INSERT  IGNORE INTO `server_fsm_instances` VALUES (244,'order_request',142,'order_creation','FAILED',NULL,1,'NO_FREE_CELLS','2026-01-12 12:08:20','2026-01-12 12:08:23',NULL,NULL,NULL,NULL,NULL);
INSERT  IGNORE INTO `server_fsm_instances` VALUES (245,'order_request',143,'order_creation','COMPLETED',NULL,1,NULL,'2026-01-12 12:13:19','2026-01-12 12:13:23',NULL,NULL,NULL,NULL,NULL);
INSERT  IGNORE INTO `server_fsm_instances` VALUES (246,'order_request',144,'order_creation','COMPLETED',NULL,1,NULL,'2026-01-12 14:47:07','2026-01-12 14:47:10',NULL,NULL,NULL,NULL,NULL);
INSERT  IGNORE INTO `server_fsm_instances` VALUES (247,'order_request',145,'order_creation','COMPLETED',NULL,1,NULL,'2026-01-12 14:47:45','2026-01-12 14:47:50',NULL,NULL,NULL,NULL,NULL);
INSERT  IGNORE INTO `server_fsm_instances` VALUES (248,'order_request',146,'order_creation','COMPLETED',NULL,1,NULL,'2026-01-12 14:49:24','2026-01-12 14:49:28',NULL,NULL,NULL,NULL,NULL);
INSERT  IGNORE INTO `server_fsm_instances` VALUES (249,'order_request',147,'order_creation','FAILED',NULL,1,'NO_FREE_CELLS','2026-01-12 14:49:49','2026-01-12 14:49:53',NULL,NULL,NULL,NULL,NULL);
INSERT  IGNORE INTO `server_fsm_instances` VALUES (250,'order_request',148,'order_creation','COMPLETED',NULL,1,NULL,'2026-01-12 15:50:00','2026-01-12 15:50:04',NULL,NULL,NULL,NULL,NULL);
INSERT  IGNORE INTO `server_fsm_instances` VALUES (251,'order_request',149,'order_creation','COMPLETED',NULL,1,NULL,'2026-01-12 15:50:37','2026-01-12 15:50:39',NULL,NULL,NULL,NULL,NULL);
INSERT  IGNORE INTO `server_fsm_instances` VALUES (252,'order_request',150,'order_creation','COMPLETED',NULL,1,NULL,'2026-01-12 15:52:46','2026-01-12 15:52:49',NULL,NULL,NULL,NULL,NULL);
INSERT  IGNORE INTO `server_fsm_instances` VALUES (253,'order_request',151,'order_creation','FAILED',NULL,1,'NO_FREE_CELLS','2026-01-12 16:15:26','2026-01-13 15:25:02',NULL,NULL,NULL,NULL,NULL);
INSERT  IGNORE INTO `server_fsm_instances` VALUES (254,'order_request',152,'order_creation','FAILED',NULL,1,'NO_FREE_CELLS','2026-01-12 16:15:29','2026-01-13 15:25:00',NULL,NULL,NULL,NULL,NULL);
INSERT  IGNORE INTO `server_fsm_instances` VALUES (255,'order_request',153,'order_creation','COMPLETED',NULL,1,NULL,'2026-01-12 16:18:37','2026-01-13 15:25:01',NULL,NULL,NULL,NULL,NULL);
INSERT  IGNORE INTO `server_fsm_instances` VALUES (256,'order_request',154,'order_creation','FAILED',NULL,1,'NO_FREE_CELLS','2026-01-12 16:21:59','2026-01-13 15:25:00',NULL,NULL,NULL,NULL,NULL);
INSERT  IGNORE INTO `server_fsm_instances` VALUES (257,'order_request',155,'order_creation','FAILED',NULL,1,'NO_FREE_CELLS','2026-01-12 16:23:16','2026-01-13 01:01:33',NULL,NULL,NULL,NULL,NULL);
INSERT  IGNORE INTO `server_fsm_instances` VALUES (258,'order_request',156,'order_creation','COMPLETED',NULL,1,NULL,'2026-01-13 07:54:40','2026-01-13 15:24:59',NULL,NULL,NULL,NULL,NULL);
INSERT  IGNORE INTO `server_fsm_instances` VALUES (259,'order_request',157,'order_creation','COMPLETED',NULL,1,NULL,'2026-01-13 07:55:58','2026-01-13 14:16:28',NULL,NULL,NULL,NULL,NULL);
INSERT  IGNORE INTO `server_fsm_instances` VALUES (260,'order_request',158,'order_creation','FAILED',NULL,1,'NO_FREE_CELLS','2026-01-13 07:58:59','2026-01-13 15:25:02',NULL,NULL,NULL,NULL,NULL);
INSERT  IGNORE INTO `server_fsm_instances` VALUES (261,'order_request',159,'order_creation','FAILED',NULL,1,'NO_FREE_CELLS','2026-01-13 08:00:47','2026-01-13 14:16:28',NULL,NULL,NULL,NULL,NULL);
INSERT  IGNORE INTO `server_fsm_instances` VALUES (262,'order_request',160,'order_creation','FAILED',NULL,1,'NO_FREE_CELLS','2026-01-13 08:01:29','2026-01-13 14:16:28',NULL,NULL,NULL,NULL,NULL);
INSERT  IGNORE INTO `server_fsm_instances` VALUES (263,'order_request',161,'order_creation','FAILED',NULL,1,'NO_FREE_CELLS','2026-01-13 08:22:44','2026-01-13 09:12:39',NULL,NULL,NULL,NULL,NULL);
INSERT  IGNORE INTO `server_fsm_instances` VALUES (264,'order',1428,'cancel_order','COMPLETED',NULL,1,NULL,'2026-01-13 08:39:38','2026-01-13 11:40:52',1002,'client',NULL,NULL,NULL);
INSERT  IGNORE INTO `server_fsm_instances` VALUES (266,'order',1425,'cancel_order','COMPLETED',NULL,1,NULL,'2026-01-13 08:46:49','2026-01-13 14:16:22',1003,'client',NULL,NULL,NULL);
INSERT  IGNORE INTO `server_fsm_instances` VALUES (268,'order_request',162,'order_creation','COMPLETED',NULL,1,NULL,'2026-01-13 08:47:16','2026-01-13 12:42:27',NULL,NULL,NULL,NULL,NULL);
INSERT  IGNORE INTO `server_fsm_instances` VALUES (269,'order',1429,'cancel_order','COMPLETED',NULL,1,NULL,'2026-01-13 08:48:14','2026-01-13 09:21:40',1004,'client',NULL,NULL,NULL);
INSERT  IGNORE INTO `server_fsm_instances` VALUES (275,'order_request',163,'order_creation','COMPLETED',NULL,1,NULL,'2026-01-13 09:23:48','2026-01-13 11:40:52',NULL,NULL,NULL,NULL,NULL);
INSERT  IGNORE INTO `server_fsm_instances` VALUES (276,'order_request',164,'order_creation','FAILED',NULL,1,'NO_FREE_CELLS','2026-01-13 15:27:13','2026-01-13 15:27:17',NULL,NULL,NULL,NULL,NULL);
INSERT  IGNORE INTO `server_fsm_instances` VALUES (277,'order_request',165,'order_creation','FAILED',NULL,1,'NO_FREE_CELLS','2026-01-13 15:34:52','2026-01-13 15:34:52',NULL,NULL,NULL,NULL,NULL);
INSERT  IGNORE INTO `server_fsm_instances` VALUES (278,'order_request',166,'order_creation','COMPLETED',NULL,1,NULL,'2026-01-13 15:53:22','2026-01-13 15:53:23',NULL,NULL,NULL,NULL,NULL);
INSERT  IGNORE INTO `server_fsm_instances` VALUES (279,'order_request',167,'order_creation','FAILED',NULL,1,'NO_FREE_CELLS','2026-01-13 18:15:03','2026-01-13 18:15:08',NULL,NULL,NULL,NULL,NULL);
INSERT  IGNORE INTO `server_fsm_instances` VALUES (280,'order_request',168,'order_creation','FAILED',NULL,1,'NO_FREE_CELLS','2026-01-13 18:17:13','2026-01-13 18:17:13',NULL,NULL,NULL,NULL,NULL);
INSERT  IGNORE INTO `server_fsm_instances` VALUES (281,'order_request',169,'order_creation','FAILED',NULL,1,'NO_FREE_CELLS','2026-01-13 18:18:02','2026-01-13 18:18:03',NULL,NULL,NULL,NULL,NULL);
INSERT  IGNORE INTO `server_fsm_instances` VALUES (282,'order',1436,'cancel_order','FAILED',NULL,1,'FSM order_cancel_reservation: 1644 (45000): Invalid transition for order: no matching fsm_transitions','2026-01-13 18:32:34','2026-01-14 10:08:54',1004,'client',NULL,NULL,NULL);
INSERT  IGNORE INTO `server_fsm_instances` VALUES (284,'order',1426,'cancel_order','COMPLETED',NULL,1,NULL,'2026-01-14 08:44:02','2026-01-14 10:08:55',1004,'client',NULL,NULL,NULL);
INSERT  IGNORE INTO `server_fsm_instances` VALUES (285,'order',1422,'cancel_order','FAILED',NULL,1,'FSM order_cancel_reservation: 1644 (45000): Invalid transition for order: no matching fsm_transitions','2026-01-15 07:41:44','2026-01-15 07:49:45',1001,'client',NULL,NULL,NULL);
INSERT  IGNORE INTO `server_fsm_instances` VALUES (287,'order',1421,'cancel_order','FAILED',NULL,1,'FSM locker_cancel_reservation: 1644 (45000): Invalid transition for locker: no matching fsm_transitions','2026-01-15 07:43:48','2026-01-15 07:43:50',1001,'client',NULL,NULL,NULL);
INSERT  IGNORE INTO `server_fsm_instances` VALUES (289,'order_request',170,'order_creation','FAILED',NULL,1,'NO_FREE_CELLS','2026-01-15 07:50:36','2026-01-15 07:50:40',NULL,NULL,NULL,NULL,NULL);
INSERT  IGNORE INTO `server_fsm_instances` VALUES (290,'order_request',171,'order_creation','COMPLETED',NULL,1,NULL,'2026-01-15 07:50:51','2026-01-15 07:50:55',NULL,NULL,NULL,NULL,NULL);
INSERT  IGNORE INTO `server_fsm_instances` VALUES (291,'order',1437,'cancel_order','COMPLETED',NULL,1,NULL,'2026-01-15 07:51:16','2026-01-15 07:51:20',1004,'client',NULL,NULL,NULL);
INSERT  IGNORE INTO `server_fsm_instances` VALUES (292,'order',1,'cancel_order','FAILED',NULL,1,'CANNOT_CANCEL_FROM_order_courier_failed','2026-01-15 07:57:16','2026-01-17 09:22:24',100,'courier',NULL,NULL,NULL);
INSERT  IGNORE INTO `server_fsm_instances` VALUES (293,'order',2,'cancel_order','FAILED',NULL,1,'CANNOT_CANCEL_FROM_order_reservation_expired','2026-01-15 07:57:38','2026-01-15 07:57:41',100,'courier',NULL,NULL,NULL);
INSERT  IGNORE INTO `server_fsm_instances` VALUES (294,'order',1361,'cancel_order','FAILED',NULL,1,'CANNOT_CANCEL_FROM_order_courier_failed','2026-01-15 07:57:51','2026-01-15 07:58:46',100,'courier',NULL,NULL,NULL);
INSERT  IGNORE INTO `server_fsm_instances` VALUES (297,'order_request',172,'order_creation','COMPLETED',NULL,1,NULL,'2026-01-15 08:01:09','2026-01-15 08:01:11',NULL,NULL,NULL,NULL,NULL);
INSERT  IGNORE INTO `server_fsm_instances` VALUES (298,'order',1435,'cancel_order','COMPLETED',NULL,1,NULL,'2026-01-15 09:46:29','2026-01-15 09:46:29',1003,'client',NULL,NULL,NULL);
INSERT  IGNORE INTO `server_fsm_instances` VALUES (299,'order',5,'order_assign_courier1','COMPLETED',NULL,1,NULL,'2026-01-15 10:16:12','2026-03-19 14:33:54',100,'courier',100,NULL,'{}');
INSERT  IGNORE INTO `server_fsm_instances` VALUES (304,'order',1438,'cancel_order','COMPLETED',NULL,1,NULL,'2026-01-15 10:27:46','2026-01-15 10:27:51',1001,'client',NULL,NULL,NULL);
INSERT  IGNORE INTO `server_fsm_instances` VALUES (306,'order_request',173,'order_creation','COMPLETED',NULL,1,NULL,'2026-01-15 10:28:35','2026-01-15 10:28:36',NULL,NULL,NULL,NULL,NULL);
INSERT  IGNORE INTO `server_fsm_instances` VALUES (307,'order',1417,'cancel_order','COMPLETED',NULL,1,NULL,'2026-01-15 10:28:46','2026-01-15 10:28:51',1001,'client',NULL,NULL,NULL);
INSERT  IGNORE INTO `server_fsm_instances` VALUES (309,'order',5,'cancel_order','COMPLETED',NULL,1,NULL,'2026-01-15 10:36:58','2026-01-17 09:22:39',100,'courier',NULL,NULL,NULL);
INSERT  IGNORE INTO `server_fsm_instances` VALUES (311,'order_request',174,'order_creation','COMPLETED',NULL,1,NULL,'2026-01-15 12:46:44','2026-01-15 12:46:48',NULL,NULL,NULL,NULL,NULL);
INSERT  IGNORE INTO `server_fsm_instances` VALUES (312,'order_request',175,'order_creation','FAILED',NULL,1,'NO_FREE_CELLS','2026-01-15 12:50:36','2026-01-15 12:50:38',NULL,NULL,NULL,NULL,NULL);
INSERT  IGNORE INTO `server_fsm_instances` VALUES (313,'order_request',176,'order_creation','FAILED',NULL,1,'name \'apply_fsm_result\' is not defined','2026-01-15 12:50:51','2026-01-15 12:50:53',NULL,NULL,NULL,NULL,NULL);
INSERT  IGNORE INTO `server_fsm_instances` VALUES (314,'order',1407,'cancel_order','FAILED',NULL,1,'FSM locker_cancel_reservation: 1644 (45000): Invalid transition for locker: no matching fsm_transitions','2026-01-15 20:45:15','2026-01-15 20:45:18',1001,'client',NULL,NULL,NULL);
INSERT  IGNORE INTO `server_fsm_instances` VALUES (315,'order_request',177,'order_creation','FAILED',NULL,1,'NO_FREE_CELLS','2026-01-15 20:50:58','2026-01-15 20:50:58',NULL,NULL,NULL,NULL,NULL);
INSERT  IGNORE INTO `server_fsm_instances` VALUES (316,'order_request',178,'order_creation','FAILED',NULL,1,'NO_FREE_CELLS','2026-01-15 20:51:16','2026-01-15 20:51:18',NULL,NULL,NULL,NULL,NULL);
INSERT  IGNORE INTO `server_fsm_instances` VALUES (317,'order_request',179,'order_creation','FAILED',NULL,1,'NO_FREE_CELLS','2026-01-15 20:51:28','2026-01-15 20:51:28',NULL,NULL,NULL,NULL,NULL);
INSERT  IGNORE INTO `server_fsm_instances` VALUES (318,'order_request',180,'order_creation','FAILED',NULL,1,'NO_FREE_CELLS','2026-01-15 20:51:38','2026-01-15 20:51:38',NULL,NULL,NULL,NULL,NULL);
INSERT  IGNORE INTO `server_fsm_instances` VALUES (319,'order_request',181,'order_creation','FAILED',NULL,1,'NO_FREE_CELLS','2026-01-15 20:51:51','2026-01-15 20:51:53',NULL,NULL,NULL,NULL,NULL);
INSERT  IGNORE INTO `server_fsm_instances` VALUES (320,'order_request',182,'order_creation','FAILED',NULL,1,'name \'apply_fsm_result\' is not defined','2026-01-15 20:52:10','2026-01-15 20:52:14',NULL,NULL,NULL,NULL,NULL);
INSERT  IGNORE INTO `server_fsm_instances` VALUES (321,'order',1442,'order_assign_courier1','FAILED',NULL,1,'ASSIGNMENT_FAILED','2026-01-15 20:56:17','2026-01-15 20:56:24',100,'courier',100,NULL,NULL);
INSERT  IGNORE INTO `server_fsm_instances` VALUES (323,'order',1442,'cancel_order','FAILED',NULL,1,'CANNOT_CANCEL_FROM_order_created','2026-01-15 20:56:44','2026-01-15 20:56:59',100,'courier',NULL,NULL,NULL);
INSERT  IGNORE INTO `server_fsm_instances` VALUES (326,'order',4,'cancel_order','FAILED',NULL,1,'CANNOT_CANCEL_FROM_order_reservation_expired','2026-01-17 08:36:43','2026-01-17 08:36:47',100,'courier',NULL,NULL,NULL);
INSERT  IGNORE INTO `server_fsm_instances` VALUES (327,'order',301,'trip_assign_driver','FAILED',NULL,1,'TARGET_USER_ID_NOT_SET','2026-01-17 08:37:23','2026-01-17 09:22:59',200,'driver',NULL,NULL,NULL);
INSERT  IGNORE INTO `server_fsm_instances` VALUES (328,'order',10,'trip_assign_driver','FAILED',NULL,1,'ASSIGNMENT_FAILED','2026-01-17 08:37:54','2026-01-17 08:37:57',200,'driver',200,NULL,NULL);
INSERT  IGNORE INTO `server_fsm_instances` VALUES (330,'order',6,'trip_assign_driver','FAILED',NULL,1,'ASSIGNMENT_FAILED','2026-01-17 09:06:40','2026-01-19 12:15:57',200,'driver',200,NULL,NULL);
INSERT  IGNORE INTO `server_fsm_instances` VALUES (358,'order_request',183,'order_creation','COMPLETED',NULL,1,NULL,'2026-01-27 14:17:24','2026-01-27 14:17:24',NULL,NULL,NULL,NULL,NULL);
INSERT  IGNORE INTO `server_fsm_instances` VALUES (359,'order_request',184,'order_creation','FAILED',NULL,1,'NO_FREE_CELLS','2026-01-27 14:19:54','2026-01-27 14:19:55',NULL,NULL,NULL,NULL,NULL);
INSERT  IGNORE INTO `server_fsm_instances` VALUES (360,'order_request',185,'order_creation','FAILED',NULL,1,'NO_FREE_CELLS','2026-01-27 14:20:38','2026-01-27 14:20:40',NULL,NULL,NULL,NULL,NULL);
INSERT  IGNORE INTO `server_fsm_instances` VALUES (361,'order_request',186,'order_creation','COMPLETED',NULL,1,NULL,'2026-01-27 14:21:01','2026-01-27 14:21:05',NULL,NULL,NULL,NULL,NULL);
INSERT  IGNORE INTO `server_fsm_instances` VALUES (362,'order_request',187,'order_creation','FAILED',NULL,1,'create_order_from_request(187) failed: DatabaseLayer.mark_request_failed() got an unexpected keyword argument \'error_text\'','2026-01-28 08:14:19','2026-01-28 08:14:24',NULL,NULL,NULL,NULL,NULL);
INSERT  IGNORE INTO `server_fsm_instances` VALUES (363,'order_request',188,'order_creation','FAILED',NULL,1,'create_order_from_request(188) failed: DatabaseLayer.create_order_and_reserve_cells() got an unexpected keyword argument \'description\'','2026-01-28 08:38:04','2026-01-28 08:38:08',NULL,NULL,NULL,NULL,NULL);
INSERT  IGNORE INTO `server_fsm_instances` VALUES (364,'order_request',189,'order_creation','FAILED',NULL,1,'create_order_from_request(189) failed: name \'logger\' is not defined','2026-01-28 09:49:33','2026-01-28 09:49:34',NULL,NULL,NULL,NULL,NULL);
INSERT  IGNORE INTO `server_fsm_instances` VALUES (365,'order_request',190,'order_creation','FAILED',NULL,1,'NO_FREE_CELLS','2026-01-28 11:38:08','2026-01-28 11:38:11',NULL,NULL,NULL,NULL,NULL);
INSERT  IGNORE INTO `server_fsm_instances` VALUES (366,'order_request',191,'order_creation','COMPLETED',NULL,1,NULL,'2026-01-28 11:48:06','2026-01-28 11:48:06',NULL,NULL,NULL,NULL,NULL);
INSERT  IGNORE INTO `server_fsm_instances` VALUES (367,'order_request',192,'order_creation','COMPLETED',NULL,1,NULL,'2026-01-28 14:55:21','2026-01-28 14:55:23',NULL,NULL,NULL,NULL,NULL);
INSERT  IGNORE INTO `server_fsm_instances` VALUES (368,'order_request',193,'order_creation','FAILED',NULL,1,'NO_FREE_CELLS','2026-01-28 14:58:30','2026-01-28 14:58:33',NULL,NULL,NULL,NULL,NULL);
INSERT  IGNORE INTO `server_fsm_instances` VALUES (369,'order',1447,'cancel_order','COMPLETED',NULL,1,NULL,'2026-01-28 15:12:41','2026-01-28 15:12:44',1005,'client',NULL,NULL,NULL);
INSERT  IGNORE INTO `server_fsm_instances` VALUES (371,'order',1446,'cancel_order','COMPLETED',NULL,1,NULL,'2026-01-28 15:12:55','2026-01-28 15:12:59',1004,'client',NULL,NULL,NULL);
INSERT  IGNORE INTO `server_fsm_instances` VALUES (372,'order_request',194,'order_creation','COMPLETED',NULL,1,NULL,'2026-01-29 08:12:39','2026-01-29 08:12:40',NULL,NULL,NULL,NULL,NULL);
INSERT  IGNORE INTO `server_fsm_instances` VALUES (373,'order_request',195,'order_creation','COMPLETED',NULL,1,NULL,'2026-02-04 15:52:57','2026-02-04 15:52:58',NULL,NULL,NULL,NULL,NULL);
INSERT  IGNORE INTO `server_fsm_instances` VALUES (374,'order_request',196,'order_creation','COMPLETED',NULL,1,NULL,'2026-02-05 07:54:07','2026-02-05 07:58:29',NULL,NULL,NULL,NULL,NULL);
INSERT  IGNORE INTO `server_fsm_instances` VALUES (375,'order_request',197,'order_creation','COMPLETED',NULL,1,NULL,'2026-02-05 08:00:37','2026-02-05 08:00:39',NULL,NULL,NULL,NULL,NULL);
INSERT  IGNORE INTO `server_fsm_instances` VALUES (376,'order',1503,'cancel_order','COMPLETED',NULL,1,NULL,'2026-02-05 08:04:32','2026-02-05 08:25:26',1004,'client',NULL,NULL,NULL);
INSERT  IGNORE INTO `server_fsm_instances` VALUES (379,'order_request',198,'order_creation','COMPLETED',NULL,1,NULL,'2026-02-05 09:06:16','2026-02-05 09:06:17',NULL,NULL,NULL,NULL,NULL);
INSERT  IGNORE INTO `server_fsm_instances` VALUES (380,'order_request',199,'order_creation','FAILED',NULL,1,'NO_FREE_CELLS','2026-02-05 09:06:50','2026-02-05 09:06:52',NULL,NULL,NULL,NULL,NULL);
INSERT  IGNORE INTO `server_fsm_instances` VALUES (381,'order',1502,'order_assign_courier1','COMPLETED',NULL,1,NULL,'2026-02-05 09:11:43','2026-02-05 09:11:47',100,'courier',100,NULL,NULL);
INSERT  IGNORE INTO `server_fsm_instances` VALUES (382,'order_request',200,'order_creation','COMPLETED',NULL,1,NULL,'2026-02-06 05:52:47','2026-02-06 05:52:52',NULL,NULL,NULL,NULL,NULL);
INSERT  IGNORE INTO `server_fsm_instances` VALUES (383,'order_request',201,'order_creation','COMPLETED',NULL,1,NULL,'2026-02-06 05:53:08','2026-02-06 05:53:12',NULL,NULL,NULL,NULL,NULL);
INSERT  IGNORE INTO `server_fsm_instances` VALUES (384,'order_request',202,'order_creation','COMPLETED',NULL,1,NULL,'2026-02-06 05:53:28','2026-02-06 05:53:32',NULL,NULL,NULL,NULL,NULL);
INSERT  IGNORE INTO `server_fsm_instances` VALUES (385,'order_request',203,'order_creation','FAILED',NULL,1,'NO_FREE_CELLS','2026-02-06 05:53:40','2026-02-06 05:53:42',NULL,NULL,NULL,NULL,NULL);
INSERT  IGNORE INTO `server_fsm_instances` VALUES (386,'order_request',204,'order_creation','FAILED',NULL,1,'NO_FREE_CELLS','2026-02-06 05:53:43','2026-02-06 05:53:47',NULL,NULL,NULL,NULL,NULL);
INSERT  IGNORE INTO `server_fsm_instances` VALUES (387,'order_request',205,'order_creation','FAILED',NULL,1,'NO_FREE_CELLS','2026-02-06 05:53:49','2026-02-06 05:53:52',NULL,NULL,NULL,NULL,NULL);
INSERT  IGNORE INTO `server_fsm_instances` VALUES (390,'order',1507,'trip_assign_driver','FAILED',NULL,1,'ASSIGNMENT_FAILED','2026-02-06 10:43:28','2026-02-06 10:43:33',200,'driver',200,NULL,NULL);
INSERT  IGNORE INTO `server_fsm_instances` VALUES (394,'order',660,'trip_assign_driver','FAILED',NULL,1,'ASSIGNMENT_FAILED','2026-02-06 10:50:08','2026-02-06 10:50:13',200,'driver',200,NULL,NULL);
INSERT  IGNORE INTO `server_fsm_instances` VALUES (395,'order',660,'order_assign_courier1','FAILED',NULL,1,'ASSIGNMENT_FAILED','2026-02-06 10:52:04','2026-02-13 13:20:47',100,'courier',100,NULL,NULL);
INSERT  IGNORE INTO `server_fsm_instances` VALUES (396,'order_request',206,'order_creation','FAILED',NULL,1,'NO_FREE_CELLS','2026-02-06 16:31:36','2026-02-06 16:31:37',NULL,NULL,NULL,NULL,NULL);
INSERT  IGNORE INTO `server_fsm_instances` VALUES (397,'order_request',207,'order_creation','FAILED',NULL,1,'List argument must consist only of tuples or dictionaries','2026-02-08 12:08:59','2026-02-08 13:13:21',NULL,NULL,NULL,NULL,NULL);
INSERT  IGNORE INTO `server_fsm_instances` VALUES (398,'order_request',208,'order_creation','FAILED',NULL,1,'List argument must consist only of tuples or dictionaries','2026-02-08 12:38:24','2026-02-08 13:13:21',NULL,NULL,NULL,NULL,NULL);
INSERT  IGNORE INTO `server_fsm_instances` VALUES (399,'order_request',209,'order_creation','FAILED',NULL,1,'List argument must consist only of tuples or dictionaries','2026-02-08 12:50:37','2026-02-08 13:13:21',NULL,NULL,NULL,NULL,NULL);
INSERT  IGNORE INTO `server_fsm_instances` VALUES (400,'order_request',210,'order_creation','FAILED',NULL,1,'List argument must consist only of tuples or dictionaries','2026-02-08 12:56:31','2026-02-08 13:13:21',NULL,NULL,NULL,NULL,NULL);
INSERT  IGNORE INTO `server_fsm_instances` VALUES (401,'order_request',211,'order_creation','FAILED',NULL,1,'List argument must consist only of tuples or dictionaries','2026-02-08 13:03:35','2026-02-08 13:13:21',NULL,NULL,NULL,NULL,NULL);
INSERT  IGNORE INTO `server_fsm_instances` VALUES (402,'order_request',212,'order_creation','FAILED',NULL,1,'List argument must consist only of tuples or dictionaries','2026-02-08 13:11:13','2026-02-08 13:13:21',NULL,NULL,NULL,NULL,NULL);
INSERT  IGNORE INTO `server_fsm_instances` VALUES (403,'order_request',213,'order_creation','COMPLETED',NULL,1,NULL,'2026-02-08 13:22:41','2026-02-08 13:22:43',NULL,NULL,NULL,NULL,NULL);
INSERT  IGNORE INTO `server_fsm_instances` VALUES (404,'order',1508,'order_assign_courier1','COMPLETED',NULL,1,NULL,'2026-02-08 14:16:12','2026-02-13 13:21:52',100,'courier',100,NULL,NULL);
INSERT  IGNORE INTO `server_fsm_instances` VALUES (405,'order',1508,'cancel_order','COMPLETED',NULL,1,NULL,'2026-02-08 14:16:52','2026-02-08 14:18:09',100,'courier',NULL,NULL,NULL);
INSERT  IGNORE INTO `server_fsm_instances` VALUES (408,'order_request',214,'order_creation','COMPLETED',NULL,1,NULL,'2026-02-10 15:14:02','2026-02-10 15:14:05',NULL,NULL,NULL,NULL,NULL);
INSERT  IGNORE INTO `server_fsm_instances` VALUES (409,'order_request',215,'order_creation','COMPLETED',NULL,1,NULL,'2026-02-10 17:07:27','2026-02-10 17:07:31',NULL,NULL,NULL,NULL,NULL);
INSERT  IGNORE INTO `server_fsm_instances` VALUES (410,'order',1508,'request_locker_access_code','COMPLETED',NULL,1,NULL,'2026-02-11 17:44:14','2026-04-04 15:19:10',100,'courier',100,NULL,'{\"leg\": \"pickup\"}');
INSERT  IGNORE INTO `server_fsm_instances` VALUES (413,'order',1510,'request_locker_access_code','COMPLETED',NULL,1,NULL,'2026-02-11 18:13:54','2026-02-12 10:40:34',1005,'client',NULL,NULL,'{\"leg\": \"pickup\"}');
INSERT  IGNORE INTO `server_fsm_instances` VALUES (420,'order',1507,'order_assign_courier1','COMPLETED',NULL,1,NULL,'2026-02-13 13:21:20','2026-02-13 13:21:22',100,'courier',100,NULL,NULL);
INSERT  IGNORE INTO `server_fsm_instances` VALUES (422,'order',1384,'cancel_order','COMPLETED',NULL,1,NULL,'2026-02-13 14:24:31','2026-02-13 14:24:35',1001,'client',NULL,NULL,NULL);
INSERT  IGNORE INTO `server_fsm_instances` VALUES (423,'order',1380,'cancel_order','COMPLETED',NULL,1,NULL,'2026-02-13 14:24:44','2026-02-13 14:24:45',1001,'client',NULL,NULL,NULL);
INSERT  IGNORE INTO `server_fsm_instances` VALUES (424,'order',1381,'cancel_order','COMPLETED',NULL,1,NULL,'2026-02-13 14:24:51','2026-02-13 14:24:55',1001,'client',NULL,NULL,NULL);
INSERT  IGNORE INTO `server_fsm_instances` VALUES (425,'order_request',216,'order_creation','COMPLETED',NULL,1,NULL,'2026-02-14 13:39:16','2026-02-14 13:39:19',NULL,NULL,NULL,NULL,NULL);
INSERT  IGNORE INTO `server_fsm_instances` VALUES (426,'order_request',217,'order_creation','COMPLETED',NULL,1,NULL,'2026-02-14 13:41:02','2026-02-14 13:41:06',NULL,NULL,NULL,NULL,NULL);
INSERT  IGNORE INTO `server_fsm_instances` VALUES (427,'order',1509,'order_assign_courier1','FAILED',NULL,1,'TARGET_USER_ID_NOT_SET','2026-02-14 13:50:56','2026-02-14 13:50:57',103,'courier',NULL,NULL,NULL);
INSERT  IGNORE INTO `server_fsm_instances` VALUES (428,'order_request',218,'order_creation','COMPLETED',NULL,1,NULL,'2026-02-14 14:13:45','2026-02-14 14:13:47',NULL,NULL,NULL,NULL,NULL);
INSERT  IGNORE INTO `server_fsm_instances` VALUES (429,'order',1513,'order_assign_courier1','COMPLETED',NULL,1,NULL,'2026-02-14 14:15:36','2026-02-16 08:22:03',103,'courier',103,'courier','{}');
INSERT  IGNORE INTO `server_fsm_instances` VALUES (431,'order',1513,'order_assign_courier2','FAILED',NULL,1,'ASSIGNMENT_FAILED','2026-02-16 08:23:05','2026-02-16 08:23:08',103,'courier',103,'courier','{}');
INSERT  IGNORE INTO `server_fsm_instances` VALUES (432,'order',1513,'open_cell','FAILED',NULL,1,'MISSING_PIN_IN_METADATA','2026-02-16 08:59:37','2026-03-21 13:50:22',103,'courier',103,NULL,'{}');
INSERT  IGNORE INTO `server_fsm_instances` VALUES (433,'order',1513,'close_cell','FAILED',NULL,1,'Неизвестный статус курьера: order_parcel_confirmed','2026-02-16 09:00:23','2026-03-21 13:50:22',103,'courier',103,NULL,'{}');
INSERT  IGNORE INTO `server_fsm_instances` VALUES (434,'order',1513,'bind_order_to_trip_after_confirmation','FAILED',NULL,1,'UNKNOWN_PROCESS: bind_order_to_trip_after_confirmation','2026-02-16 09:00:24','2026-02-16 09:00:24',0,'system',NULL,NULL,NULL);
INSERT  IGNORE INTO `server_fsm_instances` VALUES (435,'order',1513,'bind_order_to_trip','COMPLETED',NULL,1,NULL,'2026-02-16 09:43:35','2026-02-16 11:02:31',999999,'system',999999,'system','{}');
INSERT  IGNORE INTO `server_fsm_instances` VALUES (440,'order_request',219,'order_creation','COMPLETED',NULL,1,NULL,'2026-02-16 11:35:01','2026-02-16 11:35:02',NULL,NULL,NULL,NULL,NULL);
INSERT  IGNORE INTO `server_fsm_instances` VALUES (441,'order_request',220,'order_creation','COMPLETED',NULL,1,NULL,'2026-02-17 09:33:02','2026-02-17 09:39:07',NULL,NULL,NULL,NULL,NULL);
INSERT  IGNORE INTO `server_fsm_instances` VALUES (442,'order',1515,'order_assign_courier1','COMPLETED',NULL,1,NULL,'2026-02-17 09:42:51','2026-02-17 09:42:53',103,'courier',103,NULL,NULL);
INSERT  IGNORE INTO `server_fsm_instances` VALUES (443,'order',1515,'open_cell','COMPLETED',NULL,1,NULL,'2026-02-17 09:46:35','2026-02-17 09:46:38',103,'courier',103,'courier','{}');
INSERT  IGNORE INTO `server_fsm_instances` VALUES (444,'order',1515,'close_cell','FAILED',NULL,1,'Неизвестный статус курьера: order_parcel_confirmed','2026-02-17 09:47:27','2026-03-21 13:50:17',103,'courier',103,NULL,'{}');
INSERT  IGNORE INTO `server_fsm_instances` VALUES (445,'order',1515,'bind_order_to_trip','COMPLETED',NULL,1,NULL,'2026-02-17 09:47:28','2026-02-17 09:47:28',999999,'system',NULL,NULL,NULL);
INSERT  IGNORE INTO `server_fsm_instances` VALUES (446,'trip',29,'trip_assign_driver','FAILED',NULL,1,'ASSIGNMENT_FAILED','2026-02-17 09:59:48','2026-03-25 14:54:17',777,'operator',200,'driver','{\"action\": \"remove_driver\"}');
INSERT  IGNORE INTO `server_fsm_instances` VALUES (448,'order_request',221,'order_creation','COMPLETED',NULL,1,NULL,'2026-02-17 14:24:51','2026-02-17 14:24:51',NULL,NULL,NULL,NULL,NULL);
INSERT  IGNORE INTO `server_fsm_instances` VALUES (449,'order_request',222,'order_creation','COMPLETED',NULL,1,NULL,'2026-02-17 14:25:02','2026-02-17 14:25:06',NULL,NULL,NULL,NULL,NULL);
INSERT  IGNORE INTO `server_fsm_instances` VALUES (450,'order',1516,'order_assign_courier1','COMPLETED',NULL,1,NULL,'2026-02-17 14:25:45','2026-02-17 14:25:46',104,'courier',104,NULL,NULL);
INSERT  IGNORE INTO `server_fsm_instances` VALUES (451,'order',1517,'order_assign_courier1','COMPLETED',NULL,1,NULL,'2026-02-17 14:25:50','2026-02-17 14:25:51',104,'courier',104,NULL,NULL);
INSERT  IGNORE INTO `server_fsm_instances` VALUES (452,'order',1516,'open_cell','COMPLETED',NULL,1,NULL,'2026-02-17 14:27:30','2026-02-17 14:27:31',104,'courier',104,'courier','{}');
INSERT  IGNORE INTO `server_fsm_instances` VALUES (453,'order',1517,'open_cell','COMPLETED',NULL,1,NULL,'2026-02-17 14:28:21','2026-02-17 14:28:21',104,'courier',104,'courier','{}');
INSERT  IGNORE INTO `server_fsm_instances` VALUES (454,'order',1516,'close_cell','COMPLETED',NULL,1,NULL,'2026-02-17 14:29:37','2026-02-17 14:29:41',104,'courier',104,'courier','{}');
INSERT  IGNORE INTO `server_fsm_instances` VALUES (455,'order',1516,'bind_order_to_trip','COMPLETED',NULL,1,NULL,'2026-02-17 14:29:41','2026-02-17 14:29:41',999999,'system',NULL,NULL,NULL);
INSERT  IGNORE INTO `server_fsm_instances` VALUES (456,'order',1517,'close_cell','COMPLETED',NULL,1,NULL,'2026-02-17 14:30:00','2026-02-17 14:30:01',104,'courier',104,'courier','{}');
INSERT  IGNORE INTO `server_fsm_instances` VALUES (457,'order',1517,'bind_order_to_trip','COMPLETED',NULL,1,NULL,'2026-02-17 14:30:01','2026-02-17 14:30:01',999999,'system',NULL,NULL,NULL);
INSERT  IGNORE INTO `server_fsm_instances` VALUES (458,'order_request',223,'order_creation','COMPLETED',NULL,1,NULL,'2026-02-17 14:44:18','2026-02-17 14:44:22',NULL,NULL,NULL,NULL,NULL);
INSERT  IGNORE INTO `server_fsm_instances` VALUES (459,'order',1518,'order_assign_courier1','COMPLETED',NULL,1,NULL,'2026-02-17 14:44:34','2026-02-17 14:44:37',104,'courier',104,NULL,NULL);
INSERT  IGNORE INTO `server_fsm_instances` VALUES (460,'order',1518,'open_cell','FAILED',NULL,1,'ROLE_NOT_SUPPORTED_driver','2026-02-17 14:45:13','2026-02-17 15:27:47',200,'driver',200,'driver','{}');
INSERT  IGNORE INTO `server_fsm_instances` VALUES (461,'order',1518,'close_cell','COMPLETED',NULL,1,NULL,'2026-02-17 14:45:42','2026-02-17 14:45:47',104,'courier',104,'courier','{}');
INSERT  IGNORE INTO `server_fsm_instances` VALUES (462,'order',1518,'bind_order_to_trip','COMPLETED',NULL,1,NULL,'2026-02-17 14:45:47','2026-02-17 14:45:47',999999,'system',NULL,NULL,NULL);
INSERT  IGNORE INTO `server_fsm_instances` VALUES (463,'order_request',224,'order_creation','FAILED',NULL,1,'NO_FREE_CELLS','2026-02-17 14:50:21','2026-02-17 14:50:22',NULL,NULL,NULL,NULL,NULL);
INSERT  IGNORE INTO `server_fsm_instances` VALUES (464,'order_request',225,'order_creation','COMPLETED',NULL,1,NULL,'2026-02-17 14:50:50','2026-02-17 14:50:52',NULL,NULL,NULL,NULL,NULL);
INSERT  IGNORE INTO `server_fsm_instances` VALUES (465,'order_request',226,'order_creation','COMPLETED',NULL,1,NULL,'2026-02-17 14:51:04','2026-02-17 14:51:07',NULL,NULL,NULL,NULL,NULL);
INSERT  IGNORE INTO `server_fsm_instances` VALUES (466,'order',1519,'order_assign_courier1','COMPLETED',NULL,1,NULL,'2026-02-17 14:51:14','2026-02-17 14:51:17',104,'courier',104,NULL,NULL);
INSERT  IGNORE INTO `server_fsm_instances` VALUES (467,'order',1520,'order_assign_courier1','COMPLETED',NULL,1,NULL,'2026-02-17 14:51:23','2026-02-17 14:51:27',104,'courier',104,NULL,NULL);
INSERT  IGNORE INTO `server_fsm_instances` VALUES (468,'order',1519,'open_cell','COMPLETED',NULL,1,NULL,'2026-02-17 14:52:08','2026-02-17 14:52:13',104,'courier',104,'courier','{}');
INSERT  IGNORE INTO `server_fsm_instances` VALUES (469,'order',1520,'open_cell','COMPLETED',NULL,1,NULL,'2026-02-17 14:52:20','2026-02-17 14:52:23',104,'courier',104,'courier','{}');
INSERT  IGNORE INTO `server_fsm_instances` VALUES (470,'order',1519,'close_cell','COMPLETED',NULL,1,NULL,'2026-02-17 14:52:41','2026-02-17 14:52:43',104,'courier',104,'courier','{}');
INSERT  IGNORE INTO `server_fsm_instances` VALUES (471,'order',1519,'bind_order_to_trip','COMPLETED',NULL,1,NULL,'2026-02-17 14:52:43','2026-02-17 14:52:43',999999,'system',NULL,NULL,NULL);
INSERT  IGNORE INTO `server_fsm_instances` VALUES (472,'order',1520,'close_cell','COMPLETED',NULL,1,NULL,'2026-02-17 14:52:47','2026-02-17 14:52:48',104,'courier',104,'courier','{}');
INSERT  IGNORE INTO `server_fsm_instances` VALUES (473,'order',1520,'bind_order_to_trip','COMPLETED',NULL,1,NULL,'2026-02-17 14:52:48','2026-02-17 14:52:48',999999,'system',NULL,NULL,NULL);
INSERT  IGNORE INTO `server_fsm_instances` VALUES (474,'order_request',227,'order_creation','COMPLETED',NULL,1,NULL,'2026-02-17 15:07:30','2026-02-17 15:07:33',NULL,NULL,NULL,NULL,NULL);
INSERT  IGNORE INTO `server_fsm_instances` VALUES (475,'order_request',228,'order_creation','COMPLETED',NULL,1,NULL,'2026-02-17 15:07:30','2026-02-17 15:07:33',NULL,NULL,NULL,NULL,NULL);
INSERT  IGNORE INTO `server_fsm_instances` VALUES (476,'order',1521,'order_assign_courier1','COMPLETED',NULL,1,NULL,'2026-02-17 15:07:47','2026-02-17 15:07:48',104,'courier',104,NULL,NULL);
INSERT  IGNORE INTO `server_fsm_instances` VALUES (477,'order',1522,'order_assign_courier1','COMPLETED',NULL,1,NULL,'2026-02-17 15:07:53','2026-02-17 15:07:53',104,'courier',104,NULL,NULL);
INSERT  IGNORE INTO `server_fsm_instances` VALUES (478,'order',1521,'open_cell','COMPLETED',NULL,1,NULL,'2026-02-17 15:08:49','2026-02-17 15:08:52',104,'courier',104,'courier','{}');
INSERT  IGNORE INTO `server_fsm_instances` VALUES (479,'order',1522,'open_cell','COMPLETED',NULL,1,NULL,'2026-02-17 15:08:58','2026-02-17 15:09:02',104,'courier',104,'courier','{}');
INSERT  IGNORE INTO `server_fsm_instances` VALUES (480,'order',1521,'close_cell','COMPLETED',NULL,1,NULL,'2026-02-17 15:09:20','2026-02-17 15:09:22',104,'courier',104,'courier','{}');
INSERT  IGNORE INTO `server_fsm_instances` VALUES (481,'order',1521,'bind_order_to_trip','COMPLETED',NULL,1,NULL,'2026-02-17 15:09:22','2026-02-17 15:09:22',999999,'system',NULL,NULL,NULL);
INSERT  IGNORE INTO `server_fsm_instances` VALUES (482,'order',1522,'close_cell','COMPLETED',NULL,1,NULL,'2026-02-17 15:09:25','2026-02-17 15:09:27',104,'courier',104,'courier','{}');
INSERT  IGNORE INTO `server_fsm_instances` VALUES (483,'order',1522,'bind_order_to_trip','COMPLETED',NULL,1,NULL,'2026-02-17 15:09:27','2026-02-17 15:09:27',999999,'system',NULL,NULL,NULL);
INSERT  IGNORE INTO `server_fsm_instances` VALUES (484,'order_request',229,'order_creation','FAILED',NULL,1,'NO_FREE_CELLS','2026-02-17 15:12:42','2026-02-17 15:12:46',NULL,NULL,NULL,NULL,NULL);
INSERT  IGNORE INTO `server_fsm_instances` VALUES (485,'order_request',230,'order_creation','COMPLETED',NULL,1,NULL,'2026-02-17 15:12:54','2026-02-17 15:12:56',NULL,NULL,NULL,NULL,NULL);
INSERT  IGNORE INTO `server_fsm_instances` VALUES (486,'order',1523,'order_assign_courier1','COMPLETED',NULL,1,NULL,'2026-02-17 15:13:06','2026-02-17 15:13:11',104,'courier',104,NULL,NULL);
INSERT  IGNORE INTO `server_fsm_instances` VALUES (487,'order',1523,'open_cell','COMPLETED',NULL,1,NULL,'2026-02-17 15:13:40','2026-02-17 15:13:41',104,'courier',104,'courier','{}');
INSERT  IGNORE INTO `server_fsm_instances` VALUES (488,'order',1523,'close_cell','COMPLETED',NULL,1,NULL,'2026-02-17 15:13:47','2026-02-17 15:13:51',104,'courier',104,'courier','{}');
INSERT  IGNORE INTO `server_fsm_instances` VALUES (489,'order',1523,'bind_order_to_trip','COMPLETED',NULL,1,NULL,'2026-02-17 15:13:51','2026-02-17 15:13:51',999999,'system',NULL,NULL,NULL);
INSERT  IGNORE INTO `server_fsm_instances` VALUES (490,'trip',34,'trip_assign_driver','FAILED',NULL,1,'ASSIGNMENT_FAILED','2026-02-17 15:24:01','2026-03-26 13:40:21',777,'operator',201,'driver','{}');
INSERT  IGNORE INTO `server_fsm_instances` VALUES (492,'locker',36,'open_cell','COMPLETED',NULL,1,NULL,'2026-02-17 16:05:25','2026-02-20 14:20:53',200,'driver',200,'driver','{}');
INSERT  IGNORE INTO `server_fsm_instances` VALUES (496,'order_request',231,'order_creation','FAILED',NULL,1,'NO_FREE_CELLS','2026-02-17 18:04:21','2026-02-17 18:04:23',NULL,NULL,NULL,NULL,NULL);
INSERT  IGNORE INTO `server_fsm_instances` VALUES (497,'order_request',232,'order_creation','FAILED',NULL,1,'NO_FREE_CELLS','2026-02-17 18:04:49','2026-02-17 18:04:53',NULL,NULL,NULL,NULL,NULL);
INSERT  IGNORE INTO `server_fsm_instances` VALUES (498,'order_request',233,'order_creation','COMPLETED',NULL,1,NULL,'2026-02-17 18:05:53','2026-02-17 18:05:53',NULL,NULL,NULL,NULL,NULL);
INSERT  IGNORE INTO `server_fsm_instances` VALUES (499,'order',1524,'order_assign_courier1','COMPLETED',NULL,1,NULL,'2026-02-17 18:07:08','2026-02-17 18:07:08',104,'courier',104,NULL,NULL);
INSERT  IGNORE INTO `server_fsm_instances` VALUES (500,'order',1524,'open_cell','FAILED',NULL,1,'MISSING_PIN_IN_METADATA','2026-02-17 18:07:55','2026-03-21 13:50:38',104,'courier',104,NULL,'{}');
INSERT  IGNORE INTO `server_fsm_instances` VALUES (501,'order',1524,'close_cell','FAILED',NULL,1,'Неизвестный статус курьера: order_parcel_confirmed','2026-02-17 18:08:11','2026-03-21 13:50:38',104,'courier',104,NULL,'{}');
INSERT  IGNORE INTO `server_fsm_instances` VALUES (502,'order',1524,'bind_order_to_trip','COMPLETED',NULL,1,NULL,'2026-02-17 18:08:13','2026-02-17 18:08:13',999999,'system',NULL,NULL,NULL);
INSERT  IGNORE INTO `server_fsm_instances` VALUES (505,'locker',33,'open_cell','FAILED',NULL,1,'FSM locker_open_locker: (mysql.connector.errors.DatabaseError) 1267 (HY000): Illegal mix of collations (utf8mb4_0900_ai_ci,IMPLICIT) and (utf8mb4_unicode_ci,IMPLICIT) for operation \'=\'\n[SQL: \n                    CALL fsm_perform_action(\n                        %(entity_type)s,\n                        %(entity_id)s,\n                        %(action_name)s,\n                        %(user_id)s,\n                        %(extra_id)s\n                    )\n                ]\n[parameters: {\'entity_type\': \'locker\', \'entity_id\': 33, \'action_name\': \'locker_open_locker\', \'user_id\': 200, \'extra_id\': \'\'}]\n(Background on this error at: https://sqlalche.me/e/20/4xp6)','2026-02-17 19:35:37','2026-02-18 08:59:38',200,'driver',200,'driver','{}');
INSERT  IGNORE INTO `server_fsm_instances` VALUES (506,'order',1514,'order_assign_courier1','FAILED',NULL,1,'ASSIGNMENT_FAILED','2026-02-18 08:45:37','2026-02-18 08:45:42',100,'courier',100,NULL,NULL);
INSERT  IGNORE INTO `server_fsm_instances` VALUES (508,'locker',39,'open_cell','COMPLETED',NULL,1,NULL,'2026-02-18 09:06:10','2026-02-18 15:15:22',200,'driver',200,'driver','{}');
INSERT  IGNORE INTO `server_fsm_instances` VALUES (523,'locker',39,'close_cell','COMPLETED',NULL,1,NULL,'2026-02-18 15:21:41','2026-02-18 16:03:09',200,'driver',200,'driver','{}');
INSERT  IGNORE INTO `server_fsm_instances` VALUES (527,'trip',34,'start_trip','COMPLETED',NULL,1,NULL,'2026-02-19 08:39:19','2026-02-20 14:51:32',200,'driver',200,'driver','{}');
INSERT  IGNORE INTO `server_fsm_instances` VALUES (529,'locker',33,'close_cell','COMPLETED',NULL,1,NULL,'2026-02-20 11:40:47','2026-02-20 14:16:03',200,'driver',200,'driver','{}');
INSERT  IGNORE INTO `server_fsm_instances` VALUES (532,'locker',40,'open_cell','COMPLETED',NULL,1,NULL,'2026-02-20 14:23:27','2026-02-20 14:23:29',200,'driver',200,'driver','{}');
INSERT  IGNORE INTO `server_fsm_instances` VALUES (533,'locker',34,'open_cell','COMPLETED',NULL,1,NULL,'2026-02-20 14:23:40','2026-02-20 14:23:44',200,'driver',200,'driver','{}');
INSERT  IGNORE INTO `server_fsm_instances` VALUES (534,'locker',36,'close_cell','COMPLETED',NULL,1,NULL,'2026-02-20 14:24:01','2026-02-20 14:24:04',200,'driver',200,'driver','{}');
INSERT  IGNORE INTO `server_fsm_instances` VALUES (535,'locker',34,'close_cell','COMPLETED',NULL,1,NULL,'2026-02-20 14:24:10','2026-02-20 14:24:14',200,'driver',200,'driver','{}');
INSERT  IGNORE INTO `server_fsm_instances` VALUES (536,'locker',40,'close_cell','COMPLETED',NULL,1,NULL,'2026-02-20 14:24:15','2026-02-20 14:24:19',200,'driver',200,'driver','{}');
INSERT  IGNORE INTO `server_fsm_instances` VALUES (540,'order_request',234,'order_creation','FAILED',NULL,1,'SELF_CITY_NOT_ALLOWED: МСК','2026-02-21 10:03:37','2026-02-21 10:03:40',NULL,NULL,NULL,NULL,NULL);
INSERT  IGNORE INTO `server_fsm_instances` VALUES (541,'order_request',235,'order_creation','FAILED',NULL,1,'SELF_CITY_NOT_ALLOWED: МСК','2026-02-21 10:04:36','2026-02-21 10:04:40',NULL,NULL,NULL,NULL,NULL);
INSERT  IGNORE INTO `server_fsm_instances` VALUES (542,'order_request',236,'order_creation','FAILED',NULL,1,'SELF_CITY_NOT_ALLOWED: МСК','2026-02-21 10:05:23','2026-02-21 10:05:25',NULL,NULL,NULL,NULL,NULL);
INSERT  IGNORE INTO `server_fsm_instances` VALUES (543,'order_request',237,'order_creation','FAILED',NULL,1,'NO_FREE_CELLS','2026-02-21 10:10:36','2026-02-21 10:10:40',NULL,NULL,NULL,NULL,NULL);
INSERT  IGNORE INTO `server_fsm_instances` VALUES (544,'locker',18,'report_error','COMPLETED',NULL,1,NULL,'2026-02-24 14:40:49','2026-02-24 14:40:52',200,'driver',NULL,NULL,'{\"trip_id\": 33, \"order_id\": 1516, \"error_type\": \"locker_failed_to_open\"}');
INSERT  IGNORE INTO `server_fsm_instances` VALUES (545,'trip',34,'report_error','COMPLETED',NULL,1,NULL,'2026-02-24 16:09:49','2026-02-24 16:16:13',200,'driver',NULL,NULL,'{\"trip_id\": 34, \"error_type\": \"trip_breakdown\"}');
INSERT  IGNORE INTO `server_fsm_instances` VALUES (547,'order',305,'arrive_at_destination','FAILED',NULL,1,'FSM trip_end_delivery failed: 1644 (45000): Unknown from_state for trip in fsm_states','2026-02-25 06:07:35','2026-02-25 06:07:36',1,'driver',1,NULL,NULL);
INSERT  IGNORE INTO `server_fsm_instances` VALUES (551,'order',30,'trip_assign_driver','FAILED',NULL,1,'ASSIGNMENT_FAILED','2026-02-25 06:13:08','2026-02-27 13:52:10',200,'driver',200,NULL,NULL);
INSERT  IGNORE INTO `server_fsm_instances` VALUES (553,'order_request',238,'order_creation','FAILED',NULL,1,'SELF_CITY_NOT_ALLOWED: МСК','2026-02-25 07:00:51','2026-02-25 07:00:53',NULL,NULL,NULL,NULL,NULL);
INSERT  IGNORE INTO `server_fsm_instances` VALUES (554,'trip',33,'start_trip','COMPLETED',NULL,1,NULL,'2026-02-25 07:27:33','2026-02-25 07:27:34',201,'driver',201,'driver','{}');
INSERT  IGNORE INTO `server_fsm_instances` VALUES (555,'locker',9,'open_cell','FAILED',NULL,1,'Заказ 661 не привязан к рейсу','2026-02-25 07:51:53','2026-02-25 09:41:45',201,'driver',201,'driver','{}');
INSERT  IGNORE INTO `server_fsm_instances` VALUES (556,'order_request',239,'order_creation','FAILED',NULL,1,'SELF_CITY_NOT_ALLOWED: СПБ','2026-02-25 08:30:55','2026-02-25 08:30:57',NULL,NULL,NULL,NULL,NULL);
INSERT  IGNORE INTO `server_fsm_instances` VALUES (558,'order_request',240,'order_creation','FAILED',NULL,1,'NO_FREE_CELLS','2026-02-25 10:15:22','2026-02-25 10:15:22',NULL,NULL,NULL,NULL,NULL);
INSERT  IGNORE INTO `server_fsm_instances` VALUES (559,'order_request',241,'order_creation','FAILED',NULL,1,'NO_FREE_CELLS','2026-02-25 10:15:36','2026-02-25 10:15:37',NULL,NULL,NULL,NULL,NULL);
INSERT  IGNORE INTO `server_fsm_instances` VALUES (560,'order_request',242,'order_creation','COMPLETED',NULL,1,NULL,'2026-02-25 10:16:15','2026-02-25 10:16:17',NULL,NULL,NULL,NULL,NULL);
INSERT  IGNORE INTO `server_fsm_instances` VALUES (561,'order',1525,'order_assign_courier1','COMPLETED',NULL,1,NULL,'2026-02-25 11:44:51','2026-02-25 11:44:51',100,'courier',100,NULL,NULL);
INSERT  IGNORE INTO `server_fsm_instances` VALUES (562,'locker',28,'open_cell','COMPLETED',NULL,1,NULL,'2026-02-25 11:46:31','2026-02-26 08:36:42',201,'driver',201,'driver','{}');
INSERT  IGNORE INTO `server_fsm_instances` VALUES (563,'order',1525,'open_cell','FAILED',NULL,1,'MISSING_PIN_IN_METADATA','2026-02-25 11:53:19','2026-03-21 13:50:17',103,'courier',103,NULL,'{}');
INSERT  IGNORE INTO `server_fsm_instances` VALUES (564,'order',1525,'close_cell','FAILED',NULL,1,'Неизвестный статус курьера: order_completed','2026-02-25 11:53:33','2026-04-04 15:57:18',100,'courier',100,NULL,'{}');
INSERT  IGNORE INTO `server_fsm_instances` VALUES (565,'order',1525,'bind_order_to_trip','COMPLETED',NULL,1,NULL,'2026-02-25 11:53:37','2026-02-25 11:53:37',999999,'system',NULL,NULL,NULL);
INSERT  IGNORE INTO `server_fsm_instances` VALUES (567,'trip',36,'trip_assign_driver','COMPLETED',NULL,1,NULL,'2026-02-25 12:00:15','2026-02-26 08:30:07',201,'driver',201,'driver','{}');
INSERT  IGNORE INTO `server_fsm_instances` VALUES (570,'locker',28,'close_cell','COMPLETED',NULL,1,NULL,'2026-02-25 12:11:07','2026-02-26 08:37:03',201,'driver',201,'driver','{}');
INSERT  IGNORE INTO `server_fsm_instances` VALUES (571,'trip',36,'start_trip','COMPLETED',NULL,1,NULL,'2026-02-25 12:11:58','2026-02-26 08:40:48',201,'driver',201,'driver','{}');
INSERT  IGNORE INTO `server_fsm_instances` VALUES (572,'locker',38,'open_cell','COMPLETED',NULL,1,NULL,'2026-02-25 12:15:02','2026-02-26 08:41:33',201,'driver',201,'driver','{}');
INSERT  IGNORE INTO `server_fsm_instances` VALUES (573,'locker',38,'close_cell','COMPLETED',NULL,1,NULL,'2026-02-25 12:16:03','2026-02-26 08:41:53',201,'driver',201,'driver','{}');
INSERT  IGNORE INTO `server_fsm_instances` VALUES (574,'order',36,'trip_assign_driver','FAILED',NULL,1,'ASSIGNMENT_FAILED','2026-02-26 07:57:14','2026-02-26 07:57:16',200,'driver',200,NULL,NULL);
INSERT  IGNORE INTO `server_fsm_instances` VALUES (584,'trip',36,'complete_trip','COMPLETED',NULL,1,NULL,'2026-02-26 11:39:22','2026-02-26 11:39:23',201,'driver',201,'driver','{}');
INSERT  IGNORE INTO `server_fsm_instances` VALUES (585,'order',1525,'order_assign_courier2','COMPLETED',NULL,1,NULL,'2026-02-27 08:16:26','2026-02-27 08:16:29',103,'courier',103,'courier','{}');
INSERT  IGNORE INTO `server_fsm_instances` VALUES (589,'trip',30,'trip_assign_driver','COMPLETED',NULL,1,NULL,'2026-02-27 14:05:15','2026-02-27 14:05:16',200,'driver',200,'driver','{}');
INSERT  IGNORE INTO `server_fsm_instances` VALUES (590,'trip',31,'trip_assign_driver','COMPLETED',NULL,1,NULL,'2026-02-27 14:07:06','2026-02-27 14:07:11',200,'driver',200,'driver','{}');
INSERT  IGNORE INTO `server_fsm_instances` VALUES (591,'order',1506,'order_assign_courier1','COMPLETED',NULL,1,NULL,'2026-02-27 15:15:01','2026-02-27 15:15:04',100,'courier',100,NULL,NULL);
INSERT  IGNORE INTO `server_fsm_instances` VALUES (592,'order_request',243,'order_creation','FAILED',NULL,1,'SELF_CITY_NOT_ALLOWED: МСК','2026-02-27 15:25:52','2026-02-27 15:25:54',NULL,NULL,NULL,NULL,NULL);
INSERT  IGNORE INTO `server_fsm_instances` VALUES (593,'order',1525,'request_locker_access_code','FAILED',NULL,1,'CODE_NOT_ALLOWED_IN_order_completed','2026-02-28 06:03:26','2026-04-02 14:41:09',100,'courier',100,NULL,'{\"leg\": \"pickup\"}');
INSERT  IGNORE INTO `server_fsm_instances` VALUES (595,'order',1525,'confirm_courier2_delivery','FAILED',NULL,1,'INVALID_CODE: Код неактивен (статус: USED)','2026-02-28 06:16:31','2026-03-19 14:51:00',100,'courier',100,NULL,'{\"pin\": \"111\"}');
INSERT  IGNORE INTO `server_fsm_instances` VALUES (600,'order',102,'request_locker_access_code','FAILED',NULL,1,'ORDER_NOT_FOUND','2026-03-01 12:03:03','2026-03-01 12:03:08',2001,'recipient',2001,NULL,'{\"leg\": \"delivery\"}');
INSERT  IGNORE INTO `server_fsm_instances` VALUES (601,'order',1514,'request_locker_access_code','COMPLETED',NULL,1,NULL,'2026-03-02 08:16:35','2026-04-01 10:17:17',100,'courier',100,NULL,'{\"leg\": \"pickup\"}');
INSERT  IGNORE INTO `server_fsm_instances` VALUES (603,'order_request',244,'order_creation','FAILED',NULL,1,'NO_FREE_CELLS','2026-03-02 09:01:05','2026-03-02 09:01:06',NULL,NULL,NULL,NULL,NULL);
INSERT  IGNORE INTO `server_fsm_instances` VALUES (604,'order_request',245,'order_creation','FAILED',NULL,1,'NO_FREE_CELLS','2026-03-02 09:01:22','2026-03-02 09:01:26',NULL,NULL,NULL,NULL,NULL);
INSERT  IGNORE INTO `server_fsm_instances` VALUES (605,'order_request',246,'order_creation','FAILED',NULL,1,'NO_FREE_CELLS','2026-03-02 09:01:49','2026-03-02 09:01:51',NULL,NULL,NULL,NULL,NULL);
INSERT  IGNORE INTO `server_fsm_instances` VALUES (606,'order_request',247,'order_creation','COMPLETED',NULL,1,NULL,'2026-03-02 09:02:59','2026-03-02 09:03:01',NULL,NULL,NULL,NULL,NULL);
INSERT  IGNORE INTO `server_fsm_instances` VALUES (607,'order',1526,'request_locker_access_code','COMPLETED',NULL,1,NULL,'2026-03-02 09:04:33','2026-04-01 09:45:31',1001,'client',1001,NULL,'{\"leg\": \"pickup\"}');
INSERT  IGNORE INTO `server_fsm_instances` VALUES (610,'trip',32,'trip_assign_driver','COMPLETED',NULL,1,NULL,'2026-03-08 08:17:37','2026-03-08 08:17:42',201,'driver',201,'driver','{}');
INSERT  IGNORE INTO `server_fsm_instances` VALUES (611,'order_request',248,'order_creation','COMPLETED',NULL,1,NULL,'2026-03-15 13:26:11','2026-03-15 13:26:16',NULL,NULL,NULL,NULL,NULL);
INSERT  IGNORE INTO `server_fsm_instances` VALUES (612,'order',1527,'open_cell','FAILED',NULL,1,'MISSING_PIN_IN_METADATA','2026-03-15 13:28:54','2026-03-23 06:23:09',1001,'client',1001,NULL,'{}');
INSERT  IGNORE INTO `server_fsm_instances` VALUES (613,'order',1527,'request_locker_access_code','COMPLETED',NULL,1,NULL,'2026-03-15 13:30:55','2026-03-19 13:53:03',200,'driver',200,'driver','{\"leg\": \"delivery\"}');
INSERT  IGNORE INTO `server_fsm_instances` VALUES (617,'order',1527,'close_cell','FAILED',NULL,1,'FSM order_confirm_parcel_in failed: 1644 (45000): Invalid transition for order: no matching fsm_transitions','2026-03-15 13:36:34','2026-04-06 11:39:24',1001,'client',1001,NULL,'{}');
INSERT  IGNORE INTO `server_fsm_instances` VALUES (618,'order',1527,'bind_order_to_trip','COMPLETED',NULL,1,NULL,'2026-03-15 13:36:36','2026-03-15 13:36:36',999999,'system',NULL,NULL,NULL);
INSERT  IGNORE INTO `server_fsm_instances` VALUES (619,'order_request',249,'order_creation','COMPLETED',NULL,1,NULL,'2026-03-15 13:44:10','2026-03-15 13:44:12',NULL,NULL,NULL,NULL,NULL);
INSERT  IGNORE INTO `server_fsm_instances` VALUES (621,'order',1528,'request_locker_access_code','FAILED',NULL,1,'MISSING_METADATA','2026-03-15 13:46:20','2026-04-02 14:54:09',1001,'client',1001,NULL,'{}');
INSERT  IGNORE INTO `server_fsm_instances` VALUES (622,'order',1528,'open_cell','FAILED',NULL,1,'ROLE_NOT_SUPPORTED_driver','2026-03-15 13:46:57','2026-03-23 15:52:23',200,'driver',200,'driver','{\"leg\": \"pickup\", \"pin\": \"436412\"}');
INSERT  IGNORE INTO `server_fsm_instances` VALUES (623,'order',1528,'close_cell','FAILED',NULL,1,'FSM order_confirm_parcel_in failed: 1644 (45000): Invalid transition for order: no matching fsm_transitions','2026-03-15 13:47:20','2026-04-04 17:37:07',1001,'client',1001,NULL,'{}');
INSERT  IGNORE INTO `server_fsm_instances` VALUES (624,'order',1528,'bind_order_to_trip','COMPLETED',NULL,1,NULL,'2026-03-15 13:47:22','2026-03-15 13:47:22',999999,'system',NULL,NULL,NULL);
INSERT  IGNORE INTO `server_fsm_instances` VALUES (625,'direction',1,'direction_reserve_slot','COMPLETED',NULL,1,NULL,'2026-03-15 13:51:29','2026-04-01 09:55:18',200,'driver',200,'driver','{\"capacity\": 1}');
INSERT  IGNORE INTO `server_fsm_instances` VALUES (626,'order_request',250,'order_creation','COMPLETED',NULL,1,NULL,'2026-03-16 08:43:24','2026-03-16 08:43:25',NULL,NULL,NULL,NULL,NULL);
INSERT  IGNORE INTO `server_fsm_instances` VALUES (627,'order',1529,'order_assign_courier1','COMPLETED',NULL,1,NULL,'2026-03-16 08:43:54','2026-03-16 08:43:55',100,'courier',100,NULL,'{}');
INSERT  IGNORE INTO `server_fsm_instances` VALUES (628,'order',1514,'cancel_order','FAILED',NULL,1,'CANNOT_CANCEL_FROM_order_created','2026-03-16 08:46:37','2026-03-16 08:46:40',100,'courier',100,NULL,'{}');
INSERT  IGNORE INTO `server_fsm_instances` VALUES (630,'order',1529,'confirm_courier2_delivery','FAILED',NULL,1,'INVALID_CODE: Код подтверждения не найден для этого заказа','2026-03-16 09:56:49','2026-03-19 14:36:24',100,'courier',100,NULL,'{\"pin\": \"111\"}');
INSERT  IGNORE INTO `server_fsm_instances` VALUES (641,'direction',1,'direction_start_loading','FAILED',NULL,1,'START_LOADING_FAILED: FSM driver_reservation_start_loading failed: 1644 (45000): Invalid transition for driver_reservations: no matching fsm_transitions','2026-03-16 13:29:08','2026-03-22 08:30:37',200,'driver',200,'driver','{}');
INSERT  IGNORE INTO `server_fsm_instances` VALUES (650,'direction',1,'direction_complete_loading','COMPLETED',NULL,1,NULL,'2026-03-17 15:47:09','2026-04-01 09:56:29',200,'driver',200,'driver','{}');
INSERT  IGNORE INTO `server_fsm_instances` VALUES (655,'locker',5,'open_cell','COMPLETED',NULL,1,NULL,'2026-03-18 14:29:06','2026-03-18 15:38:21',200,'driver',200,'driver','{\"leg\": \"pickup\", \"pin\": \"964884\"}');
INSERT  IGNORE INTO `server_fsm_instances` VALUES (656,'locker',5,'request_locker_access_code','FAILED',NULL,1,'UNSUPPORTED_ENTITY_TYPE','2026-03-18 14:31:02','2026-03-18 14:31:05',200,'driver',200,'driver','{\"leg\": \"pickup\"}');
INSERT  IGNORE INTO `server_fsm_instances` VALUES (667,'locker',5,'close_cell','COMPLETED',NULL,1,NULL,'2026-03-18 16:15:27','2026-03-18 16:15:32',200,'driver',200,'driver','{}');
INSERT  IGNORE INTO `server_fsm_instances` VALUES (669,'order_request',251,'order_creation','COMPLETED',NULL,1,NULL,'2026-03-19 07:24:35','2026-03-19 07:24:40',NULL,NULL,NULL,NULL,NULL);
INSERT  IGNORE INTO `server_fsm_instances` VALUES (670,'order',1530,'cancel_order','COMPLETED',NULL,1,NULL,'2026-03-19 07:43:36','2026-03-19 07:43:40',1001,'client',1001,NULL,'{}');
INSERT  IGNORE INTO `server_fsm_instances` VALUES (671,'order_request',252,'order_creation','COMPLETED',NULL,1,NULL,'2026-03-19 07:44:09','2026-03-19 07:44:10',NULL,NULL,NULL,NULL,NULL);
INSERT  IGNORE INTO `server_fsm_instances` VALUES (672,'order_request',253,'order_creation','COMPLETED',NULL,1,NULL,'2026-03-19 07:55:10','2026-03-19 07:55:11',NULL,NULL,NULL,NULL,NULL);
INSERT  IGNORE INTO `server_fsm_instances` VALUES (673,'order_request',254,'order_creation','COMPLETED',NULL,1,NULL,'2026-03-19 08:02:31','2026-03-19 08:02:36',NULL,NULL,NULL,NULL,NULL);
INSERT  IGNORE INTO `server_fsm_instances` VALUES (674,'order_request',255,'order_creation','FAILED',NULL,1,'NO_FREE_CELLS','2026-03-19 08:02:37','2026-03-19 08:02:41',NULL,NULL,NULL,NULL,NULL);
INSERT  IGNORE INTO `server_fsm_instances` VALUES (675,'order_request',256,'order_creation','FAILED',NULL,1,'NO_FREE_CELLS','2026-03-19 08:02:37','2026-03-19 08:02:41',NULL,NULL,NULL,NULL,NULL);
INSERT  IGNORE INTO `server_fsm_instances` VALUES (676,'order_request',257,'order_creation','FAILED',NULL,1,'NO_FREE_CELLS','2026-03-19 08:02:37','2026-03-19 08:02:41',NULL,NULL,NULL,NULL,NULL);
INSERT  IGNORE INTO `server_fsm_instances` VALUES (677,'order_request',258,'order_creation','FAILED',NULL,1,'NO_FREE_CELLS','2026-03-19 08:02:38','2026-03-19 08:02:41',NULL,NULL,NULL,NULL,NULL);
INSERT  IGNORE INTO `server_fsm_instances` VALUES (678,'order_request',259,'order_creation','FAILED',NULL,1,'NO_FREE_CELLS','2026-03-19 08:02:38','2026-03-19 08:02:41',NULL,NULL,NULL,NULL,NULL);
INSERT  IGNORE INTO `server_fsm_instances` VALUES (679,'order_request',260,'order_creation','FAILED',NULL,1,'NO_FREE_CELLS','2026-03-19 08:02:50','2026-03-19 08:02:51',NULL,NULL,NULL,NULL,NULL);
INSERT  IGNORE INTO `server_fsm_instances` VALUES (680,'order_request',261,'order_creation','FAILED',NULL,1,'NO_FREE_CELLS','2026-03-19 08:02:50','2026-03-19 08:02:51',NULL,NULL,NULL,NULL,NULL);
INSERT  IGNORE INTO `server_fsm_instances` VALUES (681,'order_request',262,'order_creation','FAILED',NULL,1,'NO_FREE_CELLS','2026-03-19 08:02:50','2026-03-19 08:02:51',NULL,NULL,NULL,NULL,NULL);
INSERT  IGNORE INTO `server_fsm_instances` VALUES (682,'order_request',263,'order_creation','FAILED',NULL,1,'NO_FREE_CELLS','2026-03-19 08:02:54','2026-03-19 08:02:56',NULL,NULL,NULL,NULL,NULL);
INSERT  IGNORE INTO `server_fsm_instances` VALUES (683,'order_request',264,'order_creation','FAILED',NULL,1,'NO_FREE_CELLS','2026-03-19 08:02:54','2026-03-19 08:02:56',NULL,NULL,NULL,NULL,NULL);
INSERT  IGNORE INTO `server_fsm_instances` VALUES (685,'trip',38,'start_trip','COMPLETED',NULL,1,NULL,'2026-03-19 10:11:11','2026-03-19 10:11:13',200,'driver',200,'driver','{}');
INSERT  IGNORE INTO `server_fsm_instances` VALUES (686,'trip',38,'complete_trip','COMPLETED',NULL,1,NULL,'2026-03-19 13:12:00','2026-03-19 14:58:14',200,'driver',200,'driver','{}');
INSERT  IGNORE INTO `server_fsm_instances` VALUES (687,'locker',15,'open_cell','COMPLETED',NULL,1,NULL,'2026-03-19 13:13:31','2026-03-19 14:01:01',200,'driver',200,'driver','{\"leg\": \"delivery\", \"pin\": \"896353\"}');
INSERT  IGNORE INTO `server_fsm_instances` VALUES (697,'locker',15,'close_cell','COMPLETED',NULL,1,NULL,'2026-03-19 14:07:28','2026-03-19 14:07:28',200,'driver',200,'driver','{}');
INSERT  IGNORE INTO `server_fsm_instances` VALUES (701,'order',1529,'cancel_order','COMPLETED',NULL,1,NULL,'2026-03-19 14:37:23','2026-03-19 14:37:24',100,'courier',100,NULL,'{}');
INSERT  IGNORE INTO `server_fsm_instances` VALUES (702,'order',1363,'order_assign_courier1','COMPLETED',NULL,1,NULL,'2026-03-19 14:45:52','2026-03-19 14:45:55',100,'courier',100,NULL,'{}');
INSERT  IGNORE INTO `server_fsm_instances` VALUES (703,'order',1525,'cancel_order','FAILED',NULL,1,'CANNOT_CANCEL_FROM_order_completed','2026-03-19 14:46:18','2026-03-19 14:46:20',100,'courier',100,NULL,'{}');
INSERT  IGNORE INTO `server_fsm_instances` VALUES (708,'driver_reservations',6,'driver_reservation_cancel','COMPLETED',NULL,1,NULL,'2026-03-19 16:08:02','2026-03-19 16:11:04',200,'driver',200,'driver','{}');
INSERT  IGNORE INTO `server_fsm_instances` VALUES (714,'order',1531,'close_cell','FAILED',NULL,1,'Неизвестный статус курьера: order_in_transit_to_post2','2026-03-20 10:19:34','2026-04-04 17:14:00',100,'courier',100,NULL,'{}');
INSERT  IGNORE INTO `server_fsm_instances` VALUES (728,'order',1531,'order_assign_courier1','COMPLETED',NULL,1,NULL,'2026-03-20 12:54:58','2026-03-20 12:55:03',100,'courier',100,NULL,'{}');
INSERT  IGNORE INTO `server_fsm_instances` VALUES (729,'order',1531,'request_locker_access_code','FAILED',NULL,1,'USER_NOT_AUTHORIZED','2026-03-20 13:50:07','2026-04-04 16:27:26',100,'courier',100,NULL,'{\"leg\": \"delivery\"}');
INSERT  IGNORE INTO `server_fsm_instances` VALUES (730,'order_request',265,'order_creation','FAILED',NULL,1,'NO_FREE_CELLS','2026-03-20 14:00:40','2026-03-20 14:00:40',NULL,NULL,NULL,NULL,NULL);
INSERT  IGNORE INTO `server_fsm_instances` VALUES (731,'order_request',266,'order_creation','FAILED',NULL,1,'NO_FREE_CELLS','2026-03-20 14:19:07','2026-03-20 14:19:08',NULL,NULL,NULL,NULL,NULL);
INSERT  IGNORE INTO `server_fsm_instances` VALUES (732,'order',1531,'open_cell','FAILED',NULL,1,'MISSING_PIN_IN_METADATA','2026-03-20 14:47:25','2026-04-04 16:27:31',100,'courier',100,NULL,'{\"leg\": \"delivery\", \"pin\": \"\"}');
INSERT  IGNORE INTO `server_fsm_instances` VALUES (735,'order',1386,'open_cell','FAILED',NULL,1,'MISSING_PIN_IN_METADATA','2026-03-20 15:23:21','2026-03-20 15:23:26',2001,'recipient',2001,NULL,'{}');
INSERT  IGNORE INTO `server_fsm_instances` VALUES (736,'order',1386,'close_cell','FAILED',NULL,1,'FSM order_delivered_parcel failed: 1644 (45000): Invalid transition for order: no matching fsm_transitions','2026-03-20 15:23:34','2026-03-20 15:23:36',2001,'recipient',2001,NULL,'{}');
INSERT  IGNORE INTO `server_fsm_instances` VALUES (737,'order',1386,'request_locker_access_code','FAILED',NULL,1,'MISSING_METADATA','2026-03-20 15:23:42','2026-03-20 15:23:46',2001,'recipient',2001,NULL,'{}');
INSERT  IGNORE INTO `server_fsm_instances` VALUES (743,'order',1514,'open_cell','FAILED',NULL,1,'Неизвестный статус курьера: order_created','2026-03-21 13:49:06','2026-04-01 10:18:17',100,'courier',100,NULL,'{\"leg\": \"pickup\", \"pin\": \"611781\"}');
INSERT  IGNORE INTO `server_fsm_instances` VALUES (744,'order',1514,'close_cell','FAILED',NULL,1,'Неизвестный статус курьера: order_created','2026-03-21 13:49:10','2026-04-04 16:06:14',100,'courier',100,NULL,'{}');
INSERT  IGNORE INTO `server_fsm_instances` VALUES (758,'driver_reservations',12,'driver_reservation_cancel','FAILED',NULL,1,'CANCEL_RESERVATION_FAILED: validate_reservation_for_cancellation failed: DatabaseLayer.get_orders_by_reservation() missing 1 required positional argument: \'driver_user_id\'','2026-03-22 08:35:22','2026-03-22 14:04:37',200,'driver',200,'driver','{}');
INSERT  IGNORE INTO `server_fsm_instances` VALUES (760,'order_request',267,'order_creation','COMPLETED',NULL,1,NULL,'2026-03-22 09:43:58','2026-03-22 09:43:59',NULL,NULL,NULL,NULL,NULL);
INSERT  IGNORE INTO `server_fsm_instances` VALUES (761,'order',1534,'request_locker_access_code','COMPLETED',NULL,1,NULL,'2026-03-22 09:44:20','2026-03-25 10:13:07',200,'driver',200,'driver','{\"leg\": \"pickup\"}');
INSERT  IGNORE INTO `server_fsm_instances` VALUES (762,'order',1534,'open_cell','FAILED',NULL,1,'INVALID_LEG_IN_METADATA','2026-03-22 09:45:12','2026-03-23 17:58:01',200,'driver',200,NULL,'{\"pin\": \"763548\"}');
INSERT  IGNORE INTO `server_fsm_instances` VALUES (764,'order',1534,'close_cell','COMPLETED',NULL,1,NULL,'2026-03-22 09:50:43','2026-03-22 09:50:44',1004,'client',1004,'client','{}');
INSERT  IGNORE INTO `server_fsm_instances` VALUES (765,'order',1534,'bind_order_to_trip','COMPLETED',NULL,1,NULL,'2026-03-22 09:50:44','2026-03-22 09:50:44',999999,'system',NULL,NULL,NULL);
INSERT  IGNORE INTO `server_fsm_instances` VALUES (766,'direction',2,'direction_reserve_slot','COMPLETED',NULL,1,NULL,'2026-03-22 09:53:12','2026-03-24 16:42:29',200,'driver',200,'driver','{\"capacity\": 1}');
INSERT  IGNORE INTO `server_fsm_instances` VALUES (767,'driver_reservations',13,'driver_reservation_start_loading','FAILED',NULL,1,'NO_ACTIVE_RESERVATIONS','2026-03-22 09:54:03','2026-03-22 09:58:04',200,'driver',200,'driver','{}');
INSERT  IGNORE INTO `server_fsm_instances` VALUES (771,'driver_reservations',14,'driver_reservation_start_loading','COMPLETED',NULL,1,NULL,'2026-03-22 11:30:21','2026-03-22 11:32:31',200,'driver',200,'driver','{}');
INSERT  IGNORE INTO `server_fsm_instances` VALUES (774,'driver_reservations',14,'driver_reservation_cancel','COMPLETED',NULL,1,NULL,'2026-03-22 14:28:11','2026-03-22 15:09:24',200,'driver',200,'driver','{}');
INSERT  IGNORE INTO `server_fsm_instances` VALUES (780,'driver_reservations',15,'driver_reservation_start_loading','COMPLETED',NULL,1,NULL,'2026-03-22 15:22:43','2026-03-22 15:22:45',200,'driver',200,'driver','{}');
INSERT  IGNORE INTO `server_fsm_instances` VALUES (781,'order_request',268,'order_creation','FAILED',NULL,1,'NO_FREE_CELLS','2026-03-22 15:36:47','2026-03-23 06:23:09',NULL,NULL,NULL,NULL,NULL);
INSERT  IGNORE INTO `server_fsm_instances` VALUES (782,'order_request',269,'order_creation','FAILED',NULL,1,'NO_FREE_CELLS','2026-03-22 15:37:09','2026-03-23 06:23:09',NULL,NULL,NULL,NULL,NULL);
INSERT  IGNORE INTO `server_fsm_instances` VALUES (785,'driver_reservations',15,'driver_reservation_cancel','FAILED',NULL,1,'Нельзя начать погрузку: статус резерва \'reservation_completed\' (требуется \'reservation_active\')','2026-03-22 15:42:41','2026-03-23 06:23:09',200,'driver',200,'driver','{}');
INSERT  IGNORE INTO `server_fsm_instances` VALUES (800,'order_request',270,'order_creation','FAILED',NULL,1,'User 3 has no city','2026-03-23 08:19:20','2026-03-23 08:19:22',NULL,NULL,NULL,NULL,NULL);
INSERT  IGNORE INTO `server_fsm_instances` VALUES (802,'driver_reservations',17,'driver_reservation_start_loading','COMPLETED',NULL,1,NULL,'2026-03-23 09:13:25','2026-03-23 09:13:28',200,'driver',200,'driver','{}');
INSERT  IGNORE INTO `server_fsm_instances` VALUES (803,'driver_reservations',17,'driver_reservation_cancel','COMPLETED',NULL,1,NULL,'2026-03-23 09:22:44','2026-03-23 09:22:49',200,'driver',200,'driver','{}');
INSERT  IGNORE INTO `server_fsm_instances` VALUES (805,'driver_reservations',18,'driver_reservation_start_loading','COMPLETED',NULL,1,NULL,'2026-03-23 09:23:11','2026-03-23 09:23:14',200,'driver',200,'driver','{}');
INSERT  IGNORE INTO `server_fsm_instances` VALUES (812,'driver_reservations',18,'driver_reservation_cancel','COMPLETED',NULL,1,NULL,'2026-03-23 09:41:15','2026-03-23 09:41:20',200,'driver',200,'driver','{}');
INSERT  IGNORE INTO `server_fsm_instances` VALUES (814,'driver_reservations',19,'driver_reservation_start_loading','COMPLETED',NULL,1,NULL,'2026-03-23 09:41:47','2026-03-23 09:41:50',200,'driver',200,'driver','{}');
INSERT  IGNORE INTO `server_fsm_instances` VALUES (821,'driver_reservations',21,'driver_reservation_start_loading','COMPLETED',NULL,1,NULL,'2026-03-23 10:47:50','2026-03-23 10:47:53',200,'driver',200,'driver','{}');
INSERT  IGNORE INTO `server_fsm_instances` VALUES (830,'driver_reservations',22,'driver_reservation_start_loading','COMPLETED',NULL,1,NULL,'2026-03-23 15:45:59','2026-03-23 15:46:02',200,'driver',200,'driver','{}');
INSERT  IGNORE INTO `server_fsm_instances` VALUES (838,'locker',6,'open_cell','COMPLETED',NULL,1,NULL,'2026-03-23 15:54:41','2026-03-23 15:54:43',200,'driver',200,'driver','{\"leg\": \"pickup\", \"pin\": \"436412\"}');
INSERT  IGNORE INTO `server_fsm_instances` VALUES (839,'locker',6,'close_cell','COMPLETED',NULL,1,NULL,'2026-03-23 16:03:05','2026-03-23 16:03:09',200,'driver',200,'driver','{}');
INSERT  IGNORE INTO `server_fsm_instances` VALUES (842,'order',1528,'order_start_transit','FAILED',NULL,1,'UNKNOWN_PROCESS: order_start_transit','2026-03-23 17:19:44','2026-03-23 17:19:46',200,'driver',200,'driver','{\"trip_id\": 43}');
INSERT  IGNORE INTO `server_fsm_instances` VALUES (843,'trip',43,'start_trip','COMPLETED',NULL,1,NULL,'2026-03-23 17:19:44','2026-03-23 17:19:46',200,'driver',200,'driver','{}');
INSERT  IGNORE INTO `server_fsm_instances` VALUES (847,'driver_reservations',23,'driver_reservation_start_loading','FAILED',NULL,1,'START_LOADING_FAILED: FSM driver_reservation_start_loading failed: 1644 (45000): Invalid transition for driver_reservations: no matching fsm_transitions','2026-03-23 17:55:38','2026-03-24 16:36:14',200,'driver',200,'driver','{}');
INSERT  IGNORE INTO `server_fsm_instances` VALUES (850,'trip',43,'cancel_trip','FAILED',NULL,1,'CANNOT_CANCEL_FROM_trip_in_progress','2026-03-24 08:36:08','2026-03-24 08:36:08',200,'driver',200,'driver','{}');
INSERT  IGNORE INTO `server_fsm_instances` VALUES (854,'locker',1534,'request_locker_access_code','FAILED',NULL,1,'UNSUPPORTED_ENTITY_TYPE','2026-03-24 13:46:00','2026-03-24 13:49:40',200,'driver',200,'driver','{\"leg\": \"pickup\"}');
INSERT  IGNORE INTO `server_fsm_instances` VALUES (857,'locker',1534,'open_cell','FAILED',NULL,1,'CELL_NOT_LINKED_TO_ORDER','2026-03-24 13:49:23','2026-03-25 06:44:27',200,'driver',200,'driver','{\"leg\": \"pickup\", \"pin\": \"759692\"}');
INSERT  IGNORE INTO `server_fsm_instances` VALUES (865,'locker',1534,'close_cell','FAILED',NULL,1,'FSM locker_close_locker failed: 1644 (45000): Unknown from_state for locker in fsm_states','2026-03-24 14:33:08','2026-03-25 10:06:56',200,'driver',200,'driver','{\"leg\": \"pickup\"}');
INSERT  IGNORE INTO `server_fsm_instances` VALUES (866,'direction',2,'direction_complete_loading','COMPLETED',NULL,1,NULL,'2026-03-24 14:33:29','2026-03-25 10:13:32',200,'driver',200,'driver','{}');
INSERT  IGNORE INTO `server_fsm_instances` VALUES (872,'locker',305,'complete_trip','FAILED',NULL,1,'Рейс 305 не найден','2026-03-24 15:03:35','2026-03-24 15:03:39',200,'driver',200,'driver','{}');
INSERT  IGNORE INTO `server_fsm_instances` VALUES (909,'driver_reservations',23,'driver_reservation_cancel','COMPLETED',NULL,1,NULL,'2026-03-24 16:41:09','2026-03-24 16:41:14',200,'driver',200,'driver','{}');
INSERT  IGNORE INTO `server_fsm_instances` VALUES (915,'driver_reservations',24,'driver_reservation_start_loading','FAILED',NULL,1,'START_LOADING_FAILED: FSM driver_reservation_start_loading failed: 1644 (45000): Invalid transition for driver_reservations: no matching fsm_transitions','2026-03-24 16:42:33','2026-03-25 10:12:27',200,'driver',200,'driver','{}');
INSERT  IGNORE INTO `server_fsm_instances` VALUES (957,'locker',45,'open_cell','COMPLETED',NULL,1,NULL,'2026-03-25 10:13:15','2026-03-25 10:13:17',200,'driver',200,'driver','{\"leg\": \"pickup\", \"pin\": \"901902\"}');
INSERT  IGNORE INTO `server_fsm_instances` VALUES (958,'locker',45,'close_cell','COMPLETED',NULL,1,NULL,'2026-03-25 10:13:22','2026-03-25 10:13:22',200,'driver',200,'driver','{\"leg\": \"pickup\"}');
INSERT  IGNORE INTO `server_fsm_instances` VALUES (981,'order',1507,'request_locker_access_code','COMPLETED',NULL,1,NULL,'2026-03-25 11:38:12','2026-04-06 11:26:12',100,'courier',100,NULL,'{\"leg\": \"pickup\"}');
INSERT  IGNORE INTO `server_fsm_instances` VALUES (985,'order',1506,'request_locker_access_code','COMPLETED',NULL,1,NULL,'2026-03-25 11:44:07','2026-04-01 10:17:12',100,'courier',100,NULL,'{\"leg\": \"pickup\"}');
INSERT  IGNORE INTO `server_fsm_instances` VALUES (996,'order',1508,'open_cell','FAILED',NULL,1,'Неизвестный статус курьера: order_parcel_confirmed','2026-03-25 13:00:15','2026-04-04 15:19:30',100,'courier',100,NULL,'{\"leg\": \"pickup\", \"pin\": \"753381\"}');
INSERT  IGNORE INTO `server_fsm_instances` VALUES (997,'order',1508,'close_cell','FAILED',NULL,1,'Неизвестный статус курьера: order_parcel_confirmed','2026-03-25 13:00:19','2026-04-04 15:19:50',100,'courier',100,NULL,'{}');
INSERT  IGNORE INTO `server_fsm_instances` VALUES (1005,'trip',16,'trip_assign_driver','FAILED',NULL,1,'ASSIGNMENT_FAILED','2026-03-25 14:37:58','2026-03-25 14:38:01',777,'operator',777,'driver','{\"action\": \"remove_driver\"}');
INSERT  IGNORE INTO `server_fsm_instances` VALUES (1007,'trip',1,'trip_assign_driver','FAILED',NULL,1,'ASSIGNMENT_FAILED','2026-03-25 14:46:11','2026-03-27 12:46:25',777,'operator',200,'driver','{}');
INSERT  IGNORE INTO `server_fsm_instances` VALUES (1017,'trip',29,'trip_remove_driver','FAILED',NULL,1,'REMOVE_EXECUTOR_FAILED','2026-03-27 11:16:52','2026-03-27 11:19:14',777,'operator',200,'driver','{}');
INSERT  IGNORE INTO `server_fsm_instances` VALUES (1020,'order',5,'order_remove_courier1','COMPLETED',NULL,1,NULL,'2026-03-27 11:40:46','2026-03-27 11:40:50',777,'operator',303,'courier','{}');
INSERT  IGNORE INTO `server_fsm_instances` VALUES (1024,'order',5,'request_locker_access_code','COMPLETED',NULL,1,NULL,'2026-03-28 05:38:41','2026-03-30 06:00:43',777,'operator',303,'courier','{\"leg\": \"pickup\"}');
INSERT  IGNORE INTO `server_fsm_instances` VALUES (1026,'order',5,'close_cell','FAILED',NULL,1,'FSM locker_close_locker failed: 1644 (45000): Invalid transition for locker: no matching fsm_transitions','2026-03-28 05:39:17','2026-04-04 17:38:17',777,'operator',303,'courier','{\"leg\": \"pickup\"}');
INSERT  IGNORE INTO `server_fsm_instances` VALUES (1032,'order',30,'request_locker_access_code','FAILED',NULL,1,'ORDER_NOT_FOUND','2026-03-28 06:26:00','2026-03-28 06:35:11',777,'operator',777,'operator','{\"leg\": \"pickup\"}');
INSERT  IGNORE INTO `server_fsm_instances` VALUES (1044,'order_request',271,'order_creation','COMPLETED',NULL,1,NULL,'2026-03-28 12:07:57','2026-03-28 12:07:59',NULL,NULL,NULL,NULL,NULL);
INSERT  IGNORE INTO `server_fsm_instances` VALUES (1049,'order',5,'open_cell','COMPLETED',NULL,1,NULL,'2026-03-30 06:00:00','2026-03-30 06:00:03',777,'operator',303,'courier','{\"leg\": \"pickup\", \"pin\": \"386069\"}');
INSERT  IGNORE INTO `server_fsm_instances` VALUES (1052,'order_request',272,'order_creation','COMPLETED',NULL,1,NULL,'2026-03-30 13:40:34','2026-03-30 13:40:39',NULL,NULL,NULL,NULL,NULL);
INSERT  IGNORE INTO `server_fsm_instances` VALUES (1054,'order',1536,'order_assign_courier1','COMPLETED',NULL,1,NULL,'2026-03-30 13:41:19','2026-03-30 13:41:24',100,'courier',100,NULL,'{}');
INSERT  IGNORE INTO `server_fsm_instances` VALUES (1055,'order',1536,'request_locker_access_code','FAILED',NULL,1,'USER_NOT_AUTHORIZED','2026-03-30 13:53:57','2026-04-04 16:45:13',100,'courier',100,NULL,'{\"leg\": \"delivery\"}');
INSERT  IGNORE INTO `server_fsm_instances` VALUES (1058,'order',1536,'open_cell','FAILED',NULL,1,'MISSING_PIN_IN_METADATA','2026-03-30 14:00:10','2026-04-04 17:00:59',100,'courier',100,NULL,'{\"leg\": \"delivery\", \"pin\": \"\"}');
INSERT  IGNORE INTO `server_fsm_instances` VALUES (1061,'order',1536,'close_cell','FAILED',NULL,1,'Неизвестный статус курьера: order_courier2_parcel_delivered','2026-03-30 14:03:11','2026-04-04 17:40:23',100,'courier',100,NULL,'{}');
INSERT  IGNORE INTO `server_fsm_instances` VALUES (1062,'order',1536,'bind_order_to_trip','COMPLETED',NULL,1,NULL,'2026-03-30 14:03:15','2026-03-30 14:03:15',999999,'system',NULL,NULL,NULL);
INSERT  IGNORE INTO `server_fsm_instances` VALUES (1064,'driver_reservations',25,'driver_reservation_start_loading','COMPLETED',NULL,1,NULL,'2026-03-30 14:04:02','2026-03-30 14:04:06',200,'driver',200,'driver','{}');
INSERT  IGNORE INTO `server_fsm_instances` VALUES (1066,'locker',3,'open_cell','COMPLETED',NULL,1,NULL,'2026-03-30 14:04:25','2026-03-30 14:04:26',200,'driver',200,'driver','{\"leg\": \"pickup\", \"pin\": \"860008\"}');
INSERT  IGNORE INTO `server_fsm_instances` VALUES (1067,'locker',3,'close_cell','COMPLETED',NULL,1,NULL,'2026-03-30 14:04:30','2026-03-30 14:04:31',200,'driver',200,'driver','{\"leg\": \"pickup\"}');
INSERT  IGNORE INTO `server_fsm_instances` VALUES (1070,'order',1536,'order_start_transit','FAILED',NULL,1,'UNKNOWN_PROCESS: order_start_transit','2026-03-30 16:16:49','2026-03-30 16:16:50',200,'driver',200,'driver','{\"trip_id\": 44}');
INSERT  IGNORE INTO `server_fsm_instances` VALUES (1071,'trip',44,'start_trip','COMPLETED',NULL,1,NULL,'2026-03-30 16:16:49','2026-03-30 16:16:50',200,'driver',200,'driver','{}');
INSERT  IGNORE INTO `server_fsm_instances` VALUES (1079,'locker',13,'open_cell','COMPLETED',NULL,1,NULL,'2026-03-30 16:57:08','2026-03-30 16:57:13',200,'driver',200,'driver','{\"leg\": \"delivery\", \"pin\": \"319419\"}');
INSERT  IGNORE INTO `server_fsm_instances` VALUES (1081,'locker',13,'close_cell','COMPLETED',NULL,1,NULL,'2026-03-30 16:57:46','2026-03-30 16:57:48',200,'driver',200,'driver','{}');
INSERT  IGNORE INTO `server_fsm_instances` VALUES (1082,'order',1536,'order_assign_courier2','COMPLETED',NULL,1,NULL,'2026-03-30 17:10:06','2026-03-30 17:10:08',103,'courier',103,'courier','{}');
INSERT  IGNORE INTO `server_fsm_instances` VALUES (1090,'order_request',273,'order_creation','COMPLETED',NULL,1,NULL,'2026-03-31 08:54:21','2026-03-31 08:54:24',NULL,NULL,NULL,NULL,NULL);
INSERT  IGNORE INTO `server_fsm_instances` VALUES (1092,'order',1537,'cancel_order','COMPLETED',NULL,1,NULL,'2026-03-31 08:54:48','2026-03-31 08:54:49',1004,'client',1004,NULL,'{}');
INSERT  IGNORE INTO `server_fsm_instances` VALUES (1093,'order',1537,'request_locker_access_code','FAILED',NULL,1,'CODE_NOT_ALLOWED_IN_order_cancelled','2026-03-31 08:55:32','2026-03-31 08:55:35',1004,'client',1004,NULL,'{\"leg\": \"pickup\"}');
INSERT  IGNORE INTO `server_fsm_instances` VALUES (1094,'order_request',274,'order_creation','COMPLETED',NULL,1,NULL,'2026-03-31 08:58:04','2026-03-31 08:58:05',NULL,NULL,NULL,NULL,NULL);
INSERT  IGNORE INTO `server_fsm_instances` VALUES (1095,'order',1538,'order_assign_courier1','COMPLETED',NULL,1,NULL,'2026-03-31 08:59:08','2026-03-31 08:59:10',103,'courier',103,NULL,'{}');
INSERT  IGNORE INTO `server_fsm_instances` VALUES (1096,'order',1538,'cancel_order','COMPLETED',NULL,1,NULL,'2026-03-31 09:00:09','2026-03-31 09:00:10',103,'courier',103,NULL,'{}');
INSERT  IGNORE INTO `server_fsm_instances` VALUES (1110,'order',1363,'request_locker_access_code','COMPLETED',NULL,1,NULL,'2026-04-01 03:10:47','2026-04-01 10:17:06',100,'courier',100,NULL,'{\"leg\": \"pickup\"}');
INSERT  IGNORE INTO `server_fsm_instances` VALUES (1115,'order',1363,'open_cell','FAILED',NULL,1,'Неизвестный статус курьера: order_parcel_confirmed','2026-04-01 03:26:28','2026-04-01 10:18:07',100,'courier',100,NULL,'{\"leg\": \"pickup\", \"pin\": \"162520\"}');
INSERT  IGNORE INTO `server_fsm_instances` VALUES (1116,'order',1363,'close_cell','FAILED',NULL,1,'Неизвестный статус курьера: order_parcel_confirmed','2026-04-01 03:26:32','2026-04-01 10:18:27',100,'courier',100,NULL,'{}');
INSERT  IGNORE INTO `server_fsm_instances` VALUES (1121,'order',1502,'request_locker_access_code','COMPLETED',NULL,1,NULL,'2026-04-01 08:51:13','2026-04-06 11:25:02',100,'courier',100,NULL,'{\"leg\": \"pickup\"}');
INSERT  IGNORE INTO `server_fsm_instances` VALUES (1123,'order',1502,'open_cell','FAILED',NULL,1,'Неизвестный статус курьера: order_parcel_confirmed','2026-04-01 08:51:31','2026-04-06 11:25:12',100,'courier',100,NULL,'{\"leg\": \"pickup\", \"pin\": \"177464\"}');
INSERT  IGNORE INTO `server_fsm_instances` VALUES (1124,'order',1502,'close_cell','FAILED',NULL,1,'Неизвестный статус курьера: order_parcel_confirmed','2026-04-01 08:52:20','2026-04-06 11:32:43',100,'courier',100,NULL,'{}');
INSERT  IGNORE INTO `server_fsm_instances` VALUES (1134,'order',1502,'bind_order_to_trip','COMPLETED',NULL,1,NULL,'2026-04-01 09:33:15','2026-04-01 09:33:15',999999,'system',NULL,NULL,NULL);
INSERT  IGNORE INTO `server_fsm_instances` VALUES (1138,'order',1363,'bind_order_to_trip','COMPLETED',NULL,1,NULL,'2026-04-01 09:35:00','2026-04-01 09:35:00',999999,'system',NULL,NULL,NULL);
INSERT  IGNORE INTO `server_fsm_instances` VALUES (1139,'order_request',275,'order_creation','FAILED',NULL,1,'NO_FREE_CELLS','2026-04-01 09:39:01','2026-04-01 09:39:05',NULL,NULL,NULL,NULL,NULL);
INSERT  IGNORE INTO `server_fsm_instances` VALUES (1146,'order',1531,'bind_order_to_trip','COMPLETED',NULL,1,NULL,'2026-04-01 09:46:42','2026-04-01 09:46:42',999999,'system',NULL,NULL,NULL);
INSERT  IGNORE INTO `server_fsm_instances` VALUES (1150,'driver_reservations',26,'driver_reservation_start_loading','COMPLETED',NULL,1,NULL,'2026-04-01 09:55:42','2026-04-01 09:55:43',200,'driver',200,'driver','{}');
INSERT  IGNORE INTO `server_fsm_instances` VALUES (1152,'locker',10,'open_cell','COMPLETED',NULL,1,NULL,'2026-04-01 09:56:03','2026-04-01 09:56:03',200,'driver',200,'driver','{\"leg\": \"pickup\", \"pin\": \"687901\"}');
INSERT  IGNORE INTO `server_fsm_instances` VALUES (1153,'locker',10,'close_cell','COMPLETED',NULL,1,NULL,'2026-04-01 09:56:14','2026-04-01 09:56:19',200,'driver',200,'driver','{\"leg\": \"pickup\"}');
INSERT  IGNORE INTO `server_fsm_instances` VALUES (1155,'order',1531,'order_start_transit','FAILED',NULL,1,'UNKNOWN_PROCESS: order_start_transit','2026-04-01 09:59:12','2026-04-01 09:59:14',200,'driver',200,'driver','{\"trip_id\": 45}');
INSERT  IGNORE INTO `server_fsm_instances` VALUES (1156,'trip',45,'start_trip','COMPLETED',NULL,1,NULL,'2026-04-01 09:59:12','2026-04-01 09:59:14',200,'driver',200,'driver','{}');
INSERT  IGNORE INTO `server_fsm_instances` VALUES (1157,'order',10,'request_locker_access_code','FAILED',NULL,1,'USER_NOT_AUTHORIZED','2026-04-01 10:02:39','2026-04-01 10:02:44',200,'driver',200,'driver','{\"leg\": \"pickup\"}');
INSERT  IGNORE INTO `server_fsm_instances` VALUES (1159,'order',1506,'close_cell','FAILED',NULL,1,'Неизвестный статус курьера: order_parcel_confirmed','2026-04-01 10:03:12','2026-04-03 08:22:54',100,'courier',100,NULL,'{}');
INSERT  IGNORE INTO `server_fsm_instances` VALUES (1167,'order',1507,'open_cell','FAILED',NULL,1,'FSM locker_open_locker failed: 1644 (45000): Invalid transition for locker: no matching fsm_transitions','2026-04-01 10:13:51','2026-04-06 11:26:22',100,'courier',100,NULL,'{\"leg\": \"pickup\", \"pin\": \"286055\"}');
INSERT  IGNORE INTO `server_fsm_instances` VALUES (1169,'order',1508,'bind_order_to_trip','COMPLETED',NULL,1,NULL,'2026-04-01 10:13:56','2026-04-01 10:13:56',999999,'system',NULL,NULL,NULL);
INSERT  IGNORE INTO `server_fsm_instances` VALUES (1170,'order',1506,'open_cell','FAILED',NULL,1,'Неизвестный статус курьера: order_parcel_confirmed','2026-04-01 10:14:03','2026-04-01 10:18:12',100,'courier',100,NULL,'{\"leg\": \"pickup\", \"pin\": \"576781\"}');
INSERT  IGNORE INTO `server_fsm_instances` VALUES (1171,'order',1507,'close_cell','FAILED',NULL,1,'FSM order_confirm_parcel_in failed: 1644 (45000): Invalid transition for order: no matching fsm_transitions','2026-04-01 10:14:05','2026-04-06 11:26:27',100,'courier',100,NULL,'{}');
INSERT  IGNORE INTO `server_fsm_instances` VALUES (1173,'order',1506,'bind_order_to_trip','COMPLETED',NULL,1,NULL,'2026-04-01 10:14:11','2026-04-01 10:14:11',999999,'system',NULL,NULL,NULL);
INSERT  IGNORE INTO `server_fsm_instances` VALUES (1214,'order',1536,'report_error','FAILED',NULL,1,'MISSING_ORDER_ID_IN_METADATA','2026-04-02 14:54:47','2026-04-02 14:54:50',100,'courier',100,NULL,'{\"error_type\": \"wrong_parcel\"}');
INSERT  IGNORE INTO `server_fsm_instances` VALUES (1215,'order',1528,'report_error','FAILED',NULL,1,'MISSING_ORDER_ID_IN_METADATA','2026-04-02 15:17:22','2026-04-02 15:17:26',1001,'client',1001,NULL,'{\"error_type\": \"wrong_parcel\"}');
INSERT  IGNORE INTO `server_fsm_instances` VALUES (1226,'order',1536,'confirm_courier2_delivery','FAILED',NULL,1,'INVALID_CODE: Код подтверждения не найден для этого заказа','2026-04-02 17:37:20','2026-04-02 17:40:26',103,'courier',103,'courier','{\"pin\": \"784943\"}');
INSERT  IGNORE INTO `server_fsm_instances` VALUES (1231,'order',1524,'request_locker_access_code','FAILED',NULL,1,'USER_NOT_AUTHORIZED','2026-04-02 18:06:49','2026-04-02 18:06:53',2002,'recipient',2002,NULL,'{\"leg\": \"pickup\"}');
INSERT  IGNORE INTO `server_fsm_instances` VALUES (1258,'order',13,'close_cell','FAILED',NULL,1,'Нет source_cell_id для заказа 13','2026-04-04 14:49:58','2026-04-04 14:55:38',777,'operator',103,'courier','{\"leg\": \"delivery\"}');
INSERT  IGNORE INTO `server_fsm_instances` VALUES (1264,'trip',30,'trip_remove_driver','COMPLETED',NULL,1,NULL,'2026-04-04 14:57:48','2026-04-04 14:57:53',777,'operator',200,'driver','{}');
INSERT  IGNORE INTO `server_fsm_instances` VALUES (1312,'order',1364,'order_assign_courier1','COMPLETED',NULL,1,NULL,'2026-04-04 16:38:26','2026-04-04 16:38:27',100,'courier',100,NULL,'{}');
INSERT  IGNORE INTO `server_fsm_instances` VALUES (1318,'order',1365,'order_assign_courier1','COMPLETED',NULL,1,NULL,'2026-04-04 16:45:28','2026-04-04 16:45:28',100,'courier',100,NULL,'{}');
INSERT  IGNORE INTO `server_fsm_instances` VALUES (1332,'order',1535,'order_assign_courier1','COMPLETED',NULL,1,NULL,'2026-04-04 17:26:32','2026-04-04 17:26:36',100,'courier',100,NULL,'{}');
INSERT  IGNORE INTO `server_fsm_instances` VALUES (1340,'order',1535,'close_cell','FAILED',NULL,1,'FSM order_confirm_parcel_in failed: 1644 (45000): Invalid transition for order: no matching fsm_transitions','2026-04-04 17:35:09','2026-04-06 11:24:42',100,'courier',100,NULL,'{}');
INSERT  IGNORE INTO `server_fsm_instances` VALUES (1342,'order',1367,'order_assign_courier1','COMPLETED',NULL,1,NULL,'2026-04-04 17:36:08','2026-04-04 17:36:12',100,'courier',100,NULL,'{}');
INSERT  IGNORE INTO `server_fsm_instances` VALUES (1355,'order',1367,'request_locker_access_code','COMPLETED',NULL,1,NULL,'2026-04-06 11:27:13','2026-04-06 11:27:17',100,'courier',100,NULL,'{\"leg\": \"pickup\"}');
INSERT  IGNORE INTO `server_fsm_instances` VALUES (1356,'order',1367,'open_cell','FAILED',NULL,1,'FSM locker_open_locker failed: 1644 (45000): Invalid transition for locker: no matching fsm_transitions','2026-04-06 11:27:25','2026-04-06 11:35:38',100,'courier',100,NULL,'{\"leg\": \"pickup\", \"pin\": \"488387\"}');
INSERT  IGNORE INTO `server_fsm_instances` VALUES (1361,'order',1364,'request_locker_access_code','COMPLETED',NULL,1,NULL,'2026-04-06 11:35:56','2026-04-06 11:35:58',100,'courier',100,NULL,'{\"leg\": \"pickup\"}');
INSERT  IGNORE INTO `server_fsm_instances` VALUES (1362,'order',1364,'open_cell','FAILED',NULL,1,'FSM locker_open_locker failed: 1644 (45000): Invalid transition for locker: no matching fsm_transitions','2026-04-06 11:36:05','2026-04-06 11:36:08',100,'courier',100,NULL,'{\"leg\": \"pickup\", \"pin\": \"706649\"}');
INSERT  IGNORE INTO `server_fsm_instances` VALUES (1363,'order',1365,'request_locker_access_code','COMPLETED',NULL,1,NULL,'2026-04-06 11:36:34','2026-04-06 14:22:29',100,'courier',100,NULL,'{\"leg\": \"pickup\"}');
INSERT  IGNORE INTO `server_fsm_instances` VALUES (1365,'order',1365,'open_cell','FAILED',NULL,1,'FSM locker_open_locker failed: 1644 (45000): Invalid transition for locker: no matching fsm_transitions','2026-04-06 11:36:46','2026-04-06 14:22:39',100,'courier',100,NULL,'{\"leg\": \"pickup\", \"pin\": \"340951\"}');
INSERT  IGNORE INTO `server_fsm_instances` VALUES (1367,'order',1365,'close_cell','FAILED',NULL,1,'FSM order_confirm_parcel_in failed: 1644 (45000): Invalid transition for order: no matching fsm_transitions','2026-04-06 11:37:26','2026-04-06 14:41:35',100,'courier',100,NULL,'{}');
INSERT  IGNORE INTO `server_fsm_instances` VALUES (1375,'order_request',276,'order_creation','FAILED',NULL,1,'MISSING_TEST_AUTH_HASH','2026-04-07 19:57:59','2026-04-07 20:28:08',NULL,NULL,NULL,NULL,NULL);
INSERT  IGNORE INTO `server_fsm_instances` VALUES (1377,'order_request',277,'order_creation','FAILED',NULL,1,'EXCEPTION: name \'CoreAuthError\' is not defined','2026-04-07 20:54:17','2026-04-07 20:54:18',NULL,NULL,NULL,NULL,NULL);
INSERT  IGNORE INTO `server_fsm_instances` VALUES (1379,'order_request',278,'order_creation','FAILED',NULL,1,'CORE_ERROR: Core returned error: {\'code\': \'404\', \'status\': \'error\', \'message\': \'unauthorized access\', \'data\': []}','2026-04-07 21:08:14','2026-04-07 21:08:16',NULL,NULL,NULL,NULL,NULL);
INSERT  IGNORE INTO `server_fsm_instances` VALUES (1381,'order_request',279,'order_creation','FAILED',NULL,1,'CLIENT_NOT_MAPPED_TO_CORE','2026-04-08 07:48:10','2026-04-08 07:48:14',NULL,NULL,NULL,NULL,NULL);
INSERT  IGNORE INTO `server_fsm_instances` VALUES (1383,'order_request',280,'order_creation','FAILED',NULL,1,'MISSING_CORE_TOKENS','2026-04-08 07:49:02','2026-04-08 07:49:04',NULL,NULL,NULL,NULL,NULL);
INSERT  IGNORE INTO `server_fsm_instances` VALUES (1384,'order_request',281,'order_creation','FAILED',NULL,1,'CORE_ERROR: Create drive order failed: name \'json\' is not defined','2026-04-08 07:54:05','2026-04-08 07:54:10',NULL,NULL,NULL,NULL,NULL);
INSERT  IGNORE INTO `server_fsm_instances` VALUES (1386,'order_request',282,'order_creation','FAILED',NULL,1,'CORE_ERROR: Create drive order failed: RetryError[<Future at 0x7255c8f1fe50 state=finished raised CoreUnavailableError>]','2026-04-08 08:07:09','2026-04-08 08:07:14',NULL,NULL,NULL,NULL,NULL);
INSERT  IGNORE INTO `server_fsm_instances` VALUES (1388,'order_request',283,'order_creation','FAILED',NULL,1,'CORE_ERROR: Create drive order failed: RetryError[<Future at 0x70b3429b4c10 state=finished raised CoreUnavailableError>]','2026-04-08 08:35:05','2026-04-08 08:35:11',NULL,NULL,NULL,NULL,NULL);
INSERT  IGNORE INTO `server_fsm_instances` VALUES (1390,'order_request',284,'order_creation','FAILED',NULL,1,'CORE_ERROR: Core returned error: wrong b_options keys: parcel_type,cell_size,sender_delivery,recipient_delivery,client_user_id,recipient_user_id,description,pickup_type,delivery_type','2026-04-08 08:38:39','2026-04-08 08:38:40',NULL,NULL,NULL,NULL,NULL);
INSERT  IGNORE INTO `server_fsm_instances` VALUES (1392,'order_request',285,'order_creation','FAILED',NULL,1,'CORE_ERROR: Core returned error: database insert failed','2026-04-08 08:53:01','2026-04-08 08:53:02',NULL,NULL,NULL,NULL,NULL);
INSERT  IGNORE INTO `server_fsm_instances` VALUES (1394,'order_request',286,'order_creation','FAILED',NULL,1,'NO_FREE_CELLS','2026-04-08 09:00:33','2026-04-08 09:00:37',NULL,NULL,NULL,NULL,NULL);
INSERT  IGNORE INTO `server_fsm_instances` VALUES (1396,'order_request',287,'order_creation','FAILED',NULL,1,'NO_FREE_CELLS','2026-04-08 09:00:56','2026-04-08 09:00:57',NULL,NULL,NULL,NULL,NULL);
INSERT  IGNORE INTO `server_fsm_instances` VALUES (1397,'order_request',288,'order_creation','FAILED',NULL,1,'CORE_ERROR: Core returned error: database insert failed','2026-04-08 09:07:04','2026-04-08 09:07:09',NULL,NULL,NULL,NULL,NULL);
INSERT  IGNORE INTO `server_fsm_instances` VALUES (1399,'order_request',289,'order_creation','FAILED',NULL,1,'CORE_ERROR: Core returned error: database insert failed','2026-04-08 09:09:29','2026-04-08 09:09:33',NULL,NULL,NULL,NULL,NULL);
INSERT  IGNORE INTO `server_fsm_instances` VALUES (1401,'order_request',290,'order_creation','COMPLETED',NULL,1,NULL,'2026-04-08 09:26:08','2026-04-08 09:26:10',NULL,NULL,NULL,NULL,NULL);
INSERT  IGNORE INTO `server_fsm_instances` VALUES (1403,'order',1539,'cancel_order','FAILED',NULL,1,'CORE_CANCEL_FAILED: CORE_ERROR: Core returned error: wrong booking state','2026-04-08 11:47:20','2026-04-08 12:17:32',1000013,'client',1000013,NULL,'{}');
INSERT  IGNORE INTO `server_fsm_instances` VALUES (1411,'locker',0,'locker_cleanup','COMPLETED',NULL,1,NULL,'2026-04-08 12:13:47','2026-04-08 14:47:52',999999,'system',NULL,NULL,'{\"threshold_minutes\": 30}');
INSERT  IGNORE INTO `server_fsm_instances` VALUES (1413,'order_request',291,'order_creation','COMPLETED',NULL,1,NULL,'2026-04-08 12:57:54','2026-04-08 12:57:55',NULL,NULL,NULL,NULL,NULL);
INSERT  IGNORE INTO `server_fsm_instances` VALUES (1415,'order',1540,'cancel_order','COMPLETED',NULL,1,NULL,'2026-04-08 13:01:35','2026-04-08 13:01:40',1000013,'client',1000013,NULL,'{}');
INSERT  IGNORE INTO `server_fsm_instances` VALUES (1416,'order_request',292,'order_creation','COMPLETED',NULL,1,NULL,'2026-04-08 13:05:03','2026-04-08 13:05:06',NULL,NULL,NULL,NULL,NULL);
INSERT  IGNORE INTO `server_fsm_instances` VALUES (1418,'order',1540,'request_locker_access_code','FAILED',NULL,1,'CODE_NOT_ALLOWED_IN_order_cancelled','2026-04-08 14:47:50','2026-04-08 14:47:52',1000013,'client',1000013,NULL,'{\"leg\": \"pickup\"}');

--
-- Table structure for table `stage_orders`
--

DROP TABLE IF EXISTS `stage_orders`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `stage_orders` (
  `trip_id` int DEFAULT NULL,
  `direction_id` int DEFAULT NULL,
  `order_id` int NOT NULL,
  `leg` enum('pickup','delivery') NOT NULL DEFAULT 'pickup',
  `courier_user_id` int DEFAULT NULL,
  `reservation_id` int DEFAULT NULL,
  `reserved_by_driver_id` int DEFAULT NULL,
  PRIMARY KEY (`order_id`,`leg`),
  KEY `order_id` (`order_id`),
  KEY `stage_orders_ibfk_courier` (`courier_user_id`),
  KEY `direction_id` (`direction_id`),
  CONSTRAINT `stage_orders_ibfk_2` FOREIGN KEY (`order_id`) REFERENCES `orders` (`id`) ON DELETE CASCADE,
  CONSTRAINT `stage_orders_ibfk_3` FOREIGN KEY (`direction_id`) REFERENCES `directions` (`id`),
  CONSTRAINT `stage_orders_ibfk_courier` FOREIGN KEY (`courier_user_id`) REFERENCES `users` (`id`) ON DELETE SET NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `stage_orders`
--

INSERT  IGNORE INTO `stage_orders` VALUES (1,NULL,1,'pickup',2,NULL,NULL);
INSERT  IGNORE INTO `stage_orders` VALUES (1,NULL,2,'pickup',NULL,NULL,NULL);
INSERT  IGNORE INTO `stage_orders` VALUES (1,NULL,3,'pickup',NULL,NULL,NULL);
INSERT  IGNORE INTO `stage_orders` VALUES (1,NULL,4,'pickup',NULL,NULL,NULL);
INSERT  IGNORE INTO `stage_orders` VALUES (1,NULL,5,'pickup',NULL,NULL,NULL);
INSERT  IGNORE INTO `stage_orders` VALUES (1,NULL,5,'delivery',303,NULL,NULL);
INSERT  IGNORE INTO `stage_orders` VALUES (2,NULL,1361,'pickup',2,NULL,NULL);
INSERT  IGNORE INTO `stage_orders` VALUES (2,NULL,1361,'delivery',NULL,NULL,NULL);
INSERT  IGNORE INTO `stage_orders` VALUES (3,NULL,1362,'pickup',2,NULL,NULL);
INSERT  IGNORE INTO `stage_orders` VALUES (3,NULL,1362,'delivery',NULL,NULL,NULL);
INSERT  IGNORE INTO `stage_orders` VALUES (2,1,1363,'pickup',100,NULL,NULL);
INSERT  IGNORE INTO `stage_orders` VALUES (2,NULL,1364,'pickup',100,NULL,NULL);
INSERT  IGNORE INTO `stage_orders` VALUES (2,NULL,1364,'delivery',NULL,NULL,NULL);
INSERT  IGNORE INTO `stage_orders` VALUES (2,NULL,1365,'pickup',100,NULL,NULL);
INSERT  IGNORE INTO `stage_orders` VALUES (2,NULL,1365,'delivery',NULL,NULL,NULL);
INSERT  IGNORE INTO `stage_orders` VALUES (3,NULL,1366,'pickup',NULL,NULL,NULL);
INSERT  IGNORE INTO `stage_orders` VALUES (3,NULL,1366,'delivery',NULL,NULL,NULL);
INSERT  IGNORE INTO `stage_orders` VALUES (3,NULL,1367,'pickup',100,NULL,NULL);
INSERT  IGNORE INTO `stage_orders` VALUES (3,NULL,1367,'delivery',NULL,NULL,NULL);
INSERT  IGNORE INTO `stage_orders` VALUES (4,NULL,1368,'pickup',NULL,NULL,NULL);
INSERT  IGNORE INTO `stage_orders` VALUES (4,NULL,1368,'delivery',NULL,NULL,NULL);
INSERT  IGNORE INTO `stage_orders` VALUES (2,NULL,1369,'pickup',NULL,NULL,NULL);
INSERT  IGNORE INTO `stage_orders` VALUES (2,NULL,1369,'delivery',NULL,NULL,NULL);
INSERT  IGNORE INTO `stage_orders` VALUES (3,NULL,1370,'pickup',NULL,NULL,NULL);
INSERT  IGNORE INTO `stage_orders` VALUES (3,NULL,1370,'delivery',NULL,NULL,NULL);
INSERT  IGNORE INTO `stage_orders` VALUES (3,NULL,1371,'pickup',NULL,NULL,NULL);
INSERT  IGNORE INTO `stage_orders` VALUES (3,NULL,1371,'delivery',NULL,NULL,NULL);
INSERT  IGNORE INTO `stage_orders` VALUES (4,NULL,1372,'pickup',NULL,NULL,NULL);
INSERT  IGNORE INTO `stage_orders` VALUES (4,NULL,1372,'delivery',NULL,NULL,NULL);
INSERT  IGNORE INTO `stage_orders` VALUES (4,NULL,1373,'pickup',2,NULL,NULL);
INSERT  IGNORE INTO `stage_orders` VALUES (4,NULL,1373,'delivery',NULL,NULL,NULL);
INSERT  IGNORE INTO `stage_orders` VALUES (4,NULL,1374,'pickup',NULL,NULL,NULL);
INSERT  IGNORE INTO `stage_orders` VALUES (4,NULL,1374,'delivery',NULL,NULL,NULL);
INSERT  IGNORE INTO `stage_orders` VALUES (4,NULL,1375,'pickup',NULL,NULL,NULL);
INSERT  IGNORE INTO `stage_orders` VALUES (4,NULL,1375,'delivery',NULL,NULL,NULL);
INSERT  IGNORE INTO `stage_orders` VALUES (5,NULL,1376,'pickup',NULL,NULL,NULL);
INSERT  IGNORE INTO `stage_orders` VALUES (5,NULL,1376,'delivery',NULL,NULL,NULL);
INSERT  IGNORE INTO `stage_orders` VALUES (6,NULL,1377,'pickup',NULL,NULL,NULL);
INSERT  IGNORE INTO `stage_orders` VALUES (6,NULL,1377,'delivery',NULL,NULL,NULL);
INSERT  IGNORE INTO `stage_orders` VALUES (6,NULL,1378,'pickup',2,NULL,NULL);
INSERT  IGNORE INTO `stage_orders` VALUES (6,NULL,1378,'delivery',NULL,NULL,NULL);
INSERT  IGNORE INTO `stage_orders` VALUES (6,NULL,1379,'pickup',2,NULL,NULL);
INSERT  IGNORE INTO `stage_orders` VALUES (6,NULL,1379,'delivery',NULL,NULL,NULL);
INSERT  IGNORE INTO `stage_orders` VALUES (7,NULL,1380,'pickup',NULL,NULL,NULL);
INSERT  IGNORE INTO `stage_orders` VALUES (7,NULL,1380,'delivery',NULL,NULL,NULL);
INSERT  IGNORE INTO `stage_orders` VALUES (7,NULL,1381,'pickup',NULL,NULL,NULL);
INSERT  IGNORE INTO `stage_orders` VALUES (7,NULL,1381,'delivery',NULL,NULL,NULL);
INSERT  IGNORE INTO `stage_orders` VALUES (7,NULL,1382,'pickup',NULL,NULL,NULL);
INSERT  IGNORE INTO `stage_orders` VALUES (7,NULL,1382,'delivery',NULL,NULL,NULL);
INSERT  IGNORE INTO `stage_orders` VALUES (7,NULL,1383,'pickup',NULL,NULL,NULL);
INSERT  IGNORE INTO `stage_orders` VALUES (7,NULL,1383,'delivery',NULL,NULL,NULL);
INSERT  IGNORE INTO `stage_orders` VALUES (7,NULL,1384,'pickup',NULL,NULL,NULL);
INSERT  IGNORE INTO `stage_orders` VALUES (7,NULL,1384,'delivery',NULL,NULL,NULL);
INSERT  IGNORE INTO `stage_orders` VALUES (8,NULL,1385,'pickup',NULL,NULL,NULL);
INSERT  IGNORE INTO `stage_orders` VALUES (8,NULL,1385,'delivery',NULL,NULL,NULL);
INSERT  IGNORE INTO `stage_orders` VALUES (8,NULL,1386,'pickup',NULL,NULL,NULL);
INSERT  IGNORE INTO `stage_orders` VALUES (8,NULL,1386,'delivery',NULL,NULL,NULL);
INSERT  IGNORE INTO `stage_orders` VALUES (8,NULL,1387,'pickup',NULL,NULL,NULL);
INSERT  IGNORE INTO `stage_orders` VALUES (8,NULL,1387,'delivery',NULL,NULL,NULL);
INSERT  IGNORE INTO `stage_orders` VALUES (8,NULL,1388,'pickup',NULL,NULL,NULL);
INSERT  IGNORE INTO `stage_orders` VALUES (8,NULL,1388,'delivery',NULL,NULL,NULL);
INSERT  IGNORE INTO `stage_orders` VALUES (8,NULL,1389,'pickup',NULL,NULL,NULL);
INSERT  IGNORE INTO `stage_orders` VALUES (8,NULL,1389,'delivery',NULL,NULL,NULL);
INSERT  IGNORE INTO `stage_orders` VALUES (9,NULL,1390,'pickup',NULL,NULL,NULL);
INSERT  IGNORE INTO `stage_orders` VALUES (9,NULL,1390,'delivery',NULL,NULL,NULL);
INSERT  IGNORE INTO `stage_orders` VALUES (9,NULL,1391,'pickup',NULL,NULL,NULL);
INSERT  IGNORE INTO `stage_orders` VALUES (9,NULL,1391,'delivery',NULL,NULL,NULL);
INSERT  IGNORE INTO `stage_orders` VALUES (9,NULL,1392,'pickup',NULL,NULL,NULL);
INSERT  IGNORE INTO `stage_orders` VALUES (9,NULL,1392,'delivery',NULL,NULL,NULL);
INSERT  IGNORE INTO `stage_orders` VALUES (9,NULL,1393,'pickup',NULL,NULL,NULL);
INSERT  IGNORE INTO `stage_orders` VALUES (9,NULL,1393,'delivery',NULL,NULL,NULL);
INSERT  IGNORE INTO `stage_orders` VALUES (9,NULL,1394,'pickup',NULL,NULL,NULL);
INSERT  IGNORE INTO `stage_orders` VALUES (9,NULL,1394,'delivery',NULL,NULL,NULL);
INSERT  IGNORE INTO `stage_orders` VALUES (10,NULL,1395,'pickup',NULL,NULL,NULL);
INSERT  IGNORE INTO `stage_orders` VALUES (10,NULL,1395,'delivery',NULL,NULL,NULL);
INSERT  IGNORE INTO `stage_orders` VALUES (10,NULL,1396,'pickup',NULL,NULL,NULL);
INSERT  IGNORE INTO `stage_orders` VALUES (10,NULL,1396,'delivery',NULL,NULL,NULL);
INSERT  IGNORE INTO `stage_orders` VALUES (10,NULL,1397,'pickup',NULL,NULL,NULL);
INSERT  IGNORE INTO `stage_orders` VALUES (10,NULL,1397,'delivery',NULL,NULL,NULL);
INSERT  IGNORE INTO `stage_orders` VALUES (10,NULL,1398,'pickup',2,NULL,NULL);
INSERT  IGNORE INTO `stage_orders` VALUES (10,NULL,1398,'delivery',NULL,NULL,NULL);
INSERT  IGNORE INTO `stage_orders` VALUES (10,NULL,1399,'pickup',2,NULL,NULL);
INSERT  IGNORE INTO `stage_orders` VALUES (10,NULL,1399,'delivery',NULL,NULL,NULL);
INSERT  IGNORE INTO `stage_orders` VALUES (11,NULL,1400,'pickup',NULL,NULL,NULL);
INSERT  IGNORE INTO `stage_orders` VALUES (11,NULL,1400,'delivery',NULL,NULL,NULL);
INSERT  IGNORE INTO `stage_orders` VALUES (11,NULL,1401,'pickup',NULL,NULL,NULL);
INSERT  IGNORE INTO `stage_orders` VALUES (11,NULL,1401,'delivery',NULL,NULL,NULL);
INSERT  IGNORE INTO `stage_orders` VALUES (11,NULL,1402,'pickup',NULL,NULL,NULL);
INSERT  IGNORE INTO `stage_orders` VALUES (11,NULL,1402,'delivery',NULL,NULL,NULL);
INSERT  IGNORE INTO `stage_orders` VALUES (11,NULL,1403,'pickup',NULL,NULL,NULL);
INSERT  IGNORE INTO `stage_orders` VALUES (11,NULL,1403,'delivery',NULL,NULL,NULL);
INSERT  IGNORE INTO `stage_orders` VALUES (12,NULL,1404,'pickup',NULL,NULL,NULL);
INSERT  IGNORE INTO `stage_orders` VALUES (12,NULL,1404,'delivery',NULL,NULL,NULL);
INSERT  IGNORE INTO `stage_orders` VALUES (12,NULL,1405,'pickup',NULL,NULL,NULL);
INSERT  IGNORE INTO `stage_orders` VALUES (12,NULL,1405,'delivery',NULL,NULL,NULL);
INSERT  IGNORE INTO `stage_orders` VALUES (13,NULL,1406,'pickup',NULL,NULL,NULL);
INSERT  IGNORE INTO `stage_orders` VALUES (13,NULL,1406,'delivery',NULL,NULL,NULL);
INSERT  IGNORE INTO `stage_orders` VALUES (13,NULL,1407,'pickup',NULL,NULL,NULL);
INSERT  IGNORE INTO `stage_orders` VALUES (13,NULL,1407,'delivery',NULL,NULL,NULL);
INSERT  IGNORE INTO `stage_orders` VALUES (14,NULL,1408,'pickup',NULL,NULL,NULL);
INSERT  IGNORE INTO `stage_orders` VALUES (14,NULL,1408,'delivery',NULL,NULL,NULL);
INSERT  IGNORE INTO `stage_orders` VALUES (15,NULL,1409,'pickup',NULL,NULL,NULL);
INSERT  IGNORE INTO `stage_orders` VALUES (15,NULL,1409,'delivery',NULL,NULL,NULL);
INSERT  IGNORE INTO `stage_orders` VALUES (15,NULL,1410,'pickup',NULL,NULL,NULL);
INSERT  IGNORE INTO `stage_orders` VALUES (15,NULL,1410,'delivery',NULL,NULL,NULL);
INSERT  IGNORE INTO `stage_orders` VALUES (15,NULL,1411,'pickup',NULL,NULL,NULL);
INSERT  IGNORE INTO `stage_orders` VALUES (15,NULL,1411,'delivery',NULL,NULL,NULL);
INSERT  IGNORE INTO `stage_orders` VALUES (16,NULL,1412,'pickup',NULL,NULL,NULL);
INSERT  IGNORE INTO `stage_orders` VALUES (16,NULL,1412,'delivery',NULL,NULL,NULL);
INSERT  IGNORE INTO `stage_orders` VALUES (17,NULL,1413,'pickup',1003,NULL,NULL);
INSERT  IGNORE INTO `stage_orders` VALUES (17,NULL,1413,'delivery',NULL,NULL,NULL);
INSERT  IGNORE INTO `stage_orders` VALUES (18,NULL,1414,'pickup',NULL,NULL,NULL);
INSERT  IGNORE INTO `stage_orders` VALUES (18,NULL,1414,'delivery',NULL,NULL,NULL);
INSERT  IGNORE INTO `stage_orders` VALUES (18,NULL,1415,'pickup',NULL,NULL,NULL);
INSERT  IGNORE INTO `stage_orders` VALUES (18,NULL,1415,'delivery',NULL,NULL,NULL);
INSERT  IGNORE INTO `stage_orders` VALUES (18,NULL,1416,'pickup',NULL,NULL,NULL);
INSERT  IGNORE INTO `stage_orders` VALUES (18,NULL,1416,'delivery',NULL,NULL,NULL);
INSERT  IGNORE INTO `stage_orders` VALUES (18,NULL,1417,'pickup',NULL,NULL,NULL);
INSERT  IGNORE INTO `stage_orders` VALUES (18,NULL,1417,'delivery',NULL,NULL,NULL);
INSERT  IGNORE INTO `stage_orders` VALUES (18,NULL,1418,'pickup',NULL,NULL,NULL);
INSERT  IGNORE INTO `stage_orders` VALUES (18,NULL,1418,'delivery',NULL,NULL,NULL);
INSERT  IGNORE INTO `stage_orders` VALUES (19,NULL,1419,'pickup',NULL,NULL,NULL);
INSERT  IGNORE INTO `stage_orders` VALUES (19,NULL,1419,'delivery',NULL,NULL,NULL);
INSERT  IGNORE INTO `stage_orders` VALUES (19,NULL,1420,'pickup',NULL,NULL,NULL);
INSERT  IGNORE INTO `stage_orders` VALUES (19,NULL,1420,'delivery',NULL,NULL,NULL);
INSERT  IGNORE INTO `stage_orders` VALUES (19,NULL,1421,'pickup',NULL,NULL,NULL);
INSERT  IGNORE INTO `stage_orders` VALUES (19,NULL,1421,'delivery',NULL,NULL,NULL);
INSERT  IGNORE INTO `stage_orders` VALUES (19,NULL,1422,'pickup',NULL,NULL,NULL);
INSERT  IGNORE INTO `stage_orders` VALUES (19,NULL,1422,'delivery',NULL,NULL,NULL);
INSERT  IGNORE INTO `stage_orders` VALUES (20,NULL,1423,'pickup',NULL,NULL,NULL);
INSERT  IGNORE INTO `stage_orders` VALUES (20,NULL,1423,'delivery',NULL,NULL,NULL);
INSERT  IGNORE INTO `stage_orders` VALUES (20,NULL,1424,'pickup',NULL,NULL,NULL);
INSERT  IGNORE INTO `stage_orders` VALUES (20,NULL,1424,'delivery',NULL,NULL,NULL);
INSERT  IGNORE INTO `stage_orders` VALUES (20,NULL,1425,'pickup',NULL,NULL,NULL);
INSERT  IGNORE INTO `stage_orders` VALUES (20,NULL,1425,'delivery',NULL,NULL,NULL);
INSERT  IGNORE INTO `stage_orders` VALUES (20,NULL,1426,'pickup',NULL,NULL,NULL);
INSERT  IGNORE INTO `stage_orders` VALUES (20,NULL,1426,'delivery',NULL,NULL,NULL);
INSERT  IGNORE INTO `stage_orders` VALUES (20,NULL,1427,'pickup',NULL,NULL,NULL);
INSERT  IGNORE INTO `stage_orders` VALUES (20,NULL,1427,'delivery',NULL,NULL,NULL);
INSERT  IGNORE INTO `stage_orders` VALUES (21,NULL,1428,'pickup',NULL,NULL,NULL);
INSERT  IGNORE INTO `stage_orders` VALUES (21,NULL,1428,'delivery',NULL,NULL,NULL);
INSERT  IGNORE INTO `stage_orders` VALUES (21,NULL,1429,'pickup',NULL,NULL,NULL);
INSERT  IGNORE INTO `stage_orders` VALUES (21,NULL,1429,'delivery',NULL,NULL,NULL);
INSERT  IGNORE INTO `stage_orders` VALUES (21,NULL,1431,'pickup',NULL,NULL,NULL);
INSERT  IGNORE INTO `stage_orders` VALUES (21,NULL,1431,'delivery',NULL,NULL,NULL);
INSERT  IGNORE INTO `stage_orders` VALUES (21,NULL,1432,'pickup',NULL,NULL,NULL);
INSERT  IGNORE INTO `stage_orders` VALUES (21,NULL,1432,'delivery',NULL,NULL,NULL);
INSERT  IGNORE INTO `stage_orders` VALUES (21,NULL,1433,'pickup',NULL,NULL,NULL);
INSERT  IGNORE INTO `stage_orders` VALUES (21,NULL,1433,'delivery',NULL,NULL,NULL);
INSERT  IGNORE INTO `stage_orders` VALUES (22,NULL,1434,'pickup',NULL,NULL,NULL);
INSERT  IGNORE INTO `stage_orders` VALUES (22,NULL,1434,'delivery',NULL,NULL,NULL);
INSERT  IGNORE INTO `stage_orders` VALUES (22,NULL,1435,'pickup',NULL,NULL,NULL);
INSERT  IGNORE INTO `stage_orders` VALUES (22,NULL,1435,'delivery',NULL,NULL,NULL);
INSERT  IGNORE INTO `stage_orders` VALUES (22,NULL,1436,'pickup',NULL,NULL,NULL);
INSERT  IGNORE INTO `stage_orders` VALUES (22,NULL,1436,'delivery',NULL,NULL,NULL);
INSERT  IGNORE INTO `stage_orders` VALUES (23,NULL,1437,'pickup',NULL,NULL,NULL);
INSERT  IGNORE INTO `stage_orders` VALUES (23,NULL,1437,'delivery',NULL,NULL,NULL);
INSERT  IGNORE INTO `stage_orders` VALUES (23,NULL,1438,'pickup',NULL,NULL,NULL);
INSERT  IGNORE INTO `stage_orders` VALUES (23,NULL,1438,'delivery',NULL,NULL,NULL);
INSERT  IGNORE INTO `stage_orders` VALUES (23,NULL,1439,'pickup',NULL,NULL,NULL);
INSERT  IGNORE INTO `stage_orders` VALUES (23,NULL,1439,'delivery',NULL,NULL,NULL);
INSERT  IGNORE INTO `stage_orders` VALUES (23,NULL,1440,'pickup',NULL,NULL,NULL);
INSERT  IGNORE INTO `stage_orders` VALUES (23,NULL,1440,'delivery',NULL,NULL,NULL);
INSERT  IGNORE INTO `stage_orders` VALUES (23,NULL,1441,'pickup',NULL,NULL,NULL);
INSERT  IGNORE INTO `stage_orders` VALUES (23,NULL,1441,'delivery',NULL,NULL,NULL);
INSERT  IGNORE INTO `stage_orders` VALUES (24,NULL,1442,'pickup',NULL,NULL,NULL);
INSERT  IGNORE INTO `stage_orders` VALUES (24,NULL,1442,'delivery',NULL,NULL,NULL);
INSERT  IGNORE INTO `stage_orders` VALUES (25,NULL,1443,'pickup',NULL,NULL,NULL);
INSERT  IGNORE INTO `stage_orders` VALUES (25,NULL,1443,'delivery',NULL,NULL,NULL);
INSERT  IGNORE INTO `stage_orders` VALUES (25,NULL,1444,'pickup',NULL,NULL,NULL);
INSERT  IGNORE INTO `stage_orders` VALUES (25,NULL,1444,'delivery',NULL,NULL,NULL);
INSERT  IGNORE INTO `stage_orders` VALUES (25,NULL,1446,'pickup',NULL,NULL,NULL);
INSERT  IGNORE INTO `stage_orders` VALUES (25,NULL,1446,'delivery',NULL,NULL,NULL);
INSERT  IGNORE INTO `stage_orders` VALUES (26,NULL,1447,'pickup',NULL,NULL,NULL);
INSERT  IGNORE INTO `stage_orders` VALUES (26,NULL,1447,'delivery',NULL,NULL,NULL);
INSERT  IGNORE INTO `stage_orders` VALUES (26,NULL,1448,'pickup',NULL,NULL,NULL);
INSERT  IGNORE INTO `stage_orders` VALUES (26,NULL,1448,'delivery',NULL,NULL,NULL);
INSERT  IGNORE INTO `stage_orders` VALUES (27,NULL,1449,'pickup',NULL,NULL,NULL);
INSERT  IGNORE INTO `stage_orders` VALUES (27,NULL,1449,'delivery',NULL,NULL,NULL);
INSERT  IGNORE INTO `stage_orders` VALUES (27,1,1502,'pickup',100,NULL,NULL);
INSERT  IGNORE INTO `stage_orders` VALUES (27,1,1502,'delivery',NULL,NULL,NULL);
INSERT  IGNORE INTO `stage_orders` VALUES (27,NULL,1503,'pickup',NULL,NULL,NULL);
INSERT  IGNORE INTO `stage_orders` VALUES (27,NULL,1503,'delivery',NULL,NULL,NULL);
INSERT  IGNORE INTO `stage_orders` VALUES (27,NULL,1504,'pickup',NULL,NULL,NULL);
INSERT  IGNORE INTO `stage_orders` VALUES (27,NULL,1504,'delivery',NULL,NULL,NULL);
INSERT  IGNORE INTO `stage_orders` VALUES (27,NULL,1505,'pickup',NULL,NULL,NULL);
INSERT  IGNORE INTO `stage_orders` VALUES (27,NULL,1505,'delivery',NULL,NULL,NULL);
INSERT  IGNORE INTO `stage_orders` VALUES (28,1,1506,'pickup',100,NULL,NULL);
INSERT  IGNORE INTO `stage_orders` VALUES (28,1,1506,'delivery',NULL,NULL,NULL);
INSERT  IGNORE INTO `stage_orders` VALUES (28,NULL,1507,'pickup',100,NULL,NULL);
INSERT  IGNORE INTO `stage_orders` VALUES (28,NULL,1507,'delivery',NULL,NULL,NULL);
INSERT  IGNORE INTO `stage_orders` VALUES (29,2,1508,'pickup',100,NULL,NULL);
INSERT  IGNORE INTO `stage_orders` VALUES (29,2,1508,'delivery',NULL,NULL,NULL);
INSERT  IGNORE INTO `stage_orders` VALUES (30,NULL,1509,'pickup',NULL,NULL,NULL);
INSERT  IGNORE INTO `stage_orders` VALUES (30,NULL,1509,'delivery',NULL,NULL,NULL);
INSERT  IGNORE INTO `stage_orders` VALUES (31,NULL,1510,'pickup',NULL,NULL,NULL);
INSERT  IGNORE INTO `stage_orders` VALUES (31,NULL,1510,'delivery',NULL,NULL,NULL);
INSERT  IGNORE INTO `stage_orders` VALUES (29,NULL,1511,'pickup',NULL,NULL,NULL);
INSERT  IGNORE INTO `stage_orders` VALUES (29,NULL,1511,'delivery',NULL,NULL,NULL);
INSERT  IGNORE INTO `stage_orders` VALUES (29,NULL,1513,'pickup',103,NULL,NULL);
INSERT  IGNORE INTO `stage_orders` VALUES (29,NULL,1513,'delivery',NULL,NULL,NULL);
INSERT  IGNORE INTO `stage_orders` VALUES (NULL,NULL,1514,'pickup',100,NULL,NULL);
INSERT  IGNORE INTO `stage_orders` VALUES (NULL,NULL,1514,'delivery',NULL,NULL,NULL);
INSERT  IGNORE INTO `stage_orders` VALUES (32,NULL,1515,'pickup',103,NULL,NULL);
INSERT  IGNORE INTO `stage_orders` VALUES (32,NULL,1515,'delivery',NULL,NULL,NULL);
INSERT  IGNORE INTO `stage_orders` VALUES (33,NULL,1516,'pickup',104,NULL,NULL);
INSERT  IGNORE INTO `stage_orders` VALUES (33,NULL,1516,'delivery',NULL,NULL,NULL);
INSERT  IGNORE INTO `stage_orders` VALUES (34,NULL,1517,'pickup',104,NULL,NULL);
INSERT  IGNORE INTO `stage_orders` VALUES (34,NULL,1517,'delivery',NULL,NULL,NULL);
INSERT  IGNORE INTO `stage_orders` VALUES (34,NULL,1518,'pickup',104,NULL,NULL);
INSERT  IGNORE INTO `stage_orders` VALUES (34,NULL,1518,'delivery',NULL,NULL,NULL);
INSERT  IGNORE INTO `stage_orders` VALUES (33,NULL,1519,'pickup',104,NULL,NULL);
INSERT  IGNORE INTO `stage_orders` VALUES (33,NULL,1519,'delivery',NULL,NULL,NULL);
INSERT  IGNORE INTO `stage_orders` VALUES (33,NULL,1520,'pickup',104,NULL,NULL);
INSERT  IGNORE INTO `stage_orders` VALUES (33,NULL,1520,'delivery',NULL,NULL,NULL);
INSERT  IGNORE INTO `stage_orders` VALUES (34,NULL,1521,'pickup',104,NULL,NULL);
INSERT  IGNORE INTO `stage_orders` VALUES (34,NULL,1521,'delivery',NULL,NULL,NULL);
INSERT  IGNORE INTO `stage_orders` VALUES (34,NULL,1522,'pickup',104,NULL,NULL);
INSERT  IGNORE INTO `stage_orders` VALUES (34,NULL,1522,'delivery',NULL,NULL,NULL);
INSERT  IGNORE INTO `stage_orders` VALUES (34,NULL,1523,'pickup',104,NULL,NULL);
INSERT  IGNORE INTO `stage_orders` VALUES (34,NULL,1523,'delivery',NULL,NULL,NULL);
INSERT  IGNORE INTO `stage_orders` VALUES (35,NULL,1524,'pickup',104,NULL,NULL);
INSERT  IGNORE INTO `stage_orders` VALUES (35,NULL,1524,'delivery',NULL,NULL,NULL);
INSERT  IGNORE INTO `stage_orders` VALUES (36,NULL,1525,'pickup',100,NULL,NULL);
INSERT  IGNORE INTO `stage_orders` VALUES (36,NULL,1525,'delivery',103,NULL,NULL);
INSERT  IGNORE INTO `stage_orders` VALUES (NULL,NULL,1526,'pickup',NULL,NULL,NULL);
INSERT  IGNORE INTO `stage_orders` VALUES (NULL,NULL,1526,'delivery',NULL,NULL,NULL);
INSERT  IGNORE INTO `stage_orders` VALUES (41,1,1527,'pickup',NULL,NULL,NULL);
INSERT  IGNORE INTO `stage_orders` VALUES (41,1,1527,'delivery',NULL,NULL,NULL);
INSERT  IGNORE INTO `stage_orders` VALUES (43,1,1528,'pickup',NULL,NULL,NULL);
INSERT  IGNORE INTO `stage_orders` VALUES (43,1,1528,'delivery',NULL,NULL,NULL);
INSERT  IGNORE INTO `stage_orders` VALUES (NULL,NULL,1529,'pickup',NULL,NULL,NULL);
INSERT  IGNORE INTO `stage_orders` VALUES (NULL,NULL,1529,'delivery',NULL,NULL,NULL);
INSERT  IGNORE INTO `stage_orders` VALUES (NULL,NULL,1530,'pickup',NULL,NULL,NULL);
INSERT  IGNORE INTO `stage_orders` VALUES (NULL,NULL,1530,'delivery',NULL,NULL,NULL);
INSERT  IGNORE INTO `stage_orders` VALUES (45,1,1531,'pickup',100,26,200);
INSERT  IGNORE INTO `stage_orders` VALUES (45,1,1531,'delivery',NULL,NULL,NULL);
INSERT  IGNORE INTO `stage_orders` VALUES (NULL,NULL,1532,'pickup',NULL,NULL,NULL);
INSERT  IGNORE INTO `stage_orders` VALUES (NULL,NULL,1532,'delivery',NULL,NULL,NULL);
INSERT  IGNORE INTO `stage_orders` VALUES (NULL,NULL,1533,'pickup',NULL,NULL,NULL);
INSERT  IGNORE INTO `stage_orders` VALUES (NULL,NULL,1533,'delivery',NULL,NULL,NULL);
INSERT  IGNORE INTO `stage_orders` VALUES (NULL,2,1534,'pickup',NULL,24,200);
INSERT  IGNORE INTO `stage_orders` VALUES (NULL,2,1534,'delivery',NULL,NULL,NULL);
INSERT  IGNORE INTO `stage_orders` VALUES (NULL,NULL,1535,'pickup',100,NULL,NULL);
INSERT  IGNORE INTO `stage_orders` VALUES (NULL,NULL,1535,'delivery',NULL,NULL,NULL);
INSERT  IGNORE INTO `stage_orders` VALUES (44,1,1536,'pickup',100,NULL,NULL);
INSERT  IGNORE INTO `stage_orders` VALUES (44,1,1536,'delivery',103,NULL,NULL);
INSERT  IGNORE INTO `stage_orders` VALUES (NULL,NULL,1537,'pickup',NULL,NULL,NULL);
INSERT  IGNORE INTO `stage_orders` VALUES (NULL,NULL,1537,'delivery',NULL,NULL,NULL);
INSERT  IGNORE INTO `stage_orders` VALUES (NULL,NULL,1538,'pickup',NULL,NULL,NULL);
INSERT  IGNORE INTO `stage_orders` VALUES (NULL,NULL,1538,'delivery',NULL,NULL,NULL);
INSERT  IGNORE INTO `stage_orders` VALUES (NULL,NULL,1539,'pickup',NULL,NULL,NULL);
INSERT  IGNORE INTO `stage_orders` VALUES (NULL,NULL,1539,'delivery',NULL,NULL,NULL);
INSERT  IGNORE INTO `stage_orders` VALUES (NULL,NULL,1540,'pickup',NULL,NULL,NULL);
INSERT  IGNORE INTO `stage_orders` VALUES (NULL,NULL,1540,'delivery',NULL,NULL,NULL);
INSERT  IGNORE INTO `stage_orders` VALUES (NULL,NULL,1541,'pickup',NULL,NULL,NULL);
INSERT  IGNORE INTO `stage_orders` VALUES (NULL,NULL,1541,'delivery',NULL,NULL,NULL);

--
-- Table structure for table `trips`
--

DROP TABLE IF EXISTS `trips`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `trips` (
  `id` int NOT NULL AUTO_INCREMENT,
  `driver_user_id` int DEFAULT NULL,
  `from_city` varchar(100) NOT NULL,
  `to_city` varchar(100) NOT NULL,
  `pickup_locker_id` int DEFAULT NULL,
  `delivery_locker_id` int DEFAULT NULL,
  `status` varchar(50) DEFAULT 'trip_created',
  `description` varchar(255) DEFAULT NULL,
  `active` tinyint(1) DEFAULT '1',
  `created_at` datetime DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  KEY `fk_driver_user` (`driver_user_id`),
  KEY `pickup_locker_id` (`pickup_locker_id`),
  KEY `delivery_locker_id` (`delivery_locker_id`),
  CONSTRAINT `fk_driver_user` FOREIGN KEY (`driver_user_id`) REFERENCES `users` (`id`) ON DELETE RESTRICT,
  CONSTRAINT `trips_ibfk_1` FOREIGN KEY (`pickup_locker_id`) REFERENCES `lockers` (`id`),
  CONSTRAINT `trips_ibfk_2` FOREIGN KEY (`delivery_locker_id`) REFERENCES `lockers` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=46 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `trips`
--

INSERT  IGNORE INTO `trips` VALUES (1,NULL,'Msk','Spb',1,1,'trip_created',NULL,1,'2025-11-24 16:33:51');
INSERT  IGNORE INTO `trips` VALUES (2,NULL,'LOCAL','LOCAL',1,2,'trip_created',NULL,1,'2025-12-15 18:43:45');
INSERT  IGNORE INTO `trips` VALUES (3,NULL,'LOCAL','LOCAL',1,2,'trip_created',NULL,1,'2025-12-15 19:20:44');
INSERT  IGNORE INTO `trips` VALUES (4,NULL,'LOCAL','LOCAL',1,2,'trip_created',NULL,1,'2025-12-15 20:46:12');
INSERT  IGNORE INTO `trips` VALUES (5,NULL,'LOCAL','LOCAL',2,1,'trip_created',NULL,1,'2025-12-16 10:56:06');
INSERT  IGNORE INTO `trips` VALUES (6,NULL,'LOCAL','LOCAL',1,2,'trip_created',NULL,1,'2025-12-19 09:45:10');
INSERT  IGNORE INTO `trips` VALUES (7,NULL,'LOCAL','LOCAL',1,2,'trip_created',NULL,1,'2025-12-23 16:35:14');
INSERT  IGNORE INTO `trips` VALUES (8,NULL,'LOCAL','LOCAL',1,2,'trip_created',NULL,1,'2025-12-24 12:05:22');
INSERT  IGNORE INTO `trips` VALUES (9,NULL,'LOCAL','LOCAL',1,2,'trip_created',NULL,1,'2025-12-24 15:40:49');
INSERT  IGNORE INTO `trips` VALUES (10,NULL,'LOCAL','LOCAL',1,2,'trip_created',NULL,1,'2025-12-25 15:23:44');
INSERT  IGNORE INTO `trips` VALUES (11,NULL,'LOCAL','LOCAL',1,2,'trip_created',NULL,1,'2025-12-26 13:38:37');
INSERT  IGNORE INTO `trips` VALUES (12,NULL,'LOCAL','LOCAL',1,2,'trip_created',NULL,1,'2025-12-27 15:09:30');
INSERT  IGNORE INTO `trips` VALUES (13,NULL,'LOCAL','LOCAL',1,2,'trip_created',NULL,1,'2025-12-28 15:09:47');
INSERT  IGNORE INTO `trips` VALUES (14,NULL,'LOCAL','LOCAL',1,2,'trip_created',NULL,1,'2025-12-31 11:19:13');
INSERT  IGNORE INTO `trips` VALUES (15,NULL,'LOCAL','LOCAL',1,2,'trip_created',NULL,1,'2026-01-01 13:22:51');
INSERT  IGNORE INTO `trips` VALUES (16,NULL,'LOCAL','LOCAL',1,2,'trip_created',NULL,1,'2026-01-02 13:23:12');
INSERT  IGNORE INTO `trips` VALUES (17,NULL,'LOCAL','LOCAL',1,2,'trip_created',NULL,1,'2026-01-06 15:00:17');
INSERT  IGNORE INTO `trips` VALUES (18,NULL,'LOCAL','LOCAL',1,2,'trip_created',NULL,1,'2026-01-09 17:03:28');
INSERT  IGNORE INTO `trips` VALUES (19,NULL,'LOCAL','LOCAL',1,2,'trip_created',NULL,1,'2026-01-11 11:45:19');
INSERT  IGNORE INTO `trips` VALUES (20,NULL,'LOCAL','LOCAL',1,2,'trip_created',NULL,1,'2026-01-12 12:13:23');
INSERT  IGNORE INTO `trips` VALUES (21,NULL,'LOCAL','LOCAL',1,2,'trip_created',NULL,1,'2026-01-12 15:50:39');
INSERT  IGNORE INTO `trips` VALUES (22,NULL,'LOCAL','LOCAL',1,2,'trip_created',NULL,1,'2026-01-13 15:24:59');
INSERT  IGNORE INTO `trips` VALUES (23,NULL,'LOCAL','LOCAL',1,2,'trip_created',NULL,1,'2026-01-15 07:50:55');
INSERT  IGNORE INTO `trips` VALUES (24,NULL,'LOCAL','LOCAL',1,2,'trip_created',NULL,1,'2026-01-15 20:52:14');
INSERT  IGNORE INTO `trips` VALUES (25,NULL,'LOCAL','LOCAL',1,2,'trip_created',NULL,1,'2026-01-27 14:17:24');
INSERT  IGNORE INTO `trips` VALUES (26,NULL,'LOCAL','LOCAL',1,2,'trip_created',NULL,1,'2026-01-28 14:55:23');
INSERT  IGNORE INTO `trips` VALUES (27,NULL,'LOCAL','LOCAL',1,2,'trip_created',NULL,1,'2026-02-04 15:52:58');
INSERT  IGNORE INTO `trips` VALUES (28,NULL,'LOCAL','LOCAL',1,2,'trip_created',NULL,1,'2026-02-06 05:53:12');
INSERT  IGNORE INTO `trips` VALUES (29,NULL,'СПБ','МСК',2,1,'trip_assigned',NULL,1,'2026-02-08 13:22:43');
INSERT  IGNORE INTO `trips` VALUES (30,NULL,'СПБ','МСК',4,3,'trip_assigned',NULL,1,'2026-02-10 15:14:05');
INSERT  IGNORE INTO `trips` VALUES (31,200,'СПБ','МСК',4,1,'trip_assigned',NULL,1,'2026-02-10 17:07:31');
INSERT  IGNORE INTO `trips` VALUES (32,201,'СПБ','МСК',2,1,'trip_assigned',NULL,1,'2026-02-17 09:47:28');
INSERT  IGNORE INTO `trips` VALUES (33,NULL,'СПБ','МСК',2,1,'trip_in_progress',NULL,1,'2026-02-17 14:29:41');
INSERT  IGNORE INTO `trips` VALUES (34,200,'СПБ','МСК',4,3,'trip_assigned',NULL,1,'2026-02-17 14:30:01');
INSERT  IGNORE INTO `trips` VALUES (35,NULL,'СПБ','МСК',4,3,'trip_created',NULL,1,'2026-02-17 18:08:13');
INSERT  IGNORE INTO `trips` VALUES (36,201,'МСК','СПБ',3,4,'trip_completed',NULL,1,'2026-02-25 11:53:37');
INSERT  IGNORE INTO `trips` VALUES (38,200,'МСК','СПБ',1,2,'trip_completed',NULL,1,'2026-03-18 16:26:08');
INSERT  IGNORE INTO `trips` VALUES (39,200,'МСК','СПБ',1,2,'trip_assigned',NULL,1,'2026-03-22 15:16:50');
INSERT  IGNORE INTO `trips` VALUES (40,200,'МСК','СПБ',1,2,'trip_assigned',NULL,1,'2026-03-23 06:23:09');
INSERT  IGNORE INTO `trips` VALUES (41,200,'МСК','СПБ',1,2,'trip_assigned',NULL,1,'2026-03-23 09:46:15');
INSERT  IGNORE INTO `trips` VALUES (43,200,'МСК','СПБ',1,2,'trip_in_progress',NULL,1,'2026-03-23 17:19:44');
INSERT  IGNORE INTO `trips` VALUES (44,200,'МСК','СПБ',1,2,'trip_in_progress',NULL,1,'2026-03-30 16:16:49');
INSERT  IGNORE INTO `trips` VALUES (45,200,'МСК','СПБ',1,2,'trip_in_progress',NULL,1,'2026-04-01 09:59:12');

--
-- Table structure for table `users`
--

DROP TABLE IF EXISTS `users`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `users` (
  `id` int NOT NULL AUTO_INCREMENT,
  `name` varchar(255) NOT NULL,
  `role_name` varchar(50) NOT NULL DEFAULT 'client',
  `city` varchar(100) NOT NULL DEFAULT '',
  `phone` varchar(20) DEFAULT NULL COMMENT 'Номер телефона в формате +79991234567',
  PRIMARY KEY (`id`),
  KEY `role_name` (`role_name`)
) ENGINE=InnoDB AUTO_INCREMENT=1000025 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `users`
--

INSERT  IGNORE INTO `users` VALUES (1,'User 1','driver','',NULL);
INSERT  IGNORE INTO `users` VALUES (2,'User 2','courier','',NULL);
INSERT  IGNORE INTO `users` VALUES (3,'User 3','client','',NULL);
INSERT  IGNORE INTO `users` VALUES (4,'User 4','recipient','',NULL);
INSERT  IGNORE INTO `users` VALUES (5,'User 5','courier','',NULL);
INSERT  IGNORE INTO `users` VALUES (10,'Client','client','',NULL);
INSERT  IGNORE INTO `users` VALUES (20,'Courier1','courier','',NULL);
INSERT  IGNORE INTO `users` VALUES (21,'Courier2','courier','',NULL);
INSERT  IGNORE INTO `users` VALUES (30,'Driver','driver','',NULL);
INSERT  IGNORE INTO `users` VALUES (40,'Recipient','recipient','',NULL);
INSERT  IGNORE INTO `users` VALUES (100,'Курьер 100','courier','Москва',NULL);
INSERT  IGNORE INTO `users` VALUES (101,'Курьер 101','courier','Москва',NULL);
INSERT  IGNORE INTO `users` VALUES (102,'Курьер 102','courier','Москва',NULL);
INSERT  IGNORE INTO `users` VALUES (103,'Курьер 103','courier','Санкт-Петербург',NULL);
INSERT  IGNORE INTO `users` VALUES (104,'Курьер 104','courier','Санкт-Петербург',NULL);
INSERT  IGNORE INTO `users` VALUES (200,'Водитель 200','driver','',NULL);
INSERT  IGNORE INTO `users` VALUES (201,'Водитель 201','driver','',NULL);
INSERT  IGNORE INTO `users` VALUES (202,'Водитель 202','driver','',NULL);
INSERT  IGNORE INTO `users` VALUES (203,'Водитель 203','driver','',NULL);
INSERT  IGNORE INTO `users` VALUES (204,'Водитель 204','driver','',NULL);
INSERT  IGNORE INTO `users` VALUES (301,'Клиент Алиса','client','',NULL);
INSERT  IGNORE INTO `users` VALUES (302,'Курьер Борис','courier','',NULL);
INSERT  IGNORE INTO `users` VALUES (303,'Курьер Виктор','courier','',NULL);
INSERT  IGNORE INTO `users` VALUES (304,'Водитель Дима','driver','',NULL);
INSERT  IGNORE INTO `users` VALUES (305,'Получатель Ева','recipient','',NULL);
INSERT  IGNORE INTO `users` VALUES (777,'Оператор 777','operator','',NULL);
INSERT  IGNORE INTO `users` VALUES (888,'Оператор 888','operator','',NULL);
INSERT  IGNORE INTO `users` VALUES (1001,'Клиент 1001','client','Москва',NULL);
INSERT  IGNORE INTO `users` VALUES (1002,'Клиент 1002','client','Москва',NULL);
INSERT  IGNORE INTO `users` VALUES (1003,'Клиент 1003','client','Москва',NULL);
INSERT  IGNORE INTO `users` VALUES (1004,'Клиент 1004','client','Санкт-Петербург',NULL);
INSERT  IGNORE INTO `users` VALUES (1005,'Клиент 1005','client','Санкт-Петербург','+79199030069');
INSERT  IGNORE INTO `users` VALUES (2001,'Получатель 2001','recipient','Москва',NULL);
INSERT  IGNORE INTO `users` VALUES (2002,'Получатель 2002','recipient','Москва',NULL);
INSERT  IGNORE INTO `users` VALUES (2003,'Получатель 2003','recipient','Москва',NULL);
INSERT  IGNORE INTO `users` VALUES (2004,'Получатель 2004','recipient','Санкт-Петербург',NULL);
INSERT  IGNORE INTO `users` VALUES (2005,'Получатель 2005','recipient','Санкт-Петербург',NULL);
INSERT  IGNORE INTO `users` VALUES (2006,'System','system','',NULL);
INSERT  IGNORE INTO `users` VALUES (999999,'System','system','',NULL);
INSERT  IGNORE INTO `users` VALUES (1000006,'Иван Петров','driver','Москва','+79991285518');
INSERT  IGNORE INTO `users` VALUES (1000007,'Андрей Петров','client','Москва','+79991283080');
INSERT  IGNORE INTO `users` VALUES (1000008,'Андрей Петров','client','Санкт-Петербург','+79991283090');
INSERT  IGNORE INTO `users` VALUES (1000009,'Андрей Петров','client','Санкт-Петербург','+79991283590');
INSERT  IGNORE INTO `users` VALUES (1000010,'Андрей Петров','client','Санкт-Петербург','+79991783590');
INSERT  IGNORE INTO `users` VALUES (1000011,'Андрей Петров','client','Санкт-Петербург','+79991883590');
INSERT  IGNORE INTO `users` VALUES (1000012,'Андрей Петров','client','Санкт-Петербург','+79991892590');
INSERT  IGNORE INTO `users` VALUES (1000013,'Андрей Петров','client','Санкт-Петербург','+79991833590');
INSERT  IGNORE INTO `users` VALUES (1000014,'Сергей Петров','client','Санкт-Петербург','+79991833890');
INSERT  IGNORE INTO `users` VALUES (1000015,'Леха Петров','driver','Москва','+79991283123');
INSERT  IGNORE INTO `users` VALUES (1000016,'Леха1 Петров','driver','Москва','+79991283111');
INSERT  IGNORE INTO `users` VALUES (1000017,'Леха12 Петров','driver','Москва','+79991283121');
INSERT  IGNORE INTO `users` VALUES (1000018,'Леха12 Петров','courier','Москва','+79991288921');
INSERT  IGNORE INTO `users` VALUES (1000019,'Леха85 Петров','client','Москва','+79991288881');
INSERT  IGNORE INTO `users` VALUES (1000020,'Максим','client','string','+79990001136');
INSERT  IGNORE INTO `users` VALUES (1000021,'Максим12','client','string','+79990001112');
INSERT  IGNORE INTO `users` VALUES (1000022,'Максим13','driver','string','+79990001113');
INSERT  IGNORE INTO `users` VALUES (1000023,'Максим73','driver','string','+79990001173');
INSERT  IGNORE INTO `users` VALUES (1000024,'Максим79','courier','string','+79990001183');

--
-- Dumping events for database 'testdb'
--
/*!50106 SET @save_time_zone= @@TIME_ZONE */ ;
/*!50106 DROP EVENT IF EXISTS `cleanup_old_logs` */;
DELIMITER ;;
/*!50003 SET @saved_cs_client      = @@character_set_client */ ;;
/*!50003 SET @saved_cs_results     = @@character_set_results */ ;;
/*!50003 SET @saved_col_connection = @@collation_connection */ ;;
/*!50003 SET character_set_client  = utf8mb4 */ ;;
/*!50003 SET character_set_results = utf8mb4 */ ;;
/*!50003 SET collation_connection  = utf8mb4_0900_ai_ci */ ;;
/*!50003 SET @saved_sql_mode       = @@sql_mode */ ;;
/*!50003 SET sql_mode              = 'ONLY_FULL_GROUP_BY,STRICT_TRANS_TABLES,NO_ZERO_IN_DATE,NO_ZERO_DATE,ERROR_FOR_DIVISION_BY_ZERO,NO_ENGINE_SUBSTITUTION' */ ;;
/*!50003 SET @saved_time_zone      = @@time_zone */ ;;
/*!50003 SET time_zone             = 'SYSTEM' */ ;;
/*!50106 CREATE*/ /*!50117 DEFINER=`fsm`@`localhost`*/ /*!50106 EVENT `cleanup_old_logs` ON SCHEDULE EVERY 1 DAY STARTS '2025-12-12 00:00:00' ON COMPLETION NOT PRESERVE ENABLE DO BEGIN
    DELETE FROM fsm_action_logs
    WHERE created_at < NOW() - INTERVAL 30 DAY;

    DELETE FROM fsm_errors_log
    WHERE error_time < NOW() - INTERVAL 30 DAY;

    DELETE FROM hardware_command_log
    WHERE executed_at < NOW() - INTERVAL 30 DAY;
END */ ;;
/*!50003 SET time_zone             = @saved_time_zone */ ;;
/*!50003 SET sql_mode              = @saved_sql_mode */ ;;
/*!50003 SET character_set_client  = @saved_cs_client */ ;;
/*!50003 SET character_set_results = @saved_cs_results */ ;;
/*!50003 SET collation_connection  = @saved_col_connection */ ;;
DELIMITER ;
/*!50106 SET TIME_ZONE= @save_time_zone */ ;

--
-- Dumping routines for database 'testdb'
--
/*!50003 DROP PROCEDURE IF EXISTS `clear_test_data` */;
/*!50003 SET @saved_cs_client      = @@character_set_client */ ;
/*!50003 SET @saved_cs_results     = @@character_set_results */ ;
/*!50003 SET @saved_col_connection = @@collation_connection */ ;
/*!50003 SET character_set_client  = utf8mb4 */ ;
/*!50003 SET character_set_results = utf8mb4 */ ;
/*!50003 SET collation_connection  = utf8mb4_0900_ai_ci */ ;
/*!50003 SET @saved_sql_mode       = @@sql_mode */ ;
/*!50003 SET sql_mode              = 'ONLY_FULL_GROUP_BY,STRICT_TRANS_TABLES,NO_ZERO_IN_DATE,NO_ZERO_DATE,ERROR_FOR_DIVISION_BY_ZERO,NO_ENGINE_SUBSTITUTION' */ ;
DELIMITER ;;
CREATE DEFINER=`fsm`@`localhost` PROCEDURE `clear_test_data`()
BEGIN
    -- Очищаем логи и служебные таблицы
    DELETE FROM fsm_action_logs;
    DELETE FROM fsm_errors_log;
    DELETE FROM hardware_command_log;
    DELETE FROM server_fsm_instances;

    -- Сбрасываем stage_orders
    DELETE FROM stage_orders;

    -- Сбрасываем заказы и связанные сущности
    UPDATE locker_cells
    SET
        status = 'locker_free',
        reservation_expires_at = NULL,
        code_expires_at = NULL,
        unlock_code = NULL,
        reserved_for_user_id = NULL,
        current_order_id = NULL,
        failed_open_attempts = 0;

    DELETE FROM orders;

    -- Можно добавить очистку других тестовых данных по необходимости
END ;;
DELIMITER ;
/*!50003 SET sql_mode              = @saved_sql_mode */ ;
/*!50003 SET character_set_client  = @saved_cs_client */ ;
/*!50003 SET character_set_results = @saved_cs_results */ ;
/*!50003 SET collation_connection  = @saved_col_connection */ ;
/*!50003 DROP PROCEDURE IF EXISTS `fsm_perform_action` */;
/*!50003 SET @saved_cs_client      = @@character_set_client */ ;
/*!50003 SET @saved_cs_results     = @@character_set_results */ ;
/*!50003 SET @saved_col_connection = @@collation_connection */ ;
/*!50003 SET character_set_client  = utf8mb4 */ ;
/*!50003 SET character_set_results = utf8mb4 */ ;
/*!50003 SET collation_connection  = utf8mb4_0900_ai_ci */ ;
/*!50003 SET @saved_sql_mode       = @@sql_mode */ ;
/*!50003 SET sql_mode              = 'ONLY_FULL_GROUP_BY,STRICT_TRANS_TABLES,NO_ZERO_IN_DATE,NO_ZERO_DATE,ERROR_FOR_DIVISION_BY_ZERO,NO_ENGINE_SUBSTITUTION' */ ;
DELIMITER ;;
CREATE DEFINER=`fsm`@`localhost` PROCEDURE `fsm_perform_action`(
    IN p_entity_type VARCHAR(50) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci,
    IN p_entity_id INT,
    IN p_action_name VARCHAR(100) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci,
    IN p_user_id INT,
    IN p_extra_id VARCHAR(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci
)
BEGIN
    DECLARE v_action_id INT;
    DECLARE v_from_state_id INT;
    DECLARE v_to_state_id INT;
    DECLARE v_from_state_name VARCHAR(50);
    DECLARE v_to_state_name VARCHAR(50);
    DECLARE v_now DATETIME;

    SET v_now = NOW();

    SELECT id INTO v_action_id
    FROM fsm_actions
    WHERE name = p_action_name;

    IF v_action_id IS NULL THEN
        SIGNAL SQLSTATE '45000'
        SET MESSAGE_TEXT = 'Unknown action_name in fsm_actions';
    END IF;

    IF p_entity_type = 'locker' THEN
        SELECT id, name INTO v_from_state_id, v_from_state_name
        FROM fsm_states
        WHERE name = (
            SELECT status
            FROM locker_cells
            WHERE id = p_entity_id
        );

        IF v_from_state_id IS NULL THEN
            SIGNAL SQLSTATE '45000'
            SET MESSAGE_TEXT = 'Unknown from_state for locker in fsm_states';
        END IF;

        SELECT
            ft.id,
            fs_to.name
        INTO
            v_to_state_id,
            v_to_state_name
        FROM fsm_transitions ft
        JOIN fsm_states fs_to ON fs_to.id = ft.to_state_id
        WHERE
            ft.from_state_id = v_from_state_id
            AND ft.action_id = v_action_id;

        IF v_to_state_id IS NULL THEN
            SIGNAL SQLSTATE '45000'
            SET MESSAGE_TEXT = 'Invalid transition for locker: no matching fsm_transitions';
        END IF;

        UPDATE locker_cells
        SET status = v_to_state_name
        WHERE id = p_entity_id;

        INSERT INTO fsm_action_logs (
            entity_type,
            entity_id,
            action_name,
            from_state,
            to_state,
            user_id,
            created_at
        )
        VALUES (
            'locker',
            p_entity_id,
            p_action_name,
            v_from_state_name,
            v_to_state_name,
            p_user_id,
            v_now
        );

    ELSEIF p_entity_type = 'order' THEN
        SELECT id, name INTO v_from_state_id, v_from_state_name
        FROM fsm_states
        WHERE name = (
            SELECT status
            FROM orders
            WHERE id = p_entity_id
        );

        IF v_from_state_id IS NULL THEN
            SIGNAL SQLSTATE '45000'
            SET MESSAGE_TEXT = 'Unknown from_state for order in fsm_states';
        END IF;

        SELECT
            ft.id,
            fs_to.name
        INTO
            v_to_state_id,
            v_to_state_name
        FROM fsm_transitions ft
        JOIN fsm_states fs_to ON fs_to.id = ft.to_state_id
        WHERE
            ft.from_state_id = v_from_state_id
            AND ft.action_id = v_action_id;

        IF v_to_state_id IS NULL THEN
            SIGNAL SQLSTATE '45000'
            SET MESSAGE_TEXT = 'Invalid transition for order: no matching fsm_transitions';
        END IF;

        UPDATE orders
        SET status = v_to_state_name
        WHERE id = p_entity_id;

        INSERT INTO fsm_action_logs (
            entity_type,
            entity_id,
            action_name,
            from_state,
            to_state,
            user_id,
            created_at
        )
        VALUES (
            'order',
            p_entity_id,
            p_action_name,
            v_from_state_name,
            v_to_state_name,
            p_user_id,
            v_now
        );
        
	ELSEIF p_entity_type = 'trip' THEN
		-- Получаем текущее состояние рейса
		SELECT id, name INTO v_from_state_id, v_from_state_name
		FROM fsm_states
		WHERE name = (
			SELECT status
			FROM trips
			WHERE id = p_entity_id
		);

		IF v_from_state_id IS NULL THEN
			SIGNAL SQLSTATE '45000'
			SET MESSAGE_TEXT = 'Unknown from_state for trip in fsm_states';
		END IF;

		-- Ищем разрешённый переход
		SELECT
			ft.id,
			fs_to.name
		INTO
			v_to_state_id,
			v_to_state_name
		FROM fsm_transitions ft
		JOIN fsm_states fs_to ON fs_to.id = ft.to_state_id
		WHERE
			ft.from_state_id = v_from_state_id
			AND ft.action_id = v_action_id;

		IF v_to_state_id IS NULL THEN
			SIGNAL SQLSTATE '45000'
			SET MESSAGE_TEXT = 'Invalid transition for trip: no matching fsm_transitions';
		END IF;

		-- Обновляем статус рейса
		UPDATE trips
		SET status = v_to_state_name
		WHERE id = p_entity_id;

		-- Логируем действие
		INSERT INTO fsm_action_logs (
			entity_type,
			entity_id,
			action_name,
			from_state,
			to_state,
			user_id,
			created_at
		)
		VALUES (
			'trip',
			p_entity_id,
			p_action_name,
			v_from_state_name,
			v_to_state_name,
			p_user_id,
			v_now
		);        
	
	ELSEIF p_entity_type = 'driver_reservations' THEN
        SELECT id, name INTO v_from_state_id, v_from_state_name
        FROM fsm_states
        WHERE name = (SELECT status FROM driver_reservations WHERE id = p_entity_id);
        
        IF v_from_state_id IS NULL THEN
            SIGNAL SQLSTATE '45000'
            SET MESSAGE_TEXT = 'Unknown from_state for driver_reservations in fsm_states';
        END IF;
        
        SELECT ft.id, fs_to.name INTO v_to_state_id, v_to_state_name
        FROM fsm_transitions ft
        JOIN fsm_states fs_to ON fs_to.id = ft.to_state_id
        WHERE ft.from_state_id = v_from_state_id AND ft.action_id = v_action_id;
        
        IF v_to_state_id IS NULL THEN
            SIGNAL SQLSTATE '45000'
            SET MESSAGE_TEXT = 'Invalid transition for driver_reservations: no matching fsm_transitions';
        END IF;
        
        UPDATE driver_reservations SET status = v_to_state_name WHERE id = p_entity_id;
        
        INSERT INTO fsm_action_logs (entity_type, entity_id, action_name, from_state, to_state, user_id, created_at)
        VALUES ('driver_reservations', p_entity_id, p_action_name, v_from_state_name, v_to_state_name, p_user_id, v_now);
       
    ELSE
        SIGNAL SQLSTATE '45000'
        SET MESSAGE_TEXT = 'Unsupported entity_type in fsm_perform_action';
    END IF;
    
    -- возвращаем результат
    SELECT CONCAT('FSM action completed: ', v_from_state_name, ' -> ', v_to_state_name) AS result;
END ;;
DELIMITER ;
/*!50003 SET sql_mode              = @saved_sql_mode */ ;
/*!50003 SET character_set_client  = @saved_cs_client */ ;
/*!50003 SET character_set_results = @saved_cs_results */ ;
/*!50003 SET collation_connection  = @saved_col_connection */ ;
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed
