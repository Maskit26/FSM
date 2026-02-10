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
) ENGINE=InnoDB AUTO_INCREMENT=66 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `button_states`
--

INSERT  IGNORE INTO `button_states` VALUES (1,'create_order','Создать заказ','client','order_created','active'),(2,'create_order','Создать заказ','client','order_parcel_submitted','inactive'),(3,'open_cell','Открыть ячейку','client','locker_reserved','active'),(4,'open_cell','Открыть ячейку','client','locker_opened','inactive'),(5,'open_cell','Открыть ячейку','client','locker_free','inactive'),(6,'close_cell','Закрыть ячейку','client','locker_opened','active'),(7,'close_cell','Закрыть ячейку','client','locker_parcel_confirmed','active'),(8,'close_cell','Закрыть ячейку','client','locker_parcel_submitted','inactive'),(9,'cancel_order','Отменить заказ','client','order_created','active'),(10,'cancel_order','Отменить заказ','client','order_courier_reserved_post1_and_post2','active'),(11,'cancel_order','Отменить заказ','client','order_completed','inactive'),(12,'pickup_order','Забрать заказ','recipient','order_parcel_submitted','active'),(13,'pickup_order','Забрать заказ','recipient','order_delivered_to_client','inactive'),(14,'open_cell','Открыть ячейку','recipient','locker_parcel_submitted','active'),(15,'open_cell','Открыть ячейку','recipient','locker_opened','inactive'),(16,'close_cell','Закрыть ячейку','recipient','locker_opened','active'),(17,'close_cell','Закрыть ячейку','recipient','locker_free','inactive'),(18,'confirm_pickup','Подтвердить получение','recipient','order_delivered_to_client','active'),(19,'confirm_pickup','Подтвердить получение','recipient','order_completed','inactive'),(20,'take_order','Взять заказ','courier','order_courier_reserved_post1_and_post2','active'),(21,'take_order','Взять заказ','courier','order_courier1_assigned','inactive'),(22,'pickup_from_client','Забрал у клиента','courier','order_courier1_assigned','active'),(23,'pickup_from_client','Забрал у клиента','courier','order_courier_has_parcel','inactive'),(24,'arrived_at_recipient','Прибыл к получателю','courier','order_courier_has_parcel','active'),(25,'arrived_at_recipient','Прибыл к получателю','courier','order_parcel_delivered','inactive'),(26,'open_cell','Открыть ячейку','courier','locker_parcel_submitted','active'),(27,'open_cell','Открыть ячейку','courier','locker_opened','inactive'),(28,'close_cell','Закрыть ячейку','courier','locker_opened','active'),(29,'close_cell','Закрыть ячейку','courier','locker_parcel_confirmed','active'),(30,'cancel_order','Отменить заказ','courier','order_courier1_assigned','active'),(31,'cancel_order','Отменить заказ','courier','order_completed','inactive'),(32,'take_trip','Взять рейс','driver','trip_created','active'),(33,'take_trip','Взять рейс','driver','trip_assigned','inactive'),(34,'arrived_at_locker','Прибыл к постамату','driver','trip_assigned','active'),(35,'arrived_at_locker','Прибыл к постамату','driver','trip_ready_for_pickup','inactive'),(36,'start_trip','Начал путь','driver','trip_ready_for_pickup','active'),(37,'start_trip','Начал путь','driver','trip_in_progress','inactive'),(38,'arrived_destination','Прибыл','driver','trip_in_progress','active'),(39,'arrived_destination','Прибыл','driver','trip_arrived_at_destination','inactive'),(40,'open_cell','Открыть ячейку','driver','locker_reserved','active'),(41,'open_cell','Открыть ячейку','driver','locker_opened','inactive'),(42,'close_cell','Закрыть ячейку','driver','locker_opened','active'),(43,'close_cell','Закрыть ячейку','driver','locker_parcel_submitted','inactive'),(44,'cancel_trip','Отменить рейс','driver','trip_assigned','active'),(45,'cancel_trip','Отменить рейс','driver','trip_completed','inactive'),(46,'assign_courier','Назначить','operator','order_created','active'),(47,'assign_courier','Назначить','operator','order_courier1_assigned','inactive'),(48,'remove_assignment','Снять','operator','order_courier1_assigned','active'),(49,'remove_assignment','Снять','operator','order_created','inactive'),(50,'block_cell','Заблокировать ячейку','operator','locker_free','active'),(51,'block_cell','Заблокировать ячейку','operator','locker_blocked','inactive'),(52,'reserve_cell','Забронировать ячейку','operator','locker_free','active'),(53,'reserve_cell','Забронировать ячейку','operator','locker_reserved','inactive'),(54,'reset_reservation','Снять бронь ячейки (reset)','operator','locker_reserved','active'),(55,'reset_reservation','Снять бронь ячейки (reset)','operator','locker_free','inactive'),(56,'open_cell','Открыть ячейку','operator','locker_reserved','active'),(57,'open_cell','Открыть ячейку','operator','locker_opened','inactive'),(58,'close_cell','Закрыть ячейку','operator','locker_opened','active'),(59,'close_cell','Закрыть ячейку','operator','locker_parcel_submitted','inactive'),(60,'to_maintenance','В ремонт ячейку','operator','locker_free','active'),(61,'to_maintenance','В ремонт ячейку','operator','locker_maintenance','inactive'),(62,'from_maintenance','Снять с ремонта ячейку','operator','locker_maintenance','active'),(63,'from_maintenance','Снять с ремонта ячейку','operator','locker_free','inactive'),(64,'confirm_pickup','','recipient','order_courier2_parcel_delivered','active'),(65,'take_order','Взять заказ','courier','order_created','active');

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
) ENGINE=InnoDB AUTO_INCREMENT=100 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `fsm_action_logs`
--

INSERT  IGNORE INTO `fsm_action_logs` VALUES (44,'order',1429,'order_cancel_reservation','order_created','order_cancelled',1004,'2026-01-13 09:21:40'),(45,'locker',3,'locker_cancel_reservation','locker_reserved','locker_free',1004,'2026-01-13 09:21:40'),(46,'locker',14,'locker_cancel_reservation','locker_reserved','locker_free',1004,'2026-01-13 09:21:40'),(47,'order',1428,'order_cancel_reservation','order_created','order_cancelled',1002,'2026-01-13 11:40:52'),(48,'locker',2,'locker_cancel_reservation','locker_reserved','locker_free',1002,'2026-01-13 11:40:52'),(49,'locker',13,'locker_cancel_reservation','locker_reserved','locker_free',1002,'2026-01-13 11:40:52'),(50,'order',1425,'order_cancel_reservation','order_created','order_cancelled',1003,'2026-01-13 14:16:22'),(51,'locker',43,'locker_cancel_reservation','locker_reserved','locker_free',1003,'2026-01-13 14:16:22'),(52,'locker',45,'locker_cancel_reservation','locker_reserved','locker_free',1003,'2026-01-13 14:16:22'),(53,'order',1436,'order_cancel_reservation','order_created','order_cancelled',1004,'2026-01-13 18:32:38'),(54,'locker',9,'locker_cancel_reservation','locker_reserved','locker_free',1004,'2026-01-13 18:32:38'),(55,'locker',19,'locker_cancel_reservation','locker_reserved','locker_free',1004,'2026-01-13 18:32:38'),(56,'order',1426,'order_cancel_reservation','order_created','order_cancelled',1004,'2026-01-14 10:08:54'),(57,'locker',5,'locker_cancel_reservation','locker_reserved','locker_free',1004,'2026-01-14 10:08:55'),(58,'locker',15,'locker_cancel_reservation','locker_reserved','locker_free',1004,'2026-01-14 10:08:55'),(59,'order',1422,'order_cancel_reservation','order_created','order_cancelled',1001,'2026-01-15 07:41:45'),(60,'locker',6,'locker_cancel_reservation','locker_reserved','locker_free',1001,'2026-01-15 07:41:45'),(61,'locker',16,'locker_cancel_reservation','locker_reserved','locker_free',1001,'2026-01-15 07:41:45'),(62,'order',1421,'order_cancel_reservation','order_created','order_cancelled',1001,'2026-01-15 07:43:50'),(63,'order',1437,'order_cancel_reservation','order_created','order_cancelled',1004,'2026-01-15 07:51:20'),(64,'locker',9,'locker_cancel_reservation','locker_reserved','locker_free',1004,'2026-01-15 07:51:20'),(65,'locker',19,'locker_cancel_reservation','locker_reserved','locker_free',1004,'2026-01-15 07:51:20'),(66,'order',1435,'order_cancel_reservation','order_created','order_cancelled',1003,'2026-01-15 09:46:29'),(67,'locker',43,'locker_cancel_reservation','locker_reserved','locker_free',1003,'2026-01-15 09:46:29'),(68,'locker',45,'locker_cancel_reservation','locker_reserved','locker_free',1003,'2026-01-15 09:46:29'),(69,'order',5,'order_assign_courier1_to_order','order_created','order_courier1_assigned',100,'2026-01-15 10:16:15'),(70,'order',1438,'order_cancel_reservation','order_created','order_cancelled',1001,'2026-01-15 10:27:51'),(71,'locker',5,'locker_cancel_reservation','locker_reserved','locker_free',1001,'2026-01-15 10:27:51'),(72,'locker',15,'locker_cancel_reservation','locker_reserved','locker_free',1001,'2026-01-15 10:27:51'),(73,'order',1417,'order_cancel_reservation','order_created','order_cancelled',1001,'2026-01-15 10:28:51'),(74,'locker',2,'locker_cancel_reservation','locker_reserved','locker_free',1001,'2026-01-15 10:28:51'),(75,'locker',13,'locker_cancel_reservation','locker_reserved','locker_free',1001,'2026-01-15 10:28:51'),(76,'order',5,'order_courier1_cancel','order_courier1_assigned','order_created',100,'2026-01-15 10:37:01'),(77,'order',1407,'order_cancel_reservation','order_created','order_cancelled',1001,'2026-01-15 20:45:18'),(78,'order',1442,'order_assign_courier1_to_order','order_created','order_courier1_assigned',100,'2026-01-15 20:56:19'),(79,'order',1442,'order_courier1_cancel','order_courier1_assigned','order_created',100,'2026-01-15 20:56:49'),(80,'order',5,'order_assign_courier1_to_order','order_created','order_courier1_assigned',100,'2026-01-17 08:36:37'),(81,'order',5,'order_courier1_cancel','order_courier1_assigned','order_created',100,'2026-01-17 09:10:18'),(82,'order',5,'order_assign_courier1_to_order','order_created','order_courier1_assigned',100,'2026-01-17 09:12:03'),(83,'order',5,'order_courier1_cancel','order_courier1_assigned','order_created',100,'2026-01-17 09:19:29'),(84,'order',5,'order_assign_courier1_to_order','order_created','order_courier1_assigned',100,'2026-01-17 09:19:44'),(85,'order',5,'order_courier1_cancel','order_courier1_assigned','order_created',100,'2026-01-17 09:22:39'),(86,'order',1447,'order_cancel_reservation','order_created','order_cancelled',1005,'2026-01-28 15:12:44'),(87,'locker',41,'locker_cancel_reservation','locker_reserved','locker_free',1005,'2026-01-28 15:12:44'),(88,'locker',44,'locker_cancel_reservation','locker_reserved','locker_free',1005,'2026-01-28 15:12:44'),(89,'order',1446,'order_cancel_reservation','order_created','order_cancelled',1004,'2026-01-28 15:12:59'),(90,'locker',43,'locker_cancel_reservation','locker_reserved','locker_free',1004,'2026-01-28 15:12:59'),(91,'locker',45,'locker_cancel_reservation','locker_reserved','locker_free',1004,'2026-01-28 15:12:59'),(92,'order',1503,'order_cancel_reservation','order_created','order_cancelled',1004,'2026-02-05 08:25:26'),(93,'locker',1,'locker_cancel_reservation','locker_reserved','locker_free',1004,'2026-02-05 08:25:26'),(94,'locker',12,'locker_cancel_reservation','locker_reserved','locker_free',1004,'2026-02-05 08:25:26'),(95,'order',1502,'order_assign_courier1_to_order','order_created','order_courier1_assigned',100,'2026-02-05 09:11:47'),(96,'order',1508,'order_assign_courier1_to_order','order_created','order_courier1_assigned',100,'2026-02-08 14:16:14'),(97,'order',1508,'order_courier1_cancel','order_courier1_assigned','order_created',100,'2026-02-08 14:16:54'),(98,'order',1508,'order_assign_courier1_to_order','order_created','order_courier1_assigned',100,'2026-02-08 14:17:49'),(99,'order',1508,'order_courier1_cancel','order_courier1_assigned','order_created',100,'2026-02-08 14:18:09');

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
) ENGINE=InnoDB AUTO_INCREMENT=107 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `fsm_actions`
--

INSERT  IGNORE INTO `fsm_actions` VALUES (1,'locker_reserve_cell','Zabronirovat yacheyku'),(2,'trip_assign_voditel','Naznachit voditelya'),(3,'trip_start_trip','Nachat poyezdku'),(4,'trip_complete_trip','Zavershit poyezdku'),(5,'locker_open_locker','Otkryt yacheyku'),(6,'locker_close_locker','Zakryt yacheyku'),(7,'order_timeout_reservation','Taymaut rezervirovaniya'),(8,'locker_confirm_parcel_in','Podtverdit posylku vnutri'),(49,'order_assign_courier1_to_order','Naznachit Kurer1 na zakaz'),(61,'order_timeout_confirmation','Taymaut podtverzhdeniya'),(68,'order_client_will_deliver','Klient sam sdast posylku'),(69,'order_confirm_parcel_in','Подтвердить посылку (Order)'),(70,'order_parcel_submitted','Посылка сдана (Order)'),(71,'order_courier_pickup_parcel','Kurer zabral posilku'),(72,'locker_reset','sbros yacheiki'),(73,'locker_set_locker_to_maintenance','perevesti v obsluzhivanie'),(74,'order_cancel_reservation','otmenit rezervatsiyu'),(75,'locker_confirm_parcel_not_found','posylka_ne_naidena'),(76,'locker_cancel_reservation','otmena rezervatsii yacheiki'),(77,'trip_start_pickup','nachat_zabir'),(78,'trip_confirm_pickup','podtverdit_zabir'),(79,'trip_confirm_delivery','podtverdit_dostavku'),(80,'trip_end_delivery','zavershit_dostavku'),(81,'order_reserve_for_client_A_to_B','zarezervirovat_dlya_klienta_A_to_B'),(82,'order_reserve_for_courier_A_to_B','zarezervirovat_dlya_kurera_A_to_B'),(83,'order_pickup_by_voditel','voditel_zabral_posylku'),(84,'order_start_transit','nachat_perevozku'),(85,'order_arrive_at_post2','pridyal_k_post2'),(86,'locker_confirm_parcel_out','Podtverdit poluchenie posylki iz yacheiki'),(87,'locker_dont_closed','Yacheika ne zakryta posle raboty'),(88,'order_pickup_poluchatel','Klient poluchil posylku'),(89,'order_delivered_parcel','Zavershit zakaz posle polucheniya'),(90,'order_assign_courier2_to_order','Naznachit kurera2'),(91,'order_courier2_pickup_parcel','Kurer2 zabral iz post2'),(92,'order_courier2_delivered_parcel','Kurer2 zavershil dostavku'),(93,'order_report_parcel_missing','Posylka ne naidena v yacheike'),(94,'order_report_delivery_failed','Soobshchit o neudache dostavki'),(95,'order_request_manual_intervention','Zaprosit ruchnoe vmeshatelstvo'),(96,'trip_report_driver_not_found','Soobshchit: voditel ne naiden'),(97,'trip_report_failure','Soobshchit o sbue poezdki'),(98,'trip_request_manual_intervention','Zaprosit ruchnoe vmeshatelstvo'),(99,'order_courier1_cancel','Kurer1 otmenil do zabora'),(100,'order_courier2_cancel','Kurer2 otmenil do zabora iz post2'),(101,'order_timeout_no_pickup','Taymaut: kurer ne zabral posylku'),(102,'trip_vzyat_reis','Vzyat reis'),(103,'locker_confirm_parcel_out_recipient','Podtverdit vydachu poluchatelyu iz yacheiki'),(104,'order_recipient_confirmed','Klient podtverdil poluchenie'),(105,'locker_close_pickup',NULL),(106,'locker_failed_to_open','Ne otkrilas yacheika');

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

INSERT  IGNORE INTO `fsm_states` VALUES (1,'order_created','Sozdan'),(3,'trip_assigned','Naznachen'),(4,'trip_in_progress','V puti'),(5,'trip_completed','Zavershon'),(6,'locker_reserved','Yacheika zarezervirovana'),(7,'locker_opened','Yacheika otkryta'),(8,'order_parcel_submitted','Posylka sdana'),(49,'order_courier1_assigned','Kurer1 naznachen'),(60,'order_parcel_confirmed','Posylka podtverzhdena'),(61,'order_parcel_missing','Posylka ne naidena'),(68,'locker_free','Yacheika svobodna'),(69,'locker_occupied','Yacheika zanyata'),(70,'locker_error','Oshibka yacheiki'),(71,'locker_maintenance','Na obsluzhivanii'),(72,'locker_parcel_submitted','Posylka sdana'),(73,'locker_parcel_confirmed','Posylka podtverzhdena'),(74,'locker_parcel_missing','Posylka ne naidena'),(75,'order_courier_has_parcel','Kurer zabral posilku'),(76,'order_reservation_expired','rezervatsiya zavershena po taymautu'),(77,'order_courier_failed','kurer ne podtverdil zabir'),(78,'order_cancelled','zakaz otmenen klientom'),(79,'locker_closed_empty','yacheyka zakryta pustaya'),(80,'trip_ready_for_pickup','gotov_zabrat'),(81,'trip_parcel_picked_up','posylka_zabirana'),(82,'trip_arrived_at_destination','pridyal_k_meste'),(83,'trip_parcel_delivered','posylka_sdana'),(84,'order_client_reserved_post1_and_post2','klient_zarezerviroval_1_i_2'),(85,'order_courier_reserved_post1_and_post2','kurer_zarezerviroval_1_i_2'),(87,'order_picked_up_from_post1','posylka_zabrana_iz_post1'),(88,'order_in_transit_to_post2','v_perevozke_k_post2'),(89,'order_arrived_at_post2','dostavlena_v_post2'),(90,'order_delivered_to_client','Posylka poluchena klientom'),(91,'order_courier2_assigned','Kurer2 naznachen'),(92,'order_courier2_has_parcel','Kurer2 zabral posylku'),(93,'order_completed','Zakaz zavershon'),(94,'order_delivery_failed','Dostavka ne udalas'),(95,'order_manual_intervention_required','Trebuetsya ruchnoe vmeshatelstvo'),(96,'trip_driver_not_found','Voditel ne naiden'),(97,'trip_failed','Poezdka prervana'),(98,'trip_manual_intervention_required','Trebuetsya ruchnoe vmeshatelstvo'),(99,'trip_created','Reis sozdan'),(100,'locker_parcel_pickup_driver','posilku zabral voditel'),(101,'locker_parcel_pickup_recipient','Poluchatel zabral posilku'),(102,'order_courier2_parcel_delivered','Kurer2 dostavil klientu, ojidaem podtverzhdeniya'),(103,'order_parcel_confirmed_post2','Posylka podtverzhdena v postamate2');

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
) ENGINE=InnoDB AUTO_INCREMENT=134 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `fsm_transitions`
--

