import sys
import os
import pandas as pd
import numpy as np
from dataclasses import dataclass
from src.exception import CustomException
from src.utils import load_object 
from src.unsupervised_components.unsupervised_data_transformation import DataTransformation
from src.components.awr_parser import AWRParser 

@dataclass
class UnsupervisedPredictionPipelineConfig:
    scaler_path: str = os.path.join('artifacts', 'unsupervised_scaler.pkl')
    model_path: str = os.path.join("artifacts", "unsupervised_model.pkl")

class UnsupervisedPredictPipeline:
    def __init__(self):
        self.config = UnsupervisedPredictionPipelineConfig()
        self.scaler = load_object(self.config.scaler_path)
        self.model = load_object(self.config.model_path)
        self.parser = AWRParser() 
        self.feature_engineer = DataTransformation().get_data_transformer_object

    def predict(self, html_filepath: str, anomaly_threshold: float = -0.025):
        try:
            #parse awr report
            report_data = self.parser.parse_single_report(html_filepath)
            flattened_data = self.parser._flatten_report_data(report_data)
            input_df = pd.DataFrame([flattened_data])

            #feature engineering
            features_df = self.feature_engineer(input_df)

            #scale features
            scaled_data = self.scaler.transform(features_df)

            #make prediction
            anomaly_score = self.model.decision_function(scaled_data)[0]

            if anomaly_score < anomaly_threshold:
                status = "ANOMALY DETECTED"
            else:
                status = "NORMAL"

            return status, anomaly_score

        except Exception as e:
            raise CustomException(e, sys)              
