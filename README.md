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

### Project Structure
```
awr-analysis/
├── data/
│   ├── raw_awr_reports/          # Generated AWR HTML files
│   └── awr_metrics.csv           # Extracted metrics CSV
├── src/
│   ├── components/
│   │   └── awr_parser.py          # HTML parser
│   ├── generators/
│   │   └── awr_report_generator.py # Report generator
│   ├── logger.py                  # Logging utility
│   └── exception.py               # Custom exceptions
└── README.md
```
