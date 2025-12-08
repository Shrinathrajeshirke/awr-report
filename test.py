from src.components.awr_parser import AWRParser

parser = AWRParser()

df = parser.parse_all_reports(
    input_dir='data/raw_awr_reports',
    output_csv='data/awr_metrics.csv'
)

print(f"Parsed {len(df)} reports")
print(f"Columns: {len(df.columns)}")
print(df.head())
print(df['anomaly_type'].value_counts())


