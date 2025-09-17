# app/core/middleware.py
import time
import logging
import uuid
from fastapi import FastAPI, Request
from starlette.middleware.cors import CORSMiddleware
from starlette.responses import Response

logger = logging.getLogger("middleware")

def configure_middleware(app: FastAPI):
    # CORS - allow local dev; override in production
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_methods=["*"],
        allow_headers=["*"],
    )

    @app.middleware("http")
    async def add_process_time_header(request: Request, call_next):
        start = time.time()
        request_id = str(uuid.uuid4())
        request.state.request_id = request_id
        try:
            response: Response = await call_next(request)
        except Exception as e:
            logger.exception("Unhandled exception: %s", e)
            raise
        duration = (time.time() - start) * 1000.0
        response.headers["X-Process-Time-Ms"] = f"{duration:.2f}"
        response.headers["X-Request-Id"] = request_id
        logger.info("%s %s %s %.2fms", request.method, request.url.path, request_id, duration)
        return response