INSERT  IGNORE INTO `fsm_transitions` VALUES (29,60,70,8),(30,68,1,6),(31,6,5,7),(36,75,69,60),(38,49,71,75),(42,49,61,77),(47,70,72,68),(48,71,72,68),(49,79,72,68),(50,74,6,79),(51,68,73,71),(52,7,75,74),(53,6,76,68),(54,70,73,71),(55,3,2,80),(56,80,78,81),(57,81,3,4),(58,82,79,83),(59,83,4,5),(60,4,80,5),(61,73,6,69),(62,69,5,7),(63,79,76,68),(64,1,81,84),(65,1,82,85),(66,84,69,60),(68,84,7,76),(69,85,7,76),(71,84,74,78),(72,85,74,78),(74,8,83,87),(75,87,84,88),(76,88,85,89),(77,89,69,103),(79,7,87,70),(80,103,88,90),(81,90,89,93),(82,103,90,91),(83,91,91,92),(84,92,92,102),(85,60,93,61),(86,75,94,94),(87,88,94,94),(88,92,94,94),(89,1,95,95),(90,49,95,95),(91,60,95,95),(92,75,95,95),(93,84,95,95),(94,85,95,95),(95,87,95,95),(96,88,95,95),(97,89,95,95),(98,90,95,95),(99,91,95,95),(100,92,95,95),(101,3,96,96),(102,3,97,97),(103,4,97,97),(104,80,97,97),(105,81,97,97),(106,82,97,97),(109,3,98,98),(110,4,98,98),(111,80,98,98),(112,81,98,98),(113,82,98,98),(114,83,98,98),(116,49,99,1),(117,49,101,1),(118,91,100,89),(119,91,101,89),(120,99,102,3),(121,7,86,100),(122,100,6,79),(123,7,103,101),(124,101,6,79),(125,102,104,93),(126,7,6,69),(127,7,105,79),(128,103,93,61),(129,103,95,95),(130,1,49,49),(131,6,106,70),(132,1,74,78),(133,3,97,99);

--
-- Table structure for table `hardware_command_log`
--

