-- Domain DB dump (courier) — cleaned for FSM Platform
-- Removed platform/obsolete tables: core_outbox, fsm_action_logs, fsm_errors_log, fsm_timers, server_fsm_instances
-- Omitted events/routines from legacy dump (host DEFINER + platform deps).
-- Source: dump-testdb-202607091457.sql

-- MySQL dump 10.13  Distrib 8.0.19, for Win64 (x86_64)
--
-- Host: mysql-27f21b2d-maskit26-19f5.a.aivencloud.com    Database: testdb
-- ------------------------------------------------------
-- Server version	8.4.8

/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!50503 SET NAMES utf8mb4 */;
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

LOCK TABLES `button_states` WRITE;
/*!40000 ALTER TABLE `button_states` DISABLE KEYS */;
INSERT INTO `button_states` VALUES (1,'create_order','Создать заказ','client','order_created','active'),(2,'create_order','Создать заказ','client','order_parcel_submitted','inactive'),(3,'open_cell','Открыть ячейку','client','locker_reserved','active'),(4,'open_cell','Открыть ячейку','client','locker_opened','inactive'),(5,'open_cell','Открыть ячейку','client','locker_free','inactive'),(6,'close_cell','Закрыть ячейку','client','locker_opened','active'),(7,'close_cell','Закрыть ячейку','client','locker_parcel_confirmed','active'),(8,'close_cell','Закрыть ячейку','client','locker_parcel_submitted','inactive'),(9,'cancel_order','Отменить заказ','client','order_created','active'),(10,'cancel_order','Отменить заказ','client','order_courier_reserved_post1_and_post2','active'),(11,'cancel_order','Отменить заказ','client','order_completed','inactive'),(12,'pickup_order','Забрать заказ','recipient','order_parcel_submitted','active'),(13,'pickup_order','Забрать заказ','recipient','order_delivered_to_client','inactive'),(14,'open_cell','Открыть ячейку','recipient','locker_parcel_submitted','active'),(15,'open_cell','Открыть ячейку','recipient','locker_opened','inactive'),(16,'close_cell','Закрыть ячейку','recipient','locker_opened','active'),(17,'close_cell','Закрыть ячейку','recipient','locker_free','inactive'),(18,'confirm_pickup','Подтвердить получение','recipient','order_delivered_to_client','active'),(19,'confirm_pickup','Подтвердить получение','recipient','order_completed','inactive'),(20,'take_order','Взять заказ','courier','order_courier_reserved_post1_and_post2','active'),(21,'take_order','Взять заказ','courier','order_courier1_assigned','inactive'),(22,'pickup_from_client','Забрал у клиента','courier','order_courier1_assigned','active'),(23,'pickup_from_client','Забрал у клиента','courier','order_courier_has_parcel','inactive'),(24,'arrived_at_recipient','Прибыл к получателю','courier','order_courier_has_parcel','active'),(25,'arrived_at_recipient','Прибыл к получателю','courier','order_parcel_delivered','inactive'),(26,'open_cell','Открыть ячейку','courier','locker_parcel_submitted','active'),(27,'open_cell','Открыть ячейку','courier','locker_opened','inactive'),(28,'close_cell','Закрыть ячейку','courier','locker_opened','active'),(29,'close_cell','Закрыть ячейку','courier','locker_parcel_confirmed','active'),(30,'cancel_order','Отменить заказ','courier','order_courier1_assigned','active'),(31,'cancel_order','Отменить заказ','courier','order_completed','inactive'),(32,'take_trip','Взять рейс','driver','trip_created','active'),(33,'take_trip','Взять рейс','driver','trip_assigned','inactive'),(34,'arrived_at_locker','Прибыл к постамату','driver','trip_assigned','active'),(35,'arrived_at_locker','Прибыл к постамату','driver','trip_ready_for_pickup','inactive'),(36,'start_trip','Начал путь','driver','trip_ready_for_pickup','active'),(37,'start_trip','Начал путь','driver','trip_in_progress','inactive'),(38,'arrived_destination','Прибыл','driver','trip_in_progress','active'),(39,'arrived_destination','Прибыл','driver','trip_arrived_at_destination','inactive'),(40,'open_cell','Открыть ячейку','driver','locker_reserved','active'),(41,'open_cell','Открыть ячейку','driver','locker_opened','inactive'),(42,'close_cell','Закрыть ячейку','driver','locker_opened','active'),(43,'close_cell','Закрыть ячейку','driver','locker_parcel_submitted','inactive'),(44,'cancel_trip','Отменить рейс','driver','trip_assigned','active'),(45,'cancel_trip','Отменить рейс','driver','trip_completed','inactive'),(46,'assign_courier','Назначить','operator','order_created','active'),(47,'assign_courier','Назначить','operator','order_courier1_assigned','inactive'),(48,'remove_assignment','Снять','operator','order_courier1_assigned','active'),(49,'remove_assignment','Снять','operator','order_created','inactive'),(50,'block_cell','Заблокировать ячейку','operator','locker_free','active'),(51,'block_cell','Заблокировать ячейку','operator','locker_blocked','inactive'),(52,'reserve_cell','Забронировать ячейку','operator','locker_free','active'),(53,'reserve_cell','Забронировать ячейку','operator','locker_reserved','inactive'),(54,'reset_reservation','Снять бронь ячейки (reset)','operator','locker_reserved','active'),(55,'reset_reservation','Снять бронь ячейки (reset)','operator','locker_free','inactive'),(56,'open_cell','Открыть ячейку','operator','locker_reserved','active'),(57,'open_cell','Открыть ячейку','operator','locker_opened','inactive'),(58,'close_cell','Закрыть ячейку','operator','locker_opened','active'),(59,'close_cell','Закрыть ячейку','operator','locker_parcel_submitted','inactive'),(60,'to_maintenance','В ремонт ячейку','operator','locker_free','active'),(61,'to_maintenance','В ремонт ячейку','operator','locker_maintenance','inactive'),(62,'from_maintenance','Снять с ремонта ячейку','operator','locker_maintenance','active'),(63,'from_maintenance','Снять с ремонта ячейку','operator','locker_free','inactive'),(64,'confirm_pickup','','recipient','order_courier2_parcel_delivered','active'),(65,'take_order','Взять заказ','courier','order_created','active'),(66,'report_error','Сообщить об ошибке','driver','locker_reserved','active'),(67,'report_error','Сообщить об ошибке','driver','locker_opened','active'),(68,'report_error','Сообщить об ошибке','courier','locker_reserved','active'),(69,'report_error','Сообщить об ошибке','courier','locker_opened','active'),(70,'report_error','Сообщить об ошибке','client','locker_reserved','active'),(71,'report_error','Сообщить об ошибке','client','locker_opened','active'),(72,'report_error','Сообщить об ошибке','recipient','locker_parcel_submitted','active'),(73,'report_error','Сообщить об ошибке','recipient','locker_opened','active'),(74,'report_error','Сообщить об ошибке','operator','locker_free','active'),(75,'report_error','Сообщить об ошибке','operator','locker_error','active'),(76,'report_error','Сообщить об ошибке','operator','locker_maintenance','active'),(77,'confirm_delivery_with_code','Доставил заказ','courier','order_courier2_parcel_delivered','active'),(78,'reserve_slot','Vzyat slot','driver','direction_open','active'),(79,'reserve_slot','Vzyat slot','driver','direction_slot_taken','inactive'),(81,'start_loading','Nachat zagruzku','driver','direction_loading','inactive'),(82,'complete_loading','Zavershit pogruzku','driver','direction_loading','active'),(83,'complete_loading','Zavershit pogruzku','driver','direction_open','inactive'),(84,'reserve_slot','Vzyat slot','driver','direction_loading','inactive'),(85,'reserve_slot','Vzyat slot','driver','direction_loading_finished','inactive'),(89,'start_loading','Nachat zagruzku','driver','direction_open','active');
/*!40000 ALTER TABLE `button_states` ENABLE KEYS */;
UNLOCK TABLES;

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
) ENGINE=InnoDB AUTO_INCREMENT=194 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `cell_access_tokens`
--

