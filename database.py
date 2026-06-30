import psycopg2
from config import Config


def get_db():
    return psycopg2.connect(
        Config.DATABASE_URL,
        sslmode="require"
    )


def executar(sql, parametros=None):
    conn = get_db()
    cur = conn.cursor()

    if parametros:
        cur.execute(sql, parametros)
    else:
        cur.execute(sql)

    conn.commit()

    cur.close()
    conn.close()


def consultar(sql, parametros=None):
    conn = get_db()
    cur = conn.cursor()

    if parametros:
        cur.execute(sql, parametros)
    else:
        cur.execute(sql)

    dados = cur.fetchall()

    cur.close()
    conn.close()

    return dados


def consultar_um(sql, parametros=None):
    conn = get_db()
    cur = conn.cursor()

    if parametros:
        cur.execute(sql, parametros)
    else:
        cur.execute(sql)

    dado = cur.fetchone()

    cur.close()
    conn.close()

    return dado
