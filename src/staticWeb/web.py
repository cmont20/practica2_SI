from flask import Flask, request, render_template, send_file
from sphinx.util import requests
from src.staticWeb.reports.pdf_reports import generate_pdf_report
from flask_login import login_required
from src.staticWeb.auth import auth_bp, login_manager
from src.staticWeb.queries import *
from src.staticWeb.model import *
from datetime import datetime


app = Flask(__name__)
app.secret_key = 'SECRET_KEY'

login_manager.init_app(app)
app.register_blueprint(auth_bp)


@app.route('/', methods=['GET', 'POST'])
@login_required
def index():
    top_x_clientes = 0
    top_x_incidents = 0
    top_x_employees = 0
    show_employees_times = False
    top_employees_df = None
    if request.method == 'POST':
        top_x_clientes = int(request.form['top_x_clientes'])
        top_x_incidents = int(request.form['top_x_incidents'])
        top_x_employees = int(request.form['top_x_employees'])
        show_employees_times = 'show_employees_times' in request.form

    top_clients_most_incidents_df = top_clients_most_incidents(top_x_clientes)
    top_incidents_type_by_resolution_time_df = top_incidents_type_by_resolution_time(top_x_incidents)

    if show_employees_times:
        top_employees_df = top_employees_by_resolution_time(top_x_employees)

    return render_template("index.html",
                           top_clients_most_incidents=top_clients_most_incidents_df.to_html(
                               classes='table table-bordered'),
                           top_incidents_type_by_resolution_time=top_incidents_type_by_resolution_time_df.to_html(
                               classes='table table-bordered'),
                           top_employees_by_time=top_employees_df.to_html(
                               classes='table table-bordered') if top_employees_df is not None else None)


def get_cve():
    url = "https://cve.circl.lu/api/last"
    response = requests.get(url)
    data = response.json()

    vulnerabilities = []

    for item in data:
        if len(vulnerabilities) >= 10:
            break
        if "vulnerabilities" in item:
            for vul in item["vulnerabilities"]:
                cve_id = vul.get("cve", "Sin ID")
                fecha = vul.get("discovery_date", "Sin fecha")
                cwe_id = vul.get("cwe", {}).get("id", "Sin CWE")
                cwe_nombre = vul.get("cwe", {}).get("name", "")
                descripcion = next(
                    (note.get("text") for note in vul.get("notes", []) if note.get("category") == "description"),
                    "Sin descripción"
                )
                attack_complexity = (
                    vul.get("scores", [{}])[0]
                    .get("cvss_v3", {})
                    .get("attackComplexity", "Sin severidad")
                )
                vulnerabilities.append({
                    "id": cve_id,
                    "fecha": fecha,
                    "descripcion": descripcion,
                    "cwe": f"{cwe_id} {cwe_nombre}",
                    "severidad": attack_complexity
                })

        elif "cveMetadata" in item and "containers" in item:
            cve_id = item.get("cveMetadata", {}).get("cveId", "Sin ID")
            fecha = item.get("cveMetadata", {}).get("datePublished", "Sin fecha")
            descripcion = next(
                (desc.get("value") for desc in item.get("containers", {}).get("cna", {}).get("descriptions", [])
                 if desc.get("lang") == "en"),
                "Sin descripción"
            )
            cwe_id = "Sin CWE"
            cwe_nombre = ""
            for pt in item.get("containers", {}).get("cna", {}).get("problemTypes", []):
                for desc in pt.get("descriptions", []):
                    if desc.get("lang") == "en":
                        cwe_id = desc.get("cweId", "Sin CWE")
                        cwe_nombre = desc.get("description", "Sin CWE-descripcion")
                        break
            severidad = next(
                (
                    m.get("cvssV3_1", {}).get("attackComplexity")
                    for m in item.get("containers", {}).get("cna", {}).get("metrics", [])
                    if "cvssV3_1" in m
                ),
                "Sin severidad"
            )
            vulnerabilities.append({
                "id": cve_id,
                "fecha": fecha,
                "descripcion": descripcion,
                "cwe": f"{cwe_id} {cwe_nombre}",
                "severidad": severidad
            })

    return vulnerabilities


@app.route("/last_vulnerabilities")
@login_required
def last_vulnerabilities():
    cves = get_cve()
    return render_template("last_vulnerabilities.html", cves=cves)


@app.route('/report/pdf')
@login_required
def report_pdf():
    from io import BytesIO
    buf = BytesIO()
    generate_pdf_report(buf, top_n=5)
    buf.seek(0)
    return send_file(
        buf,
        mimetype='application/pdf',
        # attachment_filename='reporte.pdf',
        as_attachment=False
    )


@app.route("/classify", methods=["GET", "POST"])
def classify():
    result = None
    graphic = None
    graphics = None
    if request.method == "POST":
        fecha_apertura = request.form.get("fecha_apertura")
        fecha_cierre = request.form.get("fecha_cierre")
        fecha_apertura = int(datetime.strptime(fecha_apertura, "%Y-%m-%d").strftime("%Y%m%d"))
        fecha_cierre = int(datetime.strptime(fecha_cierre, "%Y-%m-%d").strftime("%Y%m%d"))
        data = {
            "cliente": int(request.form["cliente"]),
            "fecha_apertura": fecha_apertura,
            "fecha_cierre": fecha_cierre,
            "es_mantenimiento": int(request.form["es_mantenimiento"]),
            "tipo_incidencia": int(request.form["tipo_incidencia"])
        }

        model = request.form["model"]
        prediction, graphic, graphics = predict_model(model, data)
        result = "CRÍTICO" if prediction == 1 else "NO CRÍTICO"

    return render_template("classify.html", result=result, graphic=graphic, graphics=graphics)
