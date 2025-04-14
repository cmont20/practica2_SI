import pandas as pd
import sqlite3
import os

database_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'database', 'data.db')


def query_to_dataframe(query):
    con = sqlite3.connect(database_path)
    df = pd.read_sql_query(query, con)
    con.close()
    return df


def top_clients_most_incidents(limit):
    return query_to_dataframe(f"""
        SELECT C.NOMBRE AS CLIENT, COUNT(*) AS INCIDENT_COUNT
        FROM TICKET T
        JOIN CLIENTE C ON T.CLIENTE_ID = C.ID_CLIENTE
        GROUP BY C.NOMBRE
        ORDER BY INCIDENT_COUNT DESC
        LIMIT {limit}
        """)


def top_incidents_type_by_resolution_time(limit):
    return query_to_dataframe(f"""
        SELECT I.NOMBRE AS INCIDENT_TYPE,
        AVG(JULIANDAY(T.FECHA_CIERRE) - JULIANDAY(T.FECHA_APERTURA)) AS AVG_RESOLUTION_TIME
        FROM TICKET T
        JOIN INCIDENTE I ON T.INCIDENCIA_ID = I.ID_INCIDENTE
        GROUP BY I.NOMBRE
        ORDER BY AVG_RESOLUTION_TIME DESC
        LIMIT {limit}
        """)
