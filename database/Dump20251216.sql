CREATE DATABASE  IF NOT EXISTS `testdb` /*!40100 DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci */ /*!80016 DEFAULT ENCRYPTION='N' */;
USE `testdb`;
-- MySQL dump 10.13  Distrib 8.0.44, for Win64 (x86_64)
--
-- Host: localhost    Database: testdb
-- ------------------------------------------------------
-- Server version	8.0.44-0ubuntu0.24.04.2

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
) ENGINE=InnoDB AUTO_INCREMENT=65 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
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
) ENGINE=InnoDB AUTO_INCREMENT=23 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `fsm_action_logs`
--

INSERT  IGNORE INTO `fsm_action_logs` VALUES (1,'order',1,'order_reserve_for_courier_A_to_B','order_created','order_courier_reserved_post1_and_post2',20,'2025-11-24 16:33:51');
INSERT  IGNORE INTO `fsm_action_logs` VALUES (2,'locker',2,'locker_reserve_cell','locker_free','locker_reserved',20,'2025-11-24 16:33:51');
INSERT  IGNORE INTO `fsm_action_logs` VALUES (3,'locker',12,'locker_reserve_cell','locker_free','locker_reserved',20,'2025-11-24 16:33:51');
INSERT  IGNORE INTO `fsm_action_logs` VALUES (4,'order',2,'order_reserve_for_courier_A_to_B','order_created','order_courier_reserved_post1_and_post2',20,'2025-11-24 16:33:51');
INSERT  IGNORE INTO `fsm_action_logs` VALUES (5,'locker',3,'locker_reserve_cell','locker_free','locker_reserved',20,'2025-11-24 16:33:51');
INSERT  IGNORE INTO `fsm_action_logs` VALUES (6,'locker',13,'locker_reserve_cell','locker_free','locker_reserved',20,'2025-11-24 16:33:51');
INSERT  IGNORE INTO `fsm_action_logs` VALUES (7,'order',3,'order_reserve_for_courier_A_to_B','order_created','order_courier_reserved_post1_and_post2',20,'2025-11-24 16:33:52');
INSERT  IGNORE INTO `fsm_action_logs` VALUES (8,'locker',4,'locker_reserve_cell','locker_free','locker_reserved',20,'2025-11-24 16:33:52');
INSERT  IGNORE INTO `fsm_action_logs` VALUES (9,'locker',14,'locker_reserve_cell','locker_free','locker_reserved',20,'2025-11-24 16:33:52');
INSERT  IGNORE INTO `fsm_action_logs` VALUES (10,'order',4,'order_reserve_for_courier_A_to_B','order_created','order_courier_reserved_post1_and_post2',20,'2025-11-24 16:33:52');
INSERT  IGNORE INTO `fsm_action_logs` VALUES (11,'locker',5,'locker_reserve_cell','locker_free','locker_reserved',20,'2025-11-24 16:33:52');
INSERT  IGNORE INTO `fsm_action_logs` VALUES (12,'locker',15,'locker_reserve_cell','locker_free','locker_reserved',20,'2025-11-24 16:33:52');
INSERT  IGNORE INTO `fsm_action_logs` VALUES (13,'order',1,'order_timeout_reservation','order_courier_reserved_post1_and_post2','order_reservation_expired',0,'2025-11-24 16:36:07');
INSERT  IGNORE INTO `fsm_action_logs` VALUES (14,'order',2,'order_timeout_reservation','order_courier_reserved_post1_and_post2','order_reservation_expired',0,'2025-11-24 16:36:07');
INSERT  IGNORE INTO `fsm_action_logs` VALUES (15,'order',3,'order_timeout_reservation','order_courier_reserved_post1_and_post2','order_reservation_expired',0,'2025-11-24 16:36:08');
INSERT  IGNORE INTO `fsm_action_logs` VALUES (16,'order',4,'order_timeout_reservation','order_courier_reserved_post1_and_post2','order_reservation_expired',0,'2025-11-24 16:36:08');
INSERT  IGNORE INTO `fsm_action_logs` VALUES (17,'order',1,'order_assign_courier1_to_order','order_courier_reserved_post1_and_post2','order_courier1_assigned',2,'2025-12-15 13:34:29');
INSERT  IGNORE INTO `fsm_action_logs` VALUES (20,'order',1361,'order_assign_courier1_to_order','order_created','order_courier1_assigned',2,'2025-12-15 18:47:35');
INSERT  IGNORE INTO `fsm_action_logs` VALUES (21,'order',1362,'order_assign_courier1_to_order','order_created','order_courier1_assigned',2,'2025-12-15 19:24:09');
INSERT  IGNORE INTO `fsm_action_logs` VALUES (22,'order',1373,'order_assign_courier1_to_order','order_created','order_courier1_assigned',2,'2025-12-16 07:22:00');

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
) ENGINE=InnoDB AUTO_INCREMENT=106 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
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
) ENGINE=InnoDB AUTO_INCREMENT=131 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
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
INSERT  IGNORE INTO `fsm_transitions` VALUES (57,81,3,4);
INSERT  IGNORE INTO `fsm_transitions` VALUES (58,82,79,83);
INSERT  IGNORE INTO `fsm_transitions` VALUES (59,83,4,5);
INSERT  IGNORE INTO `fsm_transitions` VALUES (60,4,80,82);
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
INSERT  IGNORE INTO `fsm_transitions` VALUES (77,89,69,103);
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

