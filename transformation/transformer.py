import pandas as pd
import numpy as np
from shapely.geometry import Point , Polygon #clases de Shapely que permiten
from transformation.perimeter_cdmx import PerimetroCdmx #importar clase de perimetro_cdmx
from transformation.alert_processor import AlertProcessor #importar clase de agregar_alertas_nulas

class DataTransformer:
    
    def __init__(self, data):
        self.data = data
        self.alert_modifier= AlertProcessor()
        self.perim_cdmx = PerimetroCdmx()
        self.perim_cdmx.load_perimeter()
        
        
    
    def create_missing_points(self, points):
        missing_points = [
            point
            for group in points
            for point in group
        ]
        return missing_points
    
    def create_alert_points(self):
        alerts_coordinates = self.data.apply(lambda x: Point(x['location_x'], x['location_y']), axis=1).tolist()
        return alerts_coordinates
    
    def filter_points_inside_polygon(self, alerts_coordinates):
        cdmx_coordinates = [(point.x, point.y) for point in alerts_coordinates if self.perim_cdmx.polygon_cdmx.contains(point)]
        return cdmx_coordinates
    
    def build_dataframe(self, cdmx_coordinates):
        return pd.DataFrame(data=cdmx_coordinates, columns=['longitud', 'latitud'])
    
    def transform(self):
  
        added_points = self.alert_modifier.distribute_add_points(
            self.perim_cdmx.x_axis_divisions, 
            self.perim_cdmx.y_axis_divisions, 
            self.perim_cdmx.lng, 
            self.perim_cdmx.lat
            )
        
        missing_points = self.create_missing_points(added_points)

        alerts_coordinates = self.create_alert_points()

        alerts_coordinates = missing_points + alerts_coordinates

        cdmx_coordinates  =self.filter_points_inside_polygon(alerts_coordinates)

        data_cdmx = self.build_dataframe(cdmx_coordinates)

        return data_cdmx
    
    def get_perim_cdmx(self):
        return self.perim_cdmx

    