import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
from matplotlib.backends.backend_pdf import PdfPages 
from graphics.graphics import Graphics
import logging

class EvaluationModels:
    def __init__(self, rf_cv_scores, xgb_cv_scores, logistic_cv_scores, sgd_cv_scores, knn_cv_scores):
        self.rf_cv_scores = rf_cv_scores
        self.xgb_cv_scores = xgb_cv_scores
        self.logistic_cv_scores = logistic_cv_scores
        self.sgd_cv_scores = sgd_cv_scores
        self.knn_cv_scores = knn_cv_scores


    def evaluate(self):
        """# Viusalizacion de Resultados"""

        results = {
            'Random Forest': self.rf_cv_scores.mean(),
            'XGBoost': self.xgb_cv_scores.mean(),
            'Regresión Logística': self.logistic_cv_scores.mean(),
            'SGD': self.sgd_cv_scores.mean(),
            'KNN': self.knn_cv_scores.mean()
        }

        

        results_df = pd.DataFrame(list(results.items()), columns=['Modelo', 'Puntuación Media'])

        with PdfPages('assets/2019_model_evaluation.pdf') as pdf:

            graficos = Graphics()
            graficos.evaluation_models(results_df, pdf)
        
        winning_model = results_df.loc[results_df['Puntuación Media'].idxmax(), 'Modelo']
        logging.info(f"🏆 El modelo ganador es: {winning_model}")
        return winning_model
    
        