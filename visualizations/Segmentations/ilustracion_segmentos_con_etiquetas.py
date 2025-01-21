import seaborn as sns
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from sklearn.cluster import KMeans

# Generar datos simulados (mantenemos los mismos datos)
n = 1000
np.random.seed(42)
data = pd.DataFrame({
    'Datos': np.random.exponential(scale=50, size=n),
    'Voz': np.random.exponential(scale=30, size=n),
    'ARPU': np.random.lognormal(mean=3, sigma=1, size=n),
    'Antigüedad': np.random.gamma(shape=2, scale=10, size=n),
    'Tecnología': np.random.choice(['3G', '4G', '5G'], size=n, p=[0.2, 0.5, 0.3])
})

# Aplicar K-means para identificar clusters
kmeans = KMeans(n_clusters=5, random_state=42)
data['Cluster'] = kmeans.fit_predict(data[['Datos', 'Voz', 'ARPU']])

# Crear el gráfico
plt.figure(figsize=(16,12))
scatter = sns.scatterplot(x='Datos', y='Voz', hue='Cluster', style='Tecnología', 
                          size='ARPU', sizes=(20, 500), alpha=0.7, 
                          palette='viridis', data=data)

plt.title('Segmentación de clientes por uso de datos y voz', fontsize=18)
plt.xlabel('Uso de datos', fontsize=14)
plt.ylabel('Uso de voz', fontsize=14)

# Ajustar los límites de los ejes
plt.xlim(0, 250)
plt.ylim(0, 220)

# Añadir más etiquetas para segmentos específicos
segmentos = [
    {'x': 10, 'y': 80, 'label': 'Alto voz, bajo datos (4G)\n- Preferencia por llamadas\n- Potencial de migración a datos\n- Equipo compatible con 4G'},
    {'x': 80, 'y': 10, 'label': 'Alto datos, bajo voz\n- Uso intensivo de aplicaciones\n- Comunicación principalmente por chat\n- Potencial para servicios de streaming'},
    {'x': 80, 'y': 80, 'label': 'Alto valor\n- Uso equilibrado de voz y datos\n- ARPU elevado\n- Antigüedad significativa\n- Tecnología avanzada'},
    {'x': 10, 'y': 10, 'label': 'Bajo consumo\n- Uso mínimo de servicios\n- ARPU bajo\n- Potencial de crecimiento\n- Posible usuario de prepago'},
    {'x': 40, 'y': 40, 'label': 'Consumo medio\n- Uso moderado de voz y datos\n- ARPU medio\n- Oportunidad de upselling\n- Mix de tecnologías'},
    {'x': 150, 'y': 30, 'label': 'Alto datos, tecnología avanzada\n- Uso intensivo de datos\n- Equipos 4G/5G\n- Potencial para servicios premium\n- Posible early adopter'},
    {'x': 30, 'y': 150, 'label': 'Alto voz, tecnología básica\n- Uso intensivo de llamadas\n- Equipo posiblemente 3G\n- Oportunidad de upgrade tecnológico\n- Posible cliente de larga data'}
]

for seg in segmentos:
    plt.annotate(seg['label'], xy=(seg['x'], seg['y']), xytext=(5,5), 
                 textcoords='offset points', ha='left', va='bottom',
                 bbox=dict(boxstyle='round,pad=0.5', fc='yellow', alpha=0.5),
                 arrowprops=dict(arrowstyle = '->', connectionstyle='arc3,rad=0'))

plt.legend(title='Clusters', bbox_to_anchor=(1.05, 1), loc='upper left')
plt.tight_layout()
plt.show()