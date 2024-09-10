CREATE DATABASE  IF NOT EXISTS `transferencia` /*!40100 DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci */ /*!80016 DEFAULT ENCRYPTION='N' */;
USE `transferencia`;
-- MySQL dump 10.13  Distrib 8.0.39, for Linux (x86_64)
--
-- Host: localhost    Database: transferencia
-- ------------------------------------------------------
-- Server version	8.0.39-0ubuntu0.20.04.1

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
-- Table structure for table `dado`
--

DROP TABLE IF EXISTS `dado`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `dado` (
  `id_dado` int unsigned NOT NULL AUTO_INCREMENT,
  `nome` varchar(80) DEFAULT NULL,
  `download_status` varchar(15) DEFAULT NULL,
  `download_start_datetime` datetime DEFAULT NULL,
  `download_end_datetime` datetime DEFAULT NULL,
  `md5_cp_status` varchar(15) DEFAULT NULL,
  `md5_cp_start_datetime` datetime DEFAULT NULL,
  `md5_cp_end_datetime` datetime DEFAULT NULL,
  `md5_validated` tinyint(1) DEFAULT NULL,
  `md5_validated_datetime` datetime DEFAULT NULL,
  `storing_status` varchar(15) DEFAULT NULL,
  `storing_start_datetime` datetime DEFAULT NULL,
  `storing_end_datetime` datetime DEFAULT NULL,
  `retry_user` int unsigned DEFAULT NULL,
  `retry_datetime` datetime DEFAULT NULL,
  `filesize` bigint DEFAULT NULL,
  `date_cba` varchar(20) DEFAULT NULL,
  PRIMARY KEY (`id_dado`),
  KEY `fk_dado_retry_user` (`retry_user`),
  CONSTRAINT `fk_dado_retry_user` FOREIGN KEY (`retry_user`) REFERENCES `usuario` (`id_usuario`)
) ENGINE=InnoDB AUTO_INCREMENT=4876 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `dado_historico`
--

DROP TABLE IF EXISTS `dado_historico`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `dado_historico` (
  `id_dado_historico` int unsigned NOT NULL AUTO_INCREMENT,
  `id_dado` int unsigned DEFAULT NULL,
  `nome` varchar(80) DEFAULT NULL,
  `download_status` varchar(15) DEFAULT NULL,
  `download_start_datetime` datetime DEFAULT NULL,
  `download_end_datetime` datetime DEFAULT NULL,
  `md5_cp_status` varchar(15) DEFAULT NULL,
  `md5_cp_start_datetime` datetime DEFAULT NULL,
  `md5_cp_end_datetime` datetime DEFAULT NULL,
  `md5_validated` tinyint(1) DEFAULT NULL,
  `md5_validated_datetime` datetime DEFAULT NULL,
  `storing_status` varchar(15) DEFAULT NULL,
  `storing_start_datetime` datetime DEFAULT NULL,
  `storing_end_datetime` datetime DEFAULT NULL,
  `retry_user` int unsigned DEFAULT NULL,
  `retry_datetime` datetime DEFAULT NULL,
  `filesize` bigint DEFAULT NULL,
  `date_cba` varchar(20) DEFAULT NULL,
  PRIMARY KEY (`id_dado_historico`),
  KEY `fk_dado_historico_retry_user` (`retry_user`),
  KEY `fk_dado_historico_id_dado` (`id_dado`),
  CONSTRAINT `fk_dado_historico_id_dado` FOREIGN KEY (`id_dado`) REFERENCES `dado` (`id_dado`),
  CONSTRAINT `fk_dado_historico_retry_user` FOREIGN KEY (`retry_user`) REFERENCES `usuario` (`id_usuario`)
) ENGINE=InnoDB AUTO_INCREMENT=522 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `dado_retry`
--

