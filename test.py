import os
def collectOvertimeData(simulation_index):
    for filename in os.listdir("test"):
        file = os.path.join("test", filename)
        with open(file, "r") as f:        
            raw = [x.replace('\n','').split(' ') for x in f.readlines()]
            for el in raw:
                while '' in el:
                    el.remove('')
            raw.pop()
            fine_data ={}
            for element in raw:
                fine_data[element[0]] = float(element[1])
                
        if not os.path.isdir("overtime_data/simul_"+simulation_index):
            os.makedirs("overtime_data/simul_"+simulation_index)        
        with open("overtime_data/"+"simul_"+simulation_index+"/"+filename+".txt", "w") as f:
            f.write("mean " + str(fine_data["mean"]) + "\n")
            f.write("std " + str(fine_data["std"]) + "\n")
