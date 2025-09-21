import json
import logging
from fastapi import FastAPI, Request


class StructuredLogger(logging.Logger):
    def _log(self, level, msg, args, exc_info=None, extra=None, stack_info=False):
        if extra is None:
            extra = {}
        extra['app_name'] = 'MyFastAPIApp'
        super()._log(level, json.dumps(msg) if isinstance(msg, dict) else msg, args, exc_info, extra, stack_info)


logging.setLoggerClass(StructuredLogger)
logger = logging.getLogger(__name__)

app = FastAPI()


@app.middleware("http")
async def log_structured_requests(request: Request, call_next):
    logger.info({
        "event": "request",
        "method": request.method,
        "url": str(request.url),
        "headers": dict(request.headers),
        "client": request.client.host
    })
    response = await call_next(request)
    logger.info({
        "event": "response",
        "status_code": response.status_code
    })
    return response
