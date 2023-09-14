import matplotlib.pyplot as plt
import os
import pandas as pd
import numpy as np


x = []
final_data = {}
final_data['mean_off'] = []
final_data['std_off']  = []
final_data['mean_booster'] = []
final_data['std_booster']  = []
# final_data['mean_on']  = []
# final_data['std_on']   = []
# final_data['mean_simple'] = []
# final_data['std_simple'] = []


evaluate = "crossroad"
directory = "./qlearn_data/"
for root, dirs, filenames in os.walk(directory):
    for dirname in sorted(dirs, key=int):
        x.append(dirname)
        for file in os.listdir(os.path.join(directory, dirname)):
            if file != "saved_74.txt":
                data = pd.read_csv(os.path.join(directory, dirname, file))
                veic = data.iloc[74, 0]
                mean = data.iloc[74, 2]
                std  = data.iloc[74, 3]
                if file == evaluate + "_off.txt":
                    final_data['mean_off'].append(mean)
                    final_data['std_off'].append(std)
                if file == evaluate + "_booster.txt":
                    final_data['mean_booster'].append(mean)
                    final_data['std_booster'].append(std)
points = np.arange(len(x))
width = 0.1
multiplier = 0
# colors = ['orangered','coral', 'forestgreen','limegreen','dodgerblue','deepskyblue']
colors = ['orangered','coral', 'darkorchid','mediumorchid']
i = 0
fig, ax = plt.subplots(layout = 'constrained')
improv = []
for j in range(len(final_data['mean_booster'])):
    # if final_data['mean_booster'][j] < final_data['mean_off'][j]:
    improv.append(str((1-(final_data['mean_booster'][j]/final_data['mean_off'][j]))*100)[:4]+"%")
print(improv)
for attribute, measurment in final_data.items():
    offset = width * multiplier
    rects = ax.bar(points+offset, measurment, width, label=attribute, color=colors[i])
    multiplier += 1
    if i == 1:
        multiplier += 1
    if i == 2:
        ax.bar_label(container=rects, labels=improv, padding=45)   
    i += 1
ax.set_ylabel("Valore")
ax.set_xlabel("Numero di veicoli")
ax.set_title('Media e deviazione standard del tempo di attesa nel traffico')
ax.set_xticks(points + width, x)
ax.set_ylim(0, 60)
ax.legend(loc="upper left", ncols=2)
plt.savefig("./barplot.png", dpi=300)
print(final_data)
