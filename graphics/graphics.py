import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
from scipy.stats import norm

class Graphics:
    
    def scatter_plot(data, df_cdmx,lng, lat, pdf):

        """
        Grafica las coordenadas de los perimetros y de las alertas de la cdmx, se
        visualiza las divisiones (casillas)
        y guarda dicha grafica en un archivo pdf.
        """

        plt.figure(figsize=(20, 16))

        sns.scatterplot(x='longitud', y='latitud', data=data, color='blue',edgecolor='blue', s=2)

        #sns.scatterplot(x='longitud', y='latitud', data=df_cdmx, color='red', edgecolor='red', s=2)

        plt.xticks(lng)
        plt.yticks(lat)

        plt.grid(which='both', color='gray', linestyle='--', linewidth=0.5)

        plt.xlabel('Longitud')
        plt.ylabel('Latitud')

        plt.grid(True)
        pdf.savefig()
        plt.close()

    def histogram_curve(data, column, activate_frec, pdf):
        """
        Grafica el comportamiento de los datos de la variable columna mediante un histograma y muestra su curva de densidad
        para verificar si se tiene datos atipicos y guarda dicha grafica en un archivo pdf.
        """
        data_visualization = data[column]

        plt.figure(figsize=(10, 6))
        plt.hist(data_visualization, bins=20, color='skyblue', edgecolor='black', density=activate_frec) # Ajustar histograma para densidad

        average = data_visualization.mean()
        std = data_visualization.std()
        resume = data_visualization.describe()

        xmin, xmax = plt.xlim()

        x = np.linspace(xmin, xmax, 100)

        probability = norm.pdf(x, average, std)

        plt.plot(x, probability, 'k', linewidth=2)

        plt.axvline(data_visualization.quantile(0.25), color='orange', linestyle='dashed', linewidth=1.5)
        plt.axvline(data_visualization.quantile(0.75), color='orange', linestyle='dashed', linewidth=1.5)
        plt.axvline(data_visualization.quantile(0.50), color='pink', linestyle='dashed', linewidth=1.5)
        plt.axvline(average, color='black', linestyle='dashed', linewidth=1.5)

        plt.xlabel(column)
        if activate_frec == True:
            y_name = 'Densidad'
        else:
            y_name = 'Frecuencia'
        plt.ylabel(y_name)
        plt.title('Histograma y Curva de ' + y_name +' de '+ column)

        resume = f'Resumen: \n{resume}'
        plt.text(0.95, 0.95, resume,
                horizontalalignment='right', verticalalignment='top',
                transform=plt.gca().transAxes, fontsize=10)
        
        plt.grid(True)
        pdf.savefig()
        plt.close()

    def box_plot(data, column, pdf):
        """
        Grafica el comportamiento de los datos mediantes sus cuartiles, mostrando los datos atipicos
        que se presentan y guarda dicha grafica en un archivo pdf.
        """
        plt.figure(figsize=(10, 6))
        sns.boxplot(y=column, data=data)
        plt.ylabel(column)
        plt.title(f'Diagrama de Caja y Bigotes de {column}')
        pdf.savefig()
        plt.close()

    def evaluation_models(self, results_df, pdf):
        """
        Grafica la comparacion de los modelos entrenados y guarda dicha grafica en un archivo pdf.
        """

        plt.figure(figsize=(10, 6))

        sns.barplot(x='Modelo', y='Puntuación Media', data=results_df, hue='Modelo', palette='viridis', dodge=False, legend=False)

        plt.title('Comparación de Puntuaciones Medias de Validación Cruzada', fontsize=16)
        plt.xlabel('Modelos', fontsize=12)
        plt.ylabel('Puntuación Media de Validación Cruzada', fontsize=12)

        pdf.savefig()
        plt.close()