INSERT  IGNORE INTO `locker_cells` VALUES (1,1,'S-01','S','locker_free',NULL,NULL,NULL,NULL,NULL,0,'2025-11-22 15:23:13','2025-12-16 09:59:55');
INSERT  IGNORE INTO `locker_cells` VALUES (2,1,'S-02','S','locker_free',NULL,NULL,NULL,NULL,NULL,0,'2025-11-22 15:23:13','2025-12-16 09:59:55');
INSERT  IGNORE INTO `locker_cells` VALUES (3,1,'S-03','S','locker_free',NULL,NULL,NULL,NULL,NULL,0,'2025-11-22 15:23:13','2025-12-16 09:59:55');
INSERT  IGNORE INTO `locker_cells` VALUES (4,1,'S-04','S','locker_free',NULL,NULL,NULL,NULL,NULL,0,'2025-11-22 15:23:13','2025-12-15 19:56:28');
INSERT  IGNORE INTO `locker_cells` VALUES (5,1,'M-01','M','locker_free',NULL,NULL,NULL,NULL,NULL,0,'2025-11-22 15:23:13','2025-12-15 17:28:19');
INSERT  IGNORE INTO `locker_cells` VALUES (6,1,'M-02','M','locker_free',NULL,NULL,NULL,NULL,NULL,0,'2025-11-22 15:23:13','2025-12-15 17:28:19');
INSERT  IGNORE INTO `locker_cells` VALUES (7,1,'L-01','L','locker_free',NULL,NULL,NULL,NULL,NULL,0,'2025-11-22 15:23:13','2025-12-15 17:28:19');
INSERT  IGNORE INTO `locker_cells` VALUES (8,1,'L-02','L','locker_free',NULL,NULL,NULL,NULL,NULL,0,'2025-11-22 15:23:13','2025-12-15 17:28:19');
INSERT  IGNORE INTO `locker_cells` VALUES (9,1,'P-01','P','locker_free',NULL,NULL,NULL,NULL,NULL,0,'2025-11-22 15:23:13','2025-12-15 17:28:19');
INSERT  IGNORE INTO `locker_cells` VALUES (10,1,'P-02','P','locker_free',NULL,NULL,NULL,NULL,NULL,0,'2025-11-22 15:23:13','2025-12-15 17:28:19');
INSERT  IGNORE INTO `locker_cells` VALUES (11,2,'S-01','S','locker_reserved',NULL,NULL,NULL,NULL,1375,0,'2025-11-22 15:23:13','2025-12-16 10:03:20');
INSERT  IGNORE INTO `locker_cells` VALUES (12,2,'S-02','S','locker_free',NULL,NULL,NULL,NULL,NULL,0,'2025-11-22 15:23:13','2025-12-16 09:59:55');
INSERT  IGNORE INTO `locker_cells` VALUES (13,2,'S-03','S','locker_free',NULL,NULL,NULL,NULL,NULL,0,'2025-11-22 15:23:13','2025-12-16 09:59:55');
INSERT  IGNORE INTO `locker_cells` VALUES (14,2,'S-04','S','locker_free',NULL,NULL,NULL,NULL,NULL,0,'2025-11-22 15:23:13','2025-12-16 09:59:55');
INSERT  IGNORE INTO `locker_cells` VALUES (15,2,'M-01','M','locker_free',NULL,NULL,NULL,NULL,NULL,0,'2025-11-22 15:23:13','2025-12-15 17:34:52');
INSERT  IGNORE INTO `locker_cells` VALUES (16,2,'M-02','M','locker_free',NULL,NULL,NULL,NULL,NULL,0,'2025-11-22 15:23:13','2025-12-15 17:34:52');
INSERT  IGNORE INTO `locker_cells` VALUES (17,2,'L-01','L','locker_free',NULL,NULL,NULL,NULL,NULL,0,'2025-11-22 15:23:13','2025-12-15 17:34:52');
INSERT  IGNORE INTO `locker_cells` VALUES (18,2,'L-02','L','locker_free',NULL,NULL,NULL,NULL,NULL,0,'2025-11-22 15:23:13','2025-12-15 17:34:52');
INSERT  IGNORE INTO `locker_cells` VALUES (19,2,'P-01','P','locker_free',NULL,NULL,NULL,NULL,NULL,0,'2025-11-22 15:23:13','2025-12-15 17:34:52');
INSERT  IGNORE INTO `locker_cells` VALUES (20,2,'P-02','P','locker_free',NULL,NULL,NULL,NULL,NULL,0,'2025-11-22 15:23:13','2025-12-15 17:34:52');
INSERT  IGNORE INTO `locker_cells` VALUES (21,3,'S-01','S','locker_free',NULL,NULL,NULL,NULL,NULL,0,'2025-11-22 15:23:13','2025-11-22 15:23:13');
INSERT  IGNORE INTO `locker_cells` VALUES (22,3,'S-02','S','locker_free',NULL,NULL,NULL,NULL,NULL,0,'2025-11-22 15:23:13','2025-11-22 15:23:13');
INSERT  IGNORE INTO `locker_cells` VALUES (23,3,'S-03','S','locker_free',NULL,NULL,NULL,NULL,NULL,0,'2025-11-22 15:23:13','2025-11-22 15:23:13');
INSERT  IGNORE INTO `locker_cells` VALUES (24,3,'S-04','S','locker_free',NULL,NULL,NULL,NULL,NULL,0,'2025-11-22 15:23:13','2025-11-22 15:23:13');
INSERT  IGNORE INTO `locker_cells` VALUES (25,3,'M-01','M','locker_free',NULL,NULL,NULL,NULL,NULL,0,'2025-11-22 15:23:13','2025-11-22 15:23:13');
INSERT  IGNORE INTO `locker_cells` VALUES (26,3,'M-02','M','locker_free',NULL,NULL,NULL,NULL,NULL,0,'2025-11-22 15:23:13','2025-11-22 15:23:13');
INSERT  IGNORE INTO `locker_cells` VALUES (27,3,'L-01','L','locker_free',NULL,NULL,NULL,NULL,NULL,0,'2025-11-22 15:23:13','2025-11-22 15:23:13');
INSERT  IGNORE INTO `locker_cells` VALUES (28,3,'L-02','L','locker_free',NULL,NULL,NULL,NULL,NULL,0,'2025-11-22 15:23:13','2025-11-22 15:23:13');
INSERT  IGNORE INTO `locker_cells` VALUES (29,3,'P-01','P','locker_free',NULL,NULL,NULL,NULL,NULL,0,'2025-11-22 15:23:13','2025-11-22 15:23:13');
INSERT  IGNORE INTO `locker_cells` VALUES (30,3,'P-02','P','locker_free',NULL,NULL,NULL,NULL,NULL,0,'2025-11-22 15:23:13','2025-11-22 15:23:13');
INSERT  IGNORE INTO `locker_cells` VALUES (31,4,'S-01','S','locker_free',NULL,NULL,NULL,NULL,NULL,0,'2025-11-22 15:23:13','2025-11-22 15:23:13');
INSERT  IGNORE INTO `locker_cells` VALUES (32,4,'S-02','S','locker_free',NULL,NULL,NULL,NULL,NULL,0,'2025-11-22 15:23:13','2025-11-22 15:23:13');
INSERT  IGNORE INTO `locker_cells` VALUES (33,4,'S-03','S','locker_free',NULL,NULL,NULL,NULL,NULL,0,'2025-11-22 15:23:13','2025-11-22 15:23:13');
INSERT  IGNORE INTO `locker_cells` VALUES (34,4,'S-04','S','locker_free',NULL,NULL,NULL,NULL,NULL,0,'2025-11-22 15:23:13','2025-11-22 15:23:13');
INSERT  IGNORE INTO `locker_cells` VALUES (35,4,'M-01','M','locker_free',NULL,NULL,NULL,NULL,NULL,0,'2025-11-22 15:23:13','2025-11-22 15:23:13');
INSERT  IGNORE INTO `locker_cells` VALUES (36,4,'M-02','M','locker_free',NULL,NULL,NULL,NULL,NULL,0,'2025-11-22 15:23:13','2025-11-22 15:23:13');
INSERT  IGNORE INTO `locker_cells` VALUES (37,4,'L-01','L','locker_free',NULL,NULL,NULL,NULL,NULL,0,'2025-11-22 15:23:13','2025-11-22 15:23:13');
INSERT  IGNORE INTO `locker_cells` VALUES (38,4,'L-02','L','locker_free',NULL,NULL,NULL,NULL,NULL,0,'2025-11-22 15:23:13','2025-11-22 15:23:13');
INSERT  IGNORE INTO `locker_cells` VALUES (39,4,'P-01','P','locker_free',NULL,NULL,NULL,NULL,NULL,0,'2025-11-22 15:23:13','2025-11-22 15:23:13');
INSERT  IGNORE INTO `locker_cells` VALUES (40,4,'P-02','P','locker_free',NULL,NULL,NULL,NULL,NULL,0,'2025-11-22 15:23:13','2025-11-22 15:23:13');
INSERT  IGNORE INTO `locker_cells` VALUES (41,1,'A01','S','locker_reserved',NULL,NULL,NULL,NULL,1374,0,'2025-11-23 20:39:10','2025-12-16 10:03:20');
INSERT  IGNORE INTO `locker_cells` VALUES (42,1,'A02','S','locker_reserved',NULL,NULL,NULL,NULL,1375,0,'2025-11-23 20:39:10','2025-12-16 10:03:20');
INSERT  IGNORE INTO `locker_cells` VALUES (43,1,'A03','M','locker_reserved',NULL,NULL,NULL,NULL,1376,0,'2025-11-23 20:39:10','2025-12-16 10:11:58');
INSERT  IGNORE INTO `locker_cells` VALUES (44,2,'B01','S','locker_reserved',NULL,NULL,NULL,NULL,1374,0,'2025-11-23 20:39:10','2025-12-16 10:03:20');
INSERT  IGNORE INTO `locker_cells` VALUES (45,2,'B02','M','locker_reserved',NULL,NULL,NULL,NULL,1376,0,'2025-11-23 20:39:10','2025-12-16 10:11:58');
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