DROP TABLE IF EXISTS `dado_retry`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `dado_retry` (
  `id_dado_retry` int unsigned NOT NULL AUTO_INCREMENT,
  `id_dado` int unsigned DEFAULT NULL,
  `nome` varchar(80) DEFAULT NULL,
  `error` varchar(15) DEFAULT NULL,
  PRIMARY KEY (`id_dado_retry`),
  KEY `fK_dado_retry_id_dado` (`id_dado`),
  CONSTRAINT `fK_dado_retry_id_dado` FOREIGN KEY (`id_dado`) REFERENCES `dado` (`id_dado`)
) ENGINE=InnoDB AUTO_INCREMENT=491 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `dartcom`
--

DROP TABLE IF EXISTS `dartcom`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `dartcom` (
  `id_dartcom` int unsigned NOT NULL AUTO_INCREMENT,
  `nome` varchar(80) DEFAULT NULL,
  `modified_datetime` datetime DEFAULT NULL,
  `compressed_status` varchar(15) DEFAULT NULL,
  `compressed_start_datetime` datetime DEFAULT NULL,
  `compressed_end_datetime` datetime DEFAULT NULL,
  `storing_status` varchar(15) DEFAULT NULL,
  `storing_start_datetime` datetime DEFAULT NULL,
  `storing_end_datetime` datetime DEFAULT NULL,
  `filesize` bigint DEFAULT NULL,
  `retry_user` int unsigned DEFAULT NULL,
  `retry_datetime` datetime DEFAULT NULL,
  `id_dartcom_satelite` int unsigned NOT NULL,
  `date_path` varchar(50) DEFAULT NULL,
  `missao` varchar(10) DEFAULT NULL,
  PRIMARY KEY (`id_dartcom`),
  KEY `fk_dartcom_retry_user` (`retry_user`),
  KEY `fk_dartcom_id_satelite` (`id_dartcom_satelite`),
  CONSTRAINT `fk_dartcom_id_satelite` FOREIGN KEY (`id_dartcom_satelite`) REFERENCES `dartcom_satelite` (`id_dartcom_satelite`),
  CONSTRAINT `fk_dartcom_retry_user` FOREIGN KEY (`retry_user`) REFERENCES `usuario` (`id_usuario`)
) ENGINE=InnoDB AUTO_INCREMENT=1166 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `dartcom_antena`
--

DROP TABLE IF EXISTS `dartcom_antena`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `dartcom_antena` (
  `id_dartcom_antena` int unsigned NOT NULL AUTO_INCREMENT,
  `nome` varchar(10) DEFAULT NULL,
  PRIMARY KEY (`id_dartcom_antena`)
) ENGINE=InnoDB AUTO_INCREMENT=6 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `dartcom_historico`
--

