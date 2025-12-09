import os
import sys
import numpy as np
import pickle
from sklearn.model_selection import GridSearchCV
from sklearn.metrics import accuracy_score, precision_score, recall_score, roc_auc_score, f1_score
import dill
from src.exception import CustomException
from src.logger import logging

def save_object(file_path, obj):
    try:
        dir_path = os.path.dirname(file_path)
        os.makedirs(dir_path, exist_ok=True)

        with open(file_path, "wb") as file_obj:
            dill.dump(obj, file_obj)

    except Exception as e:
        raise CustomException(e, sys)
    
def evaluate_models(X_train, y_train, X_test, y_test, models, param):
    try:
        report = {}

        for i in range(len(list(models))):
            model = list(models.values())[i]
            model_name = list(models.keys())[i]
            logging.info(f"started training of {model_name}")
            para = param[model_name]

            gs = GridSearchCV(model, para, cv=3)
            gs.fit(X_train, y_train)

            model.set_params(**gs.best_params_)
            model.fit(X_train, y_train)

            ## make predictions
            y_train_pred = model.predict(X_train)
            y_test_pred = model.predict(X_test)

            y_test_proba = model.predict_proba(X_test)
            
            test_accuracy_score = accuracy_score(y_test, y_test_pred)
            test_recall_score = recall_score(y_test, y_test_pred, average="weighted")
            test_precision_score = precision_score(y_test, y_test_pred, average="weighted")
            test_f1_score = f1_score(y_test, y_test_pred, average="weighted")
            test_roc_auc_score = roc_auc_score(y_test, y_test_proba, multi_class='ovr', average="weighted")
            
            report[list(models.keys())[i]] = {
                        'accuracy_score': test_accuracy_score,
                        'precision_score': test_precision_score,
                        'recall_score': test_recall_score,
                        'roc_auc_score': test_roc_auc_score,
                        'f1_score': test_f1_score
                    }
        return report
    except Exception as e:
        raise CustomException(e,sys)
    
def load_object(file_path):
    try:
        with open(file_path, "rb") as file_pbj:
            return dill.load(file_pbj)
        
    except Exception as e:
        raise CustomException(e, sys)