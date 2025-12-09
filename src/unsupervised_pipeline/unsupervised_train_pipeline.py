import os
import sys
from src.logger import logging
from src.exception import CustomException
from src.components.data_ingestion import DataIngestion
from src.unsupervised_components.unsupervised_data_transformation import DataTransformation
from src.unsupervised_components.unsupervised_model_trainer import UnsupervisedModelTrainer

def unsupervised_training_pipeline():
    try:
        logging.info("unsupervised model training started")

        ## data ingestion
        ingestion = DataIngestion()
        df = ingestion.initiate_data_ingestion()
        logging.info('Data ingestion completed')

        ## data transformation
        transformation = DataTransformation()
        X_train_scaled, X_test_scaled = transformation.initiate_data_transformation(df)
        logging.info('Data transformation completed')

        ## model training
        trainer = UnsupervisedModelTrainer()
        model, anomaly_scores = trainer.initiate_model_trainer(X_train_scaled, X_test_scaled)
        logging.info("model training completed")
        
    except Exception as e:
        raise CustomException(e, sys)
    
if __name__ == '__main__':
    unsupervised_training_pipeline()