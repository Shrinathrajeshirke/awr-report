import os
import sys
from sklearn.multiclass import OneVsRestClassifier
from src.utils import save_object, evaluate_models
from src.logger import logging
from src.exception import CustomException
from dataclasses import dataclass

from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.tree import DecisionTreeClassifier
from sklearn.neighbors import KNeighborsClassifier
from xgboost import XGBClassifier

from sklearn.metrics import accuracy_score, classification_report, confusion_matrix


@dataclass
class ModelTrainerConfig:
    trained_model_file_path: str = os.path.join("artifacts","model.pkl")

class ModelTrainer:
    def __init__(self):
        self.model_trainer_config = ModelTrainerConfig()

    def initiate_model_trainer(self, X_train, X_test, y_train, y_test):
        try:
            logging.info("Starting model training")

            # define models
            models = {
                "Random Forest": RandomForestClassifier(random_state=42),
                "XGBoost": XGBClassifier(eval_metric='mlogloss', random_state=42),
                "Logistic Regression": LogisticRegression(max_iter=1000, random_state=42),
                "Decision Tree": DecisionTreeClassifier(random_state=42),
                "KNN" : KNeighborsClassifier()
            }
            
            # hyperparameters for Gridsearch
            params = {
                "Random Forest":{
                    'n_estimators': [100, 200],
                    'max_depth': [10, 20, None],
                    'min_samples_split': [2, 5]
                },
                "XGBoost": {
                    'n_estimators': [100, 200],
                    'max_depth': [3, 5, 7],
                    'learning_rate': [0.01, 0.1]
                },
                "Logistic Regression": {
                    'C': [0.1, 1, 10],
                    'solver': ['lbfgs']
                },
                "Decision Tree": {
                    'max_depth': [5, 10, 20],
                    'min_samples_split': [2, 5, 10]
                },
                "KNN": {
                    'n_neighbors': [3, 5, 7],
                    'weights': ['uniform', 'distance']
                }
            }

            # Evaluate models
            model_report = evaluate_models(X_train=X_train,
                                           y_train=y_train,
                                           X_test=X_test,
                                           y_test=y_test,
                                           models=models,
                                           param=params)
            
            logging.info(f"Model evaluation report: {model_report}")
            
            # Extract all accuracy scores
            accuracy_scores = {
                model_name: metrics['accuracy_score']
                for model_name, metrics in model_report.items()
            }

            # Find the model with the highest accuracy score
            best_model_name = max(accuracy_scores, key=accuracy_scores.get)
            
            # Get the best score and the corresponding model object
            best_model_score = accuracy_scores[best_model_name]
            best_model = models[best_model_name]

            if best_model_score < 0.6:
                raise CustomException("No best model found")
            
            logging.info(f"Best model: {best_model_name} with accuracy: {best_model_score}")

            #save the model
            save_object(
                file_path=self.model_trainer_config.trained_model_file_path,
                obj=best_model
            )

            y_pred = best_model.predict(X_test)
            accuracy = accuracy_score(y_test, y_pred)

            logging.info(f"\nClassification Report:\n {classification_report(y_test, y_pred)}")
            logging.info(f"\nConfusion Matrix:\n{confusion_matrix(y_test, y_pred)}")

            return accuracy, best_model_name


        except Exception as e:
            raise CustomException(e, sys)
        
        



