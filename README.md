# T3 Data Infrastructure Migration
Tasty Truck Treats (T3) is a catering company that specializes in operating a fleet of food trucks in Lichfield and its surrounding areas.
While each food truck operates independently on a day-to-day basis, T3 collects overall sales data from each truck every few hours, giving an overall view of how their fleet is performing.
Currently, the data is stored in an RDS running MySQL on AWS, and the trucks are responsible for uploading their data to the database. This architecture has been suitable so far but relatively high costs have meant they want to complete a data migration project to move to a new architecture. The chosen architecture is one of a 'Data Lake' which will cut costs whilst still ensuring the data is accessible and usable.

The process will be two step:

* Historical Data Migration: Move all of the existing data from the RDS instance to the new architecture.
* Periodic Data Migration: Every three hours new data will end up in the database, this will need to be processed and uploaded to the data lake.


# Pipeline

#### files that need .env access:
* extract.py connects to RDS
    - need MySQL/RDS credentials (eg. DB_HOST etc)
    - os.getenv() will work regardless of whether the variables came from a .env file or were passed directly to the container
* upload_to_s3.py access S3
    - need AWS/S3 credentials (eg. AWS_ACCESS_KEY_ID, ...)
* you will need in your .env
    - AWS_ACCESS_KEY_ID
    - AWS_SECRET_ACCESS_KEY
    - AWS_DEFAULT_REGION
    - DB_HOST
    - DB_PORT
    - DB_NAME
    - DB_USER
    - DB_PASSWORD

## Phase 1: exploring the data
* 1.1 `pipeline/extract.py` An extract script that downloads data from the RDS and saves it locally
* 1.2 `pipeline/transform.py`A transform script that reads the downloaded data, cleans it, and saves it as a .csv
* 1.3 `pipeline/explore.ipyn`A Jupyter notebook that explores the clean data and produces visualisations

[ETL Pipeline](./pipeline/pipeline_README.md)

### Key Findings
* Top Performing Truck: **Kings of Kebabs** with revenue of $739,796.00 
* **Card**: 2198 transactions (50.86%) **Cash**: 2124 transactions (49.14%)
* Total Revenue Across All Trucks: $2,801,433.00
* Total revenue by truck show `supersmoothie` and `hatmann's Jellied Eels` are the worst performing trucks, both under 200,000.
* Distribution of cash and card are same with card at 51% of transactions but card has a higher mode (higher transactions total).

### Recommendations for T3
* Cash customers cluster around $500, card customers around $700
Then we can reccomend things like:

#### For Hiram (CFO - cut costs, raise profits):
Underperforming trucks (SuperSmoothie, Hartmann's) - evaluate or optimize?
Card payments generate higher average revenue - incentivize card use?
Sales volatility (huge drop Feb 22→23) - investigate cause?

#### For Miranda (Culinary - menu/location insights):
Kings of Kebabs is top performer - replicate their strategy?
Underperformers need menu refresh or relocation?
Cash customers spend less - does this indicate price sensitivity?

#### For Alexander (Tech):
Data quality is good (minimal cleaning needed)
Migration to data lake is feasible
Datetime handling will be important for time-based analysis

## Phase 2: Model & Pipeline

* 2.1 `pipeline/create_parquet.py` Script to create the parquet files locally, partitioning on dates (year, month, day)
* 2.2 `terraform/pipeline/main.tf` Terraform file that creates our S3 bucket (data lake).
* 2.3 `pipeline/upload_to_s3.py` Script using AWSWrangler to upload to the S3 bucket

## Phase 3: Dockerise the Pipeline

* 3.1 `dockerfile` : create image for container

### Build/Run container:
In each folder there will be a .sh file eg `upoad_dockerfile_dashboard.sh` which will build, tag and push your image.
TO RUN: sh [filename.sh]

awswrangler uses boto.3 under the hood
* you will need in your .env
- AWS_ACCESS_KEY_ID
- AWS_SECRET_ACCESS_KEY
- AWS_DEFAULT_REGION
- DB_HOST
- DB_PORT
- DB_NAME
- DB_USER
- DB_PASSWORD

## Phase 4: Create and Query the Tables
* To run the crawler:
-  `aws glue start-crawler --name c22-jessh-glue-crawler`
* Check on AWS console: Data catalog > Databases > Tables
* You can use Athena on console to query your database now

## Phase 5: Streamlit Dashboard
* `dashboard.py` 
* `streamlit run dashboard.py` to run dashboard
* `dockerfile.dashboard` docker image for dashboard
* `docker build -f dockerfile.dashboard -t dashboard-image .` to build the dashboard image
* `docker run -p 8501:8501 --env-file .env dashboard-image` run container (maps container port 8501 to local machine port)

* `terraform/dashboard/main.tf` terraform file for creating ECR and ECS
    - to run this:
    - cd into the respective folder, 
        - do terraform init, 
        - terraform plan, 
        - terraform apply 
        - (type yes after you have checked everything is as expected)
        - To delete the resources: terraform destroy

#### The image has been pushed to ECR:
- built
- authenticated
- tagged
- pushed
AWS console → ECR → Repositories → c22-jessh-t3-dashboard → Images.

graph ideas:
revenue by truck
avg daily revenue
revenue over time (per truck)

Athena charges per query based on the amount of data scanned. 
So: 
- One SELECT * query = one charge, all data in memory
- Multiple specific queries = multiple charges
Currently the dataset size is quite small, so loading everything once and using pandas to filter/aggregate 
a better approach - cheaper and faster since subsequent operations are in memory.

## Phase 6: Batch processing
Every 3 hours we batch process the new data from the RDS into the S3. 
* ETL Pipeline: An ECS Fargate task that runs the ETL script to pull data from the RDS and upload it to the Data Lake.
* Eventbridge scheduled to run this pipeline task every 3 hours using cron

# Improvements
- On reflection it may have been better to have sql do the heavy lifting
- Doing multiple specific queries you get less data downloaded to your machine and then you can cache those results as needed rather can caching the big combined table
- Dashboard also better to be in terms of weeks, allowing filtering to see 

# Presentation
https://drive.google.com/drive/folders/0AMjtC3W2yPm4Uk9PVA
