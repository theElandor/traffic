HOW TO USE THIS SIMULATOR FOR TESTING PURPOSES
(reinforcement learning)

The following guide will be divided in 4 sections to give
you a more modular idea of how this simulator works.
The sections are:
+ Definitions;
+ Training and Testing;
+ Example workflow;
+ Extra;

------------DEFINITIONS-----------------
DEFINITIONS:
+ test_vehicle: vehicle on which the bidder is installed,
  so the only one that uses a custom bidding strategy
  learned in time thanks to reinforcement learning.

------------TRAINING AND TESTING-----------------

MAIN FILES and FOLDERS

+ ~/traffic/configs/Comp/test.yml
  contains some general configurations for
  the single simulation.
  The fields that you have to edit are the following:
  (please leave the rest unchanged)
  + Stp: lenght of the simulation. During the training
	this parameter is usually set to 200k, for
	the testing is 5k;
  + VS: number of vehicles in the simulation;
  + Spn: max percentage of the budget that vehicles
	can spend on a single sponsorship. The stable
	model has been trained with this parameter set to 10.
	
+ ~/traffic/src/cooperative.py
  This file contains the biggest part of the modifications
  made to the original simulator. It contains the class
  that handles the intersection manager (which handles the
  the bids, the sponsorships, and the custom rules for
  the test vehicle);
  The name of the class is "cooperative", but the manager
  actually handles the auctions in a "competitive" fashion.
  (Don't pay attention to the name).
  The class contains the initialization of some parameters
  that can be changed. In the code you'll find a brief description
  for all of them, so please use that as a reference.

+ ~/traffic/q-network/, ~/traffic/target-network/
  folders that contain the neural networks that
  have been trained during the last training simulation.
  
+ ~/traffic/models/: it contains a subfolder for each model.
  If you are interested in creating a new model,
  just create a folder called <modelname> and place
  the q-network and the target-network inside that folder.
  This way you will be able to load your new model by setting
  the self.load parameter = True in the cooperative.py file.
  You will also need to specify the model name in the bidder.py file.
  
+ ~/traffic/src/bidder.py:
  it contains the initialization of some important hyperparameters
  needed during the training phase of the model.
  The most important things to remember are:
  + change self.model version based on the version of
  	the model that you want to load during testing:
	the current stable version is called 'hope', and
	you can see that there is a dedicated subdirectory
	in the 'models' folder.
  + if during the testing phase you want to enable
  	the RANDOM behaviour, the only thing you have
	to do is set self.evaluation_epsilon = 1.

------------EXAMPLE WORKFLOW-----------------
Suppose you want to train and test a new model.
Theese are the main steps you need to take:

1) Write the configuration file (~/traffic/configs/Comp/test.yml).
   Here's an example:

  model: Coop
  CP: owp
  MCA: 1
  E: y
  Spn: 10
  Bdn: b
  Rts: f
  Stp: 200000
  VS: 120
  RUNS: 1
  
2) In the cooperative.py file, use the following variables:
  + self.load = False
  + self.train = True
  + self.simulation_name = "training" (not important in this case)
  +	self.simple_saver = False
  + self.test_veic = '74'
  + self.alpha = 0.3
  + self.freq = 10
3) In the bidder.py file make sure that
  + self.evaluation_epsilon = 0
4) Run the simulation with python main.py.
   When the simulation ends the following files will
   be automatically created:
   + ~/traffic/q-network/
   + ~/traffic/target-network/
   + ~/traffic/reward.txt: contains the given reward
   	 on each function call, read thesis for more info.
	 Can be plotted, it should slightly increase overtime.
   + ~/traffic/loss.txt: this file is not that important,
   	 as the loss function will not necessarly converge in
	 when using deep reinfocement learning.   
   
   + ~/traffic/qlearn_data/<VS>/crossroad_training.txt
   + ~/traffic/qlearn_data/<VS>/traffic_training.txt

   where VS stands for the number of simulated vehicles.

   The most important files are the first 4, the others
   can be deleted, as they will not be used during the
   plotting and evaluation phase.

   You have succesfully trained your model, now it's time
   for testing.

5) Create a folder named "testing" in the traffic/models directory.
   Move the previously created q-network and target-network inside the
   models/testing folder.
6) In the bidder.py file, set the following attribute:
   self.model_version = "testing"

7) Write the configuration file (~/traffic/configs/Comp/test.yml).

  Here's an example for the testing phase:

  model: Coop
  CP: owp
  MCA: 1
  E: y
  Spn: 10
  Bdn: b
  Rts: f
  Stp: 5000
  VS: 120
  RUNS: 1


8) In the cooperative.py file, use the following variables:
   + self.load = True
   + self.train = False
   + self.test_veic = '74'   
   + self.simulation_name = "booster" (meaning that the bidder is active.)
   + self.simple_saver = False

