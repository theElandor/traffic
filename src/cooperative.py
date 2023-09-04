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
        
        self.load = True
        self.train = False
        self.boosted_cars = []
        self.not_boosted_cars = []
        self.test_veic = "?"
        self.em_veic = "75"
        self.sound_boost = False
        #huge budget is given to emergency vehicle        
        VehiclesDict.vd[self.em_veic].setBudget(1000000000)
        VehiclesDict.vd[self.em_veic].setMaxBudget(1000000000)
        
        self.cumulative_reward = 0
        self.bank = 0
        self.fair_bids = 0
        
        self.bidder = Agent(load=self.load, train=self.train)
        self.sample = 0
        self.train_count = 0
        self.mapping = {
            "A": 0,
            "B": 1,
            "C": 2,
            "D": 3,
            "E": 4,
            "F": 5,
            "G": 6,
            "H": 7,
            "I": 8
        }
        # following parameters are needed to assing reward
        # and remember experience at the beginning of predict_bid
        # function
        self.prev_state = []
        self.prev_action = []        

    def get_distance(self, veic):
        point1 = VehiclesDict.vd[self.em_veic].getPosition()
        point2 = veic.getPosition()        
        if len(point1) != 2 or len(point2) != 2:
            raise ValueError("Error when calculating vehicles distance")
        
        distance = math.sqrt((point1[0] - point2[0])**2 + (point1[1] - point2[1])**2)
        return distance
    
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

        discount = prev_action / 10  # [0, 0.1, 0.2, 0.3...1]
        position_reward = (prev_position - current_position)*4  # 2 if increased, 0 otherwise
        if prev_crossroad != current_crossroad:
            position_reward = 0  # if the veic changes crossroad, do not consider position
            crossroad_reward += 8  # give big reward if veic crosses crossroad
        if discount == 0:  # fix to avoid zero division
            discount = 0.05
        if discount == 1:  # fix to avoid log(1)
            discount = 0.99
        
        efficency_reward = math.log((1/discount))  # increase reward based on used money [0-3]
        
        if prev_crossroad == current_crossroad and prev_position == current_position:
            slow_penalty = -3
        else:
            slow_penalty = 0
        
        final_reward = (position_reward) + (crossroad_reward) + slow_penalty + efficency_reward
        self.cumulative_reward += final_reward
        print("reward: " + str(final_reward))
        with open("reward.txt", "a") as f:
            f.write(str(final_reward)+"\n")
        with open("cumulative_reward.txt", "a") as cf:
            cf.write(str(self.cumulative_reward)+"\n")
        return final_reward

    def predict_bid(self, current_state_input):
        if self.bidder.train:
            # print("TESTING VEIC PREDICTING WITH THIS INPUT:")
            # print(self.prev_state, current_state_input)
            if len(self.prev_state):
                reward = self.get_reward(self.prev_state, self.prev_action, current_state_input)                
                self.bidder.remember(self.prev_state, self.prev_action, reward, current_state_input)
                self.sample += 1
            if len(self.bidder.experience_replay) < self.bidder.batch_size:
                self.bidder.set_exploration_epsilon()
            else:  # train when memory is full enough, one each 10 actions
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
    
    def getSoundBoost(self, car):
        """
        Function that boosts a car's bid if it is on a em. veichle route.
        It is usefull to make the traffic flow in favour of emergency vehicles,
        reducing the time needed to empty the lanes that will be used by the em.veic.
        """
        em_veic = VehiclesDict.vd[self.em_veic]
        em_route_index = em_veic.getRouteIndex()
        em_route = em_veic.getRoute()
        
        car_current_road = traci.vehicle.getRoadID(car.getID())
        if car_current_road in em_route[(em_route_index+1)::]:
            if car.getID() not in self.boosted_cars:
                self.boosted_cars.append(car.getID())                
            distance = self.get_distance(car)
            boost = 1+math.exp((1/math.log10(math.sqrt(distance))))
            print("PBoost: E-"+str(car.getID()) + " = " + str(boost) + "\tdistance:"+str(distance))        
            return boost
        else:
            if car.getID() not in self.not_boosted_cars:
                self.not_boosted_cars.append(car.getID())
            return 1
    
    def bidSystem(self, crossroad_stop_list, traffic_stop_list, crossroad):
        # function that handles bidding, uses many utility function inherited by base class.
        # input: cars waiting at the head of the crossing, cars waiting in line 
        # output: ordered list of cars that have to depart from the crossroad
        # traffic_stop_list and crossroad_stop_list are related to the input crossroad.
        bids = []        
        sponsors = {}
        # for now state only saves data related to test_veic           
        for v in VehiclesDict.vd.values(): #for each veichle
            if v.getID() == self.test_veic:  # only check test_veic
                road = traci.vehicle.getRoadID(v.getID())
                try:
                    position = traffic_stop_list[road].index(v)
                except ValueError:
                    position = -1
                current_state = [self.mapping[crossroad.name], position]
                current_state_input = np.array([current_state])                  
        # crossroad_stop_list --> lista di veicoli fermi all'incrocio, in testa alle linee
        for car in crossroad_stop_list:
            car_bid = int(car.makeBid() + 1)
            if car.getID() == self.test_veic:
                bid_modifier = self.predict_bid(current_state_input)
                discount = (bid_modifier / 10)

                # need to be tracked only if test veic is winning veic, at the end of the function
                self.last_discounted_bid = car_bid * discount
                self.last_flat_bid = car_bid
                
                car_bid = car_bid * discount
                print("test_veic bidded " + str(car_bid))
                print("Current state is: ")
                print(current_state)  
                    
            sponsorship = 0
            
            # Collecting sponsorships
            if self.settings['Spn'] > 0:
                for sp in traffic_stop_list[car.getRoadID()]:
                    tip = sp.makeSponsor()
                    if sp.getID() == self.test_veic:
                        sponsor_modifier = self.predict_bid(current_state_input)
                        tip_discount = (sponsor_modifier / 10)
                        
                        self.fair_bids += tip
                        self.bank += tip - (tip*tip_discount)
                        
                        tip = tip * tip_discount
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
            if self.settings['E'] == 'y':
                enhance = self.multiplier*math.log(len(traffic_stop_list[car.getRoadID()]) + 1) + 1 ## get num of cars in the same lane and apply formula.
            else:
                enhance = 1            
            if self.sound_boost: 
                boost = self.getSoundBoost(car)
            else:
                boost = 1                
                
            total_bid = int(car_bid * enhance * boost)
            bids.append([car, total_bid, car_bid, enhance, boost])            
            log_print('bidSystem: vehicle {} has a total bid of {} (bid {}, enhancement {})'.format(car.getID(), total_bid, car_bid, enhance))

        bids, winner, winner_total_bid, winner_bid, winner_enhance = self.sortBids(bids)

        log_print('bidSystem: vehicle {} pays {}'.format(winner.getID(), winner_bid - 1))
        # if winner is test_veic, then winner_bid is discounted bid, not full flat bid 
        if winner.getID() == self.test_veic:
            winner.setBudget(winner.getBudget() - self.last_flat_bid + 1)
            self.bank += self.last_flat_bid - self.last_discounted_bid
        else:
            winner.setBudget(winner.getBudget() - winner_bid + 1)
        sponsorship_winner = sponsors[winner]
        if winner.getID() != self.em_veic: #em veic does not pay        
            self.bidPayment(bids, winner_bid-sponsorship_winner)
        departing = []
        for b in bids:
            departing.append(b[0])  # appends departing cars in order and return them as a list.

        return departing
