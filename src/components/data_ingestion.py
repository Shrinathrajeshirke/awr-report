import os
import sys
import pandas as pd
from sklearn.model_selection import train_test_split
from src.logger import logging
from src.exception import CustomException
from dataclasses import dataclass

@dataclass
class DataIngestionConfig:
    raw_data_path: str = os.path.join('data', 'awr_metrics.csv')

class DataIngestion:
    def __init__(self):
        self.ingestion_config = DataIngestionConfig()

    def initiate_data_ingestion(self):
        """ Load and validate AWR metrics data """
        try:
            logging.info("Starting data ingestion")

            #load data
            df = pd.read_csv(self.ingestion_config.raw_data_path)

            #basic validation
            logging.info(f"Columns: {df.columns.tolist()}")
            logging.info(f"Missing values: {df.isnull().sum().sum()}")
            logging.info(f"Duplicated values: {df.duplicated().sum()}")
            logging.info(f"Anomaly distribution:\n {df['anomaly_type'].value_counts()}")

            logging.info("Data ingestion completed successfully")
            return df
        except Exception as e:
            raise CustomException(e, sys)
        