INSERT  IGNORE INTO `lockers` VALUES (1,1,'POST1','Точка #1',NULL,NULL,'locker_inactive','2025-11-22 15:22:48');
INSERT  IGNORE INTO `lockers` VALUES (2,1,'POST2','Точка #2',NULL,NULL,'locker_inactive','2025-11-22 15:22:48');
INSERT  IGNORE INTO `lockers` VALUES (3,1,'POST3','Точка #3',NULL,NULL,'locker_inactive','2025-11-22 15:22:48');
INSERT  IGNORE INTO `lockers` VALUES (4,1,'POST4','Точка #4',NULL,NULL,'locker_inactive','2025-11-22 15:22:48');

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
  `error_code` varchar(50) DEFAULT NULL,
  `error_message` text,
  `created_at` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=43 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `order_requests`
--

INSERT  IGNORE INTO `order_requests` VALUES (1,0,'string','string','string','string','FAILED',NULL,'NOT_IMPLEMENTED','order_creation handler not implemented yet','2025-12-07 13:53:25');
INSERT  IGNORE INTO `order_requests` VALUES (2,0,'string','string','string','string','FAILED',NULL,'NO_FREE_CELLS','Не найдены свободные ячейки нужного размера','2025-12-07 16:37:12');
INSERT  IGNORE INTO `order_requests` VALUES (3,1005,'test','S','courier','courier','COMPLETED',6,NULL,NULL,'2025-12-07 16:45:30');
INSERT  IGNORE INTO `order_requests` VALUES (4,1006,'test','L','courier','courier','COMPLETED',7,NULL,NULL,'2025-12-07 16:54:49');
INSERT  IGNORE INTO `order_requests` VALUES (5,1007,'test','M','courier','courier','COMPLETED',8,NULL,NULL,'2025-12-07 17:08:22');
INSERT  IGNORE INTO `order_requests` VALUES (6,1008,'test','M','courier','courier','COMPLETED',9,NULL,NULL,'2025-12-07 17:17:26');
INSERT  IGNORE INTO `order_requests` VALUES (7,1009,'test','L','courier','courier','COMPLETED',10,NULL,NULL,'2025-12-07 17:19:20');
INSERT  IGNORE INTO `order_requests` VALUES (8,402,'documents','M','courier','courier','FAILED',NULL,'NO_FREE_CELLS','Не найдены свободные ячейки нужного размера','2025-12-11 09:43:29');
INSERT  IGNORE INTO `order_requests` VALUES (9,391,'documents','S','courier','courier','COMPLETED',660,NULL,NULL,'2025-12-12 08:32:33');
INSERT  IGNORE INTO `order_requests` VALUES (10,491,'documents','M','courier','courier','FAILED',NULL,'NO_FREE_CELLS','Не найдены свободные ячейки нужного размера','2025-12-12 09:38:45');
INSERT  IGNORE INTO `order_requests` VALUES (11,471,'documents','L','courier','courier','FAILED',NULL,'NO_FREE_CELLS','Не найдены свободные ячейки нужного размера','2025-12-12 09:39:44');
INSERT  IGNORE INTO `order_requests` VALUES (12,461,'documents','S','courier','courier','FAILED',NULL,'NO_FREE_CELLS','Не найдены свободные ячейки нужного размера','2025-12-12 09:46:20');
INSERT  IGNORE INTO `order_requests` VALUES (13,467,'documents','P','courier','courier','COMPLETED',661,NULL,NULL,'2025-12-12 09:55:53');
INSERT  IGNORE INTO `order_requests` VALUES (14,463,'documents','А','courier','courier','FAILED',NULL,'NO_FREE_CELLS','Не найдены свободные ячейки нужного размера','2025-12-12 10:16:43');
INSERT  IGNORE INTO `order_requests` VALUES (15,493,'documents','P','courier','courier','COMPLETED',662,NULL,NULL,'2025-12-12 10:50:14');
INSERT  IGNORE INTO `order_requests` VALUES (16,589,'documents','P','courier','courier','FAILED',NULL,'NO_FREE_CELLS','Не найдены свободные ячейки нужного размера','2025-12-12 12:40:43');
INSERT  IGNORE INTO `order_requests` VALUES (17,559,'documents','P','courier','courier','FAILED',NULL,'NO_FREE_CELLS','Не найдены свободные ячейки нужного размера','2025-12-12 13:32:58');
INSERT  IGNORE INTO `order_requests` VALUES (18,584,'documents','P','courier','courier','FAILED',NULL,'NO_FREE_CELLS','Не найдены свободные ячейки нужного размера','2025-12-12 14:22:45');
INSERT  IGNORE INTO `order_requests` VALUES (19,544,'documents','S','courier','courier','FAILED',NULL,'NO_FREE_CELLS','Не найдены свободные ячейки нужного размера','2025-12-12 16:06:43');
INSERT  IGNORE INTO `order_requests` VALUES (20,591,'documents','S','courier','courier','FAILED',NULL,'NO_FREE_CELLS','Не найдены свободные ячейки нужного размера','2025-12-12 16:21:18');
INSERT  IGNORE INTO `order_requests` VALUES (21,1,'Документы','S','courier','courier','COMPLETED',1361,NULL,NULL,'2025-12-15 17:31:14');
INSERT  IGNORE INTO `order_requests` VALUES (22,1,'Финальный тест','S','courier','courier','COMPLETED',1362,NULL,NULL,'2025-12-15 19:20:14');
INSERT  IGNORE INTO `order_requests` VALUES (23,1,'Заказ A','S','courier','courier','FAILED',NULL,'TEST_CLEANUP','Не найдены свободные ячейки нужного размера','2025-12-15 19:41:42');
INSERT  IGNORE INTO `order_requests` VALUES (24,1,'Заказ B','S','courier','courier','FAILED',NULL,'TEST_CLEANUP','Не найдены свободные ячейки нужного размера','2025-12-15 19:41:42');
INSERT  IGNORE INTO `order_requests` VALUES (25,1,'Заказ A','S','courier','courier','FAILED',NULL,'NO_FREE_CELLS','Не найдены свободные ячейки нужного размера','2025-12-15 19:50:09');
INSERT  IGNORE INTO `order_requests` VALUES (26,1,'Заказ B','S','courier','courier','FAILED',NULL,'NO_FREE_CELLS','Не найдены свободные ячейки нужного размера','2025-12-15 19:50:09');
INSERT  IGNORE INTO `order_requests` VALUES (27,1,'Заказ 1','S','courier','courier','FAILED',1364,NULL,NULL,'2025-12-15 19:56:56');
INSERT  IGNORE INTO `order_requests` VALUES (28,1,'Заказ 2','S','courier','courier','FAILED',1365,NULL,NULL,'2025-12-15 19:56:56');
INSERT  IGNORE INTO `order_requests` VALUES (29,1,'Тест А','S','courier','courier','COMPLETED',1366,NULL,NULL,'2025-12-15 20:33:22');
INSERT  IGNORE INTO `order_requests` VALUES (30,1,'Тест Б','S','courier','courier','COMPLETED',1367,NULL,NULL,'2025-12-15 20:33:22');
INSERT  IGNORE INTO `order_requests` VALUES (31,1,'Проверка trip 2','S','courier','courier','COMPLETED',1368,NULL,NULL,'2025-12-15 20:46:10');
INSERT  IGNORE INTO `order_requests` VALUES (32,1,'Debug test','S','courier','courier','COMPLETED',1369,NULL,NULL,'2025-12-16 06:00:28');
INSERT  IGNORE INTO `order_requests` VALUES (33,1,'Test trip 3','S','courier','courier','COMPLETED',1370,NULL,NULL,'2025-12-16 06:04:57');
INSERT  IGNORE INTO `order_requests` VALUES (34,1,'Тест 1','S','courier','courier','PENDING',NULL,NULL,NULL,'2025-12-16 06:48:21');
INSERT  IGNORE INTO `order_requests` VALUES (35,1,'Тест 2','S','courier','courier','COMPLETED',1371,NULL,NULL,'2025-12-16 06:48:21');
INSERT  IGNORE INTO `order_requests` VALUES (36,1,'Тест 3','S','courier','courier','COMPLETED',1372,NULL,NULL,'2025-12-16 06:48:21');
INSERT  IGNORE INTO `order_requests` VALUES (37,1,'Тест 4','S','courier','courier','COMPLETED',1373,NULL,NULL,'2025-12-16 06:48:21');
INSERT  IGNORE INTO `order_requests` VALUES (38,1,'Тест 5','S','courier','courier','FAILED',NULL,'NO_FREE_CELLS','Не найдены свободные ячейки нужного размера','2025-12-16 06:48:21');
INSERT  IGNORE INTO `order_requests` VALUES (39,1,'Тест 1→2 A','S','courier','courier','PENDING',NULL,NULL,NULL,'2025-12-16 10:00:14');
INSERT  IGNORE INTO `order_requests` VALUES (40,1,'Тест 1→2 B','S','courier','courier','PENDING',NULL,NULL,NULL,'2025-12-16 10:00:14');
INSERT  IGNORE INTO `order_requests` VALUES (41,1,'Тест локер A','S','courier','courier','COMPLETED',1374,NULL,NULL,'2025-12-16 10:02:26');
INSERT  IGNORE INTO `order_requests` VALUES (42,1,'Тест локер B','S','courier','courier','COMPLETED',1375,NULL,NULL,'2025-12-16 10:02:26');

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
  `pickup_type` enum('self','courier') DEFAULT 'courier',
  `from_city` varchar(100) DEFAULT NULL,
  `to_city` varchar(100) DEFAULT NULL,
  `source_cell_id` int DEFAULT NULL,
  `dest_cell_id` int DEFAULT NULL,
  `updated_at` datetime DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  `created_at` datetime DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  KEY `source_cell_id` (`source_cell_id`),
  KEY `dest_cell_id` (`dest_cell_id`),
  CONSTRAINT `orders_ibfk_1` FOREIGN KEY (`source_cell_id`) REFERENCES `locker_cells` (`id`),
  CONSTRAINT `orders_ibfk_2` FOREIGN KEY (`dest_cell_id`) REFERENCES `locker_cells` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=1377 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `orders`
