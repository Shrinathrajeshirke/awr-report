from src.components.data_ingestion import DataIngestion, DataIngestionConfig
from src.components.data_transformation import DataTransformation, DataTransformationConfig

ingestion = DataIngestion()
df = ingestion.initiate_data_ingestion()

transformation = DataTransformation()
X_train, X_test, y_train, y_test, label_encoder = transformation.initiate_data_transformation(df)

print(f"\nFinal shapes:")
print(f"X_train: {X_train.shape}")
print(f"X_test: {X_test.shape}")
print(f"y_train: {y_train.shape}")
print(f"y_test: {y_test.shape}")