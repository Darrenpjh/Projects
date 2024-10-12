/*M!999999\- enable the sandbox mode */ 
-- MariaDB dump 10.19-11.5.2-MariaDB, for Win64 (AMD64)
--
-- Host: localhost    Database: project
-- ------------------------------------------------------
-- Server version	11.5.2-MariaDB

/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8mb4 */;
/*!40103 SET @OLD_TIME_ZONE=@@TIME_ZONE */;
/*!40103 SET TIME_ZONE='+00:00' */;
/*!40014 SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0 */;
/*!40014 SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0 */;
/*!40101 SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='NO_AUTO_VALUE_ON_ZERO' */;
/*M!100616 SET @OLD_NOTE_VERBOSITY=@@NOTE_VERBOSITY, NOTE_VERBOSITY=0 */;

--
-- Table structure for table `login_info`
--

DROP TABLE IF EXISTS `login_info`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `login_info` (
  `user_id` int(11) NOT NULL DEFAULT 0,
  `username` varchar(50) NOT NULL,
  `password` varchar(50) NOT NULL,
  `role` int(11) NOT NULL,
  PRIMARY KEY (`user_id`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1 COLLATE=latin1_swedish_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `login_info`
--

LOCK TABLES `login_info` WRITE;
/*!40000 ALTER TABLE `login_info` DISABLE KEYS */;
INSERT INTO `login_info` VALUES
(0,'root','root',0),
(1,'keefe','keefe',0),
(2,'tom','tom',1);
/*!40000 ALTER TABLE `login_info` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `order_info`
--

DROP TABLE IF EXISTS `order_info`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `order_info` (
  `order_id` int(11) NOT NULL AUTO_INCREMENT,
  `pizza_id` varchar(255) NOT NULL,
  `quantity` int(11) DEFAULT NULL,
  `DATE` int(11) DEFAULT NULL,
  `time` int(11) DEFAULT NULL,
  PRIMARY KEY (`order_id`),
  KEY `pizza_id` (`pizza_id`),
  CONSTRAINT `order_info_ibfk_1` FOREIGN KEY (`pizza_id`) REFERENCES `pizza_order` (`pizza_id`)
) ENGINE=InnoDB AUTO_INCREMENT=23 DEFAULT CHARSET=latin1 COLLATE=latin1_swedish_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `order_info`
--

LOCK TABLES `order_info` WRITE;
/*!40000 ALTER TABLE `order_info` DISABLE KEYS */;
INSERT INTO `order_info` VALUES
(1,'cali_ckn_s',1,1,13),
(2,'calabrese_m',1,1,13),
(3,'bbq_ckn_m',1,1,14),
(4,'ckn_alfredo_s',1,1,15),
(5,'ckn_pesto_l',1,1,18),
(6,'ckn_pesto_m',1,1,18),
(7,'ckn_pesto_s',1,2,15),
(8,'ckn_alfredo_m',1,2,18),
(9,'ckn_alfredo_l',2,3,20),
(10,'calabrese_s',1,4,21),
(11,'calabrese_l',1,7,19),
(17,'ckn_pesto_l',1,NULL,NULL),
(18,'ckn_pesto_l',2,NULL,NULL),
(19,'bbq_ckn_l',2,NULL,NULL),
(20,'ckn_pesto_l',1,NULL,NULL),
(21,'ckn_pesto_m',3,NULL,NULL),
(22,'ckn_pesto_m',2,NULL,NULL);
/*!40000 ALTER TABLE `order_info` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `pizza_order`
--

DROP TABLE IF EXISTS `pizza_order`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `pizza_order` (
  `pizza_id` varchar(255) NOT NULL,
  `pizza_type_id` varchar(255) NOT NULL,
  `size` char(1) NOT NULL,
  `price` float NOT NULL,
  PRIMARY KEY (`pizza_id`),
  KEY `pizza_type_id` (`pizza_type_id`),
  CONSTRAINT `pizza_order_ibfk_1` FOREIGN KEY (`pizza_type_id`) REFERENCES `pizza_type` (`pizza_type_id`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1 COLLATE=latin1_swedish_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `pizza_order`
--

LOCK TABLES `pizza_order` WRITE;
/*!40000 ALTER TABLE `pizza_order` DISABLE KEYS */;
INSERT INTO `pizza_order` VALUES
('bbq_ckn_l','bbq_ckn','L',20.75),
('bbq_ckn_m','bbq_ckn','M',16.75),
('bbq_ckn_s','bbq_ckn','S',12.75),
('calabrese_l','calabrese','L',20.25),
('calabrese_m','calabrese','M',16.25),
('calabrese_s','calabrese','S',12.25),
('cali_ckn_l','cali_ckn','L',20.75),
('cali_ckn_m','cali_ckn','M',16.75),
('cali_ckn_s','cali_ckn','S',12.75),
('ckn_alfredo_l','ckn_alfredo','L',20.75),
('ckn_alfredo_m','ckn_alfredo','M',16.75),
('ckn_alfredo_s','ckn_alfredo','S',12.75),
('ckn_pesto_l','ckn_pesto','L',20.75),
('ckn_pesto_m','ckn_pesto','M',16.75),
('ckn_pesto_s','ckn_pesto','S',12.75);
/*!40000 ALTER TABLE `pizza_order` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `pizza_type`
--

DROP TABLE IF EXISTS `pizza_type`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `pizza_type` (
  `pizza_type_id` varchar(255) NOT NULL,
  `name` varchar(50) DEFAULT NULL,
  `category` varchar(15) DEFAULT NULL,
  `ingredients` varchar(120) DEFAULT NULL,
  `image_path` varchar(255) DEFAULT NULL,
  PRIMARY KEY (`pizza_type_id`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1 COLLATE=latin1_swedish_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `pizza_type`
--

LOCK TABLES `pizza_type` WRITE;
/*!40000 ALTER TABLE `pizza_type` DISABLE KEYS */;
INSERT INTO `pizza_type` VALUES
('bbq_ckn','The Barbecue Chicken Pizza','Chicken','Barbecued Chicken_ Red Peppers_ Green Peppers_ Tomatoes_ Red Onions_ Barbecue Sauce','/static/images/pizzas/bbq chicken.jpg'),
('calabrese','The Calabrese Pizza','Supreme','‘Nduja Salami1_ Pancetta_ Tomatoes_ Red Onions_ Friggitello Peppers_ Garlic','\\static\\images\\pizzas\\calabrese pizza.jpg'),
('cali_ckn','The California Chicken Pizza','Chicken','Chicken_ Artichoke_ Spinach_ Garlic_ Jalapeno Peppers_ Fontina Cheese_ Gouda Cheese\r','\\static\\images\\pizzas\\california pizza.jpg'),
('ckn_alfredo','The Chicken Alfredo Pizza','Chicken','Chicken_ Red Onions_ Red Peppers_ Mushrooms_ Asiago Cheese_ Alfredo Sauce','\\static\\images\\pizzas\\The Chicken Alfredo Pizza.jpg'),
('ckn_pesto','The Chicken Pesto Pizza','Chicken','Chicken_ Tomatoes_ Red Peppers_ Spinach_ Garlic_ Pesto Sauce\r','\\static\\images\\pizzas\\chicken pesto pizza.jpg');
/*!40000 ALTER TABLE `pizza_type` ENABLE KEYS */;
UNLOCK TABLES;
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*M!100616 SET NOTE_VERBOSITY=@OLD_NOTE_VERBOSITY */;

-- Dump completed on 2024-10-11 14:10:19
