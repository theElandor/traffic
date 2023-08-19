import matplotlib.pyplot as plt
import os

directory = './em_data'
x = []
y_on = []
y_off = []
for dirpath, dirnames, filenames in os.walk(directory):
    try:
        x.append(int(dirpath.replace('./em_data/', '')))
    except ValueError:
        pass
    for filename in filenames:
        if filename.endswith('.txt'):
            with open(os.path.join(dirpath, filename)) as f:
                lines = f.readlines()
                for line in lines:
                    if line[:2] == "75":
                        data = line.split(",")
                        mean = data[2]                        
                        if filename == "on.txt":
                            y_on.append(float(mean))
                        else:
                            y_off.append(float(mean))
x.sort()
y_on.sort()
y_off.sort()
plt.plot(x, y_off,"--ro", label="sound boost OFF")
plt.plot(x, y_on,"--bo", label="sound boost ON")
plt.legend(loc="upper left")
plt.savefig("./em_times_plot.png")