DROP TABLE IF EXISTS `hardware_command_log`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `hardware_command_log` (
  `id` int NOT NULL AUTO_INCREMENT,
  `command` varchar(50) NOT NULL,
  `target` varchar(50) NOT NULL,
  `success` tinyint(1) DEFAULT NULL,
  `response` text,
  `executed_at` datetime DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `hardware_command_log`
--


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
  `reservation_expires_at` datetime DEFAULT NULL,
  `code_expires_at` datetime DEFAULT NULL,
  `unlock_code` char(6) DEFAULT NULL,
  `reserved_for_user_id` int DEFAULT NULL,
  `current_order_id` int DEFAULT NULL,
  `failed_open_attempts` int DEFAULT '0',
  `created_at` datetime DEFAULT CURRENT_TIMESTAMP,
  `updated_at` datetime DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  UNIQUE KEY `locker_id` (`locker_id`,`cell_code`),
  UNIQUE KEY `unique_unlock_code` (`unlock_code`),
  CONSTRAINT `locker_cells_ibfk_1` FOREIGN KEY (`locker_id`) REFERENCES `lockers` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=46 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `locker_cells`
--

INSERT  IGNORE INTO `locker_cells` VALUES (1,1,'S-01','S','locker_reserved',NULL,NULL,NULL,NULL,NULL,0,'2025-11-22 15:23:13','2026-02-06 05:52:52'),(2,1,'S-02','S','locker_reserved',NULL,NULL,NULL,NULL,NULL,0,'2025-11-22 15:23:13','2026-02-06 05:53:12'),(3,1,'S-03','S','locker_reserved',NULL,NULL,NULL,NULL,NULL,0,'2025-11-22 15:23:13','2026-02-06 05:53:32'),(4,1,'S-04','S','locker_free',NULL,NULL,NULL,NULL,NULL,0,'2025-11-22 15:23:13','2025-12-15 19:56:28'),(5,1,'M-01','M','locker_reserved',NULL,NULL,NULL,NULL,NULL,0,'2025-11-22 15:23:13','2026-02-05 09:06:17'),(6,1,'M-02','M','locker_reserved',NULL,NULL,NULL,NULL,NULL,0,'2025-11-22 15:23:13','2026-02-08 13:22:43'),(7,1,'L-01','L','locker_free',NULL,NULL,NULL,NULL,NULL,0,'2025-11-22 15:23:13','2026-01-28 11:47:47'),(8,1,'L-02','L','locker_free',NULL,NULL,NULL,NULL,NULL,0,'2025-11-22 15:23:13','2026-01-28 11:47:47'),(9,1,'P-01','P','locker_free',NULL,NULL,NULL,NULL,NULL,0,'2025-11-22 15:23:13','2026-01-28 11:47:47'),(10,1,'P-02','P','locker_free',NULL,NULL,NULL,NULL,NULL,0,'2025-11-22 15:23:13','2026-01-28 11:47:47'),(11,2,'S-01','S','locker_reserved',NULL,NULL,NULL,NULL,1449,0,'2025-11-22 15:23:13','2026-02-04 15:52:58'),(12,2,'S-02','S','locker_reserved',NULL,NULL,NULL,NULL,NULL,0,'2025-11-22 15:23:13','2026-02-06 05:52:52'),(13,2,'S-03','S','locker_reserved',NULL,NULL,NULL,NULL,NULL,0,'2025-11-22 15:23:13','2026-02-06 05:53:12'),(14,2,'S-04','S','locker_reserved',NULL,NULL,NULL,NULL,NULL,0,'2025-11-22 15:23:13','2026-02-06 05:53:32'),(15,2,'M-01','M','locker_reserved',NULL,NULL,NULL,NULL,NULL,0,'2025-11-22 15:23:13','2026-02-05 09:06:17'),(16,2,'M-02','M','locker_reserved',NULL,NULL,NULL,NULL,NULL,0,'2025-11-22 15:23:13','2026-02-08 13:22:43'),(17,2,'L-01','L','locker_free',NULL,NULL,NULL,NULL,NULL,0,'2025-11-22 15:23:13','2026-01-28 11:47:47'),(18,2,'L-02','L','locker_free',NULL,NULL,NULL,NULL,NULL,0,'2025-11-22 15:23:13','2026-01-28 11:47:47'),(19,2,'P-01','P','locker_free',NULL,NULL,NULL,NULL,NULL,0,'2025-11-22 15:23:13','2026-01-28 11:47:47'),(20,2,'P-02','P','locker_free',NULL,NULL,NULL,NULL,NULL,0,'2025-11-22 15:23:13','2026-01-28 11:47:47'),(21,3,'S-01','S','locker_free',NULL,NULL,NULL,NULL,NULL,0,'2025-11-22 15:23:13','2025-11-22 15:23:13'),(22,3,'S-02','S','locker_free',NULL,NULL,NULL,NULL,NULL,0,'2025-11-22 15:23:13','2025-11-22 15:23:13'),(23,3,'S-03','S','locker_free',NULL,NULL,NULL,NULL,NULL,0,'2025-11-22 15:23:13','2025-11-22 15:23:13'),(24,3,'S-04','S','locker_free',NULL,NULL,NULL,NULL,NULL,0,'2025-11-22 15:23:13','2025-11-22 15:23:13'),(25,3,'M-01','M','locker_free',NULL,NULL,NULL,NULL,NULL,0,'2025-11-22 15:23:13','2025-11-22 15:23:13'),(26,3,'M-02','M','locker_free',NULL,NULL,NULL,NULL,NULL,0,'2025-11-22 15:23:13','2025-11-22 15:23:13'),(27,3,'L-01','L','locker_free',NULL,NULL,NULL,NULL,NULL,0,'2025-11-22 15:23:13','2025-11-22 15:23:13'),(28,3,'L-02','L','locker_free',NULL,NULL,NULL,NULL,NULL,0,'2025-11-22 15:23:13','2025-11-22 15:23:13'),(29,3,'P-01','P','locker_free',NULL,NULL,NULL,NULL,NULL,0,'2025-11-22 15:23:13','2025-11-22 15:23:13'),(30,3,'P-02','P','locker_free',NULL,NULL,NULL,NULL,NULL,0,'2025-11-22 15:23:13','2025-11-22 15:23:13'),(31,4,'S-01','S','locker_free',NULL,NULL,NULL,NULL,NULL,0,'2025-11-22 15:23:13','2025-11-22 15:23:13'),(32,4,'S-02','S','locker_free',NULL,NULL,NULL,NULL,NULL,0,'2025-11-22 15:23:13','2025-11-22 15:23:13'),(33,4,'S-03','S','locker_free',NULL,NULL,NULL,NULL,NULL,0,'2025-11-22 15:23:13','2025-11-22 15:23:13'),(34,4,'S-04','S','locker_free',NULL,NULL,NULL,NULL,NULL,0,'2025-11-22 15:23:13','2025-11-22 15:23:13'),(35,4,'M-01','M','locker_free',NULL,NULL,NULL,NULL,NULL,0,'2025-11-22 15:23:13','2025-11-22 15:23:13'),(36,4,'M-02','M','locker_free',NULL,NULL,NULL,NULL,NULL,0,'2025-11-22 15:23:13','2025-11-22 15:23:13'),(37,4,'L-01','L','locker_free',NULL,NULL,NULL,NULL,NULL,0,'2025-11-22 15:23:13','2025-11-22 15:23:13'),(38,4,'L-02','L','locker_free',NULL,NULL,NULL,NULL,NULL,0,'2025-11-22 15:23:13','2025-11-22 15:23:13'),(39,4,'P-01','P','locker_free',NULL,NULL,NULL,NULL,NULL,0,'2025-11-22 15:23:13','2025-11-22 15:23:13'),(40,4,'P-02','P','locker_free',NULL,NULL,NULL,NULL,NULL,0,'2025-11-22 15:23:13','2025-11-22 15:23:13'),(41,1,'A01','S','locker_reserved',NULL,NULL,NULL,NULL,1448,0,'2025-11-23 20:39:10','2026-01-29 08:12:40'),(42,1,'A02','S','locker_reserved',NULL,NULL,NULL,NULL,1449,0,'2025-11-23 20:39:10','2026-02-04 15:52:58'),(43,1,'A03','M','locker_reserved',NULL,NULL,NULL,NULL,1446,0,'2025-11-23 20:39:10','2026-02-05 07:58:29'),(44,2,'B01','S','locker_reserved',NULL,NULL,NULL,NULL,1448,0,'2025-11-23 20:39:10','2026-01-29 08:12:40'),(45,2,'B02','M','locker_reserved',NULL,NULL,NULL,NULL,1446,0,'2025-11-23 20:39:10','2026-02-05 07:58:29');
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

INSERT  IGNORE INTO `locker_models` VALUES (1,'Model-Post1',NULL,10,5,2,1,'2025-10-29 17:20:54'),(2,'Model-2',NULL,10,5,2,1,'2025-11-21 13:37:49'),(3,'Model-3',NULL,10,5,2,1,'2025-11-21 13:37:49');

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

INSERT  IGNORE INTO `lockers` VALUES (1,1,'POST1','МСК','Точка #1',NULL,NULL,'locker_inactive','2025-11-22 15:22:48'),(2,1,'POST2','СПБ','Точка #2',NULL,NULL,'locker_inactive','2025-11-22 15:22:48'),(3,1,'POST3','МСК','Точка #3',NULL,NULL,'locker_inactive','2025-11-22 15:22:48'),(4,1,'POST4','СПБ','Точка #4',NULL,NULL,'locker_inactive','2025-11-22 15:22:48');

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
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=214 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `order_requests`
--

INSERT  IGNORE INTO `order_requests` VALUES (1,0,'string','string','string','string','FAILED',NULL,'NOT_IMPLEMENTED','order_creation handler not implemented yet','2025-12-07 13:53:25'),(2,0,'string','string','string','string','FAILED',NULL,'NO_FREE_CELLS','Не найдены свободные ячейки нужного размера','2025-12-07 16:37:12'),(3,1005,'test','S','courier','courier','COMPLETED',6,NULL,NULL,'2025-12-07 16:45:30'),(4,1006,'test','L','courier','courier','COMPLETED',7,NULL,NULL,'2025-12-07 16:54:49'),(5,1007,'test','M','courier','courier','COMPLETED',8,NULL,NULL,'2025-12-07 17:08:22'),(6,1008,'test','M','courier','courier','COMPLETED',9,NULL,NULL,'2025-12-07 17:17:26'),(7,1009,'test','L','courier','courier','COMPLETED',10,NULL,NULL,'2025-12-07 17:19:20'),(8,402,'documents','M','courier','courier','FAILED',NULL,'NO_FREE_CELLS','Не найдены свободные ячейки нужного размера','2025-12-11 09:43:29'),(9,391,'documents','S','courier','courier','COMPLETED',660,NULL,NULL,'2025-12-12 08:32:33'),(10,491,'documents','M','courier','courier','FAILED',NULL,'NO_FREE_CELLS','Не найдены свободные ячейки нужного размера','2025-12-12 09:38:45'),(11,471,'documents','L','courier','courier','FAILED',NULL,'NO_FREE_CELLS','Не найдены свободные ячейки нужного размера','2025-12-12 09:39:44'),(12,461,'documents','S','courier','courier','FAILED',NULL,'NO_FREE_CELLS','Не найдены свободные ячейки нужного размера','2025-12-12 09:46:20'),(13,467,'documents','P','courier','courier','COMPLETED',661,NULL,NULL,'2025-12-12 09:55:53'),(14,463,'documents','А','courier','courier','FAILED',NULL,'NO_FREE_CELLS','Не найдены свободные ячейки нужного размера','2025-12-12 10:16:43'),(15,493,'documents','P','courier','courier','COMPLETED',662,NULL,NULL,'2025-12-12 10:50:14'),(16,589,'documents','P','courier','courier','FAILED',NULL,'NO_FREE_CELLS','Не найдены свободные ячейки нужного размера','2025-12-12 12:40:43'),(17,559,'documents','P','courier','courier','FAILED',NULL,'NO_FREE_CELLS','Не найдены свободные ячейки нужного размера','2025-12-12 13:32:58'),(18,584,'documents','P','courier','courier','FAILED',NULL,'NO_FREE_CELLS','Не найдены свободные ячейки нужного размера','2025-12-12 14:22:45'),(19,544,'documents','S','courier','courier','FAILED',NULL,'NO_FREE_CELLS','Не найдены свободные ячейки нужного размера','2025-12-12 16:06:43'),(20,591,'documents','S','courier','courier','FAILED',NULL,'NO_FREE_CELLS','Не найдены свободные ячейки нужного размера','2025-12-12 16:21:18'),(21,1,'Документы','S','courier','courier','COMPLETED',1361,NULL,NULL,'2025-12-15 17:31:14'),(22,1,'Финальный тест','S','courier','courier','COMPLETED',1362,NULL,NULL,'2025-12-15 19:20:14'),(23,1,'Заказ A','S','courier','courier','FAILED',NULL,'TEST_CLEANUP','Не найдены свободные ячейки нужного размера','2025-12-15 19:41:42'),(24,1,'Заказ B','S','courier','courier','FAILED',NULL,'TEST_CLEANUP','Не найдены свободные ячейки нужного размера','2025-12-15 19:41:42'),(25,1,'Заказ A','S','courier','courier','FAILED',NULL,'NO_FREE_CELLS','Не найдены свободные ячейки нужного размера','2025-12-15 19:50:09'),(26,1,'Заказ B','S','courier','courier','FAILED',NULL,'NO_FREE_CELLS','Не найдены свободные ячейки нужного размера','2025-12-15 19:50:09'),(27,1,'Заказ 1','S','courier','courier','FAILED',1364,NULL,NULL,'2025-12-15 19:56:56'),(28,1,'Заказ 2','S','courier','courier','FAILED',1365,NULL,NULL,'2025-12-15 19:56:56'),(29,1,'Тест А','S','courier','courier','COMPLETED',1366,NULL,NULL,'2025-12-15 20:33:22'),(30,1,'Тест Б','S','courier','courier','COMPLETED',1367,NULL,NULL,'2025-12-15 20:33:22'),(31,1,'Проверка trip 2','S','courier','courier','COMPLETED',1368,NULL,NULL,'2025-12-15 20:46:10'),(32,1,'Debug test','S','courier','courier','COMPLETED',1369,NULL,NULL,'2025-12-16 06:00:28'),(33,1,'Test trip 3','S','courier','courier','COMPLETED',1370,NULL,NULL,'2025-12-16 06:04:57'),(34,1,'Тест 1','S','courier','courier','PENDING',NULL,NULL,NULL,'2025-12-16 06:48:21'),(35,1,'Тест 2','S','courier','courier','COMPLETED',1371,NULL,NULL,'2025-12-16 06:48:21'),(36,1,'Тест 3','S','courier','courier','COMPLETED',1372,NULL,NULL,'2025-12-16 06:48:21'),(37,1,'Тест 4','S','courier','courier','COMPLETED',1373,NULL,NULL,'2025-12-16 06:48:21'),(38,1,'Тест 5','S','courier','courier','FAILED',NULL,'NO_FREE_CELLS','Не найдены свободные ячейки нужного размера','2025-12-16 06:48:21'),(39,1,'Тест 1→2 A','S','courier','courier','PENDING',NULL,NULL,NULL,'2025-12-16 10:00:14'),(40,1,'Тест 1→2 B','S','courier','courier','PENDING',NULL,NULL,NULL,'2025-12-16 10:00:14'),(41,1,'Тест локер A','S','courier','courier','COMPLETED',1374,NULL,NULL,'2025-12-16 10:02:26'),(42,1,'Тест локер B','S','courier','courier','COMPLETED',1375,NULL,NULL,'2025-12-16 10:02:26'),(43,1,'документы','S','courier','courier','COMPLETED',1377,NULL,NULL,'2025-12-19 09:45:06'),(44,1,'документы','S','courier','courier','COMPLETED',1378,NULL,NULL,'2025-12-19 09:53:15'),(45,1,'документы','M','courier','courier','COMPLETED',1379,NULL,NULL,'2025-12-19 12:04:27'),(46,1001,'parcel','S','courier','courier','COMPLETED',1380,NULL,NULL,'2025-12-23 16:35:09'),(47,1001,'parcel','S','courier','courier','COMPLETED',1381,NULL,NULL,'2025-12-24 11:50:30'),(48,1001,'parcel','S','courier','courier','COMPLETED',1382,NULL,NULL,'2025-12-24 11:52:18'),(49,1001,'parcel','S','courier','courier','COMPLETED',1383,NULL,NULL,'2025-12-24 11:54:15'),(50,1001,'parcel','S','courier','courier','FAILED',NULL,'NO_FREE_CELLS','Не найдены свободные ячейки нужного размера','2025-12-24 12:00:31'),(51,1001,'parcel','M','courier','courier','COMPLETED',1384,NULL,NULL,'2025-12-24 12:04:50'),(52,1001,'parcel','M','courier','courier','COMPLETED',1385,NULL,NULL,'2025-12-24 12:05:22'),(53,1001,'parcel','S','courier','courier','FAILED',NULL,'NO_FREE_CELLS','Не найдены свободные ячейки нужного размера','2025-12-24 12:21:46'),(54,1001,'parcel','S','courier','self','FAILED',NULL,'NO_FREE_CELLS','Не найдены свободные ячейки нужного размера','2025-12-24 12:24:07'),(55,1001,'letter','P','courier','self','COMPLETED',1386,NULL,NULL,'2025-12-24 12:24:20'),(56,1001,'parcel','S','courier','courier','FAILED',NULL,'NO_FREE_CELLS','Не найдены свободные ячейки нужного размера','2025-12-24 12:31:53'),(57,1001,'parcel','S','courier','courier','FAILED',NULL,'NO_FREE_CELLS','Не найдены свободные ячейки нужного размера','2025-12-24 12:32:29'),(58,1001,'parcel','S','courier','courier','FAILED',NULL,'NO_FREE_CELLS','Не найдены свободные ячейки нужного размера','2025-12-24 12:32:50'),(59,1001,'parcel','S','courier','courier','FAILED',NULL,'NO_FREE_CELLS','Не найдены свободные ячейки нужного размера','2025-12-24 12:35:26'),(60,1001,'letter','P','courier','courier','COMPLETED',1387,NULL,NULL,'2025-12-24 12:35:33'),(61,1001,'parcel','S','courier','courier','FAILED',NULL,'NO_FREE_CELLS','Не найдены свободные ячейки нужного размера','2025-12-24 12:37:24'),(62,1001,'parcel','S','courier','courier','FAILED',NULL,'NO_FREE_CELLS','Не найдены свободные ячейки нужного размера','2025-12-24 12:37:39'),(63,1001,'letter','P','courier','courier','FAILED',NULL,'NO_FREE_CELLS','Не найдены свободные ячейки нужного размера','2025-12-24 12:37:53'),(64,1001,'parcel','S','courier','courier','FAILED',NULL,'NO_FREE_CELLS','Не найдены свободные ячейки нужного размера','2025-12-24 12:44:17'),(65,1001,'parcel','S','courier','courier','FAILED',NULL,'NO_FREE_CELLS','Не найдены свободные ячейки нужного размера','2025-12-24 12:50:17'),(66,1001,'parcel','L','courier','self','COMPLETED',1388,NULL,NULL,'2025-12-24 12:53:55'),(67,1001,'parcel','M','courier','courier','FAILED',NULL,'NO_FREE_CELLS','Не найдены свободные ячейки нужного размера','2025-12-24 14:27:35'),(68,1001,'parcel','M','courier','courier','COMPLETED',1389,NULL,NULL,'2025-12-24 15:36:48'),(69,1001,'parcel','M','courier','courier','COMPLETED',1390,NULL,NULL,'2025-12-24 15:40:47'),(70,1001,'parcel','M','courier','courier','COMPLETED',1391,NULL,NULL,'2025-12-24 15:40:59'),(71,1001,'parcel','L','courier','courier','COMPLETED',1392,NULL,NULL,'2025-12-24 15:42:42'),(72,1001,'parcel','S','courier','courier','COMPLETED',1393,NULL,NULL,'2025-12-25 15:18:01'),(73,1001,'parcel','S','courier','courier','COMPLETED',1394,NULL,NULL,'2025-12-25 15:20:26'),(74,1001,'parcel','S','courier','courier','COMPLETED',1395,NULL,NULL,'2025-12-25 15:23:40'),(75,1001,'parcel','S','courier','courier','COMPLETED',1396,NULL,NULL,'2025-12-25 15:26:12'),(76,1001,'parcel','S','courier','courier','COMPLETED',1397,NULL,NULL,'2025-12-25 15:28:13'),(77,1001,'parcel','S','courier','courier','FAILED',NULL,'NO_FREE_CELLS','Не найдены свободные ячейки нужного размера','2025-12-26 10:11:33'),(78,1001,'parcel','S','courier','courier','FAILED',NULL,'NO_FREE_CELLS','Не найдены свободные ячейки нужного размера','2025-12-26 10:14:03'),(79,1001,'parcel','S','courier','courier','FAILED',NULL,'NO_FREE_CELLS','Не найдены свободные ячейки нужного размера','2025-12-26 10:34:33'),(80,1002,'parcel','L','courier','self','COMPLETED',1398,NULL,NULL,'2025-12-26 12:26:18'),(81,1,'documents','S','courier','self','COMPLETED',1399,NULL,NULL,'2025-12-26 13:18:51'),(82,1,'documents','M','courier','self','COMPLETED',1400,NULL,NULL,'2025-12-26 13:38:36'),(83,3,'documents','M','courier','self','COMPLETED',1401,NULL,NULL,'2025-12-26 16:14:27'),(84,1002,'parcel','S','courier','self','COMPLETED',1402,NULL,NULL,'2025-12-26 16:45:47'),(85,1001,'parcel','S','courier','courier','COMPLETED',1403,NULL,NULL,'2025-12-26 17:11:36'),(86,1001,'parcel','S','courier','courier','COMPLETED',1404,NULL,NULL,'2025-12-27 15:09:28'),(87,1001,'parcel','S','courier','courier','COMPLETED',1405,NULL,NULL,'2025-12-27 15:13:30'),(88,1001,'parcel','S','courier','courier','COMPLETED',1406,NULL,NULL,'2025-12-27 15:14:23'),(89,1001,'parcel','S','self','courier','FAILED',NULL,'NO_FREE_CELLS','Не найдены свободные ячейки нужного размера','2025-12-27 15:29:29'),(90,1001,'parcel','S','courier','courier','FAILED',NULL,'NO_FREE_CELLS','Не найдены свободные ячейки нужного размера','2025-12-27 15:30:18'),(91,1001,'parcel','M','courier','courier','COMPLETED',1407,NULL,NULL,'2025-12-27 16:55:39'),(92,1001,'parcel','S','courier','courier','FAILED',NULL,'NO_FREE_CELLS','Не найдены свободные ячейки нужного размера','2025-12-29 17:34:49'),(93,1001,'parcel','S','courier','courier','FAILED',NULL,'NO_FREE_CELLS','Не найдены свободные ячейки нужного размера','2025-12-29 17:34:49'),(94,1001,'parcel','S','courier','courier','FAILED',NULL,'NO_FREE_CELLS','Не найдены свободные ячейки нужного размера','2025-12-29 17:34:50'),(95,1001,'parcel','S','courier','self','FAILED',NULL,'NO_FREE_CELLS','Не найдены свободные ячейки нужного размера','2025-12-30 14:03:58'),(96,1002,'parcel','S','courier','self','FAILED',NULL,'NO_FREE_CELLS','Не найдены свободные ячейки нужного размера','2025-12-30 17:00:52'),(97,1001,'parcel','S','courier','courier','FAILED',NULL,'NO_FREE_CELLS','Не найдены свободные ячейки нужного размера','2025-12-30 17:03:17'),(98,1001,'parcel','S','courier','self','FAILED',NULL,'NO_FREE_CELLS','Не найдены свободные ячейки нужного размера','2025-12-30 17:09:41'),(99,1001,'parcel','S','courier','courier','FAILED',NULL,'NO_FREE_CELLS','Не найдены свободные ячейки нужного размера','2025-12-30 17:10:22'),(100,1001,'parcel','S','courier','courier','FAILED',NULL,'NO_FREE_CELLS','Не найдены свободные ячейки нужного размера','2025-12-30 17:49:29'),(101,1001,'parcel','S','courier','courier','FAILED',NULL,'NO_FREE_CELLS','Не найдены свободные ячейки нужного размера','2025-12-30 17:52:06'),(102,1001,'parcel','S','courier','self','FAILED',NULL,'NO_FREE_CELLS','Не найдены свободные ячейки нужного размера','2025-12-30 19:43:43'),(103,1001,'parcel','S','courier','self','FAILED',NULL,'NO_FREE_CELLS','Не найдены свободные ячейки нужного размера','2025-12-30 19:49:57'),(104,1001,'parcel_small','M','courier','courier','FAILED',NULL,'NO_FREE_CELLS','Не найдены свободные ячейки нужного размера','2025-12-31 09:50:17'),(105,1001,'parcel','S','courier','courier','FAILED',NULL,'NO_FREE_CELLS','Не найдены свободные ячейки нужного размера','2025-12-31 11:09:27'),(106,1001,'parcel','S','courier','courier','COMPLETED',1408,NULL,NULL,'2025-12-31 11:19:12'),(107,1001,'parcel','S','courier','courier','COMPLETED',1409,NULL,NULL,'2026-01-01 13:22:50'),(108,1001,'parcel','S','courier','courier','COMPLETED',1410,NULL,NULL,'2026-01-01 13:23:50'),(109,1001,'parcel','S','courier','courier','COMPLETED',1411,NULL,NULL,'2026-01-02 10:48:14'),(110,1001,'parcel','S','courier','courier','COMPLETED',1412,NULL,NULL,'2026-01-02 11:09:22'),(111,1002,'parcel','S','courier','courier','FAILED',NULL,'NO_FREE_CELLS','Не найдены свободные ячейки нужного размера','2026-01-02 11:09:34'),(112,1001,'parcel','S','courier','courier','FAILED',NULL,'NO_FREE_CELLS','Не найдены свободные ячейки нужного размера','2026-01-02 11:54:29'),(113,1001,'parcel','S','courier','courier','FAILED',NULL,'NO_FREE_CELLS','Не найдены свободные ячейки нужного размера','2026-01-02 11:55:42'),(114,1001,'parcel','S','courier','courier','FAILED',NULL,'NO_FREE_CELLS','Не найдены свободные ячейки нужного размера','2026-01-02 13:58:06'),(115,1001,'parcel','S','courier','courier','FAILED',NULL,'NO_FREE_CELLS','Не найдены свободные ячейки нужного размера','2026-01-02 14:15:23'),(116,1003,'parcel','M','courier','courier','PENDING',NULL,NULL,NULL,'2026-01-06 13:15:59'),(117,1003,'parcel','L','courier','courier','COMPLETED',1413,NULL,NULL,'2026-01-06 15:00:13'),(118,1001,'parcel','S','courier','courier','COMPLETED',1414,NULL,NULL,'2026-01-09 17:03:26'),(119,0,'string','string','string','string','FAILED',NULL,'NO_FREE_CELLS','Не найдены свободные ячейки нужного размера','2026-01-09 17:41:53'),(120,1001,'parcel','S','courier','courier','COMPLETED',1415,NULL,NULL,'2026-01-09 18:09:14'),(121,1001,'parcel','S','courier','courier','COMPLETED',1416,NULL,NULL,'2026-01-09 18:09:48'),(122,1001,'parcel','S','courier','courier','COMPLETED',1417,NULL,NULL,'2026-01-09 18:15:57'),(123,1001,'parcel','S','courier','courier','COMPLETED',1418,NULL,NULL,'2026-01-09 18:17:30'),(124,0,'string','string','string','string','FAILED',NULL,'NO_FREE_CELLS','Не найдены свободные ячейки нужного размера','2026-01-10 08:42:22'),(125,1001,'parcel','S','courier','courier','FAILED',NULL,'NO_FREE_CELLS','Не найдены свободные ячейки нужного размера','2026-01-10 08:53:37'),(126,1001,'parcel','S','self','courier','FAILED',NULL,'NO_FREE_CELLS','Не найдены свободные ячейки нужного размера','2026-01-10 08:55:10'),(127,1001,'parcel','S','self','courier','FAILED',NULL,'NO_FREE_CELLS','Не найдены свободные ячейки нужного размера','2026-01-10 08:56:04'),(128,1001,'parcel','S','self','courier','FAILED',NULL,'NO_FREE_CELLS','Не найдены свободные ячейки нужного размера','2026-01-10 08:59:02'),(129,1002,'parcel','M','courier','courier','COMPLETED',1419,NULL,NULL,'2026-01-11 11:45:15'),(130,1003,'parcel','L','courier','courier','COMPLETED',1420,NULL,NULL,'2026-01-11 12:34:50'),(131,1001,'parcel','M','courier','courier','COMPLETED',1421,NULL,NULL,'2026-01-11 12:40:09'),(132,1001,'parcel','M','courier','courier','COMPLETED',1422,NULL,NULL,'2026-01-11 14:14:40'),(133,1001,'parcel','S','courier','courier','FAILED',NULL,'NO_FREE_CELLS','Не найдены свободные ячейки нужного размера','2026-01-12 10:14:59'),(134,1001,'parcel','S','courier','courier','FAILED',NULL,'NO_FREE_CELLS','Не найдены свободные ячейки нужного размера','2026-01-12 10:15:56'),(135,1001,'string','string','string','string','FAILED',NULL,'NO_FREE_CELLS','Не найдены свободные ячейки нужного размера','2026-01-12 10:17:22'),(136,1001,'parcel','S','courier','courier','FAILED',NULL,'NO_FREE_CELLS','Не найдены свободные ячейки нужного размера','2026-01-12 11:50:29'),(137,1001,'parcel','S','courier','courier','FAILED',NULL,'NO_FREE_CELLS','Не найдены свободные ячейки нужного размера','2026-01-12 11:50:48'),(138,1001,'parcel','S','courier','courier','FAILED',NULL,'NO_FREE_CELLS','Не найдены свободные ячейки нужного размера','2026-01-12 11:56:06'),(139,1001,'parcel','S','courier','courier','FAILED',NULL,'NO_FREE_CELLS','Не найдены свободные ячейки нужного размера','2026-01-12 12:00:26'),(140,1001,'parcel','S','courier','courier','FAILED',NULL,'NO_FREE_CELLS','Не найдены свободные ячейки нужного размера','2026-01-12 12:01:18'),(141,1002,'parcel','S','courier','courier','FAILED',NULL,'NO_FREE_CELLS','Не найдены свободные ячейки нужного размера','2026-01-12 12:02:52'),(142,1003,'parcel','M','self','courier','FAILED',NULL,'NO_FREE_CELLS','Не найдены свободные ячейки нужного размера','2026-01-12 12:08:20'),(143,1003,'parcel','S','self','courier','COMPLETED',1423,NULL,NULL,'2026-01-12 12:13:19'),(144,1003,'parcel','S','self','courier','COMPLETED',1424,NULL,NULL,'2026-01-12 14:47:07'),(145,1003,'parcel','M','self','courier','COMPLETED',1425,NULL,NULL,'2026-01-12 14:47:45'),(146,1004,'parcel','M','self','courier','COMPLETED',1426,NULL,NULL,'2026-01-12 14:49:24'),(147,1004,'parcel','XL','self','courier','FAILED',NULL,'NO_FREE_CELLS','Не найдены свободные ячейки нужного размера','2026-01-12 14:49:49'),(148,1002,'parcel','S','courier','courier','COMPLETED',1427,NULL,NULL,'2026-01-12 15:50:00'),(149,1002,'parcel','S','courier','courier','COMPLETED',1428,NULL,NULL,'2026-01-12 15:50:37'),(150,1004,'parcel','S','courier','courier','COMPLETED',1429,NULL,NULL,'2026-01-12 15:52:46'),(151,1001,'parcel','S','courier','courier','FAILED',NULL,'NO_FREE_CELLS','Не найдены свободные ячейки нужного размера','2026-01-12 16:15:26'),(152,1001,'parcel','S','courier','courier','FAILED',NULL,'NO_FREE_CELLS','Не найдены свободные ячейки нужного размера','2026-01-12 16:15:29'),(153,1003,'parcel','M','courier','courier','COMPLETED',1435,NULL,NULL,'2026-01-12 16:18:37'),(154,1004,'parcel','S','courier','courier','FAILED',NULL,'NO_FREE_CELLS','Не найдены свободные ячейки нужного размера','2026-01-12 16:21:59'),(155,1004,'parcel','S','courier','courier','FAILED',NULL,'NO_FREE_CELLS','Не найдены свободные ячейки нужного размера','2026-01-12 16:23:16'),(156,1003,'parcel','S','courier','courier','COMPLETED',1434,NULL,NULL,'2026-01-13 07:54:40'),(157,1003,'parcel','S','courier','courier','COMPLETED',1433,NULL,NULL,'2026-01-13 07:55:58'),(158,1003,'parcel','S','courier','courier','FAILED',NULL,'NO_FREE_CELLS','Не найдены свободные ячейки нужного размера','2026-01-13 07:58:59'),(159,0,'string','string','string','string','FAILED',NULL,'NO_FREE_CELLS','Не найдены свободные ячейки нужного размера','2026-01-13 08:00:47'),(160,1004,'string','string','string','string','FAILED',NULL,'NO_FREE_CELLS','Не найдены свободные ячейки нужного размера','2026-01-13 08:01:29'),(161,1005,'parcel','S','courier','courier','FAILED',NULL,'NO_FREE_CELLS','Не найдены свободные ячейки нужного размера','2026-01-13 08:22:44'),(162,1003,'parcel','M','courier','courier','COMPLETED',1432,NULL,NULL,'2026-01-13 08:47:16'),(163,1003,'parcel','L','courier','courier','COMPLETED',1431,NULL,NULL,'2026-01-13 09:23:48'),(164,1004,'parcel','M','courier','courier','FAILED',NULL,'NO_FREE_CELLS','Не найдены свободные ячейки нужного размера','2026-01-13 15:27:13'),(165,1004,'parcel','M','self','courier','FAILED',NULL,'NO_FREE_CELLS','Не найдены свободные ячейки нужного размера','2026-01-13 15:34:52'),(166,1004,'parcel','P','courier','courier','COMPLETED',1436,NULL,NULL,'2026-01-13 15:53:22'),(167,1004,'parcel','M','courier','courier','FAILED',NULL,'NO_FREE_CELLS','Не найдены свободные ячейки нужного размера','2026-01-13 18:15:03'),(168,1004,'parcel','M','courier','courier','FAILED',NULL,'NO_FREE_CELLS','Не найдены свободные ячейки нужного размера','2026-01-13 18:17:13'),(169,1004,'parcel','M','courier','courier','FAILED',NULL,'NO_FREE_CELLS','Не найдены свободные ячейки нужного размера','2026-01-13 18:18:02'),(170,1004,'parcel','S','courier','courier','FAILED',NULL,'NO_FREE_CELLS','Не найдены свободные ячейки нужного размера','2026-01-15 07:50:36'),(171,1004,'letter','P','courier','courier','COMPLETED',1437,NULL,NULL,'2026-01-15 07:50:51'),(172,1001,'parcel','M','courier','courier','COMPLETED',1438,NULL,NULL,'2026-01-15 08:01:09'),(173,1001,'letter','P','courier','courier','COMPLETED',1439,NULL,NULL,'2026-01-15 10:28:35'),(174,1004,'parcel','P','courier','courier','COMPLETED',1440,NULL,NULL,'2026-01-15 12:46:44'),(175,1004,'parcel','P','courier','courier','FAILED',NULL,'NO_FREE_CELLS','Не найдены свободные ячейки нужного размера','2026-01-15 12:50:36'),(176,1004,'parcel','L','courier','courier','COMPLETED',1441,NULL,NULL,'2026-01-15 12:50:51'),(177,1003,'parcel','L','courier','courier','FAILED',NULL,'NO_FREE_CELLS','Не найдены свободные ячейки нужного размера','2026-01-15 20:50:58'),(178,1004,'parcel','L','courier','courier','FAILED',NULL,'NO_FREE_CELLS','Не найдены свободные ячейки нужного размера','2026-01-15 20:51:16'),(179,1005,'parcel','L','courier','courier','FAILED',NULL,'NO_FREE_CELLS','Не найдены свободные ячейки нужного размера','2026-01-15 20:51:28'),(180,1001,'parcel','L','courier','courier','FAILED',NULL,'NO_FREE_CELLS','Не найдены свободные ячейки нужного размера','2026-01-15 20:51:38'),(181,1002,'parcel','L','courier','courier','FAILED',NULL,'NO_FREE_CELLS','Не найдены свободные ячейки нужного размера','2026-01-15 20:51:51'),(182,1005,'parcel','M','courier','courier','COMPLETED',1442,NULL,NULL,'2026-01-15 20:52:10'),(183,1003,'parcel','S','courier','courier','COMPLETED',1443,NULL,NULL,'2026-01-27 14:17:24'),(184,1004,'parcel','L','courier','courier','PENDING',NULL,NULL,NULL,'2026-01-27 14:19:54'),(185,1004,'parcel','S','courier','courier','PENDING',NULL,NULL,NULL,'2026-01-27 14:20:38'),(186,1004,'parcel','M','courier','courier','COMPLETED',1444,NULL,NULL,'2026-01-27 14:21:01'),(187,1004,'parcel','M','courier','courier','PENDING',NULL,NULL,NULL,'2026-01-28 08:14:19'),(188,1004,'parcel','M','courier','courier','PENDING',NULL,NULL,NULL,'2026-01-28 08:38:04'),(189,1004,'parcel','M','courier','courier','PENDING',NULL,NULL,NULL,'2026-01-28 09:49:33'),(190,1004,'parcel','M','courier','courier','PENDING',NULL,NULL,NULL,'2026-01-28 11:38:08'),(191,1004,'parcel','M','courier','courier','COMPLETED',1446,NULL,NULL,'2026-01-28 11:48:06'),(192,1005,'parcel','S','courier','self','COMPLETED',1447,NULL,NULL,'2026-01-28 14:55:21'),(193,1005,'parcel','X','self','self','FAILED',NULL,'NO_FREE_CELLS','No free cells of type \'X\' found for request 193.','2026-01-28 14:58:30'),(194,1005,'parcel','S','self','self','COMPLETED',1448,NULL,NULL,'2026-01-29 08:12:39'),(195,1004,'parcel','S','self','self','COMPLETED',1449,NULL,NULL,'2026-02-04 15:52:57'),(196,1004,'parcel','M','courier','self','COMPLETED',1502,NULL,NULL,'2026-02-05 07:54:07'),(197,1004,'parcel','S','courier','courier','COMPLETED',1503,NULL,NULL,'2026-02-05 08:00:37'),(198,1005,'parsel','M','self','self','COMPLETED',1504,NULL,NULL,'2026-02-05 09:06:16'),(199,1005,'parsel','F','self','self','FAILED',NULL,'NO_FREE_CELLS','NO_FREE_CELLS','2026-02-05 09:06:50'),(200,1003,'parcel','S','courier','courier','COMPLETED',1505,NULL,NULL,'2026-02-06 05:52:47'),(201,1003,'parcel','S','courier','courier','COMPLETED',1506,NULL,NULL,'2026-02-06 05:53:08'),(202,1003,'parcel','S','courier','courier','COMPLETED',1507,NULL,NULL,'2026-02-06 05:53:28'),(203,1003,'parcel','S','courier','courier','FAILED',NULL,'NO_FREE_CELLS','NO_FREE_CELLS','2026-02-06 05:53:40'),(204,1003,'parcel','S','courier','courier','FAILED',NULL,'NO_FREE_CELLS','NO_FREE_CELLS','2026-02-06 05:53:43'),(205,1003,'parcel','S','courier','courier','FAILED',NULL,'NO_FREE_CELLS','NO_FREE_CELLS','2026-02-06 05:53:49'),(206,1001,'parcel','S','courier','courier','FAILED',NULL,'NO_FREE_CELLS','NO_FREE_CELLS','2026-02-06 16:31:36'),(207,1004,'parcel','M','courier','courier','FAILED',NULL,'List argument must consist only of tuples or dictionaries','List argument must consist only of tuples or dictionaries','2026-02-08 12:08:59'),(208,1004,'parcel','M','courier','courier','FAILED',NULL,'List argument must consist only of tuples or dictionaries','List argument must consist only of tuples or dictionaries','2026-02-08 12:38:24'),(209,1004,'parcel','M','courier','courier','FAILED',NULL,'List argument must consist only of tuples or dictionaries','List argument must consist only of tuples or dictionaries','2026-02-08 12:50:37'),(210,1004,'parcel','M','courier','courier','FAILED',NULL,'List argument must consist only of tuples or dictionaries','List argument must consist only of tuples or dictionaries','2026-02-08 12:56:31'),(211,1004,'parcel','M','courier','courier','FAILED',NULL,'List argument must consist only of tuples or dictionaries','List argument must consist only of tuples or dictionaries','2026-02-08 13:03:35'),(212,1004,'parcel','M','courier','courier','FAILED',NULL,'List argument must consist only of tuples or dictionaries','List argument must consist only of tuples or dictionaries','2026-02-08 13:11:13'),(213,1004,'parcel','M','courier','courier','COMPLETED',1508,NULL,NULL,'2026-02-08 13:22:41');

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
  PRIMARY KEY (`id`),
  KEY `source_cell_id` (`source_cell_id`),
  KEY `dest_cell_id` (`dest_cell_id`),
  KEY `idx_orders_client_user_id` (`client_user_id`),
  CONSTRAINT `orders_ibfk_1` FOREIGN KEY (`source_cell_id`) REFERENCES `locker_cells` (`id`),
  CONSTRAINT `orders_ibfk_2` FOREIGN KEY (`dest_cell_id`) REFERENCES `locker_cells` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=1509 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `orders`
--

INSERT  IGNORE INTO `orders` VALUES (1,'order_courier_failed','Timeout Order','courier',NULL,'courier',2,12,'2025-12-16 09:46:53','2025-11-24 16:33:51',0),(2,'order_reservation_expired','Trip Order 1','courier',NULL,'courier',3,13,'2025-11-24 16:36:07','2025-11-24 16:33:51',0),(3,'order_reservation_expired','Trip Order 2','courier',NULL,'courier',4,14,'2025-11-24 16:36:08','2025-11-24 16:33:51',0),(4,'order_reservation_expired','Trip Order 3','courier',NULL,'courier',5,15,'2025-11-24 16:36:08','2025-11-24 16:33:52',0),(5,'order_created','Order','courier',NULL,'courier',2,5,'2026-01-17 09:22:39','2025-11-26 16:25:34',0),(6,'order_created','test (S)','courier','test','courier',41,44,'2026-01-28 15:49:35','2025-12-07 17:02:57',1005),(7,'order_created','test (L)','courier','test','courier',7,17,'2025-12-25 10:42:59','2025-12-07 17:02:58',0),(8,'order_created','test (M)','courier','test','courier',43,45,'2025-12-25 10:42:59','2025-12-07 17:17:06',0),(9,'order_created','test (M)','courier','test','courier',6,16,'2025-12-25 10:42:59','2025-12-07 17:18:55',0),(10,'order_created','test (L)','courier','test','courier',8,18,'2025-12-25 10:42:59','2025-12-07 17:19:25',0),(660,'order_created','documents (S)','courier','documents','courier',42,11,'2025-12-25 10:42:59','2025-12-12 09:26:46',0),(661,'order_created','documents (P)','courier','documents','courier',9,19,'2025-12-25 10:42:59','2025-12-12 09:55:55',0),(662,'order_created','documents (P)','courier','documents','courier',10,20,'2025-12-25 10:42:59','2025-12-12 10:50:17',0),(1361,'order_courier_failed','Документы (S)','courier','Документы','courier',41,44,'2025-12-25 10:42:59','2025-12-15 18:43:45',0),(1362,'order_courier_failed','Финальный тест (S)','courier','Финальный тест','courier',42,11,'2025-12-25 10:42:59','2025-12-15 19:20:44',0),(1363,'order_created','Заказ A (S)','courier',NULL,'courier',1,12,'2025-12-15 19:42:02','2025-12-15 19:42:02',0),(1364,'order_created','Заказ 1 (S)','courier','Заказ 1','courier',41,44,'2025-12-25 10:42:59','2025-12-15 19:57:16',0),(1365,'order_created','Заказ 2 (S)','courier','Заказ 2','courier',42,11,'2025-12-25 10:42:59','2025-12-15 19:57:16',0),(1366,'order_created','Тест А (S)','courier','Тест А','courier',41,44,'2025-12-25 10:42:59','2025-12-15 20:33:36',0),(1367,'order_created','Тест Б (S)','courier','Тест Б','courier',42,11,'2025-12-25 10:42:59','2025-12-15 20:33:36',0),(1368,'order_created','Проверка trip 2 (S)','courier','Проверка trip 2','courier',41,44,'2025-12-25 10:42:59','2025-12-15 20:46:12',0),(1369,'order_created','Debug test (S)','courier','Debug test','courier',41,44,'2025-12-25 10:42:59','2025-12-16 06:00:46',0),(1370,'order_created','Test trip 3 (S)','courier','Test trip 3','courier',42,11,'2025-12-25 10:42:59','2025-12-16 06:05:01',0),(1371,'order_created','Тест 2 (S)','courier','Тест 2','courier',1,12,'2025-12-25 10:42:59','2025-12-16 06:50:03',0),(1372,'order_created','Тест 3 (S)','courier','Тест 3','courier',2,13,'2025-12-25 10:42:59','2025-12-16 06:50:03',0),(1373,'order_courier_failed','Тест 4 (S)','courier','Тест 4','courier',3,14,'2025-12-25 10:42:59','2025-12-16 06:50:04',0),(1374,'order_created','Тест локер A (S)','courier','Тест локер A','courier',41,44,'2025-12-25 10:42:59','2025-12-16 10:03:20',0),(1375,'order_created','Тест локер B (S)','courier','Тест локер B','courier',42,11,'2025-12-25 10:42:59','2025-12-16 10:03:20',0),(1376,'order_created','Тест 2→1','courier',NULL,'courier',45,43,'2025-12-16 10:11:32','2025-12-16 10:11:32',0),(1377,'order_created','документы (S)','courier','документы','courier',1,12,'2025-12-25 10:42:59','2025-12-19 09:45:10',0),(1378,'order_parcel_confirmed','документы (S)','courier','документы','courier',41,44,'2025-12-25 10:42:59','2025-12-19 09:56:26',0),(1379,'order_courier_has_parcel','документы (M)','courier','документы','courier',43,45,'2025-12-25 10:42:59','2025-12-19 12:04:31',0),(1380,'order_created','parcel (S)','courier','parcel','courier',42,11,'2026-01-28 15:50:17','2025-12-23 16:35:14',1001),(1381,'order_created','parcel (S)','courier','parcel','courier',1,12,'2026-01-28 15:50:17','2025-12-24 11:50:31',1001),(1382,'order_created','parcel (S)','courier','parcel','courier',2,13,'2026-01-28 15:50:17','2025-12-24 11:52:21',1001),(1383,'order_created','parcel (S)','courier','parcel','courier',3,14,'2026-01-28 15:50:17','2025-12-24 11:54:17',1001),(1384,'order_created','parcel (M)','courier','parcel','courier',5,15,'2026-01-28 15:50:17','2025-12-24 12:04:52',1001),(1385,'order_created','parcel (M)','courier','parcel','courier',6,16,'2026-01-28 15:50:17','2025-12-24 12:05:22',1001),(1386,'order_created','letter (P)','self','letter','courier',9,19,'2026-01-28 15:50:17','2025-12-24 12:24:23',1001),(1387,'order_created','letter (P)','courier','letter','courier',10,20,'2026-01-28 15:50:17','2025-12-24 12:35:38',1001),(1388,'order_created','parcel (L)','self','parcel','courier',7,17,'2026-01-28 15:50:17','2025-12-24 12:53:59',1001),(1389,'order_created','parcel (M)','courier','parcel','courier',43,45,'2026-01-28 15:50:17','2025-12-24 15:36:49',1001),(1390,'order_created','parcel (M)','courier','parcel','courier',5,15,'2026-01-28 15:50:17','2025-12-24 15:40:49',1001),(1391,'order_created','parcel (M)','courier','parcel','courier',6,16,'2026-01-28 15:50:17','2025-12-24 15:40:59',1001),(1392,'order_created','parcel (L)','courier','parcel','courier',7,17,'2026-01-28 15:50:17','2025-12-24 15:42:45',1001),(1393,'order_created','parcel (S)','courier','parcel','courier',41,44,'2026-01-28 15:50:17','2025-12-25 15:18:03',1001),(1394,'order_created','parcel (S)','courier','parcel','courier',42,11,'2026-01-28 15:50:17','2025-12-25 15:20:29',1001),(1395,'order_created','parcel (S)','courier','parcel','courier',1,12,'2026-01-28 15:50:17','2025-12-25 15:23:44',1001),(1396,'order_created','parcel (S)','courier','parcel','courier',2,13,'2026-01-28 15:50:17','2025-12-25 15:26:14',1001),(1397,'order_created','parcel (S)','courier','parcel','courier',3,14,'2026-01-28 15:50:17','2025-12-25 15:28:14',1001),(1398,'order_courier_has_parcel','parcel (L)','self','parcel','courier',8,18,'2026-01-28 15:50:10','2025-12-26 12:26:22',1002),(1399,'order_parcel_confirmed','documents (S)','self',NULL,'courier',41,44,'2025-12-26 13:29:22','2025-12-26 13:18:51',0),(1400,'order_created','documents (M)','self',NULL,'courier',43,45,'2025-12-26 13:38:37','2025-12-26 13:38:37',0),(1401,'order_cancelled','documents (M)','self',NULL,'courier',5,15,'2025-12-26 16:32:13','2025-12-26 16:14:32',0),(1402,'order_created','parcel (S)','self',NULL,'courier',42,11,'2026-01-28 15:50:10','2025-12-26 16:45:51',1002),(1403,'order_cancelled','parcel (S)','courier',NULL,'courier',1,12,'2026-01-28 15:50:17','2025-12-26 17:11:36',1001),(1404,'order_created','parcel (S)','courier',NULL,'courier',1,12,'2026-01-28 15:50:17','2025-12-27 15:09:30',1001),(1405,'order_created','parcel (S)','courier',NULL,'courier',2,13,'2026-01-28 15:50:17','2025-12-27 15:13:30',1001),(1406,'order_created','parcel (S)','courier',NULL,'courier',3,14,'2026-01-28 15:50:17','2025-12-28 15:09:47',1001),(1407,'order_cancelled','parcel (M)','courier',NULL,'courier',6,16,'2026-01-28 15:50:17','2025-12-29 06:58:01',1001),(1408,'order_created','parcel (S)','courier',NULL,'courier',41,44,'2026-01-28 15:50:17','2025-12-31 11:19:13',1001),(1409,'order_created','parcel (S)','courier',NULL,'courier',42,11,'2026-01-28 15:50:17','2026-01-01 13:22:51',1001),(1410,'order_created','parcel (S)','courier',NULL,'courier',1,12,'2026-01-28 15:50:17','2026-01-01 13:23:52',1001),(1411,'order_created','parcel (S)','courier',NULL,'courier',2,13,'2026-01-28 15:50:17','2026-01-02 10:48:17',1001),(1412,'order_created','parcel (S)','courier',NULL,'courier',3,14,'2026-01-28 15:50:17','2026-01-02 13:23:12',1001),(1413,'order_courier_failed','parcel (L)','courier',NULL,'courier',7,17,'2026-01-28 15:50:03','2026-01-06 15:00:17',1003),(1414,'order_created','parcel (S)','courier',NULL,'courier',41,44,'2026-01-28 15:50:17','2026-01-09 17:03:28',1001),(1415,'order_created','parcel (S)','courier',NULL,'courier',42,11,'2026-01-28 15:50:17','2026-01-09 18:09:15',1001),(1416,'order_created','parcel (S)','courier',NULL,'courier',1,12,'2026-01-28 15:50:17','2026-01-09 18:09:50',1001),(1417,'order_cancelled','parcel (S)','courier',NULL,'courier',2,13,'2026-01-28 15:50:17','2026-01-09 18:16:00',1001),(1418,'order_created','parcel (S)','courier',NULL,'courier',3,14,'2026-01-28 15:50:17','2026-01-09 18:17:30',1001),(1419,'order_created','parcel (M)','courier',NULL,'courier',43,45,'2026-01-28 15:50:10','2026-01-11 11:45:19',1002),(1420,'order_created','parcel (L)','courier',NULL,'courier',8,18,'2026-01-28 15:50:03','2026-01-11 12:34:54',1003),(1421,'order_cancelled','parcel (M)','courier',NULL,'courier',5,15,'2026-01-28 15:50:17','2026-01-11 12:40:09',1001),(1422,'order_cancelled','parcel (M)','courier',NULL,'courier',6,16,'2026-01-28 15:50:17','2026-01-11 14:14:42',1001),(1423,'order_created','parcel (S)','courier',NULL,'self',41,44,'2026-01-28 15:50:03','2026-01-12 12:13:23',1003),(1424,'order_created','parcel (S)','courier',NULL,'self',42,11,'2026-01-28 15:50:03','2026-01-12 14:47:09',1003),(1425,'order_cancelled','parcel (M)','courier',NULL,'self',43,45,'2026-01-28 15:50:03','2026-01-12 14:47:50',1003),(1426,'order_cancelled','parcel (M)','courier',NULL,'self',5,15,'2026-01-28 15:30:33','2026-01-12 14:49:28',1004),(1427,'order_created','parcel (S)','courier',NULL,'courier',1,12,'2026-01-28 15:50:10','2026-01-12 15:50:04',1002),(1428,'order_cancelled','parcel (S)','courier',NULL,'courier',2,13,'2026-01-28 15:50:10','2026-01-12 15:50:39',1002),(1429,'order_cancelled','parcel (S)','courier',NULL,'courier',3,14,'2026-01-28 15:30:33','2026-01-12 15:52:49',1004),(1431,'order_created','parcel (L)','courier',NULL,'courier',7,17,'2026-01-28 15:50:03','2026-01-13 11:40:52',1003),(1432,'order_created','parcel (M)','courier',NULL,'courier',6,16,'2026-01-28 15:50:03','2026-01-13 12:42:27',1003),(1433,'order_created','parcel (S)','courier',NULL,'courier',2,13,'2026-01-28 15:50:03','2026-01-13 14:16:28',1003),(1434,'order_created','parcel (S)','courier',NULL,'courier',3,14,'2026-01-28 15:50:03','2026-01-13 15:24:59',1003),(1435,'order_cancelled','parcel (M)','courier',NULL,'courier',43,45,'2026-01-28 15:50:03','2026-01-13 15:25:01',1003),(1436,'order_cancelled','parcel (P)','courier',NULL,'courier',9,19,'2026-01-28 15:30:33','2026-01-13 15:53:23',1004),(1437,'order_cancelled','letter (P)','courier',NULL,'courier',9,19,'2026-01-28 15:30:33','2026-01-15 07:50:55',1004),(1438,'order_cancelled','parcel (M)','courier',NULL,'courier',5,15,'2026-01-28 15:50:17','2026-01-15 08:01:11',1001),(1439,'order_created','letter (P)','courier',NULL,'courier',9,19,'2026-01-28 15:50:17','2026-01-15 10:28:36',1001),(1440,'order_created','parcel (P)','courier',NULL,'courier',10,20,'2026-01-28 15:30:33','2026-01-15 12:46:48',1004),(1441,'order_created','parcel (L)','courier',NULL,'courier',8,18,'2026-01-28 15:30:33','2026-01-15 12:50:53',1004),(1442,'order_created','parcel (M)','courier',NULL,'courier',43,45,'2026-01-28 15:49:35','2026-01-15 20:52:14',1005),(1443,'order_created','parcel (S)','courier',NULL,'courier',2,13,'2026-01-28 15:50:03','2026-01-27 14:17:24',1003),(1444,'order_created','parcel (M)','courier',NULL,'courier',5,15,'2026-01-28 15:30:33','2026-01-27 14:21:05',1004),(1445,'order_created','parcel (M)','courier',NULL,'courier',6,16,'2026-01-28 09:49:34','2026-01-28 09:49:34',1004),(1446,'order_cancelled','parcel (M)','courier',NULL,'courier',43,45,'2026-01-28 15:12:59','2026-01-28 11:48:06',1004),(1447,'order_cancelled','parcel (S)','self',NULL,'courier',41,44,'2026-01-28 15:12:44','2026-01-28 14:55:23',1005),(1448,'order_created','parcel (S)','self',NULL,'self',41,44,'2026-01-29 08:12:40','2026-01-29 08:12:40',1005),(1449,'order_created','parcel (S)','self',NULL,'self',42,11,'2026-02-04 15:52:58','2026-02-04 15:52:58',1004),(1502,'order_courier1_assigned','parcel (M)','self',NULL,'courier',43,45,'2026-02-05 09:11:47','2026-02-05 07:58:29',1004),(1503,'order_cancelled','parcel (S)','courier',NULL,'courier',1,12,'2026-02-05 08:25:26','2026-02-05 08:00:39',1004),(1504,'order_created','parsel (M)','self',NULL,'self',5,15,'2026-02-05 09:06:17','2026-02-05 09:06:17',1005),(1505,'order_created','parcel (S)','courier',NULL,'courier',1,12,'2026-02-06 05:52:52','2026-02-06 05:52:52',1003),(1506,'order_created','parcel (S)','courier',NULL,'courier',2,13,'2026-02-06 05:53:12','2026-02-06 05:53:12',1003),(1507,'order_created','parcel (S)','courier',NULL,'courier',3,14,'2026-02-06 05:53:32','2026-02-06 05:53:32',1003),(1508,'order_created','parcel (M)','courier',NULL,'courier',16,6,'2026-02-08 14:18:09','2026-02-08 13:22:43',1004);
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

    -- Проверка для order_courier1_assigned (курьер pickup)
    IF NEW.status = 'order_courier1_assigned'
       AND OLD.status <> 'order_courier1_assigned' THEN

        SELECT COUNT(*)
        INTO has_courier1
        FROM stage_orders so
        JOIN trips t ON t.id = so.trip_id
        WHERE so.order_id = NEW.id
          AND so.leg = 'pickup'
          AND so.courier_user_id IS NOT NULL;

        IF has_courier1 = 0 THEN
            SIGNAL SQLSTATE '45000'
            SET MESSAGE_TEXT =
                'Transition to order_courier1_assigned requires pickup courier in stage_orders';
        END IF;
    END IF;

    -- Проверка для order_courier2_assigned (курьер delivery)
    IF NEW.status = 'order_courier2_assigned'
       AND OLD.status <> 'order_courier2_assigned' THEN

        SELECT COUNT(*)
        INTO has_courier2
        FROM stage_orders so
        JOIN trips t ON t.id = so.trip_id
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
  PRIMARY KEY (`id`),
  UNIQUE KEY `ux_fsm_entity_process` (`entity_type`,`entity_id`,`process_name`),
  KEY `idx_fsm_process_state` (`process_name`,`fsm_state`),
  KEY `idx_fsm_next_timer` (`next_timer_at`),
  KEY `idx_fsm_requested_by` (`requested_by_user_id`),
  KEY `idx_fsm_target_user` (`target_user_id`)
) ENGINE=InnoDB AUTO_INCREMENT=408 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `server_fsm_instances`
--

