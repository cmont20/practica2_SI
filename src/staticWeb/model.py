import json
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn import linear_model
from sklearn import tree
from sklearn.ensemble import RandomForestClassifier
from pathlib import Path

base = Path(__file__).resolve().parent
path_data = base/".."/"data"/"data_clasified.json"

# models -> regression, tree, forest


def load_data():
    with open(path_data) as file:
        data = json.load(file)
    return data


def process(data):
    tickets = data.get("tickets_emitidos", [])
    processed = []
    for ticket in tickets:
        processed.append({
            "cliente_id": ticket.get("cliente"),
            "fecha_apertura": pd.to_datetime(ticket.get("fecha_apertura")).timestamp(),
            "fecha_cierre": pd.to_datetime(ticket.get("fecha_cierre")).timestamp(),
            "es_mantenimiento": int(ticket.get("es_mantenimiento")),
            "tipo_incidencia": ticket.get("tipo_incidencia"),
            "es_critico": int(ticket.get("es_critico"))

        })

    df = pd.DataFrame(processed)

    data_x = df[['cliente_id', 'fecha_apertura', 'fecha_cierre', 'es_mantenimiento', 'tipo_incidencia']]
    data_y = df['es_critico']

    # x_train, x_test, y_train, y_test -> return value
    x_train, x_test, y_train, y_test = train_test_split(data_x, data_y, test_size=0.2)
    return x_train, x_test, y_train, y_test


def linear_regression(x_train, y_train):
    regr = linear_model.LinearRegression()
    regr.fit(x_train, y_train)
    return regr


def tree_decision(x_train, y_train):
    clf = tree.DecisionTreeClassifier()
    clf = clf.fit(x_train, y_train)
    return clf


def random_forest(x_train, y_train):
    clf = RandomForestClassifier(max_depth=2, random_state=0, n_estimators=10)
    clf.fit(x_train, y_train)
    return clf


def predict_model(model_name, input_data):
    data = load_data()
    x_train, x_test, y_train, y_test = process(data)
    prediction = None
    if model_name == "regression":
        regr_model = linear_regression(x_train, y_train)
        y_prediction = regr_model.predict([list(input_data.values())])[0]
        prediction = int(y_prediction >= 5)

    elif model_name == "tree":
        model = tree_decision(x_train, y_train)
        prediction = model.predict([list(input_data.values())])[0]

    elif model_name == "forest":
        model = random_forest(x_train, y_train)
        prediction = model.predict([list(input_data.values())])[0]

    return prediction
