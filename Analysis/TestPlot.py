'''
Created on Oct 26, 2015

@author: Angus
'''



import numpy as np
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt

x = 10 ** np.arange(1, 10)
y = 10 ** np.arange(1, 10)

data = pd.DataFrame(data={'x': x, 'y': y})

#f, ax = plt.subplots(figsize=(7, 7))
# ax.set(yscale="log")
sns.violinplot(data).set(yscale="log")

plt.show()