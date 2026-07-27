-- Domain DB dump (tables + data only)
-- Generated 2026-07-27T13:18:45.542744+00:00
-- No triggers / events / routines

SET NAMES utf8mb4;
SET FOREIGN_KEY_CHECKS=0;
SET UNIQUE_CHECKS=0;
SET SQL_MODE='NO_AUTO_VALUE_ON_ZERO';

--
-- Table `cell_access_tokens`
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
) ENGINE=InnoDB AUTO_INCREMENT=256 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `cell_access_tokens`
--

LOCK TABLES `cell_access_tokens` WRITE;
/*!40000 ALTER TABLE `cell_access_tokens` DISABLE KEYS */;
INSERT INTO `cell_access_tokens` (`id`,`order_id`,`leg`,`cell_id`,`actor_user_id`,`pin_hash`,`pin_encrypted`,`status`,`expires_at`,`failed_attempts`,`created_at`,`used_at`) VALUES
(238,1610,'pickup',70,2,'b20b3806320c10c9efae4810641fcd50c1095c157d8838c3f48ef3205ee9faf9','642877','ACTIVE','2026-07-24 13:06:23',0,'2026-07-24 13:00:42',NULL),
(239,1611,'pickup',1,11,'af40e58ab439012159cd240fea1e7df995e4313d4b527a9b20022ca0d3941c1f','726346','ACTIVE','2026-07-24 13:06:50',0,'2026-07-24 13:01:08',NULL),
(240,1612,'pickup',64,7,'216308f3652bff4a1b8671fc7836412fce549bd0435c7a7296a8827734494158','430460','ACTIVE','2026-07-24 13:07:22',0,'2026-07-24 13:01:40',NULL),
(241,1613,'pickup',67,13,'8b6e680d5692563563a2e723d5836a200d582c3bc7d58fe53c885ad171fd649e','183912','ACTIVE','2026-07-24 13:07:48',0,'2026-07-24 13:02:07',NULL),
(242,1610,'pickup',70,1,'fa91bc068f10873552c39c2752c0aaa62f9ff5cc463ee0944a868806cafcba37','644075','ACTIVE','2026-07-24 13:08:13',0,'2026-07-24 13:02:32',NULL),
(243,1611,'pickup',1,1,'ad0cf26e35b4d6c5d4b7b2323aaae029d1fe6157b8de9e21b808f4845c238e6e','775101','ACTIVE','2026-07-24 13:08:27',0,'2026-07-24 13:02:46',NULL),
(244,1612,'pickup',64,1,'ab418aafe20efb9685ea7a1ed4fc73e8306b3dab0a344051a6219e4b42b46860','651409','ACTIVE','2026-07-24 13:08:42',0,'2026-07-24 13:03:01',NULL),
(245,1613,'pickup',67,1,'7316613ee24b3cc94c60d76af6f41f0850d8c2eba94a2b80f9ec751f3987f3bb','267135','ACTIVE','2026-07-24 13:09:00',0,'2026-07-24 13:03:19',NULL),
(246,1610,'delivery',71,1,'756e0a9478064b2d02a2df4c2c1f07da65c81371599cf3f2c40ec654d2162a71','399963','ACTIVE','2026-07-24 13:09:52',0,'2026-07-24 13:04:11',NULL),
(247,1611,'delivery',52,1,'0b38e5ffed269f805cf7cde71d8f0f20bf41787515e5918ca44705620d124cb9','145627','ACTIVE','2026-07-24 13:10:06',0,'2026-07-24 13:04:24',NULL),
(248,1612,'delivery',87,1,'f7304cb011952c221611b884cb1166e9221cfd3b4ebc431aa1478308fd0550e8','945188','ACTIVE','2026-07-24 13:10:20',0,'2026-07-24 13:04:38',NULL),
(249,1613,'delivery',90,1,'ad19b07937f7843f624b0e864080fd89406a7ce46c089cd9a8dbca3c4b300984','538245','ACTIVE','2026-07-24 13:10:34',0,'2026-07-24 13:04:52',NULL),
(250,1610,'delivery',71,6,'a8e351de0fefff1603e12326755339ac50ce50b2b2aad866a411bd3c1a86dfa4','122793','ACTIVE','2026-07-24 13:11:02',0,'2026-07-24 13:05:21',NULL),
(251,1610,'delivery',71,4,'f4e5c898032c0f3bd267dbc4959ba4bc142ca935409a1a48eeef0673ea44a342','248028','USED','2026-07-24 13:11:18',0,'2026-07-24 13:05:37','2026-07-24 13:05:43'),
(252,1611,'delivery',52,8,'786de60db69c3e89ba9cbfe005e75c5419325815ca74f8b9f6365a9d54b78d0c','631362','ACTIVE','2026-07-24 13:11:32',0,'2026-07-24 13:05:51',NULL),
(253,1611,'delivery',52,14,'cc0c7c9deb7bafff3732de94d7d96611404848768d9d9ce81129ac993eb9094b','132824','USED','2026-07-24 13:11:46',0,'2026-07-24 13:06:05','2026-07-24 13:06:10'),
(254,1612,'delivery',87,15,'6723a5d572166f1d0e0f6f164ec954da3bb7b3d690318b5c17c232448a824c81','423517','ACTIVE','2026-07-24 13:11:55',0,'2026-07-24 13:06:13',NULL),
(255,1613,'delivery',90,16,'0ec80c1e761910d11cd4ab17382a99ac0ea17e01c23a9198ec90e5643bfa2aae','960808','ACTIVE','2026-07-24 13:12:09',0,'2026-07-24 13:06:28',NULL);
/*!40000 ALTER TABLE `cell_access_tokens` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table `core_order_mapping`
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
INSERT INTO `core_order_mapping` (`id`,`local_order_id`,`core_order_id`,`role`,`kind`,`upper`,`b_state`,`created_at`,`updated_at`,`client_local_user_id`,`performer_local_user_id`) VALUES
(1,1539,1568,NULL,NULL,NULL,NULL,'2026-04-08 09:26:10','2026-04-08 09:26:10',NULL,NULL),
(2,1540,1569,NULL,NULL,NULL,NULL,'2026-04-08 12:57:55','2026-04-08 12:57:55',NULL,NULL),
(3,1541,1570,NULL,NULL,NULL,NULL,'2026-04-08 13:05:06','2026-04-08 13:05:06',NULL,NULL);
/*!40000 ALTER TABLE `core_order_mapping` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table `core_user_mapping`
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
INSERT INTO `core_user_mapping` (`local_user_id`,`core_u_id`,`core_role`,`registered_at`,`last_sync_at`,`sync_status`,`error_message`,`token`,`u_hash`,`car_core_id`) VALUES
(1000006,972,2,'2026-04-03 09:15:56','2026-04-03 09:15:56','success',NULL,NULL,NULL,NULL),
(1000007,973,1,'2026-04-03 12:31:32','2026-04-03 12:31:32','success',NULL,NULL,NULL,NULL),
(1000008,974,1,'2026-04-03 13:15:57','2026-04-03 13:15:57','success',NULL,NULL,NULL,NULL),
(1000039,1010,1,'2026-07-27 11:47:17','2026-07-27 11:47:17','success',NULL,'47d59386dfe5518b8ba2999e74d32c40','RKv1XHMoaNU2PCC1NB5YlMAfYFY/HqdrNHOxJ6BduD9V50Dqew1vn1c3CUTQrwqP61QhJeLHdl1AiaNBmSbuW4sBesnVaBMXaU2i/PO4+vQlWTca6/GZ++Jsm5dJrLhx',NULL);
/*!40000 ALTER TABLE `core_user_mapping` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table `directions`
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
) ENGINE=InnoDB AUTO_INCREMENT=18 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `directions`
--

LOCK TABLES `directions` WRITE;
/*!40000 ALTER TABLE `directions` DISABLE KEYS */;
INSERT INTO `directions` (`id`,`from_city`,`to_city`,`pickup_locker_id`,`delivery_locker_id`,`orders_available`,`orders_reserved`) VALUES
(16,'Москва','Санкт-Петербург',1,2,0,0),
(17,'Москва','Санкт-Петербург',3,4,0,0);
/*!40000 ALTER TABLE `directions` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table `driver_reservations`
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
) ENGINE=InnoDB AUTO_INCREMENT=54 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `driver_reservations`
--

LOCK TABLES `driver_reservations` WRITE;
/*!40000 ALTER TABLE `driver_reservations` DISABLE KEYS */;
INSERT INTO `driver_reservations` (`id`,`driver_user_id`,`direction_id`,`reserved_count`,`requested_count`,`reserved_at`,`expires_at`,`status`) VALUES
(53,1,16,4,4,'2026-07-24 13:02:23','2026-07-24 13:53:05','reservation_completed');
/*!40000 ALTER TABLE `driver_reservations` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table `fsm_actions`
--

DROP TABLE IF EXISTS `fsm_actions`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `fsm_actions` (
  `id` int NOT NULL AUTO_INCREMENT,
  `name` varchar(50) NOT NULL,
  `label` varchar(100) DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=138 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `fsm_actions`
--

LOCK TABLES `fsm_actions` WRITE;
/*!40000 ALTER TABLE `fsm_actions` DISABLE KEYS */;
INSERT INTO `fsm_actions` (`id`,`name`,`label`) VALUES
(1,'locker_reserve_cell','Zabronirovat yacheyku'),
(2,'trip_assign_voditel','Naznachit voditelya'),
(3,'trip_start_trip','Nachat poyezdku'),
(4,'trip_complete_trip','Zavershit poyezdku'),
(5,'locker_open_locker','Otkryt yacheyku'),
(6,'locker_close_locker','Zakryt yacheyku'),
(7,'order_timeout_reservation','Taymaut rezervirovaniya'),
(8,'locker_confirm_parcel_in','Podtverdit posylku vnutri'),
(49,'order_assign_courier1_to_order','Naznachit Kurer1 na zakaz'),
(61,'order_timeout_confirmation','Taymaut podtverzhdeniya'),
(68,'order_client_will_deliver','Klient sam sdast posylku'),
(69,'order_confirm_parcel_in','Подтвердить посылку (Order)'),
(70,'order_parcel_submitted','Посылка сдана (Order)'),
(71,'order_courier_pickup_parcel','Kurer zabral posilku'),
(72,'locker_reset','sbros yacheiki'),
(73,'locker_set_locker_to_maintenance','perevesti v obsluzhivanie'),
(74,'order_cancel_reservation','otmenit rezervatsiyu'),
(75,'locker_confirm_parcel_not_found','posylka_ne_naidena'),
(76,'locker_cancel_reservation','otmena rezervatsii yacheiki'),
(77,'trip_start_pickup','nachat_zabir'),
(78,'trip_confirm_pickup','podtverdit_zabir'),
(79,'trip_confirm_delivery','podtverdit_dostavku'),
(81,'order_reserve_for_client_A_to_B','zarezervirovat_dlya_klienta_A_to_B'),
(82,'order_reserve_for_courier_A_to_B','zarezervirovat_dlya_kurera_A_to_B'),
(83,'order_pickup_by_voditel','voditel_zabral_posylku'),
(84,'order_start_transit','nachat_perevozku'),
(85,'order_arrive_at_post2','pridyal_k_post2'),
(86,'locker_confirm_parcel_out','Podtverdit poluchenie posylki iz yacheiki'),
(87,'locker_dont_closed','Yacheika ne zakryta posle raboty'),
(88,'order_pickup_poluchatel','Klient poluchil posylku'),
(89,'order_delivered_parcel','Zavershit zakaz posle polucheniya'),
(90,'order_assign_courier2_to_order','Naznachit kurera2'),
(91,'order_courier2_pickup_parcel','Kurer2 zabral iz post2'),
(92,'order_courier2_delivered_parcel','Kurer2 zavershil dostavku'),
(93,'order_report_parcel_missing','Posylka ne naidena v yacheike'),
(94,'order_report_delivery_failed','Soobshchit o neudache dostavki'),
(95,'order_request_manual_intervention','Zaprosit ruchnoe vmeshatelstvo'),
(96,'trip_report_driver_not_found','Soobshchit: voditel ne naiden'),
(97,'trip_report_failure','Soobshchit o sbue poezdki'),
(98,'trip_request_manual_intervention','Zaprosit ruchnoe vmeshatelstvo'),
(99,'order_courier1_cancel','Kurer1 otmenil do zabora'),
(100,'order_courier2_cancel','Kurer2 otmenil do zabora iz post2'),
(101,'order_timeout_no_pickup','Taymaut: kurer ne zabral posylku'),
(102,'trip_vzyat_reis','Vzyat reis'),
(103,'locker_confirm_parcel_out_recipient','Podtverdit vydachu poluchatelyu iz yacheiki'),
(104,'order_recipient_confirmed','Klient podtverdil poluchenie'),
(105,'locker_close_pickup',NULL),
(106,'locker_failed_to_open','Ne otkrilas yacheika'),
(107,'order_confirm_post2','voditel polozhil posilku v post2'),
(108,'order_client_deliv_post1','client polozhil posilku v post1'),
(113,'driver_reservation_start_loading','Начать погрузку'),
(114,'driver_reservation_complete_loading','Завершить погрузку'),
(115,'driver_reservation_expire','Истёк таймаут'),
(116,'driver_reservation_cancel','Отменить резерв'),
(117,'trip_cancel','Отменить рейс'),
(123,'trip_reassign_driver','Переназначить водителя'),
(124,'trip_resume_with_new_driver','Возобновить рейс с новым водителем'),
(125,'assign_executor','Naznachit ispolnitelya'),
(126,'remove_executor','Snyat ispolnitelya'),
(127,'open_cell','Otkryt yacheyku'),
(129,'close_cell','Zakryt yacheyku'),
(130,'start_loading','Nachat pogruzku'),
(131,'complete_loading','Zavershit pogruzku'),
(132,'cancel_reservation','Otmenit rezerv'),
(133,'start_trip','Nachat reys'),
(134,'start_order_transit','Zakaz v tranzit'),
(135,'expire_reservation','Taymaut rezerv'),
(136,'complete_trip','Zavershit reys'),
(137,'confirm_courier2_delivery','Podtverdit dostavku kurierom2');
/*!40000 ALTER TABLE `fsm_actions` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table `fsm_graph_meta`
--

DROP TABLE IF EXISTS `fsm_graph_meta`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `fsm_graph_meta` (
  `id` tinyint NOT NULL DEFAULT '1',
  `current_version` int NOT NULL DEFAULT '1',
  `updated_at` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `fsm_graph_meta`
--

LOCK TABLES `fsm_graph_meta` WRITE;
/*!40000 ALTER TABLE `fsm_graph_meta` DISABLE KEYS */;
INSERT INTO `fsm_graph_meta` (`id`,`current_version`,`updated_at`) VALUES
(1,1,'2026-07-26 14:47:12');
/*!40000 ALTER TABLE `fsm_graph_meta` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table `fsm_states`
--

DROP TABLE IF EXISTS `fsm_states`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `fsm_states` (
  `id` int NOT NULL AUTO_INCREMENT,
  `name` varchar(50) NOT NULL,
  `timeout_seconds` int DEFAULT NULL COMMENT 'сек жизни state; NULL = без авто-таймера',
  `timeout_event` varchar(128) DEFAULT NULL COMMENT 'event_name / process event при срабатывании',
  `timeout_owner` varchar(16) DEFAULT 'domain' COMMENT 'domain|platform — чья политика',
  `label` varchar(100) DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=115 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `fsm_states`
--

LOCK TABLES `fsm_states` WRITE;
/*!40000 ALTER TABLE `fsm_states` DISABLE KEYS */;
INSERT INTO `fsm_states` (`id`,`name`,`timeout_seconds`,`timeout_event`,`timeout_owner`,`label`) VALUES
(1,'order_created',NULL,NULL,'domain','Sozdan'),
(3,'trip_assigned',NULL,NULL,'domain','Naznachen'),
(4,'trip_in_progress',NULL,NULL,'domain','V puti'),
(5,'trip_completed',NULL,NULL,'domain','Zavershon'),
(6,'locker_reserved',NULL,NULL,'domain','Yacheika zarezervirovana'),
(7,'locker_opened',NULL,NULL,'domain','Yacheika otkryta'),
(8,'order_parcel_submitted',NULL,NULL,'domain','Posylka sdana'),
(49,'order_courier1_assigned',NULL,NULL,'domain','Kurer1 naznachen'),
(60,'order_parcel_confirmed',NULL,NULL,'domain','Posylka podtverzhdena'),
(61,'order_parcel_missing',NULL,NULL,'domain','Posylka ne naidena'),
(68,'locker_free',NULL,NULL,'domain','Yacheika svobodna'),
(69,'locker_occupied',NULL,NULL,'domain','Yacheika zanyata'),
(70,'locker_error',NULL,NULL,'domain','Oshibka yacheiki'),
(71,'locker_maintenance',NULL,NULL,'domain','Na obsluzhivanii'),
(72,'locker_parcel_submitted',NULL,NULL,'domain','Posylka sdana'),
(73,'locker_parcel_confirmed',NULL,NULL,'domain','Posylka podtverzhdena'),
(74,'locker_parcel_missing',NULL,NULL,'domain','Posylka ne naidena'),
(75,'order_courier_has_parcel',NULL,NULL,'domain','Kurer zabral posilku'),
(76,'order_reservation_expired',NULL,NULL,'domain','rezervatsiya zavershena po taymautu'),
(77,'order_courier_failed',NULL,NULL,'domain','kurer ne podtverdil zabir'),
(78,'order_cancelled',NULL,NULL,'domain','zakaz otmenen klientom'),
(79,'locker_closed_empty',NULL,NULL,'domain','yacheyka zakryta pustaya'),
(80,'trip_ready_for_pickup',NULL,NULL,'domain','gotov_zabrat'),
(81,'trip_parcel_picked_up',NULL,NULL,'domain','posylka_zabirana'),
(82,'trip_arrived_at_destination',NULL,NULL,'domain','pridyal_k_meste'),
(83,'trip_parcel_delivered',NULL,NULL,'domain','posylka_sdana'),
(84,'order_client_reserved_post1_and_post2',NULL,NULL,'domain','klient_zarezerviroval_1_i_2'),
(85,'order_courier_reserved_post1_and_post2',NULL,NULL,'domain','kurer_zarezerviroval_1_i_2'),
(87,'order_picked_up_from_post1',NULL,NULL,'domain','posylka_zabrana_iz_post1'),
(88,'order_in_transit_to_post2',NULL,NULL,'domain','v_perevozke_k_post2'),
(89,'order_arrived_at_post2',NULL,NULL,'domain','dostavlena_v_post2'),
(90,'order_delivered_to_client',NULL,NULL,'domain','Posylka poluchena klientom'),
(91,'order_courier2_assigned',NULL,NULL,'domain','Kurer2 naznachen'),
(92,'order_courier2_has_parcel',NULL,NULL,'domain','Kurer2 zabral posylku'),
(93,'order_completed',NULL,NULL,'domain','Zakaz zavershon'),
(94,'order_delivery_failed',NULL,NULL,'domain','Dostavka ne udalas'),
(95,'order_manual_intervention_required',NULL,NULL,'domain','Trebuetsya ruchnoe vmeshatelstvo'),
(96,'trip_driver_not_found',NULL,NULL,'domain','Voditel ne naiden'),
(97,'trip_failed',NULL,NULL,'domain','Poezdka prervana'),
(98,'trip_manual_intervention_required',NULL,NULL,'domain','Trebuetsya ruchnoe vmeshatelstvo'),
(99,'trip_created',NULL,NULL,'domain','Reis sozdan'),
(100,'locker_parcel_pickup_driver',NULL,NULL,'domain','posilku zabral voditel'),
(101,'locker_parcel_pickup_recipient',NULL,NULL,'domain','Poluchatel zabral posilku'),
(102,'order_courier2_parcel_delivered',NULL,NULL,'domain','Kurer2 dostavil klientu, ojidaem podtverzhdeniya'),
(103,'order_parcel_confirmed_post2',NULL,NULL,'domain','Posylka podtverzhdena v postamate2'),
(104,'order_client_post1',NULL,NULL,'domain','posilka v post1'),
(109,'reservation_active',NULL,NULL,'domain','Резерв активен'),
(110,'reservation_loading',NULL,NULL,'domain','Водитель загружает'),
(111,'reservation_completed',NULL,NULL,'domain','Погрузка завершена'),
(112,'reservation_expired',NULL,NULL,'domain','Резерв истёк'),
(113,'reservation_cancelled',NULL,NULL,'domain','Резерв отменён'),
(114,'trip_canceled',NULL,NULL,'domain','Рейс отменён');
/*!40000 ALTER TABLE `fsm_states` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table `fsm_transitions`
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
  `graph_version` int NOT NULL DEFAULT '1',
  PRIMARY KEY (`id`),
  KEY `from_state_id` (`from_state_id`),
  KEY `action_id` (`action_id`),
  KEY `to_state_id` (`to_state_id`),
  KEY `idx_tr_graph` (`entity_type`,`graph_version`),
  CONSTRAINT `fsm_transitions_ibfk_1` FOREIGN KEY (`from_state_id`) REFERENCES `fsm_states` (`id`),
  CONSTRAINT `fsm_transitions_ibfk_2` FOREIGN KEY (`action_id`) REFERENCES `fsm_actions` (`id`),
  CONSTRAINT `fsm_transitions_ibfk_3` FOREIGN KEY (`to_state_id`) REFERENCES `fsm_states` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=174 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `fsm_transitions`
--

LOCK TABLES `fsm_transitions` WRITE;
/*!40000 ALTER TABLE `fsm_transitions` DISABLE KEYS */;
INSERT INTO `fsm_transitions` (`id`,`entity_type`,`from_state_id`,`action_id`,`guard_name`,`guard_params`,`priority`,`effect_name`,`effect_params`,`to_state_id`,`graph_version`) VALUES
(29,'order',60,127,'can_open_cell','{"leg": "pickup", "user_role": "driver", "require_pin": true, "require_cell": true, "require_city": true, "stage_must_be": "driver_reserved", "required_status": "order_parcel_confirmed", "allowed_cell_statuses": ["locker_reserved", "locker_occupied"]}',100,'open_cell_effect','{"leg": "pickup", "companions": [{"event_name": "locker_open_locker", "entity_type": "locker", "entity_id_key": "cell_id"}]}',8,1),
(30,'locker',68,1,'can_reserve_locker_cell','{}',100,'reserve_locker_cell_effect','{}',6,1),
(31,'locker',6,5,NULL,NULL,100,'sync_locker_cell_status','{}',7,1),
(36,'order',75,129,'can_close_cell','{"leg": "pickup", "user_role": "courier", "type_field": "pickup_type", "type_value": "courier", "require_pin": false, "require_cell": true, "require_city": true, "stage_must_be": "owned", "required_status": "order_courier_has_parcel", "allowed_cell_statuses": ["locker_opened", "locker_parcel_confirmed"]}',100,'close_cell_effect','{"leg": "pickup", "companions": [{"event_name": "locker_close_locker", "entity_type": "locker", "entity_id_key": "cell_id"}]}',60,1),
(38,'order',49,127,'can_open_cell','{"leg": "pickup", "user_role": "courier", "type_field": "pickup_type", "type_value": "courier", "require_pin": true, "require_cell": true, "require_city": true, "stage_must_be": "owned", "required_status": "order_courier1_assigned", "allowed_cell_statuses": ["locker_reserved", "locker_occupied"]}',100,'open_cell_effect','{"leg": "pickup", "companions": [{"event_name": "locker_open_locker", "entity_type": "locker", "entity_id_key": "cell_id"}]}',75,1),
(42,'order',49,61,NULL,NULL,100,NULL,NULL,77,1),
(47,'locker',70,72,NULL,NULL,100,NULL,NULL,68,1),
(48,'locker',71,72,NULL,NULL,100,NULL,NULL,68,1),
(49,'locker',79,72,NULL,NULL,100,NULL,NULL,68,1),
(50,'locker',74,6,NULL,NULL,100,'sync_locker_cell_status','{}',79,1),
(51,'locker',68,73,NULL,NULL,100,NULL,NULL,71,1),
(52,'locker',7,75,NULL,NULL,100,NULL,NULL,74,1),
(53,'locker',6,76,NULL,NULL,100,NULL,NULL,68,1),
(54,'locker',70,73,NULL,NULL,100,NULL,NULL,71,1),
(55,'trip',3,2,NULL,NULL,100,NULL,NULL,80,1),
(56,'trip',80,78,NULL,NULL,100,NULL,NULL,81,1),
(57,'trip',3,133,'can_start_trip','{"user_role": "driver", "required_status": "trip_assigned"}',100,'sync_trip_status','{}',4,1),
(58,'trip',82,79,NULL,NULL,100,NULL,NULL,83,1),
(59,'trip',83,4,NULL,NULL,100,NULL,NULL,5,1),
(61,'locker',73,6,NULL,NULL,100,'sync_locker_cell_status','{}',69,1),
(62,'locker',69,5,NULL,NULL,100,'sync_locker_cell_status','{}',7,1),
(63,'locker',79,76,NULL,NULL,100,NULL,NULL,68,1),
(74,'order',8,129,'can_close_cell','{"leg": "pickup", "user_role": "driver", "require_pin": false, "require_cell": true, "require_city": true, "stage_must_be": "driver_reserved", "required_status": "order_parcel_submitted", "allowed_cell_statuses": ["locker_opened", "locker_parcel_confirmed"]}',100,'close_cell_effect','{"leg": "pickup", "companions": [{"event_name": "locker_close_pickup", "entity_type": "locker", "entity_id_key": "cell_id"}]}',87,1),
(75,'order',87,134,'can_start_order_transit','{"required_status": "order_picked_up_from_post1"}',100,'sync_order_status','{}',88,1),
(76,'order',88,127,'can_open_cell','{"leg": "delivery", "user_role": "driver", "require_pin": true, "require_cell": true, "require_city": false, "stage_must_be": "driver_reserved", "required_status": "order_in_transit_to_post2", "allowed_cell_statuses": ["locker_reserved", "locker_occupied"]}',100,'open_cell_effect','{"leg": "delivery", "companions": [{"event_name": "locker_open_locker", "entity_type": "locker", "entity_id_key": "cell_id"}]}',89,1),
(77,'order',89,129,'can_close_cell','{"leg": "delivery", "user_role": "driver", "require_pin": false, "require_cell": true, "require_city": false, "stage_must_be": "driver_reserved", "required_status": "order_arrived_at_post2", "allowed_cell_statuses": ["locker_opened", "locker_parcel_confirmed"]}',100,'close_cell_effect','{"leg": "delivery", "companions": [{"event_name": "locker_close_locker", "entity_type": "locker", "entity_id_key": "cell_id"}]}',103,1),
(79,'locker',7,87,NULL,NULL,100,NULL,NULL,70,1),
(80,'order',103,127,'can_open_cell','{"leg": "delivery", "user_role": "client", "type_field": "delivery_type", "type_value": "self", "actor_field": "recipient_user_id", "require_pin": true, "require_cell": true, "require_city": true, "stage_must_be": "none", "required_status": "order_parcel_confirmed_post2", "allowed_cell_statuses": ["locker_reserved", "locker_occupied", "locker_parcel_confirmed"]}',100,'open_cell_effect','{"leg": "delivery", "companions": [{"event_name": "locker_open_locker", "entity_type": "locker", "entity_id_key": "cell_id"}]}',90,1),
(81,'order',90,129,'can_close_cell','{"leg": "delivery", "user_role": "client", "type_field": "delivery_type", "type_value": "self", "actor_field": "recipient_user_id", "require_pin": false, "require_cell": true, "require_city": true, "stage_must_be": "none", "required_status": "order_delivered_to_client", "allowed_cell_statuses": ["locker_opened", "locker_parcel_confirmed"]}',100,'close_cell_effect','{"leg": "delivery", "companions": [{"event_name": "locker_close_pickup", "entity_type": "locker", "entity_id_key": "cell_id"}]}',93,1),
(82,'order',103,90,NULL,NULL,100,NULL,NULL,91,1),
(83,'order',91,127,'can_open_cell','{"leg": "delivery", "user_role": "courier", "type_field": "delivery_type", "type_value": "courier", "require_pin": true, "require_cell": true, "require_city": true, "stage_must_be": "owned", "required_status": "order_courier2_assigned", "allowed_cell_statuses": ["locker_reserved", "locker_occupied"]}',100,'open_cell_effect','{"leg": "delivery", "companions": [{"event_name": "locker_open_locker", "entity_type": "locker", "entity_id_key": "cell_id"}]}',92,1),
(84,'order',92,129,'can_close_cell','{"leg": "delivery", "user_role": "courier", "type_field": "delivery_type", "type_value": "courier", "require_pin": false, "require_cell": true, "require_city": true, "stage_must_be": "owned", "required_status": "order_courier2_has_parcel", "allowed_cell_statuses": ["locker_opened", "locker_parcel_confirmed"]}',100,'close_cell_effect','{"leg": "delivery", "companions": [{"event_name": "locker_close_pickup", "entity_type": "locker", "entity_id_key": "cell_id"}]}',102,1),
(85,'order',60,93,NULL,NULL,100,NULL,NULL,61,1),
(86,'order',75,94,NULL,NULL,100,NULL,NULL,94,1),
(87,'order',88,94,NULL,NULL,100,NULL,NULL,94,1),
(88,'order',92,94,NULL,NULL,100,NULL,NULL,94,1),
(89,'order',1,95,NULL,NULL,100,NULL,NULL,95,1),
(90,'order',49,95,NULL,NULL,100,NULL,NULL,95,1),
(91,'order',60,95,NULL,NULL,100,NULL,NULL,95,1),
(92,'order',75,95,NULL,NULL,100,NULL,NULL,95,1),
(93,'order',84,95,NULL,NULL,100,NULL,NULL,95,1),
(94,'order',85,95,NULL,NULL,100,NULL,NULL,95,1),
(95,'order',87,95,NULL,NULL,100,NULL,NULL,95,1),
(96,'order',88,95,NULL,NULL,100,NULL,NULL,95,1),
(97,'order',89,95,NULL,NULL,100,NULL,NULL,95,1),
(98,'order',90,95,NULL,NULL,100,NULL,NULL,95,1),
(99,'order',91,95,NULL,NULL,100,NULL,NULL,95,1),
(100,'order',92,95,NULL,NULL,100,NULL,NULL,95,1),
(101,'trip',3,96,NULL,NULL,100,NULL,NULL,96,1),
(102,'trip',3,97,NULL,NULL,100,NULL,NULL,97,1),
(103,'trip',4,97,NULL,NULL,100,NULL,NULL,97,1),
(104,'trip',80,97,NULL,NULL,100,NULL,NULL,97,1),
(105,'trip',81,97,NULL,NULL,100,NULL,NULL,97,1),
(106,'trip',82,97,NULL,NULL,100,NULL,NULL,97,1),
(109,'trip',3,98,NULL,NULL,100,NULL,NULL,98,1),
(110,'trip',4,98,NULL,NULL,100,NULL,NULL,98,1),
(111,'trip',80,98,NULL,NULL,100,NULL,NULL,98,1),
(112,'trip',81,98,NULL,NULL,100,NULL,NULL,98,1),
(113,'trip',82,98,NULL,NULL,100,NULL,NULL,98,1),
(114,'trip',83,98,NULL,NULL,100,NULL,NULL,98,1),
(116,'order',49,99,NULL,NULL,100,NULL,NULL,1,1),
(117,'order',49,101,NULL,NULL,100,NULL,NULL,1,1),
(118,'order',91,100,NULL,NULL,100,NULL,NULL,89,1),
(119,'order',91,101,NULL,NULL,100,NULL,NULL,89,1),
(120,'trip',99,102,NULL,NULL,100,NULL,NULL,3,1),
(121,'locker',7,86,NULL,NULL,100,NULL,NULL,100,1),
(122,'locker',100,6,NULL,NULL,100,'sync_locker_cell_status','{}',79,1),
(123,'locker',7,103,NULL,NULL,100,NULL,NULL,101,1),
(124,'locker',101,6,NULL,NULL,100,'sync_locker_cell_status','{}',79,1),
(125,'order',102,137,'can_confirm_courier2_delivery','{"leg": "delivery", "user_role": "courier", "type_field": "delivery_type", "type_value": "courier", "require_pin": true, "stage_must_be": "owned", "required_status": "order_courier2_parcel_delivered"}',100,'confirm_courier2_delivery_effect','{}',93,1),
(126,'locker',7,6,NULL,NULL,100,'sync_locker_cell_status','{}',69,1),
(127,'locker',7,105,NULL,NULL,100,'sync_locker_cell_status','{}',79,1),
(128,'order',103,93,NULL,NULL,100,NULL,NULL,61,1),
(129,'order',103,95,NULL,NULL,100,NULL,NULL,95,1),
(130,'order',1,49,'can_assign_executor','{"leg": "pickup", "user_role": "courier", "type_field": "pickup_type", "type_value": "courier", "require_cell": true, "require_city": true, "stage_must_be": "free", "required_status": "order_created"}',100,'assign_executor_effect','{"leg": "pickup"}',49,1),
(131,'locker',6,106,NULL,NULL,100,NULL,NULL,70,1),
(132,'order',1,74,NULL,NULL,100,NULL,NULL,78,1),
(133,'trip',3,97,NULL,NULL,100,NULL,NULL,99,1),
(134,'locker',69,106,NULL,NULL,100,NULL,NULL,70,1),
(135,'trip',4,136,'can_complete_trip','{"user_role": "driver", "required_status": "trip_in_progress"}',100,'sync_trip_status','{}',5,1),
(136,'order',1,127,'can_open_cell','{"leg": "pickup", "user_role": "client", "type_field": "pickup_type", "type_value": "self", "actor_field": "client_user_id", "require_pin": true, "require_cell": true, "require_city": true, "stage_must_be": "none", "required_status": "order_created", "allowed_cell_statuses": ["locker_reserved", "locker_occupied"]}',100,'open_cell_effect','{"leg": "pickup", "companions": [{"event_name": "locker_open_locker", "entity_type": "locker", "entity_id_key": "cell_id"}]}',104,1),
(137,'order',104,129,'can_close_cell','{"leg": "pickup", "user_role": "client", "type_field": "pickup_type", "type_value": "self", "actor_field": "client_user_id", "require_pin": false, "require_cell": true, "require_city": true, "stage_must_be": "none", "required_status": "order_client_post1", "allowed_cell_statuses": ["locker_opened", "locker_parcel_confirmed"]}',100,'close_cell_effect','{"leg": "pickup", "companions": [{"event_name": "locker_close_locker", "entity_type": "locker", "entity_id_key": "cell_id"}]}',60,1),
(145,'driver_reservations',109,130,'can_start_loading','{"user_role": "driver", "required_status": "reservation_active"}',100,'sync_reservation_status','{}',110,1),
(146,'driver_reservations',110,131,'can_complete_loading','{"user_role": "driver", "required_status": "reservation_loading"}',100,'sync_reservation_status','{}',111,1),
(147,'driver_reservations',109,135,'can_expire_reservation','{"user_role": "driver", "required_status": "reservation_active"}',100,'cancel_reservation_effect','{}',112,1),
(148,'driver_reservations',110,115,NULL,NULL,100,NULL,NULL,112,1),
(149,'driver_reservations',109,132,'can_cancel_reservation','{"user_role": "driver", "required_status": "reservation_active"}',100,'cancel_reservation_effect','{}',113,1),
(150,'driver_reservations',110,132,'can_cancel_reservation','{"user_role": "driver", "required_status": "reservation_loading"}',100,'cancel_reservation_effect','{}',113,1),
(151,'trip',4,117,NULL,NULL,100,NULL,NULL,114,1),
(152,'trip',3,117,NULL,NULL,100,NULL,NULL,114,1),
(153,'trip',97,123,NULL,NULL,100,NULL,NULL,3,1),
(154,'order',95,49,NULL,NULL,100,NULL,NULL,49,1),
(155,'order',95,90,NULL,NULL,100,NULL,NULL,91,1),
(156,'trip',97,124,NULL,NULL,100,NULL,NULL,4,1),
(157,'locker',6,73,NULL,NULL,100,NULL,NULL,71,1),
(158,'locker',7,73,NULL,NULL,100,NULL,NULL,71,1),
(159,'order',60,74,NULL,NULL,100,NULL,NULL,78,1),
(160,'order',49,74,NULL,NULL,100,NULL,NULL,78,1),
(161,'order',75,74,NULL,NULL,100,NULL,NULL,78,1),
(162,'order',8,74,NULL,NULL,100,NULL,NULL,78,1),
(163,'order',87,74,NULL,NULL,100,NULL,NULL,78,1),
(164,'order',88,74,NULL,NULL,100,NULL,NULL,78,1),
(165,'order',89,74,NULL,NULL,100,NULL,NULL,78,1),
(166,'order',103,74,NULL,NULL,100,NULL,NULL,78,1),
(167,'order',1,125,'can_assign_executor','{"leg": "pickup", "user_role": "courier", "type_field": "pickup_type", "type_value": "courier", "require_cell": true, "require_city": true, "stage_must_be": "free", "required_status": "order_created"}',100,'assign_executor_effect','{"leg": "pickup"}',49,1),
(168,'order',103,125,'can_assign_executor','{"leg": "delivery", "user_role": "courier", "type_field": "delivery_type", "type_value": "courier", "require_cell": true, "require_city": true, "stage_must_be": "free", "required_status": "order_parcel_confirmed_post2"}',100,'assign_executor_effect','{"leg": "delivery"}',91,1),
(169,'order',49,126,'can_remove_executor','{"leg": "pickup", "user_role": "courier", "type_field": "pickup_type", "type_value": "courier", "require_cell": true, "require_city": true, "stage_must_be": "owned", "required_status": "order_courier1_assigned"}',100,'remove_executor_effect','{"leg": "pickup"}',1,1),
(170,'order',91,126,'can_remove_executor','{"leg": "delivery", "user_role": "courier", "type_field": "delivery_type", "type_value": "courier", "require_cell": true, "require_city": true, "stage_must_be": "owned", "required_status": "order_courier2_assigned"}',100,'remove_executor_effect','{"leg": "delivery"}',89,1);
/*!40000 ALTER TABLE `fsm_transitions` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table `locker_cells`
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
  `current_request_id` bigint DEFAULT NULL COMMENT 'active order_requests.id while reserved before order bind',
  `created_at` datetime DEFAULT CURRENT_TIMESTAMP,
  `updated_at` datetime DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  UNIQUE KEY `locker_id` (`locker_id`,`cell_code`),
  CONSTRAINT `locker_cells_ibfk_1` FOREIGN KEY (`locker_id`) REFERENCES `lockers` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=95 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `locker_cells`
--

LOCK TABLES `locker_cells` WRITE;
/*!40000 ALTER TABLE `locker_cells` DISABLE KEYS */;
INSERT INTO `locker_cells` (`id`,`locker_id`,`cell_code`,`cell_type`,`status`,`current_order_id`,`current_request_id`,`created_at`,`updated_at`) VALUES
(1,1,'S-01','S','locker_closed_empty',1611,NULL,'2025-11-22 15:23:13','2026-07-24 13:02:58'),
(2,1,'S-02','S','locker_reserved',1619,NULL,'2025-11-22 15:23:13','2026-07-26 14:28:34'),
(3,1,'S-03','S','locker_reserved',1620,NULL,'2025-11-22 15:23:13','2026-07-27 09:31:18'),
(46,1,'M-01','M','locker_reserved',1614,NULL,'2026-07-18 18:19:32','2026-07-24 16:15:17'),
(47,1,'M-02','M','locker_reserved',1615,NULL,'2026-07-18 18:19:32','2026-07-24 16:25:28'),
(48,1,'M-03','M','locker_reserved',1616,NULL,'2026-07-18 18:19:32','2026-07-26 09:48:50'),
(49,1,'L-01','L','locker_free',NULL,NULL,'2026-07-18 18:19:32','2026-07-24 12:47:20'),
(50,1,'L-02','L','locker_free',NULL,NULL,'2026-07-18 18:19:32','2026-07-24 12:47:20'),
(51,1,'L-03','L','locker_free',NULL,NULL,'2026-07-18 18:19:32','2026-07-24 12:47:20'),
(52,2,'S-01','S','locker_closed_empty',1611,NULL,'2026-07-18 18:19:33','2026-07-24 13:06:02'),
(53,2,'S-02','S','locker_reserved',1619,NULL,'2026-07-18 18:19:33','2026-07-26 14:28:34'),
(54,2,'S-03','S','locker_reserved',1620,NULL,'2026-07-18 18:19:33','2026-07-27 09:31:18'),
(55,2,'M-01','M','locker_reserved',1614,NULL,'2026-07-18 18:19:33','2026-07-24 16:15:20'),
(56,2,'M-02','M','locker_reserved',1615,NULL,'2026-07-18 18:19:33','2026-07-24 16:25:34'),
(57,2,'M-03','M','locker_reserved',1616,NULL,'2026-07-18 18:19:33','2026-07-26 09:48:55'),
(58,2,'L-01','L','locker_free',NULL,NULL,'2026-07-18 18:19:33','2026-07-24 12:47:20'),
(59,2,'L-02','L','locker_free',NULL,NULL,'2026-07-18 18:19:34','2026-07-24 12:47:20'),
(60,2,'L-03','L','locker_free',NULL,NULL,'2026-07-18 18:19:34','2026-07-24 12:47:20'),
(61,3,'S-01','S','locker_free',NULL,NULL,'2026-07-18 18:19:34','2026-07-24 12:47:20'),
(62,3,'S-02','S','locker_free',NULL,NULL,'2026-07-18 18:19:34','2026-07-24 12:47:20'),
(63,3,'S-03','S','locker_free',NULL,NULL,'2026-07-18 18:19:34','2026-07-24 12:47:20'),
(64,3,'M-01','M','locker_closed_empty',1612,NULL,'2026-07-18 18:19:34','2026-07-24 13:03:15'),
(65,3,'M-02','M','locker_reserved',1617,NULL,'2026-07-18 18:19:34','2026-07-26 11:05:23'),
(66,3,'M-03','M','locker_reserved',1618,NULL,'2026-07-18 18:19:35','2026-07-26 12:36:08'),
(67,3,'L-01','L','locker_closed_empty',1613,NULL,'2026-07-18 18:19:35','2026-07-24 13:03:31'),
(68,3,'L-02','L','locker_free',NULL,NULL,'2026-07-18 18:19:35','2026-07-24 12:47:20'),
(69,3,'L-03','L','locker_free',NULL,NULL,'2026-07-18 18:19:35','2026-07-24 12:47:20'),
(70,1,'P-01','P','locker_closed_empty',1610,NULL,'2026-07-24 07:16:34','2026-07-24 13:02:43'),
(71,2,'P-01','P','locker_closed_empty',1610,NULL,'2026-07-24 07:16:34','2026-07-24 13:05:33'),
(72,3,'P-01','P','locker_free',NULL,NULL,'2026-07-24 07:16:34','2026-07-24 12:47:20'),
(73,4,'P-01','P','locker_free',NULL,NULL,'2026-07-24 07:16:34','2026-07-24 12:47:20'),
(77,3,'P-02','P','locker_free',NULL,NULL,'2026-07-24 07:22:46','2026-07-24 12:47:20'),
(78,2,'P-02','P','locker_free',NULL,NULL,'2026-07-24 07:22:46','2026-07-24 12:47:20'),
(79,1,'P-02','P','locker_free',NULL,NULL,'2026-07-24 07:22:46','2026-07-24 12:47:20'),
(80,3,'P-03','P','locker_free',NULL,NULL,'2026-07-24 07:22:46','2026-07-24 12:47:20'),
(81,2,'P-03','P','locker_free',NULL,NULL,'2026-07-24 07:22:46','2026-07-24 12:47:20'),
(82,1,'P-03','P','locker_free',NULL,NULL,'2026-07-24 07:22:46','2026-07-24 12:47:20'),
(84,4,'S-01','S','locker_free',NULL,NULL,'2026-07-24 07:22:46','2026-07-24 12:47:20'),
(85,4,'S-02','S','locker_free',NULL,NULL,'2026-07-24 07:22:46','2026-07-24 12:47:20'),
(86,4,'S-03','S','locker_free',NULL,NULL,'2026-07-24 07:22:46','2026-07-24 12:47:20'),
(87,4,'M-01','M','locker_closed_empty',1612,NULL,'2026-07-24 07:22:46','2026-07-24 13:06:25'),
(88,4,'M-02','M','locker_reserved',1617,NULL,'2026-07-24 07:22:46','2026-07-26 11:05:32'),
(89,4,'M-03','M','locker_reserved',1618,NULL,'2026-07-24 07:22:46','2026-07-26 12:36:08'),
(90,4,'L-01','L','locker_closed_empty',1613,NULL,'2026-07-24 07:22:46','2026-07-24 13:06:40'),
(91,4,'L-02','L','locker_free',NULL,NULL,'2026-07-24 07:22:46','2026-07-24 12:47:20'),
(92,4,'L-03','L','locker_free',NULL,NULL,'2026-07-24 07:22:46','2026-07-24 12:47:20'),
(93,4,'P-02','P','locker_free',NULL,NULL,'2026-07-24 07:22:46','2026-07-24 12:47:20'),
(94,4,'P-03','P','locker_free',NULL,NULL,'2026-07-24 07:22:46','2026-07-24 12:47:20');
/*!40000 ALTER TABLE `locker_cells` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table `locker_models`
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
INSERT INTO `locker_models` (`id`,`model_name`,`description`,`cell_count_s`,`cell_count_m`,`cell_count_l`,`cell_count_p`,`created_at`) VALUES
(1,'Model-Post1',NULL,10,5,2,1,'2025-10-29 17:20:54'),
(2,'Model-2',NULL,10,5,2,1,'2025-11-21 13:37:49'),
(3,'Model-3',NULL,10,5,2,1,'2025-11-21 13:37:49');
/*!40000 ALTER TABLE `locker_models` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table `lockers`
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
INSERT INTO `lockers` (`id`,`model_id`,`locker_code`,`city`,`location_address`,`latitude`,`longitude`,`status`,`created_at`) VALUES
(1,1,'POST1','Москва','Москва, ул. Тверская, д. 1',NULL,NULL,'locker_active','2025-11-22 15:22:48'),
(2,1,'POST2','Санкт-Петербург','Санкт-Петербург, Невский пр., д. 1',NULL,NULL,'locker_active','2025-11-22 15:22:48'),
(3,1,'POST3','Москва','Москва, Ленинградский проспект, д. 1',NULL,NULL,'locker_active','2025-11-22 15:22:48'),
(4,1,'POST4','Санкт-Петербург','Санкт-Петербург, Лиговский пр., д. 1',NULL,NULL,'locker_active','2026-07-24 07:16:34');
/*!40000 ALTER TABLE `lockers` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table `order_requests`
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
  `from_address` varchar(512) DEFAULT NULL,
  `to_address` varchar(512) DEFAULT NULL,
  `source_cell_id` bigint DEFAULT NULL,
  `dest_cell_id` bigint DEFAULT NULL,
  `expires_at` datetime DEFAULT NULL,
  `status` enum('PENDING','COMPLETED','FAILED') NOT NULL DEFAULT 'PENDING',
  `order_id` int DEFAULT NULL,
  `error_code` varchar(100) DEFAULT NULL,
  `error_message` text,
  `created_at` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `recipient_user_id` int DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `recipient_user_id` (`recipient_user_id`),
  CONSTRAINT `order_requests_ibfk_1` FOREIGN KEY (`recipient_user_id`) REFERENCES `users` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=348 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `order_requests`
--

LOCK TABLES `order_requests` WRITE;
/*!40000 ALTER TABLE `order_requests` DISABLE KEYS */;
INSERT INTO `order_requests` (`id`,`client_user_id`,`parcel_type`,`cell_size`,`sender_delivery`,`recipient_delivery`,`from_address`,`to_address`,`source_cell_id`,`dest_cell_id`,`expires_at`,`status`,`order_id`,`error_code`,`error_message`,`created_at`,`recipient_user_id`) VALUES
(1,0,'string','string','string','string',NULL,NULL,NULL,NULL,NULL,'FAILED',NULL,'NOT_IMPLEMENTED','order_creation handler not implemented yet','2025-12-07 13:53:25',NULL),
(2,0,'string','string','string','string',NULL,NULL,NULL,NULL,NULL,'FAILED',NULL,'NO_FREE_CELLS','Не найдены свободные ячейки нужного размера','2025-12-07 16:37:12',NULL),
(3,1005,'test','S','courier','courier',NULL,NULL,NULL,NULL,NULL,'COMPLETED',6,NULL,NULL,'2025-12-07 16:45:30',NULL),
(345,3,'документы','M','courier','courier','Москва, ул. Тверская, д. 1','Санкт-Петербург, Невский пр., д. 1',66,89,'2026-07-26 12:41:33','COMPLETED',1618,NULL,NULL,'2026-07-26 12:35:54',4),
(346,3,'документы','S','courier','courier','Москва, ул. Тверская, д. 1','Санкт-Петербург, Невский пр., д. 1',2,53,'2026-07-26 14:33:53','COMPLETED',1619,NULL,NULL,'2026-07-26 14:28:14',4),
(347,3,'документы','S','courier','courier','Москва, ул. Тверская, д. 1','Санкт-Петербург, Невский пр., д. 1',3,54,'2026-07-27 09:36:18','COMPLETED',1620,NULL,NULL,'2026-07-27 09:30:40',4);
/*!40000 ALTER TABLE `order_requests` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table `orders`
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
  `from_address` varchar(512) DEFAULT NULL,
  `to_address` varchar(512) DEFAULT NULL,
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
) ENGINE=InnoDB AUTO_INCREMENT=1621 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `orders`
--

LOCK TABLES `orders` WRITE;
/*!40000 ALTER TABLE `orders` DISABLE KEYS */;
INSERT INTO `orders` (`id`,`status`,`description`,`delivery_type`,`parcel_type`,`from_address`,`to_address`,`pickup_type`,`source_cell_id`,`dest_cell_id`,`updated_at`,`created_at`,`client_user_id`,`recipient_user_id`) VALUES
(1610,'order_completed','документы (P)','courier','документы','Москва, ул. Тверская, д. 1','Санкт-Петербург, Невский пр., д. 1','courier',70,71,'2026-07-24 13:05:42','2026-07-24 13:00:23',3,4),
(1611,'order_completed','документы (S)','courier','документы','Москва, ул. Тверская, д. 1','Санкт-Петербург, Невский пр., д. 1','self',1,52,'2026-07-24 13:06:10','2026-07-24 13:00:58',11,14),
(1612,'order_completed','документы (M)','self','документы','Москва, Ленинградский проспект, д. 1','Санкт-Петербург, Лиговский пр., д. 1','courier',64,87,'2026-07-24 13:06:24','2026-07-24 13:01:23',12,15),
(1613,'order_completed','документы (L)','self','документы','Москва, Ленинградский проспект, д. 1','Санкт-Петербург, Лиговский пр., д. 1','self',67,90,'2026-07-24 13:06:39','2026-07-24 13:01:56',13,16),
(1614,'order_courier1_assigned','документы (M)','courier','документы','Москва, ул. Тверская, д. 1','Санкт-Петербург, Невский пр., д. 1','courier',46,55,'2026-07-24 16:15:26','2026-07-24 16:15:09',3,4),
(1615,'order_courier1_assigned','документы (M)','courier','документы','Москва, ул. Тверская, д. 1','Санкт-Петербург, Невский пр., д. 1','courier',47,56,'2026-07-24 16:25:40','2026-07-24 16:25:22',3,4),
(1616,'order_courier1_assigned','документы (M)','courier','документы','Москва, ул. Тверская, д. 1','Санкт-Петербург, Невский пр., д. 1','courier',48,57,'2026-07-26 09:49:02','2026-07-26 09:48:41',3,4),
(1617,'order_courier1_assigned','документы (M)','courier','документы','Москва, ул. Тверская, д. 1','Санкт-Петербург, Невский пр., д. 1','courier',65,88,'2026-07-26 11:05:41','2026-07-26 11:05:14',3,4),
(1618,'order_courier1_assigned','документы (M)','courier','документы','Москва, ул. Тверская, д. 1','Санкт-Петербург, Невский пр., д. 1','courier',66,89,'2026-07-26 12:36:15','2026-07-26 12:36:08',3,4),
(1619,'order_courier1_assigned','документы (S)','courier','документы','Москва, ул. Тверская, д. 1','Санкт-Петербург, Невский пр., д. 1','courier',2,53,'2026-07-26 14:28:44','2026-07-26 14:28:34',3,4),
(1620,'order_courier1_assigned','документы (S)','courier','документы','Москва, ул. Тверская, д. 1','Санкт-Петербург, Невский пр., д. 1','courier',3,54,'2026-07-27 09:31:28','2026-07-27 09:31:18',3,4);
/*!40000 ALTER TABLE `orders` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table `stage_orders`
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
INSERT INTO `stage_orders` (`trip_id`,`direction_id`,`order_id`,`leg`,`courier_user_id`,`reservation_id`,`reserved_by_driver_id`) VALUES
(61,16,1610,'pickup',2,53,1),
(61,16,1610,'delivery',6,53,1),
(61,16,1611,'pickup',NULL,53,1),
(61,16,1611,'delivery',8,53,1),
(61,17,1612,'pickup',7,53,1),
(61,17,1612,'delivery',NULL,53,1),
(61,17,1613,'pickup',NULL,53,1),
(61,17,1613,'delivery',NULL,53,1),
(NULL,NULL,1614,'pickup',2,NULL,NULL),
(NULL,NULL,1614,'delivery',NULL,NULL,NULL),
(NULL,NULL,1615,'pickup',2,NULL,NULL),
(NULL,NULL,1615,'delivery',NULL,NULL,NULL),
(NULL,NULL,1616,'pickup',2,NULL,NULL),
(NULL,NULL,1616,'delivery',NULL,NULL,NULL),
(NULL,NULL,1617,'pickup',2,NULL,NULL),
(NULL,NULL,1617,'delivery',NULL,NULL,NULL),
(NULL,NULL,1618,'pickup',2,NULL,NULL),
(NULL,NULL,1618,'delivery',NULL,NULL,NULL),
(NULL,NULL,1619,'pickup',2,NULL,NULL),
(NULL,NULL,1619,'delivery',NULL,NULL,NULL),
(NULL,NULL,1620,'pickup',2,NULL,NULL),
(NULL,NULL,1620,'delivery',NULL,NULL,NULL);
/*!40000 ALTER TABLE `stage_orders` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table `trips`
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
) ENGINE=InnoDB AUTO_INCREMENT=62 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `trips`
--

LOCK TABLES `trips` WRITE;
/*!40000 ALTER TABLE `trips` DISABLE KEYS */;
INSERT INTO `trips` (`id`,`driver_user_id`,`from_city`,`to_city`,`pickup_locker_id`,`delivery_locker_id`,`status`,`description`,`active`,`created_at`) VALUES
(61,1,'Москва','Санкт-Петербург',1,2,'trip_completed',NULL,0,'2026-07-24 13:03:34');
/*!40000 ALTER TABLE `trips` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table `users`
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
  `telegram_chat_id` varchar(64) DEFAULT NULL COMMENT 'Telegram chat_id for order progress push',
  PRIMARY KEY (`id`),
  KEY `role_name` (`role_name`)
) ENGINE=InnoDB AUTO_INCREMENT=1000040 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `users`
--

LOCK TABLES `users` WRITE;
/*!40000 ALTER TABLE `users` DISABLE KEYS */;
INSERT INTO `users` (`id`,`name`,`role_name`,`city`,`phone`,`telegram_chat_id`) VALUES
(1,'User 1','driver','Москва',NULL,NULL),
(2,'User 2','courier','Москва',NULL,NULL),
(3,'User 3','client','Москва',NULL,'774531703'),
(4,'User 4','client','Санкт-Петербург',NULL,NULL),
(5,'User 5','driver','Санкт-Петербург',NULL,NULL),
(6,'User 6','courier','Санкт-Петербург',NULL,NULL),
(7,'User 7','courier','Москва',NULL,NULL),
(8,'User 8','courier','Санкт-Петербург',NULL,NULL),
(9,'User 9','driver','Москва',NULL,NULL),
(10,'User 10','driver','Санкт-Петербург',NULL,NULL),
(11,'User 11','client','Москва',NULL,NULL),
(12,'User 12','client','Москва',NULL,NULL),
(13,'User 13','client','Москва',NULL,NULL),
(14,'User 13','client','Санкт-Петербург',NULL,NULL),
(15,'User 13','client','Санкт-Петербург',NULL,NULL),
(16,'User 13','client','Санкт-Петербург',NULL,NULL),
(1000039,'Иван Иванов','client','Москва','+79091235588',NULL);
/*!40000 ALTER TABLE `users` ENABLE KEYS */;
UNLOCK TABLES;

SET FOREIGN_KEY_CHECKS=1;
SET UNIQUE_CHECKS=1;
