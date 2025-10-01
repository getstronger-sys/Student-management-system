-- MySQL dump 10.13  Distrib 8.0.43, for Linux (x86_64)
--
-- Host: localhost    Database: student_management
-- ------------------------------------------------------
-- Server version	8.0.43

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
-- Table structure for table `courses`
--

DROP TABLE IF EXISTS `courses`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `courses` (
  `id` int NOT NULL AUTO_INCREMENT,
  `course_code` varchar(20) COLLATE utf8mb4_unicode_ci NOT NULL,
  `course_name` varchar(100) COLLATE utf8mb4_unicode_ci NOT NULL,
  `credits` float NOT NULL,
  `teacher_id` int DEFAULT NULL,
  `semester` varchar(20) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `class_time` varchar(100) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `class_location` varchar(100) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `course_code` (`course_code`),
  KEY `teacher_id` (`teacher_id`),
  CONSTRAINT `courses_ibfk_1` FOREIGN KEY (`teacher_id`) REFERENCES `teachers` (`id`) ON DELETE SET NULL
) ENGINE=InnoDB AUTO_INCREMENT=13 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `courses`
--

LOCK TABLES `courses` WRITE;
/*!40000 ALTER TABLE `courses` DISABLE KEYS */;
INSERT INTO `courses` VALUES (1,'CS101','Python程序设计',3,1,'2025-2026-1','周一 10:00-11:40','教101'),(2,'CS102','数据结构',4,1,'2025-2026-1','周三 14:00-15:40','教102'),(3,'CS201','计算机网络',3,2,'2025-2026-1','周二 08:00-09:40','教103'),(4,'CS202','操作系统',4,3,'2025-2026-1','周四 10:00-11:40','教201'),(5,'CS203','数据库原理',3.5,2,'2025-2026-1','周五 14:00-15:40','教202'),(6,'CS301','软件工程',3,4,'2025-2026-2','周一 14:00-15:40','教203'),(7,'CS302','人工智能',4,5,'2025-2026-2','周二 10:00-11:40','教301'),(8,'CS303','编译原理',4,3,'2025-2026-2','周三 08:00-09:40','教302'),(9,'MA101','高等数学',5,3,'2025-2026-1','周四 14:00-15:40','教303'),(10,'MA201','线性代数',3,3,'2025-2026-2','周五 08:00-09:40','教401'),(11,'PH101','大学物理',4,4,'2025-2026-1','周一 08:00-09:40','教402'),(12,'EN101','大学英语',3,6,'2025-2026-1','周三 14:00-15:40','教403');
/*!40000 ALTER TABLE `courses` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `enrollments`
--

DROP TABLE IF EXISTS `enrollments`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `enrollments` (
  `id` int NOT NULL AUTO_INCREMENT,
  `student_id` int NOT NULL,
  `course_id` int NOT NULL,
  `semester` varchar(20) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `enrolled_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  UNIQUE KEY `unique_enrollment` (`student_id`,`course_id`,`semester`),
  KEY `course_id` (`course_id`),
  CONSTRAINT `enrollments_ibfk_1` FOREIGN KEY (`student_id`) REFERENCES `students` (`id`) ON DELETE CASCADE,
  CONSTRAINT `enrollments_ibfk_2` FOREIGN KEY (`course_id`) REFERENCES `courses` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=53 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `enrollments`
--

LOCK TABLES `enrollments` WRITE;
/*!40000 ALTER TABLE `enrollments` DISABLE KEYS */;
INSERT INTO `enrollments` VALUES (1,1,1,'2025-2026-1','2025-10-01 13:48:42'),(2,1,2,'2025-2026-1','2025-10-01 13:48:42'),(3,1,9,'2025-2026-1','2025-10-01 13:48:42'),(4,1,11,'2025-2026-1','2025-10-01 13:48:42'),(5,1,12,'2025-2026-1','2025-10-01 13:48:42'),(6,2,1,'2025-2026-1','2025-10-01 13:48:42'),(7,2,2,'2025-2026-1','2025-10-01 13:48:42'),(8,2,9,'2025-2026-1','2025-10-01 13:48:42'),(9,2,11,'2025-2026-1','2025-10-01 13:48:42'),(10,2,12,'2025-2026-1','2025-10-01 13:48:42'),(11,3,1,'2025-2026-1','2025-10-01 13:48:42'),(12,3,2,'2025-2026-1','2025-10-01 13:48:42'),(13,3,9,'2025-2026-1','2025-10-01 13:48:42'),(14,3,11,'2025-2026-1','2025-10-01 13:48:42'),(15,3,12,'2025-2026-1','2025-10-01 13:48:42'),(16,4,1,'2025-2026-1','2025-10-01 13:48:42'),(17,4,2,'2025-2026-1','2025-10-01 13:48:42'),(18,4,9,'2025-2026-1','2025-10-01 13:48:42'),(19,4,11,'2025-2026-1','2025-10-01 13:48:42'),(20,4,12,'2025-2026-1','2025-10-01 13:48:42'),(21,5,1,'2025-2026-1','2025-10-01 13:48:42'),(22,5,2,'2025-2026-1','2025-10-01 13:48:42'),(23,5,9,'2025-2026-1','2025-10-01 13:48:42'),(24,5,11,'2025-2026-1','2025-10-01 13:48:42'),(25,5,12,'2025-2026-1','2025-10-01 13:48:42'),(26,6,1,'2025-2026-1','2025-10-01 13:48:42'),(27,6,2,'2025-2026-1','2025-10-01 13:48:42'),(28,6,9,'2025-2026-1','2025-10-01 13:48:42'),(29,6,11,'2025-2026-1','2025-10-01 13:48:42'),(30,6,12,'2025-2026-1','2025-10-01 13:48:42'),(31,7,1,'2025-2026-1','2025-10-01 13:48:42'),(32,7,2,'2025-2026-1','2025-10-01 13:48:42'),(33,7,9,'2025-2026-1','2025-10-01 13:48:42'),(34,7,11,'2025-2026-1','2025-10-01 13:48:42'),(35,7,12,'2025-2026-1','2025-10-01 13:48:42'),(36,8,9,'2025-2026-1','2025-10-01 13:48:42'),(37,8,11,'2025-2026-1','2025-10-01 13:48:42'),(38,8,12,'2025-2026-1','2025-10-01 13:48:42'),(39,9,9,'2025-2026-1','2025-10-01 13:48:42'),(40,9,11,'2025-2026-1','2025-10-01 13:48:42'),(41,9,12,'2025-2026-1','2025-10-01 13:48:42'),(42,10,9,'2025-2026-1','2025-10-01 13:48:43'),(43,10,11,'2025-2026-1','2025-10-01 13:48:43'),(44,10,12,'2025-2026-1','2025-10-01 13:48:43'),(45,1,6,'2025-2026-2','2025-10-01 13:48:43'),(46,1,7,'2025-2026-2','2025-10-01 13:48:43'),(47,1,8,'2025-2026-2','2025-10-01 13:48:43'),(48,1,10,'2025-2026-2','2025-10-01 13:48:43'),(49,2,6,'2025-2026-2','2025-10-01 13:48:43'),(50,2,7,'2025-2026-2','2025-10-01 13:48:43'),(51,2,8,'2025-2026-2','2025-10-01 13:48:43'),(52,2,10,'2025-2026-2','2025-10-01 13:48:43');
/*!40000 ALTER TABLE `enrollments` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `scores`
--

DROP TABLE IF EXISTS `scores`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `scores` (
  `id` int NOT NULL AUTO_INCREMENT,
  `student_id` int NOT NULL,
  `course_id` int NOT NULL,
  `score` float NOT NULL,
  `semester` varchar(20) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `exam_time` date DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `unique_score` (`student_id`,`course_id`,`semester`),
  KEY `course_id` (`course_id`),
  CONSTRAINT `scores_ibfk_1` FOREIGN KEY (`student_id`) REFERENCES `students` (`id`) ON DELETE CASCADE,
  CONSTRAINT `scores_ibfk_2` FOREIGN KEY (`course_id`) REFERENCES `courses` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=53 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `scores`
--

LOCK TABLES `scores` WRITE;
/*!40000 ALTER TABLE `scores` DISABLE KEYS */;
INSERT INTO `scores` VALUES (1,1,1,85.5,'2025-2026-1','2025-12-20'),(2,1,2,92,'2025-2026-1','2025-12-22'),(3,1,9,78.5,'2025-2026-1','2025-12-15'),(4,1,11,82,'2025-2026-1','2025-12-18'),(5,1,12,90,'2025-2026-1','2025-12-25'),(6,2,1,90,'2025-2026-1','2025-12-20'),(7,2,2,88.5,'2025-2026-1','2025-12-22'),(8,2,9,94,'2025-2026-1','2025-12-15'),(9,2,11,85.5,'2025-2026-1','2025-12-18'),(10,2,12,92,'2025-2026-1','2025-12-25'),(11,3,1,75,'2025-2026-1','2025-12-20'),(12,3,2,82.5,'2025-2026-1','2025-12-22'),(13,3,9,79,'2025-2026-1','2025-12-15'),(14,3,11,75,'2025-2026-1','2025-12-18'),(15,3,12,85,'2025-2026-1','2025-12-25'),(16,4,1,89,'2025-2026-1','2025-12-20'),(17,4,2,91.5,'2025-2026-1','2025-12-22'),(18,4,9,86,'2025-2026-1','2025-12-15'),(19,4,11,82.5,'2025-2026-1','2025-12-18'),(20,4,12,93,'2025-2026-1','2025-12-25'),(21,5,1,84,'2025-2026-1','2025-12-20'),(22,5,2,87.5,'2025-2026-1','2025-12-22'),(23,5,9,80,'2025-2026-1','2025-12-15'),(24,5,11,78.5,'2025-2026-1','2025-12-18'),(25,5,12,89,'2025-2026-1','2025-12-25'),(26,6,1,92.5,'2025-2026-1','2025-12-20'),(27,6,2,95,'2025-2026-1','2025-12-22'),(28,6,9,91,'2025-2026-1','2025-12-15'),(29,6,11,88,'2025-2026-1','2025-12-18'),(30,6,12,94.5,'2025-2026-1','2025-12-25'),(31,7,1,79.5,'2025-2026-1','2025-12-20'),(32,7,2,84,'2025-2026-1','2025-12-22'),(33,7,9,77,'2025-2026-1','2025-12-15'),(34,7,11,81,'2025-2026-1','2025-12-18'),(35,7,12,86.5,'2025-2026-1','2025-12-25'),(36,8,9,96,'2025-2026-1','2025-12-15'),(37,8,11,89.5,'2025-2026-1','2025-12-18'),(38,8,12,91,'2025-2026-1','2025-12-25'),(39,9,9,93.5,'2025-2026-1','2025-12-15'),(40,9,11,87,'2025-2026-1','2025-12-18'),(41,9,12,88.5,'2025-2026-1','2025-12-25'),(42,10,9,90,'2025-2026-1','2025-12-15'),(43,10,11,95.5,'2025-2026-1','2025-12-18'),(44,10,12,85,'2025-2026-1','2025-12-25'),(45,1,6,87,'2025-2026-2','2026-05-15'),(46,1,7,83.5,'2025-2026-2','2026-05-18'),(47,1,8,79,'2025-2026-2','2026-05-20'),(48,1,10,85,'2025-2026-2','2026-05-22'),(49,2,6,91.5,'2025-2026-2','2026-05-15'),(50,2,7,89,'2025-2026-2','2026-05-18'),(51,2,8,92.5,'2025-2026-2','2026-05-20'),(52,2,10,94,'2025-2026-2','2026-05-22');
/*!40000 ALTER TABLE `scores` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `students`
--

DROP TABLE IF EXISTS `students`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `students` (
  `id` int NOT NULL AUTO_INCREMENT,
  `student_id` varchar(20) COLLATE utf8mb4_unicode_ci NOT NULL,
  `name` varchar(50) COLLATE utf8mb4_unicode_ci NOT NULL,
  `gender` varchar(10) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `birth` date DEFAULT NULL,
  `class` varchar(50) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `major` varchar(50) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `user_id` int DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `student_id` (`student_id`),
  UNIQUE KEY `user_id` (`user_id`),
  CONSTRAINT `students_ibfk_1` FOREIGN KEY (`user_id`) REFERENCES `users` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=11 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `students`
--

LOCK TABLES `students` WRITE;
/*!40000 ALTER TABLE `students` DISABLE KEYS */;
INSERT INTO `students` VALUES (1,'S001','王同学','男','2003-01-15','计科2101','计算机科学与技术',8),(2,'S002','陈同学','女','2003-03-22','计科2101','计算机科学与技术',9),(3,'S003','赵同学','男','2002-11-30','计科2102','计算机科学与技术',10),(4,'S004','李同学','女','2003-05-20','计科2102','计算机科学与技术',11),(5,'S005','张同学','男','2003-07-12','软工2101','软件工程',12),(6,'S006','刘同学','女','2003-09-05','软工2101','软件工程',13),(7,'S007','黄同学','男','2003-02-28','软工2102','软件工程',14),(8,'S008','周同学','女','2002-12-10','数学2101','应用数学',15),(9,'S009','吴同学','男','2003-04-18','数学2101','应用数学',16),(10,'S010','郑同学','女','2003-08-25','物理2101','应用物理',17);
/*!40000 ALTER TABLE `students` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `teachers`
--

DROP TABLE IF EXISTS `teachers`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `teachers` (
  `id` int NOT NULL AUTO_INCREMENT,
  `teacher_id` varchar(20) COLLATE utf8mb4_unicode_ci NOT NULL,
  `name` varchar(50) COLLATE utf8mb4_unicode_ci NOT NULL,
  `gender` varchar(10) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `title` varchar(50) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `department` varchar(50) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `user_id` int DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `teacher_id` (`teacher_id`),
  UNIQUE KEY `user_id` (`user_id`),
  CONSTRAINT `teachers_ibfk_1` FOREIGN KEY (`user_id`) REFERENCES `users` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=7 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `teachers`
--

LOCK TABLES `teachers` WRITE;
/*!40000 ALTER TABLE `teachers` DISABLE KEYS */;
INSERT INTO `teachers` VALUES (1,'T001','张教授','男','教授','计算机学院',2),(2,'T002','李讲师','女','讲师','信息学院',3),(3,'T003','王副教授','男','副教授','数学学院',4),(4,'T004','刘教授','男','教授','物理学院',5),(5,'T005','陈高工','女','高级工程师','计算机学院',6),(6,'T006','林教授','女','教授','外语学院',7);
/*!40000 ALTER TABLE `teachers` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `users`
--

DROP TABLE IF EXISTS `users`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `users` (
  `id` int NOT NULL AUTO_INCREMENT,
  `username` varchar(50) COLLATE utf8mb4_unicode_ci NOT NULL,
  `password` varchar(100) COLLATE utf8mb4_unicode_ci NOT NULL,
  `role` varchar(20) COLLATE utf8mb4_unicode_ci NOT NULL,
  `name` varchar(50) COLLATE utf8mb4_unicode_ci NOT NULL,
  `created_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  `email` varchar(100) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `username` (`username`)
) ENGINE=InnoDB AUTO_INCREMENT=18 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `users`
--

LOCK TABLES `users` WRITE;
/*!40000 ALTER TABLE `users` DISABLE KEYS */;
INSERT INTO `users` VALUES (1,'admin','240be518fabd2724ddb6f04eeb1da5967448d7e831c08c8fa822809f74c720a9','admin','系统管理员','2025-10-01 13:48:42',NULL),(2,'teacher1','cde383eee8ee7a4400adf7a15f716f179a2eb97646b37e089eb8d6d04e663416','teacher','张教授','2025-10-01 13:48:42',NULL),(3,'teacher2','cde383eee8ee7a4400adf7a15f716f179a2eb97646b37e089eb8d6d04e663416','teacher','李讲师','2025-10-01 13:48:42',NULL),(4,'teacher3','cde383eee8ee7a4400adf7a15f716f179a2eb97646b37e089eb8d6d04e663416','teacher','王副教授','2025-10-01 13:48:42',NULL),(5,'teacher4','cde383eee8ee7a4400adf7a15f716f179a2eb97646b37e089eb8d6d04e663416','teacher','刘教授','2025-10-01 13:48:42',NULL),(6,'teacher5','cde383eee8ee7a4400adf7a15f716f179a2eb97646b37e089eb8d6d04e663416','teacher','陈高工','2025-10-01 13:48:42',NULL),(7,'teacher6','cde383eee8ee7a4400adf7a15f716f179a2eb97646b37e089eb8d6d04e663416','teacher','林教授','2025-10-01 13:48:42',NULL),(8,'student1','703b0a3d6ad75b649a28adde7d83c6251da457549263bc7ff45ec709b0a8448b','student','王同学','2025-10-01 13:48:42',NULL),(9,'student2','703b0a3d6ad75b649a28adde7d83c6251da457549263bc7ff45ec709b0a8448b','student','陈同学','2025-10-01 13:48:42',NULL),(10,'student3','703b0a3d6ad75b649a28adde7d83c6251da457549263bc7ff45ec709b0a8448b','student','赵同学','2025-10-01 13:48:42',NULL),(11,'student4','703b0a3d6ad75b649a28adde7d83c6251da457549263bc7ff45ec709b0a8448b','student','李同学','2025-10-01 13:48:42',NULL),(12,'student5','703b0a3d6ad75b649a28adde7d83c6251da457549263bc7ff45ec709b0a8448b','student','张同学','2025-10-01 13:48:42',NULL),(13,'student6','703b0a3d6ad75b649a28adde7d83c6251da457549263bc7ff45ec709b0a8448b','student','刘同学','2025-10-01 13:48:42',NULL),(14,'student7','703b0a3d6ad75b649a28adde7d83c6251da457549263bc7ff45ec709b0a8448b','student','黄同学','2025-10-01 13:48:42',NULL),(15,'student8','703b0a3d6ad75b649a28adde7d83c6251da457549263bc7ff45ec709b0a8448b','student','周同学','2025-10-01 13:48:42',NULL),(16,'student9','703b0a3d6ad75b649a28adde7d83c6251da457549263bc7ff45ec709b0a8448b','student','吴同学','2025-10-01 13:48:42',NULL),(17,'student10','703b0a3d6ad75b649a28adde7d83c6251da457549263bc7ff45ec709b0a8448b','student','郑同学','2025-10-01 13:48:42',NULL);
/*!40000 ALTER TABLE `users` ENABLE KEYS */;
UNLOCK TABLES;
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2025-10-01 15:26:08
