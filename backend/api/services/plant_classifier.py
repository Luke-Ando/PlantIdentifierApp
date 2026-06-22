import csv
import json
import time

import numpy as np
import onnxruntime as ort

from PIL import Image, ImageOps
from django.conf import settings

from api.metrics_service import metrics_service


IMG_SIZE = (300, 300)


class PlantClassifierService:

    def __init__(self):

        model_path = settings.BASE_DIR / "static" / "model.onnx"

        self.session = ort.InferenceSession(
            str(model_path),
            providers=["CPUExecutionProvider"]
        )

        self.input_name = self.session.get_inputs()[0].name
        self.output_names = [
            output.name
            for output in self.session.get_outputs()
        ]

        with open(
            settings.BASE_DIR / "class_names.json",
            "r"
        ) as f:
            self.species_list = json.load(f)

        self.species_status_map = {}

        with open(
            settings.BASE_DIR / "static" / "training_data.csv",
            "r"
        ) as f:

            reader = csv.reader(f)

            for row in reader:
                species = row[0].strip()
                status = row[2].strip().upper()

                self.species_status_map[
                    species
                ] = status

    def preprocess(self, image_file):

        start = time.perf_counter()

        image_file.seek(0)

        img = Image.open(image_file)

        img = ImageOps.exif_transpose(img)

        img = img.convert("RGB")

        img = img.resize(
            IMG_SIZE,
            Image.BILINEAR
        )

        arr = np.asarray(img).astype(
            "float32"
        )

        arr = arr / 255.0
        arr = (arr - 0.5) * 2.0

        arr = np.expand_dims(
            arr,
            axis=0
        )

        preprocessing_ms = (
            time.perf_counter() - start
        ) * 1000

        metrics_service.record_preprocessing(
            preprocessing_ms
        )

        return arr

    def classify(self, image_file):

        arr = self.preprocess(image_file)

        start = time.perf_counter()

        species_pred, status_pred = (
            self.session.run(
                self.output_names,
                {
                    self.input_name: arr
                }
            )
        )

        inference_ms = (
            time.perf_counter() - start
        ) * 1000

        metrics_service.record_inference(
            inference_ms
        )

        species_idx = int(
            np.argmax(species_pred[0])
        )

        species_name = (
            self.species_list[species_idx]
        )

        species_conf = float(
            np.max(species_pred[0])
        )

        sorted_idx = np.argsort(
            species_pred[0]
        )[::-1][:3]

        top3_species = [
            self.species_list[i]
            for i in sorted_idx
        ]

        top3_conf = [
            float(species_pred[0][i])
            for i in sorted_idx
        ]

        status = (
            self.species_status_map[
                species_name
            ]
        )

        status_conf = float(
            status_pred[0][0]
        )

        return {
            "species": species_name,
            "species_confidence": species_conf,
            "status": status,
            "status_confidence": status_conf,
            "top_3_species": top3_species,
            "top_3_confidences": top3_conf
        }


classifier_service = (
    PlantClassifierService()
)