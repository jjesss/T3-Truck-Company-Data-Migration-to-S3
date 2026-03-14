# Pipeline README

## Deploying to AWS ECS (Fargate)

### Prerequisites
- AWS account with default VPC configured
- Terraform installed locally
- Docker installed locally
- AWS CLI configured with credentials

### Build and Push Docker Image
From the pipeline directory:
```bash
cd pipeline
./upload_dockerfile_pipeline.sh
```
This builds the image and pushes it to ECR as `c22-jessh-etl-ecr:latest`.

### Deploy Infrastructure
1. Create `terraform/pipeline/terraform.tfvars`:
```hcl
db_host     = "your-rds-endpoint"
db_port     = "3306"
db_name     = "your_database"
db_user     = "username"
db_password = "password"
```

2. Deploy:
```bash
cd terraform/pipeline
terraform init
terraform plan
terraform apply
```

This creates:
- ECS task definition with database credentials as environment variables
- CloudWatch log group (`/ecs/c22-jessh-etl-ecr`)
- Security group (outbound HTTPS/TCP for AWS services and databases)
- S3 bucket and Glue crawler for data discovery

### Run the Task Manually
```bash
# List ECS clusters
aws ecs list-clusters

# Run task in default VPC (requires cluster and service or use run-task)
aws ecs run-task \
  --cluster your-cluster-name \
  --task-definition c22-jessh-etl-task \
  --launch-type FARGATE \
  --network-configuration "awsvpcConfiguration={subnets=[subnet-xxx],securityGroups=[sg-xxx],assignPublicIp=ENABLED}"
```

### View Logs
- CloudWatch Console → Log Groups → `/ecs/c22-jessh-etl-ecr`
- Or via CLI:
```bash
aws logs tail /ecs/c22-jessh-etl-ecr --follow
```

---

## Local Development

### Prerequisites
- Create a Python virtual environment and install dependencies from the repository `requirements.txt`:

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

### Environment
- Create a `.env` file in the repository root with the following values:

```
DB_HOST=your-rds-host
DB_PORT=3306
DB_NAME=your_db
DB_USER=your_user
DB_PASSWORD=your_password
```

### Run the pipeline
- From the repository root run:

```bash# 
python pipeline/pipeline.py
```
### What pipeline.py does
- Orchestrates the full ETL: extract -> transform -> create_parquet -> upload_to_s3.
- Reads DB and S3 settings from `.env` (DB_HOST, DB_PORT, DB_NAME, DB_USER, DB_PASSWORD, S3_DATASET_PATH).
- Inputs: `data files/extracted_truck_data.csv` (created by extract) or RDS when running extract.
- Outputs: `data files/cleaned_truck_data.csv`, partitioned parquet under `data files/parquet/`, and appended S3 dataset.
- Behaviour: only extracts rows newer than the last `at` found in S3 (or local cleaned CSV), merges and deduplicates by `transaction_id`, partitions by year/month/day/hour, uploads partitions, and exits non‑zero on failure.
- Run: `python pipeline/pipeline.py` (schedule every 3 hours as documented).

## ETL pipeline files
- `extract.py` connects to the RDS and writes the latest batch to `data files/extracted_truck_data.csv`.
- `transform.py` cleans the extracted batch, merges with any existing cleaned data, and writes `data files/cleaned_truck_data.csv`.
- `create_parquet.py` partitions the cleaned CSV by `year/month/day/hour` and writes parquet files to `data files/parquet/`.
- `upload_to_s3.py` appends the partitioned dataset to the S3 dataset (configured in the `.env`).
- `pipeline.py`
- `pipeline.log` - log file to track etl process

### S3 and incremental extraction
- Set `S3_DATASET_PATH` in your `.env` to the dataset S3 path (e.g. `s3://my-bucket/prefix/`).
- The extractor will check S3 for the latest `at` timestamp and only request rows newer than that.

### Batch frequency
- Trucks report every 3 hours; pipeline partitions by `hour` as well as `year/month/day` so you can query hourly partitions.
- Schedule the pipeline every 3 hours (cron or scheduler). For example, a cron entry to run at 0,3,6... hours:

```cron
0 */3 * * * cd /path/to/repo && .venv/bin/python pipeline/pipeline.py
```

## Notes
- The pipeline is incremental: new extracted rows are merged into the cleaned dataset and deduplicated by `transaction_id` when present.
- Ensure credentials and network access to the RDS and S3 are available from the machine running the pipeline.
