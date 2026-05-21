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
            "message":           "hello from lambda",
            "function_name":     "lambda_lab_function",
            "service":           os.environ.get("SERVICE_NAME", "harness-lambda-lab"),
            "version":           os.environ.get("VERSION", "unknown"),
            "environment":       os.environ.get("ENVIRONMENT", "dev"),
            "pipeline_sequence": os.environ.get("PIPELINE_SEQUENCE", ""),
            "status":            "ok",
            "timestamp_utc":     datetime.now(tz=timezone.utc).isoformat(),
            "aws_request_id":    context.aws_request_id,
            "cold_start":        cold,
            "remaining_time_ms": context.get_remaining_time_in_millis(),
        }
        logger.info("OK %s", context.aws_request_id)

        accept = event.get("headers", {}).get("accept", "")
        if "text/html" in accept:
            return _respond_html(body)
        return _respond_json(200, body)

    except Exception as exc:
        logger.exception("Error: %s", exc)
        error = {"error": str(exc), "aws_request_id": context.aws_request_id}
        accept = event.get("headers", {}).get("accept", "")
        if "text/html" in accept:
            return _respond_html(error, is_error=True)
        return _respond_json(500, error)


def _respond_json(status: int, body: dict) -> dict:
    return {
        "statusCode": status,
        "headers": {"Content-Type": "application/json"},
        "body": json.dumps(body, indent=2, default=str),
    }


