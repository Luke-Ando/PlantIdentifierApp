# views.py

import numpy as np
import tensorflow as tf
from tensorflow.keras.applications.efficientnet import preprocess_input
from tensorflow.keras.preprocessing import image as keras_image

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny

from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
from django.conf import settings
from pathlib import Path
import csv
from django.http import JsonResponse

def ping(request):
    load_resources()
    return JsonResponse({"status": "ok"})


# ---------------------------------------------------------
# Load model + species list
# ---------------------------------------------------------

MODEL_PATH = settings.BASE_DIR / "static" / "native_invasive_classifier.keras"
CSV_PATH = settings.BASE_DIR / "static" / "training_data.csv"

model = tf.keras.models.load_model(MODEL_PATH)

# Load species names from CSV
species_list = []
with open(CSV_PATH, "r") as f:
    reader = csv.reader(f)
    for row in reader:
        if len(row) >= 1:
            species = row[0].strip()
            if species not in species_list:
                species_list.append(species)

IMG_SIZE = (300, 300)


# ---------------------------------------------------------
# Prediction function
# ---------------------------------------------------------

def predict_image(path):
    try:
        img = keras_image.load_img(path, target_size=IMG_SIZE)
        img_array = keras_image.img_to_array(img)
        img_array = np.expand_dims(img_array, axis=0)
        img_array = preprocess_input(img_array)

        species_pred, status_pred = model.predict(img_array)

        # Species
        species_idx = int(np.argmax(species_pred[0]))
        species_name = species_list[species_idx]
        species_conf = float(np.max(species_pred[0]))

        # Native / Invasive
        invasive_prob = float(status_pred[0][0])
        status = "INVASIVE" if invasive_prob > 0.5 else "NATIVE"

        return species_name, species_conf, status, invasive_prob

    except Exception as e:
        print(f"Prediction error: {e}")
        return None, None, None, None


# ---------------------------------------------------------
# API endpoint
# ---------------------------------------------------------

class ClassifyPlantView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        if model is None:
            return Response({"error": "Model not loaded"}, status=500)

        image_file = request.FILES.get("image")
        if not image_file:
            return Response({"error": "No image uploaded"}, status=400)

        # Save temporary file
        temp_path = default_storage.save(
            "temp_upload.jpg",
            ContentFile(image_file.read())
        )
        full_path = default_storage.path(temp_path)

        species, species_conf, status, status_conf = predict_image(full_path)

        # Clean up
        try:
            default_storage.delete(temp_path)
        except Exception:
            pass

        if species is None:
            return Response({"error": "Could not classify image"}, status=500)

        return Response({
            "species": species,
            "species_confidence": species_conf,
            "status": status,
            "status_confidence": status_conf
        })
