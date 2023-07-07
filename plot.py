import matplotlib.pyplot as plt
import numpy as np
import os

plt.figure(figsize = (19.2, 10.8))
for directory in os.listdir("overtime_data"): #for each simul
    x_points = [int(p) for p in np.linspace(1000,10000, 10)]
    y_points = []
    err = []
    subdir = os.path.join("overtime_data", directory) #for specific simulation
    with open(os.path.join(subdir, "name.txt"), "r") as name_file:
        desc = name_file.read()
    for filename in sorted(os.listdir(subdir)):
        if filename == "name.txt":
            continue
        file = os.path.join(subdir, filename)
        with open(file, "r") as f:
            raw = f.readlines()
            raw = [x.replace('\n', '').split(" ") for x in raw]
            fine_data = {}
            for x in raw:
                fine_data[x[0]] = x[1]
            print(fine_data)
            y_points.append(fine_data['mean'])
            err.append(fine_data['std'])
    y_points = [float(i) for i in y_points]
    err = [float(i) for i in err]
    x = np.array(x_points)
    y = np.array(y_points)
    e = np.array(err)
    plt.plot(x, y, label=desc, marker='^')
plt.legend(loc='lower right')
plt.savefig('plots/overtime_twt.png', dpi=300)

            
