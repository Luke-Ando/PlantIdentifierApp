import logging
import time

from django.http import JsonResponse

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny

from .metrics_service import metrics_service
from .services.plant_classifier import (
    classifier_service
)

logger = logging.getLogger(__name__)


def ping(request):
    return JsonResponse({
        "status": "ok"
    })


class ClassifyPlantView(APIView):

    permission_classes = [AllowAny]

    def post(self, request):

        request_start = (
            time.perf_counter()
        )

        try:

            image_file = request.FILES.get(
                "image"
            )

            if not image_file:
                return Response(
                    {
                        "error":
                        "No image uploaded"
                    },
                    status=400
                )

            result = (
                classifier_service.classify(
                    image_file
                )
            )

            latency_ms = (
                time.perf_counter()
                - request_start
            ) * 1000

            metrics_service.record_request(
                latency_ms
            )

            logger.info(
                f"Prediction="
                f"{result['species']} "
                f"latency="
                f"{latency_ms:.2f}ms"
            )

            return Response(result)

        except Exception:

            metrics_service.record_error()

            logger.exception(
                "Classification failed"
            )

            return Response(
                {
                    "error":
                    "Internal server error"
                },
                status=500
            )


class MetricsView(APIView):

    permission_classes = [AllowAny]

    def get(self, request):

        return Response(
            metrics_service.get_metrics()
        )