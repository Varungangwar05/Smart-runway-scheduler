from datetime import datetime, timedelta

from db_connection import connect_database


def assign_flight_to_runway(password, flight_id):
    connection = None
    cursor = None

    try:
        connection = connect_database(password)
        cursor = connection.cursor()

        cursor.execute("""
            SELECT flight_number, operation_type, scheduled_time, status
            FROM flights
            WHERE flight_id = %s
            FOR UPDATE
        """, (flight_id,))

        flight = cursor.fetchone()
        if not flight:
            raise ValueError("Flight database mein nahi mili.")

        flight_number, operation_type, scheduled_time, flight_status = flight

        cursor.execute("""
            SELECT r.runway_code
            FROM allocations a
            JOIN runways r ON r.runway_id = a.runway_id
            WHERE a.flight_id = %s
              AND a.status IN ('PLANNED', 'IN_PROGRESS')
            LIMIT 1
        """, (flight_id,))

        existing = cursor.fetchone()
        if existing:
            connection.commit()
            return existing[0]

        if flight_status != "WAITING":
            raise ValueError("Yeh flight ab WAITING status mein nahi hai.")

        end_time = scheduled_time + timedelta(minutes=10)

        if operation_type == "LANDING":
            support_column = "supports_landings"
        else:
            support_column = "supports_takeoffs"

        cursor.execute(f"""
            SELECT runway_id, runway_code
            FROM runways
            WHERE is_active = 1 AND {support_column} = 1
            ORDER BY runway_code
            FOR UPDATE
        """)
        runways = cursor.fetchall()

        for runway_id, runway_code in runways:
            cursor.execute("""
                SELECT 1
                FROM runway_maintenance
                WHERE runway_id = %s
                  AND status IN ('SCHEDULED', 'IN_PROGRESS')
                  AND start_time < %s
                  AND end_time > %s
                LIMIT 1
            """, (runway_id, end_time, scheduled_time))

            if cursor.fetchone():
                continue

            cursor.execute("""
                SELECT 1
                FROM allocations
                WHERE runway_id = %s
                  AND status IN ('PLANNED', 'IN_PROGRESS')
                  AND COALESCE(started_at, assigned_at) < %s
                  AND COALESCE(
                      ended_at,
                      DATE_ADD(
                          COALESCE(started_at, assigned_at),
                          INTERVAL 10 MINUTE
                      )
                  ) > %s
                LIMIT 1
            """, (runway_id, end_time, scheduled_time))

            if cursor.fetchone():
                continue

            cursor.execute("""
                INSERT INTO allocations (
                    flight_id,
                    runway_id,
                    started_at,
                    ended_at,
                    status
                )
                VALUES (%s, %s, %s, %s, 'PLANNED')
            """, (flight_id, runway_id, scheduled_time, end_time))

            cursor.execute("""
                UPDATE flights
                SET status = 'SCHEDULED'
                WHERE flight_id = %s
            """, (flight_id,))

            cursor.execute("""
                INSERT INTO simulation_events (
                    event_type,
                    flight_id,
                    runway_id,
                    details
                )
                VALUES (%s, %s, %s, %s)
            """, (
                "RUNWAY_ASSIGNED",
                flight_id,
                runway_id,
                f"{flight_number} assigned to {runway_code}"
            ))

            connection.commit()
            return runway_code

        raise ValueError(
            f"{flight_number} ke liye koi available runway nahi mili."
        )

    except Exception:
        if connection:
            connection.rollback()
        raise

    finally:
        if cursor:
            cursor.close()
        if connection and connection.is_connected():
            connection.close()
def complete_flight(password, flight_id):
    connection = None
    cursor = None

    try:
        connection = connect_database(password)
        cursor = connection.cursor()

        cursor.execute("""
            SELECT
                f.flight_number,
                a.allocation_id,
                a.runway_id,
                r.runway_code
            FROM flights f
            JOIN allocations a ON a.flight_id = f.flight_id
            JOIN runways r ON r.runway_id = a.runway_id
            WHERE f.flight_id = %s
              AND a.status IN ('PLANNED', 'IN_PROGRESS')
            ORDER BY a.assigned_at DESC
            LIMIT 1
            FOR UPDATE
        """, (flight_id,))

        allocation = cursor.fetchone()
        if not allocation:
            raise ValueError("Is flight ke liye active runway assignment nahi mili.")

        flight_number, allocation_id, runway_id, runway_code = allocation
        finished_at = datetime.now().replace(microsecond=0)

        cursor.execute("""
            UPDATE allocations
            SET status = 'COMPLETED', ended_at = %s
            WHERE allocation_id = %s
        """, (finished_at, allocation_id))

        cursor.execute("""
            UPDATE flights
            SET status = 'COMPLETED'
            WHERE flight_id = %s
        """, (flight_id,))

        cursor.execute("""
            UPDATE emergency_requests
            SET status = 'RESOLVED'
            WHERE flight_id = %s AND status = 'ACTIVE'
        """, (flight_id,))

        cursor.execute("""
            INSERT INTO simulation_events (
                event_type, flight_id, runway_id, details
            )
            VALUES (%s, %s, %s, %s)
        """, (
            "FLIGHT_COMPLETED",
            flight_id,
            runway_id,
            f"{flight_number} completed operation on {runway_code}"
        ))

        connection.commit()
        return flight_number, runway_code

    except Exception:
        if connection:
            connection.rollback()
        raise

    finally:
        if cursor:
            cursor.close()
        if connection and connection.is_connected():
            connection.close()