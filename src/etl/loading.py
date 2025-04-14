import sqlite3
from transformation import transform_data

database = "../database/data.db"


def insert_data(data, cur):
    # Insertion of clients
    for client in data["clientes"]:
        cur.execute("INSERT OR IGNORE INTO CLIENTE (ID_CLIENTE, NOMBRE, TELEFONO, PROVINCIA) VALUES (?, ?, ?, ?)",
                    (client["id_cli"], client["nombre"], client["telefono"], client["provincia"]))

    # Employees
    for employee in data["empleados"]:
        cur.execute("INSERT OR IGNORE INTO EMPLEADO (ID_EMPLEADO, NOMBRE, NIVEL, FECHA_CONTRATO) VALUES (?, ?, ?, ?)",
                    (employee["id_emp"], employee["nombre"], employee["nivel"], employee["fecha_contrato"]))

    # Types of incidents
    for incident in data["tipos_incidentes"]:
        cur.execute("INSERT OR IGNORE INTO INCIDENTE (ID_INCIDENTE, NOMBRE) VALUES (?, ?)",
                    (incident["id_inci"], incident["nombre"]))

    # Tickets
    for ticket in data["tickets_emitidos"]:
        cur.execute("INSERT OR IGNORE INTO TICKET (CLIENTE_ID, FECHA_APERTURA, FECHA_CIERRE, ES_MANTENIMIENTO, "
                    "SATISFACCION, INCIDENCIA_ID, ES_CRITICO) VALUES (?, ?, ?, ?, ?, ?, ?)",
                    (ticket["cliente"], ticket["fecha_apertura"], ticket["fecha_cierre"], ticket["es_mantenimiento"], ticket["satisfaccion_cliente"], ticket["tipo_incidencia"], ticket["es_critico"]))

        # ident -> identifier of the ticket inserted
        ident = cur.lastrowid

        # Contacts with employees
        for contact in ticket["contactos_con_empleados"]:
            cur.execute("INSERT OR IGNORE INTO CONTACTO (TICKET_ID, EMPLEADO_ID, FECHA, TIEMPO) VALUES (?, ?, ?, ?)",
                        (ident, contact["id_emp"], contact["fecha"], contact["tiempo"]))


def loading_data():
    data_transformed = transform_data()
    con = sqlite3.connect(database)
    cur = con.cursor()

    insert_data(data_transformed, cur)
    print("Data loaded")
    con.commit()
    con.close()


if __name__ == "__main__":
    loading_data()
