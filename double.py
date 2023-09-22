import matplotlib.pyplot as plt
import os

directory = './em_data'
x = []
y_74_both = []
y_75_both = []

#only veic 74 has sound boost activated
y_74_74 = []
y_75_74 = []

y_74_75 = []
y_75_75 = []

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
                    data = line.split(",")
                    mean = data[2]
                    if filename == "both.txt":
                        if line[:2] == "75":
                            y_75_both.append(float(mean))
                        if line[:2] == "74":
                            y_74_both.append(float(mean))
                    if filename == "74.txt":
                        if line[:2] == "75":
                            y_75_74.append(float(mean))
                        if line[:2] == "74":
                            y_74_74.append(float(mean))
                    if filename == "75.txt":
                        if line[:2] == "75":
                            y_75_75.append(float(mean))
                        if line[:2] == "74":
                            y_74_75.append(float(mean))
x.sort()
y_74_both.sort()
y_75_both.sort()

y_74_74.sort()
y_75_74.sort()

y_74_75.sort()
y_75_75.sort()

plt.plot(x, y_74_both, "--o", label="veic 74 both",color="darkred")
plt.plot(x, y_75_both, "--o", label="veic 75 both",color="red")

plt.plot(x, y_74_74, "--o", label="veic 74 74",color="mediumpurple")
plt.plot(x, y_75_74, "--o", label="veic 75 74",color="rebeccapurple")

plt.plot(x, y_74_75, "--o", label="veic 74 74",color="olivedrab")
plt.plot(x, y_75_75, "--o", label="veic 75 74",color="yellowgreen")

plt.xlabel("Numero di veicoli")
plt.ylabel("Tempo di attesa medio nel traffico")
plt.title("Effetti del S.B sul TWT del V.E")

plt.legend(loc="upper left")
plt.savefig("./em_times_plot.png", dpi=500)