--

INSERT  IGNORE INTO `orders` VALUES (1,'order_courier_failed','Timeout Order','courier','courier','Msk','Spb',2,12,'2025-12-16 09:46:53','2025-11-24 16:33:51');
INSERT  IGNORE INTO `orders` VALUES (2,'order_reservation_expired','Trip Order 1','courier','courier','Msk','Spb',3,13,'2025-11-24 16:36:07','2025-11-24 16:33:51');
INSERT  IGNORE INTO `orders` VALUES (3,'order_reservation_expired','Trip Order 2','courier','courier','Msk','Spb',4,14,'2025-11-24 16:36:08','2025-11-24 16:33:51');
INSERT  IGNORE INTO `orders` VALUES (4,'order_reservation_expired','Trip Order 3','courier','courier','Msk','Spb',5,15,'2025-11-24 16:36:08','2025-11-24 16:33:52');
INSERT  IGNORE INTO `orders` VALUES (5,'order_created','Order','courier','courier','Msk','Spb',2,5,'2025-11-26 16:25:34','2025-11-26 16:25:34');
INSERT  IGNORE INTO `orders` VALUES (6,'order_created','test (S)','courier','courier','LOCAL','LOCAL',41,44,'2025-12-07 17:02:57','2025-12-07 17:02:57');
INSERT  IGNORE INTO `orders` VALUES (7,'order_created','test (L)','courier','courier','LOCAL','LOCAL',7,17,'2025-12-07 17:02:58','2025-12-07 17:02:58');
INSERT  IGNORE INTO `orders` VALUES (8,'order_created','test (M)','courier','courier','LOCAL','LOCAL',43,45,'2025-12-07 17:17:06','2025-12-07 17:17:06');
INSERT  IGNORE INTO `orders` VALUES (9,'order_created','test (M)','courier','courier','LOCAL','LOCAL',6,16,'2025-12-07 17:18:55','2025-12-07 17:18:55');
INSERT  IGNORE INTO `orders` VALUES (10,'order_created','test (L)','courier','courier','LOCAL','LOCAL',8,18,'2025-12-07 17:19:25','2025-12-07 17:19:25');
INSERT  IGNORE INTO `orders` VALUES (660,'order_created','documents (S)','courier','courier','LOCAL','LOCAL',42,11,'2025-12-12 09:26:46','2025-12-12 09:26:46');
INSERT  IGNORE INTO `orders` VALUES (661,'order_created','documents (P)','courier','courier','LOCAL','LOCAL',9,19,'2025-12-12 09:55:55','2025-12-12 09:55:55');
INSERT  IGNORE INTO `orders` VALUES (662,'order_created','documents (P)','courier','courier','LOCAL','LOCAL',10,20,'2025-12-12 10:50:17','2025-12-12 10:50:17');
INSERT  IGNORE INTO `orders` VALUES (1361,'order_courier_failed','Документы (S)','courier','courier','LOCAL','LOCAL',41,44,'2025-12-16 09:46:53','2025-12-15 18:43:45');
INSERT  IGNORE INTO `orders` VALUES (1362,'order_courier_failed','Финальный тест (S)','courier','courier','LOCAL','LOCAL',42,11,'2025-12-16 09:46:53','2025-12-15 19:20:44');
INSERT  IGNORE INTO `orders` VALUES (1363,'order_created','Заказ A (S)','courier','courier','LOCAL','LOCAL',1,12,'2025-12-15 19:42:02','2025-12-15 19:42:02');
INSERT  IGNORE INTO `orders` VALUES (1364,'order_created','Заказ 1 (S)','courier','courier','LOCAL','LOCAL',41,44,'2025-12-15 19:57:16','2025-12-15 19:57:16');
INSERT  IGNORE INTO `orders` VALUES (1365,'order_created','Заказ 2 (S)','courier','courier','LOCAL','LOCAL',42,11,'2025-12-15 19:57:16','2025-12-15 19:57:16');
INSERT  IGNORE INTO `orders` VALUES (1366,'order_created','Тест А (S)','courier','courier','LOCAL','LOCAL',41,44,'2025-12-15 20:33:36','2025-12-15 20:33:36');
INSERT  IGNORE INTO `orders` VALUES (1367,'order_created','Тест Б (S)','courier','courier','LOCAL','LOCAL',42,11,'2025-12-15 20:33:36','2025-12-15 20:33:36');
INSERT  IGNORE INTO `orders` VALUES (1368,'order_created','Проверка trip 2 (S)','courier','courier','LOCAL','LOCAL',41,44,'2025-12-15 20:46:12','2025-12-15 20:46:12');
INSERT  IGNORE INTO `orders` VALUES (1369,'order_created','Debug test (S)','courier','courier','LOCAL','LOCAL',41,44,'2025-12-16 06:00:46','2025-12-16 06:00:46');
INSERT  IGNORE INTO `orders` VALUES (1370,'order_created','Test trip 3 (S)','courier','courier','LOCAL','LOCAL',42,11,'2025-12-16 06:05:01','2025-12-16 06:05:01');
INSERT  IGNORE INTO `orders` VALUES (1371,'order_created','Тест 2 (S)','courier','courier','LOCAL','LOCAL',1,12,'2025-12-16 06:50:03','2025-12-16 06:50:03');
INSERT  IGNORE INTO `orders` VALUES (1372,'order_created','Тест 3 (S)','courier','courier','LOCAL','LOCAL',2,13,'2025-12-16 06:50:03','2025-12-16 06:50:03');
INSERT  IGNORE INTO `orders` VALUES (1373,'order_courier_failed','Тест 4 (S)','courier','courier','LOCAL','LOCAL',3,14,'2025-12-16 09:46:53','2025-12-16 06:50:04');
INSERT  IGNORE INTO `orders` VALUES (1374,'order_created','Тест локер A (S)','courier','courier','LOCAL','LOCAL',41,44,'2025-12-16 10:03:20','2025-12-16 10:03:20');
INSERT  IGNORE INTO `orders` VALUES (1375,'order_created','Тест локер B (S)','courier','courier','LOCAL','LOCAL',42,11,'2025-12-16 10:03:20','2025-12-16 10:03:20');
INSERT  IGNORE INTO `orders` VALUES (1376,'order_created','Тест 2→1','courier','courier','LOCAL','LOCAL',45,43,'2025-12-16 10:11:32','2025-12-16 10:11:32');
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
) ENGINE=InnoDB AUTO_INCREMENT=53 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `server_fsm_instances`
--

