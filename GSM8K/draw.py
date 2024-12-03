import matplotlib.pyplot as plt
import numpy as np

x = np.arange(10)
x_labels = ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'j', 'k']
y = np.arange(0, 20, 2)
plt.plot(x, y)
plt.xticks(x, x_labels)

plt.show()