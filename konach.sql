-- phpMyAdmin SQL Dump
-- version 4.9.1
-- https://www.phpmyadmin.net/
--
-- Host: localhost
-- Generation Time: Mar 12, 2026 at 06:01 PM
-- Server version: 8.0.17
-- PHP Version: 7.3.10

SET SQL_MODE = "NO_AUTO_VALUE_ON_ZERO";
SET AUTOCOMMIT = 0;
START TRANSACTION;
SET time_zone = "+00:00";


/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8mb4 */;

--
-- Database: `konach_new`
--

-- --------------------------------------------------------

--
-- Table structure for table `accounts`
--

CREATE TABLE `accounts` (
  `id` int(11) NOT NULL,
  `nom_account` varchar(255) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

--
-- Dumping data for table `accounts`
--

INSERT INTO `accounts` (`id`, `nom_account`) VALUES
(1, 'Caisse Principale'),
(2, 'Banque Attijari'),
(3, 'Banque Populaire'),
(4, 'Compte Dépenses'),
(5, 'Compte Recettes'),
(6, 'Compte Fournisseurs'),
(7, 'Compte Clients'),
(8, 'Compte Salaire'),
(9, 'Compte Épargne'),
(10, 'Compte Investissement'),
(11, 'abdelfatah');

-- --------------------------------------------------------

--
-- Table structure for table `agences`
--

CREATE TABLE `agences` (
  `id` int(11) NOT NULL,
  `nom_agence` varchar(255) NOT NULL,
  `type_agence` varchar(255) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

--
-- Dumping data for table `agences`
--

INSERT INTO `agences` (`id`, `nom_agence`, `type_agence`) VALUES
(1, 'Agence Marrakech Centre', 'CashPlus'),
(2, 'Agence Casablanca Maarif', 'TPE'),
(3, 'Agence Rabat Hassan', 'TPE'),
(4, 'abdo', 'TPE'),
(5, 'dfg', 'CashPlus'),
(6, 'amana', 'bank');

-- --------------------------------------------------------

--
-- Table structure for table `agences_trans`
--

CREATE TABLE `agences_trans` (
  `id` int(11) NOT NULL,
  `nom_agence` varchar(255) NOT NULL,
  `total_transaction_cash` int(50) NOT NULL,
  `alimentation` int(50) NOT NULL,
  `balance` int(50) NOT NULL DEFAULT '0'
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

-- --------------------------------------------------------

--
-- Table structure for table `clients`
--

CREATE TABLE `clients` (
  `id` int(11) NOT NULL,
  `nom_client` varchar(255) NOT NULL,
  `cin` varchar(255) NOT NULL,
  `ice` varchar(255) NOT NULL,
  `tel_number` varchar(50) NOT NULL,
  `adresse` varchar(255) NOT NULL,
  `total` int(50) NOT NULL DEFAULT '0',
  `total_paye` int(50) NOT NULL DEFAULT '0',
  `rest` int(50) NOT NULL DEFAULT '0'
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

--
-- Dumping data for table `clients`
--

INSERT INTO `clients` (`id`, `nom_client`, `cin`, `ice`, `tel_number`, `adresse`, `total`, `total_paye`, `rest`) VALUES
(1, 'younesse', 'PB12548', '0', '685749321', 'dr ait iken tamezmoute zagora', 26910, 25972, 938),
(2, 'Ahmed Benali', 'AB123456', '0', '612345678', 'Rue Mohammed V, Marrakech', 28533, 18256, 10277),
(3, 'Sara El Idrissi', 'CD789012', '0', '623456789', 'Hay Riad, Rabat', 114926, 107422, 7504),
(4, 'Youssef Amrani', 'EF345678', '0', '634567890', 'Maarif, Casablanca', 198461, 44, 198417),
(5, 'Khadija Tazi', 'GH901234', '0', '645678901', 'Quartier Agdal, Fes', 8004, 7701, 303),
(6, 'Omar Alaoui', 'IJ567890', '0', '656789012', 'Gueliz, Marrakech', 55046, 55043, 3),
(7, 'Salma Bennani', 'KL234567', '0', '667890123', 'Centre Ville, Tanger', 48990, 48444, 546),
(8, 'Hamza Berrada', 'MN890123', '0', '678901234', 'Hay Salam, Agadir', 5, 5, 0),
(9, 'Nadia Lahlou', 'OP456789', '0', '689012345', 'Derb Sultan, Casablanca', 0, 0, 0),
(10, 'Rachid Ouali', 'QR012345', '0', '690123456', 'Bab Doukkala, Marrakech', 0, 0, 0),
(11, 'Imane Chraibi', 'ST678901', '0', '601234567', 'Hay Hassani, Casablanca', 0, 0, 0),
(12, 'abdelfatah', 'pb45621', '0', '623458798', 'dr dr iken', 0, 0, 0);

-- --------------------------------------------------------

--
-- Table structure for table `cmi_transactions`
--

CREATE TABLE `cmi_transactions` (
  `id` int(50) NOT NULL,
  `date` date NOT NULL,
  `nom_agence` varchar(255) NOT NULL,
  `price` int(50) NOT NULL DEFAULT '0',
  `price_paye` int(50) NOT NULL DEFAULT '0',
  `cost` int(50) NOT NULL DEFAULT '0',
  `comission` int(50) NOT NULL DEFAULT '0',
  `alimentation` int(50) NOT NULL DEFAULT '0',
  `designation` text NOT NULL,
  `daily_transaction_id` int(11) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

--
-- Dumping data for table `cmi_transactions`
--

INSERT INTO `cmi_transactions` (`id`, `date`, `nom_agence`, `price`, `price_paye`, `cost`, `comission`, `alimentation`, `designation`, `daily_transaction_id`) VALUES
(15, '2026-03-08', 'Agence Casablanca Maarif', 200, 195, 5, 3, 0, 'df', 66),
(16, '2026-03-08', 'Agence Casablanca Maarif', 1500, 1470, 30, 15, 0, 'hg', 67),
(17, '2026-03-08', 'Agence Casablanca Maarif', 700, 685, 15, 8, 0, 'fg', 68),
(18, '2026-03-08', 'Agence Casablanca Maarif', 2500, 2450, 50, 25, 0, 'fg', 69),
(19, '2026-03-08', 'Agence Casablanca Maarif', 0, 0, 0, 0, 10000, 'gf', 70),
(20, '2026-03-09', 'Agence Rabat Hassan', 100, 95, 5, 4, 0, 'gf', 71),
(21, '2026-03-09', 'Agence Rabat Hassan', 0, 0, 0, 0, 2000, 'alim', 72);

-- --------------------------------------------------------

--
-- Table structure for table `daily_balences`
--

CREATE TABLE `daily_balences` (
  `id` int(11) NOT NULL,
  `daily_id` int(50) NOT NULL,
  `date` date NOT NULL,
  `first_sold` float NOT NULL DEFAULT '0',
  `total_output` float NOT NULL DEFAULT '0',
  `total_input` float NOT NULL DEFAULT '0',
  `cmi` float NOT NULL DEFAULT '0',
  `last_sold` float NOT NULL DEFAULT '0'
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

--
-- Dumping data for table `daily_balences`
--

INSERT INTO `daily_balences` (`id`, `daily_id`, `date`, `first_sold`, `total_output`, `total_input`, `cmi`, `last_sold`) VALUES
(1, 2, '2026-03-03', 425280, 80573, 0, 4645, 0),
(2, 1, '2026-03-04', 0, -28034, 0, 5648, 0),
(3, 3, '2026-03-04', 1274450, -2219, 0, 15847, 0),
(4, 4, '2026-03-04', 41930, -12323, 0, 452, 0),
(5, 5, '2026-03-04', 0, -3833.69, 90, 4321, 0),
(6, 6, '2026-03-04', 202563, -9800, 90, 10000, 0),
(7, 7, '2026-03-07', 0, 0, 0, 0, 0);

-- --------------------------------------------------------

--
-- Table structure for table `daily_caisse`
--

CREATE TABLE `daily_caisse` (
  `id` int(11) NOT NULL,
  `daily_id` int(50) NOT NULL,
  `date` date NOT NULL,
  `cash10000` float NOT NULL DEFAULT '0',
  `cash200` float NOT NULL DEFAULT '0',
  `cash100` float NOT NULL DEFAULT '0',
  `cash50` float NOT NULL DEFAULT '0',
  `cash20` float NOT NULL DEFAULT '0',
  `cash10` float NOT NULL DEFAULT '0',
  `cash5` float NOT NULL DEFAULT '0',
  `cash1` float NOT NULL DEFAULT '0',
  `total` float NOT NULL DEFAULT '0'
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

--
-- Dumping data for table `daily_caisse`
--

INSERT INTO `daily_caisse` (`id`, `daily_id`, `date`, `cash10000`, `cash200`, `cash100`, `cash50`, `cash20`, `cash10`, `cash5`, `cash1`, `total`) VALUES
(1, 1, '2026-03-03', 40, 15, 89, 146, 233, 15, 25, 1145, 425280),
(31, 2, '2026-03-03', 125, 54, 5, 252, 6, 25, 12, 120, 1274450),
(32, 3, '2026-03-04', 4, 5, 5, 5, 5, 5, 5, 5, 41930),
(33, 4, '2026-03-04', 0, 0, 0, 0, 0, 0, 0, 0, 0),
(34, 5, '2026-03-04', 0, 0, 0, 0, 0, 0, 0, 202563, 202563),
(43, 5, '2026-03-04', 0, 0, 0, 0, 0, 0, 0, 0, 0),
(44, 5, '2026-03-04', 0, 0, 0, 0, 0, 0, 0, 0, 0),
(45, 5, '2026-03-04', 0, 0, 0, 0, 0, 0, 0, 0, 0),
(46, 5, '2026-03-04', 0, 0, 0, 0, 0, 0, 0, 0, 0),
(47, 5, '2026-03-04', 0, 0, 0, 0, 0, 0, 0, 0, 0),
(48, 5, '2026-03-04', 0, 0, 0, 0, 0, 0, 0, 0, 0),
(49, 5, '2026-03-04', 0, 0, 0, 0, 0, 0, 0, 0, 0),
(50, 5, '2026-03-04', 0, 0, 0, 0, 0, 0, 0, 54, 54),
(51, 5, '2026-03-04', 0, 0, 0, 0, 0, 0, 0, 54, 54),
(52, 6, '2026-03-04', 0, 0, 0, 0, 0, 0, 0, 0, 0),
(53, 7, '2026-03-07', 0, 0, 0, 0, 0, 0, 0, 0, 0);

-- --------------------------------------------------------

--
-- Table structure for table `daily_operations`
--

CREATE TABLE `daily_operations` (
  `id` int(11) NOT NULL,
  `daily_id` int(50) NOT NULL,
  `date` date NOT NULL,
  `input_transactions` float NOT NULL DEFAULT '0',
  `input_transaction_outin` float NOT NULL DEFAULT '0',
  `output_transactions` float NOT NULL DEFAULT '0',
  `ontput_transaction_outin` float NOT NULL DEFAULT '0',
  `input_transactions_compte` float NOT NULL DEFAULT '0',
  `output_transactions_compte` float NOT NULL DEFAULT '0',
  `total_factues` float NOT NULL DEFAULT '0',
  `vinette` float NOT NULL DEFAULT '0',
  `phone_recharge` float NOT NULL DEFAULT '0',
  `detaillant` float NOT NULL DEFAULT '0',
  `cp_marchant` float NOT NULL DEFAULT '0',
  `rest` float NOT NULL DEFAULT '0',
  `total` float NOT NULL DEFAULT '0',
  `cmi_tamezmoute` float NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

--
-- Dumping data for table `daily_operations`
--

INSERT INTO `daily_operations` (`id`, `daily_id`, `date`, `input_transactions`, `input_transaction_outin`, `output_transactions`, `ontput_transaction_outin`, `input_transactions_compte`, `output_transactions_compte`, `total_factues`, `vinette`, `phone_recharge`, `detaillant`, `cp_marchant`, `rest`, `total`, `cmi_tamezmoute`) VALUES
(1, 1, '2026-03-04', 10000, 535, 42301, 2000, 3000, 7680, 2687, 5000, 25, 2700, 0, -28034, -28034, 5648),
(2, 2, '2026-03-04', 10000, 535, 42301, 2000, 3000, 7680, 2687, 5000, 25, 2700, 0, 344707, 80573, 4645),
(3, 3, '2026-03-04', 45, 12, 21300, 3534, 4, 6, 6, 65, 56, 6540, 46, 1276670, -2219, 15847),
(4, 4, '2026-03-04', 0, 120, 12000, 0, 0, 0, 0, 0, 0, 0, 0, 29607, -12323, 452),
(5, 5, '2026-03-04', 1, 1, 1, 100.11, 100, 100, 100, 100, 100, 100, 100, -3833.69, -3833.69, 4321),
(6, 6, '2026-03-04', 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 192763, -9800, 10000),
(7, 7, '2026-03-07', 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0);

-- --------------------------------------------------------

--
-- Table structure for table `daily_transactions`
--

CREATE TABLE `daily_transactions` (
  `id` int(50) NOT NULL,
  `date` date NOT NULL,
  `client_id` int(50) NOT NULL DEFAULT '0',
  `name_costumer` varchar(255) NOT NULL,
  `designation` text NOT NULL,
  `price` int(50) NOT NULL DEFAULT '0',
  `payement` int(50) NOT NULL DEFAULT '0',
  `rest` int(50) NOT NULL DEFAULT '0',
  `account` varchar(255) NOT NULL,
  `today_in` tinyint(1) NOT NULL DEFAULT '0',
  `today_out` tinyint(1) NOT NULL DEFAULT '0'
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

--
-- Dumping data for table `daily_transactions`
--

INSERT INTO `daily_transactions` (`id`, `date`, `client_id`, `name_costumer`, `designation`, `price`, `payement`, `rest`, `account`, `today_in`, `today_out`) VALUES
(1, '2026-03-01', 5, 'ieh[r9gdhgoueh', 'iugfsiuvbs', 454, 223, 231, 'Banque Populaire', 0, 0),
(2, '2026-03-01', 1, 'bworubvsoi', 'nsdoinois', 40000, 35633, 4367, 'Compte Clients', 0, 0),
(3, '2026-03-05', 7, 'Salma Bennani', 'rgffgnfnfnf', 2275, 2000, 275, 'Compte Clients', 0, 0),
(4, '2026-03-05', 0, 'Omar Alaoui', 'gnhfcg', 522, 522, 0, 'Compte Dépenses', 1, 0),
(5, '2026-03-05', 0, 'Omar Alaoui', 'cbgfbgbf', 4525, 4522, 3, 'Compte Dépenses', 1, 0),
(6, '2026-03-05', 0, 'Sara El Idrissi', 'gjghjg', 52, 25, 27, 'Compte Recettes', 0, 1),
(7, '2026-03-05', 0, 'Sara El Idrissi', 'hghfhgf', 252, 52, 200, 'Compte Recettes', 0, 1),
(8, '2026-03-05', 0, 'Khadija Tazi', 'cdhcdcd', 88, 85, 3, 'Compte Fournisseurs', 1, 0),
(9, '2026-03-05', 0, 'Khadija Tazi', '455', 8, 8, 0, 'Compte Fournisseurs', 0, 1),
(10, '2026-03-05', 0, 'Sara El Idrissi', 'dcfg', 4545, 4545, 0, 'Compte Fournisseurs', 1, 0),
(11, '2026-03-05', 0, 'Sara El Idrissi', 'الالال', 45454, 45454, 0, 'Compte Fournisseurs', 0, 1),
(12, '2026-03-05', 0, 'Omar Alaoui', 'dcfg', 4545, 4545, 0, 'Compte Clients', 1, 0),
(13, '2026-03-05', 0, 'Omar Alaoui', 'الالال', 45454, 45454, 0, 'Compte Clients', 0, 1),
(14, '2026-03-06', 0, 'ABDO', 'FDJLDBG', 56, 45, 11, 'Banque Populaire', 0, 1),
(15, '2026-03-05', 7, 'Salma Bennani', 'rgffgnfnfnf', 2275, 2000, 275, 'Compte Clients', 1, 0),
(16, '2026-03-06', 3, 'Sara El Idrissi', 'اككدز', 45, 45, 0, 'Caisse Principale', 0, 1),
(17, '2026-03-06', 3, 'Sara El Idrissi', '45', 45, 45, 0, 'Caisse Principale', 1, 0),
(18, '2026-03-05', 3, 'Sara El Idrissi', 'facture orange', 99, 100, 0, 'Compte Clients', 1, 0),
(19, '2026-03-06', 5, 'Khadija Tazi', 'you', 7800, 7500, 300, 'Banque Populaire', 0, 1),
(20, '2026-03-06', 2, 'Ahmed Benali', 'g', 5, 5, 0, 'Compte Recettes', 0, 0),
(21, '2026-03-06', 1, 'younesse', 'اههلا', 10000, 5000, 5000, 'Caisse Principale', 1, 0),
(23, '2026-03-05', 1, 'younesse', '450000', 225, 20, 205, 'Caisse Principale', 0, 0),
(24, '2026-03-04', 1, 'younesse', '45', 45, 45, 0, 'Banque Attijari', 0, 1),
(25, '2026-03-06', 3, 'Sara El Idrissi', 'dfgd', 45, 45, 0, 'Compte Fournisseurs', 0, 1),
(26, '2026-03-06', 2, 'Ahmed Benali', '45', 45, 45, 0, 'Compte Recettes', 0, 0),
(27, '2026-03-06', 1, 'younesse', 'fg', 55, 22, 33, 'Banque Attijari', 0, 0),
(28, '2026-03-06', 8, 'Hamza Berrada', 'y', 5, 5, 0, 'Banque Attijari', 0, 0),
(29, '2026-03-06', 3, 'Sara El Idrissi', '65', 45, 45, 0, 'Banque Attijari', 0, 0),
(30, '2026-03-06', 1, 'younesse', 'dfd', 45, 45, 0, 'Compte Épargne', 0, 0),
(31, '2026-03-06', 5, 'Khadija Tazi', 'ggg', 54, 54, 0, 'Compte Fournisseurs', 0, 0),
(32, '2026-03-06', 5, 'Khadija Tazi', 'ggg', 54, 54, 0, 'Compte Fournisseurs', 0, 0),
(33, '2026-03-06', 1, 'younesse', 'fdg', 45, 45, 0, 'Banque Populaire', 0, 1),
(34, '2026-03-06', 7, 'Salma Bennani', '4ghfgh', 44440, 44444, -4, 'Compte Recettes', 1, 0),
(35, '2026-03-06', 3, 'Sara El Idrissi', 'hj', 54545, 47878, 6667, 'Banque Attijari', 0, 0),
(36, '2026-03-06', 4, 'Youssef Amrani', 'IU', 55, 44, 11, 'Banque Populaire', 0, 1),
(37, '2026-03-06', 3, 'Sara El Idrissi', 'iyf', 544, 500, 44, 'Compte Recettes', 0, 0),
(38, '2026-03-05', 1, 'younesse', 'gf', 500, 0, 500, 'Caisse Principale', 0, 0),
(39, '2026-03-06', 1, 'younesse', 'df', 500, 200, 300, 'Compte Fournisseurs', 0, 0),
(43, '2026-03-07', 3, 'Sara El Idrissi', 'ekfb', 55, 88, -33, 'Compte Clients', 0, 0),
(44, '2026-03-07', 1, 'younesse', 'wrd', 595, 0, 595, 'Banque Attijari', 0, 0),
(45, '2026-03-07', 1, 'younesse', 'iuerh', 10000, 0, 10000, 'Banque Attijari', 0, 0),
(46, '2026-03-07', 1, 'younesse', 'pay', 0, 10595, -10595, 'Banque Attijari', 1, 0),
(47, '2026-03-07', 2, 'Ahmed Benali', 'khlhk', 13140, 8552, 4588, 'Compte Dépenses', 0, 1),
(48, '2026-03-07', 2, 'Ahmed Benali', 'lklk', 9878, 9000, 878, 'Compte Dépenses', 1, 0),
(49, '2026-03-07', 4, 'Youssef Amrani', 'akfjbkj', 65456, 0, 65456, 'Agence Marrakech Centre', 0, 0),
(50, '2026-03-07', 4, 'Youssef Amrani', 'fjhbd', 45500, 0, 45500, 'Agence Casablanca Maarif', 0, 0),
(51, '2026-03-07', 4, 'Youssef Amrani', 'fhgfhf', 87450, 0, 87450, 'Agence Rabat Hassan', 0, 0),
(66, '2026-03-08', 1, 'younesse', 'df', 200, 0, 200, 'Agence Casablanca Maarif', 0, 0),
(67, '2026-03-08', 1, 'younesse', 'hg', 1500, 0, 1500, 'Agence Casablanca Maarif', 0, 0),
(68, '2026-03-08', 1, 'younesse', 'fg', 700, 0, 700, 'Agence Casablanca Maarif', 0, 0),
(69, '2026-03-08', 1, 'younesse', 'fg', 2500, 0, 2500, 'Agence Casablanca Maarif', 0, 0),
(70, '2026-03-08', 1, 'younesse', 'gf', 0, 10000, -10000, 'Agence Casablanca Maarif', 0, 0),
(71, '2026-03-09', 3, 'Sara El Idrissi', 'gf', 100, 0, 100, 'Agence Rabat Hassan', 0, 0),
(72, '2026-03-09', 3, 'Sara El Idrissi', 'alim', 0, 2000, -2000, 'Agence Rabat Hassan', 0, 0),
(73, '2026-03-12', 2, 'Ahmed Benali', 'jglg', 5465, 0, 5465, 'Banque Populaire', 0, 0),
(74, '2026-03-12', 2, 'Ahmed Benali', 'jhgiygi', 0, 654, -654, 'Banque Populaire', 0, 0),
(75, '2026-03-12', 3, 'Sara El Idrissi', 'odeirhgfi', 4500, 4000, 500, 'Compte Recettes', 0, 0),
(76, '2026-03-12', 3, 'Sara El Idrissi', 'rgeho', 4600, 2600, 2000, 'Compte Recettes', 0, 0);

-- --------------------------------------------------------

--
-- Table structure for table `general_balences`
--

CREATE TABLE `general_balences` (
  `id` int(11) NOT NULL,
  `daily_id` int(50) NOT NULL,
  `date` date NOT NULL,
  `first_sold` int(50) NOT NULL DEFAULT '0',
  `agences_solde` int(11) NOT NULL DEFAULT '0',
  `cashplus_sold` int(50) NOT NULL DEFAULT '0',
  `bank_sold` int(50) NOT NULL DEFAULT '0',
  `cmi_tamezmoute` int(11) NOT NULL DEFAULT '0',
  `last_sold` int(50) NOT NULL DEFAULT '0',
  `balance_variance` int(50) NOT NULL DEFAULT '0'
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

-- --------------------------------------------------------

--
-- Table structure for table `users`
--

CREATE TABLE `users` (
  `id` int(11) NOT NULL,
  `user` varchar(255) NOT NULL,
  `password` varchar(255) NOT NULL,
  `role` varchar(255) NOT NULL DEFAULT 'user'
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

--
-- Indexes for dumped tables
--

--
-- Indexes for table `accounts`
--
ALTER TABLE `accounts`
  ADD PRIMARY KEY (`id`);

--
-- Indexes for table `agences`
--
ALTER TABLE `agences`
  ADD PRIMARY KEY (`id`);

--
-- Indexes for table `agences_trans`
--
ALTER TABLE `agences_trans`
  ADD PRIMARY KEY (`id`);

--
-- Indexes for table `clients`
--
ALTER TABLE `clients`
  ADD PRIMARY KEY (`id`);

--
-- Indexes for table `cmi_transactions`
--
ALTER TABLE `cmi_transactions`
  ADD PRIMARY KEY (`id`),
  ADD KEY `fk_cmi_daily_transaction` (`daily_transaction_id`);

--
-- Indexes for table `daily_balences`
--
ALTER TABLE `daily_balences`
  ADD PRIMARY KEY (`id`);

--
-- Indexes for table `daily_caisse`
--
ALTER TABLE `daily_caisse`
  ADD PRIMARY KEY (`id`);

--
-- Indexes for table `daily_operations`
--
ALTER TABLE `daily_operations`
  ADD PRIMARY KEY (`id`);

--
-- Indexes for table `daily_transactions`
--
ALTER TABLE `daily_transactions`
  ADD PRIMARY KEY (`id`);

--
-- Indexes for table `general_balences`
--
ALTER TABLE `general_balences`
  ADD PRIMARY KEY (`id`);

--
-- Indexes for table `users`
--
ALTER TABLE `users`
  ADD PRIMARY KEY (`id`);

--
-- AUTO_INCREMENT for dumped tables
--

--
-- AUTO_INCREMENT for table `accounts`
--
ALTER TABLE `accounts`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=12;

--
-- AUTO_INCREMENT for table `agences`
--
ALTER TABLE `agences`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=7;

--
-- AUTO_INCREMENT for table `agences_trans`
--
ALTER TABLE `agences_trans`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT for table `clients`
--
ALTER TABLE `clients`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=13;

--
-- AUTO_INCREMENT for table `cmi_transactions`
--
ALTER TABLE `cmi_transactions`
  MODIFY `id` int(50) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=22;

--
-- AUTO_INCREMENT for table `daily_balences`
--
ALTER TABLE `daily_balences`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=8;

--
-- AUTO_INCREMENT for table `daily_caisse`
--
ALTER TABLE `daily_caisse`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=54;

--
-- AUTO_INCREMENT for table `daily_operations`
--
ALTER TABLE `daily_operations`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=8;

--
-- AUTO_INCREMENT for table `daily_transactions`
--
ALTER TABLE `daily_transactions`
  MODIFY `id` int(50) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=77;

--
-- AUTO_INCREMENT for table `general_balences`
--
ALTER TABLE `general_balences`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=2;

--
-- AUTO_INCREMENT for table `users`
--
ALTER TABLE `users`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT;

--
-- Constraints for dumped tables
--

--
-- Constraints for table `cmi_transactions`
--
ALTER TABLE `cmi_transactions`
  ADD CONSTRAINT `fk_cmi_daily_transaction` FOREIGN KEY (`daily_transaction_id`) REFERENCES `daily_transactions` (`id`) ON DELETE SET NULL;
COMMIT;

/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
