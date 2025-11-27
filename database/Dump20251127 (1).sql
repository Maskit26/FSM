CREATE DATABASE  IF NOT EXISTS `testdb` /*!40100 DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci */ /*!80016 DEFAULT ENCRYPTION='N' */;
USE `testdb`;
-- MySQL dump 10.13  Distrib 8.0.44, for Win64 (x86_64)
--
-- Host: 127.0.0.1    Database: testdb
-- ------------------------------------------------------
-- Server version	8.0.43

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
) ENGINE=InnoDB AUTO_INCREMENT=17 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
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
) ENGINE=InnoDB AUTO_INCREMENT=130 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
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
INSERT  IGNORE INTO `fsm_transitions` VALUES (67,85,49,49);
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

INSERT  IGNORE INTO `locker_cells` VALUES (1,1,'S-01','S','locker_free',NULL,NULL,NULL,NULL,NULL,0,'2025-11-22 15:23:13','2025-11-24 16:33:51');
INSERT  IGNORE INTO `locker_cells` VALUES (2,1,'S-02','S','locker_reserved',NULL,NULL,NULL,NULL,NULL,0,'2025-11-22 15:23:13','2025-11-24 16:33:51');
INSERT  IGNORE INTO `locker_cells` VALUES (3,1,'S-03','S','locker_reserved',NULL,NULL,NULL,NULL,NULL,0,'2025-11-22 15:23:13','2025-11-24 16:33:51');
INSERT  IGNORE INTO `locker_cells` VALUES (4,1,'S-04','S','locker_reserved',NULL,NULL,NULL,NULL,NULL,0,'2025-11-22 15:23:13','2025-11-24 16:33:52');
INSERT  IGNORE INTO `locker_cells` VALUES (5,1,'M-01','M','locker_reserved',NULL,NULL,NULL,NULL,NULL,0,'2025-11-22 15:23:13','2025-11-24 16:33:52');
INSERT  IGNORE INTO `locker_cells` VALUES (6,1,'M-02','M','locker_free',NULL,NULL,NULL,NULL,NULL,0,'2025-11-22 15:23:13','2025-11-24 16:33:51');
INSERT  IGNORE INTO `locker_cells` VALUES (7,1,'L-01','L','locker_free',NULL,NULL,NULL,NULL,NULL,0,'2025-11-22 15:23:13','2025-11-24 16:33:51');
INSERT  IGNORE INTO `locker_cells` VALUES (8,1,'L-02','L','locker_free',NULL,NULL,NULL,NULL,NULL,0,'2025-11-22 15:23:13','2025-11-24 16:33:51');
INSERT  IGNORE INTO `locker_cells` VALUES (9,1,'P-01','P','locker_free',NULL,NULL,NULL,NULL,NULL,0,'2025-11-22 15:23:13','2025-11-24 12:00:38');
INSERT  IGNORE INTO `locker_cells` VALUES (10,1,'P-02','P','locker_free',NULL,NULL,NULL,NULL,NULL,0,'2025-11-22 15:23:13','2025-11-24 12:00:38');
INSERT  IGNORE INTO `locker_cells` VALUES (11,2,'S-01','S','locker_free',NULL,NULL,NULL,NULL,NULL,0,'2025-11-22 15:23:13','2025-11-24 16:33:51');
INSERT  IGNORE INTO `locker_cells` VALUES (12,2,'S-02','S','locker_reserved',NULL,NULL,NULL,NULL,NULL,0,'2025-11-22 15:23:13','2025-11-24 16:33:51');
INSERT  IGNORE INTO `locker_cells` VALUES (13,2,'S-03','S','locker_reserved',NULL,NULL,NULL,NULL,NULL,0,'2025-11-22 15:23:13','2025-11-24 16:33:51');
INSERT  IGNORE INTO `locker_cells` VALUES (14,2,'S-04','S','locker_reserved',NULL,NULL,NULL,NULL,NULL,0,'2025-11-22 15:23:13','2025-11-24 16:33:52');
INSERT  IGNORE INTO `locker_cells` VALUES (15,2,'M-01','M','locker_reserved',NULL,NULL,NULL,NULL,NULL,0,'2025-11-22 15:23:13','2025-11-24 16:33:52');
INSERT  IGNORE INTO `locker_cells` VALUES (16,2,'M-02','M','locker_free',NULL,NULL,NULL,NULL,NULL,0,'2025-11-22 15:23:13','2025-11-24 16:33:51');
INSERT  IGNORE INTO `locker_cells` VALUES (17,2,'L-01','L','locker_free',NULL,NULL,NULL,NULL,NULL,0,'2025-11-22 15:23:13','2025-11-24 16:33:51');
INSERT  IGNORE INTO `locker_cells` VALUES (18,2,'L-02','L','locker_free',NULL,NULL,NULL,NULL,NULL,0,'2025-11-22 15:23:13','2025-11-24 16:33:51');
INSERT  IGNORE INTO `locker_cells` VALUES (19,2,'P-01','P','locker_free',NULL,NULL,NULL,NULL,NULL,0,'2025-11-22 15:23:13','2025-11-24 12:00:38');
INSERT  IGNORE INTO `locker_cells` VALUES (20,2,'P-02','P','locker_free',NULL,NULL,NULL,NULL,NULL,0,'2025-11-22 15:23:13','2025-11-24 12:00:38');
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
INSERT  IGNORE INTO `locker_cells` VALUES (41,1,'A01','S','locker_free',NULL,NULL,NULL,NULL,NULL,0,'2025-11-23 20:39:10','2025-11-24 12:00:38');
INSERT  IGNORE INTO `locker_cells` VALUES (42,1,'A02','S','locker_free',NULL,NULL,NULL,NULL,NULL,0,'2025-11-23 20:39:10','2025-11-24 12:00:38');
INSERT  IGNORE INTO `locker_cells` VALUES (43,1,'A03','M','locker_free',NULL,NULL,NULL,NULL,NULL,0,'2025-11-23 20:39:10','2025-11-24 07:00:10');
INSERT  IGNORE INTO `locker_cells` VALUES (44,2,'B01','S','locker_free',NULL,NULL,NULL,NULL,NULL,0,'2025-11-23 20:39:10','2025-11-24 12:00:38');
INSERT  IGNORE INTO `locker_cells` VALUES (45,2,'B02','M','locker_free',NULL,NULL,NULL,NULL,NULL,0,'2025-11-23 20:39:10','2025-11-24 12:00:38');
/*!50003 SET @saved_cs_client      = @@character_set_client */ ;
/*!50003 SET @saved_cs_results     = @@character_set_results */ ;
/*!50003 SET @saved_col_connection = @@collation_connection */ ;
/*!50003 SET character_set_client  = utf8mb4 */ ;
/*!50003 SET character_set_results = utf8mb4 */ ;
/*!50003 SET collation_connection  = utf8mb4_0900_ai_ci */ ;
/*!50003 SET @saved_sql_mode       = @@sql_mode */ ;
/*!50003 SET sql_mode              = 'ONLY_FULL_GROUP_BY,STRICT_TRANS_TABLES,NO_ZERO_IN_DATE,NO_ZERO_DATE,ERROR_FOR_DIVISION_BY_ZERO,NO_ENGINE_SUBSTITUTION' */ ;
DELIMITER ;;
/*!50003 CREATE*/ /*!50017 DEFINER=`root`@`%`*/ /*!50003 TRIGGER `trg_locker_cell_status_check` BEFORE UPDATE ON `locker_cells` FOR EACH ROW BEGIN
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
) ENGINE=InnoDB AUTO_INCREMENT=6 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `orders`
--

INSERT  IGNORE INTO `orders` VALUES (1,'order_reservation_expired','Timeout Order','courier','courier','Msk','Spb',2,12,'2025-11-24 16:36:07','2025-11-24 16:33:51');
INSERT  IGNORE INTO `orders` VALUES (2,'order_reservation_expired','Trip Order 1','courier','courier','Msk','Spb',3,13,'2025-11-24 16:36:07','2025-11-24 16:33:51');
INSERT  IGNORE INTO `orders` VALUES (3,'order_reservation_expired','Trip Order 2','courier','courier','Msk','Spb',4,14,'2025-11-24 16:36:08','2025-11-24 16:33:51');
INSERT  IGNORE INTO `orders` VALUES (4,'order_reservation_expired','Trip Order 3','courier','courier','Msk','Spb',5,15,'2025-11-24 16:36:08','2025-11-24 16:33:52');
INSERT  IGNORE INTO `orders` VALUES (5,'order_created','Order','courier','courier','Msk','Spb',2,5,'2025-11-26 16:25:34','2025-11-26 16:25:34');
/*!50003 SET @saved_cs_client      = @@character_set_client */ ;
/*!50003 SET @saved_cs_results     = @@character_set_results */ ;
/*!50003 SET @saved_col_connection = @@collation_connection */ ;
/*!50003 SET character_set_client  = utf8mb4 */ ;
/*!50003 SET character_set_results = utf8mb4 */ ;
/*!50003 SET collation_connection  = utf8mb4_0900_ai_ci */ ;
/*!50003 SET @saved_sql_mode       = @@sql_mode */ ;
/*!50003 SET sql_mode              = 'NO_AUTO_VALUE_ON_ZERO' */ ;
DELIMITER ;;
/*!50003 CREATE*/ /*!50017 DEFINER=`root`@`%`*/ /*!50003 TRIGGER `set_delivery_type_before_update` BEFORE UPDATE ON `orders` FOR EACH ROW BEGIN
    IF NEW.status = 'order_client_reserved' AND OLD.status != 'order_client_reserved' THEN
        SET NEW.delivery_type = 'self';
    ELSEIF NEW.status = 'order_courier_reserved' AND OLD.status != 'order_courier_reserved' THEN
        SET NEW.delivery_type = 'courier';
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
/*!50003 CREATE*/ /*!50017 DEFINER=`root`@`%`*/ /*!50003 TRIGGER `trg_order_status_check` BEFORE UPDATE ON `orders` FOR EACH ROW BEGIN
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
/*!50003 CREATE*/ /*!50017 DEFINER=`root`@`%`*/ /*!50003 TRIGGER `trg_order_courier_assignment_check` AFTER UPDATE ON `orders` FOR EACH ROW BEGIN
    DECLARE has_courier1 INT DEFAULT 0;
    DECLARE has_courier2 INT DEFAULT 0;

    -- Проверяем, если состояние стало order_courier1_assigned
    IF NEW.status = 'order_courier1_assigned' AND OLD.status != 'order_courier1_assigned' THEN
        SELECT COUNT(*) INTO has_courier1
        FROM stage_orders so
        JOIN trips t ON t.id = so.trip_id
        WHERE so.order_id = NEW.id
          AND so.courier1_user_id IS NOT NULL;

        IF has_courier1 = 0 THEN
            SIGNAL SQLSTATE '45000'
            SET MESSAGE_TEXT = 'Transition to order_courier1_assigned requires courier1_user_id in stage_orders';
        END IF;
    END IF;

    -- Проверяем, если состояние стало order_courier2_assigned
    IF NEW.status = 'order_courier2_assigned' AND OLD.status != 'order_courier2_assigned' THEN
        SELECT COUNT(*) INTO has_courier2
        FROM stage_orders so
        JOIN trips t ON t.id = so.trip_id
        WHERE so.order_id = NEW.id
          AND so.courier2_user_id IS NOT NULL;

        IF has_courier2 = 0 THEN
            SIGNAL SQLSTATE '45000'
            SET MESSAGE_TEXT = 'Transition to order_courier2_assigned requires courier2_user_id in stage_orders';
        END IF;
    END IF;
END */;;
DELIMITER ;
/*!50003 SET sql_mode              = @saved_sql_mode */ ;
/*!50003 SET character_set_client  = @saved_cs_client */ ;
/*!50003 SET character_set_results = @saved_cs_results */ ;
/*!50003 SET collation_connection  = @saved_col_connection */ ;

