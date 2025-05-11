import json
import pandas as pd
import matplotlib.pyplot as plt
import graphviz
from sklearn.model_selection import train_test_split
from sklearn import linear_model
from sklearn import tree
from sklearn.ensemble import RandomForestClassifier
from pathlib import Path

base = Path(__file__).resolve().parent
path_data = base / ".." / "data" / "data_clasified.json"
image_path = base / "static"


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
    graphic = None
    graphics = None
    if model_name == "regression":
        regr_model = linear_regression(x_train, y_train)
        y_pred = regr_model.predict([list(input_data.values())])
        y_prediction = y_pred[0]
        prediction = int(y_prediction >= 5)
        graphic, graphics = plot_regression(y_test, y_pred)

    elif model_name == "tree":
        model = tree_decision(x_train, y_train)
        prediction = model.predict([list(input_data.values())])[0]
        graphic, graphics = tree_graph(model)

    elif model_name == "forest":
        model = random_forest(x_train, y_train)
        prediction = model.predict([list(input_data.values())])[0]
        graphic, graphics = export_random_forest(model)

    return prediction, graphic, graphics


def plot_regression(y_test, y_pred):
    plt.figure()
    plt.scatter(range(len(y_test)), y_test, color="black", label="Datos reales")
    plt.scatter(range(len(y_pred)), y_pred, color="blue", label="Predicciones")
    plt.title("Regresión lineal: Predicción de criticidad")
    plt.xlabel("ID Cliente (aproximación visual)")
    plt.ylabel("Crítico (1) / No crítico (0)")
    plt.legend()
    real_path = image_path / "regression.png"
    plt.savefig(real_path)
    plt.close()
    return "regression.png", None


def tree_graph(clf):
    dot_data = tree.export_graphviz(clf, out_file=None, filled=True, rounded=True, special_characters=True,
                                    feature_names=['cliente_id', 'fecha_apertura', 'fecha_cierre', 'es_mantenimiento',
                                                   'tipo_incidencia'],
                                    class_names=['No crítico', 'Crítico'])
    graph = graphviz.Source(dot_data)
    graph.format = 'png'
    graph.render(filename="tree", directory=image_path, format="png", cleanup=True)
    return "tree.png", None


"""def export_random_forest(clf):
    estimator = clf.estimators_[0]
    dot_data = tree.export_graphviz(estimator, out_file=None, filled=True, rounded=True, special_characters=True,
                                    feature_names=['cliente_id', 'fecha_apertura', 'fecha_cierre', 'es_mantenimiento',
                                                   'tipo_incidencia'],
                                    class_names=['No crítico', 'Crítico'])

    graph = graphviz.Source(dot_data)
    graph.format = 'png'
    output_path = image_path / "random_forest"
    graph.render(output_path, cleanup=True)
    return "random_forest.png"
"""


def export_random_forest(clf):
    graphics = []
    for i, estimator in enumerate(clf.estimators_):
        dot_data = tree.export_graphviz(estimator, out_file=None, filled=True, rounded=True, special_characters=True,
                                        feature_names=['cliente_id', 'fecha_apertura', 'fecha_cierre',
                                                       'es_mantenimiento',
                                                       'tipo_incidencia'],
                                        class_names=['No crítico', 'Crítico'])
        graph = graphviz.Source(dot_data)
        graph.format = "png"
        output_path = image_path / f"random_forest{i + 1}"
        graph.render(output_path, cleanup=True)
        graphics.append(f"random_forest{i + 1}.png")

    return None, graphics
