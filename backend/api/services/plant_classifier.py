# plant_classifer.py
# This module loads machine learning model to classify, and used it to classify
# plant species their status.

# Imports
# Data Processing
import csv
import json

# Utilities
import time
from django.conf import settings # Access the project settings.
from .metrics_service import metrics_service # Access to custom
# service that controls access to the metric monitoring service.

# Image Processing
from PIL import Image, ImageOps # Used to load and manipulate images.
import numpy as np # Used to represent images as numerical arrays.

# Machine Learning Processing
import onnxruntime as ort # Open Neural Network Exchange (ONNX) -
# allows hosting service to run the machine learning model.

# Constant Variables
IMG_SIZE = (300, 300)

# Creates a reusable service class for classification
class PlantClassifierService:
    def __init__(self):
        # Access the model.
        model_path = settings.BASE_DIR / "static" / "model.onnx"
        self.session = ort.InferenceSession(
            str(model_path),
            providers=["CPUExecutionProvider"]
        ) # Loads file into memory as an attribute of the class, using CPU.
        # ensures that the model only needs to be loaded once.

        self.input_name = self.session.get_inputs()[0].name # Extracts inputs
        # to expect from the moel.
        self.output_names = [
            output.name
            for output in self.session.get_outputs()
        ] # Exracts list of outputs to expect from the model.

        # Loads plants species and status list.
        with open(
            settings.BASE_DIR / "static" / "class_names.json",
            "r"
        ) as f:
            self.species_data = json.load(f)

    # Process image for model input.
    def preprocess(self, image_file):
        start = time.perf_counter()

        image_file.seek(0) # Ensures the start of the file is read.

        img = Image.open(image_file) # Turns file into PIL image.
        img = ImageOps.exif_transpose(img) # Flips the images to the correct
        # correct orientation.
        img = img.convert("RGB") # Converts images to RGB the same as the file.
        img = img.resize(
            IMG_SIZE,
            Image.BILINEAR
        ) # Resizes image using the bilinear method.

        arr = np.asarray(img).astype(
            "float32"
        ) # Converts image into a numerical array for processing.

        # Puts pixel images into the correct array.
        arr = arr / 255.0
        arr = (arr - 0.5) * 2.0

        # Ensures each image in is a batch size of 1.
        arr = np.expand_dims(
            arr,
            axis=0
        )

        # Stores the time taken to preprocess the image.
        preprocessing_ms = (
            time.perf_counter() - start
        ) * 1000

        metrics_service.record_preprocessing(
            preprocessing_ms
        ) # Records the time taken to preprocess the image.

        return arr

    # Classifies image species and status.
    def classify(self, image_file):
        arr = self.preprocess(image_file) # Preprocesses the image.

        start = time.perf_counter()

        # Runs the machine learning model.
        species_pred, status_pred = (
            self.session.run(
                self.output_names,
                {
                    self.input_name: arr
                }
            )
        )

        # Find the three species with the highest predictions.
        sorted_idx = np.argsort(
            species_pred[0]
        )[::-1][:3]

        # Goes through the indexes of each of the top species and then
        # finds relates that the the species data already loaded.
        top_species = [
            {
                "species": self.species_data[idx]["species"],
                "status": self.species_data[idx]["status"],
                "confidence": float(species_pred[0][idx])
            }
            for idx in sorted_idx
        ]

        best = top_species[0]

        # Records the classification time in seconds.
        inference_ms = (
            time.perf_counter() - start
        ) * 1000

        metrics_service.record_inference(
            inference_ms
        ) 

        return {
            "species": best["species"],
            "species_confidence": best["confidence"],
            "status": best["status"],
            "top_3": top_species
        }

# Allows class to be reused, so that model does not have to
# continually be loaded.
classifier_service = (
    PlantClassifierService()
)