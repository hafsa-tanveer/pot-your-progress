import oracledb
import os

# === CREDENTIALS (REVERTED) ===
# We are using the simple user that we confirmed works.
DB_USER = "pot_your_progress"
DB_PASSWORD = "123"

# The DSN that worked for you
DB_DSN = "//localhost:1521/orclpdb"


def get_db_connection():
    try:
        connection = oracledb.connect(
            user=DB_USER,
            password=DB_PASSWORD,
            dsn=DB_DSN
        )
        return connection
    except oracledb.Error as e:
        print(f"❌ Database Connection Error: {e}")
        return None
