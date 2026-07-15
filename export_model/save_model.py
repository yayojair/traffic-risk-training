class SaveModel:
    def __init__(self, modelo_final,label_encoder):
        self.modelo_final = modelo_final
        self.label_encoder = label_encoder

    def save_model(self):
        """Guarda el modelo final en un archivo pickle."""
        import joblib

        joblib.dump(self.modelo_final, "artifacts/modelo_final.pkl")
        joblib.dump(self.label_encoder, "artifacts/label_encoder.pkl")
        print(f"Modelo guardado en: modelo_final.pkl")
        print(f"Label encoder guardado en: label_encoder.pkl")