INSERT  IGNORE INTO `server_fsm_instances` VALUES (1,'order_request',1,'order_creation','FAILED',NULL,1,'NOT_IMPLEMENTED','2025-12-07 13:53:25','2025-12-07 14:17:02',NULL,NULL,NULL,NULL);
INSERT  IGNORE INTO `server_fsm_instances` VALUES (2,'order_request',2,'order_creation','FAILED',NULL,1,'NO_FREE_CELLS','2025-12-07 16:37:12','2025-12-07 16:38:43',NULL,NULL,NULL,NULL);
INSERT  IGNORE INTO `server_fsm_instances` VALUES (3,'order_request',3,'order_creation','COMPLETED',NULL,1,NULL,'2025-12-07 16:45:30','2025-12-07 17:02:57',NULL,NULL,NULL,NULL);
INSERT  IGNORE INTO `server_fsm_instances` VALUES (4,'order_request',4,'order_creation','COMPLETED',NULL,1,NULL,'2025-12-07 16:54:49','2025-12-07 17:02:58',NULL,NULL,NULL,NULL);
INSERT  IGNORE INTO `server_fsm_instances` VALUES (5,'order_request',5,'order_creation','COMPLETED',NULL,1,NULL,'2025-12-07 17:08:22','2025-12-07 17:17:06',NULL,NULL,NULL,NULL);
INSERT  IGNORE INTO `server_fsm_instances` VALUES (6,'order_request',6,'order_creation','COMPLETED',NULL,1,NULL,'2025-12-07 17:17:26','2025-12-07 17:18:55',NULL,NULL,NULL,NULL);
INSERT  IGNORE INTO `server_fsm_instances` VALUES (7,'order_request',7,'order_creation','COMPLETED',NULL,1,NULL,'2025-12-07 17:19:20','2025-12-07 17:19:25',NULL,NULL,NULL,NULL);
INSERT  IGNORE INTO `server_fsm_instances` VALUES (8,'order_request',8,'order_creation','FAILED',NULL,1,'NO_FREE_CELLS','2025-12-11 09:43:29','2025-12-11 09:43:34',NULL,NULL,NULL,NULL);
INSERT  IGNORE INTO `server_fsm_instances` VALUES (9,'order_request',9,'order_creation','COMPLETED',NULL,1,NULL,'2025-12-12 08:32:33','2025-12-12 09:26:46',NULL,NULL,NULL,NULL);
INSERT  IGNORE INTO `server_fsm_instances` VALUES (10,'order_request',10,'order_creation','FAILED',NULL,1,'NO_FREE_CELLS','2025-12-12 09:38:45','2025-12-12 09:38:46',NULL,NULL,NULL,NULL);
INSERT  IGNORE INTO `server_fsm_instances` VALUES (11,'order_request',11,'order_creation','FAILED',NULL,1,'NO_FREE_CELLS','2025-12-12 09:39:44','2025-12-12 09:39:46',NULL,NULL,NULL,NULL);
INSERT  IGNORE INTO `server_fsm_instances` VALUES (12,'order_request',12,'order_creation','FAILED',NULL,1,'NO_FREE_CELLS','2025-12-12 09:46:20','2025-12-12 09:46:21',NULL,NULL,NULL,NULL);
INSERT  IGNORE INTO `server_fsm_instances` VALUES (13,'order_request',13,'order_creation','COMPLETED',NULL,1,NULL,'2025-12-12 09:55:53','2025-12-12 09:55:55',NULL,NULL,NULL,NULL);
INSERT  IGNORE INTO `server_fsm_instances` VALUES (14,'order_request',14,'order_creation','FAILED',NULL,1,'NO_FREE_CELLS','2025-12-12 10:16:43','2025-12-12 10:16:46',NULL,NULL,NULL,NULL);
INSERT  IGNORE INTO `server_fsm_instances` VALUES (15,'order_request',15,'order_creation','COMPLETED',NULL,1,NULL,'2025-12-12 10:50:14','2025-12-12 10:50:17',NULL,NULL,NULL,NULL);
INSERT  IGNORE INTO `server_fsm_instances` VALUES (16,'order_request',16,'order_creation','FAILED',NULL,1,'NO_FREE_CELLS','2025-12-12 12:40:43','2025-12-12 12:40:48',NULL,NULL,NULL,NULL);
INSERT  IGNORE INTO `server_fsm_instances` VALUES (17,'order_request',17,'order_creation','FAILED',NULL,1,'NO_FREE_CELLS','2025-12-12 13:32:58','2025-12-12 13:33:00',NULL,NULL,NULL,NULL);
INSERT  IGNORE INTO `server_fsm_instances` VALUES (18,'order_request',18,'order_creation','FAILED',NULL,1,'NO_FREE_CELLS','2025-12-12 14:22:45','2025-12-12 14:22:48',NULL,NULL,NULL,NULL);
INSERT  IGNORE INTO `server_fsm_instances` VALUES (19,'order_request',19,'order_creation','FAILED',NULL,1,'NO_FREE_CELLS','2025-12-12 16:06:43','2025-12-12 16:11:51',NULL,NULL,NULL,NULL);
INSERT  IGNORE INTO `server_fsm_instances` VALUES (20,'order_request',20,'order_creation','FAILED',NULL,1,'NO_FREE_CELLS','2025-12-12 16:21:18','2025-12-12 16:21:22',NULL,NULL,NULL,NULL);
INSERT  IGNORE INTO `server_fsm_instances` VALUES (21,'order',1,'order_assign_courier1','FAILED',NULL,1,'ASSIGNMENT_FAILED','2025-12-15 07:42:38','2025-12-15 16:40:04',1,'driver',2,'courier');
INSERT  IGNORE INTO `server_fsm_instances` VALUES (24,'order',6,'order_assign_courier1','FAILED',NULL,1,'ASSIGNMENT_FAILED','2025-12-15 16:49:32','2025-12-15 17:23:59',1,'driver',2,'courier');
INSERT  IGNORE INTO `server_fsm_instances` VALUES (26,'order_request',21,'order_creation','COMPLETED',NULL,1,NULL,'2025-12-15 17:31:35','2025-12-15 18:43:45',NULL,NULL,NULL,NULL);
INSERT  IGNORE INTO `server_fsm_instances` VALUES (27,'order',1361,'order_assign_courier1','FAILED',NULL,1,'ASSIGNMENT_FAILED','2025-12-15 18:47:30','2025-12-15 18:47:35',1,'driver',2,'courier');
INSERT  IGNORE INTO `server_fsm_instances` VALUES (28,'order_request',22,'order_creation','COMPLETED',NULL,1,NULL,'2025-12-15 19:20:40','2025-12-15 19:20:44',NULL,NULL,NULL,NULL);
INSERT  IGNORE INTO `server_fsm_instances` VALUES (29,'order',1362,'order_assign_courier1','COMPLETED',NULL,1,NULL,'2025-12-15 19:24:05','2025-12-15 19:24:09',1,'driver',2,'courier');
INSERT  IGNORE INTO `server_fsm_instances` VALUES (32,'order_request',25,'order_creation','FAILED',NULL,1,'NO_FREE_CELLS','2025-12-15 19:50:38','2025-12-15 19:50:42',NULL,NULL,NULL,NULL);
INSERT  IGNORE INTO `server_fsm_instances` VALUES (33,'order_request',26,'order_creation','FAILED',NULL,1,'NO_FREE_CELLS','2025-12-15 19:50:38','2025-12-15 19:50:42',NULL,NULL,NULL,NULL);
INSERT  IGNORE INTO `server_fsm_instances` VALUES (36,'order_request',29,'order_creation','COMPLETED',NULL,1,NULL,'2025-12-15 20:33:34','2025-12-15 20:33:36',NULL,NULL,NULL,NULL);
INSERT  IGNORE INTO `server_fsm_instances` VALUES (37,'order_request',30,'order_creation','COMPLETED',NULL,1,NULL,'2025-12-15 20:33:34','2025-12-15 20:33:36',NULL,NULL,NULL,NULL);
INSERT  IGNORE INTO `server_fsm_instances` VALUES (38,'order_request',31,'order_creation','COMPLETED',NULL,1,NULL,'2025-12-15 20:46:10','2025-12-15 20:46:12',NULL,NULL,NULL,NULL);
INSERT  IGNORE INTO `server_fsm_instances` VALUES (39,'order_request',32,'order_creation','COMPLETED',NULL,1,NULL,'2025-12-16 06:00:45','2025-12-16 06:00:46',NULL,NULL,NULL,NULL);
INSERT  IGNORE INTO `server_fsm_instances` VALUES (40,'order_request',33,'order_creation','COMPLETED',NULL,1,NULL,'2025-12-16 06:04:57','2025-12-16 06:05:01',NULL,NULL,NULL,NULL);
INSERT  IGNORE INTO `server_fsm_instances` VALUES (41,'order_request',35,'order_creation','COMPLETED',NULL,1,NULL,'2025-12-16 06:49:59','2025-12-16 06:50:03',NULL,NULL,NULL,NULL);
INSERT  IGNORE INTO `server_fsm_instances` VALUES (42,'order_request',36,'order_creation','COMPLETED',NULL,1,NULL,'2025-12-16 06:49:59','2025-12-16 06:50:04',NULL,NULL,NULL,NULL);
INSERT  IGNORE INTO `server_fsm_instances` VALUES (43,'order_request',37,'order_creation','COMPLETED',NULL,1,NULL,'2025-12-16 06:49:59','2025-12-16 06:50:04',NULL,NULL,NULL,NULL);
INSERT  IGNORE INTO `server_fsm_instances` VALUES (44,'order_request',38,'order_creation','FAILED',NULL,1,'NO_FREE_CELLS','2025-12-16 06:49:59','2025-12-16 06:50:04',NULL,NULL,NULL,NULL);
INSERT  IGNORE INTO `server_fsm_instances` VALUES (45,'order_request',39,'order_creation','FAILED',NULL,1,'ORDER_REQUEST_NOT_FOUND','2025-12-16 06:49:59','2025-12-16 06:50:04',NULL,NULL,NULL,NULL);
INSERT  IGNORE INTO `server_fsm_instances` VALUES (46,'order',1373,'order_assign_courier1','COMPLETED',NULL,1,NULL,'2025-12-16 07:21:59','2025-12-16 07:22:00',1,'driver',2,'courier');
INSERT  IGNORE INTO `server_fsm_instances` VALUES (51,'order_request',41,'order_creation','COMPLETED',NULL,1,NULL,'2025-12-16 10:03:17','2025-12-16 10:03:20',NULL,NULL,NULL,NULL);
INSERT  IGNORE INTO `server_fsm_instances` VALUES (52,'order_request',42,'order_creation','COMPLETED',NULL,1,NULL,'2025-12-16 10:03:17','2025-12-16 10:03:20',NULL,NULL,NULL,NULL);

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

