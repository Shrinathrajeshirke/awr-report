import sys
from src.logger import logging
from src.exception import CustomException
from src.components.data_ingestion import DataIngestion, DataIngestionConfig
from src.components.data_transformation import DataTransformation, DataTransformationConfig
from src.components.model_trainer import ModelTrainer, ModelTrainerConfig

def training_pipeline():

    try: 
        ingestion = DataIngestion()
        df = ingestion.initiate_data_ingestion()

        transformation = DataTransformation()
        X_train, X_test, y_train, y_test, label_encoder = transformation.initiate_data_transformation(df)

        trainer = ModelTrainer()
        accuracy, model_name = trainer.initiate_model_trainer(X_train, X_test, y_train, y_test)
    except Exception as e:
        raise CustomException(e, sys)