import json

path = "../data/data_clasified.json"


def read_json():
    file = open(path, "r")
    data = json.load(file)
    # print(data)
    return data


if __name__ == "__main__":
    read_json()
