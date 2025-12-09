import sys
import os
import pandas as pd
import numpy as np
from src.components.awr_parser import AWRParser
from src.exception import CustomException
from src.utils import load_object

class PredictionPipeline:
    def __init__(self):
        self.label_encoder = load_object(os.path.join('artifacts','label_encoder.pkl'))
        self.scaler = load_object(os.path.join('artifacts','scaler.pkl'))
        self.model = load_object(os.path.join('artifacts', 'model.pkl'))

        self.parser = AWRParser()

    def feature_engineer_data(self, df):
        try:
            
            drop_columns = ['filename', 'db_name', 'db_id', 'instance','db_time_min', 'top_event_1_time_sec', 'top_event_2_time_sec', 'top_event_2_avg_ms', 'physical_to_logical_ratio', 'top_event_1_name', 'top_event_2_name', 'top_event_3_name', 'anomaly_type']
            df = df.drop(columns=drop_columns, axis=1)

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

            return df
        except Exception as e:
            raise CustomException(e, sys)
        
    def predict(self, html_filepath:str):
        try:
            #reads the awr html file
            report_data = self.parser.parse_single_report(html_filepath)
            #flattens the data from html file
            flattened_data = self.parser._flatten_report_data(report_data)

            #convert flattened data to dataframe
            input_df = pd.DataFrame([flattened_data])

            #feature engineering
            features_df = self.feature_engineer_data(input_df)

            #scale features
            scaled_data = self.scaler.transform(features_df)

            #make prediction
            y_pred_encoded = self.model.predict(scaled_data)

            #inverse transform to get result
            anomaly_type = self.label_encoder.inverse_transform(y_pred_encoded)

            return anomaly_type[0]

        except Exception as e:
            raise CustomException(e, sys)