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
) ENGINE=InnoDB AUTO_INCREMENT=77 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
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
) ENGINE=InnoDB AUTO_INCREMENT=5 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `cell_access_tokens`
--

INSERT  IGNORE INTO `cell_access_tokens` VALUES (1,1510,'pickup',31,1005,'490a6b4f6dc249bf934da7bf548b9dcaf12dc9b0fd286e5b67f08622a1f51777','ACTIVE','2026-02-11 18:35:47',0,'2026-02-11 18:20:46',NULL);
INSERT  IGNORE INTO `cell_access_tokens` VALUES (2,1510,'pickup',31,1005,'d60ec2ef2d0fe1a779ba88272fbf3db22d4fd179ef759270535a4f1cd72f58df','ACTIVE','2026-02-12 10:06:24',0,'2026-02-12 09:51:23',NULL);
INSERT  IGNORE INTO `cell_access_tokens` VALUES (3,1510,'pickup',31,1005,'736773fd5d112b0f3f87c7439b6c105f468cfb0e6b7dcf69b8fbfc1430492fe0','ACTIVE','2026-02-12 10:34:41',0,'2026-02-12 10:19:41',NULL);
INSERT  IGNORE INTO `cell_access_tokens` VALUES (4,1510,'pickup',31,1005,'1870472713a81a194e9547b279d83a6ed8aff8c4e6704fa4b126c4ce52db5c00','ACTIVE','2026-02-12 10:55:35',0,'2026-02-12 10:40:34',NULL);

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
) ENGINE=InnoDB AUTO_INCREMENT=1026 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `fsm_action_logs`
--

