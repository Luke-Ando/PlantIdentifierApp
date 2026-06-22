from threading import Lock
import numpy as np
import psutil


class MetricsService:

    def __init__(self):
        self.lock = Lock()

        self.total_requests = 0
        self.total_errors = 0

        self.latencies = []
        self.inference_times = []
        self.preprocessing_times = []

    def record_request(self, latency_ms):
        with self.lock:
            self.total_requests += 1
            self.latencies.append(latency_ms)

    def record_error(self):
        with self.lock:
            self.total_errors += 1

    def record_inference(self, inference_ms):
        with self.lock:
            self.inference_times.append(inference_ms)

    def record_preprocessing(self, preprocessing_ms):
        with self.lock:
            self.preprocessing_times.append(preprocessing_ms)

    def _average(self, values):
        if not values:
            return 0

        return round(sum(values) / len(values), 2)

    def _percentile(self, values, p):
        if not values:
            return 0

        return round(float(np.percentile(values, p)), 2)

    def get_metrics(self):

        process = psutil.Process()

        memory_mb = (
            process.memory_info().rss
            / 1024
            / 1024
        )

        return {
            "total_requests": self.total_requests,
            "total_errors": self.total_errors,

            "average_latency_ms":
                self._average(self.latencies),

            "p95_latency_ms":
                self._percentile(self.latencies, 95),

            "p99_latency_ms":
                self._percentile(self.latencies, 99),

            "average_inference_ms":
                self._average(self.inference_times),

            "average_preprocessing_ms":
                self._average(self.preprocessing_times),

            "cpu_percent":
                psutil.cpu_percent(),

            "memory_mb":
                round(memory_mb, 2)
        }


metrics_service = MetricsService()