from db_connection import connect_database


def load_recent_events(password, limit=20):
    connection = None
    cursor = None

    try:
        connection = connect_database(password)
        cursor = connection.cursor(dictionary=True)

        cursor.execute("""
            SELECT
                e.event_id,
                e.event_type,
                e.event_time,
                f.flight_number,
                r.runway_code,
                e.details
            FROM simulation_events e
            LEFT JOIN flights f ON f.flight_id = e.flight_id
            LEFT JOIN runways r ON r.runway_id = e.runway_id
            ORDER BY e.event_time DESC, e.event_id DESC
            LIMIT %s
        """, (limit,))

        return cursor.fetchall()

    finally:
        if cursor:
            cursor.close()
        if connection and connection.is_connected():
            connection.close()