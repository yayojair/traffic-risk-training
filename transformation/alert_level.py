class AlertLevel:
    def __init__(self, data):
        self.data = data

    def classify_alert(self, average, std):
        """
        La función se encarga de clasificar los datos de datos_cdmx en niveles de alertas.
        """
        if average == std:
            std = std - 1
        
        alto = average + std + 2

        mod_alta = average + 1
                
        mod_baja = abs(average - std) + 1
                
        self.data['nivel_alertas'] = self.data['cant_alertas'].apply(
            lambda x: 'alto' if x > alto else
                    'modo_alta' if (x > mod_alta) & (x <= alto) else
                    'modo_bajo' if (x > mod_baja) & (x <= mod_alta) else
                    'bajo' if (x > 1) & (x <= mod_baja) else
                    'nulo'
        )
        
        return self.data