INSERT  IGNORE INTO `fsm_action_logs` VALUES (86,'order',1447,'order_cancel_reservation','order_created','order_cancelled',1005,'2026-01-28 15:12:44');
INSERT  IGNORE INTO `fsm_action_logs` VALUES (87,'locker',41,'locker_cancel_reservation','locker_reserved','locker_free',1005,'2026-01-28 15:12:44');
INSERT  IGNORE INTO `fsm_action_logs` VALUES (88,'locker',44,'locker_cancel_reservation','locker_reserved','locker_free',1005,'2026-01-28 15:12:44');
INSERT  IGNORE INTO `fsm_action_logs` VALUES (89,'order',1446,'order_cancel_reservation','order_created','order_cancelled',1004,'2026-01-28 15:12:59');
INSERT  IGNORE INTO `fsm_action_logs` VALUES (90,'locker',43,'locker_cancel_reservation','locker_reserved','locker_free',1004,'2026-01-28 15:12:59');
INSERT  IGNORE INTO `fsm_action_logs` VALUES (91,'locker',45,'locker_cancel_reservation','locker_reserved','locker_free',1004,'2026-01-28 15:12:59');
INSERT  IGNORE INTO `fsm_action_logs` VALUES (92,'order',1503,'order_cancel_reservation','order_created','order_cancelled',1004,'2026-02-05 08:25:26');
INSERT  IGNORE INTO `fsm_action_logs` VALUES (93,'locker',1,'locker_cancel_reservation','locker_reserved','locker_free',1004,'2026-02-05 08:25:26');
INSERT  IGNORE INTO `fsm_action_logs` VALUES (94,'locker',12,'locker_cancel_reservation','locker_reserved','locker_free',1004,'2026-02-05 08:25:26');
INSERT  IGNORE INTO `fsm_action_logs` VALUES (95,'order',1502,'order_assign_courier1_to_order','order_created','order_courier1_assigned',100,'2026-02-05 09:11:47');
INSERT  IGNORE INTO `fsm_action_logs` VALUES (96,'order',1508,'order_assign_courier1_to_order','order_created','order_courier1_assigned',100,'2026-02-08 14:16:14');
INSERT  IGNORE INTO `fsm_action_logs` VALUES (97,'order',1508,'order_courier1_cancel','order_courier1_assigned','order_created',100,'2026-02-08 14:16:54');
INSERT  IGNORE INTO `fsm_action_logs` VALUES (98,'order',1508,'order_assign_courier1_to_order','order_created','order_courier1_assigned',100,'2026-02-08 14:17:49');
INSERT  IGNORE INTO `fsm_action_logs` VALUES (99,'order',1508,'order_courier1_cancel','order_courier1_assigned','order_created',100,'2026-02-08 14:18:09');
INSERT  IGNORE INTO `fsm_action_logs` VALUES (100,'order',1507,'order_assign_courier1_to_order','order_created','order_courier1_assigned',100,'2026-02-13 13:21:22');
INSERT  IGNORE INTO `fsm_action_logs` VALUES (101,'order',1508,'order_assign_courier1_to_order','order_created','order_courier1_assigned',100,'2026-02-13 13:21:52');
INSERT  IGNORE INTO `fsm_action_logs` VALUES (102,'order',1384,'order_cancel_reservation','order_created','order_cancelled',1001,'2026-02-13 14:24:35');
INSERT  IGNORE INTO `fsm_action_logs` VALUES (103,'locker',5,'locker_cancel_reservation','locker_reserved','locker_free',1001,'2026-02-13 14:24:35');
INSERT  IGNORE INTO `fsm_action_logs` VALUES (104,'locker',15,'locker_cancel_reservation','locker_reserved','locker_free',1001,'2026-02-13 14:24:35');
INSERT  IGNORE INTO `fsm_action_logs` VALUES (105,'order',1380,'order_cancel_reservation','order_created','order_cancelled',1001,'2026-02-13 14:24:45');
INSERT  IGNORE INTO `fsm_action_logs` VALUES (106,'locker',42,'locker_cancel_reservation','locker_reserved','locker_free',1001,'2026-02-13 14:24:45');
INSERT  IGNORE INTO `fsm_action_logs` VALUES (107,'locker',11,'locker_cancel_reservation','locker_reserved','locker_free',1001,'2026-02-13 14:24:45');
INSERT  IGNORE INTO `fsm_action_logs` VALUES (108,'order',1381,'order_cancel_reservation','order_created','order_cancelled',1001,'2026-02-13 14:24:55');
INSERT  IGNORE INTO `fsm_action_logs` VALUES (109,'locker',1,'locker_cancel_reservation','locker_reserved','locker_free',1001,'2026-02-13 14:24:55');
INSERT  IGNORE INTO `fsm_action_logs` VALUES (110,'locker',12,'locker_cancel_reservation','locker_reserved','locker_free',1001,'2026-02-13 14:24:55');
INSERT  IGNORE INTO `fsm_action_logs` VALUES (111,'order',1513,'order_assign_courier1_to_order','order_created','order_courier1_assigned',103,'2026-02-16 08:22:03');
INSERT  IGNORE INTO `fsm_action_logs` VALUES (112,'order',1513,'order_courier_pickup_parcel','order_courier1_assigned','order_courier_has_parcel',103,'2026-02-16 08:59:39');
INSERT  IGNORE INTO `fsm_action_logs` VALUES (113,'locker',15,'locker_open_locker','locker_reserved','locker_opened',103,'2026-02-16 08:59:39');
INSERT  IGNORE INTO `fsm_action_logs` VALUES (114,'order',1513,'order_confirm_parcel_in','order_courier_has_parcel','order_parcel_confirmed',103,'2026-02-16 09:00:24');
INSERT  IGNORE INTO `fsm_action_logs` VALUES (115,'locker',15,'locker_close_locker','locker_opened','locker_occupied',103,'2026-02-16 09:00:24');
INSERT  IGNORE INTO `fsm_action_logs` VALUES (116,'order',1515,'order_assign_courier1_to_order','order_created','order_courier1_assigned',103,'2026-02-17 09:42:53');
INSERT  IGNORE INTO `fsm_action_logs` VALUES (117,'order',1515,'order_courier_pickup_parcel','order_courier1_assigned','order_courier_has_parcel',103,'2026-02-17 09:46:38');
INSERT  IGNORE INTO `fsm_action_logs` VALUES (118,'locker',17,'locker_open_locker','locker_reserved','locker_opened',103,'2026-02-17 09:46:38');
INSERT  IGNORE INTO `fsm_action_logs` VALUES (119,'order',1515,'order_confirm_parcel_in','order_courier_has_parcel','order_parcel_confirmed',103,'2026-02-17 09:47:28');
INSERT  IGNORE INTO `fsm_action_logs` VALUES (120,'locker',17,'locker_close_locker','locker_opened','locker_occupied',103,'2026-02-17 09:47:28');
INSERT  IGNORE INTO `fsm_action_logs` VALUES (121,'trip',29,'trip_vzyat_reis','trip_created','trip_assigned',200,'2026-02-17 10:34:56');
INSERT  IGNORE INTO `fsm_action_logs` VALUES (122,'order',1516,'order_assign_courier1_to_order','order_created','order_courier1_assigned',104,'2026-02-17 14:25:46');
INSERT  IGNORE INTO `fsm_action_logs` VALUES (123,'order',1517,'order_assign_courier1_to_order','order_created','order_courier1_assigned',104,'2026-02-17 14:25:51');
INSERT  IGNORE INTO `fsm_action_logs` VALUES (124,'order',1516,'order_courier_pickup_parcel','order_courier1_assigned','order_courier_has_parcel',104,'2026-02-17 14:27:31');
INSERT  IGNORE INTO `fsm_action_logs` VALUES (125,'locker',18,'locker_open_locker','locker_reserved','locker_opened',104,'2026-02-17 14:27:31');
INSERT  IGNORE INTO `fsm_action_logs` VALUES (126,'order',1517,'order_courier_pickup_parcel','order_courier1_assigned','order_courier_has_parcel',104,'2026-02-17 14:28:21');
INSERT  IGNORE INTO `fsm_action_logs` VALUES (127,'locker',33,'locker_open_locker','locker_reserved','locker_opened',104,'2026-02-17 14:28:21');
INSERT  IGNORE INTO `fsm_action_logs` VALUES (128,'order',1516,'order_confirm_parcel_in','order_courier_has_parcel','order_parcel_confirmed',104,'2026-02-17 14:29:41');
INSERT  IGNORE INTO `fsm_action_logs` VALUES (129,'locker',18,'locker_close_locker','locker_opened','locker_occupied',104,'2026-02-17 14:29:41');
INSERT  IGNORE INTO `fsm_action_logs` VALUES (130,'order',1517,'order_confirm_parcel_in','order_courier_has_parcel','order_parcel_confirmed',104,'2026-02-17 14:30:01');
INSERT  IGNORE INTO `fsm_action_logs` VALUES (131,'locker',33,'locker_close_locker','locker_opened','locker_occupied',104,'2026-02-17 14:30:01');
INSERT  IGNORE INTO `fsm_action_logs` VALUES (132,'order',1518,'order_assign_courier1_to_order','order_created','order_courier1_assigned',104,'2026-02-17 14:44:37');
INSERT  IGNORE INTO `fsm_action_logs` VALUES (133,'order',1518,'order_courier_pickup_parcel','order_courier1_assigned','order_courier_has_parcel',104,'2026-02-17 14:45:17');
INSERT  IGNORE INTO `fsm_action_logs` VALUES (134,'locker',36,'locker_open_locker','locker_reserved','locker_opened',104,'2026-02-17 14:45:17');
INSERT  IGNORE INTO `fsm_action_logs` VALUES (135,'order',1518,'order_confirm_parcel_in','order_courier_has_parcel','order_parcel_confirmed',104,'2026-02-17 14:45:47');
INSERT  IGNORE INTO `fsm_action_logs` VALUES (136,'locker',36,'locker_close_locker','locker_opened','locker_occupied',104,'2026-02-17 14:45:47');
INSERT  IGNORE INTO `fsm_action_logs` VALUES (137,'order',1519,'order_assign_courier1_to_order','order_created','order_courier1_assigned',104,'2026-02-17 14:51:17');
INSERT  IGNORE INTO `fsm_action_logs` VALUES (138,'order',1520,'order_assign_courier1_to_order','order_created','order_courier1_assigned',104,'2026-02-17 14:51:27');
INSERT  IGNORE INTO `fsm_action_logs` VALUES (139,'order',1519,'order_courier_pickup_parcel','order_courier1_assigned','order_courier_has_parcel',104,'2026-02-17 14:52:13');
INSERT  IGNORE INTO `fsm_action_logs` VALUES (140,'locker',19,'locker_open_locker','locker_reserved','locker_opened',104,'2026-02-17 14:52:13');
INSERT  IGNORE INTO `fsm_action_logs` VALUES (141,'order',1520,'order_courier_pickup_parcel','order_courier1_assigned','order_courier_has_parcel',104,'2026-02-17 14:52:23');
INSERT  IGNORE INTO `fsm_action_logs` VALUES (142,'locker',20,'locker_open_locker','locker_reserved','locker_opened',104,'2026-02-17 14:52:23');
INSERT  IGNORE INTO `fsm_action_logs` VALUES (143,'order',1519,'order_confirm_parcel_in','order_courier_has_parcel','order_parcel_confirmed',104,'2026-02-17 14:52:43');
INSERT  IGNORE INTO `fsm_action_logs` VALUES (144,'locker',19,'locker_close_locker','locker_opened','locker_occupied',104,'2026-02-17 14:52:43');
INSERT  IGNORE INTO `fsm_action_logs` VALUES (145,'order',1520,'order_confirm_parcel_in','order_courier_has_parcel','order_parcel_confirmed',104,'2026-02-17 14:52:48');
INSERT  IGNORE INTO `fsm_action_logs` VALUES (146,'locker',20,'locker_close_locker','locker_opened','locker_occupied',104,'2026-02-17 14:52:48');
INSERT  IGNORE INTO `fsm_action_logs` VALUES (147,'order',1521,'order_assign_courier1_to_order','order_created','order_courier1_assigned',104,'2026-02-17 15:07:48');
INSERT  IGNORE INTO `fsm_action_logs` VALUES (148,'order',1522,'order_assign_courier1_to_order','order_created','order_courier1_assigned',104,'2026-02-17 15:07:53');
INSERT  IGNORE INTO `fsm_action_logs` VALUES (149,'order',1521,'order_courier_pickup_parcel','order_courier1_assigned','order_courier_has_parcel',104,'2026-02-17 15:08:52');
INSERT  IGNORE INTO `fsm_action_logs` VALUES (150,'locker',39,'locker_open_locker','locker_reserved','locker_opened',104,'2026-02-17 15:08:52');
INSERT  IGNORE INTO `fsm_action_logs` VALUES (151,'order',1522,'order_courier_pickup_parcel','order_courier1_assigned','order_courier_has_parcel',104,'2026-02-17 15:09:02');
INSERT  IGNORE INTO `fsm_action_logs` VALUES (152,'locker',40,'locker_open_locker','locker_reserved','locker_opened',104,'2026-02-17 15:09:02');
INSERT  IGNORE INTO `fsm_action_logs` VALUES (153,'order',1521,'order_confirm_parcel_in','order_courier_has_parcel','order_parcel_confirmed',104,'2026-02-17 15:09:22');
INSERT  IGNORE INTO `fsm_action_logs` VALUES (154,'locker',39,'locker_close_locker','locker_opened','locker_occupied',104,'2026-02-17 15:09:22');
INSERT  IGNORE INTO `fsm_action_logs` VALUES (155,'order',1522,'order_confirm_parcel_in','order_courier_has_parcel','order_parcel_confirmed',104,'2026-02-17 15:09:27');
INSERT  IGNORE INTO `fsm_action_logs` VALUES (156,'locker',40,'locker_close_locker','locker_opened','locker_occupied',104,'2026-02-17 15:09:27');
INSERT  IGNORE INTO `fsm_action_logs` VALUES (157,'order',1523,'order_assign_courier1_to_order','order_created','order_courier1_assigned',104,'2026-02-17 15:13:11');
INSERT  IGNORE INTO `fsm_action_logs` VALUES (158,'order',1523,'order_courier_pickup_parcel','order_courier1_assigned','order_courier_has_parcel',104,'2026-02-17 15:13:41');
INSERT  IGNORE INTO `fsm_action_logs` VALUES (159,'locker',34,'locker_open_locker','locker_reserved','locker_opened',104,'2026-02-17 15:13:41');
INSERT  IGNORE INTO `fsm_action_logs` VALUES (160,'order',1523,'order_confirm_parcel_in','order_courier_has_parcel','order_parcel_confirmed',104,'2026-02-17 15:13:51');
INSERT  IGNORE INTO `fsm_action_logs` VALUES (161,'locker',34,'locker_close_locker','locker_opened','locker_occupied',104,'2026-02-17 15:13:51');
INSERT  IGNORE INTO `fsm_action_logs` VALUES (162,'trip',34,'trip_vzyat_reis','trip_created','trip_assigned',200,'2026-02-17 15:24:01');
INSERT  IGNORE INTO `fsm_action_logs` VALUES (163,'order',1524,'order_assign_courier1_to_order','order_created','order_courier1_assigned',104,'2026-02-17 18:07:08');
INSERT  IGNORE INTO `fsm_action_logs` VALUES (164,'order',1524,'order_courier_pickup_parcel','order_courier1_assigned','order_courier_has_parcel',104,'2026-02-17 18:07:58');
INSERT  IGNORE INTO `fsm_action_logs` VALUES (165,'locker',37,'locker_open_locker','locker_reserved','locker_opened',104,'2026-02-17 18:07:58');
INSERT  IGNORE INTO `fsm_action_logs` VALUES (166,'order',1524,'order_confirm_parcel_in','order_courier_has_parcel','order_parcel_confirmed',104,'2026-02-17 18:08:13');
INSERT  IGNORE INTO `fsm_action_logs` VALUES (167,'locker',37,'locker_close_locker','locker_opened','locker_occupied',104,'2026-02-17 18:08:13');
INSERT  IGNORE INTO `fsm_action_logs` VALUES (168,'locker',36,'locker_open_locker','locker_occupied','locker_opened',200,'2026-02-17 18:36:16');
INSERT  IGNORE INTO `fsm_action_logs` VALUES (687,'locker',33,'locker_open_locker','locker_occupied','locker_opened',200,'2026-02-17 20:19:14');
INSERT  IGNORE INTO `fsm_action_logs` VALUES (688,'order',1517,'order_parcel_submitted','order_parcel_confirmed','order_parcel_submitted',200,'2026-02-17 20:19:14');
INSERT  IGNORE INTO `fsm_action_logs` VALUES (976,'locker',39,'locker_open_locker','locker_occupied','locker_opened',200,'2026-02-18 10:01:50');
INSERT  IGNORE INTO `fsm_action_logs` VALUES (977,'locker',39,'locker_open_locker','locker_occupied','locker_opened',200,'2026-02-18 10:03:26');
INSERT  IGNORE INTO `fsm_action_logs` VALUES (978,'locker',39,'locker_open_locker','locker_occupied','locker_opened',200,'2026-02-18 10:15:51');
INSERT  IGNORE INTO `fsm_action_logs` VALUES (979,'locker',39,'locker_open_locker','locker_occupied','locker_opened',200,'2026-02-18 10:37:19');
INSERT  IGNORE INTO `fsm_action_logs` VALUES (980,'locker',39,'locker_open_locker','locker_occupied','locker_opened',200,'2026-02-18 12:38:25');
INSERT  IGNORE INTO `fsm_action_logs` VALUES (981,'locker',39,'locker_open_locker','locker_occupied','locker_opened',200,'2026-02-18 14:04:07');
INSERT  IGNORE INTO `fsm_action_logs` VALUES (982,'order',1521,'order_parcel_submitted','order_parcel_confirmed','order_parcel_submitted',200,'2026-02-18 14:04:07');
INSERT  IGNORE INTO `fsm_action_logs` VALUES (983,'locker',39,'locker_open_locker','locker_occupied','locker_opened',200,'2026-02-18 14:47:23');
INSERT  IGNORE INTO `fsm_action_logs` VALUES (987,'locker',39,'locker_open_locker','locker_occupied','locker_opened',200,'2026-02-18 15:15:22');
INSERT  IGNORE INTO `fsm_action_logs` VALUES (988,'order',1521,'order_parcel_submitted','order_parcel_confirmed','order_parcel_submitted',200,'2026-02-18 15:15:22');
INSERT  IGNORE INTO `fsm_action_logs` VALUES (989,'trip',34,'trip_assign_voditel','trip_assigned','trip_ready_for_pickup',200,'2026-02-18 15:15:22');
INSERT  IGNORE INTO `fsm_action_logs` VALUES (996,'locker',39,'locker_close_pickup','locker_opened','locker_closed_empty',200,'2026-02-18 16:03:09');
INSERT  IGNORE INTO `fsm_action_logs` VALUES (997,'order',1521,'order_pickup_by_voditel','order_parcel_submitted','order_picked_up_from_post1',200,'2026-02-18 16:03:09');
INSERT  IGNORE INTO `fsm_action_logs` VALUES (998,'trip',34,'trip_confirm_pickup','trip_ready_for_pickup','trip_parcel_picked_up',200,'2026-02-18 16:03:09');
INSERT  IGNORE INTO `fsm_action_logs` VALUES (1002,'locker',33,'locker_close_pickup','locker_opened','locker_closed_empty',200,'2026-02-20 14:16:03');
INSERT  IGNORE INTO `fsm_action_logs` VALUES (1003,'order',1517,'order_pickup_by_voditel','order_parcel_submitted','order_picked_up_from_post1',200,'2026-02-20 14:16:03');
INSERT  IGNORE INTO `fsm_action_logs` VALUES (1004,'locker',36,'locker_open_locker','locker_occupied','locker_opened',200,'2026-02-20 14:20:53');
INSERT  IGNORE INTO `fsm_action_logs` VALUES (1005,'order',1518,'order_parcel_submitted','order_parcel_confirmed','order_parcel_submitted',200,'2026-02-20 14:20:53');
INSERT  IGNORE INTO `fsm_action_logs` VALUES (1006,'locker',40,'locker_open_locker','locker_occupied','locker_opened',200,'2026-02-20 14:23:29');
INSERT  IGNORE INTO `fsm_action_logs` VALUES (1007,'order',1522,'order_parcel_submitted','order_parcel_confirmed','order_parcel_submitted',200,'2026-02-20 14:23:29');
INSERT  IGNORE INTO `fsm_action_logs` VALUES (1008,'locker',34,'locker_open_locker','locker_occupied','locker_opened',200,'2026-02-20 14:23:44');
INSERT  IGNORE INTO `fsm_action_logs` VALUES (1009,'order',1523,'order_parcel_submitted','order_parcel_confirmed','order_parcel_submitted',200,'2026-02-20 14:23:44');
INSERT  IGNORE INTO `fsm_action_logs` VALUES (1010,'locker',36,'locker_close_pickup','locker_opened','locker_closed_empty',200,'2026-02-20 14:24:04');
INSERT  IGNORE INTO `fsm_action_logs` VALUES (1011,'order',1518,'order_pickup_by_voditel','order_parcel_submitted','order_picked_up_from_post1',200,'2026-02-20 14:24:04');
INSERT  IGNORE INTO `fsm_action_logs` VALUES (1012,'locker',34,'locker_close_pickup','locker_opened','locker_closed_empty',200,'2026-02-20 14:24:14');
INSERT  IGNORE INTO `fsm_action_logs` VALUES (1013,'order',1523,'order_pickup_by_voditel','order_parcel_submitted','order_picked_up_from_post1',200,'2026-02-20 14:24:14');
INSERT  IGNORE INTO `fsm_action_logs` VALUES (1014,'locker',40,'locker_close_pickup','locker_opened','locker_closed_empty',200,'2026-02-20 14:24:19');
INSERT  IGNORE INTO `fsm_action_logs` VALUES (1015,'order',1522,'order_pickup_by_voditel','order_parcel_submitted','order_picked_up_from_post1',200,'2026-02-20 14:24:19');
INSERT  IGNORE INTO `fsm_action_logs` VALUES (1016,'trip',34,'trip_start_trip','trip_assigned','trip_in_progress',200,'2026-02-20 14:51:32');
INSERT  IGNORE INTO `fsm_action_logs` VALUES (1017,'order',1517,'order_start_transit','order_picked_up_from_post1','order_in_transit_to_post2',200,'2026-02-20 14:51:32');
INSERT  IGNORE INTO `fsm_action_logs` VALUES (1018,'order',1518,'order_start_transit','order_picked_up_from_post1','order_in_transit_to_post2',200,'2026-02-20 14:51:32');
INSERT  IGNORE INTO `fsm_action_logs` VALUES (1019,'order',1521,'order_start_transit','order_picked_up_from_post1','order_in_transit_to_post2',200,'2026-02-20 14:51:32');
INSERT  IGNORE INTO `fsm_action_logs` VALUES (1020,'order',1522,'order_start_transit','order_picked_up_from_post1','order_in_transit_to_post2',200,'2026-02-20 14:51:32');
INSERT  IGNORE INTO `fsm_action_logs` VALUES (1021,'order',1523,'order_start_transit','order_picked_up_from_post1','order_in_transit_to_post2',200,'2026-02-20 14:51:32');
INSERT  IGNORE INTO `fsm_action_logs` VALUES (1022,'locker',18,'locker_failed_to_open','locker_occupied','locker_error',200,'2026-02-24 14:40:52');
INSERT  IGNORE INTO `fsm_action_logs` VALUES (1023,'order',1516,'order_request_manual_intervention','order_parcel_confirmed','order_manual_intervention_required',200,'2026-02-24 14:40:52');
INSERT  IGNORE INTO `fsm_action_logs` VALUES (1025,'trip',34,'trip_report_failure','trip_in_progress','trip_failed',200,'2026-02-24 16:16:13');

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
) ENGINE=InnoDB AUTO_INCREMENT=108 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
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
INSERT  IGNORE INTO `fsm_actions` VALUES (80,'trip_end_delivery','zavershit_dostavku');
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
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `fsm_errors_log`
--


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
) ENGINE=InnoDB AUTO_INCREMENT=104 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
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
) ENGINE=InnoDB AUTO_INCREMENT=135 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
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
INSERT  IGNORE INTO `fsm_transitions` VALUES (60,4,80,5);
INSERT  IGNORE INTO `fsm_transitions` VALUES (61,73,6,69);
INSERT  IGNORE INTO `fsm_transitions` VALUES (62,69,5,7);
INSERT  IGNORE INTO `fsm_transitions` VALUES (63,79,76,68);
INSERT  IGNORE INTO `fsm_transitions` VALUES (64,1,81,84);
INSERT  IGNORE INTO `fsm_transitions` VALUES (65,1,82,85);
INSERT  IGNORE INTO `fsm_transitions` VALUES (66,84,69,60);
INSERT  IGNORE INTO `fsm_transitions` VALUES (68,84,7,76);
INSERT  IGNORE INTO `fsm_transitions` VALUES (69,85,7,76);
INSERT  IGNORE INTO `fsm_transitions` VALUES (71,84,74,78);
INSERT  IGNORE INTO `fsm_transitions` VALUES (72,85,74,78);
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

