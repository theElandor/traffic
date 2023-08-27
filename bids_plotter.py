import matplotlib.pyplot as plt
import os
import pandas as pd
import numpy as np

x = []
x_flow = []
values = {}
data = pd.read_csv("./bids.txt")
for i in range(len(data)):
    crossroad = data.iloc[i, 0]
    value = data.iloc[i, 1]
    if crossroad not in x:
        x.append(crossroad)
        values[crossroad] = value
    else:
        values[crossroad] += value
y = []
x.sort()
for c in x:
    y.append(values[c])

fig, ax = plt.subplots()
bar_container = ax.bar(x, y)
ax.set(ylabel='Vehicles', title='Traffico incontrato dal veicolo di testing', ylim=(0, 500))
ax.bar_label(bar_container, fmt='{:,.0f}')
plt.savefig("bid_plot.png")
