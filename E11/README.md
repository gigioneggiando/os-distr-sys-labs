# Exercise 11 Solution (Terraform + Docker)

## What gets provisioned
- `postgres` container
- `flask1` container (provided Flask app)
- `flask2` container (same app, different `APP_NAME`)
- `nginx_lb` container for load balancing on `http://localhost:3000`

## Run
1. Open terminal in this folder.
2. Initialize Terraform:
   - `terraform init`
3. Provision all containers:
   - `terraform apply -auto-approve`
4. Test load balancing:
   - Refresh `http://localhost:3000` several times.
   - Output alternates between `Using Flask1` and `Using Flask2`.

## Cleanup
- `terraform destroy -auto-approve`