DROP TABLE IF EXISTS `dartcom_historico`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `dartcom_historico` (
  `id_dartcom_historico` int unsigned NOT NULL AUTO_INCREMENT,
  `id_dartcom` int unsigned NOT NULL,
  `nome` varchar(80) DEFAULT NULL,
  `modified_datetime` datetime DEFAULT NULL,
  `compressed_status` varchar(15) DEFAULT NULL,
  `compressed_start_datetime` datetime DEFAULT NULL,
  `compressed_end_datetime` datetime DEFAULT NULL,
  `storing_status` varchar(15) DEFAULT NULL,
  `storing_start_datetime` datetime DEFAULT NULL,
  `storing_end_datetime` datetime DEFAULT NULL,
  `filesize` bigint DEFAULT NULL,
  `retry_user` int unsigned DEFAULT NULL,
  `retry_datetime` datetime DEFAULT NULL,
  `id_dartcom_satelite` int unsigned NOT NULL,
  `date_path` varchar(50) DEFAULT NULL,
  `missao` varchar(10) DEFAULT NULL,
  PRIMARY KEY (`id_dartcom_historico`),
  KEY `fk_dartcom_historico_retry_user` (`retry_user`),
  KEY `fk_dartcom_historico_id_dartcom` (`id_dartcom`),
  KEY `fk_dartcom_historico_id_satelite` (`id_dartcom_satelite`),
  CONSTRAINT `fk_dartcom_historico_id_dartcom` FOREIGN KEY (`id_dartcom`) REFERENCES `dartcom` (`id_dartcom`),
  CONSTRAINT `fk_dartcom_historico_id_satelite` FOREIGN KEY (`id_dartcom_satelite`) REFERENCES `dartcom_satelite` (`id_dartcom_satelite`),
  CONSTRAINT `fk_dartcom_historico_retry_user` FOREIGN KEY (`retry_user`) REFERENCES `usuario` (`id_usuario`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `dartcom_retry`
--

DROP TABLE IF EXISTS `dartcom_retry`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `dartcom_retry` (
  `id_dartcom_retry` int unsigned NOT NULL AUTO_INCREMENT,
  `id_dartcom` int unsigned NOT NULL,
  `nome` varchar(80) DEFAULT NULL,
  `error` varchar(15) DEFAULT NULL,
  PRIMARY KEY (`id_dartcom_retry`),
  KEY `fK_dado_retry_id_dartcom_idx` (`id_dartcom`),
  CONSTRAINT `fK_dado_retry_id_dartcom` FOREIGN KEY (`id_dartcom`) REFERENCES `dartcom` (`id_dartcom`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `dartcom_satelite`
--

DROP TABLE IF EXISTS `dartcom_satelite`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `dartcom_satelite` (
  `id_dartcom_satelite` int unsigned NOT NULL AUTO_INCREMENT,
  `id_dartcom_antena` int unsigned DEFAULT NULL,
  `nome` varchar(15) DEFAULT NULL,
  `sensor` varchar(10) DEFAULT NULL,
  `data_type` varchar(10) DEFAULT NULL,
  `satelite_path` varchar(100) DEFAULT NULL,
  `template_name` varchar(100) DEFAULT NULL,
  `command` varchar(100) DEFAULT NULL,
  `is_compressed` tinyint(1) DEFAULT '0',
  `is_epsl0` tinyint(1) DEFAULT '0',
  `epsl0_template` varchar(100) DEFAULT NULL,
  PRIMARY KEY (`id_dartcom_satelite`),
  KEY `fk_id_dartcom_antena` (`id_dartcom_antena`),
  CONSTRAINT `fk_id_dartcom_antena` FOREIGN KEY (`id_dartcom_antena`) REFERENCES `dartcom_antena` (`id_dartcom_antena`)
) ENGINE=InnoDB AUTO_INCREMENT=15 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `md5_cba_zerado`
--

DROP TABLE IF EXISTS `md5_cba_zerado`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `md5_cba_zerado` (
  `id_md5_cba_zerado` int unsigned NOT NULL AUTO_INCREMENT,
  `nome_dado` varchar(80) DEFAULT NULL,
  `registro_datetime` datetime DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id_md5_cba_zerado`)
) ENGINE=InnoDB AUTO_INCREMENT=292 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `usuario`
--

DROP TABLE IF EXISTS `usuario`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `usuario` (
  `id_usuario` int unsigned NOT NULL AUTO_INCREMENT,
  `nome` varchar(45) DEFAULT NULL,
  `email` varchar(45) DEFAULT NULL,
  `senha` varchar(100) DEFAULT NULL,
  `empresa` varchar(45) DEFAULT NULL,
  `adm` tinyint(1) DEFAULT '0',
  `ativo` tinyint(1) DEFAULT '1',
  `dark_theme` tinyint(1) DEFAULT '0',
  `perfil` varchar(20) DEFAULT 'visitante',
  `first_login` tinyint(1) DEFAULT '1',
  PRIMARY KEY (`id_usuario`)
) ENGINE=InnoDB AUTO_INCREMENT=24 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2024-09-09 17:00:07