def _respond_html(body: dict, is_error: bool = False) -> dict:
    version     = body.get("version", "unknown")
    environment = body.get("environment", "dev")
    service     = body.get("service", "")
    fn_name     = body.get("function_name", "")
    request_id  = body.get("aws_request_id", "")
    remaining   = body.get("remaining_time_ms", "")
    timestamp   = body.get("timestamp_utc", "")
    message     = body.get("message", "")
    cold        = body.get("cold_start", False)
    pipeline    = body.get("pipeline_sequence", "")

    status_pill    = (
        '<span class="pill p-err">✕ error</span>'
        if is_error else
        '<span class="pill p-ok">● ok</span>'
    )
    cold_pill      = '<span class="pill p-cold">❄ cold start</span>' if cold else ""
    footer_badge   = (
        '<span class="footer-badge err-badge">ERROR</span>'
        if is_error else
        '<span class="footer-badge">DEPLOYED</span>'
    )
    pipeline_label = f"· pipeline #{pipeline}" if pipeline else ""
    remaining_fmt  = f"{int(remaining):,} ms" if remaining != "" else "—"

    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>{fn_name} · status</title>
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link href="https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@400;500;600;700&family=Space+Mono:wght@400;700&family=Syne:wght@800&display=swap" rel="stylesheet">
  <style>
    *, *::before, *::after {{ box-sizing: border-box; margin: 0; padding: 0; }}

    body {{
      background: #07070f;
      display: flex;
      justify-content: center;
      align-items: center;
      min-height: 100vh;
      padding: 2.5rem;
      font-family: 'Space Grotesk', sans-serif;
    }}

    .card {{
      background: #0e0e1a;
      border: 1.5px solid #2a2a4a;
      border-radius: 24px;
      padding: 2.2rem;
      width: 100%;
      max-width: 525px;
    }}

    .top-label {{
      font-size: 14px;
      font-weight: 600;
      letter-spacing: 2.5px;
      text-transform: uppercase;
      color: #3a3a6a;
      margin-bottom: 1.25rem;
    }}

    .hero {{
      font-family: 'Syne', sans-serif;
      font-size: 73px;
      font-weight: 800;
      background: linear-gradient(90deg, #00c6ff, #0072ff);
      -webkit-background-clip: text;
      -webkit-text-fill-color: transparent;
      background-clip: text;
      line-height: 1;
      margin-bottom: 0.4rem;
    }}

    .fn-name {{
      font-family: 'Space Mono', monospace;
      font-size: 15px;
      color: #8080aa;
      margin-bottom: 1.5rem;
    }}

    .pills {{
      display: flex;
      gap: 9px;
      margin-bottom: 1.5rem;
      flex-wrap: wrap;
    }}

    .pill {{
      font-size: 15px;
      font-weight: 600;
      padding: 5px 15px;
      border-radius: 999px;
      border: 1.5px solid;
      letter-spacing: 0.3px;
    }}

    .p-env  {{ background: rgba(0,114,255,0.12); color: #5ab4ff; border-color: rgba(0,114,255,0.45); }}
    .p-ok   {{ background: rgba(0,230,118,0.12); color: #00e676; border-color: rgba(0,230,118,0.45); }}
    .p-cold {{ background: rgba(255,193,7,0.12);  color: #ffc107; border-color: rgba(255,193,7,0.45); }}
    .p-err  {{ background: rgba(255,82,82,0.12);  color: #ff5252; border-color: rgba(255,82,82,0.45); }}

    .divider {{
      border: none;
      border-top: 1px solid #1a1a2e;
    }}

    .rows {{ display: grid; }}

    .row {{
      display: flex;
      justify-content: space-between;
      align-items: center;
      padding: 11px 0;
      border-bottom: 1px solid #1a1a2e;
      gap: 20px;
    }}
    .row:last-child {{ border-bottom: none; }}

    .lbl {{
      font-size: 16px;
      color: #5ab4ff;
      font-weight: 600;
      white-space: nowrap;
    }}

    .val {{
      font-family: 'Space Mono', monospace;
      font-weight: 700;
      color: #ffffff;
      font-size: 15px;
      text-align: right;
      word-break: break-all;
    }}

    .footer {{
      margin-top: 1.4rem;
      padding-top: 1.1rem;
      border-top: 1px solid #1a1a2e;
      display: flex;
      align-items: center;
      justify-content: space-between;
    }}

    .footer-left {{
      font-size: 15px;
      color: #9090bb;
      letter-spacing: 0.3px;
    }}

    .harness {{
      font-weight: 700;
      background: linear-gradient(90deg, #00c6ff 0%, #0072ff 100%);
      -webkit-background-clip: text;
      -webkit-text-fill-color: transparent;
      background-clip: text;
      display: inline-block;
    }}

    .footer-badge {{
      font-size: 13px;
      font-weight: 700;
      background: rgba(0,114,255,0.1);
      color: #5ab4ff;
      border: 1px solid rgba(0,114,255,0.3);
      border-radius: 999px;
      padding: 4px 14px;
      letter-spacing: 1px;
    }}

    .err-badge {{
      background: rgba(255,82,82,0.1);
      color: #ff5252;
      border-color: rgba(255,82,82,0.3);
    }}
  </style>
</head>
<body>
  <div class="card">
    <p class="top-label">lambda status</p>
    <p class="hero">v{version}</p>
    <p class="fn-name">{fn_name}</p>

    <div class="pills">
      <span class="pill p-env">{environment}</span>
      {status_pill}
      {cold_pill}
    </div>

    <div class="divider"></div>

    <div class="rows">
      <div class="row"><span class="lbl">message</span><span class="val">{message}</span></div>
      <div class="row"><span class="lbl">service</span><span class="val">{service}</span></div>
      <div class="row"><span class="lbl">aws request id</span><span class="val">{request_id}</span></div>
      <div class="row"><span class="lbl">remaining time</span><span class="val">{remaining_fmt}</span></div>
      <div class="row"><span class="lbl">timestamp utc</span><span class="val">{timestamp}</span></div>
    </div>

    <div class="footer">
      <p class="footer-left">powered by <span class="harness">Harness CD</span> {pipeline_label}</p>
      {footer_badge}
    </div>
  </div>
</body>
</html>"""

    return {
        "statusCode": 500 if is_error else 200,
        "headers": {"Content-Type": "text/html"},
        "body": html,
    }