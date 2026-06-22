import numpy as np
import time
import logging

from .metrics_service import metrics_service
from PIL import Image, ImageOps
import onnxruntime as ort

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny

from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
from django.conf import settings
from django.http import JsonResponse

import csv
import json
import os

logger = logging.getLogger(__name__)

def ping(request):
    return JsonResponse({"status": "ok"})


# ---------------------------------------------------------
# Preprocessing (matches training exactly)
# ---------------------------------------------------------

IMG_SIZE = (300, 300)

def preprocess_pillow(path):
    img = Image.open(path)
    img = ImageOps.exif_transpose(img)
    img = img.convert("RGB")
    img = img.resize(IMG_SIZE, Image.BILINEAR)

    arr = np.asarray(img).astype("float32")

    # EfficientNet normalization
    arr = arr / 255.0
    arr = (arr - 0.5) * 2.0

    arr = np.expand_dims(arr, axis=0)
    return arr


# ---------------------------------------------------------
# Load ONNX model
# ---------------------------------------------------------

MODEL_PATH = settings.BASE_DIR / "static" / "model.onnx"

session = ort.InferenceSession(
    str(MODEL_PATH),
    providers=["CPUExecutionProvider"]
)

input_name = session.get_inputs()[0].name
output_names = [o.name for o in session.get_outputs()]


# ---------------------------------------------------------
# Load species list from class_names.json (correct order)
# ---------------------------------------------------------
CLASS_NAMES_PATH = settings.BASE_DIR / "class_names.json"


with open(CLASS_NAMES_PATH, "r") as f:
    species_list = json.load(f)


# ---------------------------------------------------------
# Load status mapping from training_data.csv
# ---------------------------------------------------------

CSV_PATH = settings.BASE_DIR / "static" / "training_data.csv"

species_status_map = {}

with open(CSV_PATH, "r") as f:
    reader = csv.reader(f)
    for row in reader:
        species = row[0].strip()
        status = row[2].strip().upper()
        species_status_map[species] = status


# ---------------------------------------------------------
# Prediction function (top‑3 + confidence + model status)
# ---------------------------------------------------------

def predict_image(path):
    preprocess_start = time.perf_counter()

    arr = preprocess_pillow(path)

    preprocessing_ms = (
        time.perf_counter()
        - preprocess_start
    ) * 1000

    metrics_service.record_preprocessing(
        preprocessing_ms
    )

    inference_start = time.perf_counter()

    species_pred, status_pred = session.run(
        output_names,
        {input_name: arr}
    )

    inference_ms = (
        time.perf_counter()
        - inference_start
    ) * 1000

    metrics_service.record_inference(
        inference_ms
)

    # Top‑1 species
    species_idx = int(np.argmax(species_pred[0]))
    species_name = species_list[species_idx]
    species_conf = float(np.max(species_pred[0]))

    # Top‑3 predictions
    sorted_idx = np.argsort(species_pred[0])[::-1][:3]
    top3_species = [species_list[i] for i in sorted_idx]
    top3_conf = [float(species_pred[0][i]) for i in sorted_idx]

    # Model invasive/native output
    invasive_prob = float(status_pred[0][0])
    status = species_status_map[species_name]

    return (
        species_name,
        species_conf,
        status,
        invasive_prob,
        top3_species,
        top3_conf
    )


# ---------------------------------------------------------
# API Endpoint
# ---------------------------------------------------------

class ClassifyPlantView(APIView):
    
    permission_classes = [AllowAny]

    def post(self, request):
        request_start = time.perf_counter()
        image_file = request.FILES.get("image")
        if not image_file:
            return Response({"error": "No image uploaded"}, status=400)

        temp_path = default_storage.save(
            "temp_upload.jpg",
            ContentFile(image_file.read())
        )
        full_path = default_storage.path(temp_path)

        (
            species,
            species_conf,
            status,
            status_conf,
            top3_species,
            top3_conf
        ) = predict_image(full_path)

        latency_ms = (
            time.perf_counter()
            - request_start
        ) * 1000

        logger.info(
            f"Prediction={species}, "
            f"confidence={species_conf:.3f}, "
            f"latency={latency_ms:.2f}ms"
        )

        default_storage.delete(temp_path)


        metrics_service.record_request(
            latency_ms
        )

        return Response({
            "species": species,
            "species_confidence": species_conf,
            "status": status,
            "status_confidence": status_conf,
            "top_3_species": top3_species,
            "top_3_confidences": top3_conf
        })

class MetricsView(APIView):

    permission_classes = [AllowAny]

    def get(self, request):

        return Response(
            metrics_service.get_metrics()
        )