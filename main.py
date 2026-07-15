import pandas as pd # manipulacion de datos
import matplotlib
matplotlib.use('Agg')
from matplotlib.backends.backend_pdf import PdfPages # guarda graficos en un pdf
import logging
from dotenv import dotenv_values # lectura de archivo .env

from cleaning.data_clean import DataCleaner #importar clase de limpieza de datos
from transformation.transformer import DataTransformer #importar clase de transformacion de datos    
from transformation.pdf_pages import PdfPagesGraficos #importar clase de graficos en pdf
from transformation.alert_level import AlertLevel #importar clase de nivel de alerta
from training_model.training import TrainingModels


if __name__ == "__main__":
    
    env_vars = dotenv_values(".env")
    
    if env_vars["RUN_DATA_CLEANING"] == "True":
        data_path = env_vars['DATA_PATH']
        df = pd.read_csv(data_path) 
    
        logging.info("archivo cargados correctamente")
        data_cleaner = DataCleaner(df) 
        data_cleaner.remove_duplicates_by_id() 
        data_cleaner.remove_nan_rows(['location_x', 'location_y'])
        data_cleaner.remove_columns(
            ['type', 
            'subtype', 
            'alcaldia', 
            'calle', 
            'fecha',
            'Longitud_normalizada',
            'Latitud_normalizada',
            'casilla',
            'cant_alerts'])
        
        data_cleaner.sample_data(100000)
        logging.info("Datos muestreados correctamente.")

        cleaned_data = data_cleaner.get_cleaned_data()
    else:
        print("ingreso")
        data_path = env_vars['CLEAN_DATA_PATH']
        cleaned_data = pd.read_csv(data_path) 


    logging.info("Datos limpios correctamente. Número de registros después de la limpieza:", len(cleaned_data))
    
    data_transformer = DataTransformer(cleaned_data)
    transformed_data = data_transformer.transform() #transformar datos
    
    logging.info("Datos transformados correctamente. Número de registros después de la transformación:", len(transformed_data))

    name_visualization_pdf = env_vars['DATA_VISUALIZATION_PDF'] #nombre del archivo pdf de graficos

    pdfPagesGraficos = PdfPagesGraficos(name_visualization_pdf, transformed_data, data_transformer.get_perim_cdmx()) #crear instancia de la clase PdfPagesGraficos
    
    alerts_statistics, transformed_data = pdfPagesGraficos.create_graphics() #generar graficos y obtener datos a analizar y datos de cdmx
    
    mean_alerts = round(alerts_statistics['cant_alertas'].mean())
    std_alerts = round(alerts_statistics['cant_alertas'].std())

    logging.info("Gráficos generados correctamente y guardados en el archivo PDF:", name_visualization_pdf)

    alert_level = AlertLevel(transformed_data) #crear instancia de la clase NivelAlerta
    data_cdmx = alert_level.classify_alert(mean_alerts, std_alerts)

    name_final_df = env_vars['CLEAN_DATA_NAME'] #nombre del archivo csv final
    data_cdmx.to_csv(name_final_df, index=False) #guardar datos finales en

    logging.info('termino el analisis de datos')
    
    TrainingModels(data_cdmx).train()

    logging.info('modelo listo para utilizarse')

