import psycopg2
from config import Config


def get_db():

    return psycopg2.connect(
        Config.DATABASE_URL,
        sslmode="require"
    )
