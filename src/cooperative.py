from src.intersectionManager import *
import math
import numpy as np
from src.bidder import Agent
#print("Next edge for veic n. " + str(veic.getID()) + " is " + str(veic.getRoute()[index+1])


class Cooperative(IntersectionManager):

    def __init__(self, settings, extra_configs):
        super().__init__(settings)
        self.multiplier = extra_configs["multiplier"]
        self.congestion_rate = extra_configs["congestion_rate"]
        self.load = False
        self.train = True
        self.bidder = Agent(load=self.load, train=self.train)
        self.sample = 0
        self.train_count = 0
        self.mapping = {
            "A":0,
            "B":1,
            "C":2,
            "D":3,
            "E":4,
            "F":5,
            "G":6,
            "H":7,
            "I":8
        }
        #following parameters are needed to assing reward
        #and remember experience at the beginning of predict_bid
        #function
        self.prev_state = []
        self.prev_action = []
    
    def get_reward(self, prev_state, prev_action, current_state):
        """
        function that returns the value of the reward based on the current
        state of the environment and the prevoius state of the environment.
        state: [crossroad id, veic position]
        + crossroad id: numeric ID of the crossroad
        + veic position: veic position in lane (0: immediatly before crosser, -1 waiting to cross)

        reward:
        +1 if veic increased his lane position
        0 if veic did not increase lane position
        +3 if veic crossed the intersection (so new crossing is different from previous)
        0 if veic did not cross the intersection        
        """
        # TODO: need to add bid value to minimize overall money spent
        print(prev_state, prev_action, current_state)
        prev_crossroad = prev_state[0][0]
        prev_position = prev_state[0][1]
        current_crossroad = current_state[0][0]        
        current_position = current_state[0][1]
        crossroad_reward = 0

        discount = prev_action / 10 # [0, 0.1, 0.2, 0.3...1]
        position_reward = prev_position - current_position        
        if prev_crossroad != current_crossroad:
            crossroad_reward += 3
        if discount == 0: # fix to avoid zero division
            discount = 0.05
        final_reward = (position_reward + crossroad_reward)*(1/discount)
        return final_reward

    def predict_bid(self,current_state_input):
        if self.bidder.train:
            # print("TESTING VEIC PREDICTING WITH THIS INPUT:")
            # print(self.prev_state, current_state_input)
            if len(self.prev_state):
                reward = self.get_reward(self.prev_state, self.prev_action, current_state_input)                
                self.bidder.remember(self.prev_state, self.prev_action, reward, current_state_input)
                self.sample += 1
            if len(self.bidder.experience_replay) < self.bidder.batch_size:
                self.bidder.set_exploration_epsilon()
            else: #train when memory is full enough, one each 10 actions
                if self.sample > 10:
                    self.bidder.set_training_epsilon()
                    self.sample = 0
                    self.train_count += 1
                    print("Training(" + str(self.train_count)+"/5)")
                    self.bidder.retrain()
                    if self.train_count == 5:
                        print("UPDATING TARGET NETWORK")
                        self.train_count = 0
                        self.bidder.alighn_target_model()
        action = self.bidder.act(current_state_input)
        self.prev_state = current_state_input  # save current state to get reward in next iteration
        self.prev_action = action
        return action
    
    def bidSystem(self, crossroad_stop_list, traffic_stop_list, crossroad):
        # function that handles bidding, uses many utility function inherited by base class.
        # input: cars waiting at the head of the crossing, cars waiting in line 
        # output: ordered list of cars that have to depart from the crossroad
        # traffic_stop_list and crossroad_stop_list are related to the input crossroad.
        bids = []
        test_veic = "74"
        sponsors = {}
        # for now state only saves data related to test_veic           
        for v in VehiclesDict.vd.values(): #for each veichle
            if v.getID() == test_veic:  # only check test_veic
                road = traci.vehicle.getRoadID(v.getID())
                try:
                    position = traffic_stop_list[road].index(v)
                except ValueError:                    
                    position = -1
                current_state = [self.mapping[crossroad.name],position]
                current_state_input = np.array([current_state])
        # crossroad_stop_list --> lista di veicoli fermi all'incrocio, in testa alle linee
        for car in crossroad_stop_list:
            car_bid = int(car.makeBid() + 1)
            if car.getID() == test_veic:      
                bid_modifier = self.predict_bid(current_state_input)
                discount = (bid_modifier / 10)
                car_bid = car_bid * discount
                # print("test_veic bidded " + str(car_bid))
                print("Current state is: ")
                print(current_state)
                # print("OTHER WAITING VEICS ARE: ")                
                # road = traci.vehicle.getRoadID(car.getID())
                # for c in traffic_stop_list[road]:
                #     print(c)
                    
            sponsorship = 0

            # Collecting sponsorships
            if self.settings['Spn'] > 0:                
                for sp in traffic_stop_list[car.getRoadID()]:
                    
                    tip = sp.makeSponsor()
                    if sp.getID() == test_veic:
                        sponsor_modifier = self.predict_bid(current_state_input)
                        tip = tip * (sponsor_modifier / 10)
                        # print("OTHER WAITING VEICS ARE: ")
                        # road = traci.vehicle.getRoadID(car.getID())
                        print("Current state is: " + str(current_state))
                        # for c in traffic_stop_list[road]:
                        #     print(c)
                        # print("test veic tipped " + str(tip))
                    # print('bidSystem: vehicle {} receives a sponsorship of {} from vehicle {}'.format(car.getID(), tip, sp.getID()))
                    sponsorship += tip
                    sp.setBudget(sp.getBudget() - tip)
            car_bid += sponsorship
            sponsors[car] = sponsorship

            
            log_print('bidSystem: vehicle {} made a bid of {}'.format(car.getID(), car_bid))
            if self.settings['E'] == 'y': ## if enhancement is activated
                enhance = self.multiplier*math.log(len(traffic_stop_list[car.getRoadID()]) + 1) + 1 ## get num of cars in the same lane and apply formula.
                # current_route_position = car.getRouteIndex()
                # next_route_position = car.getRoute()[current_route_position+1]
                # cars_in_next_edge = len(traci.edge.getLastStepVehicleIDs(next_route_position))
            else:
                enhance = 1
            total_bid = int(car_bid * enhance)
            bids.append([car, total_bid, car_bid, enhance])
            
            log_print('bidSystem: vehicle {} has a total bid of {} (bid {}, enhancement {})'.format(car.getID(), total_bid, car_bid, enhance))

        bids, winner, winner_total_bid, winner_bid, winner_enhance = self.sortBids(bids)

        log_print('bidSystem: vehicle {} pays {}'.format(winner.getID(), winner_bid - 1))
        #if winner is test vehicle, do not decrease budget and do not redistribute winning bid
        #to other vehicles        
        winner.setBudget(winner.getBudget() - winner_bid + 1)
        sponsorship_winner = sponsors[winner]
        self.bidPayment(bids, winner_bid-sponsorship_winner)        
        departing = []
        for b in bids:
            departing.append(b[0]) ## appends departing cars in order and return them as a list.

        return departing