INSERT  IGNORE INTO `server_fsm_instances` VALUES (1,'order_request',1,'order_creation','FAILED',NULL,1,'NOT_IMPLEMENTED','2025-12-07 13:53:25','2025-12-07 14:17:02',NULL,NULL,NULL,NULL),(2,'order_request',2,'order_creation','FAILED',NULL,1,'NO_FREE_CELLS','2025-12-07 16:37:12','2025-12-07 16:38:43',NULL,NULL,NULL,NULL),(3,'order_request',3,'order_creation','COMPLETED',NULL,1,NULL,'2025-12-07 16:45:30','2025-12-07 17:02:57',NULL,NULL,NULL,NULL),(4,'order_request',4,'order_creation','COMPLETED',NULL,1,NULL,'2025-12-07 16:54:49','2025-12-07 17:02:58',NULL,NULL,NULL,NULL),(5,'order_request',5,'order_creation','COMPLETED',NULL,1,NULL,'2025-12-07 17:08:22','2025-12-07 17:17:06',NULL,NULL,NULL,NULL),(6,'order_request',6,'order_creation','COMPLETED',NULL,1,NULL,'2025-12-07 17:17:26','2025-12-07 17:18:55',NULL,NULL,NULL,NULL),(7,'order_request',7,'order_creation','COMPLETED',NULL,1,NULL,'2025-12-07 17:19:20','2025-12-07 17:19:25',NULL,NULL,NULL,NULL),(8,'order_request',8,'order_creation','FAILED',NULL,1,'NO_FREE_CELLS','2025-12-11 09:43:29','2025-12-11 09:43:34',NULL,NULL,NULL,NULL),(9,'order_request',9,'order_creation','COMPLETED',NULL,1,NULL,'2025-12-12 08:32:33','2025-12-12 09:26:46',NULL,NULL,NULL,NULL),(10,'order_request',10,'order_creation','FAILED',NULL,1,'NO_FREE_CELLS','2025-12-12 09:38:45','2025-12-12 09:38:46',NULL,NULL,NULL,NULL),(11,'order_request',11,'order_creation','FAILED',NULL,1,'NO_FREE_CELLS','2025-12-12 09:39:44','2025-12-12 09:39:46',NULL,NULL,NULL,NULL),(12,'order_request',12,'order_creation','FAILED',NULL,1,'NO_FREE_CELLS','2025-12-12 09:46:20','2025-12-12 09:46:21',NULL,NULL,NULL,NULL),(13,'order_request',13,'order_creation','COMPLETED',NULL,1,NULL,'2025-12-12 09:55:53','2025-12-12 09:55:55',NULL,NULL,NULL,NULL),(14,'order_request',14,'order_creation','FAILED',NULL,1,'NO_FREE_CELLS','2025-12-12 10:16:43','2025-12-12 10:16:46',NULL,NULL,NULL,NULL),(15,'order_request',15,'order_creation','COMPLETED',NULL,1,NULL,'2025-12-12 10:50:14','2025-12-12 10:50:17',NULL,NULL,NULL,NULL),(16,'order_request',16,'order_creation','FAILED',NULL,1,'NO_FREE_CELLS','2025-12-12 12:40:43','2025-12-12 12:40:48',NULL,NULL,NULL,NULL),(17,'order_request',17,'order_creation','FAILED',NULL,1,'NO_FREE_CELLS','2025-12-12 13:32:58','2025-12-12 13:33:00',NULL,NULL,NULL,NULL),(18,'order_request',18,'order_creation','FAILED',NULL,1,'NO_FREE_CELLS','2025-12-12 14:22:45','2025-12-12 14:22:48',NULL,NULL,NULL,NULL),(19,'order_request',19,'order_creation','FAILED',NULL,1,'NO_FREE_CELLS','2025-12-12 16:06:43','2025-12-12 16:11:51',NULL,NULL,NULL,NULL),(20,'order_request',20,'order_creation','FAILED',NULL,1,'NO_FREE_CELLS','2025-12-12 16:21:18','2025-12-12 16:21:22',NULL,NULL,NULL,NULL),(21,'order',1,'order_assign_courier1','FAILED',NULL,1,'ASSIGNMENT_FAILED','2025-12-15 07:42:38','2025-12-15 16:40:04',1,'driver',2,'courier'),(24,'order',6,'order_assign_courier1','FAILED',NULL,1,'ASSIGNMENT_FAILED','2025-12-15 16:49:32','2026-01-23 09:58:03',100,'courier',100,NULL),(26,'order_request',21,'order_creation','COMPLETED',NULL,1,NULL,'2025-12-15 17:31:35','2025-12-15 18:43:45',NULL,NULL,NULL,NULL),(27,'order',1361,'order_assign_courier1','FAILED',NULL,1,'ASSIGNMENT_FAILED','2025-12-15 18:47:30','2025-12-15 18:47:35',1,'driver',2,'courier'),(28,'order_request',22,'order_creation','COMPLETED',NULL,1,NULL,'2025-12-15 19:20:40','2025-12-15 19:20:44',NULL,NULL,NULL,NULL),(29,'order',1362,'order_assign_courier1','COMPLETED',NULL,1,NULL,'2025-12-15 19:24:05','2025-12-15 19:24:09',1,'driver',2,'courier'),(32,'order_request',25,'order_creation','FAILED',NULL,1,'NO_FREE_CELLS','2025-12-15 19:50:38','2025-12-15 19:50:42',NULL,NULL,NULL,NULL),(33,'order_request',26,'order_creation','FAILED',NULL,1,'NO_FREE_CELLS','2025-12-15 19:50:38','2025-12-15 19:50:42',NULL,NULL,NULL,NULL),(36,'order_request',29,'order_creation','COMPLETED',NULL,1,NULL,'2025-12-15 20:33:34','2025-12-15 20:33:36',NULL,NULL,NULL,NULL),(37,'order_request',30,'order_creation','COMPLETED',NULL,1,NULL,'2025-12-15 20:33:34','2025-12-15 20:33:36',NULL,NULL,NULL,NULL),(38,'order_request',31,'order_creation','COMPLETED',NULL,1,NULL,'2025-12-15 20:46:10','2025-12-15 20:46:12',NULL,NULL,NULL,NULL),(39,'order_request',32,'order_creation','COMPLETED',NULL,1,NULL,'2025-12-16 06:00:45','2025-12-16 06:00:46',NULL,NULL,NULL,NULL),(40,'order_request',33,'order_creation','COMPLETED',NULL,1,NULL,'2025-12-16 06:04:57','2025-12-16 06:05:01',NULL,NULL,NULL,NULL),(41,'order_request',35,'order_creation','COMPLETED',NULL,1,NULL,'2025-12-16 06:49:59','2025-12-16 06:50:03',NULL,NULL,NULL,NULL),(42,'order_request',36,'order_creation','COMPLETED',NULL,1,NULL,'2025-12-16 06:49:59','2025-12-16 06:50:04',NULL,NULL,NULL,NULL),(43,'order_request',37,'order_creation','COMPLETED',NULL,1,NULL,'2025-12-16 06:49:59','2025-12-16 06:50:04',NULL,NULL,NULL,NULL),(44,'order_request',38,'order_creation','FAILED',NULL,1,'NO_FREE_CELLS','2025-12-16 06:49:59','2025-12-16 06:50:04',NULL,NULL,NULL,NULL),(45,'order_request',39,'order_creation','FAILED',NULL,1,'ORDER_REQUEST_NOT_FOUND','2025-12-16 06:49:59','2025-12-16 06:50:04',NULL,NULL,NULL,NULL),(46,'order',1373,'order_assign_courier1','COMPLETED',NULL,1,NULL,'2025-12-16 07:21:59','2025-12-16 07:22:00',1,'driver',2,'courier'),(51,'order_request',41,'order_creation','COMPLETED',NULL,1,NULL,'2025-12-16 10:03:17','2025-12-16 10:03:20',NULL,NULL,NULL,NULL),(52,'order_request',42,'order_creation','COMPLETED',NULL,1,NULL,'2025-12-16 10:03:17','2025-12-16 10:03:20',NULL,NULL,NULL,NULL),(53,'locker',1,'locker_cell_session','COMPLETED',NULL,3,NULL,'2025-12-18 16:26:36','2025-12-18 16:44:21',2,'courier',0,'string'),(55,'order_request',43,'order_creation','COMPLETED',NULL,1,NULL,'2025-12-19 09:45:06','2025-12-19 09:45:10',NULL,NULL,NULL,NULL),(56,'order_request',44,'order_creation','COMPLETED',NULL,1,NULL,'2025-12-19 09:53:15','2025-12-19 09:56:26',NULL,NULL,NULL,NULL),(57,'order',1378,'order_assign_courier1','COMPLETED',NULL,1,NULL,'2025-12-19 10:05:28','2025-12-19 10:05:32',1,'driver',2,NULL),(58,'order',1378,'courier_open_cell','FAILED',NULL,1,'FSM locker_open_locker: 1644 (45000): Invalid transition for locker: no matching fsm_transitions','2025-12-19 10:21:23','2025-12-19 11:40:25',2,'courier',NULL,NULL),(61,'order',1378,'courier_close_cell','COMPLETED',NULL,1,NULL,'2025-12-19 11:46:06','2025-12-19 11:46:06',2,'courier',NULL,NULL),(62,'order_request',45,'order_creation','COMPLETED',NULL,1,NULL,'2025-12-19 12:04:27','2025-12-19 12:04:31',NULL,NULL,NULL,NULL),(63,'order',1379,'order_assign_courier1','COMPLETED',NULL,1,NULL,'2025-12-19 12:33:56','2025-12-19 12:48:22',2,'courier',2,'courier'),(66,'order',1379,'courier_open_cell','COMPLETED',NULL,1,NULL,'2025-12-19 12:59:26','2025-12-19 12:59:28',2,'courier',NULL,NULL),(67,'order_request',46,'order_creation','COMPLETED',NULL,1,NULL,'2025-12-23 16:35:09','2025-12-23 16:35:14',NULL,NULL,NULL,NULL),(68,'order_request',47,'order_creation','COMPLETED',NULL,1,NULL,'2025-12-24 11:50:30','2025-12-24 11:50:31',NULL,NULL,NULL,NULL),(69,'order_request',48,'order_creation','COMPLETED',NULL,1,NULL,'2025-12-24 11:52:18','2025-12-24 11:52:21',NULL,NULL,NULL,NULL),(70,'order_request',49,'order_creation','COMPLETED',NULL,1,NULL,'2025-12-24 11:54:15','2025-12-24 11:54:17',NULL,NULL,NULL,NULL),(71,'order_request',50,'order_creation','FAILED',NULL,1,'NO_FREE_CELLS','2025-12-24 12:00:31','2025-12-24 12:00:32',NULL,NULL,NULL,NULL),(72,'order_request',51,'order_creation','COMPLETED',NULL,1,NULL,'2025-12-24 12:04:50','2025-12-24 12:04:52',NULL,NULL,NULL,NULL),(73,'order_request',52,'order_creation','COMPLETED',NULL,1,NULL,'2025-12-24 12:05:22','2025-12-24 12:05:22',NULL,NULL,NULL,NULL),(74,'order_request',53,'order_creation','FAILED',NULL,1,'NO_FREE_CELLS','2025-12-24 12:21:46','2025-12-24 12:21:48',NULL,NULL,NULL,NULL),(75,'order_request',54,'order_creation','FAILED',NULL,1,'NO_FREE_CELLS','2025-12-24 12:24:07','2025-12-24 12:24:08',NULL,NULL,NULL,NULL),(76,'order_request',55,'order_creation','COMPLETED',NULL,1,NULL,'2025-12-24 12:24:20','2025-12-24 12:24:23',NULL,NULL,NULL,NULL),(77,'order_request',56,'order_creation','FAILED',NULL,1,'NO_FREE_CELLS','2025-12-24 12:31:53','2025-12-24 12:31:58',NULL,NULL,NULL,NULL),(78,'order_request',57,'order_creation','FAILED',NULL,1,'NO_FREE_CELLS','2025-12-24 12:32:29','2025-12-24 12:32:33',NULL,NULL,NULL,NULL),(79,'order_request',58,'order_creation','FAILED',NULL,1,'NO_FREE_CELLS','2025-12-24 12:32:50','2025-12-24 12:32:53',NULL,NULL,NULL,NULL),(80,'order_request',59,'order_creation','FAILED',NULL,1,'NO_FREE_CELLS','2025-12-24 12:35:26','2025-12-24 12:35:28',NULL,NULL,NULL,NULL),(81,'order_request',60,'order_creation','COMPLETED',NULL,1,NULL,'2025-12-24 12:35:33','2025-12-24 12:35:38',NULL,NULL,NULL,NULL),(82,'order_request',61,'order_creation','FAILED',NULL,1,'NO_FREE_CELLS','2025-12-24 12:37:24','2025-12-24 12:37:28',NULL,NULL,NULL,NULL),(83,'order_request',62,'order_creation','FAILED',NULL,1,'NO_FREE_CELLS','2025-12-24 12:37:39','2025-12-24 12:37:43',NULL,NULL,NULL,NULL),(84,'order_request',63,'order_creation','FAILED',NULL,1,'NO_FREE_CELLS','2025-12-24 12:37:53','2025-12-24 12:37:53',NULL,NULL,NULL,NULL),(85,'order_request',64,'order_creation','FAILED',NULL,1,'NO_FREE_CELLS','2025-12-24 12:44:17','2025-12-24 12:44:18',NULL,NULL,NULL,NULL),(86,'order_request',65,'order_creation','FAILED',NULL,1,'NO_FREE_CELLS','2025-12-24 12:50:17','2025-12-24 12:50:19',NULL,NULL,NULL,NULL),(87,'order_request',66,'order_creation','COMPLETED',NULL,1,NULL,'2025-12-24 12:53:55','2025-12-24 12:53:59',NULL,NULL,NULL,NULL),(88,'order_request',67,'order_creation','FAILED',NULL,1,'NO_FREE_CELLS','2025-12-24 14:27:35','2025-12-24 14:27:37',NULL,NULL,NULL,NULL),(89,'order_request',68,'order_creation','COMPLETED',NULL,1,NULL,'2025-12-24 15:36:48','2025-12-24 15:36:49',NULL,NULL,NULL,NULL),(90,'order_request',69,'order_creation','COMPLETED',NULL,1,NULL,'2025-12-24 15:40:47','2025-12-24 15:40:49',NULL,NULL,NULL,NULL),(91,'order_request',70,'order_creation','COMPLETED',NULL,1,NULL,'2025-12-24 15:40:59','2025-12-24 15:40:59',NULL,NULL,NULL,NULL),(92,'order_request',71,'order_creation','COMPLETED',NULL,1,NULL,'2025-12-24 15:42:42','2025-12-24 15:42:45',NULL,NULL,NULL,NULL),(93,'order_request',72,'order_creation','COMPLETED',NULL,1,NULL,'2025-12-25 15:18:01','2025-12-25 15:18:03',NULL,NULL,NULL,NULL),(94,'order_request',73,'order_creation','COMPLETED',NULL,1,NULL,'2025-12-25 15:20:26','2025-12-25 15:20:29',NULL,NULL,NULL,NULL),(95,'order_request',74,'order_creation','COMPLETED',NULL,1,NULL,'2025-12-25 15:23:40','2025-12-25 15:23:44',NULL,NULL,NULL,NULL),(96,'order_request',75,'order_creation','COMPLETED',NULL,1,NULL,'2025-12-25 15:26:12','2025-12-25 15:26:14',NULL,NULL,NULL,NULL),(97,'order_request',76,'order_creation','COMPLETED',NULL,1,NULL,'2025-12-25 15:28:13','2025-12-25 15:28:14',NULL,NULL,NULL,NULL),(98,'order_request',77,'order_creation','FAILED',NULL,1,'NO_FREE_CELLS','2025-12-26 10:11:33','2025-12-26 10:11:38',NULL,NULL,NULL,NULL),(99,'order_request',78,'order_creation','FAILED',NULL,1,'NO_FREE_CELLS','2025-12-26 10:14:03','2025-12-26 10:14:03',NULL,NULL,NULL,NULL),(100,'order_request',79,'order_creation','FAILED',NULL,1,'NO_FREE_CELLS','2025-12-26 10:34:33','2025-12-26 10:34:38',NULL,NULL,NULL,NULL),(101,'order_request',80,'order_creation','COMPLETED',NULL,1,NULL,'2025-12-26 12:26:18','2025-12-26 12:26:22',NULL,NULL,NULL,NULL),(102,'order',1398,'order_assign_courier1','COMPLETED',NULL,1,NULL,'2025-12-26 12:53:32','2025-12-26 12:58:45',2,'courier',2,NULL),(104,'order',1398,'open_cell','FAILED',NULL,1,'FSM locker_open_locker: 1644 (45000): Invalid transition for locker: no matching fsm_transitions','2025-12-26 13:00:28','2025-12-26 13:00:31',2,'courier',NULL,NULL),(105,'order_request',81,'order_creation','COMPLETED',NULL,1,NULL,'2025-12-26 13:18:51','2025-12-26 13:18:51',NULL,NULL,NULL,NULL),(106,'order',1399,'order_assign_courier1','COMPLETED',NULL,1,NULL,'2025-12-26 13:22:13','2025-12-26 13:23:21',2,'courier',2,NULL),(108,'order',1399,'open_cell','COMPLETED',NULL,1,NULL,'2025-12-26 13:24:54','2025-12-26 13:24:56',2,'courier',NULL,NULL),(109,'order',1399,'close_cell','COMPLETED',NULL,1,NULL,'2025-12-26 13:29:17','2025-12-26 13:29:22',2,'courier',NULL,NULL),(110,'order',1399,'cancel_order','FAILED',NULL,1,'CANNOT_CANCEL_FROM_order_parcel_confirmed','2025-12-26 13:31:15','2025-12-26 13:31:17',2,'courier',NULL,NULL),(111,'order_request',82,'order_creation','COMPLETED',NULL,1,NULL,'2025-12-26 13:38:36','2025-12-26 13:38:37',NULL,NULL,NULL,NULL),(112,'order',1400,'cancel_order','FAILED',NULL,1,'FSM order_cancel_reservation: 1644 (45000): Invalid transition for order: no matching fsm_transitions','2025-12-26 13:43:35','2025-12-26 15:52:11',3,'client',NULL,NULL),(114,'order_request',83,'order_creation','COMPLETED',NULL,1,NULL,'2025-12-26 16:14:28','2025-12-26 16:14:32',NULL,NULL,NULL,NULL),(115,'order',1401,'cancel_order','FAILED',NULL,1,'name \'order\' is not defined','2025-12-26 16:18:47','2025-12-26 16:32:13',3,'client',NULL,NULL),(117,'order_request',84,'order_creation','COMPLETED',NULL,1,NULL,'2025-12-26 16:45:47','2025-12-26 16:45:51',NULL,NULL,NULL,NULL),(118,'order_request',85,'order_creation','COMPLETED',NULL,1,NULL,'2025-12-26 17:11:36','2025-12-26 17:11:36',NULL,NULL,NULL,NULL),(119,'order',1403,'cancel_order','COMPLETED',NULL,1,NULL,'2025-12-26 17:13:12','2025-12-26 17:13:17',1001,'client',NULL,NULL),(120,'order_request',86,'order_creation','COMPLETED',NULL,1,NULL,'2025-12-27 15:09:28','2025-12-27 15:09:30',NULL,NULL,NULL,NULL),(121,'order_request',87,'order_creation','COMPLETED',NULL,1,NULL,'2025-12-27 15:13:30','2025-12-27 15:13:30',NULL,NULL,NULL,NULL),(123,'order_request',88,'order_creation','COMPLETED',NULL,1,NULL,'2025-12-27 15:14:23','2025-12-28 15:09:47',NULL,NULL,NULL,NULL),(125,'order_request',89,'order_creation','FAILED',NULL,1,'NO_FREE_CELLS','2025-12-27 15:29:29','2025-12-28 15:09:47',NULL,NULL,NULL,NULL),(127,'order_request',90,'order_creation','FAILED',NULL,1,'NO_FREE_CELLS','2025-12-27 15:30:18','2025-12-29 06:58:01',NULL,NULL,NULL,NULL),(139,'order_request',91,'order_creation','COMPLETED',NULL,1,NULL,'2025-12-27 16:55:39','2025-12-29 06:58:01',NULL,NULL,NULL,NULL),(140,'order_request',93,'order_creation','FAILED',NULL,1,'NO_FREE_CELLS','2025-12-29 17:34:49','2025-12-31 09:47:42',NULL,NULL,NULL,NULL),(141,'order_request',92,'order_creation','FAILED',NULL,1,'NO_FREE_CELLS','2025-12-29 17:34:49','2025-12-31 09:47:42',NULL,NULL,NULL,NULL),(142,'order_request',94,'order_creation','FAILED',NULL,1,'NO_FREE_CELLS','2025-12-29 17:34:50','2025-12-31 09:47:42',NULL,NULL,NULL,NULL),(143,'trip',301,'trip_assign_driver','FAILED',NULL,1,'TARGET_USER_ID_NOT_SET','2025-12-29 18:36:41','2025-12-31 09:47:42',200,'driver',NULL,NULL),(144,'order',304,'cancel_order','FAILED',NULL,1,'CANCEL_NOT_ALLOWED_FOR_driver','2025-12-29 18:36:44','2026-01-17 09:17:39',200,'driver',NULL,NULL),(145,'trip',305,'arrive_at_destination','FAILED',NULL,1,'FSM trip_end_delivery: 1644 (45000): Unsupported entity_type in fsm_perform_action','2025-12-29 18:36:46','2026-01-01 17:48:43',200,'driver',NULL,NULL),(146,'order',305,'cancel_order','FAILED',NULL,1,'CANCEL_NOT_ALLOWED_FOR_driver','2025-12-29 18:36:56','2026-01-17 09:18:14',200,'driver',NULL,NULL),(147,'trip',305,'trip_assign_driver','FAILED',NULL,1,'TARGET_USER_ID_NOT_SET','2025-12-29 18:36:59','2025-12-31 09:47:42',200,'driver',NULL,NULL),(148,'order',201,'open_cell','FAILED',NULL,1,'ROLE_NOT_SUPPORTED_driver','2025-12-29 18:37:11','2025-12-31 09:47:42',200,'driver',NULL,NULL),(149,'order',203,'open_cell','FAILED',NULL,1,'ROLE_NOT_SUPPORTED_driver','2025-12-29 18:37:27','2025-12-31 09:47:42',200,'driver',NULL,NULL),(150,'order',306,'cancel_order','FAILED',NULL,1,'CANCEL_NOT_ALLOWED_FOR_driver','2025-12-29 18:37:37','2025-12-31 09:47:42',200,'driver',NULL,NULL),(151,'trip',302,'trip_assign_driver','FAILED',NULL,1,'TARGET_USER_ID_NOT_SET','2025-12-29 18:37:40','2025-12-31 09:47:42',200,'driver',NULL,NULL),(152,'trip',306,'trip_assign_driver','FAILED',NULL,1,'TARGET_USER_ID_NOT_SET','2025-12-29 18:37:49','2025-12-31 09:47:42',200,'driver',NULL,NULL),(153,'trip',304,'trip_assign_driver','FAILED',NULL,1,'TARGET_USER_ID_NOT_SET','2025-12-30 13:40:40','2025-12-31 09:47:42',200,'driver',NULL,NULL),(163,'order_request',95,'order_creation','FAILED',NULL,1,'NO_FREE_CELLS','2025-12-30 14:03:58','2025-12-31 09:47:42',NULL,NULL,NULL,NULL),(168,'order_request',96,'order_creation','FAILED',NULL,1,'NO_FREE_CELLS','2025-12-30 17:00:52','2025-12-31 09:47:42',NULL,NULL,NULL,NULL),(169,'order_request',97,'order_creation','FAILED',NULL,1,'NO_FREE_CELLS','2025-12-30 17:03:17','2025-12-31 09:47:42',NULL,NULL,NULL,NULL),(171,'order_request',98,'order_creation','FAILED',NULL,1,'NO_FREE_CELLS','2025-12-30 17:09:41','2025-12-31 09:47:42',NULL,NULL,NULL,NULL),(172,'order_request',99,'order_creation','FAILED',NULL,1,'NO_FREE_CELLS','2025-12-30 17:10:22','2025-12-31 09:47:42',NULL,NULL,NULL,NULL),(175,'order_request',100,'order_creation','FAILED',NULL,1,'NO_FREE_CELLS','2025-12-30 17:49:29','2025-12-31 09:47:42',NULL,NULL,NULL,NULL),(176,'order_request',101,'order_creation','FAILED',NULL,1,'NO_FREE_CELLS','2025-12-30 17:52:06','2025-12-31 09:47:42',NULL,NULL,NULL,NULL),(183,'order',202,'open_cell','FAILED',NULL,1,'ROLE_NOT_SUPPORTED_driver','2025-12-30 17:54:22','2025-12-31 09:47:43',200,'driver',NULL,NULL),(188,'trip',301,'start_trip','FAILED',NULL,1,'\'DatabaseLayer\' object has no attribute \'trip_start_trip\'','2025-12-30 17:54:44','2025-12-31 09:47:43',200,'driver',NULL,NULL),(190,'order',302,'cancel_order','FAILED',NULL,1,'CANCEL_NOT_ALLOWED_FOR_driver','2025-12-30 17:55:02','2025-12-31 09:47:43',200,'driver',NULL,NULL),(193,'order',301,'cancel_order','FAILED',NULL,1,'CANCEL_NOT_ALLOWED_FOR_driver','2025-12-30 17:55:13','2025-12-31 09:47:43',200,'driver',NULL,NULL),(195,'order_request',102,'order_creation','FAILED',NULL,1,'NO_FREE_CELLS','2025-12-30 19:43:43','2025-12-31 09:47:43',NULL,NULL,NULL,NULL),(196,'order_request',103,'order_creation','FAILED',NULL,1,'NO_FREE_CELLS','2025-12-30 19:49:57','2025-12-31 09:47:43',NULL,NULL,NULL,NULL),(197,'order_request',104,'order_creation','FAILED',NULL,1,'NO_FREE_CELLS','2025-12-31 09:50:17','2025-12-31 09:58:08',NULL,NULL,NULL,NULL),(198,'order_request',105,'order_creation','FAILED',NULL,1,'NO_FREE_CELLS','2025-12-31 11:09:27','2025-12-31 11:15:58',NULL,NULL,NULL,NULL),(199,'order_request',106,'order_creation','COMPLETED',NULL,1,NULL,'2025-12-31 11:19:12','2025-12-31 11:19:13',NULL,NULL,NULL,NULL),(200,'order_request',107,'order_creation','COMPLETED',NULL,1,NULL,'2026-01-01 13:22:50','2026-01-01 13:22:52',NULL,NULL,NULL,NULL),(201,'order_request',108,'order_creation','COMPLETED',NULL,1,NULL,'2026-01-01 13:23:50','2026-01-01 13:23:52',NULL,NULL,NULL,NULL),(205,'order_request',109,'order_creation','COMPLETED',NULL,1,NULL,'2026-01-02 10:48:14','2026-01-02 10:48:17',NULL,NULL,NULL,NULL),(208,'order_request',110,'order_creation','COMPLETED',NULL,1,NULL,'2026-01-02 11:09:22','2026-01-02 13:23:12',NULL,NULL,NULL,NULL),(209,'order_request',111,'order_creation','FAILED',NULL,1,'NO_FREE_CELLS','2026-01-02 11:09:34','2026-01-02 13:23:12',NULL,NULL,NULL,NULL),(210,'order',5,'trip_assign_driver','FAILED',NULL,1,'ASSIGNMENT_FAILED','2026-01-02 11:53:44','2026-02-06 10:49:43',200,'driver',200,NULL),(211,'order_request',112,'order_creation','FAILED',NULL,1,'NO_FREE_CELLS','2026-01-02 11:54:29','2026-01-02 13:23:12',NULL,NULL,NULL,NULL),(212,'order_request',113,'order_creation','FAILED',NULL,1,'NO_FREE_CELLS','2026-01-02 11:55:42','2026-01-02 13:23:12',NULL,NULL,NULL,NULL),(213,'order_request',114,'order_creation','FAILED',NULL,1,'NO_FREE_CELLS','2026-01-02 13:58:06','2026-01-06 13:10:03',NULL,NULL,NULL,NULL),(214,'order_request',115,'order_creation','FAILED',NULL,1,'NO_FREE_CELLS','2026-01-02 14:15:23','2026-01-06 13:10:03',NULL,NULL,NULL,NULL),(215,'order_request',116,'order_creation','FAILED',NULL,0,'STUCK_TIMEOUT','2026-01-06 13:15:59','2026-01-06 14:47:45',NULL,NULL,NULL,NULL),(216,'order_request',117,'order_creation','COMPLETED',NULL,1,NULL,'2026-01-06 15:00:13','2026-01-06 15:00:17',NULL,NULL,NULL,NULL),(217,'order',1413,'order_assign_courier1','COMPLETED',NULL,1,NULL,'2026-01-06 15:32:18','2026-01-06 15:32:23',1003,'client',1003,NULL),(218,'order_request',118,'order_creation','COMPLETED',NULL,1,NULL,'2026-01-09 17:03:26','2026-01-09 17:03:28',NULL,NULL,NULL,NULL),(219,'order_request',119,'order_creation','FAILED',NULL,1,'NO_FREE_CELLS','2026-01-09 17:41:53','2026-01-09 17:41:54',NULL,NULL,NULL,NULL),(220,'order',1411,'trip_assign_driver','FAILED',NULL,1,'TARGET_USER_ID_NOT_SET','2026-01-09 18:08:32','2026-01-09 18:08:35',200,'driver',NULL,NULL),(221,'order',1414,'trip_assign_driver','FAILED',NULL,1,'TARGET_USER_ID_NOT_SET','2026-01-09 18:08:37','2026-01-09 18:08:40',200,'driver',NULL,NULL),(222,'order_request',120,'order_creation','COMPLETED',NULL,1,NULL,'2026-01-09 18:09:14','2026-01-09 18:09:15',NULL,NULL,NULL,NULL),(223,'order_request',121,'order_creation','COMPLETED',NULL,1,NULL,'2026-01-09 18:09:48','2026-01-09 18:09:50',NULL,NULL,NULL,NULL),(224,'order_request',122,'order_creation','COMPLETED',NULL,1,NULL,'2026-01-09 18:15:57','2026-01-09 18:16:00',NULL,NULL,NULL,NULL),(225,'order_request',123,'order_creation','COMPLETED',NULL,1,NULL,'2026-01-09 18:17:30','2026-01-09 18:17:30',NULL,NULL,NULL,NULL),(226,'order_request',124,'order_creation','FAILED',NULL,1,'NO_FREE_CELLS','2026-01-10 08:42:22','2026-01-10 08:42:25',NULL,NULL,NULL,NULL),(227,'order_request',125,'order_creation','FAILED',NULL,1,'NO_FREE_CELLS','2026-01-10 08:53:37','2026-01-10 08:53:40',NULL,NULL,NULL,NULL),(228,'order_request',126,'order_creation','FAILED',NULL,1,'NO_FREE_CELLS','2026-01-10 08:55:10','2026-01-10 08:55:11',NULL,NULL,NULL,NULL),(229,'order_request',127,'order_creation','FAILED',NULL,1,'NO_FREE_CELLS','2026-01-10 08:56:04','2026-01-10 08:56:06',NULL,NULL,NULL,NULL),(230,'order_request',128,'order_creation','FAILED',NULL,1,'NO_FREE_CELLS','2026-01-10 08:59:02','2026-01-10 08:59:06',NULL,NULL,NULL,NULL),(231,'order_request',129,'order_creation','COMPLETED',NULL,1,NULL,'2026-01-11 11:45:15','2026-01-11 11:45:19',NULL,NULL,NULL,NULL),(232,'order_request',130,'order_creation','COMPLETED',NULL,1,NULL,'2026-01-11 12:34:50','2026-01-11 12:34:54',NULL,NULL,NULL,NULL),(233,'order_request',131,'order_creation','COMPLETED',NULL,1,NULL,'2026-01-11 12:40:09','2026-01-11 12:40:09',NULL,NULL,NULL,NULL),(234,'order_request',132,'order_creation','COMPLETED',NULL,1,NULL,'2026-01-11 14:14:40','2026-01-11 14:14:42',NULL,NULL,NULL,NULL),(235,'order_request',133,'order_creation','FAILED',NULL,1,'NO_FREE_CELLS','2026-01-12 10:14:59','2026-01-12 10:15:00',NULL,NULL,NULL,NULL),(236,'order_request',134,'order_creation','FAILED',NULL,1,'NO_FREE_CELLS','2026-01-12 10:15:56','2026-01-12 10:16:00',NULL,NULL,NULL,NULL),(237,'order_request',135,'order_creation','FAILED',NULL,1,'NO_FREE_CELLS','2026-01-12 10:17:22','2026-01-12 10:17:25',NULL,NULL,NULL,NULL),(238,'order_request',136,'order_creation','FAILED',NULL,1,'NO_FREE_CELLS','2026-01-12 11:50:29','2026-01-12 11:50:33',NULL,NULL,NULL,NULL),(239,'order_request',137,'order_creation','FAILED',NULL,1,'NO_FREE_CELLS','2026-01-12 11:50:48','2026-01-12 11:50:53',NULL,NULL,NULL,NULL),(240,'order_request',138,'order_creation','FAILED',NULL,1,'NO_FREE_CELLS','2026-01-12 11:56:06','2026-01-12 11:56:08',NULL,NULL,NULL,NULL),(241,'order_request',139,'order_creation','FAILED',NULL,1,'NO_FREE_CELLS','2026-01-12 12:00:26','2026-01-12 12:00:28',NULL,NULL,NULL,NULL),(242,'order_request',140,'order_creation','FAILED',NULL,1,'NO_FREE_CELLS','2026-01-12 12:01:18','2026-01-12 12:01:23',NULL,NULL,NULL,NULL),(243,'order_request',141,'order_creation','FAILED',NULL,1,'NO_FREE_CELLS','2026-01-12 12:02:52','2026-01-12 12:02:53',NULL,NULL,NULL,NULL),(244,'order_request',142,'order_creation','FAILED',NULL,1,'NO_FREE_CELLS','2026-01-12 12:08:20','2026-01-12 12:08:23',NULL,NULL,NULL,NULL),(245,'order_request',143,'order_creation','COMPLETED',NULL,1,NULL,'2026-01-12 12:13:19','2026-01-12 12:13:23',NULL,NULL,NULL,NULL),(246,'order_request',144,'order_creation','COMPLETED',NULL,1,NULL,'2026-01-12 14:47:07','2026-01-12 14:47:10',NULL,NULL,NULL,NULL),(247,'order_request',145,'order_creation','COMPLETED',NULL,1,NULL,'2026-01-12 14:47:45','2026-01-12 14:47:50',NULL,NULL,NULL,NULL),(248,'order_request',146,'order_creation','COMPLETED',NULL,1,NULL,'2026-01-12 14:49:24','2026-01-12 14:49:28',NULL,NULL,NULL,NULL),(249,'order_request',147,'order_creation','FAILED',NULL,1,'NO_FREE_CELLS','2026-01-12 14:49:49','2026-01-12 14:49:53',NULL,NULL,NULL,NULL),(250,'order_request',148,'order_creation','COMPLETED',NULL,1,NULL,'2026-01-12 15:50:00','2026-01-12 15:50:04',NULL,NULL,NULL,NULL),(251,'order_request',149,'order_creation','COMPLETED',NULL,1,NULL,'2026-01-12 15:50:37','2026-01-12 15:50:39',NULL,NULL,NULL,NULL),(252,'order_request',150,'order_creation','COMPLETED',NULL,1,NULL,'2026-01-12 15:52:46','2026-01-12 15:52:49',NULL,NULL,NULL,NULL),(253,'order_request',151,'order_creation','FAILED',NULL,1,'NO_FREE_CELLS','2026-01-12 16:15:26','2026-01-13 15:25:02',NULL,NULL,NULL,NULL),(254,'order_request',152,'order_creation','FAILED',NULL,1,'NO_FREE_CELLS','2026-01-12 16:15:29','2026-01-13 15:25:00',NULL,NULL,NULL,NULL),(255,'order_request',153,'order_creation','COMPLETED',NULL,1,NULL,'2026-01-12 16:18:37','2026-01-13 15:25:01',NULL,NULL,NULL,NULL),(256,'order_request',154,'order_creation','FAILED',NULL,1,'NO_FREE_CELLS','2026-01-12 16:21:59','2026-01-13 15:25:00',NULL,NULL,NULL,NULL),(257,'order_request',155,'order_creation','FAILED',NULL,1,'NO_FREE_CELLS','2026-01-12 16:23:16','2026-01-13 01:01:33',NULL,NULL,NULL,NULL),(258,'order_request',156,'order_creation','COMPLETED',NULL,1,NULL,'2026-01-13 07:54:40','2026-01-13 15:24:59',NULL,NULL,NULL,NULL),(259,'order_request',157,'order_creation','COMPLETED',NULL,1,NULL,'2026-01-13 07:55:58','2026-01-13 14:16:28',NULL,NULL,NULL,NULL),(260,'order_request',158,'order_creation','FAILED',NULL,1,'NO_FREE_CELLS','2026-01-13 07:58:59','2026-01-13 15:25:02',NULL,NULL,NULL,NULL),(261,'order_request',159,'order_creation','FAILED',NULL,1,'NO_FREE_CELLS','2026-01-13 08:00:47','2026-01-13 14:16:28',NULL,NULL,NULL,NULL),(262,'order_request',160,'order_creation','FAILED',NULL,1,'NO_FREE_CELLS','2026-01-13 08:01:29','2026-01-13 14:16:28',NULL,NULL,NULL,NULL),(263,'order_request',161,'order_creation','FAILED',NULL,1,'NO_FREE_CELLS','2026-01-13 08:22:44','2026-01-13 09:12:39',NULL,NULL,NULL,NULL),(264,'order',1428,'cancel_order','COMPLETED',NULL,1,NULL,'2026-01-13 08:39:38','2026-01-13 11:40:52',1002,'client',NULL,NULL),(266,'order',1425,'cancel_order','COMPLETED',NULL,1,NULL,'2026-01-13 08:46:49','2026-01-13 14:16:22',1003,'client',NULL,NULL),(268,'order_request',162,'order_creation','COMPLETED',NULL,1,NULL,'2026-01-13 08:47:16','2026-01-13 12:42:27',NULL,NULL,NULL,NULL),(269,'order',1429,'cancel_order','COMPLETED',NULL,1,NULL,'2026-01-13 08:48:14','2026-01-13 09:21:40',1004,'client',NULL,NULL),(275,'order_request',163,'order_creation','COMPLETED',NULL,1,NULL,'2026-01-13 09:23:48','2026-01-13 11:40:52',NULL,NULL,NULL,NULL),(276,'order_request',164,'order_creation','FAILED',NULL,1,'NO_FREE_CELLS','2026-01-13 15:27:13','2026-01-13 15:27:17',NULL,NULL,NULL,NULL),(277,'order_request',165,'order_creation','FAILED',NULL,1,'NO_FREE_CELLS','2026-01-13 15:34:52','2026-01-13 15:34:52',NULL,NULL,NULL,NULL),(278,'order_request',166,'order_creation','COMPLETED',NULL,1,NULL,'2026-01-13 15:53:22','2026-01-13 15:53:23',NULL,NULL,NULL,NULL),(279,'order_request',167,'order_creation','FAILED',NULL,1,'NO_FREE_CELLS','2026-01-13 18:15:03','2026-01-13 18:15:08',NULL,NULL,NULL,NULL),(280,'order_request',168,'order_creation','FAILED',NULL,1,'NO_FREE_CELLS','2026-01-13 18:17:13','2026-01-13 18:17:13',NULL,NULL,NULL,NULL),(281,'order_request',169,'order_creation','FAILED',NULL,1,'NO_FREE_CELLS','2026-01-13 18:18:02','2026-01-13 18:18:03',NULL,NULL,NULL,NULL),(282,'order',1436,'cancel_order','FAILED',NULL,1,'FSM order_cancel_reservation: 1644 (45000): Invalid transition for order: no matching fsm_transitions','2026-01-13 18:32:34','2026-01-14 10:08:54',1004,'client',NULL,NULL),(284,'order',1426,'cancel_order','COMPLETED',NULL,1,NULL,'2026-01-14 08:44:02','2026-01-14 10:08:55',1004,'client',NULL,NULL),(285,'order',1422,'cancel_order','FAILED',NULL,1,'FSM order_cancel_reservation: 1644 (45000): Invalid transition for order: no matching fsm_transitions','2026-01-15 07:41:44','2026-01-15 07:49:45',1001,'client',NULL,NULL),(287,'order',1421,'cancel_order','FAILED',NULL,1,'FSM locker_cancel_reservation: 1644 (45000): Invalid transition for locker: no matching fsm_transitions','2026-01-15 07:43:48','2026-01-15 07:43:50',1001,'client',NULL,NULL),(289,'order_request',170,'order_creation','FAILED',NULL,1,'NO_FREE_CELLS','2026-01-15 07:50:36','2026-01-15 07:50:40',NULL,NULL,NULL,NULL),(290,'order_request',171,'order_creation','COMPLETED',NULL,1,NULL,'2026-01-15 07:50:51','2026-01-15 07:50:55',NULL,NULL,NULL,NULL),(291,'order',1437,'cancel_order','COMPLETED',NULL,1,NULL,'2026-01-15 07:51:16','2026-01-15 07:51:20',1004,'client',NULL,NULL),(292,'order',1,'cancel_order','FAILED',NULL,1,'CANNOT_CANCEL_FROM_order_courier_failed','2026-01-15 07:57:16','2026-01-17 09:22:24',100,'courier',NULL,NULL),(293,'order',2,'cancel_order','FAILED',NULL,1,'CANNOT_CANCEL_FROM_order_reservation_expired','2026-01-15 07:57:38','2026-01-15 07:57:41',100,'courier',NULL,NULL),(294,'order',1361,'cancel_order','FAILED',NULL,1,'CANNOT_CANCEL_FROM_order_courier_failed','2026-01-15 07:57:51','2026-01-15 07:58:46',100,'courier',NULL,NULL),(297,'order_request',172,'order_creation','COMPLETED',NULL,1,NULL,'2026-01-15 08:01:09','2026-01-15 08:01:11',NULL,NULL,NULL,NULL),(298,'order',1435,'cancel_order','COMPLETED',NULL,1,NULL,'2026-01-15 09:46:29','2026-01-15 09:46:29',1003,'client',NULL,NULL),(299,'order',5,'order_assign_courier1','FAILED',NULL,1,'ASSIGNMENT_FAILED','2026-01-15 10:16:12','2026-01-17 09:19:49',100,'courier',100,NULL),(304,'order',1438,'cancel_order','COMPLETED',NULL,1,NULL,'2026-01-15 10:27:46','2026-01-15 10:27:51',1001,'client',NULL,NULL),(306,'order_request',173,'order_creation','COMPLETED',NULL,1,NULL,'2026-01-15 10:28:35','2026-01-15 10:28:36',NULL,NULL,NULL,NULL),(307,'order',1417,'cancel_order','COMPLETED',NULL,1,NULL,'2026-01-15 10:28:46','2026-01-15 10:28:51',1001,'client',NULL,NULL),(309,'order',5,'cancel_order','COMPLETED',NULL,1,NULL,'2026-01-15 10:36:58','2026-01-17 09:22:39',100,'courier',NULL,NULL),(311,'order_request',174,'order_creation','COMPLETED',NULL,1,NULL,'2026-01-15 12:46:44','2026-01-15 12:46:48',NULL,NULL,NULL,NULL),(312,'order_request',175,'order_creation','FAILED',NULL,1,'NO_FREE_CELLS','2026-01-15 12:50:36','2026-01-15 12:50:38',NULL,NULL,NULL,NULL),(313,'order_request',176,'order_creation','FAILED',NULL,1,'name \'apply_fsm_result\' is not defined','2026-01-15 12:50:51','2026-01-15 12:50:53',NULL,NULL,NULL,NULL),(314,'order',1407,'cancel_order','FAILED',NULL,1,'FSM locker_cancel_reservation: 1644 (45000): Invalid transition for locker: no matching fsm_transitions','2026-01-15 20:45:15','2026-01-15 20:45:18',1001,'client',NULL,NULL),(315,'order_request',177,'order_creation','FAILED',NULL,1,'NO_FREE_CELLS','2026-01-15 20:50:58','2026-01-15 20:50:58',NULL,NULL,NULL,NULL),(316,'order_request',178,'order_creation','FAILED',NULL,1,'NO_FREE_CELLS','2026-01-15 20:51:16','2026-01-15 20:51:18',NULL,NULL,NULL,NULL),(317,'order_request',179,'order_creation','FAILED',NULL,1,'NO_FREE_CELLS','2026-01-15 20:51:28','2026-01-15 20:51:28',NULL,NULL,NULL,NULL),(318,'order_request',180,'order_creation','FAILED',NULL,1,'NO_FREE_CELLS','2026-01-15 20:51:38','2026-01-15 20:51:38',NULL,NULL,NULL,NULL),(319,'order_request',181,'order_creation','FAILED',NULL,1,'NO_FREE_CELLS','2026-01-15 20:51:51','2026-01-15 20:51:53',NULL,NULL,NULL,NULL),(320,'order_request',182,'order_creation','FAILED',NULL,1,'name \'apply_fsm_result\' is not defined','2026-01-15 20:52:10','2026-01-15 20:52:14',NULL,NULL,NULL,NULL),(321,'order',1442,'order_assign_courier1','FAILED',NULL,1,'ASSIGNMENT_FAILED','2026-01-15 20:56:17','2026-01-15 20:56:24',100,'courier',100,NULL),(323,'order',1442,'cancel_order','FAILED',NULL,1,'CANNOT_CANCEL_FROM_order_created','2026-01-15 20:56:44','2026-01-15 20:56:59',100,'courier',NULL,NULL),(326,'order',4,'cancel_order','FAILED',NULL,1,'CANNOT_CANCEL_FROM_order_reservation_expired','2026-01-17 08:36:43','2026-01-17 08:36:47',100,'courier',NULL,NULL),(327,'order',301,'trip_assign_driver','FAILED',NULL,1,'TARGET_USER_ID_NOT_SET','2026-01-17 08:37:23','2026-01-17 09:22:59',200,'driver',NULL,NULL),(328,'order',10,'trip_assign_driver','FAILED',NULL,1,'ASSIGNMENT_FAILED','2026-01-17 08:37:54','2026-01-17 08:37:57',200,'driver',200,NULL),(330,'order',6,'trip_assign_driver','FAILED',NULL,1,'ASSIGNMENT_FAILED','2026-01-17 09:06:40','2026-01-19 12:15:57',200,'driver',200,NULL),(358,'order_request',183,'order_creation','COMPLETED',NULL,1,NULL,'2026-01-27 14:17:24','2026-01-27 14:17:24',NULL,NULL,NULL,NULL),(359,'order_request',184,'order_creation','FAILED',NULL,1,'NO_FREE_CELLS','2026-01-27 14:19:54','2026-01-27 14:19:55',NULL,NULL,NULL,NULL),(360,'order_request',185,'order_creation','FAILED',NULL,1,'NO_FREE_CELLS','2026-01-27 14:20:38','2026-01-27 14:20:40',NULL,NULL,NULL,NULL),(361,'order_request',186,'order_creation','COMPLETED',NULL,1,NULL,'2026-01-27 14:21:01','2026-01-27 14:21:05',NULL,NULL,NULL,NULL),(362,'order_request',187,'order_creation','FAILED',NULL,1,'create_order_from_request(187) failed: DatabaseLayer.mark_request_failed() got an unexpected keyword argument \'error_text\'','2026-01-28 08:14:19','2026-01-28 08:14:24',NULL,NULL,NULL,NULL),(363,'order_request',188,'order_creation','FAILED',NULL,1,'create_order_from_request(188) failed: DatabaseLayer.create_order_and_reserve_cells() got an unexpected keyword argument \'description\'','2026-01-28 08:38:04','2026-01-28 08:38:08',NULL,NULL,NULL,NULL),(364,'order_request',189,'order_creation','FAILED',NULL,1,'create_order_from_request(189) failed: name \'logger\' is not defined','2026-01-28 09:49:33','2026-01-28 09:49:34',NULL,NULL,NULL,NULL),(365,'order_request',190,'order_creation','FAILED',NULL,1,'NO_FREE_CELLS','2026-01-28 11:38:08','2026-01-28 11:38:11',NULL,NULL,NULL,NULL),(366,'order_request',191,'order_creation','COMPLETED',NULL,1,NULL,'2026-01-28 11:48:06','2026-01-28 11:48:06',NULL,NULL,NULL,NULL),(367,'order_request',192,'order_creation','COMPLETED',NULL,1,NULL,'2026-01-28 14:55:21','2026-01-28 14:55:23',NULL,NULL,NULL,NULL),(368,'order_request',193,'order_creation','FAILED',NULL,1,'NO_FREE_CELLS','2026-01-28 14:58:30','2026-01-28 14:58:33',NULL,NULL,NULL,NULL),(369,'order',1447,'cancel_order','COMPLETED',NULL,1,NULL,'2026-01-28 15:12:41','2026-01-28 15:12:44',1005,'client',NULL,NULL),(371,'order',1446,'cancel_order','COMPLETED',NULL,1,NULL,'2026-01-28 15:12:55','2026-01-28 15:12:59',1004,'client',NULL,NULL),(372,'order_request',194,'order_creation','COMPLETED',NULL,1,NULL,'2026-01-29 08:12:39','2026-01-29 08:12:40',NULL,NULL,NULL,NULL),(373,'order_request',195,'order_creation','COMPLETED',NULL,1,NULL,'2026-02-04 15:52:57','2026-02-04 15:52:58',NULL,NULL,NULL,NULL),(374,'order_request',196,'order_creation','COMPLETED',NULL,1,NULL,'2026-02-05 07:54:07','2026-02-05 07:58:29',NULL,NULL,NULL,NULL),(375,'order_request',197,'order_creation','COMPLETED',NULL,1,NULL,'2026-02-05 08:00:37','2026-02-05 08:00:39',NULL,NULL,NULL,NULL),(376,'order',1503,'cancel_order','COMPLETED',NULL,1,NULL,'2026-02-05 08:04:32','2026-02-05 08:25:26',1004,'client',NULL,NULL),(379,'order_request',198,'order_creation','COMPLETED',NULL,1,NULL,'2026-02-05 09:06:16','2026-02-05 09:06:17',NULL,NULL,NULL,NULL),(380,'order_request',199,'order_creation','FAILED',NULL,1,'NO_FREE_CELLS','2026-02-05 09:06:50','2026-02-05 09:06:52',NULL,NULL,NULL,NULL),(381,'order',1502,'order_assign_courier1','COMPLETED',NULL,1,NULL,'2026-02-05 09:11:43','2026-02-05 09:11:47',100,'courier',100,NULL),(382,'order_request',200,'order_creation','COMPLETED',NULL,1,NULL,'2026-02-06 05:52:47','2026-02-06 05:52:52',NULL,NULL,NULL,NULL),(383,'order_request',201,'order_creation','COMPLETED',NULL,1,NULL,'2026-02-06 05:53:08','2026-02-06 05:53:12',NULL,NULL,NULL,NULL),(384,'order_request',202,'order_creation','COMPLETED',NULL,1,NULL,'2026-02-06 05:53:28','2026-02-06 05:53:32',NULL,NULL,NULL,NULL),(385,'order_request',203,'order_creation','FAILED',NULL,1,'NO_FREE_CELLS','2026-02-06 05:53:40','2026-02-06 05:53:42',NULL,NULL,NULL,NULL),(386,'order_request',204,'order_creation','FAILED',NULL,1,'NO_FREE_CELLS','2026-02-06 05:53:43','2026-02-06 05:53:47',NULL,NULL,NULL,NULL),(387,'order_request',205,'order_creation','FAILED',NULL,1,'NO_FREE_CELLS','2026-02-06 05:53:49','2026-02-06 05:53:52',NULL,NULL,NULL,NULL),(390,'order',1507,'trip_assign_driver','FAILED',NULL,1,'ASSIGNMENT_FAILED','2026-02-06 10:43:28','2026-02-06 10:43:33',200,'driver',200,NULL),(394,'order',660,'trip_assign_driver','FAILED',NULL,1,'ASSIGNMENT_FAILED','2026-02-06 10:50:08','2026-02-06 10:50:13',200,'driver',200,NULL),(395,'order',660,'order_assign_courier1','FAILED',NULL,1,'ASSIGNMENT_FAILED','2026-02-06 10:52:04','2026-02-06 10:52:08',100,'courier',100,NULL),(396,'order_request',206,'order_creation','FAILED',NULL,1,'NO_FREE_CELLS','2026-02-06 16:31:36','2026-02-06 16:31:37',NULL,NULL,NULL,NULL),(397,'order_request',207,'order_creation','FAILED',NULL,1,'List argument must consist only of tuples or dictionaries','2026-02-08 12:08:59','2026-02-08 13:13:21',NULL,NULL,NULL,NULL),(398,'order_request',208,'order_creation','FAILED',NULL,1,'List argument must consist only of tuples or dictionaries','2026-02-08 12:38:24','2026-02-08 13:13:21',NULL,NULL,NULL,NULL),(399,'order_request',209,'order_creation','FAILED',NULL,1,'List argument must consist only of tuples or dictionaries','2026-02-08 12:50:37','2026-02-08 13:13:21',NULL,NULL,NULL,NULL),(400,'order_request',210,'order_creation','FAILED',NULL,1,'List argument must consist only of tuples or dictionaries','2026-02-08 12:56:31','2026-02-08 13:13:21',NULL,NULL,NULL,NULL),(401,'order_request',211,'order_creation','FAILED',NULL,1,'List argument must consist only of tuples or dictionaries','2026-02-08 13:03:35','2026-02-08 13:13:21',NULL,NULL,NULL,NULL),(402,'order_request',212,'order_creation','FAILED',NULL,1,'List argument must consist only of tuples or dictionaries','2026-02-08 13:11:13','2026-02-08 13:13:21',NULL,NULL,NULL,NULL),(403,'order_request',213,'order_creation','COMPLETED',NULL,1,NULL,'2026-02-08 13:22:41','2026-02-08 13:22:43',NULL,NULL,NULL,NULL),(404,'order',1508,'order_assign_courier1','COMPLETED',NULL,1,NULL,'2026-02-08 14:16:12','2026-02-08 14:17:49',100,'courier',100,NULL),(405,'order',1508,'cancel_order','COMPLETED',NULL,1,NULL,'2026-02-08 14:16:52','2026-02-08 14:18:09',100,'courier',NULL,NULL);

