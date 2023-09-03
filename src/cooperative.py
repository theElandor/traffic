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
        self.writeSaved = False
        self.simple_saver = False
        self.evaluation = False
        
        self.simulationName = "off"
        self.test_veic = "?"
        
        self.piggy_bank = False
        self.max_memory = 250
        self.freq = 10
        # parameter needed in training phase.
        self.alpha = 0.3  # importance of traffic flow compared to using cheap bets

        self.freeze = False
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

    def get_reward(self, prev_state, prev_action, current_state):

        """
        function that returns the value of the reward based on the current
        state of the environment and the prevoius state of the environment.
        state: [crossroad id, veic position]
        + crossroad id: numeric ID of the crossroad
        + veic position: veic position in lane (0: immediatly before crosser, -1 waiting to cross)
        reward: to be defined

        """
        # TODO: need to add bid value to minimize overall money spent
        print(prev_state, prev_action, current_state)
        prev_crossroad = prev_state[0][0]
        prev_position = prev_state[0][1]
        current_crossroad = current_state[0][0]
        current_position = current_state[0][1]

        discount = prev_action / 10  # [0, 0.1, 0.2, 0.3...1]
        position_reward = (prev_position - current_position)  # 1 if pos increased
        if prev_crossroad != current_crossroad:  # if veic crosses crossroad
            position_reward = 2
        final_reward = (self.alpha*(position_reward) + (1-self.alpha)*(1-discount))
        if prev_crossroad == current_crossroad and prev_position == current_position:
            final_reward = -0.3  # if veic does not move, reward is 0
        self.cumulative_reward += final_reward
        print("reward: " + str(final_reward))
        with open("reward.txt", "a") as f:
            f.write(str(final_reward)+"\n")
        with open("cumulative_reward.txt", "a") as cf:
            cf.write(str(self.cumulative_reward)+"\n")
        return final_reward

    def encode(self, state):
        """
        Function that encodes the state using soft encoding.
        for example:
        q_len = 5 (so 5 veics are waiting behind the first one)
        our veic is in position 1, so --> -1 0 1 2 3 4
        where -1 is the veic waiting to cross, 1 is our veic
        [2,1] --> [0, 0,(6-2)/6, 0, 0, 0, 0, 0, 0]
        #TODO: Need the len of the queue, not present in state currently
        """
        # state: [[2,0]] --> crossroad n2, position 0
        if len(state) == 0:
            return []
        print(state)
        encoding = [0 for i in range(9)]
        crossroad = state[0][0]
        position = state[0][1] + 1
        size = state[0][2] + 1
        value = (size-position)/size
        encoding[crossroad] = value
        return encoding

    def predict_bid(self, current_state_input):
        # current_state_input --> [[crossroad, position, len(dc)]]
        # need to convert current_state input to one hot encoding
        current_state_input_encoded = np.array([self.encode(current_state_input)])
        prev_state_input_encoded = np.array([self.encode(self.prev_state)])
        
        if self.bidder.train:
            print("TESTING VEIC PREDICTING WITH THIS INPUT:")
            print(prev_state_input_encoded, current_state_input_encoded)
            if len(prev_state_input_encoded[0]): # skips first prediction to avoid error
                reward = self.get_reward(self.prev_state, self.prev_action, current_state_input)
                if self.evaluation == False:  # always remember
                    self.bidder.remember(prev_state_input_encoded, self.prev_action, reward, current_state_input_encoded)
                else:
                    print("MEMORY: " + str(len(self.bidder.experience_replay)))
                    if len(self.bidder.experience_replay) < self.max_memory:
                        self.bidder.remember(prev_state_input_encoded, self.prev_action, reward, current_state_input_encoded)
                    else:
                        # freezes memory and sets epsilon
                        # so that the model always exploits, never explores
                        self.freeze = True
                        self.bidder.set_evaluation_epsilon()
                self.sample += 1
            if len(self.bidder.experience_replay) < self.bidder.batch_size:
                self.bidder.set_exploration_epsilon()
            else:  # so if memory is full enough
                self.bidder.set_training_epsilon()
                if self.sample > self.freq:  # train once each 10 actions
                    self.sample = 0
                    self.train_count += 1
                    print("Training(" + str(self.train_count)+"/"+str(self.freq)+")")
                    self.bidder.retrain()
                    if self.train_count == self.freq:
                        print("UPDATING TARGET NETWORK")
                        self.train_count = 0
                        if not self.freeze:
                            self.bidder.alighn_target_model()
                        else:
                            print("Model is freezed, not updating")
        action = self.bidder.act(current_state_input_encoded)
        self.prev_state = current_state_input  # save current state to get reward in next iteration
        self.prev_action = action
        return action

    def bidSystem(self, crossroad_stop_list, traffic_stop_list, crossroad):
        # function that handles bidding, uses many utility function inherited by base class.
        # input: cars waiting at the head of the crossing, cars waiting in line
        # output: ordered list of cars that have to depart from the crossroad
        # traffic_stop_list and crossroad_stop_list are related to the input crossroad.
        bids = []
        test_veic = self.test_veic
        sponsors = {}
        # for now state only saves data related to test_veic
        for v in VehiclesDict.vd.values():  # for each veichle
            if v.getID() == test_veic:  # only check test_veic
                road = traci.vehicle.getRoadID(v.getID())
                try:
                    position = traffic_stop_list[road].index(v)
                except ValueError:
                    position = -1
                current_state = [self.mapping[crossroad.name], position, len(traffic_stop_list[road])]
                current_state_input = np.array([current_state])
        # crossroad_stop_list --> lista di veicoli fermi all'incrocio, in testa alle linee
        for car in crossroad_stop_list:
            car_bid = int(car.makeBid())
            if car.getID() == test_veic:
                self.trained_veic = car
                if self.simple_saver:
                    self.last_discounted_bid = car_bid * 0.1
                    self.last_flat_bid = car_bid
                    car_bid = car_bid * 0.1
                else:  # in this case veic uses the bidder to predict the best reward
                    bid_modifier = self.predict_bid(current_state_input)
                    discount = (bid_modifier / 10)  # discount will be between 0 and 1

                    # need to be tracked only if test veic is winning veic, at the end of the function
                    self.last_discounted_bid = car_bid * discount
                    self.last_flat_bid = car_bid
                    car_bid = car_bid * discount  # apply discount to car bid
                    with open("bids.txt", "a") as bids_file:
                        bids_file.write(str(crossroad)+","+str(car_bid)+"\n")
                    print("test_veic bidded " + str(car_bid))
                    # print("Current state is: ")
                    # print(current_state)
            # COLLECT SPONSORSHIP FROM CARS BEHIND
            sponsorship = 0
            # Collecting sponsorships
            if self.settings['Spn'] > 0:
                for sp in traffic_stop_list[car.getRoadID()]:
                    if sp.getID() == test_veic:
                        tip = sp.getBudget()/sp.crossroad_counter
                    else:
                        tip = sp.makeSponsor()
                    discounted_tip = tip  # if veic is not trained, then discounted_tip is the same as tip
                    if sp.getID() == test_veic:
                        if self.simple_saver:
                            discounted_tip = 0
                            # simlpe_saver does not tip during sponsorship
                        else:  # in this case test veic2 predicts best bid
                            with open("./encounters.txt", "a") as en:
                                en.write(crossroad.name + "," + str(len(traffic_stop_list[car.getRoadID()]))+"\n")
                                en.write(crossroad.name + "," + str(len(crossroad_stop_list))+"\n")
                            sponsor_modifier = self.predict_bid(current_state_input)
                            tip_discount = (sponsor_modifier / 10)
                            if self.piggy_bank:
                                self.fair_bids += tip  # money that would have been spent normally
                                self.bank += tip - (tip*tip_discount)  # money saved
                            else:
                                self.fair_bids += tip*tip_discount  # money that would have been spent normally
                            discounted_tip = tip * tip_discount  # apply discount to tip
                            print("Current state is: " + str(current_state))
                    sponsorship += discounted_tip  # add only discounted tip
                    if self.piggy_bank:
                        sp.setBudget(sp.getBudget() - tip)  # decurt full tip (non discounted) from wallet
                    else:
                        sp.setBudget(sp.getBudget() - discounted_tip)  # decurt discounted tip
            car_bid += sponsorship
            sponsors[car] = sponsorship

            
            log_print('bidSystem: vehicle {} made a bid of {}'.format(car.getID(), car_bid))
            if self.settings['E'] == 'y':
                enhance = self.multiplier*math.log(len(traffic_stop_list[car.getRoadID()]) + 1) + 1 ## get num of cars in the same lane and apply formula.
            else:
                enhance = 1
            total_bid = int(car_bid * enhance)
            bids.append([car, total_bid, car_bid, enhance])
            log_print('bidSystem: vehicle {} has a total bid of {} (bid {}, enhancement {})'.format(car.getID(), total_bid, car_bid, enhance))

        bids, winner, winner_total_bid, winner_bid, winner_enhance = self.sortBids(bids, sponsors)

        log_print('bidSystem: vehicle {} pays {}'.format(winner.getID(), winner_bid - 1))
        # if winner is trained veic, then we update the amount of money spent and saved
        if winner.getID() == self.test_veic and self.piggy_bank:
            winner.setBudget(winner.getBudget() - self.last_flat_bid)
            self.bank += self.last_flat_bid - self.last_discounted_bid
            self.fair_bids += self.last_flat_bid
        else:
            winner.setBudget(winner.getBudget() - winner_bid)
            self.fair_bids += winner_bid
        # REDISTRIBUTE winning bid without sponsorship
        sponsorship_winner = sponsors[winner]
        self.bidPayment(bids, winner_bid-sponsorship_winner)
        departing = []
        for b in bids:
            departing.append(b[0])  # appends departing cars in order and return them as a list.
        return departing
