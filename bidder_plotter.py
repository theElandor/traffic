import matplotlib.pyplot as plt
import os
import pandas as pd
import numpy as np


x = []
final_data = {}
final_data['mean_on']  = []
final_data['mean_off'] = []
final_data['std_on']   = []
final_data['std_off']  = []

directory = "./qlearn_data/"
for root, dirs, filenames in os.walk(directory):
    for dirname in sorted(dirs, key=int):
        x.append(dirname)
        for file in os.listdir(os.path.join(directory, dirname)):
            if file != "saved_74.txt":
                data = pd.read_csv(os.path.join(directory, dirname, file))                
                veic = data.iloc[74, 0]
                print(veic)
                mean = data.iloc[74, 2]
                std  = data.iloc[74, 3]
                if file == "traffic_on.txt":
                    final_data['mean_on'].append(mean)
                    final_data['std_on'].append(std)
                if file == "traffic_off.txt":
                    final_data['mean_off'].append(mean)
                    final_data['std_off'].append(std)
points = np.arange(len(x))
width = 0.1
multiplier = 0
fig, ax = plt.subplots(layout = 'constrained')
for attribute, measurment in final_data.items():
    offset = width * multiplier
    rects = ax.bar(points+offset, measurment, width, label=attribute)
    multiplier += 1
ax.set_ylabel("Value")
ax.set_xlabel("Number of vehicles")
ax.set_title('Mean and std traffic waiting time, with and without bidder')
ax.set_xticks(points + width, x)
ax.set_ylim(0, 60)
ax.legend(loc="upper left", ncols=2)
plt.savefig("./barplot.png", dpi=300)
print(final_data)
