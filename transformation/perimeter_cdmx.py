import logging
import osmnx as ox
import pandas as pd
import numpy as np
from geopy.distance import geodesic
from shapely.geometry import Polygon


class PerimetroCdmx:
    def __init__(self):
            self.lng = None
            self.lat = None
            self.x_axis_divisions = None
            self.y_axis_divisions = None
            self.df_cdmx = None
            self.polygon_cdmx = None
    
    def load_perimeter(self):
        """
        Se geocodificar una ubicación (cdmx) con el fin de extraer las coordenadas que forma el poligono para
        calcular mediante la medida de 4 cuadras cuantas divisiones (cuadricula) se tiene que hacer en la CDMX,
        se encuentra las coordedas de dichas divisiones.
        """
        cdmx = ox.geocode_to_gdf("Ciudad de México, México")
        cdmx_coord = cdmx.geometry.iloc[0].exterior.coords
        self.polygon_cdmx = Polygon(cdmx_coord)
        self.df_cdmx = pd.DataFrame(data=cdmx_coord, columns=['longitud', 'latitud'])

        #divisiones para la cuadricula

        #distancias de las cuadras
        y_axis_distance_block = geodesic((19.40213,-99.14199), (19.39926,-99.14249)).meters
        x_axis_distance_block = geodesic((19.39926,-99.14249), (19.39901,-99.14077)).meters

        # coordenas del punto maximo, minimo en el eje x, y del perimetro de la cdmx
        point_x_min = tuple(self.df_cdmx.iloc[np.argmin(self.df_cdmx['longitud'])][['latitud', 'longitud']])
        point_x_max = tuple(self.df_cdmx.iloc[np.argmax(self.df_cdmx['longitud'])][['latitud','longitud']])
        point_y_min = tuple(self.df_cdmx.iloc[np.argmin(self.df_cdmx['latitud'])][['latitud','longitud']])
        point_y_max = tuple(self.df_cdmx.iloc[np.argmax(self.df_cdmx['latitud'])][['latitud','longitud']])

        # se pone en los mismos ejes para obtener la distancias
        point_x_min = (point_x_max[0],point_x_min[1])
        point_y_min = (point_y_min[0], point_y_max[1])

        # se obtiene la distancia utilizando la distancia de haversine, para saber cuantas casillas tendra el mapa
        x_axis_distance_perimeter = geodesic(tuple(point_x_max), tuple(point_x_min)).meters
        y_axis_distance_perimeter = geodesic(tuple(point_y_max), tuple(point_y_min)).meters

        #se calcula la cantidad de casillas que se va a tener en el eje xy
        self.x_axis_divisions = round( x_axis_distance_perimeter / x_axis_distance_block)
        self.y_axis_divisions = round( y_axis_distance_perimeter / y_axis_distance_block)

        # numero de divisiones
        logging.info(self.x_axis_divisions)
        logging.info(self.y_axis_divisions)

        # Crear los límites de las casillas
        self.lat = np.linspace(point_y_min[0], point_y_max[0], self.y_axis_divisions+1)
        self.lng = np.linspace(point_x_min[1], point_x_max[1], self.x_axis_divisions+1)
