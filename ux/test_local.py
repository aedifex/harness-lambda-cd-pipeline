from lambda_function import _respond_html

body = {
    "message":           "hello from lambda",
    "function_name":     "lambda_lab_function",
    "service":           "harness-lambda-lab",
    "version":           "42",
    "environment":       "dev",
    "pipeline_sequence": "42",
    "status":            "ok",
    "timestamp_utc":     "2026-05-21T16:30:00Z",
    "aws_request_id":    "abc123-xyz-ef99",
    "cold_start":        True,
    "remaining_time_ms": 2847,
}

html = _respond_html(body)["body"]

with open("test_output.html", "w") as f:
    f.write(html)

print("Done — open test_output.html in your browser")