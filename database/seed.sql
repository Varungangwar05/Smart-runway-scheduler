USE smart_runway_db;

-- Demo airlines
INSERT IGNORE INTO airlines (airline_code, airline_name, country)
VALUES
    ('DA', 'Demo Air', 'India'),
    ('CW', 'Campus Wings', 'India');

-- Demo aircraft
INSERT IGNORE INTO aircraft
    (airline_id, registration_number, aircraft_model, seating_capacity)
SELECT airline_id, 'DA-A320-01', 'Airbus A320', 180
FROM airlines
WHERE airline_code = 'DA';

INSERT IGNORE INTO aircraft
    (airline_id, registration_number, aircraft_model, seating_capacity)
SELECT airline_id, 'DA-A320-02', 'Airbus A320', 180
FROM airlines
WHERE airline_code = 'DA';

INSERT IGNORE INTO aircraft
    (airline_id, registration_number, aircraft_model, seating_capacity)
SELECT airline_id, 'CW-B737-01', 'Boeing 737', 189
FROM airlines
WHERE airline_code = 'CW';

-- Demo runways
INSERT IGNORE INTO runways
    (runway_code, supports_landings, supports_takeoffs, is_active, runway_length_m)
VALUES
    ('RWY-09', 1, 1, 1, 3200),
    ('RWY-27', 1, 1, 1, 2800);

-- Demo flights for tomorrow
INSERT INTO flights
    (flight_number, aircraft_id, operation_type, scheduled_time,
     requested_time, priority_level, status)
SELECT
    'DA101', aircraft_id, 'LANDING',
    TIMESTAMP(CURRENT_DATE + INTERVAL 1 DAY, '09:00:00'),
    CURRENT_TIMESTAMP, 3, 'WAITING'
FROM aircraft
WHERE registration_number = 'DA-A320-01'
AND NOT EXISTS (
    SELECT 1
    FROM flights
    WHERE flight_number = 'DA101'
      AND scheduled_time = TIMESTAMP(CURRENT_DATE + INTERVAL 1 DAY, '09:00:00')
);

INSERT INTO flights
    (flight_number, aircraft_id, operation_type, scheduled_time,
     requested_time, priority_level, status)
SELECT
    'CW202', aircraft_id, 'TAKEOFF',
    TIMESTAMP(CURRENT_DATE + INTERVAL 1 DAY, '09:15:00'),
    CURRENT_TIMESTAMP, 2, 'WAITING'
FROM aircraft
WHERE registration_number = 'CW-B737-01'
AND NOT EXISTS (
    SELECT 1
    FROM flights
    WHERE flight_number = 'CW202'
      AND scheduled_time = TIMESTAMP(CURRENT_DATE + INTERVAL 1 DAY, '09:15:00')
);

INSERT INTO flights
    (flight_number, aircraft_id, operation_type, scheduled_time,
     requested_time, priority_level, status)
SELECT
    'DA103', aircraft_id, 'LANDING',
    TIMESTAMP(CURRENT_DATE + INTERVAL 1 DAY, '09:20:00'),
    CURRENT_TIMESTAMP, 1, 'WAITING'
FROM aircraft
WHERE registration_number = 'DA-A320-02'
AND NOT EXISTS (
    SELECT 1
    FROM flights
    WHERE flight_number = 'DA103'
      AND scheduled_time = TIMESTAMP(CURRENT_DATE + INTERVAL 1 DAY, '09:20:00')
);

-- Emergency request for DA103
INSERT INTO emergency_requests
    (flight_id, reason, priority_level, status)
SELECT flight_id, 'Medical emergency simulation', 1, 'ACTIVE'
FROM flights
WHERE flight_number = 'DA103'
  AND scheduled_time = TIMESTAMP(CURRENT_DATE + INTERVAL 1 DAY, '09:20:00')
  AND NOT EXISTS (
      SELECT 1
      FROM emergency_requests
      WHERE emergency_requests.flight_id = flights.flight_id
        AND emergency_requests.status = 'ACTIVE'
  );

-- Maintenance window for RWY-27
INSERT INTO runway_maintenance
    (runway_id, start_time, end_time, reason, status)
SELECT
    runway_id,
    TIMESTAMP(CURRENT_DATE + INTERVAL 2 DAY, '22:00:00'),
    TIMESTAMP(CURRENT_DATE + INTERVAL 3 DAY, '02:00:00'),
    'Scheduled runway inspection simulation',
    'SCHEDULED'
FROM runways
WHERE runway_code = 'RWY-27'
AND NOT EXISTS (
    SELECT 1
    FROM runway_maintenance
    WHERE runway_maintenance.runway_id = runways.runway_id
      AND runway_maintenance.start_time =
          TIMESTAMP(CURRENT_DATE + INTERVAL 2 DAY, '22:00:00')
);