INSERT  IGNORE INTO `stage_orders` VALUES (1,2,'pickup',NULL);
INSERT  IGNORE INTO `stage_orders` VALUES (1,3,'pickup',NULL);
INSERT  IGNORE INTO `stage_orders` VALUES (1,4,'pickup',NULL);
INSERT  IGNORE INTO `stage_orders` VALUES (1,5,'pickup',NULL);
INSERT  IGNORE INTO `stage_orders` VALUES (2,1361,'delivery',NULL);
INSERT  IGNORE INTO `stage_orders` VALUES (2,1363,'pickup',NULL);
INSERT  IGNORE INTO `stage_orders` VALUES (2,1364,'pickup',NULL);
INSERT  IGNORE INTO `stage_orders` VALUES (2,1364,'delivery',NULL);
INSERT  IGNORE INTO `stage_orders` VALUES (2,1365,'pickup',NULL);
INSERT  IGNORE INTO `stage_orders` VALUES (2,1365,'delivery',NULL);
INSERT  IGNORE INTO `stage_orders` VALUES (2,1369,'pickup',NULL);
INSERT  IGNORE INTO `stage_orders` VALUES (2,1369,'delivery',NULL);
INSERT  IGNORE INTO `stage_orders` VALUES (3,1362,'delivery',NULL);
INSERT  IGNORE INTO `stage_orders` VALUES (3,1366,'pickup',NULL);
INSERT  IGNORE INTO `stage_orders` VALUES (3,1366,'delivery',NULL);
INSERT  IGNORE INTO `stage_orders` VALUES (3,1367,'pickup',NULL);
INSERT  IGNORE INTO `stage_orders` VALUES (3,1367,'delivery',NULL);
INSERT  IGNORE INTO `stage_orders` VALUES (3,1370,'pickup',NULL);
INSERT  IGNORE INTO `stage_orders` VALUES (3,1370,'delivery',NULL);
INSERT  IGNORE INTO `stage_orders` VALUES (3,1371,'pickup',NULL);
INSERT  IGNORE INTO `stage_orders` VALUES (3,1371,'delivery',NULL);
INSERT  IGNORE INTO `stage_orders` VALUES (4,1368,'pickup',NULL);
INSERT  IGNORE INTO `stage_orders` VALUES (4,1368,'delivery',NULL);
INSERT  IGNORE INTO `stage_orders` VALUES (4,1372,'pickup',NULL);
INSERT  IGNORE INTO `stage_orders` VALUES (4,1372,'delivery',NULL);
INSERT  IGNORE INTO `stage_orders` VALUES (4,1373,'delivery',NULL);
INSERT  IGNORE INTO `stage_orders` VALUES (4,1374,'pickup',NULL);
INSERT  IGNORE INTO `stage_orders` VALUES (4,1374,'delivery',NULL);
INSERT  IGNORE INTO `stage_orders` VALUES (4,1375,'pickup',NULL);
INSERT  IGNORE INTO `stage_orders` VALUES (4,1375,'delivery',NULL);
INSERT  IGNORE INTO `stage_orders` VALUES (5,1376,'pickup',NULL);
INSERT  IGNORE INTO `stage_orders` VALUES (5,1376,'delivery',NULL);
INSERT  IGNORE INTO `stage_orders` VALUES (1,1,'pickup',2);
INSERT  IGNORE INTO `stage_orders` VALUES (2,1361,'pickup',2);
INSERT  IGNORE INTO `stage_orders` VALUES (3,1362,'pickup',2);
INSERT  IGNORE INTO `stage_orders` VALUES (4,1373,'pickup',2);
INSERT  IGNORE INTO `stage_orders` VALUES (1,5,'delivery',303);

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
) ENGINE=InnoDB AUTO_INCREMENT=6 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `trips`
--