--
-- Table structure for table `stage_orders`
--

DROP TABLE IF EXISTS `stage_orders`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `stage_orders` (
  `trip_id` int NOT NULL,
  `order_id` int NOT NULL,
  `courier1_user_id` int DEFAULT NULL,
  `courier2_user_id` int DEFAULT NULL,
  PRIMARY KEY (`trip_id`,`order_id`),
  KEY `order_id` (`order_id`),
  KEY `stage_orders_ibfk_3` (`courier1_user_id`),
  KEY `stage_orders_ibfk_4` (`courier2_user_id`),
  CONSTRAINT `stage_orders_ibfk_1` FOREIGN KEY (`trip_id`) REFERENCES `trips` (`id`) ON DELETE CASCADE,
  CONSTRAINT `stage_orders_ibfk_2` FOREIGN KEY (`order_id`) REFERENCES `orders` (`id`) ON DELETE CASCADE,
  CONSTRAINT `stage_orders_ibfk_3` FOREIGN KEY (`courier1_user_id`) REFERENCES `users` (`id`) ON DELETE SET NULL,
  CONSTRAINT `stage_orders_ibfk_4` FOREIGN KEY (`courier2_user_id`) REFERENCES `users` (`id`) ON DELETE SET NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `stage_orders`
--

INSERT  IGNORE INTO `stage_orders` VALUES (1,2,NULL,NULL);
INSERT  IGNORE INTO `stage_orders` VALUES (1,3,NULL,NULL);
INSERT  IGNORE INTO `stage_orders` VALUES (1,4,NULL,NULL);

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
  `status` varchar(50) DEFAULT 'trip_created',
  `description` varchar(255) DEFAULT NULL,
  `active` tinyint(1) DEFAULT '1',
  `created_at` datetime DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  KEY `fk_driver_user` (`driver_user_id`),
  CONSTRAINT `fk_driver_user` FOREIGN KEY (`driver_user_id`) REFERENCES `users` (`id`) ON DELETE RESTRICT
) ENGINE=InnoDB AUTO_INCREMENT=2 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `trips`
--

