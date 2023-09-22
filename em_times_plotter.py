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
    print(filenames)
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
plt.plot(x, y_off,"--o", label="sound boost OFF")
plt.plot(x, y_on,"--o", label="sound boost ON")

plt.xlabel("Numero di veicoli")
plt.ylabel("Tempo di attesa medio nel traffico")
plt.title("Effetti del S.B sul TWT del V.E")

plt.legend(loc="upper left")
plt.savefig("./em_times_plot.png", dpi=500)
