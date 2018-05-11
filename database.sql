-- MySQL dump 10.13  Distrib 5.7.17, for Win64 (x86_64)
--
-- Host: 10.122.84.138    Database: userdb
-- ------------------------------------------------------
-- Server version	5.7.20-log

/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8 */;
/*!40103 SET @OLD_TIME_ZONE=@@TIME_ZONE */;
/*!40103 SET TIME_ZONE='+00:00' */;
/*!40014 SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0 */;
/*!40014 SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0 */;
/*!40101 SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='NO_AUTO_VALUE_ON_ZERO' */;
/*!40111 SET @OLD_SQL_NOTES=@@SQL_NOTES, SQL_NOTES=0 */;

--
-- Current Database: `userdb`
--

CREATE DATABASE /*!32312 IF NOT EXISTS*/ `userdb` /*!40100 DEFAULT CHARACTER SET utf8 */;

USE `userdb`;

--
-- Table structure for table `role`
--

DROP TABLE IF EXISTS `role`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `role` (
  `role_id` int(11) NOT NULL,
  `role_name` varchar(45) NOT NULL DEFAULT '普通用户',
  `role_basic` varchar(14) NOT NULL DEFAULT '1',
  PRIMARY KEY (`role_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `role`
--

LOCK TABLES `role` WRITE;
/*!40000 ALTER TABLE `role` DISABLE KEYS */;
INSERT INTO `role` VALUES (1,'普通用户','1'),(2,'数据处理人员','1,2,3'),(3,'班组管理员','1,2,3,4'),(4,'输电所管理员','1,2,3,5,6'),(5,'超级用户','1,2,3,5,6,7');
/*!40000 ALTER TABLE `role` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `role_basic`
--

DROP TABLE IF EXISTS `role_basic`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `role_basic` (
  `role_basic_id` int(11) NOT NULL,
  `role_basic_type` varchar(45) DEFAULT NULL,
  PRIMARY KEY (`role_basic_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `role_basic`
--

LOCK TABLES `role_basic` WRITE;
/*!40000 ALTER TABLE `role_basic` DISABLE KEYS */;
INSERT INTO `role_basic` VALUES (1,'read'),(2,'upload'),(3,'modify'),(4,'manager_team'),(5,'manager'),(6,'team_manager'),(7,'bgdata_manager');
/*!40000 ALTER TABLE `role_basic` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `user`
--

DROP TABLE IF EXISTS `user`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `user` (
  `user_id` varchar(20) NOT NULL,
  `user_password` varchar(32) DEFAULT NULL,
  `user_name` varchar(45) DEFAULT NULL,
  `user_phone` varchar(11) DEFAULT NULL,
  `user_team` varchar(45) DEFAULT NULL,
  `user_role` int(11) DEFAULT NULL,
  PRIMARY KEY (`user_id`),
  UNIQUE KEY `iduser_id_UNIQUE` (`user_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `user`
--

LOCK TABLES `user` WRITE;
/*!40000 ALTER TABLE `user` DISABLE KEYS */;
INSERT INTO `user` VALUES ('admin','21232f297a57a5a743894a0e4a801fc3','wuwei','13098808763','admin',5),('usr1','f558d5a44a1bc8d32be16a2b0f179bed','usr1','13098808763','班组1',1);
/*!40000 ALTER TABLE `user` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Current Database: `uav_device`
--

CREATE DATABASE /*!32312 IF NOT EXISTS*/ `uav_device` /*!40100 DEFAULT CHARACTER SET utf8 */;

USE `uav_device`;

--
-- Table structure for table `tb_approval`
--

DROP TABLE IF EXISTS `tb_approval`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `tb_approval` (
  `apply_person` varchar(45) NOT NULL COMMENT '提交申请人',
  `approval_team` varchar(45) DEFAULT NULL COMMENT '审批班组',
  `return_date` varchar(45) DEFAULT NULL,
  `device_ver` varchar(45) DEFAULT NULL COMMENT '无人机设备',
  `device_number` int(11) DEFAULT '1',
  `battery_ver` varchar(45) DEFAULT NULL COMMENT '电池',
  `battery_number` int(11) DEFAULT '1',
  `pad_ver` varchar(45) DEFAULT NULL COMMENT '配件',
  `pad_number` int(11) DEFAULT '1',
  `approval_status` int(11) DEFAULT '0',
  PRIMARY KEY (`apply_person`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COMMENT='审批流程';
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `tb_approval`
--

LOCK TABLES `tb_approval` WRITE;
/*!40000 ALTER TABLE `tb_approval` DISABLE KEYS */;
INSERT INTO `tb_approval` VALUES ('jkey','班组2',NULL,'平板',1,'mi平板',2,'平板',1,1),('markou','班组2',NULL,'无人机',2,'华为电池',1,'云台平板',1,0),('测试人','班组1',NULL,'无人机',1,'电池',1,'平板',1,0);
/*!40000 ALTER TABLE `tb_approval` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `tb_battery`
--

DROP TABLE IF EXISTS `tb_battery`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `tb_battery` (
  `battery_id` int(11) NOT NULL,
  `battery_ver` varchar(45) DEFAULT NULL,
  `battery_type` varchar(45) DEFAULT NULL,
  `battery_fact` varchar(45) DEFAULT NULL,
  `battery_date` varchar(45) DEFAULT NULL,
  `user_team` varchar(45) DEFAULT NULL,
  `battery_status` varchar(10) DEFAULT NULL,
  `battery_use_number` int(11) DEFAULT '0',
  PRIMARY KEY (`battery_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `tb_battery`
--

LOCK TABLES `tb_battery` WRITE;
/*!40000 ALTER TABLE `tb_battery` DISABLE KEYS */;
INSERT INTO `tb_battery` VALUES (21,'diachi','华为电池','蔡彬','2018-05-07','班组1','在库',2),(22,'yuntai','yuntai电池','蔡彬','2018-05-07','班组2','出库',1),(23,'huawei','电池','蔡彬','2018-05-07','班组2','在库',0);
/*!40000 ALTER TABLE `tb_battery` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `tb_device`
--

DROP TABLE IF EXISTS `tb_device`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `tb_device` (
  `device_id` int(20) NOT NULL,
  `device_ver` varchar(45) DEFAULT NULL,
  `device_type` varchar(45) DEFAULT NULL,
  `uad_code` varchar(45) DEFAULT NULL,
  `device_fact` varchar(45) DEFAULT NULL,
  `device_date` varchar(45) DEFAULT NULL,
  `user_team` varchar(45) DEFAULT NULL,
  `uad_camera` varchar(45) DEFAULT '相机型号',
  `uav_yuntai` varchar(45) DEFAULT '云台型号',
  `uad_rcontrol` varchar(45) DEFAULT '遥控器类型',
  `device_status` varchar(10) DEFAULT NULL,
  `device_use_number` int(10) DEFAULT '0',
  PRIMARY KEY (`device_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COMMENT='无人机设备管理';
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `tb_device`
--

LOCK TABLES `tb_device` WRITE;
/*!40000 ALTER TABLE `tb_device` DISABLE KEYS */;
INSERT INTO `tb_device` VALUES (11,'无人机','DJI','123456','蔡彬','2018-05-07','班组1','DJI','DJI','DJI','在库',9),(12,'HUAWEIp8','HUAWEIp8','78963','蔡彬','2018-05-07','班组2','HUAWEIp8','HUAWEIp8','HUAWEIp8','在库',1),(13,'YUNTAI','YUNTAI','123156','蔡彬','2018-05-07','班组2','YUNTAI','YUNTAI','YUNTAI','维修',3);
/*!40000 ALTER TABLE `tb_device` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `tb_fault`
--

DROP TABLE IF EXISTS `tb_fault`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `tb_fault` (
  `fault_id` int(11) NOT NULL AUTO_INCREMENT,
  `device_id` int(20) NOT NULL,
  `device_ver` varchar(45) DEFAULT NULL,
  `fault_date` varchar(45) DEFAULT NULL,
  `fault_reason` varchar(45) DEFAULT NULL,
  `fault_deal` varchar(45) DEFAULT '故障处理方法',
  `fault_finished` int(11) DEFAULT NULL,
  PRIMARY KEY (`fault_id`)
) ENGINE=InnoDB AUTO_INCREMENT=4 DEFAULT CHARSET=utf8 COMMENT='故障管理';
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `tb_fault`
--

LOCK TABLES `tb_fault` WRITE;
/*!40000 ALTER TABLE `tb_fault` DISABLE KEYS */;
INSERT INTO `tb_fault` VALUES (1,2,'JL400','2018-05-07','精灵3无人机','故障处理方法',NULL),(2,3,'HUWp8','2018-05-07','华为P8','故障处理方法',NULL),(3,1,'YUNTAI','2018-05-08','云台无人机','故障处理方法',NULL);
/*!40000 ALTER TABLE `tb_fault` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `tb_fault_report`
--

DROP TABLE IF EXISTS `tb_fault_report`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `tb_fault_report` (
  `fault_report_id` int(11) NOT NULL AUTO_INCREMENT,
  `fault_report_device_id` int(11) DEFAULT NULL,
  `fault_report_line_name` varchar(45) DEFAULT NULL,
  `fault_report_towerRange` varchar(45) DEFAULT NULL,
  `fault_report_date` varchar(45) DEFAULT NULL,
  `fault_report_flyer` varchar(45) DEFAULT NULL,
  `fault_report_wether` varchar(45) DEFAULT NULL,
  `fault_report_observer` varchar(45) DEFAULT NULL,
  `fault_time` varchar(45) DEFAULT NULL,
  `fault_crash_position` varchar(256) DEFAULT NULL,
  `fault_crash_desc` varchar(1024) DEFAULT NULL,
  `fault_crash_operation` varchar(1024) DEFAULT NULL,
  `fault_crash_damage` varchar(1024) DEFAULT NULL,
  `fault_crash_electric` varchar(1024) DEFAULT NULL,
  `fault_crash_around` varchar(1024) DEFAULT NULL,
  PRIMARY KEY (`fault_report_id`)
) ENGINE=InnoDB AUTO_INCREMENT=4 DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `tb_fault_report`
--

LOCK TABLES `tb_fault_report` WRITE;
/*!40000 ALTER TABLE `tb_fault_report` DISABLE KEYS */;
INSERT INTO `tb_fault_report` VALUES (1,1,'DJI','10km','2018-05-07','飞鸟','bdta','蔡彬','2018-05-08','广州','yisui','手动操作','测试数据','电动的','拐角处'),(2,2,'YUNTAI','2KM','2018-05-08','精灵3无人机','测试','蔡彬','2018-05-09','东莞','sfs','自动','测试2','测试数据策士','公路公里'),(3,3,'HUAWEI','4KM','2018-05-02','云台无人机','aga','蔡彬','2018-05-07','广州','sgt','手动','测试三','测试三数据','雨天');
/*!40000 ALTER TABLE `tb_fault_report` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `tb_manager`
--

DROP TABLE IF EXISTS `tb_manager`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `tb_manager` (
  `manager_id` int(11) NOT NULL AUTO_INCREMENT,
  `device_id` int(20) NOT NULL,
  `device_ver` varchar(50) NOT NULL,
  `device_type` varchar(50) DEFAULT NULL,
  `user_team` varchar(50) DEFAULT NULL,
  `borrower_name` varchar(45) DEFAULT NULL,
  `borrow_date` varchar(45) DEFAULT NULL,
  `approver_name` varchar(45) DEFAULT NULL,
  `manager_status` varchar(10) DEFAULT NULL COMMENT '包括借用和归还',
  `return_date` varchar(45) DEFAULT NULL,
  `return_desc` varchar(1024) DEFAULT NULL COMMENT '描述',
  PRIMARY KEY (`manager_id`),
  UNIQUE KEY `manager_id_UNIQUE` (`manager_id`)
) ENGINE=InnoDB AUTO_INCREMENT=21 DEFAULT CHARSET=utf8 COMMENT='出入库管理';
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `tb_manager`
--

LOCK TABLES `tb_manager` WRITE;
/*!40000 ALTER TABLE `tb_manager` DISABLE KEYS */;
INSERT INTO `tb_manager` VALUES (1,1,'HUAWEI','无人机','班组1','蔡彬','2018-05-07','蔡彬','归还','2018-05-07',NULL),(2,2,'YUNTAI','电池','班组2','蔡彬','2018-05-01','蔡彬','归还',NULL,NULL),(3,3,'DJI','无人机','班组3','周逸永','20118-05-07','蔡彬','归还','2018-05-07',NULL),(14,11,'无人机','DJI','班组1','usr1','2018/5/10','admin','归还','2018-05-18','ddd'),(15,11,'无人机','DJI','班组1','usr1','2018/5/10','admin','归还','2018-05-18','ddd'),(16,11,'无人机','DJI','班组1','usr1','2018/5/10','admin','归还','2018-05-18','ddd'),(17,11,'无人机','DJI','班组1','usr1','2018/5/10','admin','归还','2018-05-18','ddd'),(18,11,'无人机','DJI','班组1','usr1','2018/5/10','admin','归还','2018-05-18','ddd'),(19,11,'无人机','DJI','班组1','usr1','2018/5/10','admin','归还','2018-05-18','ddd'),(20,11,'无人机','DJI','班组1','usr1','2018/5/10','admin','归还','2018-05-18','ddd');
/*!40000 ALTER TABLE `tb_manager` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `tb_pad`
--

DROP TABLE IF EXISTS `tb_pad`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `tb_pad` (
  `pad_id` int(11) NOT NULL,
  `pad_ver` varchar(45) DEFAULT NULL,
  `pad_type` varchar(45) DEFAULT NULL,
  `pad_fact` varchar(45) DEFAULT NULL,
  `pad_date` varchar(45) DEFAULT NULL,
  `user_team` varchar(45) DEFAULT NULL,
  `pad_status` varchar(45) DEFAULT NULL,
  `pad_use_number` int(11) DEFAULT '0',
  PRIMARY KEY (`pad_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COMMENT='平板\n';
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `tb_pad`
--

LOCK TABLES `tb_pad` WRITE;
/*!40000 ALTER TABLE `tb_pad` DISABLE KEYS */;
INSERT INTO `tb_pad` VALUES (31,'apid','平板','供电公司','2018-05-07','班组1','在库',0),(32,'MIpad','平板','供电公司','2018-05-07','班组2','出库',1),(33,'HUAWEIpad','平板','供电公司','2018-05-07','班组1','在库',3);
/*!40000 ALTER TABLE `tb_pad` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `tb_parts`
--

DROP TABLE IF EXISTS `tb_parts`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `tb_parts` (
  `parts_id` int(11) NOT NULL,
  `parts_ver` varchar(45) DEFAULT NULL,
  `parts_type` varchar(45) DEFAULT NULL,
  `parts_fact` varchar(45) DEFAULT NULL,
  `parts_date` varchar(45) DEFAULT NULL,
  `user_team` varchar(45) DEFAULT NULL,
  `parts_status` varchar(10) DEFAULT NULL,
  `parts_use_number` int(11) DEFAULT '0',
  PRIMARY KEY (`parts_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COMMENT='配件';
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `tb_parts`
--

LOCK TABLES `tb_parts` WRITE;
/*!40000 ALTER TABLE `tb_parts` DISABLE KEYS */;
INSERT INTO `tb_parts` VALUES (41,'无人机','无人机配件','蔡彬','2018-05-07','班组1','在库',0),(42,'华为P8','华为P8配件','蔡彬','2018-05-07','班组2','出库',0),(43,'云台','云台配件','蔡彬','2018-05-07','班组3','维修',0);
/*!40000 ALTER TABLE `tb_parts` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Current Database: `jiangmendb`
--

CREATE DATABASE /*!32312 IF NOT EXISTS*/ `jiangmendb` /*!40100 DEFAULT CHARACTER SET utf8 */;

USE `jiangmendb`;

--
-- Table structure for table `tb_lines`
--

DROP TABLE IF EXISTS `tb_lines`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `tb_lines` (
  `lines_id` int(11) NOT NULL,
  `lines_name` varchar(45) DEFAULT NULL,
  `lines_construct_date` varchar(45) DEFAULT NULL,
  `lines_voltage` varchar(45) DEFAULT NULL,
  `lines_work_team` varchar(45) DEFAULT NULL,
  `lines_incharge` varchar(45) DEFAULT NULL COMMENT '负责人',
  PRIMARY KEY (`lines_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COMMENT='线路';
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `tb_lines`
--

LOCK TABLES `tb_lines` WRITE;
/*!40000 ALTER TABLE `tb_lines` DISABLE KEYS */;
/*!40000 ALTER TABLE `tb_lines` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `tb_tower`
--

DROP TABLE IF EXISTS `tb_tower`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `tb_tower` (
  `tower_id` int(11) NOT NULL COMMENT 'id主键',
  `tower_line` varchar(45) DEFAULT NULL,
  `tower_idx` int(11) DEFAULT NULL COMMENT '杆塔编号',
  `tower_type` varchar(45) DEFAULT NULL,
  `tower_height` float DEFAULT NULL COMMENT '杆塔高度',
  `tower_lat` float DEFAULT NULL,
  `tower_lng` float DEFAULT NULL,
  `tower_elevation` float DEFAULT NULL COMMENT '杆塔海拔高度',
  PRIMARY KEY (`tower_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `tb_tower`
--

LOCK TABLES `tb_tower` WRITE;
/*!40000 ALTER TABLE `tb_tower` DISABLE KEYS */;
/*!40000 ALTER TABLE `tb_tower` ENABLE KEYS */;
UNLOCK TABLES;
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2018-05-11 17:38:40