LOCK TABLES `cell_access_tokens` WRITE;
/*!40000 ALTER TABLE `cell_access_tokens` DISABLE KEYS */;
INSERT INTO `cell_access_tokens` VALUES (1,1510,'pickup',31,1005,'490a6b4f6dc249bf934da7bf548b9dcaf12dc9b0fd286e5b67f08622a1f51777',NULL,'ACTIVE','2026-02-11 18:35:47',0,'2026-02-11 18:20:46',NULL),(2,1510,'pickup',31,1005,'d60ec2ef2d0fe1a779ba88272fbf3db22d4fd179ef759270535a4f1cd72f58df',NULL,'ACTIVE','2026-02-12 10:06:24',0,'2026-02-12 09:51:23',NULL),(3,1510,'pickup',31,1005,'736773fd5d112b0f3f87c7439b6c105f468cfb0e6b7dcf69b8fbfc1430492fe0',NULL,'ACTIVE','2026-02-12 10:34:41',0,'2026-02-12 10:19:41',NULL);
/*!40000 ALTER TABLE `cell_access_tokens` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `core_order_mapping`
--

DROP TABLE IF EXISTS `core_order_mapping`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `core_order_mapping` (
  `id` int NOT NULL AUTO_INCREMENT,
  `local_order_id` int NOT NULL,
  `core_order_id` int NOT NULL,
  `role` varchar(50) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `kind` varchar(50) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `upper` int DEFAULT NULL,
  `b_state` int DEFAULT NULL,
  `created_at` datetime DEFAULT CURRENT_TIMESTAMP,
  `updated_at` datetime DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  `client_local_user_id` int DEFAULT NULL,
  `performer_local_user_id` int DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `uk_core_order` (`core_order_id`),
  UNIQUE KEY `uk_local_order_role` (`local_order_id`,`role`),
  CONSTRAINT `core_order_mapping_ibfk_1` FOREIGN KEY (`local_order_id`) REFERENCES `orders` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=113 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `core_order_mapping`
--

LOCK TABLES `core_order_mapping` WRITE;
/*!40000 ALTER TABLE `core_order_mapping` DISABLE KEYS */;
INSERT INTO `core_order_mapping` VALUES (1,1539,1568,NULL,NULL,NULL,NULL,'2026-04-08 09:26:10','2026-04-08 09:26:10',NULL,NULL),(2,1540,1569,NULL,NULL,NULL,NULL,'2026-04-08 12:57:55','2026-04-08 12:57:55',NULL,NULL),(3,1541,1570,NULL,NULL,NULL,NULL,'2026-04-08 13:05:06','2026-04-08 13:05:06',NULL,NULL);
/*!40000 ALTER TABLE `core_order_mapping` ENABLE KEYS */;
UNLOCK TABLES;

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
  `registered_at` datetime DEFAULT CURRENT_TIMESTAMP,
  `last_sync_at` datetime DEFAULT NULL,
  `sync_status` enum('success','failed') DEFAULT 'success',
  `error_message` text,
  `token` varchar(255) DEFAULT NULL,
  `u_hash` varchar(255) DEFAULT NULL,
  `car_core_id` int DEFAULT NULL,
  PRIMARY KEY (`local_user_id`),
  UNIQUE KEY `uk_core` (`core_u_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `core_user_mapping`
--

LOCK TABLES `core_user_mapping` WRITE;
/*!40000 ALTER TABLE `core_user_mapping` DISABLE KEYS */;
INSERT INTO `core_user_mapping` VALUES (1000006,972,2,'2026-04-03 09:15:56','2026-04-03 09:15:56','success',NULL,NULL,NULL,NULL),(1000007,973,1,'2026-04-03 12:31:32','2026-04-03 12:31:32','success',NULL,NULL,NULL,NULL),(1000008,974,1,'2026-04-03 13:15:57','2026-04-03 13:15:57','success',NULL,NULL,NULL,NULL);
/*!40000 ALTER TABLE `core_user_mapping` ENABLE KEYS */;
UNLOCK TABLES;

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
) ENGINE=InnoDB AUTO_INCREMENT=9 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `directions`
--

LOCK TABLES `directions` WRITE;
/*!40000 ALTER TABLE `directions` DISABLE KEYS */;
INSERT INTO `directions` VALUES (1,'МСК','СПБ',1,2,0,0),(2,'СПБ','МСК',2,1,0,1),(3,'Москва','Санкт-Петербург',1,2,1,1);
/*!40000 ALTER TABLE `directions` ENABLE KEYS */;
UNLOCK TABLES;

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
) ENGINE=InnoDB AUTO_INCREMENT=44 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `driver_reservations`
--

LOCK TABLES `driver_reservations` WRITE;
/*!40000 ALTER TABLE `driver_reservations` DISABLE KEYS */;
INSERT INTO `driver_reservations` VALUES (1,200,1,1,1,'2026-03-15 13:51:32','2026-03-15 14:21:33','reservation_completed'),(3,200,1,1,1,'2026-03-17 09:43:03','2026-03-17 10:13:04','reservation_completed'),(5,200,1,1,1,'2026-03-18 14:23:34','2026-03-18 14:53:35','reservation_completed');
/*!40000 ALTER TABLE `driver_reservations` ENABLE KEYS */;
UNLOCK TABLES;

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
) ENGINE=InnoDB AUTO_INCREMENT=125 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `fsm_actions`
--

LOCK TABLES `fsm_actions` WRITE;
/*!40000 ALTER TABLE `fsm_actions` DISABLE KEYS */;
INSERT INTO `fsm_actions` VALUES (1,'locker_reserve_cell','Zabronirovat yacheyku'),(2,'trip_assign_voditel','Naznachit voditelya'),(3,'trip_start_trip','Nachat poyezdku'),(4,'trip_complete_trip','Zavershit poyezdku'),(5,'locker_open_locker','Otkryt yacheyku'),(6,'locker_close_locker','Zakryt yacheyku'),(7,'order_timeout_reservation','Taymaut rezervirovaniya'),(8,'locker_confirm_parcel_in','Podtverdit posylku vnutri'),(49,'order_assign_courier1_to_order','Naznachit Kurer1 na zakaz'),(61,'order_timeout_confirmation','Taymaut podtverzhdeniya'),(68,'order_client_will_deliver','Klient sam sdast posylku'),(69,'order_confirm_parcel_in','Подтвердить посылку (Order)'),(70,'order_parcel_submitted','Посылка сдана (Order)'),(71,'order_courier_pickup_parcel','Kurer zabral posilku'),(72,'locker_reset','sbros yacheiki'),(73,'locker_set_locker_to_maintenance','perevesti v obsluzhivanie'),(74,'order_cancel_reservation','otmenit rezervatsiyu'),(75,'locker_confirm_parcel_not_found','posylka_ne_naidena'),(76,'locker_cancel_reservation','otmena rezervatsii yacheiki'),(77,'trip_start_pickup','nachat_zabir'),(78,'trip_confirm_pickup','podtverdit_zabir'),(79,'trip_confirm_delivery','podtverdit_dostavku'),(81,'order_reserve_for_client_A_to_B','zarezervirovat_dlya_klienta_A_to_B'),(82,'order_reserve_for_courier_A_to_B','zarezervirovat_dlya_kurera_A_to_B'),(83,'order_pickup_by_voditel','voditel_zabral_posylku'),(84,'order_start_transit','nachat_perevozku'),(85,'order_arrive_at_post2','pridyal_k_post2'),(86,'locker_confirm_parcel_out','Podtverdit poluchenie posylki iz yacheiki'),(87,'locker_dont_closed','Yacheika ne zakryta posle raboty'),(88,'order_pickup_poluchatel','Klient poluchil posylku'),(89,'order_delivered_parcel','Zavershit zakaz posle polucheniya'),(90,'order_assign_courier2_to_order','Naznachit kurera2'),(91,'order_courier2_pickup_parcel','Kurer2 zabral iz post2'),(92,'order_courier2_delivered_parcel','Kurer2 zavershil dostavku'),(93,'order_report_parcel_missing','Posylka ne naidena v yacheike'),(94,'order_report_delivery_failed','Soobshchit o neudache dostavki'),(95,'order_request_manual_intervention','Zaprosit ruchnoe vmeshatelstvo'),(96,'trip_report_driver_not_found','Soobshchit: voditel ne naiden'),(97,'trip_report_failure','Soobshchit o sbue poezdki'),(98,'trip_request_manual_intervention','Zaprosit ruchnoe vmeshatelstvo'),(99,'order_courier1_cancel','Kurer1 otmenil do zabora'),(100,'order_courier2_cancel','Kurer2 otmenil do zabora iz post2'),(101,'order_timeout_no_pickup','Taymaut: kurer ne zabral posylku'),(102,'trip_vzyat_reis','Vzyat reis'),(103,'locker_confirm_parcel_out_recipient','Podtverdit vydachu poluchatelyu iz yacheiki'),(104,'order_recipient_confirmed','Klient podtverdil poluchenie'),(105,'locker_close_pickup',NULL),(106,'locker_failed_to_open','Ne otkrilas yacheika'),(107,'order_confirm_post2','voditel polozhil posilku v post2'),(108,'order_client_deliv_post1','client polozhil posilku v post1'),(113,'driver_reservation_start_loading','Начать погрузку'),(114,'driver_reservation_complete_loading','Завершить погрузку'),(115,'driver_reservation_expire','Истёк таймаут'),(116,'driver_reservation_cancel','Отменить резерв'),(117,'trip_cancel','Отменить рейс'),(123,'trip_reassign_driver','Переназначить водителя'),(124,'trip_resume_with_new_driver','Возобновить рейс с новым водителем');
/*!40000 ALTER TABLE `fsm_actions` ENABLE KEYS */;
UNLOCK TABLES;

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

LOCK TABLES `fsm_states` WRITE;
/*!40000 ALTER TABLE `fsm_states` DISABLE KEYS */;
INSERT INTO `fsm_states` VALUES (1,'order_created','Sozdan'),(3,'trip_assigned','Naznachen'),(4,'trip_in_progress','V puti'),(5,'trip_completed','Zavershon'),(6,'locker_reserved','Yacheika zarezervirovana'),(7,'locker_opened','Yacheika otkryta'),(8,'order_parcel_submitted','Posylka sdana'),(49,'order_courier1_assigned','Kurer1 naznachen'),(60,'order_parcel_confirmed','Posylka podtverzhdena'),(61,'order_parcel_missing','Posylka ne naidena'),(68,'locker_free','Yacheika svobodna'),(69,'locker_occupied','Yacheika zanyata'),(70,'locker_error','Oshibka yacheiki'),(71,'locker_maintenance','Na obsluzhivanii'),(72,'locker_parcel_submitted','Posylka sdana'),(73,'locker_parcel_confirmed','Posylka podtverzhdena'),(74,'locker_parcel_missing','Posylka ne naidena'),(75,'order_courier_has_parcel','Kurer zabral posilku'),(76,'order_reservation_expired','rezervatsiya zavershena po taymautu'),(77,'order_courier_failed','kurer ne podtverdil zabir'),(78,'order_cancelled','zakaz otmenen klientom'),(79,'locker_closed_empty','yacheyka zakryta pustaya'),(80,'trip_ready_for_pickup','gotov_zabrat'),(81,'trip_parcel_picked_up','posylka_zabirana'),(82,'trip_arrived_at_destination','pridyal_k_meste'),(83,'trip_parcel_delivered','posylka_sdana'),(84,'order_client_reserved_post1_and_post2','klient_zarezerviroval_1_i_2'),(85,'order_courier_reserved_post1_and_post2','kurer_zarezerviroval_1_i_2'),(87,'order_picked_up_from_post1','posylka_zabrana_iz_post1'),(88,'order_in_transit_to_post2','v_perevozke_k_post2'),(89,'order_arrived_at_post2','dostavlena_v_post2'),(90,'order_delivered_to_client','Posylka poluchena klientom'),(91,'order_courier2_assigned','Kurer2 naznachen'),(92,'order_courier2_has_parcel','Kurer2 zabral posylku'),(93,'order_completed','Zakaz zavershon'),(94,'order_delivery_failed','Dostavka ne udalas'),(95,'order_manual_intervention_required','Trebuetsya ruchnoe vmeshatelstvo'),(96,'trip_driver_not_found','Voditel ne naiden'),(97,'trip_failed','Poezdka prervana'),(98,'trip_manual_intervention_required','Trebuetsya ruchnoe vmeshatelstvo'),(99,'trip_created','Reis sozdan'),(100,'locker_parcel_pickup_driver','posilku zabral voditel'),(101,'locker_parcel_pickup_recipient','Poluchatel zabral posilku'),(102,'order_courier2_parcel_delivered','Kurer2 dostavil klientu, ojidaem podtverzhdeniya'),(103,'order_parcel_confirmed_post2','Posylka podtverzhdena v postamate2'),(104,'order_client_post1','posilka v post1'),(109,'reservation_active','Резерв активен'),(110,'reservation_loading','Водитель загружает'),(111,'reservation_completed','Погрузка завершена'),(112,'reservation_expired','Резерв истёк'),(113,'reservation_cancelled','Резерв отменён'),(114,'trip_canceled','Рейс отменён');
/*!40000 ALTER TABLE `fsm_states` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `fsm_transitions`
--

DROP TABLE IF EXISTS `fsm_transitions`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `fsm_transitions` (
  `id` int NOT NULL AUTO_INCREMENT,
  `entity_type` varchar(100) NOT NULL,
  `from_state_id` int NOT NULL,
  `action_id` int NOT NULL,
  `guard_name` varchar(100) DEFAULT NULL,
  `guard_params` json DEFAULT NULL,
  `priority` int NOT NULL DEFAULT '100',
  `effect_name` varchar(100) DEFAULT NULL,
  `effect_params` json DEFAULT NULL,
  `to_state_id` int NOT NULL,
  PRIMARY KEY (`id`),
  KEY `from_state_id` (`from_state_id`),
  KEY `action_id` (`action_id`),
  KEY `to_state_id` (`to_state_id`),
  CONSTRAINT `fsm_transitions_ibfk_1` FOREIGN KEY (`from_state_id`) REFERENCES `fsm_states` (`id`),
  CONSTRAINT `fsm_transitions_ibfk_2` FOREIGN KEY (`action_id`) REFERENCES `fsm_actions` (`id`),
  CONSTRAINT `fsm_transitions_ibfk_3` FOREIGN KEY (`to_state_id`) REFERENCES `fsm_states` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=167 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `fsm_transitions`
--

LOCK TABLES `fsm_transitions` WRITE;
/*!40000 ALTER TABLE `fsm_transitions` DISABLE KEYS */;
INSERT INTO `fsm_transitions` VALUES (29,'order',60,70,NULL,NULL,100,NULL,NULL,8),(30,'locker',68,1,NULL,NULL,100,NULL,NULL,6),(31,'locker',6,5,NULL,NULL,100,NULL,NULL,7),(36,'order',75,69,NULL,NULL,100,NULL,NULL,60),(38,'order',49,71,NULL,NULL,100,NULL,NULL,75),(42,'order',49,61,NULL,NULL,100,NULL,NULL,77),(47,'locker',70,72,NULL,NULL,100,NULL,NULL,68),(48,'locker',71,72,NULL,NULL,100,NULL,NULL,68),(49,'locker',79,72,NULL,NULL,100,NULL,NULL,68),(50,'locker',74,6,NULL,NULL,100,NULL,NULL,79),(51,'locker',68,73,NULL,NULL,100,NULL,NULL,71),(52,'locker',7,75,NULL,NULL,100,NULL,NULL,74),(53,'locker',6,76,NULL,NULL,100,NULL,NULL,68),(54,'locker',70,73,NULL,NULL,100,NULL,NULL,71),(55,'trip',3,2,NULL,NULL,100,NULL,NULL,80),(56,'trip',80,78,NULL,NULL,100,NULL,NULL,81),(57,'trip',3,3,NULL,NULL,100,NULL,NULL,4),(58,'trip',82,79,NULL,NULL,100,NULL,NULL,83),(59,'trip',83,4,NULL,NULL,100,NULL,NULL,5),(61,'locker',73,6,NULL,NULL,100,NULL,NULL,69),(62,'locker',69,5,NULL,NULL,100,NULL,NULL,7),(63,'locker',79,76,NULL,NULL,100,NULL,NULL,68),(74,'order',8,83,NULL,NULL,100,NULL,NULL,87),(75,'order',87,84,NULL,NULL,100,NULL,NULL,88),(76,'order',88,85,NULL,NULL,100,NULL,NULL,89),(77,'order',89,107,NULL,NULL,100,NULL,NULL,103),(79,'locker',7,87,NULL,NULL,100,NULL,NULL,70),(80,'order',103,88,NULL,NULL,100,NULL,NULL,90),(81,'order',90,89,NULL,NULL,100,NULL,NULL,93),(82,'order',103,90,NULL,NULL,100,NULL,NULL,91),(83,'order',91,91,NULL,NULL,100,NULL,NULL,92),(84,'order',92,92,NULL,NULL,100,NULL,NULL,102),(85,'order',60,93,NULL,NULL,100,NULL,NULL,61),(86,'order',75,94,NULL,NULL,100,NULL,NULL,94),(87,'order',88,94,NULL,NULL,100,NULL,NULL,94),(88,'order',92,94,NULL,NULL,100,NULL,NULL,94),(89,'order',1,95,NULL,NULL,100,NULL,NULL,95),(90,'order',49,95,NULL,NULL,100,NULL,NULL,95),(91,'order',60,95,NULL,NULL,100,NULL,NULL,95),(92,'order',75,95,NULL,NULL,100,NULL,NULL,95),(93,'order',84,95,NULL,NULL,100,NULL,NULL,95),(94,'order',85,95,NULL,NULL,100,NULL,NULL,95),(95,'order',87,95,NULL,NULL,100,NULL,NULL,95),(96,'order',88,95,NULL,NULL,100,NULL,NULL,95),(97,'order',89,95,NULL,NULL,100,NULL,NULL,95),(98,'order',90,95,NULL,NULL,100,NULL,NULL,95),(99,'order',91,95,NULL,NULL,100,NULL,NULL,95),(100,'order',92,95,NULL,NULL,100,NULL,NULL,95),(101,'trip',3,96,NULL,NULL,100,NULL,NULL,96),(102,'trip',3,97,NULL,NULL,100,NULL,NULL,97),(103,'trip',4,97,NULL,NULL,100,NULL,NULL,97),(104,'trip',80,97,NULL,NULL,100,NULL,NULL,97),(105,'trip',81,97,NULL,NULL,100,NULL,NULL,97),(106,'trip',82,97,NULL,NULL,100,NULL,NULL,97),(109,'trip',3,98,NULL,NULL,100,NULL,NULL,98),(110,'trip',4,98,NULL,NULL,100,NULL,NULL,98),(111,'trip',80,98,NULL,NULL,100,NULL,NULL,98),(112,'trip',81,98,NULL,NULL,100,NULL,NULL,98),(113,'trip',82,98,NULL,NULL,100,NULL,NULL,98),(114,'trip',83,98,NULL,NULL,100,NULL,NULL,98),(116,'order',49,99,NULL,NULL,100,NULL,NULL,1),(117,'order',49,101,NULL,NULL,100,NULL,NULL,1),(118,'order',91,100,NULL,NULL,100,NULL,NULL,89),(119,'order',91,101,NULL,NULL,100,NULL,NULL,89),(120,'trip',99,102,NULL,NULL,100,NULL,NULL,3),(121,'locker',7,86,NULL,NULL,100,NULL,NULL,100),(122,'locker',100,6,NULL,NULL,100,NULL,NULL,79),(123,'locker',7,103,NULL,NULL,100,NULL,NULL,101),(124,'locker',101,6,NULL,NULL,100,NULL,NULL,79),(125,'order',102,104,NULL,NULL,100,NULL,NULL,93),(126,'locker',7,6,NULL,NULL,100,NULL,NULL,69),(127,'locker',7,105,NULL,NULL,100,NULL,NULL,79),(128,'order',103,93,NULL,NULL,100,NULL,NULL,61),(129,'order',103,95,NULL,NULL,100,NULL,NULL,95),(130,'order',1,49,NULL,NULL,100,NULL,NULL,49),(131,'locker',6,106,NULL,NULL,100,NULL,NULL,70),(132,'order',1,74,NULL,NULL,100,NULL,NULL,78),(133,'trip',3,97,NULL,NULL,100,NULL,NULL,99),(134,'locker',69,106,NULL,NULL,100,NULL,NULL,70),(135,'trip',4,4,NULL,NULL,100,NULL,NULL,5),(136,'order',1,108,NULL,NULL,100,NULL,NULL,104),(137,'order',104,69,NULL,NULL,100,NULL,NULL,60),(145,'driver_reservations',109,113,NULL,NULL,100,NULL,NULL,110),(146,'driver_reservations',110,114,NULL,NULL,100,NULL,NULL,111),(147,'driver_reservations',109,115,NULL,NULL,100,NULL,NULL,112),(148,'driver_reservations',110,115,NULL,NULL,100,NULL,NULL,112),(149,'driver_reservations',109,116,NULL,NULL,100,NULL,NULL,113),(150,'driver_reservations',110,116,NULL,NULL,100,NULL,NULL,113),(151,'trip',4,117,NULL,NULL,100,NULL,NULL,114),(152,'trip',3,117,NULL,NULL,100,NULL,NULL,114),(153,'trip',97,123,NULL,NULL,100,NULL,NULL,3),(154,'order',95,49,NULL,NULL,100,NULL,NULL,49),(155,'order',95,90,NULL,NULL,100,NULL,NULL,91),(156,'trip',97,124,NULL,NULL,100,NULL,NULL,4),(157,'locker',6,73,NULL,NULL,100,NULL,NULL,71),(158,'locker',7,73,NULL,NULL,100,NULL,NULL,71),(159,'order',60,74,NULL,NULL,100,NULL,NULL,78),(160,'order',49,74,NULL,NULL,100,NULL,NULL,78),(161,'order',75,74,NULL,NULL,100,NULL,NULL,78),(162,'order',8,74,NULL,NULL,100,NULL,NULL,78),(163,'order',87,74,NULL,NULL,100,NULL,NULL,78),(164,'order',88,74,NULL,NULL,100,NULL,NULL,78),(165,'order',89,74,NULL,NULL,100,NULL,NULL,78),(166,'order',103,74,NULL,NULL,100,NULL,NULL,78);
/*!40000 ALTER TABLE `fsm_transitions` ENABLE KEYS */;
UNLOCK TABLES;

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

LOCK TABLES `locker_cells` WRITE;
/*!40000 ALTER TABLE `locker_cells` DISABLE KEYS */;
INSERT INTO `locker_cells` VALUES (1,1,'S-01','S','locker_free',1561,'2025-11-22 15:23:13','2026-05-11 14:32:03'),(2,1,'S-02','S','locker_free',1562,'2025-11-22 15:23:13','2026-05-11 14:32:03'),(3,1,'S-03','S','locker_free',1563,'2025-11-22 15:23:13','2026-05-11 14:32:03');
/*!40000 ALTER TABLE `locker_cells` ENABLE KEYS */;
UNLOCK TABLES;
/*!50003 SET @saved_cs_client      = @@character_set_client */ ;
/*!50003 SET @saved_cs_results     = @@character_set_results */ ;
/*!50003 SET @saved_col_connection = @@collation_connection */ ;
/*!50003 SET character_set_client  = utf8mb4 */ ;
/*!50003 SET character_set_results = utf8mb4 */ ;
/*!50003 SET collation_connection  = utf8mb4_0900_ai_ci */ ;
/*!50003 SET @saved_sql_mode       = @@sql_mode */ ;
/*!50003 SET sql_mode              = 'ONLY_FULL_GROUP_BY,STRICT_TRANS_TABLES,NO_ZERO_IN_DATE,NO_ZERO_DATE,ERROR_FOR_DIVISION_BY_ZERO,NO_ENGINE_SUBSTITUTION' */ ;
DELIMITER ;;
/*!50003 CREATE*/ /*!50017 DEFINER=`avnadmin`@`%`*/ /*!50003 TRIGGER `trg_locker_cell_status_check` BEFORE UPDATE ON `locker_cells` FOR EACH ROW BEGIN
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

LOCK TABLES `locker_models` WRITE;
/*!40000 ALTER TABLE `locker_models` DISABLE KEYS */;
INSERT INTO `locker_models` VALUES (1,'Model-Post1',NULL,10,5,2,1,'2025-10-29 17:20:54'),(2,'Model-2',NULL,10,5,2,1,'2025-11-21 13:37:49'),(3,'Model-3',NULL,10,5,2,1,'2025-11-21 13:37:49');
/*!40000 ALTER TABLE `locker_models` ENABLE KEYS */;
UNLOCK TABLES;

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

LOCK TABLES `lockers` WRITE;
/*!40000 ALTER TABLE `lockers` DISABLE KEYS */;
INSERT INTO `lockers` VALUES (1,1,'POST1','Москва','Москва, ул. Тверская, д. 1',NULL,NULL,'locker_inactive','2025-11-22 15:22:48'),(2,1,'POST2','Санкт-Петербург','Санкт-Петербург, Невский пр., д. 1',NULL,NULL,'locker_inactive','2025-11-22 15:22:48'),(3,1,'POST3','Москва','Москва, Ленинградский проспект, д. 1',NULL,NULL,'locker_inactive','2025-11-22 15:22:48');
/*!40000 ALTER TABLE `lockers` ENABLE KEYS */;
UNLOCK TABLES;

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
) ENGINE=InnoDB AUTO_INCREMENT=345 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `order_requests`
--

LOCK TABLES `order_requests` WRITE;
/*!40000 ALTER TABLE `order_requests` DISABLE KEYS */;
INSERT INTO `order_requests` VALUES (1,0,'string','string','string','string','FAILED',NULL,'NOT_IMPLEMENTED','order_creation handler not implemented yet','2025-12-07 13:53:25',NULL),(2,0,'string','string','string','string','FAILED',NULL,'NO_FREE_CELLS','Не найдены свободные ячейки нужного размера','2025-12-07 16:37:12',NULL),(3,1005,'test','S','courier','courier','COMPLETED',6,NULL,NULL,'2025-12-07 16:45:30',NULL);
/*!40000 ALTER TABLE `order_requests` ENABLE KEYS */;
UNLOCK TABLES;

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
) ENGINE=InnoDB AUTO_INCREMENT=1569 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `orders`
--

LOCK TABLES `orders` WRITE;
/*!40000 ALTER TABLE `orders` DISABLE KEYS */;
INSERT INTO `orders` VALUES (1,'order_courier_failed','Timeout Order','courier',NULL,'courier',2,12,'2025-12-16 09:46:53','2025-11-24 16:33:51',0,NULL),(2,'order_reservation_expired','Trip Order 1','courier',NULL,'courier',3,13,'2025-11-24 16:36:07','2025-11-24 16:33:51',0,NULL),(3,'order_reservation_expired','Trip Order 2','courier',NULL,'courier',4,14,'2025-11-24 16:36:08','2025-11-24 16:33:51',0,NULL);
/*!40000 ALTER TABLE `orders` ENABLE KEYS */;
UNLOCK TABLES;
/*!50003 SET @saved_cs_client      = @@character_set_client */ ;
/*!50003 SET @saved_cs_results     = @@character_set_results */ ;
/*!50003 SET @saved_col_connection = @@collation_connection */ ;
/*!50003 SET character_set_client  = utf8mb4 */ ;
/*!50003 SET character_set_results = utf8mb4 */ ;
/*!50003 SET collation_connection  = utf8mb4_0900_ai_ci */ ;
/*!50003 SET @saved_sql_mode       = @@sql_mode */ ;
/*!50003 SET sql_mode              = 'ONLY_FULL_GROUP_BY,STRICT_TRANS_TABLES,NO_ZERO_IN_DATE,NO_ZERO_DATE,ERROR_FOR_DIVISION_BY_ZERO,NO_ENGINE_SUBSTITUTION' */ ;
DELIMITER ;;
/*!50003 CREATE*/ /*!50017 DEFINER=`avnadmin`@`%`*/ /*!50003 TRIGGER `trg_order_status_check` BEFORE UPDATE ON `orders` FOR EACH ROW BEGIN
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
/*!50003 CREATE*/ /*!50017 DEFINER=`avnadmin`@`%`*/ /*!50003 TRIGGER `trg_order_courier_assignment_check` AFTER UPDATE ON `orders` FOR EACH ROW BEGIN
    DECLARE has_courier1 INT DEFAULT 0;
    DECLARE has_courier2 INT DEFAULT 0;

    
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
  `issue_type` varchar(100) NOT NULL,
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
) ENGINE=InnoDB AUTO_INCREMENT=20 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `report_issues`
--

LOCK TABLES `report_issues` WRITE;
/*!40000 ALTER TABLE `report_issues` DISABLE KEYS */;
INSERT INTO `report_issues` VALUES (1,1516,33,200,NULL,'locker_failed_to_open','Driver reported: locker_failed_to_open','2026-02-24 14:40:52'),(3,NULL,34,200,NULL,'trip_breakdown','Driver reported: trip_breakdown','2026-02-24 16:16:13'),(4,NULL,29,777,NULL,'manual_override','Водитель 200 снят с рейса оператором','2026-03-27 11:16:53');
/*!40000 ALTER TABLE `report_issues` ENABLE KEYS */;
UNLOCK TABLES;

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

LOCK TABLES `stage_orders` WRITE;
/*!40000 ALTER TABLE `stage_orders` DISABLE KEYS */;
INSERT INTO `stage_orders` VALUES (1,NULL,1,'pickup',2,NULL,NULL),(1,NULL,2,'pickup',NULL,NULL,NULL),(1,NULL,3,'pickup',NULL,NULL,NULL);
/*!40000 ALTER TABLE `stage_orders` ENABLE KEYS */;
UNLOCK TABLES;

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
) ENGINE=InnoDB AUTO_INCREMENT=59 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `trips`
--

LOCK TABLES `trips` WRITE;
/*!40000 ALTER TABLE `trips` DISABLE KEYS */;
INSERT INTO `trips` VALUES (1,NULL,'Msk','Spb',1,1,'trip_created',NULL,1,'2025-11-24 16:33:51'),(2,NULL,'LOCAL','LOCAL',1,2,'trip_created',NULL,1,'2025-12-15 18:43:45'),(3,NULL,'LOCAL','LOCAL',1,2,'trip_created',NULL,1,'2025-12-15 19:20:44');
/*!40000 ALTER TABLE `trips` ENABLE KEYS */;
UNLOCK TABLES;

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
) ENGINE=InnoDB AUTO_INCREMENT=1000039 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `users`
--

LOCK TABLES `users` WRITE;
/*!40000 ALTER TABLE `users` DISABLE KEYS */;
INSERT INTO `users` VALUES (1,'User 1','driver','',NULL),(2,'User 2','courier','',NULL),(3,'User 3','client','',NULL);
/*!40000 ALTER TABLE `users` ENABLE KEYS */;
UNLOCK TABLES;

-- Events/routines from legacy dump omitted (DEFINER host-specific; platform tables removed).

/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;
/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;
