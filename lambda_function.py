import json
import os
import logging
from datetime import datetime, timezone

logger = logging.getLogger()
logger.setLevel(logging.INFO)

_is_cold_start = True

def lambda_handler(event: dict, context) -> dict:
    global _is_cold_start
    cold = _is_cold_start
    _is_cold_start = False

    try:
        body = {
            "message": "hello from lambda",
            "function_name": "lambda_lab_function",
            "service":     os.environ.get("SERVICE_NAME", "harness-lambda-lab"),
            "version":     os.environ.get("VERSION"),
            "environment": os.environ.get("ENVIRONMENT", "dev"),
            "status":      "ok",
            "timestamp_utc": datetime.now(tz=timezone.utc).isoformat(),
            "aws_request_id": context.aws_request_id,
            "cold_start": cold,
            "remaining_time_ms": context.get_remaining_time_in_millis(),
        }
        logger.info("OK %s", context.aws_request_id)
        return _respond(200, body)

    except Exception as exc:
        logger.exception("Error: %s", exc)
        return _respond(500, {"error": str(exc), "aws_request_id": context.aws_request_id})


def _respond(status: int, body: dict) -> dict:
    return {
        "statusCode": status,
        "headers": {"Content-Type": "application/json"},
        "body": json.dumps(body, indent=2, default=str),
    }