from src.intersectionManager import *
import math
import numpy as np
#print("Next edge for veic n. " + str(veic.getID()) + " is " + str(veic.getRoute()[index+1])


class Cooperative(IntersectionManager):

    def __init__(self, settings, extra_configs):
        super().__init__(settings)
        self.multiplier = extra_configs["multiplier"]
        self.congestion_rate = extra_configs["congestion_rate"]
    # override
    def bidSystem(self, crossroad_stop_list, traffic_stop_list):
        # function that handles bidding, uses many utility function inherited by base class.
        # input: cars waiting at the head of the crossing, cars waiting in line 
        # output: ordered list of cars that have to depart from the 
        bids = []
        # crossroad_stop_list --> lista di veicoli fermi all'incrocio, in testa alle linee
        for car in crossroad_stop_list:
            car_bid = int(car.makeBid() + 1)
            sponsorship = 0

            # Collecting sponsorships
            if self.settings['Spn'] > 0:
                print("Cars in " + car.getRoadID())                
                for sp in traffic_stop_list[car.getRoadID()]:
                    print(sp)
                    tip = sp.makeSponsor()
                    print('bidSystem: vehicle {} receives a sponsorship of {} from vehicle {}'.format(car.getID(), tip, sp.getID()))
                    sponsorship += tip
                    sp.setBudget(sp.getBudget() - tip)                    
            car_bid += sponsorship

            
            log_print('bidSystem: vehicle {} made a bid of {}'.format(car.getID(), car_bid))
            if self.settings['E'] == 'y': ## if enhancement is activated
                enhance = self.multiplier*math.log(len(traffic_stop_list[car.getRoadID()]) + 1) + 1 ## get num of cars in the same lane and apply formula.
                current_route_position = car.getRouteIndex()
                next_route_position = car.getRoute()[current_route_position+1]
                cars_in_next_edge = len(traci.edge.getLastStepVehicleIDs(next_route_position))
                if cars_in_next_edge < 3:
                    congestion_rate_1 = 1 #congestion rate is not applied
                else:                    
                    congestion_rate_1 = (1/np.log(cars_in_next_edge))                   
                try:
                    next_next_route_position = car.getRoute()[current_route_position+2]
                    cars_in_next_next_edge = len(traci.edge.getLastStepVehicleIDs(next_next_route_position))
                    congestion_rate_2 = (1/np.log(cars_in_next_next_edge))
                    if cars_in_next_next_edge < 3:
                        congestion_rate_2 = -1
                except:
                    cars_in_next_next_edge = next_route_position
                    congestion_rate_2 = -1
                    # print("exceeded list length")
            else:
                enhance = 1
            if self.congestion_rate:
                if congestion_rate_2 == -1:
                    congestion_rate_2 = congestion_rate_1
                corr_en = enhance * (congestion_rate_1 + congestion_rate_2)/2 #media
                # print("Congestion_rate_1 for veic " + car.getID() +" --> "+str(congestion_rate_1))
                # print("Congestion_rate_2 for veic " + car.getID() +" --> "+str(congestion_rate_2))
                # print("Next edge vor this veic is" + next_route_position)
                # print("-----------------------------------")
                log_print('bidSystem: enhancement applied on vehicle {} is {}'.format(car.getID(), enhance))
            else:
                corr_en = enhance
            total_bid = int(car_bid * corr_en)
            # if car.getID() == "10":
            #     total_bid = 500
            bids.append([car, total_bid, car_bid, corr_en])
            
            log_print('bidSystem: vehicle {} has a total bid of {} (bid {}, enhancement {})'.format(car.getID(), total_bid, car_bid, enhance))

        bids, winner, winner_total_bid, winner_bid, winner_enhance = self.sortBids(bids)

        log_print('bidSystem: vehicle {} pays {}'.format(winner.getID(), winner_bid - 1))
        #if winner is test vehicle, do not decrease budget and do not redistribute winning bid
        #to other vehicles
        # if winner.getID() != 10:
        winner.setBudget(winner.getBudget() - winner_bid + 1)        
        self.bidPayment(bids, winner_bid)

        departing = []
        for b in bids:
            departing.append(b[0]) ## appends departing cars in order and return them as a list.

        return departing
