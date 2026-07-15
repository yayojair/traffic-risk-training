import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.preprocessing import LabelEncoder, StandardScaler
from sklearn.metrics import accuracy_score, make_scorer
from sklearn.pipeline import make_pipeline

from sklearn.neighbors import KNeighborsClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import SGDClassifier
import xgboost as xgb

from evaluation.model_evaluation import EvaluationModels
from export_model.save_model import SaveModel
from datetime import datetime
import json
import logging

class TrainingModels:
    def __init__(self, data):
        self.data = data
        self.metadata = {}
    
    def train_model(self, name, model, X, y, scorer):
        rf_cv_scores = cross_val_score(model, X, y, cv=10, scoring=scorer)

        logging.info(f"Puntuaciones {name}: {rf_cv_scores}")
        logging.info(f"Promedio de la Validacion Cruzada {name}: {rf_cv_scores.mean()}\n")

        date_now = datetime.now()
        self.metadata[name] = {
            "mean_cv_score": float(rf_cv_scores.mean()),
            "std_cv_score": float(rf_cv_scores.std()),
            "min_cv_score": float(rf_cv_scores.min()),
            "max_cv_score": float(rf_cv_scores.max()),
            'timestamp': date_now.strftime("%Y-%m-%d %H:%M:%S")
        }

        return rf_cv_scores
    

    def fit_best_model(self, model, name):
        # Definir características (X) y variable objetivo (y)
        X = self.data[['longitud', 'latitud']]
        y = self.data['nivel_alertas']
        model.fit(X,y)
        self.metadata['metadata'] = {
            "algorithm": name,
            "version": "1.0.0",
            "trained_at": datetime.now().isoformat(),
            "dataset_size": len(self.data),
            "features": ["longitud", "latitud"],
            "target": "nivel_alertas",
            "cv_folds": 10,
            "metric": "accuracy",
            "mean_cv_score": self.metadata[name]["mean_cv_score"],
            "std_cv_score": self.metadata[name]["std_cv_score"]
        }
        # Guardar el diccionario en un archivo JSON
        with open("artifacts/MetadataBuilder.json", "w") as archivo:
            json.dump(self.metadata, archivo, indent=4)
        return model

    def train(self):
        
        le = LabelEncoder()
        self.data['nivel_alertas'] = le.fit_transform(self.data['nivel_alertas'])

        X = self.data[['longitud', 'latitud']]
        y = self.data['nivel_alertas']

        #Create models
        model_random_forest = RandomForestClassifier(n_estimators=100, random_state=42)
        model_knn_pipeline = make_pipeline(StandardScaler(), KNeighborsClassifier(n_neighbors=5))
        model_logistic_pipeline = make_pipeline(StandardScaler(), LogisticRegression(max_iter=1000))
        model_sgd_pipeline = make_pipeline(StandardScaler(), SGDClassifier(loss='hinge', random_state=42))
        model_xgb = xgb.XGBClassifier(n_estimators=100, random_state=42, eval_metric='mlogloss')

        # Nota: Si usas cross_val_score con cv=10, evalúas directamente sobre X e y genéricos.
        # Quitamos train_test_split a menos que quieras dejar un conjunto de "test" oculto final.
        scorer = make_scorer(accuracy_score)

        
        rf_cv_scores = self.train_model("RandomForest",model_random_forest,X, y, scorer)
        xgb_cv_scores  = self.train_model("KNN", model_knn_pipeline, X, y, scorer)
        logistic_cv_scores = self.train_model("LogisticRegression", model_logistic_pipeline, X, y, scorer)
        sgd_cv_scores = self.train_model("SGD", model_sgd_pipeline, X, y, scorer)
        knn_cv_scores = self.train_model("XGBoost", model_xgb,X, y, scorer)

        evaluacion_modelos = EvaluationModels(rf_cv_scores, xgb_cv_scores, logistic_cv_scores, sgd_cv_scores, knn_cv_scores)
        winning_model = evaluacion_modelos.evaluate()

        models = {
            "Random Forest": RandomForestClassifier(n_estimators=100, random_state=42),
            "XGBoost": xgb.XGBClassifier(n_estimators=100, random_state=42, eval_metric='mlogloss'),
            "Logistic Regression": make_pipeline(StandardScaler(), LogisticRegression(max_iter=1000)),
            "SGD": make_pipeline(StandardScaler(), SGDClassifier(loss='hinge', random_state=42)),
            "KNN": make_pipeline(StandardScaler(), KNeighborsClassifier(n_neighbors=5))
        }

        final_model = models[winning_model]
        
        final_model = self.fit_best_model(final_model, winning_model)

        SaveModel(final_model, le).save_model()
