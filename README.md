# AWR Analysis Project

## Data Extraction Pipeline

### Overview
Automated extraction of Oracle AWR (Automatic Workload Repository) reports for database health monitoring and anomaly detection.

### Components

#### 1. AWR Report Generator
**Location:** `src/generators/awr_report_generator.py`

Generates synthetic AWR reports with realistic metrics and anomaly patterns.
```bash
python src/generators/awr_report_generator.py
```

**Output:** 300 HTML reports in `data/raw_awr_reports/`
- 80% Normal reports
- 20% Anomaly reports (CPU_SPIKE, MEMORY_PRESSURE, IO_BOTTLENECK, LOCK_CONTENTION, TEMP_SPACE, NETWORK_LATENCY)

#### 2. AWR Parser
**Location:** `src/components/awr_parser.py`

Extracts key metrics from AWR HTML reports and converts to structured CSV.
```bash
python test_parser.py
```

**Key Features:**
- Parses header information (DB name, timestamps, elapsed time)
- Extracts 35+ performance metrics from multiple sections
- Flattens nested data structures
- Handles missing values and data cleaning

**Extracted Metrics:**
- Load Profile: DB Time, CPU, I/O, transactions
- Instance Efficiency: Buffer hit %, parse ratios
- Memory Statistics: SGA/PGA usage, sorts
- OS Statistics: CPU usage, load average
- Wait Events: Top 3 wait events with timings
- Time Model: Parse time percentages
- Calculated: CPU % of DB Time, Physical/Logical ratio

**Output:** `data/awr_metrics.csv`

### Data Ingestion
**Location:** `src/components/data_ingestion.py`

Loads and validates the parsed AWR metrics CSV file.
```bash
python src/components/data_ingestion.py
```

**Features:**
- Loads AWR metrics from CSV (300 reports, 43 features)
- Validates data quality (shape, missing values, duplicates)
- Logs anomaly distribution
- Returns DataFrame for transformation

---

### Data Transformation
**Location:** `src/components/data_transformation.py`

Applies feature engineering, encoding, balancing, and scaling.

**Key Steps:**

1. **Feature Engineering:**
   - Drops 12 unnecessary columns (identifiers, redundant metrics, text features)
   - Extracts temporal features (hour, day of week, month)
   - Applies cyclical encoding (sin/cos) for time features
   - Adds is_weekend flag

2. **Data Preprocessing:**
   - Multi-class label encoding (7 classes: NORMAL + 6 anomaly types)
   - Stratified train-test split (80/20)
   - SMOTE balancing on training set (handles class imbalance)
   - StandardScaler normalization

3. **Saved Artifacts:**
   - `artifacts/label_encoder.pkl` - For decoding predictions
   - `artifacts/scaler.pkl` - For feature scaling

**Output:**
- Balanced training set: ~1344 samples (192 per class)
- Test set: 60 samples (maintains original distribution)
- 36 engineered features

**Class Distribution After SMOTE:**
```
Original Train: {NORMAL: 192, CPU_SPIKE: 8, IO_BOTTLENECK: 8, ...}
After SMOTE: {0: 192, 1: 192, 2: 192, 3: 192, 4: 192, 5: 192, 6: 192}
```

