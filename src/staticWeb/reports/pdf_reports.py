# src/reports/pdf_reports.py

import os
import sqlite3
from io import BytesIO
from reportlab.lib.pagesizes import landscape, A4
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, Image
from reportlab.lib.styles import getSampleStyleSheet

# Usar backend no interactivo para evitar problemas de GUI
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

# Ruta absoluta a la base de datos (resuelve según la ubicación de este script)
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR,'..', '..', 'database', 'data.db')


def fetch_client_metrics(top_n=10):
    """
    Obtiene métricas del top N de clientes: total incidencias, tiempo medio de resolución (días) y satisfacción media.
    """
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute(
        """
        SELECT c.ID_CLIENTE,
               c.NOMBRE,
               COUNT(t.rowid) AS total_incidencias,
               ROUND(AVG(julianday(t.FECHA_CIERRE) - julianday(t.FECHA_APERTURA)), 2) AS tiempo_medio_dias,
               ROUND(AVG(t.SATISFACCION), 2) AS satisfaccion_media
        FROM CLIENTE c
        JOIN TICKET t ON c.ID_CLIENTE = t.CLIENTE_ID
        GROUP BY c.ID_CLIENTE
        ORDER BY total_incidencias DESC
        LIMIT ?
        """, (top_n,)
    )
    results = cursor.fetchall()
    conn.close()
    return results


def generate_charts(metrics):
    """
    Genera y devuelve gráficos como objetos BytesIO:
    - Barras de incidencias
    - Barras de tiempo medio de resolución
    - Scatter de tiempo medio vs satisfacción
    """
    names = [row[1] for row in metrics]
    totals = [row[2] for row in metrics]
    times = [row[3] for row in metrics]
    sats = [row[4] for row in metrics]

    buffers = []

    # 1) Incidencias por cliente
    plt.figure(figsize=(6,3))
    plt.bar(names, totals)
    plt.title('Incidencias por Cliente')
    plt.xticks(rotation=45, ha='right')
    plt.tight_layout()
    buf1 = BytesIO()
    plt.savefig(buf1, format='PNG')
    buf1.seek(0)
    buffers.append(buf1)
    plt.close()

    # 2) Tiempo medio de resolución
    plt.figure(figsize=(6,3))
    plt.bar(names, times)
    plt.title('Tiempo Medio de Resolución (días)')
    plt.xticks(rotation=45, ha='right')
    plt.tight_layout()
    buf2 = BytesIO()
    plt.savefig(buf2, format='PNG')
    buf2.seek(0)
    buffers.append(buf2)
    plt.close()

    # 3) Scatter: Tiempo medio vs Satisfacción
    plt.figure(figsize=(6,3))
    plt.scatter(times, sats)
    for i, name in enumerate(names):
        plt.annotate(name, (times[i], sats[i]), textcoords="offset points", xytext=(0,5), ha='center')
    plt.title('Tiempo Medio vs Satisfacción (clientes)')
    plt.xlabel('Tiempo medio (días)')
    plt.ylabel('Satisfacción media')
    plt.tight_layout()
    buf3 = BytesIO()
    plt.savefig(buf3, format='PNG')
    buf3.seek(0)
    buffers.append(buf3)
    plt.close()

    return buffers


def generate_pdf_report(output_path, top_n=10):
    """
    Genera un informe en PDF con el top N de clientes, incluyendo métricas y gráficos.

    output_path puede ser una ruta de archivo o un objeto BytesIO.
    """
    doc = SimpleDocTemplate(output_path, pagesize=landscape(A4))
    elements = []
    styles = getSampleStyleSheet()

    # Título
    elements.append(Paragraph(f"Informe: Top {top_n} Clientes con Métricas", styles['Title']))
    elements.append(Spacer(1, 12))

    # Datos y tabla
    metrics = fetch_client_metrics(top_n)
    if not metrics:
        elements.append(Paragraph("No hay datos disponibles.", styles['Normal']))
    else:
        table_data = [["Cliente", "Incidencias", "Tiempo Medio (días)", "Satisfacción Media"]]
        for _id, name, total, avg_time, avg_sat in metrics:
            table_data.append([name, total, avg_time, avg_sat])
        table = Table(table_data, colWidths=[200, 100, 120, 120])
        table.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,0), colors.gray),
            ('TEXTCOLOR', (0,0), (-1,0), colors.whitesmoke),
            ('ALIGN', (0,0), (-1,-1), 'CENTER'),
            ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
            ('BOTTOMPADDING', (0,0), (-1,0), 12),
            ('GRID', (0,0), (-1,-1), 1, colors.black),
        ]))
        elements.append(table)
        elements.append(Spacer(1, 24))

        chart_buffers = generate_charts(metrics)
        for buf in chart_buffers:
            img = Image(buf, width=400, height=200)
            elements.append(img)
            elements.append(Spacer(1, 12))

    doc.build(elements)
