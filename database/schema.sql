CREATE DATABASE IF NOT EXISTS smart_runway_db;
USE smart_runway_db;

CREATE TABLE IF NOT EXISTS airlines (
    airline_id INT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    airline_code VARCHAR(10) NOT NULL UNIQUE,
    airline_name VARCHAR(100) NOT NULL,
    country VARCHAR(60),
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS aircraft (
    aircraft_id INT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    airline_id INT UNSIGNED NOT NULL,
    registration_number VARCHAR(20) NOT NULL UNIQUE,
    aircraft_model VARCHAR(60) NOT NULL,
    seating_capacity INT UNSIGNED NOT NULL DEFAULT 0,
    status ENUM('ACTIVE', 'MAINTENANCE', 'INACTIVE') NOT NULL DEFAULT 'ACTIVE',
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_aircraft_airline
        FOREIGN KEY (airline_id) REFERENCES airlines(airline_id)
);

CREATE TABLE IF NOT EXISTS flights (
    flight_id INT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    flight_number VARCHAR(20) NOT NULL,
    aircraft_id INT UNSIGNED NOT NULL,
    operation_type ENUM('LANDING', 'TAKEOFF') NOT NULL,
    scheduled_time DATETIME NOT NULL,
    requested_time DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    priority_level TINYINT UNSIGNED NOT NULL DEFAULT 3,
    status ENUM(
        'WAITING',
        'SCHEDULED',
        'IN_PROGRESS',
        'COMPLETED',
        'CANCELLED'
    ) NOT NULL DEFAULT 'WAITING',
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP
        ON UPDATE CURRENT_TIMESTAMP,
    CONSTRAINT fk_flights_aircraft
        FOREIGN KEY (aircraft_id) REFERENCES aircraft(aircraft_id),
    INDEX idx_flights_queue (status, priority_level, scheduled_time)
);

CREATE TABLE IF NOT EXISTS runways (
    runway_id INT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    runway_code VARCHAR(20) NOT NULL UNIQUE,
    supports_landings TINYINT(1) NOT NULL DEFAULT 1,
    supports_takeoffs TINYINT(1) NOT NULL DEFAULT 1,
    is_active TINYINT(1) NOT NULL DEFAULT 1,
    runway_length_m INT UNSIGNED
);

CREATE TABLE IF NOT EXISTS allocations (
    allocation_id INT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    flight_id INT UNSIGNED NOT NULL,
    runway_id INT UNSIGNED NOT NULL,
    assigned_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    started_at DATETIME,
    ended_at DATETIME,
    status ENUM(
        'PLANNED',
        'IN_PROGRESS',
        'COMPLETED',
        'CANCELLED'
    ) NOT NULL DEFAULT 'PLANNED',
    CONSTRAINT fk_allocations_flight
        FOREIGN KEY (flight_id) REFERENCES flights(flight_id),
    CONSTRAINT fk_allocations_runway
        FOREIGN KEY (runway_id) REFERENCES runways(runway_id),
    INDEX idx_allocations_runway_time (runway_id, started_at, ended_at)
);

CREATE TABLE IF NOT EXISTS emergency_requests (
    emergency_id INT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    flight_id INT UNSIGNED NOT NULL,
    requested_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    reason VARCHAR(255) NOT NULL,
    priority_level TINYINT UNSIGNED NOT NULL DEFAULT 1,
    status ENUM('ACTIVE', 'RESOLVED', 'CANCELLED') NOT NULL DEFAULT 'ACTIVE',
    CONSTRAINT fk_emergency_flight
        FOREIGN KEY (flight_id) REFERENCES flights(flight_id)
);

CREATE TABLE IF NOT EXISTS runway_maintenance (
    maintenance_id INT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    runway_id INT UNSIGNED NOT NULL,
    start_time DATETIME NOT NULL,
    end_time DATETIME NOT NULL,
    reason VARCHAR(255) NOT NULL,
    status ENUM(
        'SCHEDULED',
        'IN_PROGRESS',
        'COMPLETED',
        'CANCELLED'
    ) NOT NULL DEFAULT 'SCHEDULED',
    CONSTRAINT fk_maintenance_runway
        FOREIGN KEY (runway_id) REFERENCES runways(runway_id),
    INDEX idx_maintenance_window (runway_id, start_time, end_time)
);

CREATE TABLE IF NOT EXISTS simulation_events (
    event_id INT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    event_type VARCHAR(50) NOT NULL,
    event_time DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    flight_id INT UNSIGNED,
    runway_id INT UNSIGNED,
    details TEXT,
    CONSTRAINT fk_events_flight
        FOREIGN KEY (flight_id) REFERENCES flights(flight_id),
    CONSTRAINT fk_events_runway
        FOREIGN KEY (runway_id) REFERENCES runways(runway_id)
);