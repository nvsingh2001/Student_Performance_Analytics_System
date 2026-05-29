import csv
import json
from boto3.dynamodb.types import TypeDeserializer
import decimal


class DecimalEncoder(json.JSONEncoder):
    def default(self, o):
        if isinstance(o, decimal.Decimal):
            return int(o) if o % 1 == 0 else float(o)
        return super(DecimalEncoder, self).default(o)


def to_json(csv_file, json_file):
    with open(csv_file, "r") as file:
        reader = csv.DictReader(file)
        data = list(reader)

    with open(json_file, "w") as file:
        json.dump(data, file, indent=4)


def export_to_csv(page_iterator, filename):
    all_items = []
    all_keys = set()

    for page in page_iterator:
        for item in page["Items"]:
            all_items.append(item)
            all_keys.update(item.keys())

    headers = sorted(list(all_keys))

    with open(filename, "w", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(file, fieldnames=headers, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(all_items)

    print(f"Data exported to {filename}")


def export_to_json(page_iterator, filename):
    with open(filename, "w") as file:
        file.write("[\n")
        first_item = True

        for page in page_iterator:
            for item in page["Items"]:
                if not first_item:
                    file.write(",\n")

                file.write(json.dumps(item, cls=DecimalEncoder))
                first_item = False

        file.write("\n]")

    print(f"Data exported to {filename}")
