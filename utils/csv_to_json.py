import csv
import json


def to_json(csv_file, json_file):
    with open(csv_file, "r") as file:
        reader = csv.DictReader(file)
        data = list(reader)

    with open(json_file, "w") as file:
        json.dump(data, file, indent=4)
