from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from prometheus_fastapi_instrumentator import Instrumentator
import logging, json
from .config import settings
from .db import init_db
from .infra.telemetry.logging import TraceMiddleware
from .routers import auth, visits, workflow, ai, exports, comments

app = FastAPI(title="ClinicOps Multimodal", version=settings.version, docs_url="/docs", openapi_url="/openapi.json")

# CORS
origins = [o.strip() for o in settings.cors_origins.split(",")] if settings.cors_origins else ["*"]
app.add_middleware(CORSMiddleware, allow_origins=origins, allow_credentials=True, allow_methods=["*"], allow_headers=["*"])
app.add_middleware(TraceMiddleware)

# Metrics — ClinicOps business counters must be registered BEFORE Instrumentator snapshot
try:
    from .infra.telemetry.metrics import register_metrics
    register_metrics()
except Exception:
    pass
Instrumentator().instrument(app).expose(app, endpoint="/metrics")

# Routers
app.include_router(auth.router, prefix="/api")
app.include_router(visits.router, prefix="/api")
app.include_router(workflow.router, prefix="/api")
app.include_router(ai.router, prefix="/api")
app.include_router(exports.router, prefix="/api")
app.include_router(comments.router, prefix="/api")

# Logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("clinicops")

@app.on_event("startup")
def startup():
    init_db()
    logger.info(json.dumps({"event":"startup","version":settings.version}))

@app.get("/healthz")
def healthz():
    return {"status":"ok","version":settings.version}

@app.get("/readyz")
def readyz():
    return {"status":"ready"}

@app.get("/")
def root():
    return {"service":"ClinicOps Multimodal","version":settings.version,"docs":"/docs","health":"/healthz"}

# OTel optional
if settings.otel_enabled:
    try:
        from opentelemetry import trace
        from opentelemetry.sdk.trace import TracerProvider
        from opentelemetry.sdk.trace.export import BatchSpanProcessor
        from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
        from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
        provider = TracerProvider()
        processor = BatchSpanProcessor(OTLPSpanExporter(endpoint=settings.otel_exporter_otlp_endpoint, insecure=True))
        provider.add_span_processor(processor)
        trace.set_tracer_provider(provider)
        FastAPIInstrumentor.instrument_app(app)
    except Exception as e:
        logger.warning(f"OTel setup failed: {e}")
