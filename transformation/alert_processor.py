from multiprocessing import Pool , cpu_count #concurrente
import numpy as np
from shapely.geometry import Point , Polygon #clases de Shapely que permiten

class AlertProcessor:

    def add_points(self, partitions, x_axis_divisions, lng, lat):
        """
        Se agrega un punto al centro da cada cuadricula donde cada proceso 
        empezara desde una fila en particular.
        """
        start = partitions[0]
        stop = np.max(partitions) + 1
        coordinate_store = []
        
        for y in range(start, stop):  # itera por el eje y
            for x in range(x_axis_divisions): # itera por el eje x
                lng_new = (lng[x] + lng[x+1]) / 2
                lat_new = (lat[y] + lat[y+1]) / 2
                coordinate_store.append(Point(lng_new, lat_new))
                
        return coordinate_store
    
    def get_box_data(self, x, y, x_axis_divisions, y_axis_divisions, lat, lng, data):
        lat_min = data['latitud'] >= lat[y]
        lat_max_closed = data['latitud'] <= lat[y+1]
        lat_max_open = data['latitud'] < lat[y+1]

        lng_min = data['longitud'] >= lng[x]
        lng_max_closed = data['longitud'] <= lng[x+1]
        lng_max_open = data['longitud'] < lng[x+1]

        if (x+1 == x_axis_divisions) & (y+1 == y_axis_divisions):
            df_aux = data[(lat_min) & (lat_max_closed) & (lng_min) & (lng_max_closed)]
            
        elif y+1 == y_axis_divisions:
            df_aux = data[(lat_min) & (lat_max_closed) & (lng_min) & (lng_max_open)]
            
        elif x+1 == x_axis_divisions:
            df_aux = data[(lat_min) & (lat_max_open) & (lng_min) & (lng_max_closed)]
            
        else:
            df_aux = data[(lat_min) & (lat_max_open) & (lng_min) & (lng_max_open)]

        return df_aux

    def count_alerts(self, partitions, x_axis_divisions, y_axis_divisions, lng, lat, data):
        """
        Cada proceso recorre sus respectivas filas para asignar un numero de casilla y
        contar cuantas alertas hay en cada casilla:
        """
        start = partitions[0]
        stop = np.max(partitions) + 1
        boxes = (start * x_axis_divisions) + 1
        data_boxes = []
        data_analyze = []
        
        for y in range(start, stop):  # itera por el eje y
            for x in range(x_axis_divisions): # itera por el eje x
                
                df_aux = self.get_box_data(x, y, x_axis_divisions, y_axis_divisions, lat, lng, data)
                alerts = df_aux.shape[0]
                
                if alerts > 0:
                    data_boxes.append([df_aux.index, boxes, alerts])
                if alerts > 1:
                    data_analyze.append([boxes, (alerts - 1)])
                    
                boxes += 1
                
        return data_boxes, data_analyze

    
    def partitions(self, y_axis_divisions):
        # agregar puntos a todo el mapa repartiendo la tarea a procesos
        process_number = min(y_axis_divisions, cpu_count())
        process_values = [valor for valor in range(y_axis_divisions)]
        
        # divide las filas que le toca a cada proceso
        partitions_values = np.array_split(process_values, process_number)

        return process_number, partitions_values

    def distribute_add_points(self, x_axis_divisions, y_axis_divisions, lng, lat):
        process_number, partitions_values = self.partitions(y_axis_divisions)

        with Pool(processes=process_number) as pool:
            args = [(partitions, x_axis_divisions, lng, lat) for partitions in partitions_values]
            # Cada proceso recibe una partición distinta del mapa para procesarla de forma independiente.
            data_processes = pool.starmap(self.add_points, args)
        
        return data_processes

    def distribute_count_alerts(self, x_axis_divisions, y_axis_divisions, lng, lat, data):
        process_number, partitions_values = self.partitions(y_axis_divisions)
        with Pool(processes=process_number) as pool:
            args = [(partitions, x_axis_divisions, y_axis_divisions, lng, lat, data) for partitions in partitions_values]
            data_processes = pool.starmap(self.count_alerts, args)
            
        return data_processes