--
-- Table structure for table `stage_orders`
--

DROP TABLE IF EXISTS `stage_orders`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `stage_orders` (
  `trip_id` int NOT NULL,
  `order_id` int NOT NULL,
  `leg` enum('pickup','delivery') NOT NULL DEFAULT 'pickup',
  `courier_user_id` int DEFAULT NULL,
  PRIMARY KEY (`trip_id`,`order_id`,`leg`),
  KEY `order_id` (`order_id`),
  KEY `stage_orders_ibfk_courier` (`courier_user_id`),
  CONSTRAINT `stage_orders_ibfk_1` FOREIGN KEY (`trip_id`) REFERENCES `trips` (`id`) ON DELETE CASCADE,
  CONSTRAINT `stage_orders_ibfk_2` FOREIGN KEY (`order_id`) REFERENCES `orders` (`id`) ON DELETE CASCADE,
  CONSTRAINT `stage_orders_ibfk_courier` FOREIGN KEY (`courier_user_id`) REFERENCES `users` (`id`) ON DELETE SET NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `stage_orders`
--

INSERT  IGNORE INTO `stage_orders` VALUES (1,2,'pickup',NULL),(1,3,'pickup',NULL),(1,4,'pickup',NULL),(1,5,'pickup',NULL),(2,1361,'delivery',NULL),(2,1363,'pickup',NULL),(2,1364,'pickup',NULL),(2,1364,'delivery',NULL),(2,1365,'pickup',NULL),(2,1365,'delivery',NULL),(2,1369,'pickup',NULL),(2,1369,'delivery',NULL),(3,1362,'delivery',NULL),(3,1366,'pickup',NULL),(3,1366,'delivery',NULL),(3,1367,'pickup',NULL),(3,1367,'delivery',NULL),(3,1370,'pickup',NULL),(3,1370,'delivery',NULL),(3,1371,'pickup',NULL),(3,1371,'delivery',NULL),(4,1368,'pickup',NULL),(4,1368,'delivery',NULL),(4,1372,'pickup',NULL),(4,1372,'delivery',NULL),(4,1373,'delivery',NULL),(4,1374,'pickup',NULL),(4,1374,'delivery',NULL),(4,1375,'pickup',NULL),(4,1375,'delivery',NULL),(5,1376,'pickup',NULL),(5,1376,'delivery',NULL),(6,1377,'pickup',NULL),(6,1377,'delivery',NULL),(6,1378,'delivery',NULL),(6,1379,'delivery',NULL),(7,1380,'pickup',NULL),(7,1380,'delivery',NULL),(7,1381,'pickup',NULL),(7,1381,'delivery',NULL),(7,1382,'pickup',NULL),(7,1382,'delivery',NULL),(7,1383,'pickup',NULL),(7,1383,'delivery',NULL),(7,1384,'pickup',NULL),(7,1384,'delivery',NULL),(8,1385,'pickup',NULL),(8,1385,'delivery',NULL),(8,1386,'pickup',NULL),(8,1386,'delivery',NULL),(8,1387,'pickup',NULL),(8,1387,'delivery',NULL),(8,1388,'pickup',NULL),(8,1388,'delivery',NULL),(8,1389,'pickup',NULL),(8,1389,'delivery',NULL),(9,1390,'pickup',NULL),(9,1390,'delivery',NULL),(9,1391,'pickup',NULL),(9,1391,'delivery',NULL),(9,1392,'pickup',NULL),(9,1392,'delivery',NULL),(9,1393,'pickup',NULL),(9,1393,'delivery',NULL),(9,1394,'pickup',NULL),(9,1394,'delivery',NULL),(10,1395,'pickup',NULL),(10,1395,'delivery',NULL),(10,1396,'pickup',NULL),(10,1396,'delivery',NULL),(10,1397,'pickup',NULL),(10,1397,'delivery',NULL),(10,1398,'delivery',NULL),(10,1399,'delivery',NULL),(11,1400,'pickup',NULL),(11,1400,'delivery',NULL),(11,1401,'pickup',NULL),(11,1401,'delivery',NULL),(11,1402,'pickup',NULL),(11,1402,'delivery',NULL),(11,1403,'pickup',NULL),(11,1403,'delivery',NULL),(12,1404,'pickup',NULL),(12,1404,'delivery',NULL),(12,1405,'pickup',NULL),(12,1405,'delivery',NULL),(13,1406,'pickup',NULL),(13,1406,'delivery',NULL),(13,1407,'pickup',NULL),(13,1407,'delivery',NULL),(14,1408,'pickup',NULL),(14,1408,'delivery',NULL),(15,1409,'pickup',NULL),(15,1409,'delivery',NULL),(15,1410,'pickup',NULL),(15,1410,'delivery',NULL),(15,1411,'pickup',NULL),(15,1411,'delivery',NULL),(16,1412,'pickup',NULL),(16,1412,'delivery',NULL),(17,1413,'delivery',NULL),(18,1414,'pickup',NULL),(18,1414,'delivery',NULL),(18,1415,'pickup',NULL),(18,1415,'delivery',NULL),(18,1416,'pickup',NULL),(18,1416,'delivery',NULL),(18,1417,'pickup',NULL),(18,1417,'delivery',NULL),(18,1418,'pickup',NULL),(18,1418,'delivery',NULL),(19,1419,'pickup',NULL),(19,1419,'delivery',NULL),(19,1420,'pickup',NULL),(19,1420,'delivery',NULL),(19,1421,'pickup',NULL),(19,1421,'delivery',NULL),(19,1422,'pickup',NULL),(19,1422,'delivery',NULL),(20,1423,'pickup',NULL),(20,1423,'delivery',NULL),(20,1424,'pickup',NULL),(20,1424,'delivery',NULL),(20,1425,'pickup',NULL),(20,1425,'delivery',NULL),(20,1426,'pickup',NULL),(20,1426,'delivery',NULL),(20,1427,'pickup',NULL),(20,1427,'delivery',NULL),(21,1428,'pickup',NULL),(21,1428,'delivery',NULL),(21,1429,'pickup',NULL),(21,1429,'delivery',NULL),(21,1431,'pickup',NULL),(21,1431,'delivery',NULL),(21,1432,'pickup',NULL),(21,1432,'delivery',NULL),(21,1433,'pickup',NULL),(21,1433,'delivery',NULL),(22,1434,'pickup',NULL),(22,1434,'delivery',NULL),(22,1435,'pickup',NULL),(22,1435,'delivery',NULL),(22,1436,'pickup',NULL),(22,1436,'delivery',NULL),(23,1437,'pickup',NULL),(23,1437,'delivery',NULL),(23,1438,'pickup',NULL),(23,1438,'delivery',NULL),(23,1439,'pickup',NULL),(23,1439,'delivery',NULL),(23,1440,'pickup',NULL),(23,1440,'delivery',NULL),(23,1441,'pickup',NULL),(23,1441,'delivery',NULL),(24,1442,'pickup',NULL),(24,1442,'delivery',NULL),(25,1443,'pickup',NULL),(25,1443,'delivery',NULL),(25,1444,'pickup',NULL),(25,1444,'delivery',NULL),(25,1446,'pickup',NULL),(25,1446,'delivery',NULL),(26,1447,'pickup',NULL),(26,1447,'delivery',NULL),(26,1448,'pickup',NULL),(26,1448,'delivery',NULL),(27,1449,'pickup',NULL),(27,1449,'delivery',NULL),(27,1502,'delivery',NULL),(27,1503,'pickup',NULL),(27,1503,'delivery',NULL),(27,1504,'pickup',NULL),(27,1504,'delivery',NULL),(27,1505,'pickup',NULL),(27,1505,'delivery',NULL),(28,1506,'pickup',NULL),(28,1506,'delivery',NULL),(28,1507,'pickup',NULL),(28,1507,'delivery',NULL),(29,1508,'pickup',NULL),(29,1508,'delivery',NULL),(1,1,'pickup',2),(2,1361,'pickup',2),(3,1362,'pickup',2),(4,1373,'pickup',2),(6,1378,'pickup',2),(6,1379,'pickup',2),(10,1398,'pickup',2),(10,1399,'pickup',2),(27,1502,'pickup',100),(1,5,'delivery',303),(17,1413,'pickup',1003);

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
) ENGINE=InnoDB AUTO_INCREMENT=30 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `trips`
--

