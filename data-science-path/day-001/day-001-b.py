import numpy as np
import matplotlib.pyplot as plt

x = np.linspace(-4, 4, 1000)
y = 1/(np.sqrt(2*np.pi)) * np.exp(-x**2/2)

plt.plot(x, y)
plt.title('Distribución Normal')
plt.savefig('assets/normal_distribution_b.png', dpi=300, bbox_inches='tight')
plt.close()
plt.show()