import matplotlib.pyplot as plt
import os 
import statistics as st
import pandas as pd
import numpy as np
directory = './em_data'
x = []
final_data = {}
final_data['avg_on'] = []
final_data['std_on'] = []
final_data['avg_off'] = []
final_data['std_off'] = []


# id,count,mean,std,min,25%,50%,75%,max

with open("./not_boosted_cars.txt") as b:
    lines = b.read().splitlines()
    veics = [i for i in lines]
    not_boosted = []
    boosted = True
    for root, dirs, filenames in os.walk(directory):
        for dirname in sorted(dirs, key=int):
            for j in range(int(dirname)):
                if str(j) not in veics:                    
                    not_boosted.append(str(j))
            x.append(int(dirname))
            mean_on = []
            mean_off = []
            std_on = []
            std_off = []            
            for file in os.listdir(os.path.join(directory, dirname)):                
                data=pd.read_csv(os.path.join(directory,dirname,file))                
                for i in range(len(data)):
                    veic = data.iloc[i,0]
                    mean = data.iloc[i,2]
                    std  = data.iloc[i,3]
                    if boosted:
                        used_list = veics
                    else:
                        used_list = not_boosted
                    if str(veic) in used_list:                        
                        if file == "on.txt":                            
                            mean_on.append(float(mean))
                            std_on.append(float(std))
                        else:                            
                            mean_off.append(float(mean))
                            std_off.append(float(std))
            mean_of_means_on = st.mean(mean_on)
            mean_of_stds_on = np.std(mean_on)
            mean_of_means_off = st.mean(mean_off)
            mean_of_stds_off = np.std(mean_off)
            final_data['avg_on'].append(mean_of_means_on)
            final_data['avg_off'].append(mean_of_means_off)
            final_data['std_on'].append(mean_of_stds_on)
            final_data['std_off'].append(mean_of_stds_off)
            mean_on.clear()
            mean_off.clear()
            std_on.clear()
            std_off.clear()
points = np.arange(len(x))  # the label locations
width = 0.3  # the width of the bars
multiplier = 0

fig, ax = plt.subplots(layout='constrained')
colors = ['mediumpurple', 'rebeccapurple']
i = 0
for attribute, measurement in final_data.items():
    if attribute == "std_on" or attribute == "std_off":
        continue
    else:
        if attribute == "mean_on":
            error = final_data["std_on"]
        else:
            error = final_data["std_off"]
    offset = width * multiplier
    rects = ax.bar(points + offset, measurement, width, label=attribute, color=colors[i], yerr=error, ecolor='black')
    multiplier += 1
    i+=1

# Add some text for labels, title and custom x-axis tick labels, etc.
ax.set_ylabel('Tempo di attesa nel traffico')
ax.set_xlabel('Numero di veicoli')
ax.set_title('Tempo di attesa dei veicoli NON "boosted" nel traffico')
ax.set_xticks(points + width, x)
ax.legend(loc='upper left', ncols=len(x))
ax.set_ylim(0, 120)
ax.legend(loc='upper left', ncols=2)

plt.savefig("./barplot.png", dpi=300)
