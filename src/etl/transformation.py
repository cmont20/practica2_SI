from extraction import read_json


def transform_data():
    data = read_json()
    # Transforming data of clients (remove spaces, adjusting values, ...)
    for client in data["clientes"]:
        client["nombre"] = client["nombre"].strip()
        client["telefono"] = client.get("telefono", "None")
        client["provincia"] = client.get("provincia", "None")

    # Employee
    for employee in data["empleados"]:
        employee["nombre"] = employee["nombre"].strip()
        employee["nivel"] = employee.get("nivel", 0)
        # employee["fecha_contrato"] = employee.get("fecha_contrato", "None")

    # Ticket
    for ticket in data["tickets_emitidos"]:

        ticket["fecha_apertura"] = ticket.get("fecha_apertura", "None")
        ticket["fecha_cierre"] = ticket.get("fecha_cierre", "None")
        ticket["satisfaccion_cliente"] = ticket.get("satisfaccion_cliente", 1)
        ticket["es_mantenimiento"] = int(ticket["es_mantenimiento"])
        ticket["es_critico"] = int(ticket["es_critico"])

    # Incident
    for incident in data["tipos_incidentes"]:
        incident["nombre"] = incident["nombre"].strip()

    return data


if __name__ == "__main__":
    clean_data = transform_data()
    print(clean_data)
