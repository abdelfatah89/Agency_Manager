-- phpMyAdmin SQL Dump
-- version 4.9.1
-- https://www.phpmyadmin.net/
--
-- Host: localhost
-- Generation Time: Mar 13, 2026 at 10:19 PM
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
  `id` int(10) UNSIGNED NOT NULL,
  `account_name` varchar(255) COLLATE utf8mb4_unicode_ci NOT NULL,
  `is_active` tinyint(1) NOT NULL DEFAULT '1',
  `created_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- --------------------------------------------------------

--
-- Table structure for table `agencies`
--

CREATE TABLE `agencies` (
  `id` int(10) UNSIGNED NOT NULL,
  `agency_name` varchar(255) COLLATE utf8mb4_unicode_ci NOT NULL,
  `agency_type` enum('CashPlus','TPE','bank','other') COLLATE utf8mb4_unicode_ci NOT NULL DEFAULT 'other',
  `total_cashplus_transaction` decimal(14,2) NOT NULL DEFAULT '0.00',
  `alimentation` decimal(14,2) NOT NULL DEFAULT '0.00',
  `balance` decimal(14,2) NOT NULL DEFAULT '0.00',
  `is_active` tinyint(1) NOT NULL DEFAULT '1',
  `created_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  `updated_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- --------------------------------------------------------

--
-- Table structure for table `clients`
--

CREATE TABLE `clients` (
  `id` int(10) UNSIGNED NOT NULL,
  `full_name` varchar(255) COLLATE utf8mb4_unicode_ci NOT NULL,
  `cin` varchar(100) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `ice` varchar(100) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `phone` varchar(50) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `address` varchar(255) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `total` decimal(14,2) NOT NULL DEFAULT '0.00',
  `total_paid` decimal(14,2) NOT NULL DEFAULT '0.00',
  `rest` decimal(14,2) NOT NULL DEFAULT '0.00',
  `created_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  `updated_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- --------------------------------------------------------

--
-- Table structure for table `cmi_transactions`
--

CREATE TABLE `cmi_transactions` (
  `id` bigint(20) UNSIGNED NOT NULL,
  `transaction_date` date NOT NULL,
  `agency_name` varchar(255) COLLATE utf8mb4_unicode_ci NOT NULL,
  `amount` decimal(14,2) NOT NULL DEFAULT '0.00',
  `paid_amount` decimal(14,2) NOT NULL DEFAULT '0.00',
  `cost` decimal(14,2) NOT NULL DEFAULT '0.00',
  `commission` decimal(14,2) NOT NULL DEFAULT '0.00',
  `alimentation` decimal(14,2) NOT NULL DEFAULT '0.00',
  `designation` text COLLATE utf8mb4_unicode_ci NOT NULL,
  `created_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- --------------------------------------------------------

--
-- Table structure for table `daily_balance`
--

