import matplotlib.pyplot as plt
import math as m
import statistics as s
gran = 175

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
    for i in range(1, len(data)):
        chunk.append(data[i])
        if i % gran == 0:
            blocks.append(chunk[:])
            chunk = []
    y = [s.mean(c) for c in blocks]
    x = [i for i in range(len(y))]

    x_points = [i for i in range(len(data))]
    plt.title("Funzione di reward nel tempo, bidderV1")
    plt.xlabel("Gruppi da " + str(180) + " chiamate di funzione")
    plt.ylabel("Reward")
    plt.plot(x, y, '--bo')
    plt.savefig(name, dpi=300)
