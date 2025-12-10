# AWR Analysis and Anomaly Detection Project

## 1. Project Overview

This project implements a robust, end-to-end pipeline for automated analysis of Oracle AWR (Automatic Workload Repository) performance reports. It features:

1.  **Automated Extraction:** A parser to convert unstructured AWR HTML reports into structured metrics.
2.  **Dual ML Pipelines:** Parallel **Supervised** (classification) and **Unsupervised** (anomaly detection) models.
3.  **Deployment:** A Streamlit application for real-time inference using the unsupervised model.

## 2. Project Structure

The repository follows a clear, modular structure separating core components, pipelines, and artifacts.

## 📁 Project Structure
```
AWR-Anomaly-Detection/
├── artifacts/
│   ├── scaler.pkl                    # Supervised StandardScaler
│   ├── label_encoder.pkl             # Supervised LabelEncoder
│   ├── model.pkl                     # Supervised Random Forest Model
│   ├── unsupervised_scaler.pkl       # Unsupervised StandardScaler
│   └── unsupervised_model.pkl        # Unsupervised Isolation Forest Model
│
├── data/
│   ├── raw_awr_reports/              # Input AWR HTML reports
│   └── awr_metrics.csv               # Parsed and consolidated structured data
│
├── pipeline/
│   ├── train_pipeline.py             # Supervised training workflow
│   ├── predict_pipeline.py           # Supervised prediction workflow
│   ├── unsupervised_train_pipeline.py     # Unsupervised training workflow
│   └── unsupervised_predict_pipeline.py   # Unsupervised prediction workflow
│
├── src/
│   ├── components/
│   │   ├── awr_parser.py             # Core logic for HTML parsing & extraction
│   │   ├── data_ingestion.py         # Data loading and validation
│   │   ├── data_transformation.py    # Supervised feature engineering/scaling/SMOTE
│   │   └── model_trainer.py          # Supervised model selection (Random Forest)
│   │
│   ├── unsupervised_components/
│   │   ├── unsupervised_data_transformation.py  # Unsupervised feature engineering
│   │   └── unsupervised_model_trainer.py        # Isolation Forest training
│   │
│   ├── generators/
│   │   └── awr_report_generator.py   # Script for synthetic data creation
│   │
│   ├── exception.py
│   ├── logger.py
│   └── utils.py                      # Helper functions
│
└── unsupervised_app.py               # Streamlit web application
```
## 3. Data Extraction Pipeline

The initial phase converts raw AWR reports into a structured CSV dataset.

### 3.1. AWR Report Generator (Synthetic Data)
* **Location:** `src/generators/awr_report_generator.py`
* **Purpose:** Generates synthetic AWR reports with realistic metrics and injected anomaly patterns.
* **Output:** 300 HTML reports in `data/raw_awr_reports/`.
    * 80% Normal reports
    * 20% Anomaly reports (CPU\_SPIKE, IO\_BOTTLENECK, etc.)
* **Execution:**
    ```bash
    python src/generators/awr_report_generator.py
    ```

### 3.2. AWR Parser
* **Location:** `src/components/awr_parser.py`
* **Purpose:** Extracts 43+ key metrics from AWR HTML reports, flattens, and cleans the data.
    * **Extracted Metrics:** Load Profile, Instance Efficiency, Memory Statistics, OS Statistics, Top Wait Events, and calculated ratios (e.g., Physical/Logical ratio).
* **Output:** `data/awr_metrics.csv`

### 3.3. Data Ingestion
* **Location:** `src/components/data_ingestion.py`
* **Purpose:** Loads the parsed CSV, validates data quality (shape, missing values), and prepares the DataFrame for transformation.
* **Execution:**
    ```bash
    python src/components/data_ingestion.py
    ```

## 4. Data Transformation and Feature Engineering

### Common Steps (Shared by both pipelines)
1.  **Feature Engineering:** Drops 12 identifier/redundant columns, extracts temporal features (hour, day of week, month), applies cyclical encoding (sin/cos), and adds an `is_weekend` flag.
2.  **Standardization:** Features are scaled using `StandardScaler` to normalize the distribution.

### 4.1. Supervised Transformation (`src/components/data_transformation.py`)
* **Label Encoding:** Multi-class label encoding for the 7 anomaly classes (0-6).
* **Balancing:** **SMOTE** oversampling is applied to the training set to resolve the 80:20 class imbalance, resulting in ~1344 balanced samples (192 per class).
* **Artifacts:** `artifacts/label_encoder.pkl`, `artifacts/scaler.pkl`.

### 4.2. Unsupervised Transformation (`src/components/unsupervised_data_transformation.py`)
* **Key Difference:** This pipeline skips label encoding and balancing, training directly on the feature matrix $X$.
* **Artifacts:** `artifacts/unsupervised_scaler.pkl`.

## 5. Machine Learning Pipelines

The project maintains two distinct models for different operational requirements.

### 5.1. Supervised Classification (Classification of Anomaly Type)
* **Model:** Random Forest Classifier
* **Training Pipeline:** `pipeline/train_pipeline.py`
* **Findings:** The model achieved perfect performance on the test set due to the high-quality synthetic data and aggressive balancing.
    * **Accuracy:** **1.0**
    * **Classification Report:** Precision, Recall, and F1-score of **1.00** for all 7 classes (including NORMAL).
    * **Confusion Matrix:** Perfect diagonal matrix, confirming zero misclassifications.

### 5.2. Unsupervised Anomaly Detection (Real-World Alerting)
* **Model:** Isolation Forest (`sklearn.ensemble.IsolationForest`)
* **Training Pipeline:** `pipeline/unsupervised_train_pipeline.py`
* **Contamination Parameter:** Set to `0.20` to match the expected anomaly rate of the dataset.
* **Execution:**
    ```bash
    python pipeline/unsupervised_train_pipeline.py
    ```
* **Findings (Test Set Evaluation):**
    * Min Anomaly Score observed: **-0.1528**
    * Max Anomaly Score observed: **0.0738**
    * Number of reports predicted as anomalies (Score < Threshold): **11**

## 6. Deployment

The final product is deployed as a user-friendly Streamlit application that uses the Unsupervised Anomaly Detection pipeline.

* **Application File:** `unsupervised_app.py`
* **Prediction Pipeline:** `pipeline/unsupervised_predict_pipeline.py`
* **Functionality:** Allows users to upload an AWR HTML file and instantly receive an **Anomaly Score** and **Status** (NORMAL or ANOMALY DETECTED) based on the Isolation Forest boundary.
* **Execution:**
    ```bash
    streamlit run unsupervised_app.py
    ```

