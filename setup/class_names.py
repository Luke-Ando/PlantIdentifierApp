import csv
import json

CSV_PATH = "static/training_data.csv"

species_to_urls = {}

with open(CSV_PATH, "r") as f:
    reader = csv.reader(f)
    for row in reader:
        species = row[0].strip()
        url = row[1].strip()
        species_to_urls.setdefault(species, []).append(url)

class_names = list(species_to_urls.keys())

with open("class_names.json", "w") as f:
    json.dump(class_names, f)