INSERT  IGNORE INTO `trips` VALUES (1,NULL,'Msk','Spb',1,1,'trip_created',NULL,1,'2025-11-24 16:33:51'),(2,NULL,'LOCAL','LOCAL',1,2,'trip_created',NULL,1,'2025-12-15 18:43:45'),(3,NULL,'LOCAL','LOCAL',1,2,'trip_created',NULL,1,'2025-12-15 19:20:44'),(4,NULL,'LOCAL','LOCAL',1,2,'trip_created',NULL,1,'2025-12-15 20:46:12'),(5,NULL,'LOCAL','LOCAL',2,1,'trip_created',NULL,1,'2025-12-16 10:56:06'),(6,NULL,'LOCAL','LOCAL',1,2,'trip_created',NULL,1,'2025-12-19 09:45:10'),(7,NULL,'LOCAL','LOCAL',1,2,'trip_created',NULL,1,'2025-12-23 16:35:14'),(8,NULL,'LOCAL','LOCAL',1,2,'trip_created',NULL,1,'2025-12-24 12:05:22'),(9,NULL,'LOCAL','LOCAL',1,2,'trip_created',NULL,1,'2025-12-24 15:40:49'),(10,NULL,'LOCAL','LOCAL',1,2,'trip_created',NULL,1,'2025-12-25 15:23:44'),(11,NULL,'LOCAL','LOCAL',1,2,'trip_created',NULL,1,'2025-12-26 13:38:37'),(12,NULL,'LOCAL','LOCAL',1,2,'trip_created',NULL,1,'2025-12-27 15:09:30'),(13,NULL,'LOCAL','LOCAL',1,2,'trip_created',NULL,1,'2025-12-28 15:09:47'),(14,NULL,'LOCAL','LOCAL',1,2,'trip_created',NULL,1,'2025-12-31 11:19:13'),(15,NULL,'LOCAL','LOCAL',1,2,'trip_created',NULL,1,'2026-01-01 13:22:51'),(16,NULL,'LOCAL','LOCAL',1,2,'trip_created',NULL,1,'2026-01-02 13:23:12'),(17,NULL,'LOCAL','LOCAL',1,2,'trip_created',NULL,1,'2026-01-06 15:00:17'),(18,NULL,'LOCAL','LOCAL',1,2,'trip_created',NULL,1,'2026-01-09 17:03:28'),(19,NULL,'LOCAL','LOCAL',1,2,'trip_created',NULL,1,'2026-01-11 11:45:19'),(20,NULL,'LOCAL','LOCAL',1,2,'trip_created',NULL,1,'2026-01-12 12:13:23'),(21,NULL,'LOCAL','LOCAL',1,2,'trip_created',NULL,1,'2026-01-12 15:50:39'),(22,NULL,'LOCAL','LOCAL',1,2,'trip_created',NULL,1,'2026-01-13 15:24:59'),(23,NULL,'LOCAL','LOCAL',1,2,'trip_created',NULL,1,'2026-01-15 07:50:55'),(24,NULL,'LOCAL','LOCAL',1,2,'trip_created',NULL,1,'2026-01-15 20:52:14'),(25,NULL,'LOCAL','LOCAL',1,2,'trip_created',NULL,1,'2026-01-27 14:17:24'),(26,NULL,'LOCAL','LOCAL',1,2,'trip_created',NULL,1,'2026-01-28 14:55:23'),(27,NULL,'LOCAL','LOCAL',1,2,'trip_created',NULL,0,'2026-02-04 15:52:58'),(28,NULL,'LOCAL','LOCAL',1,2,'trip_created',NULL,0,'2026-02-06 05:53:12'),(29,NULL,'СПБ','МСК',2,1,'trip_created',NULL,0,'2026-02-08 13:22:43');

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
  PRIMARY KEY (`id`),
  KEY `role_name` (`role_name`)
) ENGINE=InnoDB AUTO_INCREMENT=2006 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `users`
--

