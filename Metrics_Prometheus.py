from fastapi import FastAPI
from prometheus_client import Counter, Histogram
from starlette_exporter import PrometheusMiddleware, handle_metrics

app = FastAPI()
app.add_middleware(PrometheusMiddleware)
app.add_route("/metrics", handle_metrics)

# Define custom metrics
REQUEST_COUNT = Counter('request_count', 'Total request count')
REQUEST_LATENCY = Histogram('request_latency_seconds', 'Request latency in seconds')


@app.get("/")
async def root():
    REQUEST_COUNT.inc()
    with REQUEST_LATENCY.time():
        # Your logic here
        return {"message": "Hello World"}
