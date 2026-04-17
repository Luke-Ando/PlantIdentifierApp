# views.py

import numpy as np
import onnxruntime as ort
from PIL import Image
from tensorflow.keras.applications.efficientnet import preprocess_input   # <-- ADD THIS

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
    return JsonResponse({"status": "ok"})


# ---------------------------------------------------------
# Load ONNX model + species list
# ---------------------------------------------------------

MODEL_PATH = settings.BASE_DIR / "static" / "model.onnx"
CSV_PATH = settings.BASE_DIR / "static" / "training_data.csv"

# Load ONNX model
session = ort.InferenceSession(str(MODEL_PATH), providers=["CPUExecutionProvider"])
input_name = session.get_inputs()[0].name
output_names = [o.name for o in session.get_outputs()]

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
        img = Image.open(path).convert("RGB")
        img = img.resize(IMG_SIZE)

        # 🔥 EfficientNet preprocessing (CRITICAL FIX)
        arr = np.array(img).astype("float32")
        arr = preprocess_input(arr)     # <-- FIXED
        arr = np.expand_dims(arr, axis=0)

        outputs = session.run(output_names, {input_name: arr})

        species_pred = outputs[0]
        status_pred = outputs[1]

        species_idx = int(np.argmax(species_pred[0]))
        species_name = species_list[species_idx]
        species_conf = float(np.max(species_pred[0]))

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
        image_file = request.FILES.get("image")
        if not image_file:
            return Response({"error": "No image uploaded"}, status=400)

        temp_path = default_storage.save(
            "temp_upload.jpg",
            ContentFile(image_file.read())
        )
        full_path = default_storage.path(temp_path)

        species, species_conf, status, status_conf = predict_image(full_path)

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
