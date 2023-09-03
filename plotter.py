import matplotlib.pyplot as plt
import math as m
import statistics as s
gran = 100

filename = "reward.txt"

name = "unk.png"
if filename == "loss.txt":
    name = "loss.png"
if filename == "reward.txt":
    name = "reward.png"
if filename == "cumulative_reward.txt":
    name = "cumul_reward.png"
with open(filename) as f:
    data = [float(s.strip()) for s in f.readlines()]
    blocks = []
    chunk = []
    y = []
    for i in range(1, int(len(data)/2)):
        chunk.append(data[i])
        if i % gran == 0:
            blocks.append(chunk[:])
            chunk = []
    y = [s.mean(c) for c in blocks]
    x = [i for i in range(len(y))]

    x_points = [i for i in range(int(len(data)/2))]
    plt.xlabel("Sets of 80 function calls")
    plt.ylabel(name)
    plt.plot(x, y, '--bo')
    plt.savefig(name, dpi=300)
