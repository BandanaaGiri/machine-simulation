import sqlite3
import pandas as pd


class Database:

    def __init__(self, db_name="machine.db"):
        self.db_name = db_name
        self.create_table()

    def create_table(self):
        connection = sqlite3.connect(self.db_name)
        cursor = connection.cursor()

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS machine_logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                running INTEGER,
                speed INTEGER,
                temperature REAL,
                pressure REAL,
                error TEXT
            )
        """)

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS machine_events (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                event TEXT
            )
        """)

        connection.commit()
        connection.close()

    def log_machine_status(self, status):
        connection = sqlite3.connect(self.db_name)
        cursor = connection.cursor()

        cursor.execute("""
            INSERT INTO machine_logs
            (running, speed, temperature, pressure, error)
            VALUES (?, ?, ?, ?, ?)
        """, (
            int(status["running"]),
            status["speed"],
            status["temperature"],
            status["pressure"],
            status["error"]
        ))

        connection.commit()
        connection.close()

    def get_logs(self, limit=100):
        connection = sqlite3.connect(self.db_name)

        query = """
            SELECT
                timestamp,
                running,
                speed,
                temperature,
                pressure,
                error
            FROM machine_logs
            ORDER BY id DESC
            LIMIT ?
        """

        df = pd.read_sql_query(
            query,
            connection,
            params=(limit,)
        )

        connection.close()

        return df

    def log_event(self, event):
        connection = sqlite3.connect(self.db_name)
        cursor = connection.cursor()

        cursor.execute("""
            INSERT INTO machine_events (event)
            VALUES (?)
        """, (event,))

        connection.commit()
        connection.close()

    def get_events(self, limit=100):
        connection = sqlite3.connect(self.db_name)

        query = """
            SELECT
                timestamp,
                event
            FROM machine_events
            ORDER BY id DESC
            LIMIT ?
        """

        df = pd.read_sql_query(
            query,
            connection,
            params=(limit,)
        )

        connection.close()

        return df