INSERT  IGNORE INTO `users` VALUES (1,'User 1','driver',''),(2,'User 2','courier',''),(3,'User 3','client',''),(4,'User 4','recipient',''),(5,'User 5','courier',''),(10,'Client','client',''),(20,'Courier1','courier',''),(21,'Courier2','courier',''),(30,'Driver','driver',''),(40,'Recipient','recipient',''),(100,'Курьер 100','courier','МСК'),(101,'Курьер 101','courier','МСК'),(102,'Курьер 102','courier','МСК'),(103,'Курьер 103','courier','СПБ'),(104,'Курьер 104','courier','СПБ'),(200,'Водитель 200','driver',''),(201,'Водитель 201','driver',''),(202,'Водитель 202','driver',''),(203,'Водитель 203','driver',''),(204,'Водитель 204','driver',''),(301,'Клиент Алиса','client',''),(302,'Курьер Борис','courier',''),(303,'Курьер Виктор','courier',''),(304,'Водитель Дима','driver',''),(305,'Получатель Ева','recipient',''),(777,'Оператор 777','operator',''),(888,'Оператор 888','operator',''),(1001,'Клиент 1001','client','МСК'),(1002,'Клиент 1002','client','МСК'),(1003,'Клиент 1003','client','МСК'),(1004,'Клиент 1004','client','СПБ'),(1005,'Клиент 1005','client','СПБ'),(2001,'Получатель 2001','recipient','МСК'),(2002,'Получатель 2002','recipient','МСК'),(2003,'Получатель 2003','recipient','МСК'),(2004,'Получатель 2004','recipient','СПБ'),(2005,'Получатель 2005','recipient','СПБ');

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
