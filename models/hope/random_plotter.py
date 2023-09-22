import pandas as pd
import numpy as np
import matplotlib.pyplot as plt


width = 0.5
data_120 = pd.read_csv("average_120B/random_gained_data.txt")
data_130 = pd.read_csv("average_130B/random_gained_data.txt")
data_140 = pd.read_csv("average_140B/random_gained_data.txt")
print(data_120)

veics = ("120", "130", "140")
means = {
    'BidderV1': (round(data_120.iloc[0, 0], 2), round(data_130.iloc[0, 0], 2), round(data_140.iloc[0, 0],2)),
    'Random': (round(data_120.iloc[1, 0],2), round(data_130.iloc[1, 0],2), round(data_140.iloc[1, 0],2)),
}
errors = {
    'BidderV1': (round(data_120.iloc[0, 1],2), round(data_130.iloc[0, 1],2), round(data_140.iloc[0, 1], 2)),
    'Random': (round(data_120.iloc[1, 1],2), round(data_130.iloc[1, 1],2), round(data_140.iloc[1, 1],2)),
}
colors = {
    'BidderV1': "yellowgreen",
    'Random': "greenyellow"
}
x = np.arange(len(veics))  # the label locations
width = 0.25  # the width of the bars
multiplier = 0

fig, ax = plt.subplots(layout='constrained')

for attribute, measurement in means.items():
    offset = width * multiplier
    rects = ax.bar(x + offset, measurement, width, label=attribute, color=colors[attribute], yerr=errors[attribute])
    ax.bar_label(rects, fmt='{:,.2f}%',padding=3)
    multiplier += 1

# Add some text for labels, title and custom x-axis tick labels, etc.
ax.set_ylabel('Valuta media risparmiata')
ax.set_xlabel('Numero di veicoli')
ax.set_title('Valuta risparmiata, bidderV1 e Random')
ax.set_xticks(x + width, veics)
ax.legend(loc='upper left', ncols=3)
ax.set_ylim(0, 100)

plt.savefig("output.png")
