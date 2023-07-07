temp = []
if crossroad == "F":                    
print("Listing extra followers for current = " + str(current))
for car in traffic[crossroad][current_start]:
   # traci.vehicle.isStopped(v.getID())               
   # get only cars that are stopped behind the current stopped car
   if traci.vehicle.getSpeed(car.getID()) == 0: 
       temp.append(car)
sorted_temp = sorted(temp, key=lambda vehicle: traci.vehicle.getLanePosition(vehicle.getID()), reverse=True)
for car in sorted_temp:                        
   if car.getID() != current: 
       print(type(car))

       index = car.getRouteIndex()
       car_current_position = car.getRoute()[index]
       direction = car.getRoute()[index+1]

       print("current position for car " + str(car) + " " + car_current_position)
       if (direction == current_direction):
           try:
               traci.vehicle.setStop(car.getID(), car_current_position, duration=0)
           except Exception as e:
               print("Car current index: " + str(index))
               print("Car current position: " + str(car_current_position))
               print("Route for veic " + car.getID() +" --> " + str(car.getRoute()))
               print("Stop for veic " + car.getID() +" --> " + str(traci.vehicle.getStops(car.getID())))
               print(e)
                
