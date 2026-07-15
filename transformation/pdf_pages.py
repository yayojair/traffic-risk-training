import matplotlib
matplotlib.use('Agg')
from matplotlib.backends.backend_pdf import PdfPages
import pandas as pd
import logging

from graphics.graphics import Graphics 
from cleaning.data_clean import DataCleaner 
from transformation.transformer import DataTransformer
from transformation.alert_processor import AlertProcessor

class PdfPagesGraficos:
    def __init__(self, name_pdf, df, perim_cdmx):
        self.name_pdf = name_pdf
        self.df = df
        self.perim_cdmx = perim_cdmx

    def create_graphics(self):
        data_cleaner = DataCleaner(self.df)
        alert_modifier = AlertProcessor()
        x_axis_divisions = self.perim_cdmx.x_axis_divisions
        y_axis_divisions = self.perim_cdmx.y_axis_divisions
        lng = self.perim_cdmx.lng
        lat = self.perim_cdmx.lat
        df_cdmx = self.perim_cdmx.df_cdmx
       

        with PdfPages(self.name_pdf) as pdf:
            Graphics.scatter_plot(self.df, 
                                  df_cdmx, 
                                  lng, 
                                  lat, 
                                  pdf)
            
            # se crean dos columnas en el dataframe de los datos
            self.df['casilla'] = pd.NA
            self.df['cant_alertas'] = pd.NA

            logging.info("empezando multihilo para agregar las casillas y la cantidad de alertas a los datos")
            
            data_tuples = alert_modifier.distribute_count_alerts(x_axis_divisions, y_axis_divisions, lng, lat, self.df)
            
            # agregar las casillas y la cantidad de alerta a las alertas
            data_analyze = self.add_alert_data(data_tuples)


            # Data Frame de los datos a analizar
            data_analyze = pd.DataFrame(data=data_analyze, columns=['casilla', 'cant_alertas'])
            Graphics.box_plot(data_analyze, 'cant_alertas', pdf)
            Graphics.histogram_curve(data_analyze, 'cant_alertas', True, pdf)
                    
            data_analyze = self.outliers(data_analyze)

            # visualizar datos sin valores atipicos
            Graphics.box_plot(data_analyze, 'cant_alertas', pdf)
            Graphics.histogram_curve(data_analyze, 'cant_alertas', True, pdf)
        
        return data_analyze, self.df
    
    def add_alert_data(self, data_tuples):
        data_analyze = []
        for i in range(len(data_tuples)):
            data = data_tuples[i]
            data_analyze = data_analyze + data[1]
            for j in range(len(data[0])):
                alerts = data[0][j]
                index = alerts[0]
                self.df.loc[index, 'casilla'] = alerts[1]
                self.df.loc[index, 'cant_alertas'] = alerts[2]
        return data_analyze
    
    def outliers(self, data_analyze):
        outliers = True
        while(outliers):
            
            top_indexes, lower_indexes = self.remove_outliers(data_analyze, 'cant_alertas')
            
            if (len(top_indexes[0]) != 0):
                data_analyze = data_analyze.drop(index=top_indexes[0])
            else:
                outliers = False
                
            data_analyze = data_analyze.reset_index(drop=True)

        return data_analyze

    def remove_outliers(self, data, column):
        """The indices of the data frame that are considered atypical 
        are found using the interquartile range."""
        superior_outliers = []
        lower_outliers = []

        q1 = data[column].quantile(0.25)
        q3 = data[column].quantile(0.75)

        iqr = q3 - q1

        upper_limit = q3 + 1.5 * iqr
        lower_limit = q1 - 1.5 * iqr
        
        top_index = data[data[column] > upper_limit].index
        lower_index = data[data[column] < lower_limit].index

        superior_outliers.append(top_index)
        lower_outliers.append(lower_index)

        return superior_outliers, lower_outliers