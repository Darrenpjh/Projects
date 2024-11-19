-- --------------------------------------------------------
-- Host:                         127.0.0.1
-- Server version:               11.5.2-MariaDB - mariadb.org binary distribution
-- Server OS:                    Win64
-- HeidiSQL Version:             12.6.0.6765
-- --------------------------------------------------------

/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET NAMES utf8 */;
/*!50503 SET NAMES utf8mb4 */;
/*!40103 SET @OLD_TIME_ZONE=@@TIME_ZONE */;
/*!40103 SET TIME_ZONE='+00:00' */;
/*!40014 SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0 */;
/*!40101 SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='NO_AUTO_VALUE_ON_ZERO' */;
/*!40111 SET @OLD_SQL_NOTES=@@SQL_NOTES, SQL_NOTES=0 */;


-- Dumping database structure for project
DROP DATABASE IF EXISTS `project`;
CREATE DATABASE IF NOT EXISTS `project` /*!40100 DEFAULT CHARACTER SET latin1 COLLATE latin1_swedish_ci */;
USE `project`;

-- Dumping structure for table project.login_info
DROP TABLE IF EXISTS `login_info`;
CREATE TABLE IF NOT EXISTS `login_info` (
  `user_id` int(11) NOT NULL DEFAULT 0,
  `username` varchar(50) NOT NULL,
  `password` varchar(50) NOT NULL,
  `role` int(11) NOT NULL,
  PRIMARY KEY (`user_id`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1 COLLATE=latin1_swedish_ci;

-- Dumping data for table project.login_info: ~4 rows (approximately)
DELETE FROM `login_info`;
INSERT INTO `login_info` (`user_id`, `username`, `password`, `role`) VALUES
	(0, 'root', 'root', 0),
	(1, 'keefe', 'keefe', 0),
	(2, 'tom', 'tom', 1),
	(3, 'hehe', 'hehe', 1);

-- Dumping structure for table project.order_info
DROP TABLE IF EXISTS `order_info`;
CREATE TABLE IF NOT EXISTS `order_info` (
  `order_id` int(11) NOT NULL AUTO_INCREMENT,
  `pizza_id` varchar(255) NOT NULL,
  `quantity` int(11) DEFAULT NULL,
  `DATE` int(11) DEFAULT NULL,
  `time` int(11) DEFAULT NULL,
  `user_id` int(11) NOT NULL,
  `status` int(11) NOT NULL,
  PRIMARY KEY (`order_id`),
  KEY `pizza_id` (`pizza_id`),
  KEY `user_id` (`user_id`),
  KEY `idx_order_id` (`order_id`,`status`),
  KEY `idx_status` (`status`,`order_id`),
  KEY `idx_pizza_id` (`pizza_id`,`status`),
  CONSTRAINT `order_info_ibfk_1` FOREIGN KEY (`pizza_id`) REFERENCES `pizza_order` (`pizza_id`),
  CONSTRAINT `order_info_ibfk_2` FOREIGN KEY (`user_id`) REFERENCES `login_info` (`user_id`)
) ENGINE=InnoDB AUTO_INCREMENT=25 DEFAULT CHARSET=latin1 COLLATE=latin1_swedish_ci;

-- Dumping data for table project.order_info: ~19 rows (approximately)
DELETE FROM `order_info`;
INSERT INTO `order_info` (`order_id`, `pizza_id`, `quantity`, `DATE`, `time`, `user_id`, `status`) VALUES
	(1, 'cali_ckn_s', 1, 1, 13, 2, 0),
	(2, 'calabrese_m', 1, 1, 13, 2, 0),
	(3, 'bbq_ckn_m', 1, 1, 14, 3, 0),
	(4, 'ckn_alfredo_s', 1, 1, 15, 2, 0),
	(5, 'ckn_pesto_l', 1, 1, 18, 2, 0),
	(6, 'ckn_pesto_m', 1, 1, 18, 3, 0),
	(7, 'ckn_pesto_s', 1, 2, 15, 2, 0),
	(8, 'ckn_alfredo_m', 1, 2, 18, 2, 0),
	(9, 'ckn_alfredo_l', 2, 3, 20, 2, 0),
	(10, 'calabrese_s', 1, 4, 21, 2, 0),
	(11, 'calabrese_l', 1, 7, 19, 2, 0),
	(17, 'ckn_pesto_l', 1, NULL, NULL, 2, 0),
	(18, 'ckn_pesto_l', 2, NULL, NULL, 2, 0),
	(19, 'bbq_ckn_l', 2, NULL, NULL, 2, 0),
	(20, 'ckn_pesto_l', 1, NULL, NULL, 2, 0),
	(21, 'ckn_pesto_m', 3, NULL, NULL, 3, 0),
	(22, 'ckn_pesto_m', 2, NULL, NULL, 2, 0),
	(23, 'bbq_ckn_s', 1, NULL, NULL, 2, 0),
	(24, 'bbq_ckn_s', 1, NULL, NULL, 3, 0);

-- Dumping structure for table project.pizza_order
DROP TABLE IF EXISTS `pizza_order`;
CREATE TABLE IF NOT EXISTS `pizza_order` (
  `pizza_id` varchar(255) NOT NULL,
  `pizza_type_id` varchar(255) NOT NULL,
  `size` char(1) NOT NULL,
  `price` float NOT NULL,
  PRIMARY KEY (`pizza_id`),
  KEY `pizza_type_id` (`pizza_type_id`),
  CONSTRAINT `pizza_order_ibfk_1` FOREIGN KEY (`pizza_type_id`) REFERENCES `pizza_type` (`pizza_type_id`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1 COLLATE=latin1_swedish_ci;

-- Dumping data for table project.pizza_order: ~15 rows (approximately)
DELETE FROM `pizza_order`;
INSERT INTO `pizza_order` (`pizza_id`, `pizza_type_id`, `size`, `price`) VALUES
	('bbq_ckn_l', 'bbq_ckn', 'L', 20.75),
	('bbq_ckn_m', 'bbq_ckn', 'M', 16.75),
	('bbq_ckn_s', 'bbq_ckn', 'S', 12.75),
	('calabrese_l', 'calabrese', 'L', 20.25),
	('calabrese_m', 'calabrese', 'M', 16.25),
	('calabrese_s', 'calabrese', 'S', 12.25),
	('cali_ckn_l', 'cali_ckn', 'L', 20.75),
	('cali_ckn_m', 'cali_ckn', 'M', 16.75),
	('cali_ckn_s', 'cali_ckn', 'S', 12.75),
	('ckn_alfredo_l', 'ckn_alfredo', 'L', 20.75),
	('ckn_alfredo_m', 'ckn_alfredo', 'M', 16.75),
	('ckn_alfredo_s', 'ckn_alfredo', 'S', 12.75),
	('ckn_pesto_l', 'ckn_pesto', 'L', 20.75),
	('ckn_pesto_m', 'ckn_pesto', 'M', 16.75),
	('ckn_pesto_s', 'ckn_pesto', 'S', 12.75);

-- Dumping structure for table project.pizza_type
DROP TABLE IF EXISTS `pizza_type`;
CREATE TABLE IF NOT EXISTS `pizza_type` (
  `pizza_type_id` varchar(255) NOT NULL,
  `name` varchar(50) DEFAULT NULL,
  `category` varchar(15) DEFAULT NULL,
  `ingredients` varchar(120) DEFAULT NULL,
  `image_path` varchar(255) DEFAULT NULL,
  PRIMARY KEY (`pizza_type_id`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1 COLLATE=latin1_swedish_ci;

-- Dumping data for table project.pizza_type: ~5 rows (approximately)
DELETE FROM `pizza_type`;
INSERT INTO `pizza_type` (`pizza_type_id`, `name`, `category`, `ingredients`, `image_path`) VALUES
	('bbq_ckn', 'The Barbecue Chicken Pizza', 'Chicken', 'Barbecued Chicken_ Red Peppers_ Green Peppers_ Tomatoes_ Red Onions_ Barbecue Sauce', '/static/images/pizzas/bbq chicken.jpg'),
	('calabrese', 'The Calabrese Pizza', 'Supreme', '‘Nduja Salami1_ Pancetta_ Tomatoes_ Red Onions_ Friggitello Peppers_ Garlic', '\\static\\images\\pizzas\\calabrese pizza.jpg'),
	('cali_ckn', 'The California Chicken Pizza', 'Chicken', 'Chicken_ Artichoke_ Spinach_ Garlic_ Jalapeno Peppers_ Fontina Cheese_ Gouda Cheese\r', '\\static\\images\\pizzas\\california pizza.jpg'),
	('ckn_alfredo', 'The Chicken Alfredo Pizza', 'Chicken', 'Chicken_ Red Onions_ Red Peppers_ Mushrooms_ Asiago Cheese_ Alfredo Sauce', '\\static\\images\\pizzas\\The Chicken Alfredo Pizza.jpg'),
	('ckn_pesto', 'The Chicken Pesto Pizza', 'Chicken', 'Chicken_ Tomatoes_ Red Peppers_ Spinach_ Garlic_ Pesto Sauce\r', '\\static\\images\\pizzas\\chicken pesto pizza.jpg');

/*!40103 SET TIME_ZONE=IFNULL(@OLD_TIME_ZONE, 'system') */;
/*!40101 SET SQL_MODE=IFNULL(@OLD_SQL_MODE, '') */;
/*!40014 SET FOREIGN_KEY_CHECKS=IFNULL(@OLD_FOREIGN_KEY_CHECKS, 1) */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40111 SET SQL_NOTES=IFNULL(@OLD_SQL_NOTES, 1) */;