9) Run the simulation.
   The following files will be created:
   
   + ~/traffic/qlearn_data/<VS>/crossroad_booster.txt
   + ~/traffic/qlearn_data/<VS>/traffic_booster.txt
   + ~/traffic/qlearn_data/<VS>/gained_booster.txt
   
   where VS stands for the number of simulated vehicles.
   + crossroad_booster.txt:
     contains mean and std of crossroad waiting time for
	 each one of the simulated vehicles. So basically
	 line "i" is referred to vehicle "i". We are interested
	 on line 74 (because test_veic in this case is 74).
   + traffic_booster.twxt: same as crossroad_booster, but
     contains mean and std of traffic waiting time instead.
   + gained_booster.txt --> contains the amount of money
   	 that the bidder was able to save during the simulation
	 and the total number of reroutes (= the number of
	 times that the vehicle completed his route).
	 
10) Run one simulation for 80,90,100, ecc... vehicles

11) If you want to compare your model to a random bidder,
	repeat steps from 7-10, just change the following variables:
	+ in bidder.py
	  self.evaluation_epsilon = 1
	+ in cooperative.py
	  self.simulation_name = "off"
12) Now you filled correctly the qlearn_data subfolders, and
	you can alredy make a first plot to check the results:
	run python pre_testing.py
	obv theese results are not going to be really accurate, because
	we did just 1 simulation for each number of vehicles.
	(Actually 2 simulations, one with the bidder ON and the other with the bidder OFF);
	It would be nice to have an average of multiple simulations for each number of vehicles.
	
13) Take a look at the ~/traffic/models/hope folder.
	+ q-network/, target-network/ : they contain the model;
	+ training_data/: folder that contains the backup of some
	  data gathered during the training phase. It is really important
	  to store this data in a secure place.
	+ compared_exp/: it is the main folder containg the data that is plotted
	  to produce the 2 types of plots contained in the thesis_plots/ folder.
	  For each number of vehicles (120, 130, 140) there is a folder containing
	  the data from 8 different simulations (1/ 2/ 3/ ...).
	  The final resulting structure is something like the one showed at the end of this paragraph.
	  To fill this folder there is not an automated script (needs to be done).
	  The data was manually copied from (for example) qlearn_data/120/ to models/hope/compared_exp/average_120B/1/.
	  Yes, it is a long process.
	+ The folders ending with "B" are referred to simulations where beta was set to 0.1, while
	  the ones ending with "R" are filled with data from simulations where beta was set to 0.2.
	  Just ignore the "R" ones for now.
	+ In the next paragraph I'll show you how to plot the data contained in this folder.
	  ├── average_120B
	  │   ├── 1
	  │   │   ├── crossroad_booster.txt
	  │   │   ├── crossroad_off.txt
	  │   │   ├── gained_booster.txt
	  │   │   ├── gained_off.txt
	  │   │   ├── traffic_booster.txt
	  │   │   └── traffic_off.txt
	  │   ├── 2
	  │   │   ├── crossroad_booster.txt
	  │   │   ├── crossroad_off.txt
	  │   │   ├── gained_booster.txt
	  │   │   ├── gained_off.txt
	  │   │   ├── traffic_booster.txt
	  │   │   └── traffic_off.txt
	  │   ├── 3
	  │   │   ├── crossroad_booster.txt
	  │   │   ├── crossroad_off.txt
	  │   │   ├── gained_booster.txt
	  │   │   ├── gained_off.txt
	  │   │   ├── traffic_booster.txt
	  │   │   └── traffic_off.txt
      ...
	  ...
	  ...
	  ...
	  │   ├── evaluation_data.txt
	  │   ├── evaluation.py
	  │   └── random_gained_data.txt
     
 14) If you followed the process untill here succesfully,
 	 you can run the script  ~/traffic/models/hope/compared_exp/average_120B/evaluation.py
	 for each one of average_120B/ average_130B/ and average_140B/ folders. The output
	 of this script are the files "evaluation_data.txt" and "random_gained_data.txt".
	 They are simple csv files that "sum up" the content of the subfolders, they
	 are ready to be plotted.
15)  Now you can run the ~/traffic/models/hope/random_bidder_compare_gains.py and the
	 ~/traffic/models/hope/random_bidder_compare_gains.py scripts to make the plots.
	 Theese scripts by default read the data in the subfolders contained in
	 ~/traffic/models/hope/compared_exp/ ending with "B", you can easily
	 change that in the code.

-------------------EXTRA-----------------------
+ If you want to plot the reward function, use the ~/traffic/plotter.py script.
  It reads the reward.txt file in the same folder.
  By changing the "gran" variable you can choose the granularity of the
  plot. By default this parameter is set to 180.
  	 
