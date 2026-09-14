# Data Quality & ETL Pipeline

A configuration-driven data quality and ETL pipeline built with Python and Pandas using the Brazilian E-Commerce Public Dataset by Olist.

The project follows a **validation-first architecture**, where source data is validated against configurable quality rules before the ETL layer is allowed to execute.

---

## Table of Contents

- [Overview](#overview)
- [Objectives](#objectives)
- [Dataset](#dataset)
- [Architecture](#architecture)
- [Project Structure](#project-structure)
- [Data Quality Framework](#data-quality-framework)
  - [Schema Validation](#1-schema-validation)
  - [Datatype Validation](#2-datatype-validation)
  - [Null Validation](#3-null-validation)
  - [Duplicate Validation](#4-duplicate-validation)
  - [Business Rule Validation](#5-business-rule-validation)
- [Configuration-Driven Design](#configuration-driven-design)
- [Quality Gate](#quality-gate)
- [ETL Layer](#etl-layer)
- [Curated Data Model](#curated-data-model)
- [Pipeline Orchestration](#pipeline-orchestration)
- [Error Handling](#error-handling)
- [Logging and Metadata](#logging-and-metadata)
- [Running the Project](#running-the-project)
- [Current Validation Results](#current-validation-results)
- [Technologies](#technologies)
- [Engineering Concepts Demonstrated](#engineering-concepts-demonstrated)
- [Design Decisions](#design-decisions)
- [Future Enhancements](#future-enhancements)
- [Project Status](#project-status)

---

# Overview

Data pipelines can produce unreliable downstream datasets when source data contains:

- Unexpected schema changes
- Invalid data types
- Missing values
- Duplicate records
- Invalid business values
- Broken referential relationships

This project implements a modular data quality and ETL framework to identify these issues before data reaches the curated layer.

The pipeline follows:

```text
Raw Source Data
      │
      ▼
Data Quality Validation
      │
      ▼
Quality Gate
      │
      ├── FAIL ──► Stop Pipeline
      │
      └── PASS
            │
            ▼
           ETL
            │
            ▼
     Curated Data Layer
            │
            ▼
     Pipeline Metadata
```

The main design principle is:

> **Validate source data before allowing ETL execution.**

---

# Objectives

The project was designed to demonstrate practical data engineering concepts including:

- Configuration-driven data validation
- Schema validation
- Datatype validation
- Null profiling
- Duplicate detection
- Business rule validation
- Referential integrity
- Validation severity
- Quality gates
- Modular ETL processing
- Error isolation
- Pipeline orchestration
- Step-level logging
- Pipeline-level logging
- Curated fact and dimension datasets
- Git-based project management

---

# Dataset

The project uses the **Brazilian E-Commerce Public Dataset by Olist**.

The dataset contains information related to Brazilian e-commerce transactions, including:

- Customers
- Orders
- Order items
- Payments
- Reviews
- Products
- Sellers
- Product category translations
- Geolocation

The raw dataset is kept outside version control.

The local raw data directory is:

```text
data/raw/
```

The project processes the source CSV files into curated datasets under:

```text
data/processed/
```

---

# Architecture

The current V1 architecture is:

```text
                         ┌──────────────────────┐
                         │    Raw Olist CSVs    │
                         └──────────┬───────────┘
                                    │
                                    ▼
                         ┌──────────────────────┐
                         │ Validation Pipeline  │
                         └──────────┬───────────┘
                                    │
          ┌─────────────────────────┼─────────────────────────┐
          │                         │                         │
          ▼                         ▼                         ▼
 ┌─────────────────┐       ┌─────────────────┐       ┌─────────────────┐
 │ Schema          │       │ Datatype        │       │ Null            │
 │ Validation      │       │ Validation      │       │ Validation      │
 └────────┬────────┘       └────────┬────────┘       └────────┬────────┘
          │                         │                         │
          └─────────────────────────┼─────────────────────────┘
                                    │
                    ┌───────────────┴───────────────┐
                    │                               │
                    ▼                               ▼
          ┌─────────────────┐             ┌─────────────────┐
          │ Duplicate       │             │ Business Rule   │
          │ Validation      │             │ Validation      │
          └────────┬────────┘             └────────┬────────┘
                   │                               │
                   └───────────────┬───────────────┘
                                   │
                                   ▼
                         ┌──────────────────────┐
                         │     Quality Gate     │
                         └──────────┬───────────┘
                                    │
                         ┌──────────┴──────────┐
                         │                     │
                       FAIL                   PASS
                         │                     │
                         ▼                     ▼
                  ┌─────────────┐       ┌─────────────┐
                  │    STOP     │       │     ETL     │
                  │  PIPELINE   │       │   LAYER     │
                  └─────────────┘       └──────┬──────┘
                                               │
                                               ▼
                                    ┌──────────────────────┐
                                    │  Curated Data Layer  │
                                    └──────────┬───────────┘
                                               │
                       ┌───────────────────────┼───────────────────────┐
                       │           │           │          │            │
                       ▼           ▼           ▼          ▼            ▼
                  dim_customer  dim_product  dim_seller  fact_order  fact_payment
                                                           │
                                                           ├── fact_order_item
                                                           │
                                                           └── fact_review
                                               │
                                               ▼
                                    ┌──────────────────────┐
                                    │ Pipeline Metadata    │
                                    └──────────────────────┘
```

---

# Project Structure

```text
data-quality-etl/
│
├── config/
│   ├── business_rules.csv
│   ├── duplicate_config.csv
│   ├── file_manifest.csv
│   └── schema_config.csv
│
├── data/
│   ├── raw/
│   ├── processed/
│   └── errors/
│       ├── business_rules/
│       ├── datatype/
│       ├── duplicate/
│       └── null/
│
├── metadata/
│   ├── pipeline_runs.csv
│   └── etl_step_runs.csv
│
├── src/
│   │
│   ├── etl/
│   │   ├── customer_etl.py
│   │   ├── order_etl.py
│   │   ├── order_item_etl.py
│   │   ├── payment_etl.py
│   │   ├── review_etl.py
│   │   ├── product_etl.py
│   │   ├── seller_etl.py
│   │   ├── run_logger.py
│   │   ├── step_logger.py
│   │   └── run_pipeline.py
│   │
│   └── validation/
│       ├── generate_schema_hash.py
│       ├── datatype_validator.py
│       ├── null_validator.py
│       ├── duplicate_validator.py
│       ├── business_rule_validator.py
│       ├── validation_gateway.py
│       └── run_validation.py
│
├── tests/
├── notebooks/
├── docs/
├── requirements.txt
├── .gitignore
└── README.md
```

---

# Data Quality Framework

The validation framework contains five validation layers:

```text
Schema
   │
   ▼
Datatype
   │
   ▼
Null
   │
   ▼
Duplicate
   │
   ▼
Business Rules
   │
   ▼
Quality Gate
```

Each validation component is implemented as a separate Python module.

---

# 1. Schema Validation

Schema validation verifies that the incoming source files match their expected structure.

The validation checks:

- File existence
- File size
- Column names
- Column order
- Expected schema
- Actual schema
- Schema SHA-256 hash

Expected source metadata is maintained in:

```text
config/file_manifest.csv
```

Example:

```text
source_name
file_pattern
expected_schema
partition_columns
file_type
```

The validator also generates schema metadata under:

```text
src/validation/metadata/
```

Schema-related errors are written to:

```text
data/errors/schema/
```

This allows source structure changes to be detected before downstream processing.

---

# 2. Datatype Validation

Datatype validation verifies configured columns against their expected datatypes.

Supported types include:

```text
string
integer
float
datetime
```

Datatype expectations are maintained in:

```text
config/schema_config.csv
```

Example configuration:

```text
source_name,column_name,expected_dtype

orders,order_id,string
orders,customer_id,string
orders,order_purchase_timestamp,datetime
orders,order_status,string
```

Null values are not treated as datatype failures because missing-value analysis is handled separately by the null validation layer.

Datatype validation results are written to:

```text
src/validation/metadata/datatype_validation.csv
```

Invalid datatype records are written to:

```text
data/errors/datatype/
```

---

# 3. Null Validation

The null validator profiles missing values across the source datasets.

For each column, the validation records:

- Source name
- Column name
- Total records
- Null count
- Null percentage
- Validation status

Null values are treated as **data quality findings rather than automatic pipeline failures**.

This is important because some fields in the Olist dataset are legitimately optional.

For example:

```text
order_reviews.review_comment_title
order_reviews.review_comment_message
```

contain a significant number of missing values.

Null validation results are written to:

```text
src/validation/metadata/null_validation.csv
```

Null records are also isolated under:

```text
data/errors/null/
```

---

# 4. Duplicate Validation

Duplicate validation checks configured business keys.

The duplicate rules are maintained in:

```text
config/duplicate_config.csv
```

Configured keys include:

```text
customers
    customer_id

orders
    order_id

order_items
    order_id + order_item_id

order_payments
    order_id + payment_sequential

order_reviews
    order_id + review_id

products
    product_id

sellers
    seller_id

product_category_translation
    product_category_name
```

Duplicate records are extracted using the configured composite keys and written to:

```text
data/errors/duplicate/
```

Geolocation is intentionally excluded from duplicate validation because multiple geographic records can legitimately share the same ZIP-code prefix.

---

# 5. Business Rule Validation

Business rules are maintained in:

```text
config/business_rules.csv
```

The framework supports several rule types:

```text
allowed_values
min_value
range
date_order
conditional_not_null
referential_integrity
```

---

## Allowed Values

Examples include:

```text
order_status
payment_type
customer_state
seller_state
```

For example, `order_status` is restricted to the configured set of valid Olist order statuses.

---

## Minimum Value

Examples include:

```text
payment_installments >= 1
payment_sequential >= 1
payment_value >= 0
price >= 0
freight_value >= 0
```

Product measurements and counts are also validated against configured minimum values.

---

## Range Validation

Review scores are validated using:

```text
1 <= review_score <= 5
```

---

## Date Validation

The project validates configured relationships between relevant order timestamps.

Examples include:

```text
order_purchase_timestamp <= order_approved_at

order_purchase_timestamp <= order_delivered_customer_date

order_purchase_timestamp <= order_estimated_delivery_date
```

Only rules currently considered valid for the project are enabled.

---

## Conditional Not-Null

Conditional rules ensure that required fields are populated when another field indicates that the value should exist.

For example:

```text
order_status = delivered
        │
        ▼
order_delivered_customer_date
must be present
```

The same principle is applied to the delivered carrier date.

---

## Referential Integrity

The pipeline validates relationships between source entities.

```text
orders.customer_id
        │
        ▼
customers.customer_id
```

```text
order_items.order_id
        │
        ▼
orders.order_id
```

```text
order_items.product_id
        │
        ▼
products.product_id
```

```text
order_items.seller_id
        │
        ▼
sellers.seller_id
```

```text
order_payments.order_id
        │
        ▼
orders.order_id
```

```text
order_reviews.order_id
        │
        ▼
orders.order_id
```

Failed business-rule records are written to:

```text
data/errors/business_rules/
```

Each rule has its own error output.

---

# Configuration-Driven Design

A key design principle of the project is separating **validation logic** from **validation configuration**.

Instead of hard-coding every expected schema, datatype, duplicate key, and business rule directly into Python code, the project maintains configuration files.

```text
config/
│
├── file_manifest.csv
│       └── Source files and expected schemas
│
├── schema_config.csv
│       └── Expected column datatypes
│
├── duplicate_config.csv
│       └── Duplicate detection keys
│
└── business_rules.csv
        └── Business and data quality rules
```

This provides a cleaner separation between:

```text
WHAT should be validated
        │
        ▼
Configuration
        │
        ▼
HOW it should be validated
        │
        ▼
Python Validation Framework
```

Adding or modifying rules therefore does not necessarily require changes to the validation engine itself.

---

# Quality Gate

The quality gate determines whether the ETL layer is allowed to execute.

The pipeline follows:

```text
Validation
    │
    ▼
Quality Gate
    │
    ├── Blocking FAIL
    │       │
    │       ▼
    │   Stop Pipeline
    │
    └── PASS
            │
            ▼
           ETL
```

Business rules support severity levels:

```text
FAIL
WARN
```

A failed rule with:

```text
severity = FAIL
```

blocks ETL execution.

A failed rule with:

```text
severity = WARN
```

is reported but does not block the pipeline.

This separates:

```text
Data Quality Detection
        │
        ├── Report the issue
        │
        └── Decide whether it blocks execution
```

This allows the same validation framework to support both blocking and non-blocking quality findings.

---

# ETL Layer

The ETL layer executes only after the validation pipeline and quality gate pass.

Seven curated datasets are generated.

---

## 1. dim_customer

Source:

```text
olist_customers_dataset.csv
```

Target:

```text
data/processed/dim_customer.csv
```

Represents customer master data.

---

## 2. fact_order

Source:

```text
olist_orders_dataset.csv
```

Target:

```text
data/processed/fact_order.csv
```

The transformation also derives analytical fields such as:

```text
purchase_date
purchase_year
purchase_month
delivery_days
delivery_delay_days
```

---

## 3. fact_order_item

Source:

```text
olist_order_items_dataset.csv
```

Target:

```text
data/processed/fact_order_item.csv
```

A derived field is created:

```text
item_total = price + freight_value
```

The dataset represents individual products included within orders.

---

## 4. fact_payment

Source:

```text
olist_order_payments_dataset.csv
```

Target:

```text
data/processed/fact_payment.csv
```

Contains payment-level transactional information.

---

## 5. fact_review

Source:

```text
olist_order_reviews_dataset.csv
```

Target:

```text
data/processed/fact_review.csv
```

Contains:

- Review identifiers
- Order relationships
- Review scores
- Review comments
- Review timestamps

The transformation parses the configured date fields and preserves nullable values where appropriate.

---

## 6. dim_product

Sources:

```text
olist_products_dataset.csv
product_category_name_translation.csv
```

Target:

```text
data/processed/dim_product.csv
```

The product dataset is enriched using a left join against the product category translation table.

A left join is used so that products without an English category translation are not removed from the curated dataset.

---

## 7. dim_seller

Source:

```text
olist_sellers_dataset.csv
```

Target:

```text
data/processed/dim_seller.csv
```

Represents seller master data.

---

# Curated Data Model

The resulting V1 model consists of dimension and fact datasets.

```text
                  ┌─────────────────┐
                  │  dim_customer   │
                  └────────┬────────┘
                           │
                           ▼
                  ┌─────────────────┐
                  │   fact_order    │
                  └───────┬─┬───────┘
                          │ │
              ┌───────────┘ └────────────┐
              │                          │
              ▼                          ▼
     ┌─────────────────┐       ┌─────────────────┐
     │ fact_order_item │       │  fact_payment   │
     └────────┬────────┘       └─────────────────┘
              │
       ┌──────┴──────┐
       │             │
       ▼             ▼
┌──────────────┐ ┌──────────────┐
│ dim_product  │ │  dim_seller  │
└──────────────┘ └──────────────┘

                  ┌─────────────────┐
                  │   fact_review   │
                  └────────┬────────┘
                           │
                           ▼
                      fact_order
```

The model provides a foundation for downstream analytical workloads.

---

# Pipeline Orchestration

The complete pipeline is orchestrated through:

```text
src/etl/run_pipeline.py
```

The execution sequence is:

```text
1. Start Pipeline
       │
       ▼
2. Run Data Validation
       │
       ▼
3. Evaluate Quality Gate
       │
       ├── FAIL ──► Log Failure ──► Stop
       │
       ▼
4. Execute ETL Steps
       │
       ├── dim_customer
       ├── fact_order
       ├── fact_order_item
       ├── fact_payment
       ├── fact_review
       ├── dim_product
       └── dim_seller
       │
       ▼
5. Log Each ETL Step
       │
       ▼
6. Log Pipeline Run
       │
       ▼
7. Report Final Status
```

Each ETL step is executed independently inside the orchestration loop.

If an ETL step fails, the failure is logged and the pipeline stops.

---

# Error Handling

Validation errors are isolated by validation category.

```text
data/errors/
│
├── schema/
├── business_rules/
├── datatype/
├── duplicate/
└── null/
```

This makes it possible to investigate different classes of data quality problems independently.

The ETL orchestration also catches runtime exceptions.

If an ETL step raises an exception:

```text
ETL Step Failure
       │
       ▼
Capture Exception
       │
       ▼
Log Failed Step
       │
       ▼
Log Failed Pipeline Run
       │
       ▼
Stop Pipeline
```

The pipeline exits with a failure status when execution cannot be completed successfully.

---

# Logging and Metadata

The pipeline maintains both pipeline-level and step-level execution metadata.

---

## Pipeline-Level Logging

File:

```text
metadata/pipeline_runs.csv
```

The pipeline log records:

| Field | Description |
|---|---|
| run_id | Unique pipeline run identifier |
| start_time | Pipeline start timestamp |
| end_time | Pipeline completion timestamp |
| duration_seconds | Total pipeline execution duration |
| validation_status | Validation result |
| etl_steps | Number of configured ETL steps |
| completed_steps | Number of successfully completed steps |
| failed_steps | Number of failed steps |
| status | Overall pipeline status |

Possible pipeline statuses include:

```text
SUCCESS
VALIDATION_FAILED
ETL_FAILED
```

---

## ETL Step-Level Logging

File:

```text
metadata/etl_step_runs.csv
```

Each ETL step records:

| Field | Description |
|---|---|
| run_id | Pipeline run identifier |
| step_name | ETL step name |
| start_time | Step start timestamp |
| end_time | Step completion timestamp |
| duration_seconds | Step execution duration |
| status | Step execution status |
| error_message | Error details when applicable |

This provides visibility into individual ETL execution times and failures.

---

# Running the Project

## 1. Clone the Repository

Clone the repository and navigate to the project directory.

```bash
git clone <repository-url>
cd data-quality-etl
```

---

## 2. Create a Virtual Environment

```bash
python -m venv .venv
```

Activate it on Windows:

```bash
.venv\Scripts\activate
```

---

## 3. Install Dependencies

```bash
pip install -r requirements.txt
```

The current V1 implementation primarily uses:

```text
pandas
```

---

## 4. Add the Dataset

Place the Olist source CSV files under:

```text
data/raw/
```

The expected files are:

```text
olist_customers_dataset.csv
olist_geolocation_dataset.csv
olist_order_items_dataset.csv
olist_order_payments_dataset.csv
olist_order_reviews_dataset.csv
olist_orders_dataset.csv
olist_products_dataset.csv
olist_sellers_dataset.csv
product_category_name_translation.csv
```

---

## 5. Run Validation

Run:

```bash
python src/validation/run_validation.py
```

The validation pipeline executes:

```text
Schema
   ↓
Datatype
   ↓
Null
   ↓
Duplicate
   ↓
Business Rules
   ↓
Quality Gate
```

---

## 6. Run the Complete ETL Pipeline

Run:

```bash
python src/etl/run_pipeline.py
```

The pipeline first executes validation.

If the quality gate passes, ETL execution begins.

If a blocking validation failure occurs, ETL execution is prevented.

---

# Current Validation Results

The current V1 configuration identifies a small number of intentional business-rule violations in the Olist source data.

Current configured failing rules include:

```text
PAY-003
ORD-007
ORD-008
```

These rules are configured with:

```text
severity = FAIL
```

Therefore, when these violations are present, the quality gate correctly prevents ETL execution.

This demonstrates the intended behavior:

```text
Source Data
    │
    ▼
Business Rule Validation
    │
    ├── PASS ──► Continue
    │
    └── FAIL
          │
          ▼
      Quality Gate
          │
          ▼
      Stop ETL
```

The validation framework itself is therefore functioning as an execution control mechanism rather than simply generating a report.

---

# ETL Output

When the quality gate passes, the following curated datasets are produced:

```text
data/processed/
│
├── dim_customer.csv
├── dim_product.csv
├── dim_seller.csv
├── fact_order.csv
├── fact_order_item.csv
├── fact_payment.csv
└── fact_review.csv
```

The current processed datasets contain approximately:

```text
dim_customer       99,441 records
fact_order         99,441 records
fact_order_item   112,650 records
fact_payment      103,886 records
fact_review        99,224 records
dim_product        32,951 records
dim_seller          3,095 records
```

---

# Technologies

The current V1 implementation uses:

- **Python**
- **Pandas**
- **CSV**
- **Git**
- **GitHub**

The project intentionally keeps the current processing layer lightweight while applying production-oriented data engineering design principles.

---

# Engineering Concepts Demonstrated

## Data Quality

- Schema validation
- Schema hashing
- Datatype validation
- Null profiling
- Duplicate detection
- Business rule validation
- Referential integrity
- Validation severity
- Quality gates

## ETL

- Source-to-target transformation
- Data cleansing
- Datatype conversion
- Derived columns
- Multi-source joins
- Dimension modelling
- Fact modelling
- Curated datasets

## Pipeline Engineering

- Validation-first execution
- Pipeline orchestration
- Step-level execution
- Exception handling
- Execution timing
- Pipeline metadata
- Step metadata
- Failure handling

## Configuration Management

- External validation configuration
- Schema configuration
- Duplicate-key configuration
- Business-rule configuration
- Separation of logic and configuration

## Software Engineering

- Modular Python scripts
- Reusable validation components
- Separation of concerns
- Error isolation
- Git version control
- Repository organization

---

# Design Decisions

## Validation Before ETL

The pipeline validates the source data before transformation.

This prevents configured blocking data quality issues from reaching the curated layer.

---

## Configuration Instead of Hard-Coding

Schemas, datatypes, duplicate keys, and business rules are maintained externally.

This makes the validation framework easier to maintain and extend.

---

## Separate Validation Modules

Each validation category has a dedicated module.

```text
generate_schema_hash.py
datatype_validator.py
null_validator.py
duplicate_validator.py
business_rule_validator.py
validation_gateway.py
```

This keeps validation responsibilities separated.

---

## Separate Error Outputs

Each validation category produces its own error artifacts.

This makes root-cause investigation easier.

---

## Severity-Aware Quality Gate

Not every data quality issue must necessarily stop a pipeline.

The framework distinguishes between:

```text
FAIL
WARN
```

This provides a mechanism to separate blocking data quality issues from non-blocking observations.

---

## Modular ETL

Each target dataset has a dedicated ETL module.

```text
customer_etl.py
order_etl.py
order_item_etl.py
payment_etl.py
review_etl.py
product_etl.py
seller_etl.py
```

This keeps transformations isolated and easier to maintain.

---

## Referential Integrity

Relationships between core entities are explicitly validated before ETL.

This helps prevent orphan records from entering the curated data layer.

---

# Scope of V1

The current version intentionally focuses on building the core data quality and ETL foundation using local Python/Pandas processing.

The following are outside the current V1 scope:

- Cloud storage
- Distributed processing
- Workflow scheduling
- Production cloud deployment
- BI dashboards
- Incremental processing
- CI/CD automation

These can be considered future extensions rather than requirements for the current implementation.

---

# Future Enhancements

Potential V2 enhancements include:

### Cloud Data Lake

```text
Local CSV
    ↓
AWS S3 Landing
    ↓
Validation
    ↓
Curated Storage
```

### Distributed Processing

Replace or extend the Pandas processing layer with:

```text
PySpark
Spark SQL
Databricks
```

### Workflow Orchestration

Introduce:

```text
Apache Airflow
```

for scheduled and dependency-aware pipeline execution.

### Data Warehouse

Load curated datasets into a warehouse such as:

```text
Amazon Redshift
```

### Data Quality Dashboard

Build a monitoring layer using:

```text
Power BI
```

for:

- Validation failures
- Null percentages
- Duplicate counts
- Business-rule violations
- Pipeline execution times
- Historical quality trends

### Automated Testing

Add:

```text
pytest
```

for unit and integration testing.

### CI/CD

Introduce automated:

```text
Git
   ↓
Tests
   ↓
Validation
   ↓
Build
   ↓
Deployment
```

---

# Project Status

| Component | Status |
|---|---|
| File Arrival Validation | ✅ Complete |
| Schema Validation | ✅ Complete |
| Schema Hashing | ✅ Complete |
| Datatype Validation | ✅ Complete |
| Null Validation | ✅ Complete |
| Duplicate Validation | ✅ Complete |
| Business Rule Validation | ✅ Complete |
| Referential Integrity | ✅ Complete |
| Quality Gate | ✅ Complete |
| Customer ETL | ✅ Complete |
| Order ETL | ✅ Complete |
| Order Item ETL | ✅ Complete |
| Payment ETL | ✅ Complete |
| Review ETL | ✅ Complete |
| Product ETL | ✅ Complete |
| Seller ETL | ✅ Complete |
| Pipeline Orchestration | ✅ Complete |
| Error Handling | ✅ Complete |
| Pipeline Logging | ✅ Complete |
| Step-Level Logging | ✅ Complete |
| Documentation | ✅ Complete |

---

# V1 Completion

The V1 pipeline provides a complete local validation-first ETL workflow:

```text
                 ┌─────────────────┐
                 │   Raw CSV Data  │
                 └────────┬────────┘
                          │
                          ▼
                 ┌─────────────────┐
                 │   Validation    │
                 └────────┬────────┘
                          │
                          ▼
                 ┌─────────────────┐
                 │  Quality Gate   │
                 └────────┬────────┘
                          │
                    ┌─────┴─────┐
                    │           │
                  FAIL         PASS
                    │           │
                    ▼           ▼
                  STOP         ETL
                                │
                                ▼
                       ┌─────────────────┐
                       │ Curated Tables  │
                       └────────┬────────┘
                                │
                                ▼
                       ┌─────────────────┐
                       │    Metadata     │
                       └─────────────────┘
```

The implementation demonstrates the core principles required for a production-oriented data pipeline while keeping the V1 implementation manageable and locally executable.

---

# License

This project is intended for learning, portfolio, and interview preparation purposes.

The underlying Olist dataset is provided by its original publisher under its applicable dataset terms.