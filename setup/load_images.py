# load_images.py

import galah
import os
import hashlib
import requests

# Constant Variables
NATIVE_LIST_PATH = "static/native_list.txt"
INVASIVE_LIST_PATH = "static/invasive_list.txt"

MODEL_VERSION = "v1"
TRAINING_LIST_FILE = "plant_list.txt"

TARGET_OCCURENCES = 500
NUM_NATIVE = 30
NUM_INVASIVE = 10

GALAH_REGISTERED_EMAIL = "luke@ando.id.au"

# Configure Galah
galah.galah_config(email=GALAH_REGISTERED_EMAIL)

# Load plant lists
native_plant_list = open(NATIVE_LIST_PATH).read().splitlines()
invasive_plant_list = open(INVASIVE_LIST_PATH).read().splitlines()

os.makedirs(f"model/{MODEL_VERSION}", exist_ok=True)

species_years = {}


# Count occurrences safely (FIXED)
def get_species_occurence(name, current_year, target_occurrences):
    year = current_year
    total = 0

    while total < target_occurrences and year > 1900:
        try:
            df = galah.atlas_occurrences(
                taxa=name,
                year=year
            )

            count = len(df)  # FIX: dataframe -> integer count
            total += count

        except Exception:
            count = 0

        year -= 1

    return year + 1


# Select top species, filter one per genus
def get_top_species(plant_list, num_plants):
    species_occurrences = {}

    for plant in plant_list:
        year = get_species_occurence(
            plant,
            2026,
            TARGET_OCCURENCES
        )
        species_occurrences[plant] = year

    # keep best per genus
    best_by_genus = {}

    for plant, year in species_occurrences.items():
        genus = plant.split()[0]

        if genus not in best_by_genus:
            best_by_genus[genus] = (plant, year)
        elif year > best_by_genus[genus][1]:
            best_by_genus[genus] = (plant, year)

    filtered = {p: y for p, y in best_by_genus.values()}

    sorted_species = sorted(
        filtered,
        key=filtered.get,
        reverse=True
    )

    return sorted_species[:num_plants], filtered


def process_species(species_list, status, training_file):
    for plant in species_list:

        year = species_years[plant]

        training_file.write(f"{plant},{year},{status}\n")

        try:
            plant_media = galah.atlas_media(
                taxa=plant
            )

            image_urls = plant_media["imageUrl"].dropna().tolist()
            selected_urls = image_urls[:TARGET_OCCURENCES]

        except Exception as e:
            print(f"Failed media for {plant}: {e}")
            continue

        species_dir = os.path.join(
            "../PlantIdentifier/cached_dataset",
            plant.replace(" ", "_")
        )

        os.makedirs(species_dir, exist_ok=True)

        downloaded = 0

        for url in selected_urls:
            try:
                r = requests.get(url, timeout=10)
                r.raise_for_status()

                img = r.content

                if len(img) < 2000:
                    continue

                filename = hashlib.md5(url.encode()).hexdigest() + ".jpg"
                path = os.path.join(species_dir, filename)

                if os.path.exists(path):
                    continue

                with open(path, "wb") as f:
                    f.write(img)

                downloaded += 1

            except Exception:
                continue

        print(f"{plant}: downloaded {downloaded} images")


def get_images(native_plants, invasive_plants, num_native, num_invasive):
    global species_years

    top_native, native_years = get_top_species(native_plants, num_native)
    top_invasive, invasive_years = get_top_species(invasive_plants, num_invasive)

    species_years = {**native_years, **invasive_years}

    with open(f"model/{MODEL_VERSION}/{TRAINING_LIST_FILE}", "w") as f:
        process_species(top_native, "NATIVE", f)
        process_species(top_invasive, "INVASIVE", f)


if __name__ == "__main__":
    get_images(
        native_plant_list,
        invasive_plant_list,
        NUM_NATIVE,
        NUM_INVASIVE
    )