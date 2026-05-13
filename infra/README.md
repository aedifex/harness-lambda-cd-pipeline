# infra/lambda_function
 
Terraform module that provisions the AWS infrastructure skeleton for `lambda_lab_function`. This is a **one-time provisioning step** — it creates the function and its execution role, but does not manage application code or configuration. All subsequent deployments are handled by Harness CD.
 
## What This Provisions
 
| Resource | Name | Purpose |
|---|---|---|
| `aws_iam_role` | `lambda_exec_role` | Execution role for the Lambda function |
| `aws_iam_role_policy_attachment` | — | Attaches `AWSLambdaBasicExecutionRole` (CloudWatch logs) |
| `aws_lambda_function` | `lambda_lab_function` | The Lambda function itself (Python 3.11) |
| `aws_lambda_function_url` | — | Public HTTPS endpoint (no auth) |
| `aws_lambda_permission` | — | Allows public invocation via Function URL and direct invoke |
 
## Separation of Concerns
 
```
Terraform (this module)          Harness CD
────────────────────────         ──────────────────────────────
IAM role & policies          →   (uses role ARN at deploy time)
Lambda function shell        →   updates code + env vars
Function URL                 →   traffic shifting (canary/blue-green)
```
 
Terraform owns the **infrastructure**. Harness owns the **artifact and runtime config** — including the `VERSION` and `ENVIRONMENT` variables injected dynamically via the [function definition manifest](../../AWS-Lambda-Function-Definition.yaml).
 
## Usage
 
```bash
cd infra/lambda_function
terraform init
terraform apply
```
 
The initial `apply` bootstraps the function using a local placeholder ZIP (`s3/lambda_function.zip`). After that, Harness takes over all deploys.
 
## Outputs
 
| Output | Description |
|---|---|
| `lambda_url` | Public Function URL for invoking the Lambda directly |
 
## Notes
 
- **Region:** `us-west-2`
- **Auth:** Function URL is set to `NONE` — this is intentional for lab/demo purposes. Lock this down before any production use.
- The `source_code_hash` references `s3/lambda_function.zip` locally only for the bootstrap deploy. Harness deploys pull the versioned artifact from S3 directly.