# api/views.py

import joblib
import numpy as np
from pathlib import Path
from skimage import io, transform, feature
from skimage.color import rgb2gray

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny

from django.core.files.storage import default_storage
from django.core.files.base import ContentFile


# ---------------------------------------------------------
# Load model + label encoder once at server startup
# ---------------------------------------------------------

# BASE_DIR = folder containing manage.py
BASE_DIR = Path(__file__).resolve().parent.parent

MODEL_PATH = BASE_DIR / "model.pkl"
ENCODER_PATH = BASE_DIR / "label_encoder.pkl"

clf = None
le = None

try:
    clf = joblib.load(MODEL_PATH)
    le = joblib.load(ENCODER_PATH)
    print("Model and label encoder loaded successfully.")
except Exception as e:
    print("Error loading model or label encoder:", e)


# ---------------------------------------------------------
# Helper function: classify an uploaded image
# ---------------------------------------------------------

def predict_image(path, model, label_encoder, target_size=(128, 128)):
    try:
        img = io.imread(path)

        if img.ndim == 3:
            img = rgb2gray(img)

        img_resized = transform.resize(img, target_size, anti_aliasing=True)

        hog = feature.hog(
            img_resized,
            orientations=9,
            pixels_per_cell=(8, 8),
            cells_per_block=(2, 2),
            block_norm="L2-Hys"
        )

        pred = model.predict([hog])[0]
        prob = model.predict_proba([hog])[0]

        class_name = label_encoder.inverse_transform([pred])[0]
        confidence = float(np.max(prob))

        return class_name, confidence

    except Exception as e:
        print("Prediction error:", e)
        return None, None


# ---------------------------------------------------------
# API endpoint: /api/classify/
# ---------------------------------------------------------

class ClassifyPlantView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        if clf is None or le is None:
            return Response({"error": "Model not loaded"}, status=500)

        image_file = request.FILES.get("image")
        if not image_file:
            return Response({"error": "No image uploaded"}, status=400)

        temp_path = default_storage.save(
            "temp_upload.jpg",
            ContentFile(image_file.read())
        )
        full_path = default_storage.path(temp_path)

        class_name, confidence = predict_image(full_path, clf, le)

        if class_name is None:
            return Response({"error": "Could not classify image"}, status=500)

        return Response({
            "class": class_name,
            "confidence": confidence
        })
