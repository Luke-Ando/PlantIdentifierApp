# views.py
# Returns the information from a HTTP request.

# Imports
# Utilities
import logging # Provides a structured way to print text to the screen.
import time # Used by metrics services.

# Django Libraries
from django.http import JsonResponse
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny

# Internal Services
from .services.metrics_service import metrics_service
from .services.plant_classifier import (
    classifier_service
)

logger = logging.getLogger(__name__) # Sets up logger.

# Used by frontend to test server accessibility.
def ping(request):
    return JsonResponse({
        "status": "ok"
    })

# /classify/
class ClassifyPlantView(APIView):
    permission_classes = [AllowAny] # No login required for API.

    def post(self, request):

        request_start = (
            time.perf_counter()
        ) # Start measuring the time.

        # Ensure that error is catched in the block and recorded.
        try:
            image_file = request.FILES.get(
                "image"
            ) # Saves file labelled image.

            # Notify error that a bad request was made if no image was
            # uploaded.
            if not image_file:
                return Response(
                    {
                        "error":
                        "No image uploaded"
                    },
                    status=400
                )

            # Call the classifier service.
            result = (
                classifier_service.classify(
                    image_file
                )
            )

            latency_ms = (
                time.perf_counter()
                - request_start
            ) * 1000

            # Record the latency in ms.
            metrics_service.record_request(
                latency_ms
            )

            logger.info(
                f"Prediction="
                f"{result['species']} "
                f"latency="
                f"{latency_ms:.2f}ms"
            ) # Output the latency to the screen.

            return Response(result)

        except Exception:
            metrics_service.record_error() # Ensure error is logged.

            logger.exception(
                "Classification failed"
            ) # Create error log.

            return Response(
                {
                    "error":
                    "Internal server error"
                },
                status=500
            ) # Return internal service error.

#/metrics/
class MetricsView(APIView):
    permission_classes = [AllowAny]
    def get(self, request):
        return Response(
            metrics_service.get_metrics()
        )