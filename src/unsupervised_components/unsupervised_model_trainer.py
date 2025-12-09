import os
import sys
import numpy as np
from sklearn.ensemble import IsolationForest
from sklearn.metrics import confusion_matrix
from src.utils import save_object
from src.logger import logging
from src.exception import CustomException
from dataclasses import dataclass

@dataclass
class UnsupervisedModelTrainingConfig:
    trained_model_file_path: str = os.path.join("artifacts","unsupervised_model.pkl")

class UnsupervisedModelTrainer:
    def __init__(self):
        self.model_trainer_config =UnsupervisedModelTrainingConfig()

    def initiate_model_trainer(self, X_train, X_test):
        try:
            logging.info("starting unsupervised model training (Isolation Forest)")

            #define the model
            model = IsolationForest(
                n_estimators=100,
                contamination=0.20,
                random_state=42,
                n_jobs=-1
            )

            #fit the model
            model.fit(X_train)
            logging.info("Isolation forest model training completed")

            #predict the class (-1 for anomaly, 1 for normal)
            y_pred_test = model.predict(X_test)

            #predict the anomaly score (lower is anomalous)
            anomaly_scores= model.decision_function(X_test)

            logging.info(f"Min Anomaly Score: {np.min(anomaly_scores):.4f}")
            logging.info(f"Max Anomaly Score: {np.max(anomaly_scores):.4f}")
            logging.info(f"Number of predicted anomalies (-1): {np.sum(y_pred_test == -1)}")

            # Save the trained model
            save_object(
                file_path=self.model_trainer_config.trained_model_file_path,
                obj=model
            )
            logging.info("Unsupervised model saved successfully.")
            
            return model, anomaly_scores

        except Exception as e:
            raise CustomException(e, sys)
