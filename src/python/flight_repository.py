from datetime import datetime, timedelta

from db_connection import connect_database


def get_active_aircraft(password):
    connection = None
    cursor = None

    try:
        connection = connect_database(password)
        cursor = connection.cursor()
        cursor.execute("""
            SELECT aircraft_id, registration_number, aircraft_model
            FROM aircraft
            WHERE status = 'ACTIVE'
            ORDER BY registration_number
        """)

        return [
            {
                "aircraft_id": row[0],
                "registration_number": row[1],
                "aircraft_model": row[2]
            }
            for row in cursor.fetchall()
        ]

    finally:
        if cursor:
            cursor.close()
        if connection and connection.is_connected():
            connection.close()


def save_flight(password, flight, aircraft_id):
    connection = None
    cursor = None

    try:
        connection = connect_database(password)
        cursor = connection.cursor()

        now = datetime.now().replace(microsecond=0)
        requested_time = now - timedelta(minutes=flight["waiting"])
        scheduled_time = now + timedelta(minutes=10)

        cursor.execute("""
            INSERT INTO flights (
                flight_number,
                aircraft_id,
                operation_type,
                scheduled_time,
                requested_time,
                priority_level,
                status
            )
            VALUES (%s, %s, %s, %s, %s, %s, 'WAITING')
        """, (
            flight["number"],
            aircraft_id,
            flight["operation"].upper(),
            scheduled_time,
            requested_time,
            flight["priority"]
        ))

        flight_id = cursor.lastrowid

        if flight["emergency"]:
            cursor.execute("""
                INSERT INTO emergency_requests (
                    flight_id,
                    reason,
                    priority_level,
                    status
                )
                VALUES (%s, %s, 1, 'ACTIVE')
            """, (
                flight_id,
                "Emergency request entered from runway dashboard"
            ))

        connection.commit()
        return flight_id

    except Exception:
        if connection:
            connection.rollback()
        raise

    finally:
        if cursor:
            cursor.close()
        if connection and connection.is_connected():
            connection.close()


def load_waiting_flights(password):
    connection = None
    cursor = None

    try:
        connection = connect_database(password)
        cursor = connection.cursor()
        cursor.execute("""
            SELECT
                f.flight_id,
                f.flight_number,
                f.operation_type,
                f.priority_level,
                a.registration_number,
                TIMESTAMPDIFF(
                    MINUTE, f.requested_time, CURRENT_TIMESTAMP
                ) AS waiting_minutes,
                EXISTS (
                    SELECT 1
                    FROM emergency_requests e
                    WHERE e.flight_id = f.flight_id
                      AND e.status = 'ACTIVE'
                ) AS is_emergency
            FROM flights f
            JOIN aircraft a ON a.aircraft_id = f.aircraft_id
            WHERE f.status = 'WAITING'
            ORDER BY f.scheduled_time
        """)

        return cursor.fetchall()

    finally:
        if cursor:
            cursor.close()
        if connection and connection.is_connected():
            connection.close()