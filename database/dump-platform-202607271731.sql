-- Platform DB dump (tables + data only)
-- Generated 2026-07-27T13:31:41.266096+00:00
-- No triggers / events / routines

SET NAMES utf8mb4;
SET FOREIGN_KEY_CHECKS=0;
SET UNIQUE_CHECKS=0;
SET SQL_MODE='NO_AUTO_VALUE_ON_ZERO';

--
-- Table `domain_secrets`
--

DROP TABLE IF EXISTS `domain_secrets`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `domain_secrets` (
  `service_id` varchar(64) NOT NULL,
  `key` varchar(128) NOT NULL,
  `value_enc` text NOT NULL,
  `created_at` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `updated_at` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`service_id`,`key`),
  KEY `idx_domain_secrets_service` (`service_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `domain_secrets`
--

LOCK TABLES `domain_secrets` WRITE;
/*!40000 ALTER TABLE `domain_secrets` DISABLE KEYS */;
INSERT INTO `domain_secrets` (`service_id`,`key`,`value_enc`,`created_at`,`updated_at`) VALUES
('svc_courier_01','CORE','gAAAAABqZy1lujueh_PrfiW6vHz5Bvxk24gsE_5ZJflLPeFafWeH5XAQf4qN2_oIIm21Pz_U0iCw6-Mlh3ExGWbI6ZvRko-nAFglsOjQ6_A6XEBd0pqkceAJ13smISUznzqljNdXEA-l3sXBacvAHiKhH3jRF5t8zuCDaixVNFvX0PLQPMRkRso=','2026-07-27 10:14:48','2026-07-27 10:14:48'),
('svc_courier_01','TELEGRAM_BOT_TOKEN','gAAAAABqZx1d8AbiycXwQKkMeXkcJqxhvuZRhf1Qhi0S0VgW0PRx3aEBA_s0TjSQNT-iCxkrowthZTrRnVgB4eKM32eFw7zZjwfv5MCY_HFtXdxQafBoOdifFyHKlHL8RetpSJTo05nu','2026-07-27 09:06:26','2026-07-27 09:06:26'),
('svc_courier_01','TELEGRAM_BOT_USERNAME','gAAAAABqZx2FrvwU7I_Af2KSFEZe7NTKLSVzKu7tZWDPljW263oDdLF-zIl4sELbpdvBX27DjaNVnJQJWLuYzf98n7z3EXIeGQ==','2026-07-27 09:07:04','2026-07-27 09:07:04');
/*!40000 ALTER TABLE `domain_secrets` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table `domain_services`
--

DROP TABLE IF EXISTS `domain_services`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `domain_services` (
  `service_id` varchar(64) NOT NULL,
  `cartridge_type` varchar(64) NOT NULL,
  `version` varchar(32) NOT NULL,
  `package_ref` varchar(512) DEFAULT NULL,
  `package_checksum` varchar(128) DEFAULT NULL,
  `db_secret_ref` varchar(256) NOT NULL,
  `pool_options_json` json DEFAULT NULL,
  `status` varchar(32) NOT NULL DEFAULT 'pending',
  `validation_report` text,
  `activated_by` varchar(128) DEFAULT NULL,
  `created_at` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `updated_at` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`service_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `domain_services`
--

LOCK TABLES `domain_services` WRITE;
/*!40000 ALTER TABLE `domain_services` DISABLE KEYS */;
INSERT INTO `domain_services` (`service_id`,`cartridge_type`,`version`,`package_ref`,`package_checksum`,`db_secret_ref`,`pool_options_json`,`status`,`validation_report`,`activated_by`,`created_at`,`updated_at`) VALUES
('svc_courier_01','courier','0.1.0','domains.courier',NULL,'DOMAIN_DATABASE_URL',NULL,'active',NULL,'seed','2026-07-18 17:44:02','2026-07-18 17:44:02');
/*!40000 ALTER TABLE `domain_services` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table `entity_fsm_state`
--

DROP TABLE IF EXISTS `entity_fsm_state`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `entity_fsm_state` (
  `service_id` varchar(64) NOT NULL,
  `entity_type` varchar(128) NOT NULL,
  `entity_id` bigint NOT NULL,
  `current_state` varchar(128) NOT NULL,
  `updated_at` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`service_id`,`entity_type`,`entity_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `entity_fsm_state`
--

LOCK TABLES `entity_fsm_state` WRITE;
/*!40000 ALTER TABLE `entity_fsm_state` DISABLE KEYS */;
INSERT INTO `entity_fsm_state` (`service_id`,`entity_type`,`entity_id`,`current_state`,`updated_at`) VALUES
('svc_courier_01','driver_reservations',53,'reservation_completed','2026-07-24 13:03:39'),
('svc_courier_01','locker',1,'locker_closed_empty','2026-07-24 13:02:58'),
('svc_courier_01','locker',2,'locker_reserved','2026-07-26 14:28:24'),
('svc_courier_01','locker',3,'locker_reserved','2026-07-27 09:31:08'),
('svc_courier_01','locker',46,'locker_reserved','2026-07-24 16:15:17'),
('svc_courier_01','locker',47,'locker_reserved','2026-07-24 16:25:28'),
('svc_courier_01','locker',48,'locker_reserved','2026-07-26 09:48:49'),
('svc_courier_01','locker',52,'locker_closed_empty','2026-07-24 13:06:02'),
('svc_courier_01','locker',53,'locker_reserved','2026-07-26 14:28:30'),
('svc_courier_01','locker',54,'locker_reserved','2026-07-27 09:31:14'),
('svc_courier_01','locker',55,'locker_reserved','2026-07-24 16:15:20'),
('svc_courier_01','locker',56,'locker_reserved','2026-07-24 16:25:33'),
('svc_courier_01','locker',57,'locker_reserved','2026-07-26 09:48:55'),
('svc_courier_01','locker',64,'locker_closed_empty','2026-07-24 13:03:15'),
('svc_courier_01','locker',65,'locker_reserved','2026-07-26 11:05:23'),
('svc_courier_01','locker',66,'locker_reserved','2026-07-26 12:36:01'),
('svc_courier_01','locker',67,'locker_closed_empty','2026-07-24 13:03:30'),
('svc_courier_01','locker',70,'locker_closed_empty','2026-07-24 13:02:43'),
('svc_courier_01','locker',71,'locker_closed_empty','2026-07-24 13:05:33'),
('svc_courier_01','locker',87,'locker_closed_empty','2026-07-24 13:06:25'),
('svc_courier_01','locker',88,'locker_reserved','2026-07-26 11:05:31'),
('svc_courier_01','locker',89,'locker_reserved','2026-07-26 12:36:05'),
('svc_courier_01','locker',90,'locker_closed_empty','2026-07-24 13:06:39'),
('svc_courier_01','order',1610,'order_completed','2026-07-24 13:05:42'),
('svc_courier_01','order',1611,'order_completed','2026-07-24 13:06:09'),
('svc_courier_01','order',1612,'order_completed','2026-07-24 13:06:23'),
('svc_courier_01','order',1613,'order_completed','2026-07-24 13:06:38'),
('svc_courier_01','order',1614,'order_courier1_assigned','2026-07-24 16:15:25'),
('svc_courier_01','order',1615,'order_courier1_assigned','2026-07-24 16:25:40'),
('svc_courier_01','order',1616,'order_courier1_assigned','2026-07-26 09:49:02'),
('svc_courier_01','order',1617,'order_courier1_assigned','2026-07-26 11:05:41'),
('svc_courier_01','order',1618,'order_courier1_assigned','2026-07-26 12:36:15'),
('svc_courier_01','order',1619,'order_courier1_assigned','2026-07-26 14:28:42'),
('svc_courier_01','order',1620,'order_courier1_assigned','2026-07-27 09:31:27'),
('svc_courier_01','order_request',345,'COMPLETED','2026-07-26 12:36:10'),
('svc_courier_01','order_request',346,'COMPLETED','2026-07-26 14:28:36'),
('svc_courier_01','order_request',347,'COMPLETED','2026-07-27 09:31:21'),
('svc_courier_01','trip',61,'trip_completed','2026-07-24 13:05:12');
/*!40000 ALTER TABLE `entity_fsm_state` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table `fsm_saga_children`
--

DROP TABLE IF EXISTS `fsm_saga_children`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `fsm_saga_children` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `saga_id` bigint NOT NULL,
  `instance_id` bigint NOT NULL,
  `entity_type` varchar(128) NOT NULL,
  `entity_id` bigint NOT NULL,
  `process_name` varchar(128) NOT NULL,
  `status` varchar(32) NOT NULL DEFAULT 'PENDING',
  `last_error` text,
  `created_at` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `updated_at` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  `finished_at` datetime DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `uq_saga_child_instance` (`instance_id`),
  KEY `idx_saga_children_saga_status` (`saga_id`,`status`),
  CONSTRAINT `fk_saga_children_saga` FOREIGN KEY (`saga_id`) REFERENCES `fsm_sagas` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=10 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `fsm_saga_children`
--

LOCK TABLES `fsm_saga_children` WRITE;
/*!40000 ALTER TABLE `fsm_saga_children` DISABLE KEYS */;
INSERT INTO `fsm_saga_children` (`id`,`saga_id`,`instance_id`,`entity_type`,`entity_id`,`process_name`,`status`,`last_error`,`created_at`,`updated_at`,`finished_at`) VALUES
(1,1,96,'order',1596,'start_order_transit','COMPLETED',NULL,'2026-07-24 06:25:33','2026-07-24 06:25:40','2026-07-24 06:25:40'),
(2,1,97,'order',1597,'start_order_transit','COMPLETED',NULL,'2026-07-24 06:25:33','2026-07-24 06:41:31','2026-07-24 06:41:31'),
(3,1,98,'order',1598,'start_order_transit','COMPLETED',NULL,'2026-07-24 06:25:34','2026-07-24 06:41:31','2026-07-24 06:41:31'),
(4,2,124,'order',1601,'start_order_transit','COMPLETED',NULL,'2026-07-24 08:10:56','2026-07-24 08:11:00','2026-07-24 08:11:00'),
(5,2,125,'order',1602,'start_order_transit','COMPLETED',NULL,'2026-07-24 08:10:56','2026-07-24 08:11:05','2026-07-24 08:11:05'),
(6,3,185,'order',1610,'start_order_transit','COMPLETED',NULL,'2026-07-24 13:03:43','2026-07-24 13:03:50','2026-07-24 13:03:50'),
(7,3,186,'order',1611,'start_order_transit','COMPLETED',NULL,'2026-07-24 13:03:44','2026-07-24 13:03:55','2026-07-24 13:03:55'),
(8,3,187,'order',1612,'start_order_transit','COMPLETED',NULL,'2026-07-24 13:03:45','2026-07-24 13:03:59','2026-07-24 13:03:59'),
(9,3,188,'order',1613,'start_order_transit','COMPLETED',NULL,'2026-07-24 13:03:45','2026-07-24 13:04:03','2026-07-24 13:04:03');
/*!40000 ALTER TABLE `fsm_saga_children` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table `fsm_sagas`
--

DROP TABLE IF EXISTS `fsm_sagas`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `fsm_sagas` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `service_id` varchar(64) NOT NULL,
  `status` varchar(32) NOT NULL DEFAULT 'RUNNING',
  `fail_policy` varchar(32) NOT NULL DEFAULT 'fail_fast',
  `on_success_json` json DEFAULT NULL,
  `on_fail_json` json DEFAULT NULL,
  `payload_json` json DEFAULT NULL,
  `actor_id` bigint DEFAULT NULL,
  `created_at` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `updated_at` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  `finished_at` datetime DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `idx_sagas_service_status` (`service_id`,`status`)
) ENGINE=InnoDB AUTO_INCREMENT=4 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `fsm_sagas`
--

LOCK TABLES `fsm_sagas` WRITE;
/*!40000 ALTER TABLE `fsm_sagas` DISABLE KEYS */;
INSERT INTO `fsm_sagas` (`id`,`service_id`,`status`,`fail_policy`,`on_success_json`,`on_fail_json`,`payload_json`,`actor_id`,`created_at`,`updated_at`,`finished_at`) VALUES
(1,'svc_courier_01','SUCCEEDED','fail_fast','{"payload": {"source": "start_trip", "driver_user_id": 1, "executor_user_id": 1}, "entity_id": 59, "entity_type": "trip", "process_name": "start_trip", "initial_state": "trip_assigned"}',NULL,'{}',1,'2026-07-24 06:25:32','2026-07-24 06:41:32','2026-07-24 06:41:32'),
(2,'svc_courier_01','SUCCEEDED','fail_fast','{"payload": {"source": "start_trip", "driver_user_id": 5, "executor_user_id": 5}, "entity_id": 60, "entity_type": "trip", "process_name": "start_trip", "initial_state": "trip_assigned"}',NULL,'{}',5,'2026-07-24 08:10:55','2026-07-24 08:11:05','2026-07-24 08:11:05'),
(3,'svc_courier_01','SUCCEEDED','fail_fast','{"payload": {"source": "start_trip", "driver_user_id": 1, "executor_user_id": 1}, "entity_id": 61, "entity_type": "trip", "process_name": "start_trip", "initial_state": "trip_assigned"}',NULL,'{}',1,'2026-07-24 13:03:43','2026-07-24 13:04:04','2026-07-24 13:04:04');
/*!40000 ALTER TABLE `fsm_sagas` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table `fsm_schedules`
--

DROP TABLE IF EXISTS `fsm_schedules`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `fsm_schedules` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `service_id` varchar(64) NOT NULL,
  `process_name` varchar(128) NOT NULL,
  `entity_type` varchar(128) NOT NULL DEFAULT 'schedule',
  `entity_id` bigint NOT NULL DEFAULT '0',
  `interval_seconds` int NOT NULL,
  `payload_json` json DEFAULT NULL,
  `next_run_at` datetime NOT NULL,
  `status` varchar(32) NOT NULL DEFAULT 'ACTIVE',
  `last_error` text,
  `created_at` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `updated_at` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  KEY `idx_schedules_due` (`status`,`next_run_at`,`id`),
  KEY `idx_schedules_service` (`service_id`,`status`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `fsm_schedules`
--

LOCK TABLES `fsm_schedules` WRITE;
/*!40000 ALTER TABLE `fsm_schedules` DISABLE KEYS */;
/*!40000 ALTER TABLE `fsm_schedules` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table `fsm_timers`
--

DROP TABLE IF EXISTS `fsm_timers`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `fsm_timers` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `service_id` varchar(64) NOT NULL,
  `entity_type` varchar(128) NOT NULL,
  `entity_id` bigint NOT NULL,
  `process_name` varchar(128) NOT NULL,
  `fire_at` datetime NOT NULL,
  `status` varchar(32) NOT NULL DEFAULT 'SCHEDULED',
  `payload_json` json DEFAULT NULL,
  `idempotency_key` varchar(128) DEFAULT NULL,
  `owner` varchar(16) NOT NULL DEFAULT 'domain' COMMENT 'domain|platform — чья политика породила таймер',
  `created_at` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `cancelled_at` datetime DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `uq_timer_idem` (`service_id`,`idempotency_key`),
  KEY `idx_timers_due` (`status`,`fire_at`)
) ENGINE=InnoDB AUTO_INCREMENT=4 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `fsm_timers`
--

LOCK TABLES `fsm_timers` WRITE;
/*!40000 ALTER TABLE `fsm_timers` DISABLE KEYS */;
INSERT INTO `fsm_timers` (`id`,`service_id`,`entity_type`,`entity_id`,`process_name`,`fire_at`,`status`,`payload_json`,`idempotency_key`,`owner`,`created_at`,`cancelled_at`) VALUES
(3,'svc_courier_01','driver_reservations',53,'expire_reservation','2026-07-24 13:53:05','CANCELLED','{"source": "expire_timer", "to_city": "Санкт-Петербург", "from_city": "Москва", "direction_id": 16, "driver_user_id": 1, "executor_user_id": 1}','expire_reservation:53','domain','2026-07-24 13:02:25','2026-07-24 13:02:26');
/*!40000 ALTER TABLE `fsm_timers` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table `fsm_transition_logs`
--

DROP TABLE IF EXISTS `fsm_transition_logs`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `fsm_transition_logs` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `service_id` varchar(64) NOT NULL,
  `entity_type` varchar(128) NOT NULL,
  `entity_id` bigint NOT NULL,
  `from_state` varchar(128) NOT NULL,
  `to_state` varchar(128) NOT NULL,
  `event_name` varchar(128) NOT NULL,
  `transition_id` bigint NOT NULL,
  `instance_id` bigint DEFAULT NULL,
  `user_id` bigint DEFAULT NULL,
  `created_at` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  UNIQUE KEY `uq_log_instance_transition` (`instance_id`,`transition_id`),
  KEY `idx_logs_entity` (`service_id`,`entity_type`,`entity_id`)
) ENGINE=InnoDB AUTO_INCREMENT=341 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `fsm_transition_logs`
--

LOCK TABLES `fsm_transition_logs` WRITE;
/*!40000 ALTER TABLE `fsm_transition_logs` DISABLE KEYS */;
INSERT INTO `fsm_transition_logs` (`id`,`service_id`,`entity_type`,`entity_id`,`from_state`,`to_state`,`event_name`,`transition_id`,`instance_id`,`user_id`,`created_at`) VALUES
(234,'svc_courier_01','locker',70,'locker_free','locker_reserved','locker_reserve_cell',30,157,3,'2026-07-24 13:00:30'),
(235,'svc_courier_01','locker',71,'locker_free','locker_reserved','locker_reserve_cell',30,158,3,'2026-07-24 13:00:34'),
(236,'svc_courier_01','order',1610,'order_created','order_courier1_assigned','assign_executor',167,159,2,'2026-07-24 13:00:39'),
(237,'svc_courier_01','order',1610,'order_courier1_assigned','order_courier_has_parcel','open_cell',38,160,2,'2026-07-24 13:00:47'),
(238,'svc_courier_01','locker',70,'locker_reserved','locker_opened','locker_open_locker',31,160,2,'2026-07-24 13:00:48'),
(239,'svc_courier_01','order',1610,'order_courier_has_parcel','order_parcel_confirmed','close_cell',36,161,2,'2026-07-24 13:00:53'),
(240,'svc_courier_01','locker',70,'locker_opened','locker_occupied','locker_close_locker',126,161,2,'2026-07-24 13:00:55'),
(241,'svc_courier_01','locker',1,'locker_free','locker_reserved','locker_reserve_cell',30,162,11,'2026-07-24 13:01:02'),
(242,'svc_courier_01','locker',52,'locker_free','locker_reserved','locker_reserve_cell',30,163,11,'2026-07-24 13:01:05'),
(243,'svc_courier_01','order',1611,'order_created','order_client_post1','open_cell',136,164,11,'2026-07-24 13:01:12'),
(244,'svc_courier_01','locker',1,'locker_reserved','locker_opened','locker_open_locker',31,164,11,'2026-07-24 13:01:13'),
(245,'svc_courier_01','order',1611,'order_client_post1','order_parcel_confirmed','close_cell',137,165,11,'2026-07-24 13:01:19'),
(246,'svc_courier_01','locker',1,'locker_opened','locker_occupied','locker_close_locker',126,165,11,'2026-07-24 13:01:21'),
(247,'svc_courier_01','locker',64,'locker_free','locker_reserved','locker_reserve_cell',30,166,12,'2026-07-24 13:01:28'),
(248,'svc_courier_01','locker',87,'locker_free','locker_reserved','locker_reserve_cell',30,167,12,'2026-07-24 13:01:31'),
(249,'svc_courier_01','order',1612,'order_created','order_courier1_assigned','assign_executor',167,168,7,'2026-07-24 13:01:37'),
(250,'svc_courier_01','order',1612,'order_courier1_assigned','order_courier_has_parcel','open_cell',38,169,7,'2026-07-24 13:01:44'),
(251,'svc_courier_01','locker',64,'locker_reserved','locker_opened','locker_open_locker',31,169,7,'2026-07-24 13:01:45'),
(252,'svc_courier_01','order',1612,'order_courier_has_parcel','order_parcel_confirmed','close_cell',36,170,7,'2026-07-24 13:01:51'),
(253,'svc_courier_01','locker',64,'locker_opened','locker_occupied','locker_close_locker',126,170,7,'2026-07-24 13:01:54'),
(254,'svc_courier_01','locker',67,'locker_free','locker_reserved','locker_reserve_cell',30,171,13,'2026-07-24 13:02:00'),
(255,'svc_courier_01','locker',90,'locker_free','locker_reserved','locker_reserve_cell',30,172,13,'2026-07-24 13:02:03'),
(256,'svc_courier_01','order',1613,'order_created','order_client_post1','open_cell',136,173,13,'2026-07-24 13:02:11'),
(257,'svc_courier_01','locker',67,'locker_reserved','locker_opened','locker_open_locker',31,173,13,'2026-07-24 13:02:12'),
(258,'svc_courier_01','order',1613,'order_client_post1','order_parcel_confirmed','close_cell',137,174,13,'2026-07-24 13:02:17'),
(259,'svc_courier_01','locker',67,'locker_opened','locker_occupied','locker_close_locker',126,174,13,'2026-07-24 13:02:19'),
(260,'svc_courier_01','driver_reservations',53,'reservation_active','reservation_loading','start_loading',145,175,1,'2026-07-24 13:02:29'),
(261,'svc_courier_01','order',1610,'order_parcel_confirmed','order_parcel_submitted','open_cell',29,176,1,'2026-07-24 13:02:36'),
(262,'svc_courier_01','locker',70,'locker_occupied','locker_opened','locker_open_locker',62,176,1,'2026-07-24 13:02:37'),
(263,'svc_courier_01','order',1610,'order_parcel_submitted','order_picked_up_from_post1','close_cell',74,177,1,'2026-07-24 13:02:42'),
(264,'svc_courier_01','locker',70,'locker_opened','locker_closed_empty','locker_close_pickup',127,177,1,'2026-07-24 13:02:43'),
(265,'svc_courier_01','order',1611,'order_parcel_confirmed','order_parcel_submitted','open_cell',29,178,1,'2026-07-24 13:02:51'),
(266,'svc_courier_01','locker',1,'locker_occupied','locker_opened','locker_open_locker',62,178,1,'2026-07-24 13:02:52'),
(267,'svc_courier_01','order',1611,'order_parcel_submitted','order_picked_up_from_post1','close_cell',74,179,1,'2026-07-24 13:02:57'),
(268,'svc_courier_01','locker',1,'locker_opened','locker_closed_empty','locker_close_pickup',127,179,1,'2026-07-24 13:02:58'),
(269,'svc_courier_01','order',1612,'order_parcel_confirmed','order_parcel_submitted','open_cell',29,180,1,'2026-07-24 13:03:05'),
(270,'svc_courier_01','locker',64,'locker_occupied','locker_opened','locker_open_locker',62,180,1,'2026-07-24 13:03:06'),
(271,'svc_courier_01','order',1612,'order_parcel_submitted','order_picked_up_from_post1','close_cell',74,181,1,'2026-07-24 13:03:14'),
(272,'svc_courier_01','locker',64,'locker_opened','locker_closed_empty','locker_close_pickup',127,181,1,'2026-07-24 13:03:15'),
(273,'svc_courier_01','order',1613,'order_parcel_confirmed','order_parcel_submitted','open_cell',29,182,1,'2026-07-24 13:03:23'),
(274,'svc_courier_01','locker',67,'locker_occupied','locker_opened','locker_open_locker',62,182,1,'2026-07-24 13:03:24'),
(275,'svc_courier_01','order',1613,'order_parcel_submitted','order_picked_up_from_post1','close_cell',74,183,1,'2026-07-24 13:03:29'),
(276,'svc_courier_01','locker',67,'locker_opened','locker_closed_empty','locker_close_pickup',127,183,1,'2026-07-24 13:03:30'),
(277,'svc_courier_01','driver_reservations',53,'reservation_loading','reservation_completed','complete_loading',146,184,1,'2026-07-24 13:03:39'),
(278,'svc_courier_01','order',1610,'order_picked_up_from_post1','order_in_transit_to_post2','start_order_transit',75,185,1,'2026-07-24 13:03:49'),
(279,'svc_courier_01','order',1611,'order_picked_up_from_post1','order_in_transit_to_post2','start_order_transit',75,186,1,'2026-07-24 13:03:54'),
(280,'svc_courier_01','order',1612,'order_picked_up_from_post1','order_in_transit_to_post2','start_order_transit',75,187,1,'2026-07-24 13:03:58'),
(281,'svc_courier_01','order',1613,'order_picked_up_from_post1','order_in_transit_to_post2','start_order_transit',75,188,1,'2026-07-24 13:04:03'),
(282,'svc_courier_01','trip',61,'trip_assigned','trip_in_progress','start_trip',57,189,1,'2026-07-24 13:04:07'),
(283,'svc_courier_01','order',1610,'order_in_transit_to_post2','order_arrived_at_post2','open_cell',76,190,1,'2026-07-24 13:04:14'),
(284,'svc_courier_01','locker',71,'locker_reserved','locker_opened','locker_open_locker',31,190,1,'2026-07-24 13:04:15'),
(285,'svc_courier_01','order',1610,'order_arrived_at_post2','order_parcel_confirmed_post2','close_cell',77,191,1,'2026-07-24 13:04:20'),
(286,'svc_courier_01','locker',71,'locker_opened','locker_occupied','locker_close_locker',126,191,1,'2026-07-24 13:04:21'),
(287,'svc_courier_01','order',1611,'order_in_transit_to_post2','order_arrived_at_post2','open_cell',76,192,1,'2026-07-24 13:04:29'),
(288,'svc_courier_01','locker',52,'locker_reserved','locker_opened','locker_open_locker',31,192,1,'2026-07-24 13:04:29'),
(289,'svc_courier_01','order',1611,'order_arrived_at_post2','order_parcel_confirmed_post2','close_cell',77,193,1,'2026-07-24 13:04:35'),
(290,'svc_courier_01','locker',52,'locker_opened','locker_occupied','locker_close_locker',126,193,1,'2026-07-24 13:04:36'),
(291,'svc_courier_01','order',1612,'order_in_transit_to_post2','order_arrived_at_post2','open_cell',76,194,1,'2026-07-24 13:04:43'),
(292,'svc_courier_01','locker',87,'locker_reserved','locker_opened','locker_open_locker',31,194,1,'2026-07-24 13:04:44'),
(293,'svc_courier_01','order',1612,'order_arrived_at_post2','order_parcel_confirmed_post2','close_cell',77,195,1,'2026-07-24 13:04:49'),
(294,'svc_courier_01','locker',87,'locker_opened','locker_occupied','locker_close_locker',126,195,1,'2026-07-24 13:04:50'),
(295,'svc_courier_01','order',1613,'order_in_transit_to_post2','order_arrived_at_post2','open_cell',76,196,1,'2026-07-24 13:04:57'),
(296,'svc_courier_01','locker',90,'locker_reserved','locker_opened','locker_open_locker',31,196,1,'2026-07-24 13:04:58'),
(297,'svc_courier_01','order',1613,'order_arrived_at_post2','order_parcel_confirmed_post2','close_cell',77,197,1,'2026-07-24 13:05:03'),
(298,'svc_courier_01','locker',90,'locker_opened','locker_occupied','locker_close_locker',126,197,1,'2026-07-24 13:05:04'),
(299,'svc_courier_01','trip',61,'trip_in_progress','trip_completed','complete_trip',135,198,1,'2026-07-24 13:05:12'),
(300,'svc_courier_01','order',1610,'order_parcel_confirmed_post2','order_courier2_assigned','assign_executor',168,199,6,'2026-07-24 13:05:18'),
(301,'svc_courier_01','order',1610,'order_courier2_assigned','order_courier2_has_parcel','open_cell',83,200,6,'2026-07-24 13:05:25'),
(302,'svc_courier_01','locker',71,'locker_occupied','locker_opened','locker_open_locker',62,200,6,'2026-07-24 13:05:26'),
(303,'svc_courier_01','order',1610,'order_courier2_has_parcel','order_courier2_parcel_delivered','close_cell',84,201,6,'2026-07-24 13:05:32'),
(304,'svc_courier_01','locker',71,'locker_opened','locker_closed_empty','locker_close_pickup',127,201,6,'2026-07-24 13:05:33'),
(305,'svc_courier_01','order',1610,'order_courier2_parcel_delivered','order_completed','confirm_courier2_delivery',125,202,6,'2026-07-24 13:05:42'),
(306,'svc_courier_01','order',1611,'order_parcel_confirmed_post2','order_courier2_assigned','assign_executor',168,203,8,'2026-07-24 13:05:48'),
(307,'svc_courier_01','order',1611,'order_courier2_assigned','order_courier2_has_parcel','open_cell',83,204,8,'2026-07-24 13:05:55'),
(308,'svc_courier_01','locker',52,'locker_occupied','locker_opened','locker_open_locker',62,204,8,'2026-07-24 13:05:56'),
(309,'svc_courier_01','order',1611,'order_courier2_has_parcel','order_courier2_parcel_delivered','close_cell',84,205,8,'2026-07-24 13:06:01'),
(310,'svc_courier_01','locker',52,'locker_opened','locker_closed_empty','locker_close_pickup',127,205,8,'2026-07-24 13:06:02'),
(311,'svc_courier_01','order',1611,'order_courier2_parcel_delivered','order_completed','confirm_courier2_delivery',125,206,8,'2026-07-24 13:06:10'),
(312,'svc_courier_01','order',1612,'order_parcel_confirmed_post2','order_delivered_to_client','open_cell',80,207,15,'2026-07-24 13:06:17'),
(313,'svc_courier_01','locker',87,'locker_occupied','locker_opened','locker_open_locker',62,207,15,'2026-07-24 13:06:18'),
(314,'svc_courier_01','order',1612,'order_delivered_to_client','order_completed','close_cell',81,208,15,'2026-07-24 13:06:24'),
(315,'svc_courier_01','locker',87,'locker_opened','locker_closed_empty','locker_close_pickup',127,208,15,'2026-07-24 13:06:25'),
(316,'svc_courier_01','order',1613,'order_parcel_confirmed_post2','order_delivered_to_client','open_cell',80,209,16,'2026-07-24 13:06:32'),
(317,'svc_courier_01','locker',90,'locker_occupied','locker_opened','locker_open_locker',62,209,16,'2026-07-24 13:06:33'),
(318,'svc_courier_01','order',1613,'order_delivered_to_client','order_completed','close_cell',81,210,16,'2026-07-24 13:06:38'),
(319,'svc_courier_01','locker',90,'locker_opened','locker_closed_empty','locker_close_pickup',127,210,16,'2026-07-24 13:06:39'),
(320,'svc_courier_01','locker',46,'locker_free','locker_reserved','locker_reserve_cell',30,211,3,'2026-07-24 16:15:17'),
(321,'svc_courier_01','locker',55,'locker_free','locker_reserved','locker_reserve_cell',30,212,3,'2026-07-24 16:15:20'),
(322,'svc_courier_01','order',1614,'order_created','order_courier1_assigned','assign_executor',167,213,2,'2026-07-24 16:15:26'),
(323,'svc_courier_01','locker',47,'locker_free','locker_reserved','locker_reserve_cell',30,214,3,'2026-07-24 16:25:28'),
(324,'svc_courier_01','locker',56,'locker_free','locker_reserved','locker_reserve_cell',30,215,3,'2026-07-24 16:25:33'),
(325,'svc_courier_01','order',1615,'order_created','order_courier1_assigned','assign_executor',167,216,2,'2026-07-24 16:25:40'),
(326,'svc_courier_01','locker',48,'locker_free','locker_reserved','locker_reserve_cell',30,217,3,'2026-07-26 09:48:49'),
(327,'svc_courier_01','locker',57,'locker_free','locker_reserved','locker_reserve_cell',30,218,3,'2026-07-26 09:48:55'),
(328,'svc_courier_01','order',1616,'order_created','order_courier1_assigned','assign_executor',167,219,2,'2026-07-26 09:49:02'),
(329,'svc_courier_01','locker',65,'locker_free','locker_reserved','locker_reserve_cell',30,220,3,'2026-07-26 11:05:23'),
(330,'svc_courier_01','locker',88,'locker_free','locker_reserved','locker_reserve_cell',30,221,3,'2026-07-26 11:05:32'),
(331,'svc_courier_01','order',1617,'order_created','order_courier1_assigned','assign_executor',167,222,2,'2026-07-26 11:05:41'),
(332,'svc_courier_01','locker',66,'locker_free','locker_reserved','locker_reserve_cell',30,223,3,'2026-07-26 12:36:01'),
(333,'svc_courier_01','locker',89,'locker_free','locker_reserved','locker_reserve_cell',30,224,3,'2026-07-26 12:36:05'),
(334,'svc_courier_01','order',1618,'order_created','order_courier1_assigned','assign_executor',167,225,2,'2026-07-26 12:36:15'),
(335,'svc_courier_01','locker',2,'locker_free','locker_reserved','locker_reserve_cell',30,226,3,'2026-07-26 14:28:24'),
(336,'svc_courier_01','locker',53,'locker_free','locker_reserved','locker_reserve_cell',30,227,3,'2026-07-26 14:28:30'),
(337,'svc_courier_01','order',1619,'order_created','order_courier1_assigned','assign_executor',167,228,2,'2026-07-26 14:28:42'),
(338,'svc_courier_01','locker',3,'locker_free','locker_reserved','locker_reserve_cell',30,229,3,'2026-07-27 09:31:08'),
(339,'svc_courier_01','locker',54,'locker_free','locker_reserved','locker_reserve_cell',30,230,3,'2026-07-27 09:31:14'),
(340,'svc_courier_01','order',1620,'order_created','order_courier1_assigned','assign_executor',167,231,2,'2026-07-27 09:31:27');
/*!40000 ALTER TABLE `fsm_transition_logs` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table `idempotency_keys`
--

DROP TABLE IF EXISTS `idempotency_keys`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `idempotency_keys` (
  `service_id` varchar(64) NOT NULL,
  `scope` varchar(32) NOT NULL,
  `key` varchar(128) NOT NULL,
  `instance_id` bigint DEFAULT NULL,
  `response_json` json DEFAULT NULL,
  `created_at` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `expires_at` datetime DEFAULT NULL,
  PRIMARY KEY (`service_id`,`scope`,`key`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `idempotency_keys`
--

LOCK TABLES `idempotency_keys` WRITE;
/*!40000 ALTER TABLE `idempotency_keys` DISABLE KEYS */;
/*!40000 ALTER TABLE `idempotency_keys` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table `platform_events`
--

DROP TABLE IF EXISTS `platform_events`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `platform_events` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `service_id` varchar(64) NOT NULL,
  `event_type` varchar(128) NOT NULL,
  `instance_id` bigint DEFAULT NULL,
  `entity_type` varchar(128) DEFAULT NULL,
  `entity_id` bigint DEFAULT NULL,
  `payload_json` json DEFAULT NULL,
  `correlation_id` varchar(128) DEFAULT NULL,
  `client_request_id` varchar(128) DEFAULT NULL,
  `created_at` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  KEY `idx_events_service_id` (`service_id`,`id`)
) ENGINE=InnoDB AUTO_INCREMENT=232 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `platform_events`
--

LOCK TABLES `platform_events` WRITE;
/*!40000 ALTER TABLE `platform_events` DISABLE KEYS */;
INSERT INTO `platform_events` (`id`,`service_id`,`event_type`,`instance_id`,`entity_type`,`entity_id`,`payload_json`,`correlation_id`,`client_request_id`,`created_at`) VALUES
(1,'svc_courier_01','fsm.instance.completed',1,'order',1569,'{"effect": {"status": "order_courier1_assigned", "order_id": 1569}, "to_state": "order_courier1_assigned", "event_name": "order_assign_courier1_to_order", "from_state": "order_created", "transition_id": 130}',NULL,NULL,'2026-07-18 17:45:03'),
(2,'svc_courier_01','fsm.instance.completed',2,'order',1570,'{"effect": {"status": "order_courier1_assigned", "order_id": 1570}, "to_state": "order_courier1_assigned", "event_name": "order_assign_courier1_to_order", "from_state": "order_created", "transition_id": 130}',NULL,NULL,'2026-07-18 18:21:48'),
(3,'svc_courier_01','fsm.instance.completed',3,'order',1571,'{"effect": {"status": "order_courier1_assigned", "order_id": 1571}, "to_state": "order_courier1_assigned", "event_name": "order_assign_courier1_to_order", "from_state": "order_created", "transition_id": 130}',NULL,NULL,'2026-07-18 18:22:31'),
(4,'svc_courier_01','fsm.instance.completed',4,'order',1572,'{"effect": {"status": "order_courier1_assigned", "order_id": 1572}, "to_state": "order_courier1_assigned", "event_name": "order_assign_courier1_to_order", "from_state": "order_created", "transition_id": 130}',NULL,NULL,'2026-07-21 10:28:28'),
(5,'svc_courier_01','fsm.instance.completed',5,'order',1574,'{"effect": {"status": "order_courier1_assigned", "order_id": 1574, "courier_user_id": 2}, "to_state": "order_courier1_assigned", "event_name": "order_assign_courier1_to_order", "from_state": "order_created", "transition_id": 130}',NULL,NULL,'2026-07-21 14:32:45'),
(6,'svc_courier_01','fsm.instance.completed',6,'order',1575,'{"effect": {"leg": "pickup", "status": "order_courier1_assigned", "order_id": 1575, "executor_user_id": 2}, "to_state": "order_courier1_assigned", "event_name": "assign_executor", "from_state": "order_created", "transition_id": 167}',NULL,NULL,'2026-07-21 19:18:33'),
(7,'svc_courier_01','fsm.instance.failed',7,'order',1575,'{"last_error": "UNKNOWN_PROCESS: svc_courier_01/open_cell"}',NULL,NULL,'2026-07-22 11:39:19'),
(8,'svc_courier_01','fsm.instance.completed',8,'order',1575,'{"effect": {"leg": "pickup", "status": "order_courier_has_parcel", "cell_id": 46, "order_id": 1575}, "to_state": "order_courier_has_parcel", "entity_id": 1575, "companions": [{"index": 0, "effect": {"cell_id": 46, "cell_status": "locker_opened"}, "to_state": "locker_opened", "entity_id": 46, "event_name": "locker_open_locker", "from_state": "locker_reserved", "entity_type": "locker", "transition_id": 31}], "event_name": "open_cell", "from_state": "order_courier1_assigned", "entity_type": "order", "transition_id": 38}',NULL,NULL,'2026-07-22 11:45:49'),
(9,'svc_courier_01','fsm.instance.completed',9,'order',1575,'{"effect": {"leg": "pickup", "status": "order_parcel_confirmed", "cell_id": 46, "order_id": 1575}, "to_state": "order_parcel_confirmed", "entity_id": 1575, "companions": [{"index": 0, "effect": {"cell_id": 46, "cell_status": "locker_occupied"}, "to_state": "locker_occupied", "entity_id": 46, "event_name": "locker_close_locker", "from_state": "locker_opened", "entity_type": "locker", "transition_id": 126}], "event_name": "close_cell", "from_state": "order_courier_has_parcel", "entity_type": "order", "transition_id": 36}',NULL,NULL,'2026-07-22 12:50:43'),
(10,'svc_courier_01','fsm.instance.failed',10,'order',1577,'{"last_error": "NO_GUARD_MATCHED: order/order_created/open_cell (ACTOR_CITY_REQUIRED)"}',NULL,NULL,'2026-07-22 13:57:12'),
(11,'svc_courier_01','fsm.instance.completed',11,'order',1577,'{"effect": {"leg": "pickup", "status": "order_client_post1", "cell_id": 50, "order_id": 1577}, "to_state": "order_client_post1", "entity_id": 1577, "companions": [{"index": 0, "effect": {"cell_id": 50, "cell_status": "locker_opened"}, "to_state": "locker_opened", "entity_id": 50, "event_name": "locker_open_locker", "from_state": "locker_reserved", "entity_type": "locker", "transition_id": 31}], "event_name": "open_cell", "from_state": "order_created", "entity_type": "order", "transition_id": 136}',NULL,NULL,'2026-07-22 14:01:50'),
(12,'svc_courier_01','fsm.instance.completed',12,'order',1577,'{"effect": {"leg": "pickup", "status": "order_parcel_confirmed", "cell_id": 50, "order_id": 1577, "direction_id": 3}, "to_state": "order_parcel_confirmed", "entity_id": 1577, "companions": [{"index": 0, "effect": {"cell_id": 50, "cell_status": "locker_occupied"}, "to_state": "locker_occupied", "entity_id": 50, "event_name": "locker_close_locker", "from_state": "locker_opened", "entity_type": "locker", "transition_id": 126}], "event_name": "close_cell", "from_state": "order_client_post1", "entity_type": "order", "transition_id": 137}',NULL,NULL,'2026-07-22 14:03:56'),
(13,'svc_courier_01','fsm.instance.completed',13,'order',1578,'{"effect": {"leg": "pickup", "status": "order_client_post1", "cell_id": 48, "order_id": 1578}, "to_state": "order_client_post1", "entity_id": 1578, "companions": [{"index": 0, "effect": {"cell_id": 48, "cell_status": "locker_opened"}, "to_state": "locker_opened", "entity_id": 48, "event_name": "locker_open_locker", "from_state": "locker_reserved", "entity_type": "locker", "transition_id": 31}], "event_name": "open_cell", "from_state": "order_created", "entity_type": "order", "transition_id": 136}',NULL,NULL,'2026-07-22 16:51:54'),
(14,'svc_courier_01','fsm.instance.completed',14,'order',1578,'{"effect": {"leg": "pickup", "status": "order_parcel_confirmed", "cell_id": 48, "order_id": 1578, "direction_id": 3}, "to_state": "order_parcel_confirmed", "entity_id": 1578, "companions": [{"index": 0, "effect": {"cell_id": 48, "cell_status": "locker_occupied"}, "to_state": "locker_occupied", "entity_id": 48, "event_name": "locker_close_locker", "from_state": "locker_opened", "entity_type": "locker", "transition_id": 126}], "event_name": "close_cell", "from_state": "order_client_post1", "entity_type": "order", "transition_id": 137}',NULL,NULL,'2026-07-22 16:52:00'),
(15,'svc_courier_01','fsm.instance.completed',15,'driver_reservations',45,'{"effect": {"status": "reservation_loading", "direction_id": 3, "reservation_id": 45}, "to_state": "reservation_loading", "entity_id": 45, "companions": [], "event_name": "start_loading", "from_state": "reservation_active", "entity_type": "driver_reservations", "transition_id": 145}',NULL,NULL,'2026-07-22 16:52:06'),
(16,'svc_courier_01','fsm.instance.completed',16,'order',1578,'{"effect": {"leg": "pickup", "status": "order_parcel_submitted", "cell_id": 48, "order_id": 1578}, "to_state": "order_parcel_submitted", "entity_id": 1578, "companions": [{"index": 0, "effect": {"cell_id": 48, "cell_status": "locker_opened"}, "to_state": "locker_opened", "entity_id": 48, "event_name": "locker_open_locker", "from_state": "locker_occupied", "entity_type": "locker", "transition_id": 62}], "event_name": "open_cell", "from_state": "order_parcel_confirmed", "entity_type": "order", "transition_id": 29}',NULL,NULL,'2026-07-22 16:52:13'),
(17,'svc_courier_01','fsm.instance.completed',17,'order',1578,'{"effect": {"leg": "pickup", "status": "order_picked_up_from_post1", "cell_id": 48, "order_id": 1578}, "to_state": "order_picked_up_from_post1", "entity_id": 1578, "companions": [{"index": 0, "effect": {"cell_id": 48, "cell_status": "locker_closed_empty"}, "to_state": "locker_closed_empty", "entity_id": 48, "event_name": "locker_close_pickup", "from_state": "locker_opened", "entity_type": "locker", "transition_id": 127}], "event_name": "close_cell", "from_state": "order_parcel_submitted", "entity_type": "order", "transition_id": 74}',NULL,NULL,'2026-07-22 16:52:18'),
(18,'svc_courier_01','fsm.instance.completed',18,'driver_reservations',45,'{"effect": {"status": "reservation_completed", "direction_id": 3, "reservation_id": 45}, "to_state": "reservation_completed", "entity_id": 45, "companions": [], "event_name": "complete_loading", "from_state": "reservation_loading", "entity_type": "driver_reservations", "transition_id": 146}',NULL,NULL,'2026-07-22 16:52:24'),
(19,'svc_courier_01','fsm.instance.completed',19,'order',1579,'{"effect": {"leg": "pickup", "status": "order_client_post1", "cell_id": 46, "order_id": 1579}, "to_state": "order_client_post1", "entity_id": 1579, "companions": [{"index": 0, "effect": {"cell_id": 46, "cell_status": "locker_opened"}, "to_state": "locker_opened", "entity_id": 46, "event_name": "locker_open_locker", "from_state": "locker_occupied", "entity_type": "locker", "transition_id": 62}], "event_name": "open_cell", "from_state": "order_created", "entity_type": "order", "transition_id": 136}',NULL,NULL,'2026-07-22 17:31:31'),
(20,'svc_courier_01','fsm.instance.completed',20,'order',1579,'{"effect": {"leg": "pickup", "status": "order_parcel_confirmed", "cell_id": 46, "order_id": 1579, "direction_id": 3}, "to_state": "order_parcel_confirmed", "entity_id": 1579, "companions": [{"index": 0, "effect": {"cell_id": 46, "cell_status": "locker_occupied"}, "to_state": "locker_occupied", "entity_id": 46, "event_name": "locker_close_locker", "from_state": "locker_opened", "entity_type": "locker", "transition_id": 126}], "event_name": "close_cell", "from_state": "order_client_post1", "entity_type": "order", "transition_id": 137}',NULL,NULL,'2026-07-22 17:31:39'),
(21,'svc_courier_01','fsm.instance.completed',21,'order',1580,'{"effect": {"leg": "pickup", "status": "order_client_post1", "cell_id": 47, "order_id": 1580}, "to_state": "order_client_post1", "entity_id": 1580, "companions": [{"index": 0, "effect": {"cell_id": 47, "cell_status": "locker_opened"}, "to_state": "locker_opened", "entity_id": 47, "event_name": "locker_open_locker", "from_state": "locker_reserved", "entity_type": "locker", "transition_id": 31}], "event_name": "open_cell", "from_state": "order_created", "entity_type": "order", "transition_id": 136}',NULL,NULL,'2026-07-22 17:31:49'),
(22,'svc_courier_01','fsm.instance.completed',22,'order',1580,'{"effect": {"leg": "pickup", "status": "order_parcel_confirmed", "cell_id": 47, "order_id": 1580, "direction_id": 3}, "to_state": "order_parcel_confirmed", "entity_id": 1580, "companions": [{"index": 0, "effect": {"cell_id": 47, "cell_status": "locker_occupied"}, "to_state": "locker_occupied", "entity_id": 47, "event_name": "locker_close_locker", "from_state": "locker_opened", "entity_type": "locker", "transition_id": 126}], "event_name": "close_cell", "from_state": "order_client_post1", "entity_type": "order", "transition_id": 137}',NULL,NULL,'2026-07-22 17:31:57'),
(23,'svc_courier_01','fsm.instance.failed',23,'order',1581,'{"last_error": "COMPANION_FAILED: index=0 locker/48/locker_open_locker: NO_CANDIDATE_TRANSITIONS: locker/locker_closed_empty/locker_open_locker"}',NULL,NULL,'2026-07-22 17:32:07'),
(24,'svc_courier_01','fsm.instance.completed',24,'order',1582,'{"effect": {"leg": "pickup", "status": "order_client_post1", "cell_id": 1, "order_id": 1582}, "to_state": "order_client_post1", "entity_id": 1582, "companions": [{"index": 0, "effect": {"cell_id": 1, "cell_status": "locker_opened"}, "to_state": "locker_opened", "entity_id": 1, "event_name": "locker_open_locker", "from_state": "locker_reserved", "entity_type": "locker", "transition_id": 31}], "event_name": "open_cell", "from_state": "order_created", "entity_type": "order", "transition_id": 136}',NULL,NULL,'2026-07-22 17:50:46'),
(25,'svc_courier_01','fsm.instance.completed',25,'order',1582,'{"effect": {"leg": "pickup", "status": "order_parcel_confirmed", "cell_id": 1, "order_id": 1582, "direction_id": 3}, "to_state": "order_parcel_confirmed", "entity_id": 1582, "companions": [{"index": 0, "effect": {"cell_id": 1, "cell_status": "locker_occupied"}, "to_state": "locker_occupied", "entity_id": 1, "event_name": "locker_close_locker", "from_state": "locker_opened", "entity_type": "locker", "transition_id": 126}], "event_name": "close_cell", "from_state": "order_client_post1", "entity_type": "order", "transition_id": 137}',NULL,NULL,'2026-07-22 17:50:53'),
(26,'svc_courier_01','fsm.instance.failed',26,'order',1583,'{"last_error": "CONTEXT_BUILD_FAILED: (mysql.connector.errors.ProgrammingError) 1226 (42000): User \'uz0bg7qrzcdoq1kn\' has exceeded the \'max_user_connections\' resource (current value: 5)\\n(Background on this error at: https://sqlalche.me/e/20/f405)"}',NULL,NULL,'2026-07-22 17:59:54'),
(27,'svc_courier_01','fsm.instance.completed',27,'order',1584,'{"effect": {"leg": "pickup", "status": "order_client_post1", "cell_id": 2, "order_id": 1584}, "to_state": "order_client_post1", "entity_id": 1584, "companions": [{"index": 0, "effect": {"cell_id": 2, "cell_status": "locker_opened"}, "to_state": "locker_opened", "entity_id": 2, "event_name": "locker_open_locker", "from_state": "locker_reserved", "entity_type": "locker", "transition_id": 31}], "event_name": "open_cell", "from_state": "order_created", "entity_type": "order", "transition_id": 136}',NULL,NULL,'2026-07-23 07:41:23'),
(28,'svc_courier_01','fsm.instance.completed',28,'order',1584,'{"effect": {"leg": "pickup", "status": "order_parcel_confirmed", "cell_id": 2, "order_id": 1584, "direction_id": 3}, "to_state": "order_parcel_confirmed", "entity_id": 1584, "companions": [{"index": 0, "effect": {"cell_id": 2, "cell_status": "locker_occupied"}, "to_state": "locker_occupied", "entity_id": 2, "event_name": "locker_close_locker", "from_state": "locker_opened", "entity_type": "locker", "transition_id": 126}], "event_name": "close_cell", "from_state": "order_client_post1", "entity_type": "order", "transition_id": 137}',NULL,NULL,'2026-07-23 07:41:31'),
(29,'svc_courier_01','fsm.instance.failed',29,'order',1585,'{"last_error": "COMPANION_FAILED: index=0 locker/46/locker_open_locker: NO_CANDIDATE_TRANSITIONS: locker/locker_free/locker_open_locker"}',NULL,NULL,'2026-07-23 07:41:41'),
(30,'svc_courier_01','fsm.instance.completed',30,'locker',3,'{"effect": {"cell_id": 3, "order_id": 1586, "cell_status": "locker_reserved"}, "to_state": "locker_reserved", "entity_id": 3, "companions": [], "event_name": "locker_reserve_cell", "from_state": "locker_free", "entity_type": "locker", "transition_id": 30}',NULL,NULL,'2026-07-23 09:08:08'),
(31,'svc_courier_01','fsm.instance.completed',31,'locker',54,'{"effect": {"cell_id": 54, "order_id": 1586, "cell_status": "locker_reserved"}, "to_state": "locker_reserved", "entity_id": 54, "companions": [], "event_name": "locker_reserve_cell", "from_state": "locker_free", "entity_type": "locker", "transition_id": 30}',NULL,NULL,'2026-07-23 09:08:11'),
(32,'svc_courier_01','fsm.instance.completed',32,'order',1586,'{"effect": {"leg": "pickup", "status": "order_client_post1", "cell_id": 3, "order_id": 1586}, "to_state": "order_client_post1", "entity_id": 1586, "companions": [{"index": 0, "effect": {"cell_id": 3, "cell_status": "locker_opened"}, "to_state": "locker_opened", "entity_id": 3, "event_name": "locker_open_locker", "from_state": "locker_reserved", "entity_type": "locker", "transition_id": 31}], "event_name": "open_cell", "from_state": "order_created", "entity_type": "order", "transition_id": 136}',NULL,NULL,'2026-07-23 09:08:19'),
(33,'svc_courier_01','fsm.instance.completed',33,'order',1586,'{"effect": {"leg": "pickup", "status": "order_parcel_confirmed", "cell_id": 3, "order_id": 1586, "direction_id": 3}, "to_state": "order_parcel_confirmed", "entity_id": 1586, "companions": [{"index": 0, "effect": {"cell_id": 3, "cell_status": "locker_occupied"}, "to_state": "locker_occupied", "entity_id": 3, "event_name": "locker_close_locker", "from_state": "locker_opened", "entity_type": "locker", "transition_id": 126}], "event_name": "close_cell", "from_state": "order_client_post1", "entity_type": "order", "transition_id": 137}',NULL,NULL,'2026-07-23 09:08:28'),
(34,'svc_courier_01','fsm.instance.completed',34,'locker',47,'{"effect": {"cell_id": 47, "order_id": 1587, "cell_status": "locker_reserved"}, "to_state": "locker_reserved", "entity_id": 47, "companions": [], "event_name": "locker_reserve_cell", "from_state": "locker_free", "entity_type": "locker", "transition_id": 30}',NULL,NULL,'2026-07-23 09:08:35'),
(35,'svc_courier_01','fsm.instance.completed',35,'locker',56,'{"effect": {"cell_id": 56, "order_id": 1587, "cell_status": "locker_reserved"}, "to_state": "locker_reserved", "entity_id": 56, "companions": [], "event_name": "locker_reserve_cell", "from_state": "locker_free", "entity_type": "locker", "transition_id": 30}',NULL,NULL,'2026-07-23 09:08:37'),
(36,'svc_courier_01','fsm.instance.completed',36,'order',1587,'{"effect": {"leg": "pickup", "status": "order_client_post1", "cell_id": 47, "order_id": 1587}, "to_state": "order_client_post1", "entity_id": 1587, "companions": [{"index": 0, "effect": {"cell_id": 47, "cell_status": "locker_opened"}, "to_state": "locker_opened", "entity_id": 47, "event_name": "locker_open_locker", "from_state": "locker_reserved", "entity_type": "locker", "transition_id": 31}], "event_name": "open_cell", "from_state": "order_created", "entity_type": "order", "transition_id": 136}',NULL,NULL,'2026-07-23 09:08:46'),
(37,'svc_courier_01','fsm.instance.completed',37,'order',1587,'{"effect": {"leg": "pickup", "status": "order_parcel_confirmed", "cell_id": 47, "order_id": 1587, "direction_id": 3}, "to_state": "order_parcel_confirmed", "entity_id": 1587, "companions": [{"index": 0, "effect": {"cell_id": 47, "cell_status": "locker_occupied"}, "to_state": "locker_occupied", "entity_id": 47, "event_name": "locker_close_locker", "from_state": "locker_opened", "entity_type": "locker", "transition_id": 126}], "event_name": "close_cell", "from_state": "order_client_post1", "entity_type": "order", "transition_id": 137}',NULL,NULL,'2026-07-23 09:08:52'),
(38,'svc_courier_01','fsm.instance.completed',38,'locker',49,'{"effect": {"cell_id": 49, "order_id": 1588, "cell_status": "locker_reserved"}, "to_state": "locker_reserved", "entity_id": 49, "companions": [], "event_name": "locker_reserve_cell", "from_state": "locker_free", "entity_type": "locker", "transition_id": 30}',NULL,NULL,'2026-07-23 09:08:59'),
(39,'svc_courier_01','fsm.instance.completed',39,'locker',58,'{"effect": {"cell_id": 58, "order_id": 1588, "cell_status": "locker_reserved"}, "to_state": "locker_reserved", "entity_id": 58, "companions": [], "event_name": "locker_reserve_cell", "from_state": "locker_free", "entity_type": "locker", "transition_id": 30}',NULL,NULL,'2026-07-23 09:09:01'),
(40,'svc_courier_01','fsm.instance.completed',40,'order',1588,'{"effect": {"leg": "pickup", "status": "order_client_post1", "cell_id": 49, "order_id": 1588}, "to_state": "order_client_post1", "entity_id": 1588, "companions": [{"index": 0, "effect": {"cell_id": 49, "cell_status": "locker_opened"}, "to_state": "locker_opened", "entity_id": 49, "event_name": "locker_open_locker", "from_state": "locker_reserved", "entity_type": "locker", "transition_id": 31}], "event_name": "open_cell", "from_state": "order_created", "entity_type": "order", "transition_id": 136}',NULL,NULL,'2026-07-23 09:09:09'),
(41,'svc_courier_01','fsm.instance.completed',41,'order',1588,'{"effect": {"leg": "pickup", "status": "order_parcel_confirmed", "cell_id": 49, "order_id": 1588, "direction_id": 3}, "to_state": "order_parcel_confirmed", "entity_id": 1588, "companions": [{"index": 0, "effect": {"cell_id": 49, "cell_status": "locker_occupied"}, "to_state": "locker_occupied", "entity_id": 49, "event_name": "locker_close_locker", "from_state": "locker_opened", "entity_type": "locker", "transition_id": 126}], "event_name": "close_cell", "from_state": "order_client_post1", "entity_type": "order", "transition_id": 137}',NULL,NULL,'2026-07-23 09:09:17'),
(42,'svc_courier_01','fsm.instance.completed',42,'driver_reservations',46,'{"effect": {"status": "reservation_loading", "direction_id": 3, "reservation_id": 46}, "to_state": "reservation_loading", "entity_id": 46, "companions": [], "event_name": "start_loading", "from_state": "reservation_active", "entity_type": "driver_reservations", "transition_id": 145}',NULL,NULL,'2026-07-23 09:09:23'),
(43,'svc_courier_01','fsm.instance.completed',43,'locker',1,'{"effect": {"cell_id": 1, "order_id": 1590, "cell_status": "locker_reserved"}, "to_state": "locker_reserved", "entity_id": 1, "companions": [], "event_name": "locker_reserve_cell", "from_state": "locker_free", "entity_type": "locker", "transition_id": 30}',NULL,NULL,'2026-07-23 14:40:11'),
(44,'svc_courier_01','fsm.instance.completed',44,'locker',52,'{"effect": {"cell_id": 52, "order_id": 1590, "cell_status": "locker_reserved"}, "to_state": "locker_reserved", "entity_id": 52, "companions": [], "event_name": "locker_reserve_cell", "from_state": "locker_free", "entity_type": "locker", "transition_id": 30}',NULL,NULL,'2026-07-23 14:40:14'),
(45,'svc_courier_01','fsm.instance.completed',45,'order',1590,'{"effect": {"leg": "pickup", "status": "order_client_post1", "cell_id": 1, "order_id": 1590}, "to_state": "order_client_post1", "entity_id": 1590, "companions": [{"index": 0, "effect": {"cell_id": 1, "cell_status": "locker_opened"}, "to_state": "locker_opened", "entity_id": 1, "event_name": "locker_open_locker", "from_state": "locker_reserved", "entity_type": "locker", "transition_id": 31}], "event_name": "open_cell", "from_state": "order_created", "entity_type": "order", "transition_id": 136}',NULL,NULL,'2026-07-23 14:40:22'),
(46,'svc_courier_01','fsm.instance.completed',46,'order',1590,'{"effect": {"leg": "pickup", "status": "order_parcel_confirmed", "cell_id": 1, "order_id": 1590, "direction_id": 9}, "to_state": "order_parcel_confirmed", "entity_id": 1590, "companions": [{"index": 0, "effect": {"cell_id": 1, "cell_status": "locker_occupied"}, "to_state": "locker_occupied", "entity_id": 1, "event_name": "locker_close_locker", "from_state": "locker_opened", "entity_type": "locker", "transition_id": 126}], "event_name": "close_cell", "from_state": "order_client_post1", "entity_type": "order", "transition_id": 137}',NULL,NULL,'2026-07-23 14:40:30'),
(47,'svc_courier_01','fsm.instance.completed',47,'locker',46,'{"effect": {"cell_id": 46, "order_id": 1591, "cell_status": "locker_reserved"}, "to_state": "locker_reserved", "entity_id": 46, "companions": [], "event_name": "locker_reserve_cell", "from_state": "locker_free", "entity_type": "locker", "transition_id": 30}',NULL,NULL,'2026-07-23 14:40:37'),
(48,'svc_courier_01','fsm.instance.completed',48,'locker',55,'{"effect": {"cell_id": 55, "order_id": 1591, "cell_status": "locker_reserved"}, "to_state": "locker_reserved", "entity_id": 55, "companions": [], "event_name": "locker_reserve_cell", "from_state": "locker_free", "entity_type": "locker", "transition_id": 30}',NULL,NULL,'2026-07-23 14:40:39'),
(49,'svc_courier_01','fsm.instance.completed',49,'order',1591,'{"effect": {"leg": "pickup", "status": "order_client_post1", "cell_id": 46, "order_id": 1591}, "to_state": "order_client_post1", "entity_id": 1591, "companions": [{"index": 0, "effect": {"cell_id": 46, "cell_status": "locker_opened"}, "to_state": "locker_opened", "entity_id": 46, "event_name": "locker_open_locker", "from_state": "locker_reserved", "entity_type": "locker", "transition_id": 31}], "event_name": "open_cell", "from_state": "order_created", "entity_type": "order", "transition_id": 136}',NULL,NULL,'2026-07-23 14:40:47'),
(50,'svc_courier_01','fsm.instance.completed',50,'order',1591,'{"effect": {"leg": "pickup", "status": "order_parcel_confirmed", "cell_id": 46, "order_id": 1591, "direction_id": 9}, "to_state": "order_parcel_confirmed", "entity_id": 1591, "companions": [{"index": 0, "effect": {"cell_id": 46, "cell_status": "locker_occupied"}, "to_state": "locker_occupied", "entity_id": 46, "event_name": "locker_close_locker", "from_state": "locker_opened", "entity_type": "locker", "transition_id": 126}], "event_name": "close_cell", "from_state": "order_client_post1", "entity_type": "order", "transition_id": 137}',NULL,NULL,'2026-07-23 14:40:55'),
(51,'svc_courier_01','fsm.instance.completed',51,'locker',49,'{"effect": {"cell_id": 49, "order_id": 1592, "cell_status": "locker_reserved"}, "to_state": "locker_reserved", "entity_id": 49, "companions": [], "event_name": "locker_reserve_cell", "from_state": "locker_free", "entity_type": "locker", "transition_id": 30}',NULL,NULL,'2026-07-23 14:41:02'),
(52,'svc_courier_01','fsm.instance.completed',52,'locker',58,'{"effect": {"cell_id": 58, "order_id": 1592, "cell_status": "locker_reserved"}, "to_state": "locker_reserved", "entity_id": 58, "companions": [], "event_name": "locker_reserve_cell", "from_state": "locker_free", "entity_type": "locker", "transition_id": 30}',NULL,NULL,'2026-07-23 14:41:04'),
(53,'svc_courier_01','fsm.instance.completed',53,'order',1592,'{"effect": {"leg": "pickup", "status": "order_client_post1", "cell_id": 49, "order_id": 1592}, "to_state": "order_client_post1", "entity_id": 1592, "companions": [{"index": 0, "effect": {"cell_id": 49, "cell_status": "locker_opened"}, "to_state": "locker_opened", "entity_id": 49, "event_name": "locker_open_locker", "from_state": "locker_reserved", "entity_type": "locker", "transition_id": 31}], "event_name": "open_cell", "from_state": "order_created", "entity_type": "order", "transition_id": 136}',NULL,NULL,'2026-07-23 14:41:12'),
(54,'svc_courier_01','fsm.instance.completed',54,'order',1592,'{"effect": {"leg": "pickup", "status": "order_parcel_confirmed", "cell_id": 49, "order_id": 1592, "direction_id": 9}, "to_state": "order_parcel_confirmed", "entity_id": 1592, "companions": [{"index": 0, "effect": {"cell_id": 49, "cell_status": "locker_occupied"}, "to_state": "locker_occupied", "entity_id": 49, "event_name": "locker_close_locker", "from_state": "locker_opened", "entity_type": "locker", "transition_id": 126}], "event_name": "close_cell", "from_state": "order_client_post1", "entity_type": "order", "transition_id": 137}',NULL,NULL,'2026-07-23 14:41:21'),
(55,'svc_courier_01','fsm.instance.completed',55,'driver_reservations',47,'{"effect": {"status": "reservation_loading", "direction_id": 9, "reservation_id": 47}, "to_state": "reservation_loading", "entity_id": 47, "companions": [], "event_name": "start_loading", "from_state": "reservation_active", "entity_type": "driver_reservations", "transition_id": 145}',NULL,NULL,'2026-07-23 14:43:58'),
(56,'svc_courier_01','fsm.instance.completed',56,'order',1590,'{"effect": {"leg": "pickup", "status": "order_parcel_submitted", "cell_id": 1, "order_id": 1590}, "to_state": "order_parcel_submitted", "entity_id": 1590, "companions": [{"index": 0, "effect": {"cell_id": 1, "cell_status": "locker_opened"}, "to_state": "locker_opened", "entity_id": 1, "event_name": "locker_open_locker", "from_state": "locker_occupied", "entity_type": "locker", "transition_id": 62}], "event_name": "open_cell", "from_state": "order_parcel_confirmed", "entity_type": "order", "transition_id": 29}',NULL,NULL,'2026-07-23 14:44:06'),
(57,'svc_courier_01','fsm.instance.completed',57,'order',1590,'{"effect": {"leg": "pickup", "status": "order_picked_up_from_post1", "cell_id": 1, "order_id": 1590}, "to_state": "order_picked_up_from_post1", "entity_id": 1590, "companions": [{"index": 0, "effect": {"cell_id": 1, "cell_status": "locker_closed_empty"}, "to_state": "locker_closed_empty", "entity_id": 1, "event_name": "locker_close_pickup", "from_state": "locker_opened", "entity_type": "locker", "transition_id": 127}], "event_name": "close_cell", "from_state": "order_parcel_submitted", "entity_type": "order", "transition_id": 74}',NULL,NULL,'2026-07-23 14:44:13'),
(58,'svc_courier_01','fsm.instance.completed',58,'order',1591,'{"effect": {"leg": "pickup", "status": "order_parcel_submitted", "cell_id": 46, "order_id": 1591}, "to_state": "order_parcel_submitted", "entity_id": 1591, "companions": [{"index": 0, "effect": {"cell_id": 46, "cell_status": "locker_opened"}, "to_state": "locker_opened", "entity_id": 46, "event_name": "locker_open_locker", "from_state": "locker_occupied", "entity_type": "locker", "transition_id": 62}], "event_name": "open_cell", "from_state": "order_parcel_confirmed", "entity_type": "order", "transition_id": 29}',NULL,NULL,'2026-07-23 14:44:21'),
(59,'svc_courier_01','fsm.instance.completed',59,'order',1591,'{"effect": {"leg": "pickup", "status": "order_picked_up_from_post1", "cell_id": 46, "order_id": 1591}, "to_state": "order_picked_up_from_post1", "entity_id": 1591, "companions": [{"index": 0, "effect": {"cell_id": 46, "cell_status": "locker_closed_empty"}, "to_state": "locker_closed_empty", "entity_id": 46, "event_name": "locker_close_pickup", "from_state": "locker_opened", "entity_type": "locker", "transition_id": 127}], "event_name": "close_cell", "from_state": "order_parcel_submitted", "entity_type": "order", "transition_id": 74}',NULL,NULL,'2026-07-23 14:44:28'),
(60,'svc_courier_01','fsm.instance.completed',60,'order',1592,'{"effect": {"leg": "pickup", "status": "order_parcel_submitted", "cell_id": 49, "order_id": 1592}, "to_state": "order_parcel_submitted", "entity_id": 1592, "companions": [{"index": 0, "effect": {"cell_id": 49, "cell_status": "locker_opened"}, "to_state": "locker_opened", "entity_id": 49, "event_name": "locker_open_locker", "from_state": "locker_occupied", "entity_type": "locker", "transition_id": 62}], "event_name": "open_cell", "from_state": "order_parcel_confirmed", "entity_type": "order", "transition_id": 29}',NULL,NULL,'2026-07-23 14:44:36'),
(61,'svc_courier_01','fsm.instance.completed',61,'order',1592,'{"effect": {"leg": "pickup", "status": "order_picked_up_from_post1", "cell_id": 49, "order_id": 1592}, "to_state": "order_picked_up_from_post1", "entity_id": 1592, "companions": [{"index": 0, "effect": {"cell_id": 49, "cell_status": "locker_closed_empty"}, "to_state": "locker_closed_empty", "entity_id": 49, "event_name": "locker_close_pickup", "from_state": "locker_opened", "entity_type": "locker", "transition_id": 127}], "event_name": "close_cell", "from_state": "order_parcel_submitted", "entity_type": "order", "transition_id": 74}',NULL,NULL,'2026-07-23 14:44:43'),
(62,'svc_courier_01','fsm.instance.completed',62,'driver_reservations',47,'{"effect": {"status": "reservation_completed", "direction_id": 9, "reservation_id": 47}, "to_state": "reservation_completed", "entity_id": 47, "companions": [], "event_name": "complete_loading", "from_state": "reservation_loading", "entity_type": "driver_reservations", "transition_id": 146}',NULL,NULL,'2026-07-23 14:44:49'),
(63,'svc_courier_01','fsm.instance.completed',63,'locker',2,'{"effect": {"cell_id": 2, "order_id": 1593, "cell_status": "locker_reserved"}, "to_state": "locker_reserved", "entity_id": 2, "companions": [], "event_name": "locker_reserve_cell", "from_state": "locker_free", "entity_type": "locker", "transition_id": 30}',NULL,NULL,'2026-07-23 15:34:22'),
(64,'svc_courier_01','fsm.instance.completed',64,'locker',53,'{"effect": {"cell_id": 53, "order_id": 1593, "cell_status": "locker_reserved"}, "to_state": "locker_reserved", "entity_id": 53, "companions": [], "event_name": "locker_reserve_cell", "from_state": "locker_free", "entity_type": "locker", "transition_id": 30}',NULL,NULL,'2026-07-23 15:34:24'),
(65,'svc_courier_01','fsm.instance.completed',65,'order',1593,'{"effect": {"leg": "pickup", "status": "order_client_post1", "cell_id": 2, "order_id": 1593}, "to_state": "order_client_post1", "entity_id": 1593, "companions": [{"index": 0, "effect": {"cell_id": 2, "cell_status": "locker_opened"}, "to_state": "locker_opened", "entity_id": 2, "event_name": "locker_open_locker", "from_state": "locker_reserved", "entity_type": "locker", "transition_id": 31}], "event_name": "open_cell", "from_state": "order_created", "entity_type": "order", "transition_id": 136}',NULL,NULL,'2026-07-23 15:34:33'),
(66,'svc_courier_01','fsm.instance.completed',66,'order',1593,'{"effect": {"leg": "pickup", "status": "order_parcel_confirmed", "cell_id": 2, "order_id": 1593, "direction_id": 9}, "to_state": "order_parcel_confirmed", "entity_id": 1593, "companions": [{"index": 0, "effect": {"cell_id": 2, "cell_status": "locker_occupied"}, "to_state": "locker_occupied", "entity_id": 2, "event_name": "locker_close_locker", "from_state": "locker_opened", "entity_type": "locker", "transition_id": 126}], "event_name": "close_cell", "from_state": "order_client_post1", "entity_type": "order", "transition_id": 137}',NULL,NULL,'2026-07-23 15:34:41'),
(67,'svc_courier_01','fsm.instance.completed',67,'locker',47,'{"effect": {"cell_id": 47, "order_id": 1594, "cell_status": "locker_reserved"}, "to_state": "locker_reserved", "entity_id": 47, "companions": [], "event_name": "locker_reserve_cell", "from_state": "locker_free", "entity_type": "locker", "transition_id": 30}',NULL,NULL,'2026-07-23 15:34:48'),
(68,'svc_courier_01','fsm.instance.completed',68,'locker',56,'{"effect": {"cell_id": 56, "order_id": 1594, "cell_status": "locker_reserved"}, "to_state": "locker_reserved", "entity_id": 56, "companions": [], "event_name": "locker_reserve_cell", "from_state": "locker_free", "entity_type": "locker", "transition_id": 30}',NULL,NULL,'2026-07-23 15:34:51'),
(69,'svc_courier_01','fsm.instance.completed',69,'order',1594,'{"effect": {"leg": "pickup", "status": "order_client_post1", "cell_id": 47, "order_id": 1594}, "to_state": "order_client_post1", "entity_id": 1594, "companions": [{"index": 0, "effect": {"cell_id": 47, "cell_status": "locker_opened"}, "to_state": "locker_opened", "entity_id": 47, "event_name": "locker_open_locker", "from_state": "locker_reserved", "entity_type": "locker", "transition_id": 31}], "event_name": "open_cell", "from_state": "order_created", "entity_type": "order", "transition_id": 136}',NULL,NULL,'2026-07-23 15:34:59'),
(70,'svc_courier_01','fsm.instance.completed',70,'order',1594,'{"effect": {"leg": "pickup", "status": "order_parcel_confirmed", "cell_id": 47, "order_id": 1594, "direction_id": 9}, "to_state": "order_parcel_confirmed", "entity_id": 1594, "companions": [{"index": 0, "effect": {"cell_id": 47, "cell_status": "locker_occupied"}, "to_state": "locker_occupied", "entity_id": 47, "event_name": "locker_close_locker", "from_state": "locker_opened", "entity_type": "locker", "transition_id": 126}], "event_name": "close_cell", "from_state": "order_client_post1", "entity_type": "order", "transition_id": 137}',NULL,NULL,'2026-07-23 15:35:06'),
(71,'svc_courier_01','fsm.instance.completed',71,'locker',50,'{"effect": {"cell_id": 50, "order_id": 1595, "cell_status": "locker_reserved"}, "to_state": "locker_reserved", "entity_id": 50, "companions": [], "event_name": "locker_reserve_cell", "from_state": "locker_free", "entity_type": "locker", "transition_id": 30}',NULL,NULL,'2026-07-23 15:35:13'),
(72,'svc_courier_01','fsm.instance.completed',72,'locker',59,'{"effect": {"cell_id": 59, "order_id": 1595, "cell_status": "locker_reserved"}, "to_state": "locker_reserved", "entity_id": 59, "companions": [], "event_name": "locker_reserve_cell", "from_state": "locker_free", "entity_type": "locker", "transition_id": 30}',NULL,NULL,'2026-07-23 15:35:16'),
(73,'svc_courier_01','fsm.instance.completed',73,'order',1595,'{"effect": {"leg": "pickup", "status": "order_client_post1", "cell_id": 50, "order_id": 1595}, "to_state": "order_client_post1", "entity_id": 1595, "companions": [{"index": 0, "effect": {"cell_id": 50, "cell_status": "locker_opened"}, "to_state": "locker_opened", "entity_id": 50, "event_name": "locker_open_locker", "from_state": "locker_reserved", "entity_type": "locker", "transition_id": 31}], "event_name": "open_cell", "from_state": "order_created", "entity_type": "order", "transition_id": 136}',NULL,NULL,'2026-07-23 15:35:25'),
(74,'svc_courier_01','fsm.instance.completed',74,'order',1595,'{"effect": {"leg": "pickup", "status": "order_parcel_confirmed", "cell_id": 50, "order_id": 1595, "direction_id": 9}, "to_state": "order_parcel_confirmed", "entity_id": 1595, "companions": [{"index": 0, "effect": {"cell_id": 50, "cell_status": "locker_occupied"}, "to_state": "locker_occupied", "entity_id": 50, "event_name": "locker_close_locker", "from_state": "locker_opened", "entity_type": "locker", "transition_id": 126}], "event_name": "close_cell", "from_state": "order_client_post1", "entity_type": "order", "transition_id": 137}',NULL,NULL,'2026-07-23 15:35:32'),
(75,'svc_courier_01','fsm.instance.completed',75,'driver_reservations',48,'{"effect": {"status": "reservation_cancelled", "direction_id": 9, "released_count": 3, "reservation_id": 48}, "to_state": "reservation_cancelled", "entity_id": 48, "companions": [], "event_name": "cancel_reservation", "from_state": "reservation_active", "entity_type": "driver_reservations", "transition_id": 149}',NULL,NULL,'2026-07-23 15:36:30'),
(76,'svc_courier_01','fsm.instance.completed',77,'locker',54,'{"effect": {"cell_id": 54, "order_id": 1596, "cell_status": "locker_reserved"}, "to_state": "locker_reserved", "entity_id": 54, "companions": [], "event_name": "locker_reserve_cell", "from_state": "locker_free", "entity_type": "locker", "transition_id": 30}',NULL,NULL,'2026-07-24 03:43:25'),
(77,'svc_courier_01','fsm.instance.completed',76,'locker',3,'{"effect": {"cell_id": 3, "order_id": 1596, "cell_status": "locker_reserved"}, "to_state": "locker_reserved", "entity_id": 3, "companions": [], "event_name": "locker_reserve_cell", "from_state": "locker_free", "entity_type": "locker", "transition_id": 30}',NULL,NULL,'2026-07-24 03:43:25'),
(78,'svc_courier_01','fsm.instance.completed',78,'order',1596,'{"effect": {"leg": "pickup", "status": "order_client_post1", "cell_id": 3, "order_id": 1596}, "to_state": "order_client_post1", "entity_id": 1596, "companions": [{"index": 0, "effect": {"cell_id": 3, "cell_status": "locker_opened"}, "to_state": "locker_opened", "entity_id": 3, "event_name": "locker_open_locker", "from_state": "locker_reserved", "entity_type": "locker", "transition_id": 31}], "event_name": "open_cell", "from_state": "order_created", "entity_type": "order", "transition_id": 136}',NULL,NULL,'2026-07-24 03:43:34'),
(79,'svc_courier_01','fsm.instance.completed',79,'order',1596,'{"effect": {"leg": "pickup", "status": "order_parcel_confirmed", "cell_id": 3, "order_id": 1596, "direction_id": 9}, "to_state": "order_parcel_confirmed", "entity_id": 1596, "companions": [{"index": 0, "effect": {"cell_id": 3, "cell_status": "locker_occupied"}, "to_state": "locker_occupied", "entity_id": 3, "event_name": "locker_close_locker", "from_state": "locker_opened", "entity_type": "locker", "transition_id": 126}], "event_name": "close_cell", "from_state": "order_client_post1", "entity_type": "order", "transition_id": 137}',NULL,NULL,'2026-07-24 03:43:42'),
(80,'svc_courier_01','fsm.instance.completed',80,'locker',48,'{"effect": {"cell_id": 48, "order_id": 1597, "cell_status": "locker_reserved"}, "to_state": "locker_reserved", "entity_id": 48, "companions": [], "event_name": "locker_reserve_cell", "from_state": "locker_free", "entity_type": "locker", "transition_id": 30}',NULL,NULL,'2026-07-24 03:43:48'),
(81,'svc_courier_01','fsm.instance.completed',81,'locker',57,'{"effect": {"cell_id": 57, "order_id": 1597, "cell_status": "locker_reserved"}, "to_state": "locker_reserved", "entity_id": 57, "companions": [], "event_name": "locker_reserve_cell", "from_state": "locker_free", "entity_type": "locker", "transition_id": 30}',NULL,NULL,'2026-07-24 03:43:49'),
(82,'svc_courier_01','fsm.instance.completed',82,'order',1597,'{"effect": {"leg": "pickup", "status": "order_client_post1", "cell_id": 48, "order_id": 1597}, "to_state": "order_client_post1", "entity_id": 1597, "companions": [{"index": 0, "effect": {"cell_id": 48, "cell_status": "locker_opened"}, "to_state": "locker_opened", "entity_id": 48, "event_name": "locker_open_locker", "from_state": "locker_reserved", "entity_type": "locker", "transition_id": 31}], "event_name": "open_cell", "from_state": "order_created", "entity_type": "order", "transition_id": 136}',NULL,NULL,'2026-07-24 03:43:56'),
(83,'svc_courier_01','fsm.instance.completed',83,'order',1597,'{"effect": {"leg": "pickup", "status": "order_parcel_confirmed", "cell_id": 48, "order_id": 1597, "direction_id": 9}, "to_state": "order_parcel_confirmed", "entity_id": 1597, "companions": [{"index": 0, "effect": {"cell_id": 48, "cell_status": "locker_occupied"}, "to_state": "locker_occupied", "entity_id": 48, "event_name": "locker_close_locker", "from_state": "locker_opened", "entity_type": "locker", "transition_id": 126}], "event_name": "close_cell", "from_state": "order_client_post1", "entity_type": "order", "transition_id": 137}',NULL,NULL,'2026-07-24 03:44:03'),
(84,'svc_courier_01','fsm.instance.completed',84,'locker',51,'{"effect": {"cell_id": 51, "order_id": 1598, "cell_status": "locker_reserved"}, "to_state": "locker_reserved", "entity_id": 51, "companions": [], "event_name": "locker_reserve_cell", "from_state": "locker_free", "entity_type": "locker", "transition_id": 30}',NULL,NULL,'2026-07-24 03:44:09'),
(85,'svc_courier_01','fsm.instance.completed',85,'locker',60,'{"effect": {"cell_id": 60, "order_id": 1598, "cell_status": "locker_reserved"}, "to_state": "locker_reserved", "entity_id": 60, "companions": [], "event_name": "locker_reserve_cell", "from_state": "locker_free", "entity_type": "locker", "transition_id": 30}',NULL,NULL,'2026-07-24 03:44:10'),
(86,'svc_courier_01','fsm.instance.completed',86,'order',1598,'{"effect": {"leg": "pickup", "status": "order_client_post1", "cell_id": 51, "order_id": 1598}, "to_state": "order_client_post1", "entity_id": 1598, "companions": [{"index": 0, "effect": {"cell_id": 51, "cell_status": "locker_opened"}, "to_state": "locker_opened", "entity_id": 51, "event_name": "locker_open_locker", "from_state": "locker_reserved", "entity_type": "locker", "transition_id": 31}], "event_name": "open_cell", "from_state": "order_created", "entity_type": "order", "transition_id": 136}',NULL,NULL,'2026-07-24 03:44:16'),
(87,'svc_courier_01','fsm.instance.completed',87,'order',1598,'{"effect": {"leg": "pickup", "status": "order_parcel_confirmed", "cell_id": 51, "order_id": 1598, "direction_id": 9}, "to_state": "order_parcel_confirmed", "entity_id": 1598, "companions": [{"index": 0, "effect": {"cell_id": 51, "cell_status": "locker_occupied"}, "to_state": "locker_occupied", "entity_id": 51, "event_name": "locker_close_locker", "from_state": "locker_opened", "entity_type": "locker", "transition_id": 126}], "event_name": "close_cell", "from_state": "order_client_post1", "entity_type": "order", "transition_id": 137}',NULL,NULL,'2026-07-24 03:44:24'),
(88,'svc_courier_01','fsm.instance.completed',88,'driver_reservations',50,'{"effect": {"status": "reservation_loading", "direction_id": 9, "reservation_id": 50}, "to_state": "reservation_loading", "entity_id": 50, "companions": [], "event_name": "start_loading", "from_state": "reservation_active", "entity_type": "driver_reservations", "transition_id": 145}',NULL,NULL,'2026-07-24 03:50:47'),
(89,'svc_courier_01','fsm.instance.completed',89,'order',1596,'{"effect": {"leg": "pickup", "status": "order_parcel_submitted", "cell_id": 3, "order_id": 1596}, "to_state": "order_parcel_submitted", "entity_id": 1596, "companions": [{"index": 0, "effect": {"cell_id": 3, "cell_status": "locker_opened"}, "to_state": "locker_opened", "entity_id": 3, "event_name": "locker_open_locker", "from_state": "locker_occupied", "entity_type": "locker", "transition_id": 62}], "event_name": "open_cell", "from_state": "order_parcel_confirmed", "entity_type": "order", "transition_id": 29}',NULL,NULL,'2026-07-24 03:50:56'),
(90,'svc_courier_01','fsm.instance.completed',90,'order',1596,'{"effect": {"leg": "pickup", "status": "order_picked_up_from_post1", "cell_id": 3, "order_id": 1596}, "to_state": "order_picked_up_from_post1", "entity_id": 1596, "companions": [{"index": 0, "effect": {"cell_id": 3, "cell_status": "locker_closed_empty"}, "to_state": "locker_closed_empty", "entity_id": 3, "event_name": "locker_close_pickup", "from_state": "locker_opened", "entity_type": "locker", "transition_id": 127}], "event_name": "close_cell", "from_state": "order_parcel_submitted", "entity_type": "order", "transition_id": 74}',NULL,NULL,'2026-07-24 03:51:01'),
(91,'svc_courier_01','fsm.instance.completed',91,'order',1597,'{"effect": {"leg": "pickup", "status": "order_parcel_submitted", "cell_id": 48, "order_id": 1597}, "to_state": "order_parcel_submitted", "entity_id": 1597, "companions": [{"index": 0, "effect": {"cell_id": 48, "cell_status": "locker_opened"}, "to_state": "locker_opened", "entity_id": 48, "event_name": "locker_open_locker", "from_state": "locker_occupied", "entity_type": "locker", "transition_id": 62}], "event_name": "open_cell", "from_state": "order_parcel_confirmed", "entity_type": "order", "transition_id": 29}',NULL,NULL,'2026-07-24 03:51:09'),
(92,'svc_courier_01','fsm.instance.completed',92,'order',1597,'{"effect": {"leg": "pickup", "status": "order_picked_up_from_post1", "cell_id": 48, "order_id": 1597}, "to_state": "order_picked_up_from_post1", "entity_id": 1597, "companions": [{"index": 0, "effect": {"cell_id": 48, "cell_status": "locker_closed_empty"}, "to_state": "locker_closed_empty", "entity_id": 48, "event_name": "locker_close_pickup", "from_state": "locker_opened", "entity_type": "locker", "transition_id": 127}], "event_name": "close_cell", "from_state": "order_parcel_submitted", "entity_type": "order", "transition_id": 74}',NULL,NULL,'2026-07-24 03:51:16'),
(93,'svc_courier_01','fsm.instance.completed',93,'order',1598,'{"effect": {"leg": "pickup", "status": "order_parcel_submitted", "cell_id": 51, "order_id": 1598}, "to_state": "order_parcel_submitted", "entity_id": 1598, "companions": [{"index": 0, "effect": {"cell_id": 51, "cell_status": "locker_opened"}, "to_state": "locker_opened", "entity_id": 51, "event_name": "locker_open_locker", "from_state": "locker_occupied", "entity_type": "locker", "transition_id": 62}], "event_name": "open_cell", "from_state": "order_parcel_confirmed", "entity_type": "order", "transition_id": 29}',NULL,NULL,'2026-07-24 03:51:24'),
(94,'svc_courier_01','fsm.instance.completed',94,'order',1598,'{"effect": {"leg": "pickup", "status": "order_picked_up_from_post1", "cell_id": 51, "order_id": 1598}, "to_state": "order_picked_up_from_post1", "entity_id": 1598, "companions": [{"index": 0, "effect": {"cell_id": 51, "cell_status": "locker_closed_empty"}, "to_state": "locker_closed_empty", "entity_id": 51, "event_name": "locker_close_pickup", "from_state": "locker_opened", "entity_type": "locker", "transition_id": 127}], "event_name": "close_cell", "from_state": "order_parcel_submitted", "entity_type": "order", "transition_id": 74}',NULL,NULL,'2026-07-24 03:51:31'),
(95,'svc_courier_01','fsm.instance.completed',95,'driver_reservations',50,'{"effect": {"status": "reservation_completed", "direction_id": 9, "reservation_id": 50}, "to_state": "reservation_completed", "entity_id": 50, "companions": [], "event_name": "complete_loading", "from_state": "reservation_loading", "entity_type": "driver_reservations", "transition_id": 146}',NULL,NULL,'2026-07-24 05:08:42'),
(96,'svc_courier_01','fsm.instance.completed',97,'order',1597,'{"effect": {"status": "order_in_transit_to_post2", "order_id": 1597}, "to_state": "order_in_transit_to_post2", "entity_id": 1597, "companions": [], "event_name": "start_order_transit", "from_state": "order_picked_up_from_post1", "entity_type": "order", "transition_id": 75}',NULL,NULL,'2026-07-24 06:25:39'),
(97,'svc_courier_01','fsm.instance.completed',96,'order',1596,'{"effect": {"status": "order_in_transit_to_post2", "order_id": 1596}, "to_state": "order_in_transit_to_post2", "entity_id": 1596, "companions": [], "event_name": "start_order_transit", "from_state": "order_picked_up_from_post1", "entity_type": "order", "transition_id": 75}',NULL,NULL,'2026-07-24 06:25:39'),
(98,'svc_courier_01','fsm.instance.completed',98,'order',1598,'{"effect": {"status": "order_in_transit_to_post2", "order_id": 1598}, "to_state": "order_in_transit_to_post2", "entity_id": 1598, "companions": [], "event_name": "start_order_transit", "from_state": "order_picked_up_from_post1", "entity_type": "order", "transition_id": 75}',NULL,NULL,'2026-07-24 06:25:42'),
(99,'svc_courier_01','fsm.instance.completed',99,'trip',59,'{"effect": {"status": "trip_in_progress", "trip_id": 59}, "to_state": "trip_in_progress", "entity_id": 59, "companions": [], "event_name": "start_trip", "from_state": "trip_assigned", "entity_type": "trip", "transition_id": 57}',NULL,NULL,'2026-07-24 06:41:37'),
(100,'svc_courier_01','fsm.instance.completed',100,'locker',71,'{"effect": {"cell_id": 71, "order_id": 1599, "cell_status": "locker_reserved"}, "to_state": "locker_reserved", "entity_id": 71, "companions": [], "event_name": "locker_reserve_cell", "from_state": "locker_free", "entity_type": "locker", "transition_id": 30}',NULL,NULL,'2026-07-24 07:26:30'),
(101,'svc_courier_01','fsm.instance.completed',101,'locker',70,'{"effect": {"cell_id": 70, "order_id": 1599, "cell_status": "locker_reserved"}, "to_state": "locker_reserved", "entity_id": 70, "companions": [], "event_name": "locker_reserve_cell", "from_state": "locker_free", "entity_type": "locker", "transition_id": 30}',NULL,NULL,'2026-07-24 07:26:31'),
(102,'svc_courier_01','fsm.instance.completed',102,'order',1599,'{"effect": {"leg": "pickup", "status": "order_client_post1", "cell_id": 71, "order_id": 1599}, "to_state": "order_client_post1", "entity_id": 1599, "companions": [{"index": 0, "effect": {"cell_id": 71, "cell_status": "locker_opened"}, "to_state": "locker_opened", "entity_id": 71, "event_name": "locker_open_locker", "from_state": "locker_reserved", "entity_type": "locker", "transition_id": 31}], "event_name": "open_cell", "from_state": "order_created", "entity_type": "order", "transition_id": 136}',NULL,NULL,'2026-07-24 07:26:39'),
(103,'svc_courier_01','fsm.instance.completed',103,'order',1599,'{"effect": {"leg": "pickup", "status": "order_parcel_confirmed", "cell_id": 71, "order_id": 1599, "direction_id": 10}, "to_state": "order_parcel_confirmed", "entity_id": 1599, "companions": [{"index": 0, "effect": {"cell_id": 71, "cell_status": "locker_occupied"}, "to_state": "locker_occupied", "entity_id": 71, "event_name": "locker_close_locker", "from_state": "locker_opened", "entity_type": "locker", "transition_id": 126}], "event_name": "close_cell", "from_state": "order_client_post1", "entity_type": "order", "transition_id": 137}',NULL,NULL,'2026-07-24 07:26:46'),
(104,'svc_courier_01','fsm.instance.completed',104,'locker',73,'{"effect": {"cell_id": 73, "order_id": 1600, "cell_status": "locker_reserved"}, "to_state": "locker_reserved", "entity_id": 73, "companions": [], "event_name": "locker_reserve_cell", "from_state": "locker_free", "entity_type": "locker", "transition_id": 30}',NULL,NULL,'2026-07-24 07:26:53'),
(105,'svc_courier_01','fsm.instance.completed',105,'locker',72,'{"effect": {"cell_id": 72, "order_id": 1600, "cell_status": "locker_reserved"}, "to_state": "locker_reserved", "entity_id": 72, "companions": [], "event_name": "locker_reserve_cell", "from_state": "locker_free", "entity_type": "locker", "transition_id": 30}',NULL,NULL,'2026-07-24 07:26:54'),
(106,'svc_courier_01','fsm.instance.completed',106,'order',1600,'{"effect": {"leg": "pickup", "status": "order_courier1_assigned", "order_id": 1600, "executor_user_id": 6}, "to_state": "order_courier1_assigned", "entity_id": 1600, "companions": [], "event_name": "assign_executor", "from_state": "order_created", "entity_type": "order", "transition_id": 167}',NULL,NULL,'2026-07-24 07:27:00'),
(107,'svc_courier_01','fsm.instance.completed',107,'order',1600,'{"effect": {"leg": "pickup", "status": "order_courier_has_parcel", "cell_id": 73, "order_id": 1600}, "to_state": "order_courier_has_parcel", "entity_id": 1600, "companions": [{"index": 0, "effect": {"cell_id": 73, "cell_status": "locker_opened"}, "to_state": "locker_opened", "entity_id": 73, "event_name": "locker_open_locker", "from_state": "locker_reserved", "entity_type": "locker", "transition_id": 31}], "event_name": "open_cell", "from_state": "order_courier1_assigned", "entity_type": "order", "transition_id": 38}',NULL,NULL,'2026-07-24 07:27:08'),
(108,'svc_courier_01','fsm.instance.completed',108,'order',1600,'{"effect": {"leg": "pickup", "status": "order_parcel_confirmed", "cell_id": 73, "order_id": 1600, "direction_id": 11}, "to_state": "order_parcel_confirmed", "entity_id": 1600, "companions": [{"index": 0, "effect": {"cell_id": 73, "cell_status": "locker_occupied"}, "to_state": "locker_occupied", "entity_id": 73, "event_name": "locker_close_locker", "from_state": "locker_opened", "entity_type": "locker", "transition_id": 126}], "event_name": "close_cell", "from_state": "order_courier_has_parcel", "entity_type": "order", "transition_id": 36}',NULL,NULL,'2026-07-24 07:27:18'),
(109,'svc_courier_01','fsm.instance.completed',109,'locker',71,'{"effect": {"cell_id": 71, "order_id": 1601, "cell_status": "locker_reserved"}, "to_state": "locker_reserved", "entity_id": 71, "companions": [], "event_name": "locker_reserve_cell", "from_state": "locker_free", "entity_type": "locker", "transition_id": 30}',NULL,NULL,'2026-07-24 08:09:04'),
(110,'svc_courier_01','fsm.instance.completed',110,'locker',70,'{"effect": {"cell_id": 70, "order_id": 1601, "cell_status": "locker_reserved"}, "to_state": "locker_reserved", "entity_id": 70, "companions": [], "event_name": "locker_reserve_cell", "from_state": "locker_free", "entity_type": "locker", "transition_id": 30}',NULL,NULL,'2026-07-24 08:09:07'),
(111,'svc_courier_01','fsm.instance.completed',111,'order',1601,'{"effect": {"leg": "pickup", "status": "order_client_post1", "cell_id": 71, "order_id": 1601}, "to_state": "order_client_post1", "entity_id": 1601, "companions": [{"index": 0, "effect": {"cell_id": 71, "cell_status": "locker_opened"}, "to_state": "locker_opened", "entity_id": 71, "event_name": "locker_open_locker", "from_state": "locker_reserved", "entity_type": "locker", "transition_id": 31}], "event_name": "open_cell", "from_state": "order_created", "entity_type": "order", "transition_id": 136}',NULL,NULL,'2026-07-24 08:09:15'),
(112,'svc_courier_01','fsm.instance.completed',112,'order',1601,'{"effect": {"leg": "pickup", "status": "order_parcel_confirmed", "cell_id": 71, "order_id": 1601, "direction_id": 12}, "to_state": "order_parcel_confirmed", "entity_id": 1601, "companions": [{"index": 0, "effect": {"cell_id": 71, "cell_status": "locker_occupied"}, "to_state": "locker_occupied", "entity_id": 71, "event_name": "locker_close_locker", "from_state": "locker_opened", "entity_type": "locker", "transition_id": 126}], "event_name": "close_cell", "from_state": "order_client_post1", "entity_type": "order", "transition_id": 137}',NULL,NULL,'2026-07-24 08:09:24'),
(113,'svc_courier_01','fsm.instance.completed',113,'locker',73,'{"effect": {"cell_id": 73, "order_id": 1602, "cell_status": "locker_reserved"}, "to_state": "locker_reserved", "entity_id": 73, "companions": [], "event_name": "locker_reserve_cell", "from_state": "locker_free", "entity_type": "locker", "transition_id": 30}',NULL,NULL,'2026-07-24 08:09:30'),
(114,'svc_courier_01','fsm.instance.completed',114,'locker',72,'{"effect": {"cell_id": 72, "order_id": 1602, "cell_status": "locker_reserved"}, "to_state": "locker_reserved", "entity_id": 72, "companions": [], "event_name": "locker_reserve_cell", "from_state": "locker_free", "entity_type": "locker", "transition_id": 30}',NULL,NULL,'2026-07-24 08:09:34'),
(115,'svc_courier_01','fsm.instance.completed',115,'order',1602,'{"effect": {"leg": "pickup", "status": "order_courier1_assigned", "order_id": 1602, "executor_user_id": 6}, "to_state": "order_courier1_assigned", "entity_id": 1602, "companions": [], "event_name": "assign_executor", "from_state": "order_created", "entity_type": "order", "transition_id": 167}',NULL,NULL,'2026-07-24 08:09:40'),
(116,'svc_courier_01','fsm.instance.completed',116,'order',1602,'{"effect": {"leg": "pickup", "status": "order_courier_has_parcel", "cell_id": 73, "order_id": 1602}, "to_state": "order_courier_has_parcel", "entity_id": 1602, "companions": [{"index": 0, "effect": {"cell_id": 73, "cell_status": "locker_opened"}, "to_state": "locker_opened", "entity_id": 73, "event_name": "locker_open_locker", "from_state": "locker_reserved", "entity_type": "locker", "transition_id": 31}], "event_name": "open_cell", "from_state": "order_courier1_assigned", "entity_type": "order", "transition_id": 38}',NULL,NULL,'2026-07-24 08:09:48'),
(117,'svc_courier_01','fsm.instance.completed',117,'order',1602,'{"effect": {"leg": "pickup", "status": "order_parcel_confirmed", "cell_id": 73, "order_id": 1602, "direction_id": 13}, "to_state": "order_parcel_confirmed", "entity_id": 1602, "companions": [{"index": 0, "effect": {"cell_id": 73, "cell_status": "locker_occupied"}, "to_state": "locker_occupied", "entity_id": 73, "event_name": "locker_close_locker", "from_state": "locker_opened", "entity_type": "locker", "transition_id": 126}], "event_name": "close_cell", "from_state": "order_courier_has_parcel", "entity_type": "order", "transition_id": 36}',NULL,NULL,'2026-07-24 08:09:56'),
(118,'svc_courier_01','fsm.instance.completed',118,'driver_reservations',52,'{"effect": {"status": "reservation_loading", "direction_id": 12, "reservation_id": 52}, "to_state": "reservation_loading", "entity_id": 52, "companions": [], "event_name": "start_loading", "from_state": "reservation_active", "entity_type": "driver_reservations", "transition_id": 145}',NULL,NULL,'2026-07-24 08:10:07'),
(119,'svc_courier_01','fsm.instance.completed',119,'order',1601,'{"effect": {"leg": "pickup", "status": "order_parcel_submitted", "cell_id": 71, "order_id": 1601}, "to_state": "order_parcel_submitted", "entity_id": 1601, "companions": [{"index": 0, "effect": {"cell_id": 71, "cell_status": "locker_opened"}, "to_state": "locker_opened", "entity_id": 71, "event_name": "locker_open_locker", "from_state": "locker_occupied", "entity_type": "locker", "transition_id": 62}], "event_name": "open_cell", "from_state": "order_parcel_confirmed", "entity_type": "order", "transition_id": 29}',NULL,NULL,'2026-07-24 08:10:16'),
(120,'svc_courier_01','fsm.instance.completed',120,'order',1601,'{"effect": {"leg": "pickup", "status": "order_picked_up_from_post1", "cell_id": 71, "order_id": 1601}, "to_state": "order_picked_up_from_post1", "entity_id": 1601, "companions": [{"index": 0, "effect": {"cell_id": 71, "cell_status": "locker_closed_empty"}, "to_state": "locker_closed_empty", "entity_id": 71, "event_name": "locker_close_pickup", "from_state": "locker_opened", "entity_type": "locker", "transition_id": 127}], "event_name": "close_cell", "from_state": "order_parcel_submitted", "entity_type": "order", "transition_id": 74}',NULL,NULL,'2026-07-24 08:10:23'),
(121,'svc_courier_01','fsm.instance.completed',121,'order',1602,'{"effect": {"leg": "pickup", "status": "order_parcel_submitted", "cell_id": 73, "order_id": 1602}, "to_state": "order_parcel_submitted", "entity_id": 1602, "companions": [{"index": 0, "effect": {"cell_id": 73, "cell_status": "locker_opened"}, "to_state": "locker_opened", "entity_id": 73, "event_name": "locker_open_locker", "from_state": "locker_occupied", "entity_type": "locker", "transition_id": 62}], "event_name": "open_cell", "from_state": "order_parcel_confirmed", "entity_type": "order", "transition_id": 29}',NULL,NULL,'2026-07-24 08:10:33'),
(122,'svc_courier_01','fsm.instance.completed',122,'order',1602,'{"effect": {"leg": "pickup", "status": "order_picked_up_from_post1", "cell_id": 73, "order_id": 1602}, "to_state": "order_picked_up_from_post1", "entity_id": 1602, "companions": [{"index": 0, "effect": {"cell_id": 73, "cell_status": "locker_closed_empty"}, "to_state": "locker_closed_empty", "entity_id": 73, "event_name": "locker_close_pickup", "from_state": "locker_opened", "entity_type": "locker", "transition_id": 127}], "event_name": "close_cell", "from_state": "order_parcel_submitted", "entity_type": "order", "transition_id": 74}',NULL,NULL,'2026-07-24 08:10:42'),
(123,'svc_courier_01','fsm.instance.completed',123,'driver_reservations',52,'{"effect": {"status": "reservation_completed", "direction_id": 12, "reservation_id": 52}, "to_state": "reservation_completed", "entity_id": 52, "companions": [], "event_name": "complete_loading", "from_state": "reservation_loading", "entity_type": "driver_reservations", "transition_id": 146}',NULL,NULL,'2026-07-24 08:10:52'),
(124,'svc_courier_01','fsm.instance.completed',124,'order',1601,'{"effect": {"status": "order_in_transit_to_post2", "order_id": 1601}, "to_state": "order_in_transit_to_post2", "entity_id": 1601, "companions": [], "event_name": "start_order_transit", "from_state": "order_picked_up_from_post1", "entity_type": "order", "transition_id": 75}',NULL,NULL,'2026-07-24 08:11:00'),
(125,'svc_courier_01','fsm.instance.completed',125,'order',1602,'{"effect": {"status": "order_in_transit_to_post2", "order_id": 1602}, "to_state": "order_in_transit_to_post2", "entity_id": 1602, "companions": [], "event_name": "start_order_transit", "from_state": "order_picked_up_from_post1", "entity_type": "order", "transition_id": 75}',NULL,NULL,'2026-07-24 08:11:04'),
(126,'svc_courier_01','fsm.instance.completed',126,'trip',60,'{"effect": {"status": "trip_in_progress", "trip_id": 60}, "to_state": "trip_in_progress", "entity_id": 60, "companions": [], "event_name": "start_trip", "from_state": "trip_assigned", "entity_type": "trip", "transition_id": 57}',NULL,NULL,'2026-07-24 08:11:08'),
(127,'svc_courier_01','fsm.instance.completed',127,'order',1601,'{"effect": {"leg": "delivery", "status": "order_arrived_at_post2", "cell_id": 70, "order_id": 1601}, "to_state": "order_arrived_at_post2", "entity_id": 1601, "companions": [{"index": 0, "effect": {"cell_id": 70, "cell_status": "locker_opened"}, "to_state": "locker_opened", "entity_id": 70, "event_name": "locker_open_locker", "from_state": "locker_reserved", "entity_type": "locker", "transition_id": 31}], "event_name": "open_cell", "from_state": "order_in_transit_to_post2", "entity_type": "order", "transition_id": 76}',NULL,NULL,'2026-07-24 08:54:46'),
(128,'svc_courier_01','fsm.instance.completed',128,'order',1601,'{"effect": {"leg": "delivery", "status": "order_parcel_confirmed_post2", "cell_id": 70, "order_id": 1601}, "to_state": "order_parcel_confirmed_post2", "entity_id": 1601, "companions": [{"index": 0, "effect": {"cell_id": 70, "cell_status": "locker_occupied"}, "to_state": "locker_occupied", "entity_id": 70, "event_name": "locker_close_locker", "from_state": "locker_opened", "entity_type": "locker", "transition_id": 126}], "event_name": "close_cell", "from_state": "order_arrived_at_post2", "entity_type": "order", "transition_id": 77}',NULL,NULL,'2026-07-24 08:54:52'),
(129,'svc_courier_01','fsm.instance.completed',129,'order',1602,'{"effect": {"leg": "delivery", "status": "order_arrived_at_post2", "cell_id": 72, "order_id": 1602}, "to_state": "order_arrived_at_post2", "entity_id": 1602, "companions": [{"index": 0, "effect": {"cell_id": 72, "cell_status": "locker_opened"}, "to_state": "locker_opened", "entity_id": 72, "event_name": "locker_open_locker", "from_state": "locker_reserved", "entity_type": "locker", "transition_id": 31}], "event_name": "open_cell", "from_state": "order_in_transit_to_post2", "entity_type": "order", "transition_id": 76}',NULL,NULL,'2026-07-24 08:55:01'),
(130,'svc_courier_01','fsm.instance.completed',130,'order',1602,'{"effect": {"leg": "delivery", "status": "order_parcel_confirmed_post2", "cell_id": 72, "order_id": 1602}, "to_state": "order_parcel_confirmed_post2", "entity_id": 1602, "companions": [{"index": 0, "effect": {"cell_id": 72, "cell_status": "locker_occupied"}, "to_state": "locker_occupied", "entity_id": 72, "event_name": "locker_close_locker", "from_state": "locker_opened", "entity_type": "locker", "transition_id": 126}], "event_name": "close_cell", "from_state": "order_arrived_at_post2", "entity_type": "order", "transition_id": 77}',NULL,NULL,'2026-07-24 08:55:08'),
(131,'svc_courier_01','fsm.instance.completed',131,'trip',60,'{"effect": {"status": "trip_completed", "trip_id": 60}, "to_state": "trip_completed", "entity_id": 60, "companions": [], "event_name": "complete_trip", "from_state": "trip_in_progress", "entity_type": "trip", "transition_id": 135}',NULL,NULL,'2026-07-24 08:55:13'),
(132,'svc_courier_01','fsm.instance.completed',132,'order',1601,'{"effect": {"leg": "delivery", "status": "order_delivered_to_client", "cell_id": 70, "order_id": 1601}, "to_state": "order_delivered_to_client", "entity_id": 1601, "companions": [{"index": 0, "effect": {"cell_id": 70, "cell_status": "locker_opened"}, "to_state": "locker_opened", "entity_id": 70, "event_name": "locker_open_locker", "from_state": "locker_occupied", "entity_type": "locker", "transition_id": 62}], "event_name": "open_cell", "from_state": "order_parcel_confirmed_post2", "entity_type": "order", "transition_id": 80}',NULL,NULL,'2026-07-24 10:17:56'),
(133,'svc_courier_01','fsm.instance.completed',133,'order',1601,'{"effect": {"leg": "delivery", "status": "order_completed", "cell_id": 70, "order_id": 1601}, "to_state": "order_completed", "entity_id": 1601, "companions": [{"index": 0, "effect": {"cell_id": 70, "cell_status": "locker_closed_empty"}, "to_state": "locker_closed_empty", "entity_id": 70, "event_name": "locker_close_pickup", "from_state": "locker_opened", "entity_type": "locker", "transition_id": 127}], "event_name": "close_cell", "from_state": "order_delivered_to_client", "entity_type": "order", "transition_id": 81}',NULL,NULL,'2026-07-24 10:18:03'),
(134,'svc_courier_01','fsm.instance.completed',134,'order',1602,'{"effect": {"leg": "delivery", "status": "order_courier2_assigned", "order_id": 1602, "executor_user_id": 2}, "to_state": "order_courier2_assigned", "entity_id": 1602, "companions": [], "event_name": "assign_executor", "from_state": "order_parcel_confirmed_post2", "entity_type": "order", "transition_id": 168}',NULL,NULL,'2026-07-24 10:18:49'),
(135,'svc_courier_01','fsm.instance.completed',135,'order',1602,'{"effect": {"leg": "delivery", "status": "order_courier2_has_parcel", "cell_id": 72, "order_id": 1602}, "to_state": "order_courier2_has_parcel", "entity_id": 1602, "companions": [{"index": 0, "effect": {"cell_id": 72, "cell_status": "locker_opened"}, "to_state": "locker_opened", "entity_id": 72, "event_name": "locker_open_locker", "from_state": "locker_occupied", "entity_type": "locker", "transition_id": 62}], "event_name": "open_cell", "from_state": "order_courier2_assigned", "entity_type": "order", "transition_id": 83}',NULL,NULL,'2026-07-24 10:18:57'),
(136,'svc_courier_01','fsm.instance.completed',136,'order',1602,'{"effect": {"leg": "delivery", "status": "order_courier2_parcel_delivered", "cell_id": 72, "order_id": 1602}, "to_state": "order_courier2_parcel_delivered", "entity_id": 1602, "companions": [{"index": 0, "effect": {"cell_id": 72, "cell_status": "locker_closed_empty"}, "to_state": "locker_closed_empty", "entity_id": 72, "event_name": "locker_close_pickup", "from_state": "locker_opened", "entity_type": "locker", "transition_id": 127}], "event_name": "close_cell", "from_state": "order_courier2_has_parcel", "entity_type": "order", "transition_id": 84}',NULL,NULL,'2026-07-24 10:19:04'),
(137,'svc_courier_01','fsm.instance.completed',137,'order',1602,'{"effect": {"status": "order_completed", "order_id": 1602, "delivery_code_used": true}, "to_state": "order_completed", "entity_id": 1602, "companions": [], "event_name": "confirm_courier2_delivery", "from_state": "order_courier2_parcel_delivered", "entity_type": "order", "transition_id": 125}',NULL,NULL,'2026-07-24 10:19:14'),
(138,'svc_courier_01','fsm.instance.completed',138,'locker',79,'{"effect": {"cell_id": 79, "order_id": 1603, "cell_status": "locker_reserved"}, "to_state": "locker_reserved", "entity_id": 79, "companions": [], "event_name": "locker_reserve_cell", "from_state": "locker_free", "entity_type": "locker", "transition_id": 30}',NULL,NULL,'2026-07-24 11:57:31'),
(139,'svc_courier_01','fsm.instance.completed',139,'locker',78,'{"effect": {"cell_id": 78, "order_id": 1603, "cell_status": "locker_reserved"}, "to_state": "locker_reserved", "entity_id": 78, "companions": [], "event_name": "locker_reserve_cell", "from_state": "locker_free", "entity_type": "locker", "transition_id": 30}',NULL,NULL,'2026-07-24 11:57:34'),
(140,'svc_courier_01','fsm.instance.completed',140,'order',1603,'{"effect": {"leg": "pickup", "status": "order_courier1_assigned", "order_id": 1603, "executor_user_id": 2}, "to_state": "order_courier1_assigned", "entity_id": 1603, "companions": [], "event_name": "assign_executor", "from_state": "order_created", "entity_type": "order", "transition_id": 167}',NULL,NULL,'2026-07-24 11:57:39'),
(141,'svc_courier_01','fsm.instance.completed',141,'order',1603,'{"effect": {"leg": "pickup", "status": "order_courier_has_parcel", "cell_id": 79, "order_id": 1603}, "to_state": "order_courier_has_parcel", "entity_id": 1603, "companions": [{"index": 0, "effect": {"cell_id": 79, "cell_status": "locker_opened"}, "to_state": "locker_opened", "entity_id": 79, "event_name": "locker_open_locker", "from_state": "locker_reserved", "entity_type": "locker", "transition_id": 31}], "event_name": "open_cell", "from_state": "order_courier1_assigned", "entity_type": "order", "transition_id": 38}',NULL,NULL,'2026-07-24 11:57:48'),
(142,'svc_courier_01','fsm.instance.completed',142,'order',1603,'{"effect": {"leg": "pickup", "status": "order_parcel_confirmed", "cell_id": 79, "order_id": 1603, "direction_id": 14}, "to_state": "order_parcel_confirmed", "entity_id": 1603, "companions": [{"index": 0, "effect": {"cell_id": 79, "cell_status": "locker_occupied"}, "to_state": "locker_occupied", "entity_id": 79, "event_name": "locker_close_locker", "from_state": "locker_opened", "entity_type": "locker", "transition_id": 126}], "event_name": "close_cell", "from_state": "order_courier_has_parcel", "entity_type": "order", "transition_id": 36}',NULL,NULL,'2026-07-24 11:57:56'),
(143,'svc_courier_01','fsm.instance.completed',143,'locker',82,'{"effect": {"cell_id": 82, "order_id": 1605, "cell_status": "locker_reserved"}, "to_state": "locker_reserved", "entity_id": 82, "companions": [], "event_name": "locker_reserve_cell", "from_state": "locker_free", "entity_type": "locker", "transition_id": 30}',NULL,NULL,'2026-07-24 12:01:45'),
(144,'svc_courier_01','fsm.instance.completed',144,'locker',81,'{"effect": {"cell_id": 81, "order_id": 1605, "cell_status": "locker_reserved"}, "to_state": "locker_reserved", "entity_id": 81, "companions": [], "event_name": "locker_reserve_cell", "from_state": "locker_free", "entity_type": "locker", "transition_id": 30}',NULL,NULL,'2026-07-24 12:01:48'),
(145,'svc_courier_01','fsm.instance.completed',145,'order',1605,'{"effect": {"leg": "pickup", "status": "order_courier1_assigned", "order_id": 1605, "executor_user_id": 2}, "to_state": "order_courier1_assigned", "entity_id": 1605, "companions": [], "event_name": "assign_executor", "from_state": "order_created", "entity_type": "order", "transition_id": 167}',NULL,NULL,'2026-07-24 12:01:54'),
(146,'svc_courier_01','fsm.instance.completed',146,'order',1605,'{"effect": {"leg": "pickup", "status": "order_courier_has_parcel", "cell_id": 82, "order_id": 1605}, "to_state": "order_courier_has_parcel", "entity_id": 1605, "companions": [{"index": 0, "effect": {"cell_id": 82, "cell_status": "locker_opened"}, "to_state": "locker_opened", "entity_id": 82, "event_name": "locker_open_locker", "from_state": "locker_reserved", "entity_type": "locker", "transition_id": 31}], "event_name": "open_cell", "from_state": "order_courier1_assigned", "entity_type": "order", "transition_id": 38}',NULL,NULL,'2026-07-24 12:02:03'),
(147,'svc_courier_01','fsm.instance.completed',147,'order',1605,'{"effect": {"leg": "pickup", "status": "order_parcel_confirmed", "cell_id": 82, "order_id": 1605, "direction_id": 14}, "to_state": "order_parcel_confirmed", "entity_id": 1605, "companions": [{"index": 0, "effect": {"cell_id": 82, "cell_status": "locker_occupied"}, "to_state": "locker_occupied", "entity_id": 82, "event_name": "locker_close_locker", "from_state": "locker_opened", "entity_type": "locker", "transition_id": 126}], "event_name": "close_cell", "from_state": "order_courier_has_parcel", "entity_type": "order", "transition_id": 36}',NULL,NULL,'2026-07-24 12:02:11'),
(148,'svc_courier_01','fsm.instance.completed',148,'locker',77,'{"effect": {"cell_id": 77, "order_id": 1606, "cell_status": "locker_reserved"}, "to_state": "locker_reserved", "entity_id": 77, "companions": [], "event_name": "locker_reserve_cell", "from_state": "locker_free", "entity_type": "locker", "transition_id": 30}',NULL,NULL,'2026-07-24 12:02:18'),
(149,'svc_courier_01','fsm.instance.completed',149,'locker',93,'{"effect": {"cell_id": 93, "order_id": 1606, "cell_status": "locker_reserved"}, "to_state": "locker_reserved", "entity_id": 93, "companions": [], "event_name": "locker_reserve_cell", "from_state": "locker_free", "entity_type": "locker", "transition_id": 30}',NULL,NULL,'2026-07-24 12:02:21'),
(150,'svc_courier_01','fsm.instance.completed',150,'order',1606,'{"effect": {"leg": "pickup", "status": "order_client_post1", "cell_id": 77, "order_id": 1606}, "to_state": "order_client_post1", "entity_id": 1606, "companions": [{"index": 0, "effect": {"cell_id": 77, "cell_status": "locker_opened"}, "to_state": "locker_opened", "entity_id": 77, "event_name": "locker_open_locker", "from_state": "locker_reserved", "entity_type": "locker", "transition_id": 31}], "event_name": "open_cell", "from_state": "order_created", "entity_type": "order", "transition_id": 136}',NULL,NULL,'2026-07-24 12:02:30'),
(151,'svc_courier_01','fsm.instance.completed',151,'order',1606,'{"effect": {"leg": "pickup", "status": "order_parcel_confirmed", "cell_id": 77, "order_id": 1606, "direction_id": 15}, "to_state": "order_parcel_confirmed", "entity_id": 1606, "companions": [{"index": 0, "effect": {"cell_id": 77, "cell_status": "locker_occupied"}, "to_state": "locker_occupied", "entity_id": 77, "event_name": "locker_close_locker", "from_state": "locker_opened", "entity_type": "locker", "transition_id": 126}], "event_name": "close_cell", "from_state": "order_client_post1", "entity_type": "order", "transition_id": 137}',NULL,NULL,'2026-07-24 12:02:38'),
(152,'svc_courier_01','fsm.instance.completed',152,'locker',80,'{"effect": {"cell_id": 80, "order_id": 1607, "cell_status": "locker_reserved"}, "to_state": "locker_reserved", "entity_id": 80, "companions": [], "event_name": "locker_reserve_cell", "from_state": "locker_free", "entity_type": "locker", "transition_id": 30}',NULL,NULL,'2026-07-24 12:02:44'),
(153,'svc_courier_01','fsm.instance.completed',153,'locker',94,'{"effect": {"cell_id": 94, "order_id": 1607, "cell_status": "locker_reserved"}, "to_state": "locker_reserved", "entity_id": 94, "companions": [], "event_name": "locker_reserve_cell", "from_state": "locker_free", "entity_type": "locker", "transition_id": 30}',NULL,NULL,'2026-07-24 12:02:48'),
(154,'svc_courier_01','fsm.instance.completed',154,'order',1607,'{"effect": {"leg": "pickup", "status": "order_courier1_assigned", "order_id": 1607, "executor_user_id": 7}, "to_state": "order_courier1_assigned", "entity_id": 1607, "companions": [], "event_name": "assign_executor", "from_state": "order_created", "entity_type": "order", "transition_id": 167}',NULL,NULL,'2026-07-24 12:02:53'),
(155,'svc_courier_01','fsm.instance.completed',155,'order',1607,'{"effect": {"leg": "pickup", "status": "order_courier_has_parcel", "cell_id": 80, "order_id": 1607}, "to_state": "order_courier_has_parcel", "entity_id": 1607, "companions": [{"index": 0, "effect": {"cell_id": 80, "cell_status": "locker_opened"}, "to_state": "locker_opened", "entity_id": 80, "event_name": "locker_open_locker", "from_state": "locker_reserved", "entity_type": "locker", "transition_id": 31}], "event_name": "open_cell", "from_state": "order_courier1_assigned", "entity_type": "order", "transition_id": 38}',NULL,NULL,'2026-07-24 12:03:01'),
(156,'svc_courier_01','fsm.instance.completed',156,'order',1607,'{"effect": {"leg": "pickup", "status": "order_parcel_confirmed", "cell_id": 80, "order_id": 1607, "direction_id": 15}, "to_state": "order_parcel_confirmed", "entity_id": 1607, "companions": [{"index": 0, "effect": {"cell_id": 80, "cell_status": "locker_occupied"}, "to_state": "locker_occupied", "entity_id": 80, "event_name": "locker_close_locker", "from_state": "locker_opened", "entity_type": "locker", "transition_id": 126}], "event_name": "close_cell", "from_state": "order_courier_has_parcel", "entity_type": "order", "transition_id": 36}',NULL,NULL,'2026-07-24 12:03:09'),
(157,'svc_courier_01','fsm.instance.completed',157,'locker',70,'{"effect": {"cell_id": 70, "order_id": 1610, "cell_status": "locker_reserved"}, "to_state": "locker_reserved", "entity_id": 70, "companions": [], "event_name": "locker_reserve_cell", "from_state": "locker_free", "entity_type": "locker", "transition_id": 30}',NULL,NULL,'2026-07-24 13:00:31'),
(158,'svc_courier_01','fsm.instance.completed',158,'locker',71,'{"effect": {"cell_id": 71, "order_id": 1610, "cell_status": "locker_reserved"}, "to_state": "locker_reserved", "entity_id": 71, "companions": [], "event_name": "locker_reserve_cell", "from_state": "locker_free", "entity_type": "locker", "transition_id": 30}',NULL,NULL,'2026-07-24 13:00:34'),
(159,'svc_courier_01','fsm.instance.completed',159,'order',1610,'{"effect": {"leg": "pickup", "status": "order_courier1_assigned", "order_id": 1610, "executor_user_id": 2}, "to_state": "order_courier1_assigned", "entity_id": 1610, "companions": [], "event_name": "assign_executor", "from_state": "order_created", "entity_type": "order", "transition_id": 167}',NULL,NULL,'2026-07-24 13:00:39'),
(160,'svc_courier_01','fsm.instance.completed',160,'order',1610,'{"effect": {"leg": "pickup", "status": "order_courier_has_parcel", "cell_id": 70, "order_id": 1610}, "to_state": "order_courier_has_parcel", "entity_id": 1610, "companions": [{"index": 0, "effect": {"cell_id": 70, "cell_status": "locker_opened"}, "to_state": "locker_opened", "entity_id": 70, "event_name": "locker_open_locker", "from_state": "locker_reserved", "entity_type": "locker", "transition_id": 31}], "event_name": "open_cell", "from_state": "order_courier1_assigned", "entity_type": "order", "transition_id": 38}',NULL,NULL,'2026-07-24 13:00:48'),
(161,'svc_courier_01','fsm.instance.completed',161,'order',1610,'{"effect": {"leg": "pickup", "status": "order_parcel_confirmed", "cell_id": 70, "order_id": 1610, "direction_id": 16}, "to_state": "order_parcel_confirmed", "entity_id": 1610, "companions": [{"index": 0, "effect": {"cell_id": 70, "cell_status": "locker_occupied"}, "to_state": "locker_occupied", "entity_id": 70, "event_name": "locker_close_locker", "from_state": "locker_opened", "entity_type": "locker", "transition_id": 126}], "event_name": "close_cell", "from_state": "order_courier_has_parcel", "entity_type": "order", "transition_id": 36}',NULL,NULL,'2026-07-24 13:00:56'),
(162,'svc_courier_01','fsm.instance.completed',162,'locker',1,'{"effect": {"cell_id": 1, "order_id": 1611, "cell_status": "locker_reserved"}, "to_state": "locker_reserved", "entity_id": 1, "companions": [], "event_name": "locker_reserve_cell", "from_state": "locker_free", "entity_type": "locker", "transition_id": 30}',NULL,NULL,'2026-07-24 13:01:02'),
(163,'svc_courier_01','fsm.instance.completed',163,'locker',52,'{"effect": {"cell_id": 52, "order_id": 1611, "cell_status": "locker_reserved"}, "to_state": "locker_reserved", "entity_id": 52, "companions": [], "event_name": "locker_reserve_cell", "from_state": "locker_free", "entity_type": "locker", "transition_id": 30}',NULL,NULL,'2026-07-24 13:01:05'),
(164,'svc_courier_01','fsm.instance.completed',164,'order',1611,'{"effect": {"leg": "pickup", "status": "order_client_post1", "cell_id": 1, "order_id": 1611}, "to_state": "order_client_post1", "entity_id": 1611, "companions": [{"index": 0, "effect": {"cell_id": 1, "cell_status": "locker_opened"}, "to_state": "locker_opened", "entity_id": 1, "event_name": "locker_open_locker", "from_state": "locker_reserved", "entity_type": "locker", "transition_id": 31}], "event_name": "open_cell", "from_state": "order_created", "entity_type": "order", "transition_id": 136}',NULL,NULL,'2026-07-24 13:01:14'),
(165,'svc_courier_01','fsm.instance.completed',165,'order',1611,'{"effect": {"leg": "pickup", "status": "order_parcel_confirmed", "cell_id": 1, "order_id": 1611, "direction_id": 16}, "to_state": "order_parcel_confirmed", "entity_id": 1611, "companions": [{"index": 0, "effect": {"cell_id": 1, "cell_status": "locker_occupied"}, "to_state": "locker_occupied", "entity_id": 1, "event_name": "locker_close_locker", "from_state": "locker_opened", "entity_type": "locker", "transition_id": 126}], "event_name": "close_cell", "from_state": "order_client_post1", "entity_type": "order", "transition_id": 137}',NULL,NULL,'2026-07-24 13:01:21'),
(166,'svc_courier_01','fsm.instance.completed',166,'locker',64,'{"effect": {"cell_id": 64, "order_id": 1612, "cell_status": "locker_reserved"}, "to_state": "locker_reserved", "entity_id": 64, "companions": [], "event_name": "locker_reserve_cell", "from_state": "locker_free", "entity_type": "locker", "transition_id": 30}',NULL,NULL,'2026-07-24 13:01:28'),
(167,'svc_courier_01','fsm.instance.completed',167,'locker',87,'{"effect": {"cell_id": 87, "order_id": 1612, "cell_status": "locker_reserved"}, "to_state": "locker_reserved", "entity_id": 87, "companions": [], "event_name": "locker_reserve_cell", "from_state": "locker_free", "entity_type": "locker", "transition_id": 30}',NULL,NULL,'2026-07-24 13:01:31'),
(168,'svc_courier_01','fsm.instance.completed',168,'order',1612,'{"effect": {"leg": "pickup", "status": "order_courier1_assigned", "order_id": 1612, "executor_user_id": 7}, "to_state": "order_courier1_assigned", "entity_id": 1612, "companions": [], "event_name": "assign_executor", "from_state": "order_created", "entity_type": "order", "transition_id": 167}',NULL,NULL,'2026-07-24 13:01:37'),
(169,'svc_courier_01','fsm.instance.completed',169,'order',1612,'{"effect": {"leg": "pickup", "status": "order_courier_has_parcel", "cell_id": 64, "order_id": 1612}, "to_state": "order_courier_has_parcel", "entity_id": 1612, "companions": [{"index": 0, "effect": {"cell_id": 64, "cell_status": "locker_opened"}, "to_state": "locker_opened", "entity_id": 64, "event_name": "locker_open_locker", "from_state": "locker_reserved", "entity_type": "locker", "transition_id": 31}], "event_name": "open_cell", "from_state": "order_courier1_assigned", "entity_type": "order", "transition_id": 38}',NULL,NULL,'2026-07-24 13:01:46'),
(170,'svc_courier_01','fsm.instance.completed',170,'order',1612,'{"effect": {"leg": "pickup", "status": "order_parcel_confirmed", "cell_id": 64, "order_id": 1612, "direction_id": 17}, "to_state": "order_parcel_confirmed", "entity_id": 1612, "companions": [{"index": 0, "effect": {"cell_id": 64, "cell_status": "locker_occupied"}, "to_state": "locker_occupied", "entity_id": 64, "event_name": "locker_close_locker", "from_state": "locker_opened", "entity_type": "locker", "transition_id": 126}], "event_name": "close_cell", "from_state": "order_courier_has_parcel", "entity_type": "order", "transition_id": 36}',NULL,NULL,'2026-07-24 13:01:54'),
(171,'svc_courier_01','fsm.instance.completed',171,'locker',67,'{"effect": {"cell_id": 67, "order_id": 1613, "cell_status": "locker_reserved"}, "to_state": "locker_reserved", "entity_id": 67, "companions": [], "event_name": "locker_reserve_cell", "from_state": "locker_free", "entity_type": "locker", "transition_id": 30}',NULL,NULL,'2026-07-24 13:02:01'),
(172,'svc_courier_01','fsm.instance.completed',172,'locker',90,'{"effect": {"cell_id": 90, "order_id": 1613, "cell_status": "locker_reserved"}, "to_state": "locker_reserved", "entity_id": 90, "companions": [], "event_name": "locker_reserve_cell", "from_state": "locker_free", "entity_type": "locker", "transition_id": 30}',NULL,NULL,'2026-07-24 13:02:04'),
(173,'svc_courier_01','fsm.instance.completed',173,'order',1613,'{"effect": {"leg": "pickup", "status": "order_client_post1", "cell_id": 67, "order_id": 1613}, "to_state": "order_client_post1", "entity_id": 1613, "companions": [{"index": 0, "effect": {"cell_id": 67, "cell_status": "locker_opened"}, "to_state": "locker_opened", "entity_id": 67, "event_name": "locker_open_locker", "from_state": "locker_reserved", "entity_type": "locker", "transition_id": 31}], "event_name": "open_cell", "from_state": "order_created", "entity_type": "order", "transition_id": 136}',NULL,NULL,'2026-07-24 13:02:12'),
(174,'svc_courier_01','fsm.instance.completed',174,'order',1613,'{"effect": {"leg": "pickup", "status": "order_parcel_confirmed", "cell_id": 67, "order_id": 1613, "direction_id": 17}, "to_state": "order_parcel_confirmed", "entity_id": 1613, "companions": [{"index": 0, "effect": {"cell_id": 67, "cell_status": "locker_occupied"}, "to_state": "locker_occupied", "entity_id": 67, "event_name": "locker_close_locker", "from_state": "locker_opened", "entity_type": "locker", "transition_id": 126}], "event_name": "close_cell", "from_state": "order_client_post1", "entity_type": "order", "transition_id": 137}',NULL,NULL,'2026-07-24 13:02:19'),
(175,'svc_courier_01','fsm.instance.completed',175,'driver_reservations',53,'{"effect": {"status": "reservation_loading", "direction_id": 16, "reservation_id": 53}, "to_state": "reservation_loading", "entity_id": 53, "companions": [], "event_name": "start_loading", "from_state": "reservation_active", "entity_type": "driver_reservations", "transition_id": 145}',NULL,NULL,'2026-07-24 13:02:29'),
(176,'svc_courier_01','fsm.instance.completed',176,'order',1610,'{"effect": {"leg": "pickup", "status": "order_parcel_submitted", "cell_id": 70, "order_id": 1610}, "to_state": "order_parcel_submitted", "entity_id": 1610, "companions": [{"index": 0, "effect": {"cell_id": 70, "cell_status": "locker_opened"}, "to_state": "locker_opened", "entity_id": 70, "event_name": "locker_open_locker", "from_state": "locker_occupied", "entity_type": "locker", "transition_id": 62}], "event_name": "open_cell", "from_state": "order_parcel_confirmed", "entity_type": "order", "transition_id": 29}',NULL,NULL,'2026-07-24 13:02:37'),
(177,'svc_courier_01','fsm.instance.completed',177,'order',1610,'{"effect": {"leg": "pickup", "status": "order_picked_up_from_post1", "cell_id": 70, "order_id": 1610}, "to_state": "order_picked_up_from_post1", "entity_id": 1610, "companions": [{"index": 0, "effect": {"cell_id": 70, "cell_status": "locker_closed_empty"}, "to_state": "locker_closed_empty", "entity_id": 70, "event_name": "locker_close_pickup", "from_state": "locker_opened", "entity_type": "locker", "transition_id": 127}], "event_name": "close_cell", "from_state": "order_parcel_submitted", "entity_type": "order", "transition_id": 74}',NULL,NULL,'2026-07-24 13:02:43'),
(178,'svc_courier_01','fsm.instance.completed',178,'order',1611,'{"effect": {"leg": "pickup", "status": "order_parcel_submitted", "cell_id": 1, "order_id": 1611}, "to_state": "order_parcel_submitted", "entity_id": 1611, "companions": [{"index": 0, "effect": {"cell_id": 1, "cell_status": "locker_opened"}, "to_state": "locker_opened", "entity_id": 1, "event_name": "locker_open_locker", "from_state": "locker_occupied", "entity_type": "locker", "transition_id": 62}], "event_name": "open_cell", "from_state": "order_parcel_confirmed", "entity_type": "order", "transition_id": 29}',NULL,NULL,'2026-07-24 13:02:52'),
(179,'svc_courier_01','fsm.instance.completed',179,'order',1611,'{"effect": {"leg": "pickup", "status": "order_picked_up_from_post1", "cell_id": 1, "order_id": 1611}, "to_state": "order_picked_up_from_post1", "entity_id": 1611, "companions": [{"index": 0, "effect": {"cell_id": 1, "cell_status": "locker_closed_empty"}, "to_state": "locker_closed_empty", "entity_id": 1, "event_name": "locker_close_pickup", "from_state": "locker_opened", "entity_type": "locker", "transition_id": 127}], "event_name": "close_cell", "from_state": "order_parcel_submitted", "entity_type": "order", "transition_id": 74}',NULL,NULL,'2026-07-24 13:02:58'),
(180,'svc_courier_01','fsm.instance.completed',180,'order',1612,'{"effect": {"leg": "pickup", "status": "order_parcel_submitted", "cell_id": 64, "order_id": 1612}, "to_state": "order_parcel_submitted", "entity_id": 1612, "companions": [{"index": 0, "effect": {"cell_id": 64, "cell_status": "locker_opened"}, "to_state": "locker_opened", "entity_id": 64, "event_name": "locker_open_locker", "from_state": "locker_occupied", "entity_type": "locker", "transition_id": 62}], "event_name": "open_cell", "from_state": "order_parcel_confirmed", "entity_type": "order", "transition_id": 29}',NULL,NULL,'2026-07-24 13:03:06'),
(181,'svc_courier_01','fsm.instance.completed',181,'order',1612,'{"effect": {"leg": "pickup", "status": "order_picked_up_from_post1", "cell_id": 64, "order_id": 1612}, "to_state": "order_picked_up_from_post1", "entity_id": 1612, "companions": [{"index": 0, "effect": {"cell_id": 64, "cell_status": "locker_closed_empty"}, "to_state": "locker_closed_empty", "entity_id": 64, "event_name": "locker_close_pickup", "from_state": "locker_opened", "entity_type": "locker", "transition_id": 127}], "event_name": "close_cell", "from_state": "order_parcel_submitted", "entity_type": "order", "transition_id": 74}',NULL,NULL,'2026-07-24 13:03:16'),
(182,'svc_courier_01','fsm.instance.completed',182,'order',1613,'{"effect": {"leg": "pickup", "status": "order_parcel_submitted", "cell_id": 67, "order_id": 1613}, "to_state": "order_parcel_submitted", "entity_id": 1613, "companions": [{"index": 0, "effect": {"cell_id": 67, "cell_status": "locker_opened"}, "to_state": "locker_opened", "entity_id": 67, "event_name": "locker_open_locker", "from_state": "locker_occupied", "entity_type": "locker", "transition_id": 62}], "event_name": "open_cell", "from_state": "order_parcel_confirmed", "entity_type": "order", "transition_id": 29}',NULL,NULL,'2026-07-24 13:03:24'),
(183,'svc_courier_01','fsm.instance.completed',183,'order',1613,'{"effect": {"leg": "pickup", "status": "order_picked_up_from_post1", "cell_id": 67, "order_id": 1613}, "to_state": "order_picked_up_from_post1", "entity_id": 1613, "companions": [{"index": 0, "effect": {"cell_id": 67, "cell_status": "locker_closed_empty"}, "to_state": "locker_closed_empty", "entity_id": 67, "event_name": "locker_close_pickup", "from_state": "locker_opened", "entity_type": "locker", "transition_id": 127}], "event_name": "close_cell", "from_state": "order_parcel_submitted", "entity_type": "order", "transition_id": 74}',NULL,NULL,'2026-07-24 13:03:31'),
(184,'svc_courier_01','fsm.instance.completed',184,'driver_reservations',53,'{"effect": {"status": "reservation_completed", "direction_id": 16, "reservation_id": 53}, "to_state": "reservation_completed", "entity_id": 53, "companions": [], "event_name": "complete_loading", "from_state": "reservation_loading", "entity_type": "driver_reservations", "transition_id": 146}',NULL,NULL,'2026-07-24 13:03:40'),
(185,'svc_courier_01','fsm.instance.completed',185,'order',1610,'{"effect": {"status": "order_in_transit_to_post2", "order_id": 1610}, "to_state": "order_in_transit_to_post2", "entity_id": 1610, "companions": [], "event_name": "start_order_transit", "from_state": "order_picked_up_from_post1", "entity_type": "order", "transition_id": 75}',NULL,NULL,'2026-07-24 13:03:49'),
(186,'svc_courier_01','fsm.instance.completed',186,'order',1611,'{"effect": {"status": "order_in_transit_to_post2", "order_id": 1611}, "to_state": "order_in_transit_to_post2", "entity_id": 1611, "companions": [], "event_name": "start_order_transit", "from_state": "order_picked_up_from_post1", "entity_type": "order", "transition_id": 75}',NULL,NULL,'2026-07-24 13:03:54'),
(187,'svc_courier_01','fsm.instance.completed',187,'order',1612,'{"effect": {"status": "order_in_transit_to_post2", "order_id": 1612}, "to_state": "order_in_transit_to_post2", "entity_id": 1612, "companions": [], "event_name": "start_order_transit", "from_state": "order_picked_up_from_post1", "entity_type": "order", "transition_id": 75}',NULL,NULL,'2026-07-24 13:03:59'),
(188,'svc_courier_01','fsm.instance.completed',188,'order',1613,'{"effect": {"status": "order_in_transit_to_post2", "order_id": 1613}, "to_state": "order_in_transit_to_post2", "entity_id": 1613, "companions": [], "event_name": "start_order_transit", "from_state": "order_picked_up_from_post1", "entity_type": "order", "transition_id": 75}',NULL,NULL,'2026-07-24 13:04:03'),
(189,'svc_courier_01','fsm.instance.completed',189,'trip',61,'{"effect": {"status": "trip_in_progress", "trip_id": 61}, "to_state": "trip_in_progress", "entity_id": 61, "companions": [], "event_name": "start_trip", "from_state": "trip_assigned", "entity_type": "trip", "transition_id": 57}',NULL,NULL,'2026-07-24 13:04:07'),
(190,'svc_courier_01','fsm.instance.completed',190,'order',1610,'{"effect": {"leg": "delivery", "status": "order_arrived_at_post2", "cell_id": 71, "order_id": 1610}, "to_state": "order_arrived_at_post2", "entity_id": 1610, "companions": [{"index": 0, "effect": {"cell_id": 71, "cell_status": "locker_opened"}, "to_state": "locker_opened", "entity_id": 71, "event_name": "locker_open_locker", "from_state": "locker_reserved", "entity_type": "locker", "transition_id": 31}], "event_name": "open_cell", "from_state": "order_in_transit_to_post2", "entity_type": "order", "transition_id": 76}',NULL,NULL,'2026-07-24 13:04:16'),
(191,'svc_courier_01','fsm.instance.completed',191,'order',1610,'{"effect": {"leg": "delivery", "status": "order_parcel_confirmed_post2", "cell_id": 71, "order_id": 1610}, "to_state": "order_parcel_confirmed_post2", "entity_id": 1610, "companions": [{"index": 0, "effect": {"cell_id": 71, "cell_status": "locker_occupied"}, "to_state": "locker_occupied", "entity_id": 71, "event_name": "locker_close_locker", "from_state": "locker_opened", "entity_type": "locker", "transition_id": 126}], "event_name": "close_cell", "from_state": "order_arrived_at_post2", "entity_type": "order", "transition_id": 77}',NULL,NULL,'2026-07-24 13:04:22'),
(192,'svc_courier_01','fsm.instance.completed',192,'order',1611,'{"effect": {"leg": "delivery", "status": "order_arrived_at_post2", "cell_id": 52, "order_id": 1611}, "to_state": "order_arrived_at_post2", "entity_id": 1611, "companions": [{"index": 0, "effect": {"cell_id": 52, "cell_status": "locker_opened"}, "to_state": "locker_opened", "entity_id": 52, "event_name": "locker_open_locker", "from_state": "locker_reserved", "entity_type": "locker", "transition_id": 31}], "event_name": "open_cell", "from_state": "order_in_transit_to_post2", "entity_type": "order", "transition_id": 76}',NULL,NULL,'2026-07-24 13:04:30'),
(193,'svc_courier_01','fsm.instance.completed',193,'order',1611,'{"effect": {"leg": "delivery", "status": "order_parcel_confirmed_post2", "cell_id": 52, "order_id": 1611}, "to_state": "order_parcel_confirmed_post2", "entity_id": 1611, "companions": [{"index": 0, "effect": {"cell_id": 52, "cell_status": "locker_occupied"}, "to_state": "locker_occupied", "entity_id": 52, "event_name": "locker_close_locker", "from_state": "locker_opened", "entity_type": "locker", "transition_id": 126}], "event_name": "close_cell", "from_state": "order_arrived_at_post2", "entity_type": "order", "transition_id": 77}',NULL,NULL,'2026-07-24 13:04:36'),
(194,'svc_courier_01','fsm.instance.completed',194,'order',1612,'{"effect": {"leg": "delivery", "status": "order_arrived_at_post2", "cell_id": 87, "order_id": 1612}, "to_state": "order_arrived_at_post2", "entity_id": 1612, "companions": [{"index": 0, "effect": {"cell_id": 87, "cell_status": "locker_opened"}, "to_state": "locker_opened", "entity_id": 87, "event_name": "locker_open_locker", "from_state": "locker_reserved", "entity_type": "locker", "transition_id": 31}], "event_name": "open_cell", "from_state": "order_in_transit_to_post2", "entity_type": "order", "transition_id": 76}',NULL,NULL,'2026-07-24 13:04:44'),
(195,'svc_courier_01','fsm.instance.completed',195,'order',1612,'{"effect": {"leg": "delivery", "status": "order_parcel_confirmed_post2", "cell_id": 87, "order_id": 1612}, "to_state": "order_parcel_confirmed_post2", "entity_id": 1612, "companions": [{"index": 0, "effect": {"cell_id": 87, "cell_status": "locker_occupied"}, "to_state": "locker_occupied", "entity_id": 87, "event_name": "locker_close_locker", "from_state": "locker_opened", "entity_type": "locker", "transition_id": 126}], "event_name": "close_cell", "from_state": "order_arrived_at_post2", "entity_type": "order", "transition_id": 77}',NULL,NULL,'2026-07-24 13:04:50'),
(196,'svc_courier_01','fsm.instance.completed',196,'order',1613,'{"effect": {"leg": "delivery", "status": "order_arrived_at_post2", "cell_id": 90, "order_id": 1613}, "to_state": "order_arrived_at_post2", "entity_id": 1613, "companions": [{"index": 0, "effect": {"cell_id": 90, "cell_status": "locker_opened"}, "to_state": "locker_opened", "entity_id": 90, "event_name": "locker_open_locker", "from_state": "locker_reserved", "entity_type": "locker", "transition_id": 31}], "event_name": "open_cell", "from_state": "order_in_transit_to_post2", "entity_type": "order", "transition_id": 76}',NULL,NULL,'2026-07-24 13:04:58'),
(197,'svc_courier_01','fsm.instance.completed',197,'order',1613,'{"effect": {"leg": "delivery", "status": "order_parcel_confirmed_post2", "cell_id": 90, "order_id": 1613}, "to_state": "order_parcel_confirmed_post2", "entity_id": 1613, "companions": [{"index": 0, "effect": {"cell_id": 90, "cell_status": "locker_occupied"}, "to_state": "locker_occupied", "entity_id": 90, "event_name": "locker_close_locker", "from_state": "locker_opened", "entity_type": "locker", "transition_id": 126}], "event_name": "close_cell", "from_state": "order_arrived_at_post2", "entity_type": "order", "transition_id": 77}',NULL,NULL,'2026-07-24 13:05:04'),
(198,'svc_courier_01','fsm.instance.completed',198,'trip',61,'{"effect": {"status": "trip_completed", "trip_id": 61}, "to_state": "trip_completed", "entity_id": 61, "companions": [], "event_name": "complete_trip", "from_state": "trip_in_progress", "entity_type": "trip", "transition_id": 135}',NULL,NULL,'2026-07-24 13:05:12'),
(199,'svc_courier_01','fsm.instance.completed',199,'order',1610,'{"effect": {"leg": "delivery", "status": "order_courier2_assigned", "order_id": 1610, "executor_user_id": 6}, "to_state": "order_courier2_assigned", "entity_id": 1610, "companions": [], "event_name": "assign_executor", "from_state": "order_parcel_confirmed_post2", "entity_type": "order", "transition_id": 168}',NULL,NULL,'2026-07-24 13:05:18'),
(200,'svc_courier_01','fsm.instance.completed',200,'order',1610,'{"effect": {"leg": "delivery", "status": "order_courier2_has_parcel", "cell_id": 71, "order_id": 1610}, "to_state": "order_courier2_has_parcel", "entity_id": 1610, "companions": [{"index": 0, "effect": {"cell_id": 71, "cell_status": "locker_opened"}, "to_state": "locker_opened", "entity_id": 71, "event_name": "locker_open_locker", "from_state": "locker_occupied", "entity_type": "locker", "transition_id": 62}], "event_name": "open_cell", "from_state": "order_courier2_assigned", "entity_type": "order", "transition_id": 83}',NULL,NULL,'2026-07-24 13:05:27');
INSERT INTO `platform_events` (`id`,`service_id`,`event_type`,`instance_id`,`entity_type`,`entity_id`,`payload_json`,`correlation_id`,`client_request_id`,`created_at`) VALUES
(201,'svc_courier_01','fsm.instance.completed',201,'order',1610,'{"effect": {"leg": "delivery", "status": "order_courier2_parcel_delivered", "cell_id": 71, "order_id": 1610}, "to_state": "order_courier2_parcel_delivered", "entity_id": 1610, "companions": [{"index": 0, "effect": {"cell_id": 71, "cell_status": "locker_closed_empty"}, "to_state": "locker_closed_empty", "entity_id": 71, "event_name": "locker_close_pickup", "from_state": "locker_opened", "entity_type": "locker", "transition_id": 127}], "event_name": "close_cell", "from_state": "order_courier2_has_parcel", "entity_type": "order", "transition_id": 84}',NULL,NULL,'2026-07-24 13:05:34'),
(202,'svc_courier_01','fsm.instance.completed',202,'order',1610,'{"effect": {"status": "order_completed", "order_id": 1610, "delivery_code_used": true}, "to_state": "order_completed", "entity_id": 1610, "companions": [], "event_name": "confirm_courier2_delivery", "from_state": "order_courier2_parcel_delivered", "entity_type": "order", "transition_id": 125}',NULL,NULL,'2026-07-24 13:05:43'),
(203,'svc_courier_01','fsm.instance.completed',203,'order',1611,'{"effect": {"leg": "delivery", "status": "order_courier2_assigned", "order_id": 1611, "executor_user_id": 8}, "to_state": "order_courier2_assigned", "entity_id": 1611, "companions": [], "event_name": "assign_executor", "from_state": "order_parcel_confirmed_post2", "entity_type": "order", "transition_id": 168}',NULL,NULL,'2026-07-24 13:05:48'),
(204,'svc_courier_01','fsm.instance.completed',204,'order',1611,'{"effect": {"leg": "delivery", "status": "order_courier2_has_parcel", "cell_id": 52, "order_id": 1611}, "to_state": "order_courier2_has_parcel", "entity_id": 1611, "companions": [{"index": 0, "effect": {"cell_id": 52, "cell_status": "locker_opened"}, "to_state": "locker_opened", "entity_id": 52, "event_name": "locker_open_locker", "from_state": "locker_occupied", "entity_type": "locker", "transition_id": 62}], "event_name": "open_cell", "from_state": "order_courier2_assigned", "entity_type": "order", "transition_id": 83}',NULL,NULL,'2026-07-24 13:05:56'),
(205,'svc_courier_01','fsm.instance.completed',205,'order',1611,'{"effect": {"leg": "delivery", "status": "order_courier2_parcel_delivered", "cell_id": 52, "order_id": 1611}, "to_state": "order_courier2_parcel_delivered", "entity_id": 1611, "companions": [{"index": 0, "effect": {"cell_id": 52, "cell_status": "locker_closed_empty"}, "to_state": "locker_closed_empty", "entity_id": 52, "event_name": "locker_close_pickup", "from_state": "locker_opened", "entity_type": "locker", "transition_id": 127}], "event_name": "close_cell", "from_state": "order_courier2_has_parcel", "entity_type": "order", "transition_id": 84}',NULL,NULL,'2026-07-24 13:06:03'),
(206,'svc_courier_01','fsm.instance.completed',206,'order',1611,'{"effect": {"status": "order_completed", "order_id": 1611, "delivery_code_used": true}, "to_state": "order_completed", "entity_id": 1611, "companions": [], "event_name": "confirm_courier2_delivery", "from_state": "order_courier2_parcel_delivered", "entity_type": "order", "transition_id": 125}',NULL,NULL,'2026-07-24 13:06:10'),
(207,'svc_courier_01','fsm.instance.completed',207,'order',1612,'{"effect": {"leg": "delivery", "status": "order_delivered_to_client", "cell_id": 87, "order_id": 1612}, "to_state": "order_delivered_to_client", "entity_id": 1612, "companions": [{"index": 0, "effect": {"cell_id": 87, "cell_status": "locker_opened"}, "to_state": "locker_opened", "entity_id": 87, "event_name": "locker_open_locker", "from_state": "locker_occupied", "entity_type": "locker", "transition_id": 62}], "event_name": "open_cell", "from_state": "order_parcel_confirmed_post2", "entity_type": "order", "transition_id": 80}',NULL,NULL,'2026-07-24 13:06:18'),
(208,'svc_courier_01','fsm.instance.completed',208,'order',1612,'{"effect": {"leg": "delivery", "status": "order_completed", "cell_id": 87, "order_id": 1612}, "to_state": "order_completed", "entity_id": 1612, "companions": [{"index": 0, "effect": {"cell_id": 87, "cell_status": "locker_closed_empty"}, "to_state": "locker_closed_empty", "entity_id": 87, "event_name": "locker_close_pickup", "from_state": "locker_opened", "entity_type": "locker", "transition_id": 127}], "event_name": "close_cell", "from_state": "order_delivered_to_client", "entity_type": "order", "transition_id": 81}',NULL,NULL,'2026-07-24 13:06:25'),
(209,'svc_courier_01','fsm.instance.completed',209,'order',1613,'{"effect": {"leg": "delivery", "status": "order_delivered_to_client", "cell_id": 90, "order_id": 1613}, "to_state": "order_delivered_to_client", "entity_id": 1613, "companions": [{"index": 0, "effect": {"cell_id": 90, "cell_status": "locker_opened"}, "to_state": "locker_opened", "entity_id": 90, "event_name": "locker_open_locker", "from_state": "locker_occupied", "entity_type": "locker", "transition_id": 62}], "event_name": "open_cell", "from_state": "order_parcel_confirmed_post2", "entity_type": "order", "transition_id": 80}',NULL,NULL,'2026-07-24 13:06:33'),
(210,'svc_courier_01','fsm.instance.completed',210,'order',1613,'{"effect": {"leg": "delivery", "status": "order_completed", "cell_id": 90, "order_id": 1613}, "to_state": "order_completed", "entity_id": 1613, "companions": [{"index": 0, "effect": {"cell_id": 90, "cell_status": "locker_closed_empty"}, "to_state": "locker_closed_empty", "entity_id": 90, "event_name": "locker_close_pickup", "from_state": "locker_opened", "entity_type": "locker", "transition_id": 127}], "event_name": "close_cell", "from_state": "order_delivered_to_client", "entity_type": "order", "transition_id": 81}',NULL,NULL,'2026-07-24 13:06:40'),
(211,'svc_courier_01','fsm.instance.completed',211,'locker',46,'{"effect": {"cell_id": 46, "order_id": 1614, "cell_status": "locker_reserved"}, "to_state": "locker_reserved", "entity_id": 46, "companions": [], "event_name": "locker_reserve_cell", "from_state": "locker_free", "entity_type": "locker", "transition_id": 30}',NULL,NULL,'2026-07-24 16:15:17'),
(212,'svc_courier_01','fsm.instance.completed',212,'locker',55,'{"effect": {"cell_id": 55, "order_id": 1614, "cell_status": "locker_reserved"}, "to_state": "locker_reserved", "entity_id": 55, "companions": [], "event_name": "locker_reserve_cell", "from_state": "locker_free", "entity_type": "locker", "transition_id": 30}',NULL,NULL,'2026-07-24 16:15:21'),
(213,'svc_courier_01','fsm.instance.completed',213,'order',1614,'{"effect": {"leg": "pickup", "status": "order_courier1_assigned", "order_id": 1614, "executor_user_id": 2}, "to_state": "order_courier1_assigned", "entity_id": 1614, "companions": [], "event_name": "assign_executor", "from_state": "order_created", "entity_type": "order", "transition_id": 167}',NULL,NULL,'2026-07-24 16:15:26'),
(214,'svc_courier_01','fsm.instance.completed',214,'locker',47,'{"effect": {"cell_id": 47, "order_id": 1615, "cell_status": "locker_reserved"}, "to_state": "locker_reserved", "entity_id": 47, "companions": [], "event_name": "locker_reserve_cell", "from_state": "locker_free", "entity_type": "locker", "transition_id": 30}',NULL,NULL,'2026-07-24 16:25:29'),
(215,'svc_courier_01','fsm.instance.completed',215,'locker',56,'{"effect": {"cell_id": 56, "order_id": 1615, "cell_status": "locker_reserved"}, "to_state": "locker_reserved", "entity_id": 56, "companions": [], "event_name": "locker_reserve_cell", "from_state": "locker_free", "entity_type": "locker", "transition_id": 30}',NULL,NULL,'2026-07-24 16:25:34'),
(216,'svc_courier_01','fsm.instance.completed',216,'order',1615,'{"effect": {"leg": "pickup", "status": "order_courier1_assigned", "order_id": 1615, "executor_user_id": 2}, "to_state": "order_courier1_assigned", "entity_id": 1615, "companions": [], "event_name": "assign_executor", "from_state": "order_created", "entity_type": "order", "transition_id": 167}',NULL,NULL,'2026-07-24 16:25:41'),
(217,'svc_courier_01','fsm.instance.completed',217,'locker',48,'{"effect": {"cell_id": 48, "order_id": 1616, "cell_status": "locker_reserved"}, "to_state": "locker_reserved", "entity_id": 48, "companions": [], "event_name": "locker_reserve_cell", "from_state": "locker_free", "entity_type": "locker", "transition_id": 30}',NULL,NULL,'2026-07-26 09:48:50'),
(218,'svc_courier_01','fsm.instance.completed',218,'locker',57,'{"effect": {"cell_id": 57, "order_id": 1616, "cell_status": "locker_reserved"}, "to_state": "locker_reserved", "entity_id": 57, "companions": [], "event_name": "locker_reserve_cell", "from_state": "locker_free", "entity_type": "locker", "transition_id": 30}',NULL,NULL,'2026-07-26 09:48:55'),
(219,'svc_courier_01','fsm.instance.completed',219,'order',1616,'{"effect": {"leg": "pickup", "status": "order_courier1_assigned", "order_id": 1616, "executor_user_id": 2}, "to_state": "order_courier1_assigned", "entity_id": 1616, "companions": [], "event_name": "assign_executor", "from_state": "order_created", "entity_type": "order", "transition_id": 167}',NULL,NULL,'2026-07-26 09:49:03'),
(220,'svc_courier_01','fsm.instance.completed',220,'locker',65,'{"effect": {"cell_id": 65, "order_id": 1617, "cell_status": "locker_reserved"}, "to_state": "locker_reserved", "entity_id": 65, "companions": [], "event_name": "locker_reserve_cell", "from_state": "locker_free", "entity_type": "locker", "transition_id": 30}',NULL,NULL,'2026-07-26 11:05:24'),
(221,'svc_courier_01','fsm.instance.completed',221,'locker',88,'{"effect": {"cell_id": 88, "order_id": 1617, "cell_status": "locker_reserved"}, "to_state": "locker_reserved", "entity_id": 88, "companions": [], "event_name": "locker_reserve_cell", "from_state": "locker_free", "entity_type": "locker", "transition_id": 30}',NULL,NULL,'2026-07-26 11:05:32'),
(222,'svc_courier_01','fsm.instance.completed',222,'order',1617,'{"effect": {"leg": "pickup", "status": "order_courier1_assigned", "order_id": 1617, "executor_user_id": 2}, "to_state": "order_courier1_assigned", "entity_id": 1617, "companions": [], "event_name": "assign_executor", "from_state": "order_created", "entity_type": "order", "transition_id": 167}',NULL,NULL,'2026-07-26 11:05:43'),
(223,'svc_courier_01','fsm.instance.completed',223,'locker',66,'{"effect": {"cell_id": 66, "request_id": 345, "cell_status": "locker_reserved"}, "to_state": "locker_reserved", "entity_id": 66, "companions": [], "event_name": "locker_reserve_cell", "from_state": "locker_free", "entity_type": "locker", "transition_id": 30}',NULL,NULL,'2026-07-26 12:36:01'),
(224,'svc_courier_01','fsm.instance.completed',224,'locker',89,'{"effect": {"cell_id": 89, "request_id": 345, "cell_status": "locker_reserved"}, "to_state": "locker_reserved", "entity_id": 89, "companions": [], "event_name": "locker_reserve_cell", "from_state": "locker_free", "entity_type": "locker", "transition_id": 30}',NULL,NULL,'2026-07-26 12:36:05'),
(225,'svc_courier_01','fsm.instance.completed',225,'order',1618,'{"effect": {"leg": "pickup", "status": "order_courier1_assigned", "order_id": 1618, "executor_user_id": 2}, "to_state": "order_courier1_assigned", "entity_id": 1618, "companions": [], "event_name": "assign_executor", "from_state": "order_created", "entity_type": "order", "transition_id": 167}',NULL,NULL,'2026-07-26 12:36:16'),
(226,'svc_courier_01','fsm.instance.completed',226,'locker',2,'{"effect": {"cell_id": 2, "request_id": 346, "cell_status": "locker_reserved"}, "to_state": "locker_reserved", "entity_id": 2, "companions": [], "event_name": "locker_reserve_cell", "from_state": "locker_free", "entity_type": "locker", "transition_id": 30}',NULL,NULL,'2026-07-26 14:28:25'),
(227,'svc_courier_01','fsm.instance.completed',227,'locker',53,'{"effect": {"cell_id": 53, "request_id": 346, "cell_status": "locker_reserved"}, "to_state": "locker_reserved", "entity_id": 53, "companions": [], "event_name": "locker_reserve_cell", "from_state": "locker_free", "entity_type": "locker", "transition_id": 30}',NULL,NULL,'2026-07-26 14:28:31'),
(228,'svc_courier_01','fsm.instance.completed',228,'order',1619,'{"effect": {"leg": "pickup", "status": "order_courier1_assigned", "order_id": 1619, "executor_user_id": 2}, "to_state": "order_courier1_assigned", "entity_id": 1619, "companions": [], "event_name": "assign_executor", "from_state": "order_created", "entity_type": "order", "transition_id": 167}',NULL,NULL,'2026-07-26 14:28:45'),
(229,'svc_courier_01','fsm.instance.completed',229,'locker',3,'{"effect": {"cell_id": 3, "request_id": 347, "cell_status": "locker_reserved"}, "to_state": "locker_reserved", "entity_id": 3, "companions": [], "event_name": "locker_reserve_cell", "from_state": "locker_free", "entity_type": "locker", "transition_id": 30}',NULL,NULL,'2026-07-27 09:31:09'),
(230,'svc_courier_01','fsm.instance.completed',230,'locker',54,'{"effect": {"cell_id": 54, "request_id": 347, "cell_status": "locker_reserved"}, "to_state": "locker_reserved", "entity_id": 54, "companions": [], "event_name": "locker_reserve_cell", "from_state": "locker_free", "entity_type": "locker", "transition_id": 30}',NULL,NULL,'2026-07-27 09:31:15'),
(231,'svc_courier_01','fsm.instance.completed',231,'order',1620,'{"effect": {"leg": "pickup", "status": "order_courier1_assigned", "order_id": 1620, "executor_user_id": 2}, "to_state": "order_courier1_assigned", "entity_id": 1620, "companions": [], "event_name": "assign_executor", "from_state": "order_created", "entity_type": "order", "transition_id": 167}',NULL,NULL,'2026-07-27 09:31:29');
/*!40000 ALTER TABLE `platform_events` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table `platform_outbox`
--

DROP TABLE IF EXISTS `platform_outbox`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `platform_outbox` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `service_id` varchar(64) NOT NULL,
  `channel` varchar(64) NOT NULL,
  `destination` varchar(1024) NOT NULL,
  `event_type` varchar(128) NOT NULL,
  `payload_json` json DEFAULT NULL,
  `status` varchar(32) NOT NULL DEFAULT 'PENDING',
  `attempts` int NOT NULL DEFAULT '0',
  `next_attempt_at` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `idempotency_key` varchar(128) DEFAULT NULL,
  `last_error` text,
  `created_at` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `sent_at` datetime DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `uq_outbox_idem` (`service_id`,`idempotency_key`),
  KEY `idx_outbox_poll` (`status`,`next_attempt_at`,`id`)
) ENGINE=InnoDB AUTO_INCREMENT=14 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `platform_outbox`
--

LOCK TABLES `platform_outbox` WRITE;
/*!40000 ALTER TABLE `platform_outbox` DISABLE KEYS */;
INSERT INTO `platform_outbox` (`id`,`service_id`,`channel`,`destination`,`event_type`,`payload_json`,`status`,`attempts`,`next_attempt_at`,`idempotency_key`,`last_error`,`created_at`,`sent_at`) VALUES
(1,'svc_courier_01','telegram','774531703','order.progress.order_created','{"text": "Заказ №1614 успешно создан.", "user_id": 3, "audience": "client", "order_id": 1614, "to_state": "order_created"}','SENT',1,'2026-07-24 16:15:11','tg:1614:order_created:client',NULL,'2026-07-24 16:15:11','2026-07-24 16:23:10'),
(2,'svc_courier_01','telegram','774531703','order.progress.order_created','{"text": "Заказ №1615 успешно создан.", "user_id": 3, "audience": "client", "order_id": 1615, "to_state": "order_created"}','SENT',1,'2026-07-24 16:25:23','tg:1615:order_created:client',NULL,'2026-07-24 16:25:23','2026-07-24 16:25:31'),
(3,'svc_courier_01','telegram','774531703','order.progress.order_courier1_assigned','{"text": "Заказ №1615 принял курьер User 2. Ожидайте: в ближайшие 30 минут курьер приедет забрать посылку.", "user_id": 3, "audience": "client", "order_id": 1615, "to_state": "order_courier1_assigned"}','SENT',1,'2026-07-24 16:25:41','tg:1615:order_courier1_assigned:client:i216',NULL,'2026-07-24 16:25:41','2026-07-24 16:25:44'),
(4,'svc_courier_01','telegram','774531703','order.progress.order_created','{"text": "Заказ №1616 успешно создан.", "user_id": 3, "audience": "client", "order_id": 1616, "to_state": "order_created"}','SENT',1,'2026-07-26 09:48:44','tg:1616:order_created:client',NULL,'2026-07-26 09:48:44','2026-07-26 09:48:52'),
(5,'svc_courier_01','telegram','774531703','order.progress.order_courier1_assigned','{"text": "Заказ №1616 принял курьер User 2. Ожидайте: в ближайшие 30 минут курьер приедет забрать посылку.", "user_id": 3, "audience": "client", "order_id": 1616, "to_state": "order_courier1_assigned"}','SENT',1,'2026-07-26 09:49:03','tg:1616:order_courier1_assigned:client:i219',NULL,'2026-07-26 09:49:03','2026-07-26 09:49:05'),
(6,'svc_courier_01','telegram','774531703','order.progress.order_created','{"text": "Заказ №1617 успешно создан.", "user_id": 3, "audience": "client", "order_id": 1617, "to_state": "order_created"}','SENT',1,'2026-07-26 11:05:15','tg:1617:order_created:client',NULL,'2026-07-26 11:05:15','2026-07-26 11:05:26'),
(7,'svc_courier_01','telegram','774531703','order.progress.order_courier1_assigned','{"text": "Заказ №1617 принял курьер User 2. Ожидайте: в ближайшие 30 минут курьер приедет забрать посылку.", "user_id": 3, "audience": "client", "order_id": 1617, "to_state": "order_courier1_assigned"}','SENT',1,'2026-07-26 11:05:43','tg:1617:order_courier1_assigned:client:i222',NULL,'2026-07-26 11:05:43','2026-07-26 11:05:45'),
(8,'svc_courier_01','telegram','774531703','order.progress.order_created','{"text": "Заказ №1618 успешно создан.", "user_id": 3, "audience": "client", "order_id": 1618, "to_state": "order_created"}','SENT',1,'2026-07-26 12:36:09','tg:1618:order_created:client',NULL,'2026-07-26 12:36:09','2026-07-26 12:36:12'),
(9,'svc_courier_01','telegram','774531703','order.progress.order_courier1_assigned','{"text": "Заказ №1618 принял курьер User 2. Ожидайте: в ближайшие 30 минут курьер приедет забрать посылку.", "user_id": 3, "audience": "client", "order_id": 1618, "to_state": "order_courier1_assigned"}','SENT',1,'2026-07-26 12:36:16','tg:1618:order_courier1_assigned:client:i225',NULL,'2026-07-26 12:36:16','2026-07-26 12:36:19'),
(10,'svc_courier_01','telegram','774531703','order.progress.order_created','{"text": "Заказ №1619 успешно создан.", "user_id": 3, "audience": "client", "order_id": 1619, "to_state": "order_created"}','SENT',1,'2026-07-26 14:28:35','tg:1619:order_created:client',NULL,'2026-07-26 14:28:35','2026-07-26 14:28:38'),
(11,'svc_courier_01','telegram','774531703','order.progress.order_courier1_assigned','{"text": "Заказ №1619 принял курьер User 2. Ожидайте: в ближайшие 30 минут курьер приедет забрать посылку.", "user_id": 3, "audience": "client", "order_id": 1619, "to_state": "order_courier1_assigned"}','SENT',1,'2026-07-26 14:28:45','tg:1619:order_courier1_assigned:client:i228',NULL,'2026-07-26 14:28:45','2026-07-26 14:28:47'),
(12,'svc_courier_01','telegram','774531703','order.progress.order_created','{"text": "Заказ №1620 успешно создан.", "user_id": 3, "audience": "client", "order_id": 1620, "to_state": "order_created"}','SENT',1,'2026-07-27 09:31:19','tg:1620:order_created:client',NULL,'2026-07-27 09:31:19','2026-07-27 09:31:23'),
(13,'svc_courier_01','telegram','774531703','order.progress.order_courier1_assigned','{"text": "Заказ №1620 принял курьер User 2. Ожидайте: в ближайшие 30 минут курьер приедет забрать посылку.", "user_id": 3, "audience": "client", "order_id": 1620, "to_state": "order_courier1_assigned"}','SENT',1,'2026-07-27 09:31:29','tg:1620:order_courier1_assigned:client:i231',NULL,'2026-07-27 09:31:29','2026-07-27 09:31:32');
/*!40000 ALTER TABLE `platform_outbox` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table `platform_reconcile_queue`
--

DROP TABLE IF EXISTS `platform_reconcile_queue`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `platform_reconcile_queue` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `service_id` varchar(64) NOT NULL,
  `instance_id` bigint NOT NULL,
  `entity_type` varchar(128) NOT NULL,
  `entity_id` bigint NOT NULL,
  `from_state` varchar(128) DEFAULT NULL,
  `to_state` varchar(128) NOT NULL,
  `event_name` varchar(128) DEFAULT NULL,
  `transition_id` bigint NOT NULL,
  `payload_json` json DEFAULT NULL,
  `status` varchar(32) NOT NULL DEFAULT 'PENDING',
  `attempts` int NOT NULL DEFAULT '0',
  `last_error` text,
  `created_at` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `updated_at` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  `done_at` datetime DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `uq_reconcile_instance_transition` (`instance_id`,`transition_id`),
  KEY `idx_reconcile_poll` (`status`,`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `platform_reconcile_queue`
--

LOCK TABLES `platform_reconcile_queue` WRITE;
/*!40000 ALTER TABLE `platform_reconcile_queue` DISABLE KEYS */;
/*!40000 ALTER TABLE `platform_reconcile_queue` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table `server_fsm_instances`
--

DROP TABLE IF EXISTS `server_fsm_instances`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `server_fsm_instances` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `service_id` varchar(64) NOT NULL,
  `process_name` varchar(128) NOT NULL,
  `entity_type` varchar(128) NOT NULL,
  `entity_id` bigint NOT NULL,
  `status` varchar(32) NOT NULL DEFAULT 'PENDING',
  `attempts` int NOT NULL DEFAULT '0',
  `next_attempt_at` datetime DEFAULT NULL COMMENT 'PENDING retry not before this UTC time',
  `last_error` text,
  `payload_json` json DEFAULT NULL,
  `actor_id` bigint DEFAULT NULL,
  `graph_version` int DEFAULT NULL COMMENT 'pinned domain graph version at enqueue',
  `created_at` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `updated_at` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  `started_at` datetime DEFAULT NULL,
  `finished_at` datetime DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `idx_instances_status_id` (`status`,`id`),
  KEY `idx_instances_service` (`service_id`),
  KEY `idx_instances_claim` (`status`,`next_attempt_at`,`id`)
) ENGINE=InnoDB AUTO_INCREMENT=232 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `server_fsm_instances`
--

LOCK TABLES `server_fsm_instances` WRITE;
/*!40000 ALTER TABLE `server_fsm_instances` DISABLE KEYS */;
INSERT INTO `server_fsm_instances` (`id`,`service_id`,`process_name`,`entity_type`,`entity_id`,`status`,`attempts`,`next_attempt_at`,`last_error`,`payload_json`,`actor_id`,`graph_version`,`created_at`,`updated_at`,`started_at`,`finished_at`) VALUES
(157,'svc_courier_01','locker_reserve','locker',70,'COMPLETED',0,NULL,NULL,'{"source": "create_order", "order_id": 1610, "cell_role": "source"}',3,NULL,'2026-07-24 13:00:26','2026-07-24 13:00:31','2026-07-24 13:00:27','2026-07-24 13:00:31'),
(158,'svc_courier_01','locker_reserve','locker',71,'COMPLETED',0,NULL,NULL,'{"source": "create_order", "order_id": 1610, "cell_role": "dest"}',3,NULL,'2026-07-24 13:00:26','2026-07-24 13:00:34','2026-07-24 13:00:32','2026-07-24 13:00:34'),
(159,'svc_courier_01','assign_executor','order',1610,'COMPLETED',0,NULL,NULL,'{"leg": "pickup", "source": "assign_executor", "courier_user_id": 2, "executor_user_id": 2}',2,NULL,'2026-07-24 13:00:36','2026-07-24 13:00:39','2026-07-24 13:00:37','2026-07-24 13:00:39'),
(160,'svc_courier_01','open_cell','order',1610,'COMPLETED',0,NULL,NULL,'{"leg": "pickup", "pin": "642877", "source": "open_cell", "courier_user_id": 2, "executor_user_id": 2}',2,NULL,'2026-07-24 13:00:43','2026-07-24 13:00:48','2026-07-24 13:00:44','2026-07-24 13:00:48'),
(161,'svc_courier_01','close_cell','order',1610,'COMPLETED',0,NULL,NULL,'{"leg": "pickup", "source": "close_cell", "courier_user_id": 2, "executor_user_id": 2}',2,NULL,'2026-07-24 13:00:50','2026-07-24 13:00:56','2026-07-24 13:00:51','2026-07-24 13:00:56'),
(162,'svc_courier_01','locker_reserve','locker',1,'COMPLETED',0,NULL,NULL,'{"source": "create_order", "order_id": 1611, "cell_role": "source"}',11,NULL,'2026-07-24 13:00:59','2026-07-24 13:01:02','2026-07-24 13:01:00','2026-07-24 13:01:02'),
(163,'svc_courier_01','locker_reserve','locker',52,'COMPLETED',0,NULL,NULL,'{"source": "create_order", "order_id": 1611, "cell_role": "dest"}',11,NULL,'2026-07-24 13:00:59','2026-07-24 13:01:06','2026-07-24 13:01:03','2026-07-24 13:01:06'),
(164,'svc_courier_01','open_cell','order',1611,'COMPLETED',0,NULL,NULL,'{"leg": "pickup", "pin": "726346", "source": "open_cell", "courier_user_id": 11, "executor_user_id": 11}',11,NULL,'2026-07-24 13:01:09','2026-07-24 13:01:14','2026-07-24 13:01:10','2026-07-24 13:01:14'),
(165,'svc_courier_01','close_cell','order',1611,'COMPLETED',0,NULL,NULL,'{"leg": "pickup", "source": "close_cell", "courier_user_id": 11, "executor_user_id": 11}',11,NULL,'2026-07-24 13:01:16','2026-07-24 13:01:21','2026-07-24 13:01:17','2026-07-24 13:01:21'),
(166,'svc_courier_01','locker_reserve','locker',64,'COMPLETED',0,NULL,NULL,'{"source": "create_order", "order_id": 1612, "cell_role": "source"}',12,NULL,'2026-07-24 13:01:24','2026-07-24 13:01:28','2026-07-24 13:01:26','2026-07-24 13:01:28'),
(167,'svc_courier_01','locker_reserve','locker',87,'COMPLETED',0,NULL,NULL,'{"source": "create_order", "order_id": 1612, "cell_role": "dest"}',12,NULL,'2026-07-24 13:01:25','2026-07-24 13:01:31','2026-07-24 13:01:29','2026-07-24 13:01:31'),
(168,'svc_courier_01','assign_executor','order',1612,'COMPLETED',0,NULL,NULL,'{"leg": "pickup", "source": "assign_executor", "courier_user_id": 7, "executor_user_id": 7}',7,NULL,'2026-07-24 13:01:32','2026-07-24 13:01:37','2026-07-24 13:01:34','2026-07-24 13:01:37'),
(169,'svc_courier_01','open_cell','order',1612,'COMPLETED',0,NULL,NULL,'{"leg": "pickup", "pin": "430460", "source": "open_cell", "courier_user_id": 7, "executor_user_id": 7}',7,NULL,'2026-07-24 13:01:41','2026-07-24 13:01:46','2026-07-24 13:01:42','2026-07-24 13:01:46'),
(170,'svc_courier_01','close_cell','order',1612,'COMPLETED',0,NULL,NULL,'{"leg": "pickup", "source": "close_cell", "courier_user_id": 7, "executor_user_id": 7}',7,NULL,'2026-07-24 13:01:48','2026-07-24 13:01:54','2026-07-24 13:01:49','2026-07-24 13:01:54'),
(171,'svc_courier_01','locker_reserve','locker',67,'COMPLETED',0,NULL,NULL,'{"source": "create_order", "order_id": 1613, "cell_role": "source"}',13,NULL,'2026-07-24 13:01:58','2026-07-24 13:02:01','2026-07-24 13:01:59','2026-07-24 13:02:01'),
(172,'svc_courier_01','locker_reserve','locker',90,'COMPLETED',0,NULL,NULL,'{"source": "create_order", "order_id": 1613, "cell_role": "dest"}',13,NULL,'2026-07-24 13:01:58','2026-07-24 13:02:04','2026-07-24 13:02:02','2026-07-24 13:02:04'),
(173,'svc_courier_01','open_cell','order',1613,'COMPLETED',0,NULL,NULL,'{"leg": "pickup", "pin": "183912", "source": "open_cell", "courier_user_id": 13, "executor_user_id": 13}',13,NULL,'2026-07-24 13:02:08','2026-07-24 13:02:12','2026-07-24 13:02:08','2026-07-24 13:02:12'),
(174,'svc_courier_01','close_cell','order',1613,'COMPLETED',0,NULL,NULL,'{"leg": "pickup", "source": "close_cell", "courier_user_id": 13, "executor_user_id": 13}',13,NULL,'2026-07-24 13:02:14','2026-07-24 13:02:20','2026-07-24 13:02:15','2026-07-24 13:02:20'),
(175,'svc_courier_01','start_loading','driver_reservations',53,'COMPLETED',0,NULL,NULL,'{"source": "start_loading", "direction_id": 16, "driver_user_id": 1, "executor_user_id": 1}',1,NULL,'2026-07-24 13:02:26','2026-07-24 13:02:29','2026-07-24 13:02:28','2026-07-24 13:02:29'),
(176,'svc_courier_01','open_cell','order',1610,'COMPLETED',0,NULL,NULL,'{"leg": "pickup", "pin": "644075", "source": "open_cell", "courier_user_id": 1, "executor_user_id": 1}',1,NULL,'2026-07-24 13:02:33','2026-07-24 13:02:37','2026-07-24 13:02:34','2026-07-24 13:02:37'),
(177,'svc_courier_01','close_cell','order',1610,'COMPLETED',0,NULL,NULL,'{"leg": "pickup", "source": "close_cell", "courier_user_id": 1, "executor_user_id": 1}',1,NULL,'2026-07-24 13:02:39','2026-07-24 13:02:44','2026-07-24 13:02:40','2026-07-24 13:02:44'),
(178,'svc_courier_01','open_cell','order',1611,'COMPLETED',0,NULL,NULL,'{"leg": "pickup", "pin": "775101", "source": "open_cell", "courier_user_id": 1, "executor_user_id": 1}',1,NULL,'2026-07-24 13:02:47','2026-07-24 13:02:52','2026-07-24 13:02:48','2026-07-24 13:02:52'),
(179,'svc_courier_01','close_cell','order',1611,'COMPLETED',0,NULL,NULL,'{"leg": "pickup", "source": "close_cell", "courier_user_id": 1, "executor_user_id": 1}',1,NULL,'2026-07-24 13:02:54','2026-07-24 13:02:58','2026-07-24 13:02:55','2026-07-24 13:02:58'),
(180,'svc_courier_01','open_cell','order',1612,'COMPLETED',0,NULL,NULL,'{"leg": "pickup", "pin": "651409", "source": "open_cell", "courier_user_id": 1, "executor_user_id": 1}',1,NULL,'2026-07-24 13:03:02','2026-07-24 13:03:07','2026-07-24 13:03:03','2026-07-24 13:03:07'),
(181,'svc_courier_01','close_cell','order',1612,'COMPLETED',0,NULL,NULL,'{"leg": "pickup", "source": "close_cell", "courier_user_id": 1, "executor_user_id": 1}',1,NULL,'2026-07-24 13:03:10','2026-07-24 13:03:16','2026-07-24 13:03:12','2026-07-24 13:03:16'),
(182,'svc_courier_01','open_cell','order',1613,'COMPLETED',0,NULL,NULL,'{"leg": "pickup", "pin": "267135", "source": "open_cell", "courier_user_id": 1, "executor_user_id": 1}',1,NULL,'2026-07-24 13:03:20','2026-07-24 13:03:24','2026-07-24 13:03:21','2026-07-24 13:03:24'),
(183,'svc_courier_01','close_cell','order',1613,'COMPLETED',0,NULL,NULL,'{"leg": "pickup", "source": "close_cell", "courier_user_id": 1, "executor_user_id": 1}',1,NULL,'2026-07-24 13:03:27','2026-07-24 13:03:31','2026-07-24 13:03:27','2026-07-24 13:03:31'),
(184,'svc_courier_01','complete_loading','driver_reservations',53,'COMPLETED',0,NULL,NULL,'{"source": "complete_loading", "to_city": "Санкт-Петербург", "from_city": "Москва", "direction_id": 16, "driver_user_id": 1, "executor_user_id": 1}',1,NULL,'2026-07-24 13:03:37','2026-07-24 13:03:40','2026-07-24 13:03:38','2026-07-24 13:03:40'),
(185,'svc_courier_01','start_order_transit','order',1610,'COMPLETED',0,NULL,NULL,'{"source": "start_trip", "trip_id": 61, "driver_user_id": 1, "executor_user_id": 1}',1,NULL,'2026-07-24 13:03:43','2026-07-24 13:03:50','2026-07-24 13:03:47','2026-07-24 13:03:50'),
(186,'svc_courier_01','start_order_transit','order',1611,'COMPLETED',0,NULL,NULL,'{"source": "start_trip", "trip_id": 61, "driver_user_id": 1, "executor_user_id": 1}',1,NULL,'2026-07-24 13:03:44','2026-07-24 13:03:55','2026-07-24 13:03:52','2026-07-24 13:03:55'),
(187,'svc_courier_01','start_order_transit','order',1612,'COMPLETED',0,NULL,NULL,'{"source": "start_trip", "trip_id": 61, "driver_user_id": 1, "executor_user_id": 1}',1,NULL,'2026-07-24 13:03:45','2026-07-24 13:03:59','2026-07-24 13:03:57','2026-07-24 13:03:59'),
(188,'svc_courier_01','start_order_transit','order',1613,'COMPLETED',0,NULL,NULL,'{"source": "start_trip", "trip_id": 61, "driver_user_id": 1, "executor_user_id": 1}',1,NULL,'2026-07-24 13:03:45','2026-07-24 13:04:03','2026-07-24 13:04:01','2026-07-24 13:04:03'),
(189,'svc_courier_01','start_trip','trip',61,'COMPLETED',0,NULL,NULL,'{"source": "start_trip", "saga_id": 3, "saga_finish": "on_success", "driver_user_id": 1, "executor_user_id": 1}',1,NULL,'2026-07-24 13:04:04','2026-07-24 13:04:08','2026-07-24 13:04:05','2026-07-24 13:04:08'),
(190,'svc_courier_01','open_cell','order',1610,'COMPLETED',0,NULL,NULL,'{"leg": "delivery", "pin": "399963", "source": "open_cell", "courier_user_id": 1, "executor_user_id": 1}',1,NULL,'2026-07-24 13:04:12','2026-07-24 13:04:16','2026-07-24 13:04:12','2026-07-24 13:04:16'),
(191,'svc_courier_01','close_cell','order',1610,'COMPLETED',0,NULL,NULL,'{"leg": "delivery", "source": "close_cell", "courier_user_id": 1, "executor_user_id": 1}',1,NULL,'2026-07-24 13:04:17','2026-07-24 13:04:22','2026-07-24 13:04:19','2026-07-24 13:04:22'),
(192,'svc_courier_01','open_cell','order',1611,'COMPLETED',0,NULL,NULL,'{"leg": "delivery", "pin": "145627", "source": "open_cell", "courier_user_id": 1, "executor_user_id": 1}',1,NULL,'2026-07-24 13:04:25','2026-07-24 13:04:30','2026-07-24 13:04:26','2026-07-24 13:04:30'),
(193,'svc_courier_01','close_cell','order',1611,'COMPLETED',0,NULL,NULL,'{"leg": "delivery", "source": "close_cell", "courier_user_id": 1, "executor_user_id": 1}',1,NULL,'2026-07-24 13:04:32','2026-07-24 13:04:36','2026-07-24 13:04:33','2026-07-24 13:04:36'),
(194,'svc_courier_01','open_cell','order',1612,'COMPLETED',0,NULL,NULL,'{"leg": "delivery", "pin": "945188", "source": "open_cell", "courier_user_id": 1, "executor_user_id": 1}',1,NULL,'2026-07-24 13:04:39','2026-07-24 13:04:44','2026-07-24 13:04:41','2026-07-24 13:04:44'),
(195,'svc_courier_01','close_cell','order',1612,'COMPLETED',0,NULL,NULL,'{"leg": "delivery", "source": "close_cell", "courier_user_id": 1, "executor_user_id": 1}',1,NULL,'2026-07-24 13:04:46','2026-07-24 13:04:50','2026-07-24 13:04:47','2026-07-24 13:04:50'),
(196,'svc_courier_01','open_cell','order',1613,'COMPLETED',0,NULL,NULL,'{"leg": "delivery", "pin": "538245", "source": "open_cell", "courier_user_id": 1, "executor_user_id": 1}',1,NULL,'2026-07-24 13:04:53','2026-07-24 13:04:58','2026-07-24 13:04:55','2026-07-24 13:04:58'),
(197,'svc_courier_01','close_cell','order',1613,'COMPLETED',0,NULL,NULL,'{"leg": "delivery", "source": "close_cell", "courier_user_id": 1, "executor_user_id": 1}',1,NULL,'2026-07-24 13:05:00','2026-07-24 13:05:05','2026-07-24 13:05:01','2026-07-24 13:05:05'),
(198,'svc_courier_01','complete_trip','trip',61,'COMPLETED',0,NULL,NULL,'{"source": "complete_trip", "driver_user_id": 1, "executor_user_id": 1}',1,NULL,'2026-07-24 13:05:08','2026-07-24 13:05:13','2026-07-24 13:05:10','2026-07-24 13:05:13'),
(199,'svc_courier_01','assign_executor','order',1610,'COMPLETED',0,NULL,NULL,'{"leg": "delivery", "source": "assign_executor", "courier_user_id": 6, "executor_user_id": 6}',6,NULL,'2026-07-24 13:05:14','2026-07-24 13:05:18','2026-07-24 13:05:16','2026-07-24 13:05:18'),
(200,'svc_courier_01','open_cell','order',1610,'COMPLETED',0,NULL,NULL,'{"leg": "delivery", "pin": "122793", "source": "open_cell", "courier_user_id": 6, "executor_user_id": 6}',6,NULL,'2026-07-24 13:05:22','2026-07-24 13:05:27','2026-07-24 13:05:23','2026-07-24 13:05:27'),
(201,'svc_courier_01','close_cell','order',1610,'COMPLETED',0,NULL,NULL,'{"leg": "delivery", "source": "close_cell", "courier_user_id": 6, "executor_user_id": 6}',6,NULL,'2026-07-24 13:05:29','2026-07-24 13:05:34','2026-07-24 13:05:30','2026-07-24 13:05:34'),
(202,'svc_courier_01','confirm_courier2_delivery','order',1610,'COMPLETED',0,NULL,NULL,'{"leg": "delivery", "pin": "248028", "source": "confirm_courier2_delivery", "courier_user_id": 6, "executor_user_id": 6}',6,NULL,'2026-07-24 13:05:38','2026-07-24 13:05:43','2026-07-24 13:05:40','2026-07-24 13:05:43'),
(203,'svc_courier_01','assign_executor','order',1611,'COMPLETED',0,NULL,NULL,'{"leg": "delivery", "source": "assign_executor", "courier_user_id": 8, "executor_user_id": 8}',8,NULL,'2026-07-24 13:05:45','2026-07-24 13:05:48','2026-07-24 13:05:46','2026-07-24 13:05:48'),
(204,'svc_courier_01','open_cell','order',1611,'COMPLETED',0,NULL,NULL,'{"leg": "delivery", "pin": "631362", "source": "open_cell", "courier_user_id": 8, "executor_user_id": 8}',8,NULL,'2026-07-24 13:05:52','2026-07-24 13:05:57','2026-07-24 13:05:53','2026-07-24 13:05:57'),
(205,'svc_courier_01','close_cell','order',1611,'COMPLETED',0,NULL,NULL,'{"leg": "delivery", "source": "close_cell", "courier_user_id": 8, "executor_user_id": 8}',8,NULL,'2026-07-24 13:05:59','2026-07-24 13:06:03','2026-07-24 13:05:59','2026-07-24 13:06:03'),
(206,'svc_courier_01','confirm_courier2_delivery','order',1611,'COMPLETED',0,NULL,NULL,'{"leg": "delivery", "pin": "132824", "source": "confirm_courier2_delivery", "courier_user_id": 8, "executor_user_id": 8}',8,NULL,'2026-07-24 13:06:07','2026-07-24 13:06:10','2026-07-24 13:06:07','2026-07-24 13:06:10'),
(207,'svc_courier_01','open_cell','order',1612,'COMPLETED',0,NULL,NULL,'{"leg": "delivery", "pin": "423517", "source": "open_cell", "courier_user_id": 15, "executor_user_id": 15}',15,NULL,'2026-07-24 13:06:14','2026-07-24 13:06:18','2026-07-24 13:06:15','2026-07-24 13:06:18'),
(208,'svc_courier_01','close_cell','order',1612,'COMPLETED',0,NULL,NULL,'{"leg": "delivery", "source": "close_cell", "courier_user_id": 15, "executor_user_id": 15}',15,NULL,'2026-07-24 13:06:21','2026-07-24 13:06:25','2026-07-24 13:06:21','2026-07-24 13:06:25'),
(209,'svc_courier_01','open_cell','order',1613,'COMPLETED',0,NULL,NULL,'{"leg": "delivery", "pin": "960808", "source": "open_cell", "courier_user_id": 16, "executor_user_id": 16}',16,NULL,'2026-07-24 13:06:29','2026-07-24 13:06:33','2026-07-24 13:06:30','2026-07-24 13:06:33'),
(210,'svc_courier_01','close_cell','order',1613,'COMPLETED',0,NULL,NULL,'{"leg": "delivery", "source": "close_cell", "courier_user_id": 16, "executor_user_id": 16}',16,NULL,'2026-07-24 13:06:36','2026-07-24 13:06:40','2026-07-24 13:06:36','2026-07-24 13:06:40'),
(211,'svc_courier_01','locker_reserve','locker',46,'COMPLETED',0,NULL,NULL,'{"source": "create_order", "order_id": 1614, "cell_role": "source"}',3,NULL,'2026-07-24 16:15:12','2026-07-24 16:15:18','2026-07-24 16:15:14','2026-07-24 16:15:18'),
(212,'svc_courier_01','locker_reserve','locker',55,'COMPLETED',0,NULL,NULL,'{"source": "create_order", "order_id": 1614, "cell_role": "dest"}',3,NULL,'2026-07-24 16:15:13','2026-07-24 16:15:21','2026-07-24 16:15:19','2026-07-24 16:15:21'),
(213,'svc_courier_01','assign_executor','order',1614,'COMPLETED',0,NULL,NULL,'{"leg": "pickup", "source": "assign_executor", "courier_user_id": 2, "executor_user_id": 2}',2,NULL,'2026-07-24 16:15:23','2026-07-24 16:15:26','2026-07-24 16:15:24','2026-07-24 16:15:26'),
(214,'svc_courier_01','locker_reserve','locker',47,'COMPLETED',0,NULL,NULL,'{"source": "create_order", "order_id": 1615, "cell_role": "source"}',3,NULL,'2026-07-24 16:25:25','2026-07-24 16:25:29','2026-07-24 16:25:27','2026-07-24 16:25:29'),
(215,'svc_courier_01','locker_reserve','locker',56,'COMPLETED',0,NULL,NULL,'{"source": "create_order", "order_id": 1615, "cell_role": "dest"}',3,NULL,'2026-07-24 16:25:25','2026-07-24 16:25:34','2026-07-24 16:25:32','2026-07-24 16:25:34'),
(216,'svc_courier_01','assign_executor','order',1615,'COMPLETED',0,NULL,NULL,'{"leg": "pickup", "source": "assign_executor", "courier_user_id": 2, "executor_user_id": 2}',2,NULL,'2026-07-24 16:25:36','2026-07-24 16:25:41','2026-07-24 16:25:38','2026-07-24 16:25:41'),
(217,'svc_courier_01','locker_reserve','locker',48,'COMPLETED',0,NULL,NULL,'{"source": "create_order", "order_id": 1616, "cell_role": "source"}',3,NULL,'2026-07-26 09:48:45','2026-07-26 09:48:50','2026-07-26 09:48:46','2026-07-26 09:48:50'),
(218,'svc_courier_01','locker_reserve','locker',57,'COMPLETED',0,NULL,NULL,'{"source": "create_order", "order_id": 1616, "cell_role": "dest"}',3,NULL,'2026-07-26 09:48:45','2026-07-26 09:48:55','2026-07-26 09:48:53','2026-07-26 09:48:55'),
(219,'svc_courier_01','assign_executor','order',1616,'COMPLETED',0,NULL,NULL,'{"leg": "pickup", "source": "assign_executor", "courier_user_id": 2, "executor_user_id": 2}',2,NULL,'2026-07-26 09:48:57','2026-07-26 09:49:03','2026-07-26 09:49:00','2026-07-26 09:49:03'),
(220,'svc_courier_01','locker_reserve','locker',65,'COMPLETED',0,NULL,NULL,'{"source": "create_order", "order_id": 1617, "cell_role": "source"}',3,NULL,'2026-07-26 11:05:16','2026-07-26 11:05:24','2026-07-26 11:05:22','2026-07-26 11:05:24'),
(221,'svc_courier_01','locker_reserve','locker',88,'COMPLETED',0,NULL,NULL,'{"source": "create_order", "order_id": 1617, "cell_role": "dest"}',3,NULL,'2026-07-26 11:05:16','2026-07-26 11:05:32','2026-07-26 11:05:29','2026-07-26 11:05:32'),
(222,'svc_courier_01','assign_executor','order',1617,'COMPLETED',0,NULL,NULL,'{"leg": "pickup", "source": "assign_executor", "courier_user_id": 2, "executor_user_id": 2}',2,NULL,'2026-07-26 11:05:35','2026-07-26 11:05:43','2026-07-26 11:05:38','2026-07-26 11:05:43'),
(223,'svc_courier_01','locker_reserve','locker',66,'COMPLETED',0,NULL,NULL,'{"source": "create_order_request", "cell_role": "source", "request_id": 345}',3,NULL,'2026-07-26 12:35:57','2026-07-26 12:36:01','2026-07-26 12:35:58','2026-07-26 12:36:01'),
(224,'svc_courier_01','locker_reserve','locker',89,'COMPLETED',0,NULL,NULL,'{"source": "create_order_request", "cell_role": "dest", "request_id": 345}',3,NULL,'2026-07-26 12:35:57','2026-07-26 12:36:06','2026-07-26 12:36:03','2026-07-26 12:36:06'),
(225,'svc_courier_01','assign_executor','order',1618,'COMPLETED',0,NULL,NULL,'{"leg": "pickup", "source": "assign_executor", "courier_user_id": 2, "executor_user_id": 2}',2,NULL,'2026-07-26 12:36:11','2026-07-26 12:36:16','2026-07-26 12:36:13','2026-07-26 12:36:16'),
(226,'svc_courier_01','locker_reserve','locker',2,'COMPLETED',0,NULL,NULL,'{"source": "create_order_request", "cell_role": "source", "request_id": 346}',3,NULL,'2026-07-26 14:28:17','2026-07-26 14:28:25','2026-07-26 14:28:20','2026-07-26 14:28:25'),
(227,'svc_courier_01','locker_reserve','locker',53,'COMPLETED',0,NULL,NULL,'{"source": "create_order_request", "cell_role": "dest", "request_id": 346}',3,NULL,'2026-07-26 14:28:18','2026-07-26 14:28:31','2026-07-26 14:28:28','2026-07-26 14:28:31'),
(228,'svc_courier_01','assign_executor','order',1619,'COMPLETED',0,NULL,NULL,'{"leg": "pickup", "source": "assign_executor", "courier_user_id": 2, "executor_user_id": 2}',2,NULL,'2026-07-26 14:28:38','2026-07-26 14:28:45','2026-07-26 14:28:40','2026-07-26 14:28:45'),
(229,'svc_courier_01','locker_reserve','locker',3,'COMPLETED',0,NULL,NULL,'{"source": "create_order_request", "cell_role": "source", "request_id": 347}',3,1,'2026-07-27 09:30:42','2026-07-27 09:31:10','2026-07-27 09:30:46','2026-07-27 09:31:10'),
(230,'svc_courier_01','locker_reserve','locker',54,'COMPLETED',0,NULL,NULL,'{"source": "create_order_request", "cell_role": "dest", "request_id": 347}',3,1,'2026-07-27 09:30:43','2026-07-27 09:31:15','2026-07-27 09:31:12','2026-07-27 09:31:15'),
(231,'svc_courier_01','assign_executor','order',1620,'COMPLETED',0,NULL,NULL,'{"leg": "pickup", "source": "assign_executor", "courier_user_id": 2, "executor_user_id": 2}',2,1,'2026-07-27 09:31:23','2026-07-27 09:31:29','2026-07-27 09:31:25','2026-07-27 09:31:29');
/*!40000 ALTER TABLE `server_fsm_instances` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table `webhook_subscriptions`
--

DROP TABLE IF EXISTS `webhook_subscriptions`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `webhook_subscriptions` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `service_id` varchar(64) NOT NULL,
  `url` varchar(1024) NOT NULL,
  `secret` varchar(256) NOT NULL,
  `event_types` json DEFAULT NULL,
  `active` tinyint(1) NOT NULL DEFAULT '1',
  `created_at` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  KEY `idx_webhooks_service` (`service_id`,`active`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `webhook_subscriptions`
--

LOCK TABLES `webhook_subscriptions` WRITE;
/*!40000 ALTER TABLE `webhook_subscriptions` DISABLE KEYS */;
/*!40000 ALTER TABLE `webhook_subscriptions` ENABLE KEYS */;
UNLOCK TABLES;

SET FOREIGN_KEY_CHECKS=1;
SET UNIQUE_CHECKS=1;
