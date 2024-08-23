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
  `date_path` varchar(50),
  PRIMARY KEY (`id_dartcom`),
  KEY `fk_dartcom_retry_user` (`retry_user`),
  CONSTRAINT `fk_dartcom_retry_user` FOREIGN KEY (`retry_user`) REFERENCES `usuario` (`id_usuario`),
  CONSTRAINT `fk_dartcom_id_satelite` FOREIGN KEY (`id_dartcom_satelite`) REFERENCES `dartcom_satelite` (`id_dartcom_satelite`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
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
  `date_path` varchar(50),
  PRIMARY KEY (`id_dartcom_historico`),
  KEY `fk_dartcom_historico_retry_user` (`retry_user`),
  KEY `fk_dartcom_historico_id_dartcom` (`id_dartcom`),
  CONSTRAINT `fk_dartcom_historico_id_dartcom` FOREIGN KEY (`id_dartcom`) REFERENCES `dartcom` (`id_dartcom`),
  CONSTRAINT `fk_dartcom_historico_retry_user` FOREIGN KEY (`retry_user`) REFERENCES `usuario` (`id_usuario`),
  CONSTRAINT `fk_dartcom_historico_id_satelite` FOREIGN KEY (`id_dartcom_satelite`) REFERENCES `dartcom_satelite` (`id_dartcom_satelite`)
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
) ENGINE=InnoDB AUTO_INCREMENT=445 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

CREATE TABLE IF NOT EXISTS dartcom_antena(
 id_dartcom_antena int unsigned primary key auto_increment,
 nome varchar(10),
);

CREATE TABLE IF NOT EXISTS dartcom_satelite(
 id_dartcom_satelite int unsigned primary key auto_increment,
 id_dartcom_antena int unsigned,
 nome varchar(15),
 sensor varchar(10),
 data_type varchar(10),
 satelite_path varchar(100),
 template_name varchar(100),
 command varchar(100),
 is_compressed boolean default 0,
 is_epsl0 boolean default 0,
 epsl0_template varchar(100),
 template_path_origin_scp varchar(100),
 CONSTRAINT fk_id_dartcom_antena FOREIGN KEY (id_dartcom_antena) REFERENCES dartcom_antena (id_dartcom_antena)
);


/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2024-08-09 16:38:28