INSERT  IGNORE INTO `trips` VALUES (1,NULL,'Msk','Spb',1,1,'trip_created',NULL,1,'2025-11-24 16:33:51');
INSERT  IGNORE INTO `trips` VALUES (2,NULL,'LOCAL','LOCAL',1,2,'trip_created',NULL,1,'2025-12-15 18:43:45');
INSERT  IGNORE INTO `trips` VALUES (3,NULL,'LOCAL','LOCAL',1,2,'trip_created',NULL,1,'2025-12-15 19:20:44');
INSERT  IGNORE INTO `trips` VALUES (4,NULL,'LOCAL','LOCAL',1,2,'trip_created',NULL,1,'2025-12-15 20:46:12');
INSERT  IGNORE INTO `trips` VALUES (5,NULL,'LOCAL','LOCAL',2,1,'trip_created',NULL,0,'2025-12-16 10:56:06');

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
  PRIMARY KEY (`id`),
  KEY `role_name` (`role_name`)
) ENGINE=InnoDB AUTO_INCREMENT=306 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `users`
--

INSERT  IGNORE INTO `users` VALUES (1,'User 1','driver');
INSERT  IGNORE INTO `users` VALUES (2,'User 2','courier');
INSERT  IGNORE INTO `users` VALUES (3,'User 3','client');
INSERT  IGNORE INTO `users` VALUES (4,'User 4','recipient');
INSERT  IGNORE INTO `users` VALUES (5,'User 5','courier');
INSERT  IGNORE INTO `users` VALUES (10,'Client','client');
INSERT  IGNORE INTO `users` VALUES (20,'Courier1','courier');
INSERT  IGNORE INTO `users` VALUES (21,'Courier2','courier');
INSERT  IGNORE INTO `users` VALUES (30,'Driver','driver');
INSERT  IGNORE INTO `users` VALUES (40,'Recipient','recipient');
INSERT  IGNORE INTO `users` VALUES (301,'Клиент Алиса','client');
INSERT  IGNORE INTO `users` VALUES (302,'Курьер Борис','courier');
INSERT  IGNORE INTO `users` VALUES (303,'Курьер Виктор','courier');
INSERT  IGNORE INTO `users` VALUES (304,'Водитель Дима','driver');
INSERT  IGNORE INTO `users` VALUES (305,'Получатель Ева','recipient');

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
/*!50106 DROP EVENT IF EXISTS `courier_timeout_event` */;;
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
/*!50106 CREATE*/ /*!50117 DEFINER=`fsm`@`localhost`*/ /*!50106 EVENT `courier_timeout_event` ON SCHEDULE EVERY 1 MINUTE STARTS '2025-12-16 09:46:53' ON COMPLETION NOT PRESERVE ENABLE DO BEGIN
    UPDATE orders
    SET status = 'order_courier_failed'
    WHERE status = 'order_courier1_assigned'
      AND updated_at < NOW() - INTERVAL 15 MINUTE;
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
