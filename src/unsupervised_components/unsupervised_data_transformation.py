import os 
import sys
import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder, StandardScaler
#from imblearn.over_sampling import SMOTE
from src.logger import logging
from collections import Counter
from src.exception import CustomException
from dataclasses import dataclass
from src.utils import save_object

@dataclass
class DataTransformationConfig:
    scaler_path: str = os.path.join('artifacts','unsupervised_scaler.pkl')

class DataTransformation:
    def __init__(self):
        self.transformation_config = DataTransformationConfig()
        self.label_encoder = LabelEncoder()
        self.scaler = StandardScaler()

    def get_data_transformer_object(self, df):
        try:
            logging.info("starting feature engineering")
            drop_columns = ['anomaly_type','filename', 'db_name', 'db_id', 'instance','db_time_min', 'top_event_1_time_sec', 'top_event_2_time_sec', 'top_event_2_avg_ms', 'physical_to_logical_ratio', 'top_event_1_name', 'top_event_2_name', 'top_event_3_name']
            df = df.drop(columns=drop_columns, axis=1)
            logging.info(f"Dropped columns: {drop_columns}")

            ## converts start_time and end_time in datetime format
            df['start_time'] = pd.to_datetime(df['start_time'])
            df['end_time'] = pd.to_datetime(df['end_time'])
            
            ## extract time features
            df['start_hour'] = df['start_time'].dt.hour
            df['day_of_week'] = df['start_time'].dt.dayofweek
            df['start_month'] = df['start_time'].dt.month
            df['is_weekend'] = (df['start_time'].dt.dayofweek >= 5).astype(int)

            # Encode Hour of Day (Cycle Length = 24)
            df['hour_sin'] = np.sin(2 * np.pi * df['start_hour'] / 24)
            df['hour_cos'] = np.cos(2 * np.pi * df['start_hour'] / 24)

            # Encode Day of Week (Cycle Length = 7)
            df['day_sin'] = np.sin(2 * np.pi * df['day_of_week'] / 7)
            df['day_cos'] = np.cos(2 * np.pi * df['day_of_week'] / 7)

            # Encode month (Cycle Length = 30)
            df['month_sin'] = np.sin(2 * np.pi * df['start_month'] / 30)
            df['month_cos'] = np.cos(2 * np.pi * df['start_month'] / 30)
            
            #drop original time columns
            df = df.drop(columns=['start_time', 'end_time', 'start_hour', 'day_of_week', 'start_month'])

            logging.info("feature engineering completed")
            return df
        
        except Exception as e:
            raise CustomException(e, sys)
        
    def initiate_data_transformation(self, df):
        try:
            logging.info("starting data transformation")

            #apply feature engineering
            df = self.get_data_transformer_object(df)


            # stratified train-test split 
            X_train, X_test= train_test_split(df, test_size=0.2, random_state=42)

            logging.info(f"Train set shape: X_train: {X_train.shape}")
            logging.info(f"Test set shape: X_test: {X_test.shape}")

            # scale features
            X_train_scaled = self.scaler.fit_transform(X_train)
            X_test_scaled = self.scaler.transform(X_test)

            logging.info("feature scaling completed")

            # save preprocessing object
            save_object(file_path=self.transformation_config.scaler_path, obj = self.scaler)

            logging.info("data transformation completed successfully")

            return X_train_scaled, X_test_scaled
        
        except Exception as e:
            raise CustomException(e, sys)
