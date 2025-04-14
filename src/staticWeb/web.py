from flask import Flask, render_template, request

from staticWeb import queries

app = Flask(__name__)


@app.route('/', methods=['GET', 'POST'])
def index():
    top_x_clientes = 0
    top_x_incidents = 0

    if request.method == 'POST':
        top_x_clientes = int(request.form['top_x_clientes'])
        top_x_incidents = int(request.form['top_x_incidents'])

    top_clients_most_incidents_df = queries.top_clients_most_incidents(top_x_clientes)
    top_incidents_type_by_resolution_time_df = queries.top_incidents_type_by_resolution_time(top_x_incidents)

    return render_template("index.html",
                           top_clients_most_incidents=top_clients_most_incidents_df.to_html(
                               classes='table table-bordered'),
                           top_incidents_type_by_resolution_time=top_incidents_type_by_resolution_time_df.to_html(
                               classes='table table-bordered'))
