import traci
from src.utils import *

from src.vehiclesDict import VehiclesDict

class Listener(traci.StepListener):

    def __init__(self, step_limit, settings, spawn_rate, timestamps, spawn_points, routes, crossroads_names):
        # When listener is initialized, vehicles have yet been spawned, with one simulation step for each of them
        self.step_count = len(VehiclesDict.vd.keys())
        self.step_limit = step_limit
        self.simulation_status = True
        self.settings = settings
        self.spawn_rate = spawn_rate
        self.timestamps = timestamps
        self.spawn_points = spawn_points
        self.spawned_cars = spawn_rate
        self.routes = routes
        self.crossroads_names = crossroads_names

    # NOTE: step method wants argument 't'
    def step(self, t):
        """
        At each traci.simulationStep() invocation, this method is invoked to execute a 
        routine to check step limit, apply common operations (i.e. rerouting check 
        of vehicles) and specific operations for models (i.e. 'Hurry' changing in 
        'Emergent Behavior' model.
        """
        self.step_count += 1
        # if self.step_count in self.timestamps:
        #     # print("collect WT now\n")
        #     cross_total, traffic_total, df_waiting_times, crossroads_wt, traffic_wt, crossroad_vehicles, traffic_vehicles = collectWT(self.crossroads_names)
        #     with open("test/temp"+str(self.step_count), "w") as f:
        #         f.write(str(traffic_total))
            
        # if self.step_count in self.spawn_points[1::] and self.spawned_cars < self.settings['VS']: #spawn cars according to spawn_rate
        #     # print(self.spawned_cars)
        #     spawnCars(self.spawn_rate, self.settings, self.routes, offset=self.spawned_cars)
        #     self.spawned_cars += self.spawn_rate
        #     # print(self.spawned_cars)


        if self.step_limit != 0 and self.step_count >= self.step_limit:
            self.simulation_status = False
            return False

        for v in VehiclesDict.vd.values():
            # print("reroute\n")
            v.reroute()
            v.setLabel()

        # indicate that the step listener should stay active in the next step
        return True

    def getStep(self):
        return self.step_count

    def getSimulationStatus(self):
        return self.simulation_status

class AutonomousListener(Listener):
    def __init__(self, step_limit, settings):
        super().__init__(step_limit, settings)

    def step(self, t):
        super().step(t)

        for v in VehiclesDict.vd.values():
            v.action()

        return True