INSERT  IGNORE INTO `locker_cells` VALUES (1,1,'S-01','S','locker_reserved',NULL,'2025-11-22 15:23:13','2026-02-14 13:39:19');
INSERT  IGNORE INTO `locker_cells` VALUES (2,1,'S-02','S','locker_reserved',NULL,'2025-11-22 15:23:13','2026-02-06 05:53:12');
INSERT  IGNORE INTO `locker_cells` VALUES (3,1,'S-03','S','locker_reserved',NULL,'2025-11-22 15:23:13','2026-02-06 05:53:32');
INSERT  IGNORE INTO `locker_cells` VALUES (4,1,'S-04','S','locker_reserved',NULL,'2025-11-22 15:23:13','2026-02-10 17:07:30');
INSERT  IGNORE INTO `locker_cells` VALUES (5,1,'M-01','M','locker_reserved',NULL,'2025-11-22 15:23:13','2026-02-14 14:13:47');
INSERT  IGNORE INTO `locker_cells` VALUES (6,1,'M-02','M','locker_reserved',NULL,'2025-11-22 15:23:13','2026-02-08 13:22:43');
INSERT  IGNORE INTO `locker_cells` VALUES (7,1,'L-01','L','locker_reserved',NULL,'2025-11-22 15:23:13','2026-02-17 09:39:07');
INSERT  IGNORE INTO `locker_cells` VALUES (8,1,'L-02','L','locker_reserved',NULL,'2025-11-22 15:23:13','2026-02-17 14:24:51');
INSERT  IGNORE INTO `locker_cells` VALUES (9,1,'P-01','P','locker_reserved',NULL,'2025-11-22 15:23:13','2026-02-17 14:50:52');
INSERT  IGNORE INTO `locker_cells` VALUES (10,1,'P-02','P','locker_reserved',NULL,'2025-11-22 15:23:13','2026-02-17 14:51:07');
INSERT  IGNORE INTO `locker_cells` VALUES (11,2,'S-01','S','locker_reserved',1449,'2025-11-22 15:23:13','2026-02-14 13:39:19');
INSERT  IGNORE INTO `locker_cells` VALUES (12,2,'S-02','S','locker_reserved',NULL,'2025-11-22 15:23:13','2026-02-14 13:41:06');
INSERT  IGNORE INTO `locker_cells` VALUES (13,2,'S-03','S','locker_reserved',NULL,'2025-11-22 15:23:13','2026-02-06 05:53:12');
INSERT  IGNORE INTO `locker_cells` VALUES (14,2,'S-04','S','locker_reserved',NULL,'2025-11-22 15:23:13','2026-02-06 05:53:32');
INSERT  IGNORE INTO `locker_cells` VALUES (15,2,'M-01','M','locker_occupied',NULL,'2025-11-22 15:23:13','2026-02-16 09:00:24');
INSERT  IGNORE INTO `locker_cells` VALUES (16,2,'M-02','M','locker_reserved',NULL,'2025-11-22 15:23:13','2026-02-08 13:22:43');
INSERT  IGNORE INTO `locker_cells` VALUES (17,2,'L-01','L','locker_occupied',NULL,'2025-11-22 15:23:13','2026-02-17 09:47:28');
INSERT  IGNORE INTO `locker_cells` VALUES (18,2,'L-02','L','locker_error',NULL,'2025-11-22 15:23:13','2026-02-24 14:40:52');
INSERT  IGNORE INTO `locker_cells` VALUES (19,2,'P-01','P','locker_occupied',NULL,'2025-11-22 15:23:13','2026-02-17 14:52:43');
INSERT  IGNORE INTO `locker_cells` VALUES (20,2,'P-02','P','locker_occupied',NULL,'2025-11-22 15:23:13','2026-02-17 14:52:48');
INSERT  IGNORE INTO `locker_cells` VALUES (21,3,'S-01','S','locker_reserved',NULL,'2025-11-22 15:23:13','2026-02-16 11:35:02');
INSERT  IGNORE INTO `locker_cells` VALUES (22,3,'S-02','S','locker_reserved',1517,'2025-11-22 15:23:13','2026-02-17 18:31:24');
INSERT  IGNORE INTO `locker_cells` VALUES (23,3,'S-03','S','locker_reserved',1523,'2025-11-22 15:23:13','2026-02-17 18:31:24');
INSERT  IGNORE INTO `locker_cells` VALUES (24,3,'S-04','S','locker_free',NULL,'2025-11-22 15:23:13','2025-11-22 15:23:13');
INSERT  IGNORE INTO `locker_cells` VALUES (25,3,'M-01','M','locker_reserved',NULL,'2025-11-22 15:23:13','2026-02-10 15:14:05');
INSERT  IGNORE INTO `locker_cells` VALUES (26,3,'M-02','M','locker_reserved',1518,'2025-11-22 15:23:13','2026-02-17 18:31:24');
INSERT  IGNORE INTO `locker_cells` VALUES (27,3,'L-01','L','locker_reserved',NULL,'2025-11-22 15:23:13','2026-02-17 18:05:53');
INSERT  IGNORE INTO `locker_cells` VALUES (28,3,'L-02','L','locker_free',NULL,'2025-11-22 15:23:13','2025-11-22 15:23:13');
INSERT  IGNORE INTO `locker_cells` VALUES (29,3,'P-01','P','locker_reserved',1521,'2025-11-22 15:23:13','2026-02-17 18:31:24');
INSERT  IGNORE INTO `locker_cells` VALUES (30,3,'P-02','P','locker_reserved',1522,'2025-11-22 15:23:13','2026-02-17 18:31:24');
INSERT  IGNORE INTO `locker_cells` VALUES (31,4,'S-01','S','locker_reserved',NULL,'2025-11-22 15:23:13','2026-02-10 17:07:30');
INSERT  IGNORE INTO `locker_cells` VALUES (32,4,'S-02','S','locker_reserved',NULL,'2025-11-22 15:23:13','2026-02-16 11:35:02');
INSERT  IGNORE INTO `locker_cells` VALUES (33,4,'S-03','S','locker_closed_empty',1517,'2025-11-22 15:23:13','2026-02-20 14:16:03');
INSERT  IGNORE INTO `locker_cells` VALUES (34,4,'S-04','S','locker_closed_empty',1523,'2025-11-22 15:23:13','2026-02-20 14:50:07');
INSERT  IGNORE INTO `locker_cells` VALUES (35,4,'M-01','M','locker_reserved',NULL,'2025-11-22 15:23:13','2026-02-10 15:14:05');
INSERT  IGNORE INTO `locker_cells` VALUES (36,4,'M-02','M','locker_closed_empty',1518,'2025-11-22 15:23:13','2026-02-20 14:24:04');
INSERT  IGNORE INTO `locker_cells` VALUES (37,4,'L-01','L','locker_occupied',NULL,'2025-11-22 15:23:13','2026-02-17 18:08:13');
INSERT  IGNORE INTO `locker_cells` VALUES (38,4,'L-02','L','locker_free',NULL,'2025-11-22 15:23:13','2025-11-22 15:23:13');
INSERT  IGNORE INTO `locker_cells` VALUES (39,4,'P-01','P','locker_closed_empty',1521,'2025-11-22 15:23:13','2026-02-18 16:03:09');
INSERT  IGNORE INTO `locker_cells` VALUES (40,4,'P-02','P','locker_closed_empty',1522,'2025-11-22 15:23:13','2026-02-20 14:24:19');
INSERT  IGNORE INTO `locker_cells` VALUES (41,1,'A01','S','locker_reserved',1448,'2025-11-23 20:39:10','2026-01-29 08:12:40');
INSERT  IGNORE INTO `locker_cells` VALUES (42,1,'A02','S','locker_reserved',1449,'2025-11-23 20:39:10','2026-02-14 13:41:06');
INSERT  IGNORE INTO `locker_cells` VALUES (43,1,'A03','M','locker_reserved',1446,'2025-11-23 20:39:10','2026-02-05 07:58:29');
INSERT  IGNORE INTO `locker_cells` VALUES (44,2,'B01','S','locker_reserved',1448,'2025-11-23 20:39:10','2026-01-29 08:12:40');
INSERT  IGNORE INTO `locker_cells` VALUES (45,2,'B02','M','locker_reserved',1446,'2025-11-23 20:39:10','2026-02-05 07:58:29');
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

