import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import os

# Set style
sns.set_palette("husl")

# Create data
x = np.linspace(-4, 4, 1000)
y = 1/(np.sqrt(2*np.pi)) * np.exp(-x**2/2)

# Create plot
fig, ax = plt.subplots(figsize=(10, 6))

# Plot normal distribution
ax.plot(x, y, color='#00005e', lw=2, label='Distribución Normal\nEstándar')
ax.fill_between(x, y, alpha=0.3, color='#00005e')

# Add key areas annotations
areas = [
    (-1, 1, '68%', 0.25),
    (-2, 2, '95%', 0.15),
    (-3, 3, '99.7%', 0.05)
]

colors = ['#00005e', '#10f2f6', '#cfcfe1']
for (left, right, label, height), color in zip(areas, colors):
    ax.fill_between(x, y, where=(x >= left) & (x <= right), 
                    color=color, alpha=0.3)
    ax.annotate(f'{label} de los datos',
                xy=(0, height),
                ha='center',
                va='bottom',
                color='#00005e')

ax.set_title('La Distribución Normal 📊\n"La Campana que está en todas partes"', 
             fontsize=14, pad=20, color='#00005e')
ax.set_xlabel('Valores Estandarizados (Z-score)', fontsize=12, color='#00005e')
ax.set_ylabel('Densidad de Probabilidad', fontsize=12, color='#00005e')

# Add grid and legend
ax.grid(True, alpha=0.3)
ax.legend()

plt.tight_layout()
# plt.show()

# Create assets directory if it doesn't exist
if not os.path.exists('assets'):
    os.makedirs('assets')

# Save the plot
plt.savefig('assets/normal_distribution_a.png', dpi=300, bbox_inches='tight')
plt.close()