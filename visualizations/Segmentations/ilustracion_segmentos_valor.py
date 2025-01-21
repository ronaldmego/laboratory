import matplotlib.pyplot as plt
import numpy as np

# Datos simulados
bajo = [80, 20, 10]  # Prepago, Postpago, Corporativo
medio = [15, 50, 30]
alto = [5, 30, 60]

labels = ['Prepago', 'Postpago', 'Corporativo']
x = np.arange(len(labels))
width = 0.25

fig, ax = plt.subplots(figsize=(12,6))
rects1 = ax.bar(x - width, bajo, width, label='Bajo', color='#FFF2CC')
rects2 = ax.bar(x, medio, width, label='Medio', color='#FFD966')
rects3 = ax.bar(x + width, alto, width, label='Alto', color='#4472C4')

ax.set_ylabel('Porcentaje de clientes')
ax.set_title('Segmentación por valor en líneas de negocio')
ax.set_xticks(x)
ax.set_xticklabels(labels)
ax.legend()

plt.tight_layout()
plt.show()