INSERT  IGNORE INTO `lockers` VALUES (1,1,'POST1','МСК','Точка #1',NULL,NULL,'locker_inactive','2025-11-22 15:22:48');
INSERT  IGNORE INTO `lockers` VALUES (2,1,'POST2','СПБ','Точка #2',NULL,NULL,'locker_inactive','2025-11-22 15:22:48');
INSERT  IGNORE INTO `lockers` VALUES (3,1,'POST3','МСК','Точка #3',NULL,NULL,'locker_inactive','2025-11-22 15:22:48');
INSERT  IGNORE INTO `lockers` VALUES (4,1,'POST4','СПБ','Точка #4',NULL,NULL,'locker_inactive','2025-11-22 15:22:48');

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
) ENGINE=InnoDB AUTO_INCREMENT=238 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
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
) ENGINE=InnoDB AUTO_INCREMENT=1525 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `orders`
--

INSERT  IGNORE INTO `orders` VALUES (1,'order_courier_failed','Timeout Order','courier',NULL,'courier',2,12,'2025-12-16 09:46:53','2025-11-24 16:33:51',0,NULL);
INSERT  IGNORE INTO `orders` VALUES (2,'order_reservation_expired','Trip Order 1','courier',NULL,'courier',3,13,'2025-11-24 16:36:07','2025-11-24 16:33:51',0,NULL);
INSERT  IGNORE INTO `orders` VALUES (3,'order_reservation_expired','Trip Order 2','courier',NULL,'courier',4,14,'2025-11-24 16:36:08','2025-11-24 16:33:51',0,NULL);
INSERT  IGNORE INTO `orders` VALUES (4,'order_reservation_expired','Trip Order 3','courier',NULL,'courier',5,15,'2025-11-24 16:36:08','2025-11-24 16:33:52',0,NULL);
INSERT  IGNORE INTO `orders` VALUES (5,'order_created','Order','courier',NULL,'courier',2,5,'2026-01-17 09:22:39','2025-11-26 16:25:34',0,NULL);
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
INSERT  IGNORE INTO `orders` VALUES (1363,'order_created','Заказ A (S)','courier',NULL,'courier',1,12,'2025-12-15 19:42:02','2025-12-15 19:42:02',0,NULL);
INSERT  IGNORE INTO `orders` VALUES (1364,'order_created','Заказ 1 (S)','courier','Заказ 1','courier',41,44,'2025-12-25 10:42:59','2025-12-15 19:57:16',0,NULL);
INSERT  IGNORE INTO `orders` VALUES (1365,'order_created','Заказ 2 (S)','courier','Заказ 2','courier',42,11,'2025-12-25 10:42:59','2025-12-15 19:57:16',0,NULL);
INSERT  IGNORE INTO `orders` VALUES (1366,'order_created','Тест А (S)','courier','Тест А','courier',41,44,'2025-12-25 10:42:59','2025-12-15 20:33:36',0,NULL);
INSERT  IGNORE INTO `orders` VALUES (1367,'order_created','Тест Б (S)','courier','Тест Б','courier',42,11,'2025-12-25 10:42:59','2025-12-15 20:33:36',0,NULL);
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
INSERT  IGNORE INTO `orders` VALUES (1502,'order_courier1_assigned','parcel (M)','self',NULL,'courier',43,45,'2026-02-05 09:11:47','2026-02-05 07:58:29',1004,NULL);
INSERT  IGNORE INTO `orders` VALUES (1503,'order_cancelled','parcel (S)','courier',NULL,'courier',1,12,'2026-02-05 08:25:26','2026-02-05 08:00:39',1004,NULL);
INSERT  IGNORE INTO `orders` VALUES (1504,'order_created','parsel (M)','self',NULL,'self',5,15,'2026-02-05 09:06:17','2026-02-05 09:06:17',1005,NULL);
INSERT  IGNORE INTO `orders` VALUES (1505,'order_created','parcel (S)','courier',NULL,'courier',1,12,'2026-02-06 05:52:52','2026-02-06 05:52:52',1003,NULL);
INSERT  IGNORE INTO `orders` VALUES (1506,'order_created','parcel (S)','courier',NULL,'courier',2,13,'2026-02-06 05:53:12','2026-02-06 05:53:12',1003,NULL);
INSERT  IGNORE INTO `orders` VALUES (1507,'order_courier1_assigned','parcel (S)','courier',NULL,'courier',3,14,'2026-02-13 13:21:22','2026-02-06 05:53:32',1003,NULL);
INSERT  IGNORE INTO `orders` VALUES (1508,'order_courier1_assigned','parcel (M)','courier',NULL,'courier',16,6,'2026-02-13 13:21:52','2026-02-08 13:22:43',1004,NULL);
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
INSERT  IGNORE INTO `orders` VALUES (1519,'order_parcel_confirmed','parcel (P)','courier',NULL,'courier',19,9,'2026-02-17 14:52:43','2026-02-17 14:50:52',1004,2002);
INSERT  IGNORE INTO `orders` VALUES (1520,'order_parcel_confirmed','parcel (P)','courier',NULL,'courier',20,10,'2026-02-17 14:52:48','2026-02-17 14:51:07',1004,2002);
INSERT  IGNORE INTO `orders` VALUES (1521,'order_in_transit_to_post2','parcel (P)','courier',NULL,'courier',39,29,'2026-02-20 14:51:32','2026-02-17 15:07:33',1004,2002);
INSERT  IGNORE INTO `orders` VALUES (1522,'order_in_transit_to_post2','parcel (P)','courier',NULL,'courier',40,30,'2026-02-20 14:51:32','2026-02-17 15:07:33',1004,2002);
INSERT  IGNORE INTO `orders` VALUES (1523,'order_in_transit_to_post2','parcel (S)','courier',NULL,'courier',34,23,'2026-02-20 14:51:32','2026-02-17 15:12:56',1004,2002);
INSERT  IGNORE INTO `orders` VALUES (1524,'order_parcel_confirmed','parcel (L)','courier',NULL,'courier',37,27,'2026-02-17 18:08:13','2026-02-17 18:05:53',1004,2002);
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
) ENGINE=InnoDB AUTO_INCREMENT=4 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `report_issues`
--

