from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from prometheus_fastapi_instrumentator import Instrumentator
import logging, json
from .config import settings
from .db import init_db
from .infra.telemetry.logging import TraceMiddleware
from .routers import auth, visits, workflow, ai, exports, comments

app = FastAPI(title="ClinicOps Multimodal", version=settings.version, docs_url="/docs", openapi_url="/openapi.json")

# CORS — allow exact origins + any *.vercel.app preview (git-main-hesam2 etc.)
# Dev may use CORS_ORIGINS=* for open access; prod uses explicit list but still needs preview regex
_raw = settings.cors_origins.strip() if settings.cors_origins else "*"
if _raw == "*":
    cors_origins = ["*"]
    cors_regex = None
else:
    cors_origins = [o.strip() for o in _raw.split(",") if o.strip()]
    # If any allowed origin is a vercel.app domain, allow all vercel previews via regex
    # This fixes clinicops-multimodal-git-main-hesam2.vercel.app preflight blocked by exact match
    cors_regex = r"https://.*\.vercel\.app" if any("vercel.app" in o for o in cors_origins) else None
app.add_middleware(CORSMiddleware, allow_origins=cors_origins, allow_origin_regex=cors_regex, allow_credentials=True, allow_methods=["*"], allow_headers=["*"])
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

# OTel optional — traces + logs
if settings.otel_enabled:
    try:
        from opentelemetry import trace
        from opentelemetry.sdk.trace import TracerProvider
        from opentelemetry.sdk.trace.export import BatchSpanProcessor
        from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
        from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
        from opentelemetry.sdk.resources import Resource as TraceResource
        provider = TracerProvider(resource=TraceResource.create({"service.name": settings.otel_service_name, "service.version": settings.version}))
        processor = BatchSpanProcessor(OTLPSpanExporter(endpoint=settings.otel_exporter_otlp_endpoint, insecure=True))
        provider.add_span_processor(processor)
        trace.set_tracer_provider(provider)
        FastAPIInstrumentor.instrument_app(app)
    except Exception as e:
        logger.warning(f"OTel trace setup failed: {e}")
    # OTLP logs → Loki via otel-collector
    try:
        from opentelemetry.sdk._logs import LoggerProvider, LoggingHandler
        from opentelemetry.sdk._logs.export import BatchLogRecordProcessor
        from opentelemetry.exporter.otlp.proto.grpc._log_exporter import OTLPLogExporter
        from opentelemetry.sdk.resources import Resource
        from app.infra.telemetry.logging_conf import OtlpLogHandler, JsonFormatter
        # Use same endpoint for logs
        log_provider = LoggerProvider(resource=Resource.create({"service.name": "clinicops-backend"}))
        log_provider.add_log_record_processor(BatchLogRecordProcessor(OTLPLogExporter(endpoint=settings.otel_exporter_otlp_endpoint, insecure=True)))
        # Attach OTLP handler to clinicops logger (and root for TraceMiddleware logs)
        otlp_handler = OtlpLogHandler(log_provider)
        otlp_handler.setLevel(logging.INFO)
        # Ensure clinicops logger ships JSON logs with trace_id to Loki
        for lg_name in ["clinicops", "uvicorn.access"]:
            lg = logging.getLogger(lg_name)
            lg.addHandler(otlp_handler)
            lg.setLevel(logging.INFO)
    except Exception as e:
        logger.warning(f"OTel log setup failed: {e}")