INSERT  IGNORE INTO `trips` VALUES (1,NULL,'Msk','Spb','trip_created',NULL,1,'2025-11-24 16:33:51');

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
/*!50106 CREATE*/ /*!50117 DEFINER=`root`@`%`*/ /*!50106 EVENT `cleanup_old_logs` ON SCHEDULE EVERY 1 DAY STARTS '2025-11-07 13:44:52' ON COMPLETION NOT PRESERVE ENABLE DO BEGIN
    DELETE FROM fsm_action_logs WHERE created_at < NOW() - INTERVAL 90 DAY;
    DELETE FROM fsm_errors_log WHERE errortime < NOW() - INTERVAL 90 DAY;
    DELETE FROM hardware_command_log WHERE executedat < NOW() - INTERVAL 90 DAY;
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
/*!50106 CREATE*/ /*!50117 DEFINER=`root`@`%`*/ /*!50106 EVENT `courier_timeout_event` ON SCHEDULE EVERY 5 MINUTE STARTS '2025-11-06 09:23:39' ON COMPLETION NOT PRESERVE ENABLE DO BEGIN
    DECLARE done INT DEFAULT FALSE;
    DECLARE v_order_id INT;
    DECLARE cur CURSOR FOR
        SELECT id FROM orders
        WHERE status IN ('order_courier1_assigned', 'order_courier2_assigned')
          AND updated_at < NOW() - INTERVAL 30 MINUTE;

    DECLARE CONTINUE HANDLER FOR NOT FOUND SET done = TRUE;

    OPEN cur;
    read_loop: LOOP
        FETCH cur INTO v_order_id;
        IF done THEN LEAVE read_loop; END IF;
        CALL fsm_perform_action('order', v_order_id, 'order_timeout_no_pickup', -1, NULL);
    END LOOP;
    CLOSE cur;
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
CREATE DEFINER=`root`@`%` PROCEDURE `clear_test_data`()
BEGIN
  SET FOREIGN_KEY_CHECKS = 0;

  TRUNCATE TABLE stage_orders;
  TRUNCATE TABLE orders;
  TRUNCATE TABLE trips;

  TRUNCATE TABLE fsm_errors_log;
  TRUNCATE TABLE fsm_action_logs;
  TRUNCATE TABLE hardware_command_log;

  SET FOREIGN_KEY_CHECKS = 1;
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
CREATE DEFINER=`root`@`%` PROCEDURE `fsm_perform_action`(
    IN p_entity_type VARCHAR(50),
    IN p_entity_id INT,
    IN p_action_name VARCHAR(100),
    IN p_user_id INT,
    IN p_extra_id VARCHAR(255)
)
BEGIN
    DECLARE v_current_state_id INT;
    DECLARE v_next_state_id INT;
    DECLARE v_action_id INT;
    DECLARE v_status_field VARCHAR(50);
    DECLARE v_table_name VARCHAR(50);
    DECLARE v_message TEXT;
    DECLARE v_current_status VARCHAR(50);
    DECLARE v_next_status VARCHAR(50);
    DECLARE v_locker_id INT DEFAULT NULL;
    DECLARE v_state VARCHAR(50);
    DECLARE v_active_flag TINYINT(1) DEFAULT 1;
    DECLARE v_cnt INT DEFAULT 0;

    -- Обработчик исключений
    DECLARE EXIT HANDLER FOR SQLEXCEPTION
    BEGIN
        INSERT IGNORE INTO fsm_errors_log(error_time, error_message, entity_type, entity_id, action_name, user_id)
        VALUES (NOW(), CONCAT('SQL Exception during ', p_action_name), p_entity_type, p_entity_id, p_action_name, p_user_id);
    END;

    -- ОСНОВНОЙ БЛОК
    proc_end: BEGIN
        -- 1. Определяем таблицу и поле статуса
        IF p_entity_type = 'order' THEN
            SET v_table_name = 'orders';
            SET v_status_field = 'status';
        ELSEIF p_entity_type = 'trip' THEN
            SET v_table_name = 'trips';
            SET v_status_field = 'status';
        ELSEIF p_entity_type = 'locker' THEN
            SET v_table_name = 'locker_cells';
            SET v_status_field = 'status';
        ELSE
            INSERT IGNORE INTO fsm_errors_log(error_time, error_message, entity_type, entity_id, action_name, user_id)
            VALUES (NOW(), CONCAT('Unknown entity_type: ', p_entity_type), p_entity_type, p_entity_id, p_action_name, p_user_id);
            LEAVE proc_end;
        END IF;

        -- 2. Проверяем существование записи
        SET v_cnt = 0;
        SET @check_sql = CONCAT('SELECT COUNT(*) INTO @cnt FROM ', v_table_name, ' WHERE id = ', p_entity_id);
        PREPARE stmt_check FROM @check_sql;
        EXECUTE stmt_check;
        DEALLOCATE PREPARE stmt_check;

        IF @cnt = 0 THEN
            INSERT IGNORE INTO fsm_errors_log(error_time, error_message, entity_type, entity_id, action_name, user_id)
            VALUES (NOW(), CONCAT('Entity not found: ', p_entity_type, ' #', p_entity_id), p_entity_type, p_entity_id, p_action_name, p_user_id);
            LEAVE proc_end;
        END IF;

        -- 3. Получаем текущее состояние
        SET @sql = CONCAT('SELECT ', v_status_field, ' INTO @current_status FROM ', v_table_name, ' WHERE id = ', p_entity_id);
        PREPARE stmt1 FROM @sql;
        EXECUTE stmt1;
        DEALLOCATE PREPARE stmt1;

        SET v_current_status = @current_status;

        IF v_current_status IS NULL THEN
            INSERT IGNORE INTO fsm_errors_log(error_time, error_message, entity_type, entity_id, action_name, user_id)
            VALUES (NOW(), CONCAT('Entity has NULL status: ', p_entity_type, ' #', p_entity_id), p_entity_type, p_entity_id, p_action_name, p_user_id);
            LEAVE proc_end;
        END IF;

        -- 4. Для рейсов проверяем active=1 ПЕРЕД поиском действия
        IF p_entity_type = 'trip' AND p_action_name IN ('trip_vzyat_reis', 'trip_start_trip') THEN
            SELECT active INTO v_active_flag FROM trips WHERE id = p_entity_id;
            
            IF v_active_flag = 0 THEN
                INSERT IGNORE INTO fsm_errors_log(error_time, error_message, entity_type, entity_id, action_name, user_id)
                VALUES (NOW(), CONCAT('Trip #', p_entity_id, ' is not active yet (active=0)'), 
                        p_entity_type, p_entity_id, p_action_name, p_user_id);
                
                SELECT CONCAT('ERROR: Trip #', p_entity_id, ' not active yet') AS result;
                LEAVE proc_end;
            END IF;
        END IF;

        -- 5. Находим ID действия
        SELECT id INTO v_action_id FROM fsm_actions WHERE name = p_action_name;
        IF v_action_id IS NULL THEN
            INSERT IGNORE INTO fsm_errors_log(error_time, error_message, entity_type, entity_id, action_name, user_id)
            VALUES (NOW(), CONCAT('Unknown action: ', p_action_name), p_entity_type, p_entity_id, p_action_name, p_user_id);
            LEAVE proc_end;
        END IF;

        /*-- 6. Специальная логика для locker
        IF p_entity_type = 'locker' THEN
            -- locker_reset
            IF p_action_name = 'locker_reset' THEN
                SELECT id INTO v_locker_id FROM locker_cells
                WHERE id = p_entity_id AND status IN ('locker_error', 'locker_closed_empty', 'locker_maintenance');
                IF v_locker_id IS NULL THEN
                    INSERT IGNORE INTO fsm_errors_log(error_time, error_message, entity_type, entity_id, action_name, user_id)
                    VALUES (NOW(), CONCAT('Cannot reset locker: invalid state for locker #', p_entity_id), p_entity_type, p_entity_id, p_action_name, p_user_id);
                    LEAVE proc_end;
                END IF;

                INSERT INTO hardware_command_log (command, target, success)
                VALUES ('RESET_LOCKER', CONCAT('cell_', v_locker_id), NULL);

                UPDATE locker_cells
                SET status = 'locker_free', unlock_code = NULL, code_expires_at = NULL,
                    reservation_expires_at = NULL, current_order_id = NULL, reserved_for_user_id = NULL, failed_open_attempts = 0
                WHERE id = v_locker_id;

                INSERT INTO fsm_action_logs(entity_type, entity_id, action_name, from_state, to_state, user_id, created_at)
                SELECT 'locker', v_locker_id, 'locker_reset', v_current_status, 'locker_free', p_user_id, NOW();

                SELECT CONCAT('Locker cell #', v_locker_id, ' reset and set to free') AS result;
                LEAVE proc_end;
            END IF;

            -- locker_cancel_reservation
            IF p_action_name = 'locker_cancel_reservation' THEN
                SELECT id INTO v_locker_id FROM locker_cells
                WHERE id = p_entity_id AND status = 'locker_reserved';
                IF v_locker_id IS NULL THEN
                    INSERT IGNORE INTO fsm_errors_log(error_time, error_message, entity_type, entity_id, action_name, user_id)
                    VALUES (NOW(), CONCAT('Cannot cancel reservation: not reserved, locker #', p_entity_id), p_entity_type, p_entity_id, p_action_name, p_user_id);
                    LEAVE proc_end;
                END IF;

                INSERT INTO hardware_command_log (command, target, success)
                VALUES ('CANCEL_RESERVATION', CONCAT('cell_', v_locker_id), NULL);

                UPDATE locker_cells
                SET status = 'locker_free', unlock_code = NULL, code_expires_at = NULL,
                    reservation_expires_at = NULL, current_order_id = NULL, reserved_for_user_id = NULL, failed_open_attempts = 0
                WHERE id = v_locker_id;

                INSERT INTO fsm_action_logs(entity_type, entity_id, action_name, from_state, to_state, user_id, created_at)
                SELECT 'locker', v_locker_id, 'locker_cancel_reservation', v_current_status, 'locker_free', p_user_id, NOW();

                SELECT CONCAT('Reservation cancelled for locker cell #', v_locker_id) AS result;
                LEAVE proc_end;
            END IF;

            -- locker_open_locker
            IF p_action_name = 'locker_open_locker' THEN
                SELECT failed_open_attempts INTO @attempts FROM locker_cells WHERE id = p_entity_id;
                IF @attempts >= 10 THEN
                    UPDATE locker_cells SET status = 'locker_error' WHERE id = p_entity_id;
                    INSERT IGNORE INTO fsm_errors_log(error_time, error_message, entity_type, entity_id, action_name, user_id)
                    VALUES (NOW(), CONCAT('Locker cell #', p_entity_id, ' blocked due to too many failed attempts'), p_entity_type, p_entity_id, p_action_name, p_user_id);
                    SELECT CONCAT('Locker cell #', p_entity_id, ' is blocked') AS result;
                    LEAVE proc_end;
                END IF;

                SELECT id INTO v_locker_id FROM locker_cells
                WHERE id = p_entity_id AND unlock_code = p_extra_id AND code_expires_at > NOW() AND status = 'locker_reserved';

                IF v_locker_id IS NULL THEN
                    UPDATE locker_cells SET failed_open_attempts = failed_open_attempts + 1 WHERE id = p_entity_id;
                    INSERT IGNORE INTO fsm_errors_log(error_time, error_message, entity_type, entity_id, action_name, user_id)
                    VALUES (NOW(), CONCAT('Invalid or expired unlock code for locker cell #', p_entity_id), p_entity_type, p_entity_id, p_action_name, p_user_id);
                    LEAVE proc_end;
                END IF;

                UPDATE locker_cells SET failed_open_attempts = 0 WHERE id = v_locker_id;
                INSERT INTO hardware_command_log (command, target, success)
                VALUES ('OPEN_CELL', CONCAT('cell_', v_locker_id), NULL);
                UPDATE locker_cells SET status = 'locker_opened' WHERE id = v_locker_id;

                INSERT INTO fsm_action_logs(entity_type, entity_id, action_name, from_state, to_state, user_id, created_at)
                VALUES ('locker', v_locker_id, 'locker_open_locker', 'locker_reserved', 'locker_opened', p_user_id, NOW());

                SELECT CONCAT('Locker cell #', v_locker_id, ' opened') AS result;
                LEAVE proc_end;
            END IF;

            -- locker_close_locker
            IF p_action_name = 'locker_close_locker' THEN
                SELECT status INTO v_state FROM locker_cells WHERE id = p_entity_id;
                IF v_state NOT IN ('locker_parcel_confirmed', 'locker_parcel_pickup_driver', 'locker_parcel_pickup_recipient') THEN
                    INSERT IGNORE INTO fsm_errors_log(error_time, error_message, entity_type, entity_id, action_name, user_id)
                    VALUES (NOW(), CONCAT('Cannot close locker: not confirmed, locker cell #', p_entity_id), p_entity_type, p_entity_id, p_action_name, p_user_id);
                    LEAVE proc_end;
                END IF;

                INSERT INTO hardware_command_log (command, target, success)
                VALUES ('CLOSE_CELL', CONCAT('cell_', p_entity_id), NULL);

                UPDATE locker_cells
                SET status = 'locker_closed_empty', unlock_code = NULL, code_expires_at = NULL,
                    reservation_expires_at = NULL, current_order_id = NULL, reserved_for_user_id = NULL, failed_open_attempts = 0
                WHERE id = p_entity_id;

                INSERT INTO fsm_action_logs(entity_type, entity_id, action_name, from_state, to_state, user_id, created_at)
                VALUES ('locker', p_entity_id, 'locker_close_locker', v_state, 'locker_closed_empty', p_user_id, NOW());

                SELECT CONCAT('Locker cell #', p_entity_id, ' closed') AS result;
                LEAVE proc_end;
            END IF;
        END IF;*/

        -- 7. Находим следующий статус (ИСПРАВЛЕНО: сохраняем в переменную)
        SELECT t.to_state_id, s2.name 
        INTO v_next_state_id, v_next_status
        FROM fsm_transitions t
        JOIN fsm_states s ON s.id = t.from_state_id
        JOIN fsm_states s2 ON s2.id = t.to_state_id
        WHERE s.name = v_current_status AND t.action_id = v_action_id
        LIMIT 1;

        IF v_next_state_id IS NULL OR v_next_status IS NULL THEN
            INSERT IGNORE INTO fsm_errors_log(error_time, error_message, entity_type, entity_id, action_name, user_id)
            VALUES (NOW(), CONCAT('Transition not allowed: ', p_action_name, ' from ', v_current_status), p_entity_type, p_entity_id, p_action_name, p_user_id);
            SELECT CONCAT('ERROR: No transition for ', p_action_name, ' from state ', v_current_status) AS result;
            LEAVE proc_end;
        END IF;

        -- 8. ИСПРАВЛЕНО: Обновляем статус через ПЕРЕМЕННУЮ, а не через подзапрос
        -- Используем v_next_status (уже загруженный выше)
        SET @sql_update = CONCAT(
            'UPDATE ', v_table_name,
            ' SET ', v_status_field, ' = ''', v_next_status, '''',
            ' WHERE id = ', p_entity_id
        );
        PREPARE stmt_update FROM @sql_update;
        EXECUTE stmt_update;
        DEALLOCATE PREPARE stmt_update;

        -- 9. Логируем действие
        INSERT INTO fsm_action_logs(entity_type, entity_id, action_name, from_state, to_state, user_id, created_at)
        VALUES (
            p_entity_type,
            p_entity_id,
            p_action_name,
            v_current_status,
            v_next_status,
            p_user_id,
            NOW()
        );

        -- 10. Результат
        SET v_message = CONCAT('FSM action "', p_action_name, '" applied on ', p_entity_type, ' #', p_entity_id, 
                               ': ', v_current_status, ' → ', v_next_status);
        SELECT v_message AS result;

    END proc_end;
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