CREATE TABLE `daily_balance` (
  `id` int(10) UNSIGNED NOT NULL,
  `daily_id` int(10) UNSIGNED NOT NULL,
  `opening_balance` decimal(14,2) NOT NULL DEFAULT '0.00',
  `total_output` decimal(14,2) NOT NULL DEFAULT '0.00',
  `total_input` decimal(14,2) NOT NULL DEFAULT '0.00',
  `closing_balance` decimal(14,2) NOT NULL DEFAULT '0.00',
  `created_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  `updated_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- --------------------------------------------------------

--
-- Table structure for table `daily_cash`
--

CREATE TABLE `daily_cash` (
  `id` int(10) UNSIGNED NOT NULL,
  `daily_id` int(10) UNSIGNED NOT NULL,
  `cash_10000` decimal(14,2) NOT NULL DEFAULT '0.00',
  `cash_200` decimal(14,2) NOT NULL DEFAULT '0.00',
  `cash_100` decimal(14,2) NOT NULL DEFAULT '0.00',
  `cash_50` decimal(14,2) NOT NULL DEFAULT '0.00',
  `cash_20` decimal(14,2) NOT NULL DEFAULT '0.00',
  `cash_10` decimal(14,2) NOT NULL DEFAULT '0.00',
  `cash_5` decimal(14,2) NOT NULL DEFAULT '0.00',
  `cash_1` decimal(14,2) NOT NULL DEFAULT '0.00',
  `total_cash` decimal(14,2) NOT NULL DEFAULT '0.00',
  `created_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  `updated_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- --------------------------------------------------------

--
-- Table structure for table `daily_operation_summary`
--

CREATE TABLE `daily_operation_summary` (
  `id` int(10) UNSIGNED NOT NULL,
  `daily_id` int(10) UNSIGNED NOT NULL,
  `input_transactions` decimal(14,2) NOT NULL DEFAULT '0.00',
  `input_transaction_outin` decimal(14,2) NOT NULL DEFAULT '0.00',
  `output_transactions` decimal(14,2) NOT NULL DEFAULT '0.00',
  `output_transaction_outin` decimal(14,2) NOT NULL DEFAULT '0.00',
  `input_transactions_account` decimal(14,2) NOT NULL DEFAULT '0.00',
  `output_transactions_account` decimal(14,2) NOT NULL DEFAULT '0.00',
  `total_bills` decimal(14,2) NOT NULL DEFAULT '0.00',
  `vignette` decimal(14,2) NOT NULL DEFAULT '0.00',
  `phone_recharge` decimal(14,2) NOT NULL DEFAULT '0.00',
  `retailer` decimal(14,2) NOT NULL DEFAULT '0.00',
  `cp_merchant` decimal(14,2) NOT NULL DEFAULT '0.00',
  `rest_amount` decimal(14,2) NOT NULL DEFAULT '0.00',
  `total_result` decimal(14,2) NOT NULL DEFAULT '0.00',
  `cmi_tamezmoute` decimal(14,2) NOT NULL DEFAULT '0.00',
  `created_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  `updated_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- --------------------------------------------------------

--
-- Table structure for table `daily_sessions`
--

CREATE TABLE `daily_sessions` (
  `id` int(10) UNSIGNED NOT NULL,
  `session_date` date NOT NULL,
  `status` enum('open','closed') COLLATE utf8mb4_unicode_ci NOT NULL DEFAULT 'open',
  `notes` text COLLATE utf8mb4_unicode_ci,
  `opened_by` int(10) UNSIGNED DEFAULT NULL,
  `closed_by` int(10) UNSIGNED DEFAULT NULL,
  `created_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  `updated_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- --------------------------------------------------------

--
-- Table structure for table `general_balance`
--

CREATE TABLE `general_balance` (
  `id` int(10) UNSIGNED NOT NULL,
  `daily_id` int(10) UNSIGNED NOT NULL,
  `opening_balance` decimal(14,2) NOT NULL DEFAULT '0.00',
  `agencies_balance` decimal(14,2) NOT NULL DEFAULT '0.00',
  `cashplus_balance` decimal(14,2) NOT NULL DEFAULT '0.00',
  `bank_balance` decimal(14,2) NOT NULL DEFAULT '0.00',
  `cmi_tamezmoute` decimal(14,2) NOT NULL DEFAULT '0.00',
  `closing_balance` decimal(14,2) NOT NULL DEFAULT '0.00',
  `balance_variance` decimal(14,2) NOT NULL DEFAULT '0.00',
  `created_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  `updated_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- --------------------------------------------------------

--
-- Table structure for table `transactions`
--

CREATE TABLE `transactions` (
  `id` bigint(20) UNSIGNED NOT NULL,
  `daily_id` int(10) UNSIGNED NOT NULL,
  `transaction_date` date NOT NULL,
  `client_name` varchar(255) COLLATE utf8mb4_unicode_ci NOT NULL,
  `account_name` varchar(255) COLLATE utf8mb4_unicode_ci NOT NULL,
  `designation` text COLLATE utf8mb4_unicode_ci NOT NULL,
  `amount` decimal(14,2) NOT NULL DEFAULT '0.00',
  `paid_amount` decimal(14,2) NOT NULL DEFAULT '0.00',
  `balance_due` decimal(14,2) NOT NULL DEFAULT '0.00',
  `today_in` tinyint(1) NOT NULL DEFAULT '0',
  `today_out` tinyint(1) NOT NULL DEFAULT '0',
  `created_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- --------------------------------------------------------

--
-- Table structure for table `users`
--

CREATE TABLE `users` (
  `id` int(10) UNSIGNED NOT NULL,
  `username` varchar(100) COLLATE utf8mb4_unicode_ci NOT NULL,
  `password_hash` varchar(255) COLLATE utf8mb4_unicode_ci NOT NULL,
  `role` enum('admin','manager','user') COLLATE utf8mb4_unicode_ci NOT NULL DEFAULT 'user',
  `created_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

--
-- Indexes for dumped tables
--

--
-- Indexes for table `accounts`
--
ALTER TABLE `accounts`
  ADD PRIMARY KEY (`id`),
  ADD UNIQUE KEY `uq_accounts_name` (`account_name`);

--
-- Indexes for table `agencies`
--
ALTER TABLE `agencies`
  ADD PRIMARY KEY (`id`),
  ADD UNIQUE KEY `uq_agencies_name` (`agency_name`);

--
-- Indexes for table `clients`
--
ALTER TABLE `clients`
  ADD PRIMARY KEY (`id`),
  ADD UNIQUE KEY `uq_clients_cin` (`cin`),
  ADD UNIQUE KEY `uq_clients_ice` (`ice`),
  ADD KEY `idx_clients_name` (`full_name`);

--
-- Indexes for table `cmi_transactions`
--
ALTER TABLE `cmi_transactions`
  ADD PRIMARY KEY (`id`),
  ADD KEY `idx_cmi_date` (`transaction_date`),
  ADD KEY `idx_cmi_agency_name` (`agency_name`);

--
-- Indexes for table `daily_balance`
--
ALTER TABLE `daily_balance`
  ADD PRIMARY KEY (`id`),
  ADD UNIQUE KEY `uq_daily_balance_daily_id` (`daily_id`);

--
-- Indexes for table `daily_cash`
--
ALTER TABLE `daily_cash`
  ADD PRIMARY KEY (`id`),
  ADD UNIQUE KEY `uq_daily_cash_daily_id` (`daily_id`);

--
-- Indexes for table `daily_operation_summary`
--
ALTER TABLE `daily_operation_summary`
  ADD PRIMARY KEY (`id`),
  ADD UNIQUE KEY `uq_daily_operation_summary_daily_id` (`daily_id`);

--
-- Indexes for table `daily_sessions`
--
ALTER TABLE `daily_sessions`
  ADD PRIMARY KEY (`id`),
  ADD UNIQUE KEY `uq_daily_sessions_date` (`session_date`),
  ADD KEY `fk_daily_sessions_opened_by` (`opened_by`),
  ADD KEY `fk_daily_sessions_closed_by` (`closed_by`);

--
-- Indexes for table `general_balance`
--
ALTER TABLE `general_balance`
  ADD PRIMARY KEY (`id`),
  ADD UNIQUE KEY `uq_general_balance_daily_id` (`daily_id`);

--
-- Indexes for table `transactions`
--
ALTER TABLE `transactions`
  ADD PRIMARY KEY (`id`),
  ADD KEY `idx_transactions_daily_id` (`daily_id`),
  ADD KEY `idx_transactions_date` (`transaction_date`),
  ADD KEY `idx_transactions_client_name` (`client_name`),
  ADD KEY `idx_transactions_account_name` (`account_name`);

--
-- Indexes for table `users`
--
ALTER TABLE `users`
  ADD PRIMARY KEY (`id`),
  ADD UNIQUE KEY `username` (`username`);

--
-- AUTO_INCREMENT for dumped tables
--

--
-- AUTO_INCREMENT for table `accounts`
--
ALTER TABLE `accounts`
  MODIFY `id` int(10) UNSIGNED NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT for table `agencies`
--
ALTER TABLE `agencies`
  MODIFY `id` int(10) UNSIGNED NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT for table `clients`
--
ALTER TABLE `clients`
  MODIFY `id` int(10) UNSIGNED NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT for table `cmi_transactions`
--
ALTER TABLE `cmi_transactions`
  MODIFY `id` bigint(20) UNSIGNED NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT for table `daily_balance`
--
ALTER TABLE `daily_balance`
  MODIFY `id` int(10) UNSIGNED NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT for table `daily_cash`
--
ALTER TABLE `daily_cash`
  MODIFY `id` int(10) UNSIGNED NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT for table `daily_operation_summary`
--
ALTER TABLE `daily_operation_summary`
  MODIFY `id` int(10) UNSIGNED NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT for table `daily_sessions`
--
ALTER TABLE `daily_sessions`
  MODIFY `id` int(10) UNSIGNED NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT for table `general_balance`
--
ALTER TABLE `general_balance`
  MODIFY `id` int(10) UNSIGNED NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT for table `transactions`
--
ALTER TABLE `transactions`
  MODIFY `id` bigint(20) UNSIGNED NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT for table `users`
--
ALTER TABLE `users`
  MODIFY `id` int(10) UNSIGNED NOT NULL AUTO_INCREMENT;

--
-- Constraints for dumped tables
--

--
-- Constraints for table `daily_balance`
--
ALTER TABLE `daily_balance`
  ADD CONSTRAINT `fk_daily_balance_daily` FOREIGN KEY (`daily_id`) REFERENCES `daily_sessions` (`id`) ON DELETE CASCADE ON UPDATE CASCADE;

--
-- Constraints for table `daily_cash`
--
ALTER TABLE `daily_cash`
  ADD CONSTRAINT `fk_daily_cash_daily` FOREIGN KEY (`daily_id`) REFERENCES `daily_sessions` (`id`) ON DELETE CASCADE ON UPDATE CASCADE;

--
-- Constraints for table `daily_operation_summary`
--
ALTER TABLE `daily_operation_summary`
  ADD CONSTRAINT `fk_daily_operation_summary_daily` FOREIGN KEY (`daily_id`) REFERENCES `daily_sessions` (`id`) ON DELETE CASCADE ON UPDATE CASCADE;

--
-- Constraints for table `daily_sessions`
--
ALTER TABLE `daily_sessions`
  ADD CONSTRAINT `fk_daily_sessions_closed_by` FOREIGN KEY (`closed_by`) REFERENCES `users` (`id`) ON DELETE SET NULL ON UPDATE CASCADE,
  ADD CONSTRAINT `fk_daily_sessions_opened_by` FOREIGN KEY (`opened_by`) REFERENCES `users` (`id`) ON DELETE SET NULL ON UPDATE CASCADE;

--
-- Constraints for table `general_balance`
--
ALTER TABLE `general_balance`
  ADD CONSTRAINT `fk_general_balance_daily` FOREIGN KEY (`daily_id`) REFERENCES `daily_sessions` (`id`) ON DELETE CASCADE ON UPDATE CASCADE;

--
-- Constraints for table `transactions`
--
ALTER TABLE `transactions`
  ADD CONSTRAINT `fk_transactions_daily` FOREIGN KEY (`daily_id`) REFERENCES `daily_sessions` (`id`) ON DELETE CASCADE ON UPDATE CASCADE;
COMMIT;

/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
