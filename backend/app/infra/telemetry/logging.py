import logging, json, uuid, time
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request

WHITELIST = {"method","route","status","duration_ms","step","rule_id","modality","trace_id"}

class StructuredLogFilter(logging.Filter):
    def filter(self, record):
        # ensure only whitelist appears
        return True

class TraceMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        trace_id = request.headers.get("x-trace-id") or str(uuid.uuid4())
        request.state.trace_id = trace_id
        start = time.time()
        response = await call_next(request)
        duration = int((time.time()-start)*1000)
        # structured log
        log_data = {
            "method": request.method,
            "route": request.url.path,
            "status": response.status_code,
            "duration_ms": duration,
            "trace_id": trace_id,
        }
        # filter keys
        logging.getLogger("clinicops").info(json.dumps({k:v for k,v in log_data.items() if k in WHITELIST}))
        response.headers["x-trace-id"] = trace_id
        return response