INSERT  IGNORE INTO `report_issues` VALUES (1,1516,33,200,NULL,'locker_failed_to_open','Driver reported: locker_failed_to_open','2026-02-24 14:40:52');
INSERT  IGNORE INTO `report_issues` VALUES (3,NULL,34,200,NULL,'trip_breakdown','Driver reported: trip_breakdown','2026-02-24 16:16:13');

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
) ENGINE=InnoDB AUTO_INCREMENT=547 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
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
INSERT  IGNORE INTO `server_fsm_instances` VALUES (148,'order',201,'open_cell','FAILED',NULL,1,'ROLE_NOT_SUPPORTED_driver','2025-12-29 18:37:11','2025-12-31 09:47:42',200,'driver',NULL,NULL,NULL);
INSERT  IGNORE INTO `server_fsm_instances` VALUES (149,'order',203,'open_cell','FAILED',NULL,1,'ROLE_NOT_SUPPORTED_driver','2025-12-29 18:37:27','2025-12-31 09:47:42',200,'driver',NULL,NULL,NULL);
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
INSERT  IGNORE INTO `server_fsm_instances` VALUES (183,'order',202,'open_cell','FAILED',NULL,1,'ROLE_NOT_SUPPORTED_driver','2025-12-30 17:54:22','2025-12-31 09:47:43',200,'driver',NULL,NULL,NULL);
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
INSERT  IGNORE INTO `server_fsm_instances` VALUES (299,'order',5,'order_assign_courier1','FAILED',NULL,1,'ASSIGNMENT_FAILED','2026-01-15 10:16:12','2026-01-17 09:19:49',100,'courier',100,NULL,NULL);
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
INSERT  IGNORE INTO `server_fsm_instances` VALUES (410,'order',1508,'request_locker_access_code','FAILED',NULL,1,'USER_NOT_AUTHORIZED','2026-02-11 17:44:14','2026-02-11 18:00:32',1004,'client',NULL,NULL,'{\"leg\": \"pickup\"}');
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
INSERT  IGNORE INTO `server_fsm_instances` VALUES (432,'order',1513,'open_cell','COMPLETED',NULL,1,NULL,'2026-02-16 08:59:37','2026-02-16 08:59:39',103,'courier',103,'courier','{}');
INSERT  IGNORE INTO `server_fsm_instances` VALUES (433,'order',1513,'close_cell','COMPLETED',NULL,1,NULL,'2026-02-16 09:00:23','2026-02-16 09:00:24',103,'courier',103,'courier','{}');
INSERT  IGNORE INTO `server_fsm_instances` VALUES (434,'order',1513,'bind_order_to_trip_after_confirmation','FAILED',NULL,1,'UNKNOWN_PROCESS: bind_order_to_trip_after_confirmation','2026-02-16 09:00:24','2026-02-16 09:00:24',0,'system',NULL,NULL,NULL);
INSERT  IGNORE INTO `server_fsm_instances` VALUES (435,'order',1513,'bind_order_to_trip','COMPLETED',NULL,1,NULL,'2026-02-16 09:43:35','2026-02-16 11:02:31',999999,'system',999999,'system','{}');
INSERT  IGNORE INTO `server_fsm_instances` VALUES (440,'order_request',219,'order_creation','COMPLETED',NULL,1,NULL,'2026-02-16 11:35:01','2026-02-16 11:35:02',NULL,NULL,NULL,NULL,NULL);
INSERT  IGNORE INTO `server_fsm_instances` VALUES (441,'order_request',220,'order_creation','COMPLETED',NULL,1,NULL,'2026-02-17 09:33:02','2026-02-17 09:39:07',NULL,NULL,NULL,NULL,NULL);
INSERT  IGNORE INTO `server_fsm_instances` VALUES (442,'order',1515,'order_assign_courier1','COMPLETED',NULL,1,NULL,'2026-02-17 09:42:51','2026-02-17 09:42:53',103,'courier',103,NULL,NULL);
INSERT  IGNORE INTO `server_fsm_instances` VALUES (443,'order',1515,'open_cell','COMPLETED',NULL,1,NULL,'2026-02-17 09:46:35','2026-02-17 09:46:38',103,'courier',103,'courier','{}');
INSERT  IGNORE INTO `server_fsm_instances` VALUES (444,'order',1515,'close_cell','COMPLETED',NULL,1,NULL,'2026-02-17 09:47:27','2026-02-17 09:47:28',103,'courier',103,'courier','{}');
INSERT  IGNORE INTO `server_fsm_instances` VALUES (445,'order',1515,'bind_order_to_trip','COMPLETED',NULL,1,NULL,'2026-02-17 09:47:28','2026-02-17 09:47:28',999999,'system',NULL,NULL,NULL);
INSERT  IGNORE INTO `server_fsm_instances` VALUES (446,'trip',29,'trip_assign_driver','COMPLETED',NULL,1,NULL,'2026-02-17 09:59:48','2026-02-17 10:34:56',200,'driver',200,'driver','{}');
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
INSERT  IGNORE INTO `server_fsm_instances` VALUES (490,'trip',34,'trip_assign_driver','COMPLETED',NULL,1,NULL,'2026-02-17 15:24:01','2026-02-17 15:24:01',200,'driver',200,'driver','{}');
INSERT  IGNORE INTO `server_fsm_instances` VALUES (492,'locker',36,'open_cell','COMPLETED',NULL,1,NULL,'2026-02-17 16:05:25','2026-02-20 14:20:53',200,'driver',200,'driver','{}');
INSERT  IGNORE INTO `server_fsm_instances` VALUES (496,'order_request',231,'order_creation','FAILED',NULL,1,'NO_FREE_CELLS','2026-02-17 18:04:21','2026-02-17 18:04:23',NULL,NULL,NULL,NULL,NULL);
INSERT  IGNORE INTO `server_fsm_instances` VALUES (497,'order_request',232,'order_creation','FAILED',NULL,1,'NO_FREE_CELLS','2026-02-17 18:04:49','2026-02-17 18:04:53',NULL,NULL,NULL,NULL,NULL);
INSERT  IGNORE INTO `server_fsm_instances` VALUES (498,'order_request',233,'order_creation','COMPLETED',NULL,1,NULL,'2026-02-17 18:05:53','2026-02-17 18:05:53',NULL,NULL,NULL,NULL,NULL);
INSERT  IGNORE INTO `server_fsm_instances` VALUES (499,'order',1524,'order_assign_courier1','COMPLETED',NULL,1,NULL,'2026-02-17 18:07:08','2026-02-17 18:07:08',104,'courier',104,NULL,NULL);
INSERT  IGNORE INTO `server_fsm_instances` VALUES (500,'order',1524,'open_cell','COMPLETED',NULL,1,NULL,'2026-02-17 18:07:55','2026-02-17 18:07:58',104,'courier',104,'courier','{}');
INSERT  IGNORE INTO `server_fsm_instances` VALUES (501,'order',1524,'close_cell','COMPLETED',NULL,1,NULL,'2026-02-17 18:08:11','2026-02-17 18:08:13',104,'courier',104,'courier','{}');
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

