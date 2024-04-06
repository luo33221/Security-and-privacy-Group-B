DROP DATABASE IF EXISTS smarthospital;
CREATE DATABASE IF NOT EXISTS smarthospital;
USE smarthospital;

DROP TABLE IF EXISTS user;
CREATE TABLE user (
    id INT(11) NOT NULL AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(20) NOT NULL UNIQUE COMMENT 'username',
    email VARCHAR(50) NOT NULL COMMENT 'email',
    password VARCHAR(32) NOT NULL COMMENT 'password',
    failed_times INT NOT NULL DEFAULT 0,
    block_time INT DEFAULT 0,
    token VARCHAR(32),
    token_start_time INT
);

DROP TABLE IF EXISTS medicalcase;
CREATE TABLE medicalcase (
    id INT(11) NOT NULL AUTO_INCREMENT PRIMARY KEY,
    patientname  VARCHAR(50) NOT NULL,
    age VARCHAR(50) NOT NULL,
    gender VARCHAR(50) NOT NULL,
    doctor VARCHAR(50) NOT NULL,
    illness VARCHAR(50) NOT NULL,
    diagnosis VARCHAR(50) NOT NULL
);