--
-- Table structure for table `stage_orders`
--

DROP TABLE IF EXISTS `stage_orders`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `stage_orders` (
  `trip_id` int DEFAULT NULL,
  `order_id` int NOT NULL,
  `leg` enum('pickup','delivery') NOT NULL DEFAULT 'pickup',
  `courier_user_id` int DEFAULT NULL,
  PRIMARY KEY (`order_id`,`leg`),
  KEY `order_id` (`order_id`),
  KEY `stage_orders_ibfk_courier` (`courier_user_id`),
  CONSTRAINT `stage_orders_ibfk_2` FOREIGN KEY (`order_id`) REFERENCES `orders` (`id`) ON DELETE CASCADE,
  CONSTRAINT `stage_orders_ibfk_courier` FOREIGN KEY (`courier_user_id`) REFERENCES `users` (`id`) ON DELETE SET NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `stage_orders`
--

INSERT  IGNORE INTO `stage_orders` VALUES (1,1,'pickup',2);
INSERT  IGNORE INTO `stage_orders` VALUES (1,2,'pickup',NULL);
INSERT  IGNORE INTO `stage_orders` VALUES (1,3,'pickup',NULL);
INSERT  IGNORE INTO `stage_orders` VALUES (1,4,'pickup',NULL);
INSERT  IGNORE INTO `stage_orders` VALUES (1,5,'pickup',NULL);
INSERT  IGNORE INTO `stage_orders` VALUES (1,5,'delivery',303);
INSERT  IGNORE INTO `stage_orders` VALUES (2,1361,'pickup',2);
INSERT  IGNORE INTO `stage_orders` VALUES (2,1361,'delivery',NULL);
INSERT  IGNORE INTO `stage_orders` VALUES (3,1362,'pickup',2);
INSERT  IGNORE INTO `stage_orders` VALUES (3,1362,'delivery',NULL);
INSERT  IGNORE INTO `stage_orders` VALUES (2,1363,'pickup',NULL);
INSERT  IGNORE INTO `stage_orders` VALUES (2,1364,'pickup',NULL);
INSERT  IGNORE INTO `stage_orders` VALUES (2,1364,'delivery',NULL);
INSERT  IGNORE INTO `stage_orders` VALUES (2,1365,'pickup',NULL);
INSERT  IGNORE INTO `stage_orders` VALUES (2,1365,'delivery',NULL);
INSERT  IGNORE INTO `stage_orders` VALUES (3,1366,'pickup',NULL);
INSERT  IGNORE INTO `stage_orders` VALUES (3,1366,'delivery',NULL);
INSERT  IGNORE INTO `stage_orders` VALUES (3,1367,'pickup',NULL);
INSERT  IGNORE INTO `stage_orders` VALUES (3,1367,'delivery',NULL);
INSERT  IGNORE INTO `stage_orders` VALUES (4,1368,'pickup',NULL);
INSERT  IGNORE INTO `stage_orders` VALUES (4,1368,'delivery',NULL);
INSERT  IGNORE INTO `stage_orders` VALUES (2,1369,'pickup',NULL);
INSERT  IGNORE INTO `stage_orders` VALUES (2,1369,'delivery',NULL);
INSERT  IGNORE INTO `stage_orders` VALUES (3,1370,'pickup',NULL);
INSERT  IGNORE INTO `stage_orders` VALUES (3,1370,'delivery',NULL);
INSERT  IGNORE INTO `stage_orders` VALUES (3,1371,'pickup',NULL);
INSERT  IGNORE INTO `stage_orders` VALUES (3,1371,'delivery',NULL);
INSERT  IGNORE INTO `stage_orders` VALUES (4,1372,'pickup',NULL);
INSERT  IGNORE INTO `stage_orders` VALUES (4,1372,'delivery',NULL);
INSERT  IGNORE INTO `stage_orders` VALUES (4,1373,'pickup',2);
INSERT  IGNORE INTO `stage_orders` VALUES (4,1373,'delivery',NULL);
INSERT  IGNORE INTO `stage_orders` VALUES (4,1374,'pickup',NULL);
INSERT  IGNORE INTO `stage_orders` VALUES (4,1374,'delivery',NULL);
INSERT  IGNORE INTO `stage_orders` VALUES (4,1375,'pickup',NULL);
INSERT  IGNORE INTO `stage_orders` VALUES (4,1375,'delivery',NULL);
INSERT  IGNORE INTO `stage_orders` VALUES (5,1376,'pickup',NULL);
INSERT  IGNORE INTO `stage_orders` VALUES (5,1376,'delivery',NULL);
INSERT  IGNORE INTO `stage_orders` VALUES (6,1377,'pickup',NULL);
INSERT  IGNORE INTO `stage_orders` VALUES (6,1377,'delivery',NULL);
INSERT  IGNORE INTO `stage_orders` VALUES (6,1378,'pickup',2);
INSERT  IGNORE INTO `stage_orders` VALUES (6,1378,'delivery',NULL);
INSERT  IGNORE INTO `stage_orders` VALUES (6,1379,'pickup',2);
INSERT  IGNORE INTO `stage_orders` VALUES (6,1379,'delivery',NULL);
INSERT  IGNORE INTO `stage_orders` VALUES (7,1380,'pickup',NULL);
INSERT  IGNORE INTO `stage_orders` VALUES (7,1380,'delivery',NULL);
INSERT  IGNORE INTO `stage_orders` VALUES (7,1381,'pickup',NULL);
INSERT  IGNORE INTO `stage_orders` VALUES (7,1381,'delivery',NULL);
INSERT  IGNORE INTO `stage_orders` VALUES (7,1382,'pickup',NULL);
INSERT  IGNORE INTO `stage_orders` VALUES (7,1382,'delivery',NULL);
INSERT  IGNORE INTO `stage_orders` VALUES (7,1383,'pickup',NULL);
INSERT  IGNORE INTO `stage_orders` VALUES (7,1383,'delivery',NULL);
INSERT  IGNORE INTO `stage_orders` VALUES (7,1384,'pickup',NULL);
INSERT  IGNORE INTO `stage_orders` VALUES (7,1384,'delivery',NULL);
INSERT  IGNORE INTO `stage_orders` VALUES (8,1385,'pickup',NULL);
INSERT  IGNORE INTO `stage_orders` VALUES (8,1385,'delivery',NULL);
INSERT  IGNORE INTO `stage_orders` VALUES (8,1386,'pickup',NULL);
INSERT  IGNORE INTO `stage_orders` VALUES (8,1386,'delivery',NULL);
INSERT  IGNORE INTO `stage_orders` VALUES (8,1387,'pickup',NULL);
INSERT  IGNORE INTO `stage_orders` VALUES (8,1387,'delivery',NULL);
INSERT  IGNORE INTO `stage_orders` VALUES (8,1388,'pickup',NULL);
INSERT  IGNORE INTO `stage_orders` VALUES (8,1388,'delivery',NULL);
INSERT  IGNORE INTO `stage_orders` VALUES (8,1389,'pickup',NULL);
INSERT  IGNORE INTO `stage_orders` VALUES (8,1389,'delivery',NULL);
INSERT  IGNORE INTO `stage_orders` VALUES (9,1390,'pickup',NULL);
INSERT  IGNORE INTO `stage_orders` VALUES (9,1390,'delivery',NULL);
INSERT  IGNORE INTO `stage_orders` VALUES (9,1391,'pickup',NULL);
INSERT  IGNORE INTO `stage_orders` VALUES (9,1391,'delivery',NULL);
INSERT  IGNORE INTO `stage_orders` VALUES (9,1392,'pickup',NULL);
INSERT  IGNORE INTO `stage_orders` VALUES (9,1392,'delivery',NULL);
INSERT  IGNORE INTO `stage_orders` VALUES (9,1393,'pickup',NULL);
INSERT  IGNORE INTO `stage_orders` VALUES (9,1393,'delivery',NULL);
INSERT  IGNORE INTO `stage_orders` VALUES (9,1394,'pickup',NULL);
INSERT  IGNORE INTO `stage_orders` VALUES (9,1394,'delivery',NULL);
INSERT  IGNORE INTO `stage_orders` VALUES (10,1395,'pickup',NULL);
INSERT  IGNORE INTO `stage_orders` VALUES (10,1395,'delivery',NULL);
INSERT  IGNORE INTO `stage_orders` VALUES (10,1396,'pickup',NULL);
INSERT  IGNORE INTO `stage_orders` VALUES (10,1396,'delivery',NULL);
INSERT  IGNORE INTO `stage_orders` VALUES (10,1397,'pickup',NULL);
INSERT  IGNORE INTO `stage_orders` VALUES (10,1397,'delivery',NULL);
INSERT  IGNORE INTO `stage_orders` VALUES (10,1398,'pickup',2);
INSERT  IGNORE INTO `stage_orders` VALUES (10,1398,'delivery',NULL);
INSERT  IGNORE INTO `stage_orders` VALUES (10,1399,'pickup',2);
INSERT  IGNORE INTO `stage_orders` VALUES (10,1399,'delivery',NULL);
INSERT  IGNORE INTO `stage_orders` VALUES (11,1400,'pickup',NULL);
INSERT  IGNORE INTO `stage_orders` VALUES (11,1400,'delivery',NULL);
INSERT  IGNORE INTO `stage_orders` VALUES (11,1401,'pickup',NULL);
INSERT  IGNORE INTO `stage_orders` VALUES (11,1401,'delivery',NULL);
INSERT  IGNORE INTO `stage_orders` VALUES (11,1402,'pickup',NULL);
INSERT  IGNORE INTO `stage_orders` VALUES (11,1402,'delivery',NULL);
INSERT  IGNORE INTO `stage_orders` VALUES (11,1403,'pickup',NULL);
INSERT  IGNORE INTO `stage_orders` VALUES (11,1403,'delivery',NULL);
INSERT  IGNORE INTO `stage_orders` VALUES (12,1404,'pickup',NULL);
INSERT  IGNORE INTO `stage_orders` VALUES (12,1404,'delivery',NULL);
INSERT  IGNORE INTO `stage_orders` VALUES (12,1405,'pickup',NULL);
INSERT  IGNORE INTO `stage_orders` VALUES (12,1405,'delivery',NULL);
INSERT  IGNORE INTO `stage_orders` VALUES (13,1406,'pickup',NULL);
INSERT  IGNORE INTO `stage_orders` VALUES (13,1406,'delivery',NULL);
INSERT  IGNORE INTO `stage_orders` VALUES (13,1407,'pickup',NULL);
INSERT  IGNORE INTO `stage_orders` VALUES (13,1407,'delivery',NULL);
INSERT  IGNORE INTO `stage_orders` VALUES (14,1408,'pickup',NULL);
INSERT  IGNORE INTO `stage_orders` VALUES (14,1408,'delivery',NULL);
INSERT  IGNORE INTO `stage_orders` VALUES (15,1409,'pickup',NULL);
INSERT  IGNORE INTO `stage_orders` VALUES (15,1409,'delivery',NULL);
INSERT  IGNORE INTO `stage_orders` VALUES (15,1410,'pickup',NULL);
INSERT  IGNORE INTO `stage_orders` VALUES (15,1410,'delivery',NULL);
INSERT  IGNORE INTO `stage_orders` VALUES (15,1411,'pickup',NULL);
INSERT  IGNORE INTO `stage_orders` VALUES (15,1411,'delivery',NULL);
INSERT  IGNORE INTO `stage_orders` VALUES (16,1412,'pickup',NULL);
INSERT  IGNORE INTO `stage_orders` VALUES (16,1412,'delivery',NULL);
INSERT  IGNORE INTO `stage_orders` VALUES (17,1413,'pickup',1003);
INSERT  IGNORE INTO `stage_orders` VALUES (17,1413,'delivery',NULL);
INSERT  IGNORE INTO `stage_orders` VALUES (18,1414,'pickup',NULL);
INSERT  IGNORE INTO `stage_orders` VALUES (18,1414,'delivery',NULL);
INSERT  IGNORE INTO `stage_orders` VALUES (18,1415,'pickup',NULL);
INSERT  IGNORE INTO `stage_orders` VALUES (18,1415,'delivery',NULL);
INSERT  IGNORE INTO `stage_orders` VALUES (18,1416,'pickup',NULL);
INSERT  IGNORE INTO `stage_orders` VALUES (18,1416,'delivery',NULL);
INSERT  IGNORE INTO `stage_orders` VALUES (18,1417,'pickup',NULL);
INSERT  IGNORE INTO `stage_orders` VALUES (18,1417,'delivery',NULL);
INSERT  IGNORE INTO `stage_orders` VALUES (18,1418,'pickup',NULL);
INSERT  IGNORE INTO `stage_orders` VALUES (18,1418,'delivery',NULL);
INSERT  IGNORE INTO `stage_orders` VALUES (19,1419,'pickup',NULL);
INSERT  IGNORE INTO `stage_orders` VALUES (19,1419,'delivery',NULL);
INSERT  IGNORE INTO `stage_orders` VALUES (19,1420,'pickup',NULL);
INSERT  IGNORE INTO `stage_orders` VALUES (19,1420,'delivery',NULL);
INSERT  IGNORE INTO `stage_orders` VALUES (19,1421,'pickup',NULL);
INSERT  IGNORE INTO `stage_orders` VALUES (19,1421,'delivery',NULL);
INSERT  IGNORE INTO `stage_orders` VALUES (19,1422,'pickup',NULL);
INSERT  IGNORE INTO `stage_orders` VALUES (19,1422,'delivery',NULL);
INSERT  IGNORE INTO `stage_orders` VALUES (20,1423,'pickup',NULL);
INSERT  IGNORE INTO `stage_orders` VALUES (20,1423,'delivery',NULL);
INSERT  IGNORE INTO `stage_orders` VALUES (20,1424,'pickup',NULL);
INSERT  IGNORE INTO `stage_orders` VALUES (20,1424,'delivery',NULL);
INSERT  IGNORE INTO `stage_orders` VALUES (20,1425,'pickup',NULL);
INSERT  IGNORE INTO `stage_orders` VALUES (20,1425,'delivery',NULL);
INSERT  IGNORE INTO `stage_orders` VALUES (20,1426,'pickup',NULL);
INSERT  IGNORE INTO `stage_orders` VALUES (20,1426,'delivery',NULL);
INSERT  IGNORE INTO `stage_orders` VALUES (20,1427,'pickup',NULL);
INSERT  IGNORE INTO `stage_orders` VALUES (20,1427,'delivery',NULL);
INSERT  IGNORE INTO `stage_orders` VALUES (21,1428,'pickup',NULL);
INSERT  IGNORE INTO `stage_orders` VALUES (21,1428,'delivery',NULL);
INSERT  IGNORE INTO `stage_orders` VALUES (21,1429,'pickup',NULL);
INSERT  IGNORE INTO `stage_orders` VALUES (21,1429,'delivery',NULL);
INSERT  IGNORE INTO `stage_orders` VALUES (21,1431,'pickup',NULL);
INSERT  IGNORE INTO `stage_orders` VALUES (21,1431,'delivery',NULL);
INSERT  IGNORE INTO `stage_orders` VALUES (21,1432,'pickup',NULL);
INSERT  IGNORE INTO `stage_orders` VALUES (21,1432,'delivery',NULL);
INSERT  IGNORE INTO `stage_orders` VALUES (21,1433,'pickup',NULL);
INSERT  IGNORE INTO `stage_orders` VALUES (21,1433,'delivery',NULL);
INSERT  IGNORE INTO `stage_orders` VALUES (22,1434,'pickup',NULL);
INSERT  IGNORE INTO `stage_orders` VALUES (22,1434,'delivery',NULL);
INSERT  IGNORE INTO `stage_orders` VALUES (22,1435,'pickup',NULL);
INSERT  IGNORE INTO `stage_orders` VALUES (22,1435,'delivery',NULL);
INSERT  IGNORE INTO `stage_orders` VALUES (22,1436,'pickup',NULL);
INSERT  IGNORE INTO `stage_orders` VALUES (22,1436,'delivery',NULL);
INSERT  IGNORE INTO `stage_orders` VALUES (23,1437,'pickup',NULL);
INSERT  IGNORE INTO `stage_orders` VALUES (23,1437,'delivery',NULL);
INSERT  IGNORE INTO `stage_orders` VALUES (23,1438,'pickup',NULL);
INSERT  IGNORE INTO `stage_orders` VALUES (23,1438,'delivery',NULL);
INSERT  IGNORE INTO `stage_orders` VALUES (23,1439,'pickup',NULL);
INSERT  IGNORE INTO `stage_orders` VALUES (23,1439,'delivery',NULL);
INSERT  IGNORE INTO `stage_orders` VALUES (23,1440,'pickup',NULL);
INSERT  IGNORE INTO `stage_orders` VALUES (23,1440,'delivery',NULL);
INSERT  IGNORE INTO `stage_orders` VALUES (23,1441,'pickup',NULL);
INSERT  IGNORE INTO `stage_orders` VALUES (23,1441,'delivery',NULL);
INSERT  IGNORE INTO `stage_orders` VALUES (24,1442,'pickup',NULL);
INSERT  IGNORE INTO `stage_orders` VALUES (24,1442,'delivery',NULL);
INSERT  IGNORE INTO `stage_orders` VALUES (25,1443,'pickup',NULL);
INSERT  IGNORE INTO `stage_orders` VALUES (25,1443,'delivery',NULL);
INSERT  IGNORE INTO `stage_orders` VALUES (25,1444,'pickup',NULL);
INSERT  IGNORE INTO `stage_orders` VALUES (25,1444,'delivery',NULL);
INSERT  IGNORE INTO `stage_orders` VALUES (25,1446,'pickup',NULL);
INSERT  IGNORE INTO `stage_orders` VALUES (25,1446,'delivery',NULL);
INSERT  IGNORE INTO `stage_orders` VALUES (26,1447,'pickup',NULL);
INSERT  IGNORE INTO `stage_orders` VALUES (26,1447,'delivery',NULL);
INSERT  IGNORE INTO `stage_orders` VALUES (26,1448,'pickup',NULL);
INSERT  IGNORE INTO `stage_orders` VALUES (26,1448,'delivery',NULL);
INSERT  IGNORE INTO `stage_orders` VALUES (27,1449,'pickup',NULL);
INSERT  IGNORE INTO `stage_orders` VALUES (27,1449,'delivery',NULL);
INSERT  IGNORE INTO `stage_orders` VALUES (27,1502,'pickup',100);
INSERT  IGNORE INTO `stage_orders` VALUES (27,1502,'delivery',NULL);
INSERT  IGNORE INTO `stage_orders` VALUES (27,1503,'pickup',NULL);
INSERT  IGNORE INTO `stage_orders` VALUES (27,1503,'delivery',NULL);
INSERT  IGNORE INTO `stage_orders` VALUES (27,1504,'pickup',NULL);
INSERT  IGNORE INTO `stage_orders` VALUES (27,1504,'delivery',NULL);
INSERT  IGNORE INTO `stage_orders` VALUES (27,1505,'pickup',NULL);
INSERT  IGNORE INTO `stage_orders` VALUES (27,1505,'delivery',NULL);
INSERT  IGNORE INTO `stage_orders` VALUES (28,1506,'pickup',NULL);
INSERT  IGNORE INTO `stage_orders` VALUES (28,1506,'delivery',NULL);
INSERT  IGNORE INTO `stage_orders` VALUES (28,1507,'pickup',100);
INSERT  IGNORE INTO `stage_orders` VALUES (28,1507,'delivery',NULL);
INSERT  IGNORE INTO `stage_orders` VALUES (29,1508,'pickup',100);
INSERT  IGNORE INTO `stage_orders` VALUES (29,1508,'delivery',NULL);
INSERT  IGNORE INTO `stage_orders` VALUES (30,1509,'pickup',NULL);
INSERT  IGNORE INTO `stage_orders` VALUES (30,1509,'delivery',NULL);
INSERT  IGNORE INTO `stage_orders` VALUES (31,1510,'pickup',NULL);
INSERT  IGNORE INTO `stage_orders` VALUES (31,1510,'delivery',NULL);
INSERT  IGNORE INTO `stage_orders` VALUES (29,1511,'pickup',NULL);
INSERT  IGNORE INTO `stage_orders` VALUES (29,1511,'delivery',NULL);
INSERT  IGNORE INTO `stage_orders` VALUES (29,1513,'pickup',103);
INSERT  IGNORE INTO `stage_orders` VALUES (29,1513,'delivery',NULL);
INSERT  IGNORE INTO `stage_orders` VALUES (NULL,1514,'pickup',100);
INSERT  IGNORE INTO `stage_orders` VALUES (NULL,1514,'delivery',NULL);
INSERT  IGNORE INTO `stage_orders` VALUES (32,1515,'pickup',103);
INSERT  IGNORE INTO `stage_orders` VALUES (32,1515,'delivery',NULL);
INSERT  IGNORE INTO `stage_orders` VALUES (33,1516,'pickup',104);
INSERT  IGNORE INTO `stage_orders` VALUES (33,1516,'delivery',NULL);
INSERT  IGNORE INTO `stage_orders` VALUES (34,1517,'pickup',104);
INSERT  IGNORE INTO `stage_orders` VALUES (34,1517,'delivery',NULL);
INSERT  IGNORE INTO `stage_orders` VALUES (34,1518,'pickup',104);
INSERT  IGNORE INTO `stage_orders` VALUES (34,1518,'delivery',NULL);
INSERT  IGNORE INTO `stage_orders` VALUES (33,1519,'pickup',104);
INSERT  IGNORE INTO `stage_orders` VALUES (33,1519,'delivery',NULL);
INSERT  IGNORE INTO `stage_orders` VALUES (33,1520,'pickup',104);
INSERT  IGNORE INTO `stage_orders` VALUES (33,1520,'delivery',NULL);
INSERT  IGNORE INTO `stage_orders` VALUES (34,1521,'pickup',104);
INSERT  IGNORE INTO `stage_orders` VALUES (34,1521,'delivery',NULL);
INSERT  IGNORE INTO `stage_orders` VALUES (34,1522,'pickup',104);
INSERT  IGNORE INTO `stage_orders` VALUES (34,1522,'delivery',NULL);
INSERT  IGNORE INTO `stage_orders` VALUES (34,1523,'pickup',104);
INSERT  IGNORE INTO `stage_orders` VALUES (34,1523,'delivery',NULL);
INSERT  IGNORE INTO `stage_orders` VALUES (35,1524,'pickup',104);
INSERT  IGNORE INTO `stage_orders` VALUES (35,1524,'delivery',NULL);

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
) ENGINE=InnoDB AUTO_INCREMENT=36 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
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
INSERT  IGNORE INTO `trips` VALUES (29,200,'СПБ','МСК',2,1,'trip_assigned',NULL,1,'2026-02-08 13:22:43');
INSERT  IGNORE INTO `trips` VALUES (30,NULL,'СПБ','МСК',4,3,'trip_created',NULL,1,'2026-02-10 15:14:05');
INSERT  IGNORE INTO `trips` VALUES (31,NULL,'СПБ','МСК',4,1,'trip_created',NULL,1,'2026-02-10 17:07:31');
INSERT  IGNORE INTO `trips` VALUES (32,NULL,'СПБ','МСК',2,1,'trip_created',NULL,1,'2026-02-17 09:47:28');
INSERT  IGNORE INTO `trips` VALUES (33,NULL,'СПБ','МСК',2,1,'trip_created',NULL,1,'2026-02-17 14:29:41');
INSERT  IGNORE INTO `trips` VALUES (34,200,'СПБ','МСК',4,3,'trip_failed',NULL,1,'2026-02-17 14:30:01');
INSERT  IGNORE INTO `trips` VALUES (35,NULL,'СПБ','МСК',4,3,'trip_created',NULL,1,'2026-02-17 18:08:13');

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
) ENGINE=InnoDB AUTO_INCREMENT=1000000 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
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
INSERT  IGNORE INTO `users` VALUES (100,'Курьер 100','courier','МСК',NULL);
INSERT  IGNORE INTO `users` VALUES (101,'Курьер 101','courier','МСК',NULL);
INSERT  IGNORE INTO `users` VALUES (102,'Курьер 102','courier','МСК',NULL);
INSERT  IGNORE INTO `users` VALUES (103,'Курьер 103','courier','СПБ',NULL);
INSERT  IGNORE INTO `users` VALUES (104,'Курьер 104','courier','СПБ',NULL);
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
INSERT  IGNORE INTO `users` VALUES (1001,'Клиент 1001','client','МСК',NULL);
INSERT  IGNORE INTO `users` VALUES (1002,'Клиент 1002','client','МСК',NULL);
INSERT  IGNORE INTO `users` VALUES (1003,'Клиент 1003','client','МСК',NULL);
INSERT  IGNORE INTO `users` VALUES (1004,'Клиент 1004','client','СПБ',NULL);
INSERT  IGNORE INTO `users` VALUES (1005,'Клиент 1005','client','СПБ','+79199030069');
INSERT  IGNORE INTO `users` VALUES (2001,'Получатель 2001','recipient','МСК',NULL);
INSERT  IGNORE INTO `users` VALUES (2002,'Получатель 2002','recipient','МСК',NULL);
INSERT  IGNORE INTO `users` VALUES (2003,'Получатель 2003','recipient','МСК',NULL);
INSERT  IGNORE INTO `users` VALUES (2004,'Получатель 2004','recipient','СПБ',NULL);
INSERT  IGNORE INTO `users` VALUES (2005,'Получатель 2005','recipient','СПБ',NULL);
INSERT  IGNORE INTO `users` VALUES (2006,'System','system','',NULL);
INSERT  IGNORE INTO `users` VALUES (999999,'System','system','',NULL);

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
        
    ELSE
        SIGNAL SQLSTATE '45000'
        SET MESSAGE_TEXT = 'Unsupported entity_type in fsm_perform_action';
    END IF;
    
    -- ✨ НОВОЕ: возвращаем результат
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
