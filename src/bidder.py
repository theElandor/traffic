import tensorflow as tf
from tensorflow.keras.models import Model
from tensorflow.keras.layers import Input, Dense, Concatenate, Embedding, Reshape, Flatten
from tensorflow.keras import Sequential
import numpy as np
import tensorflow as tf
from tensorflow.keras.models import Model
from tensorflow.keras.layers import Input, Dense, Concatenate, Embedding, Reshape, Flatten
from tensorflow.keras import Sequential
import numpy as np
import random
from collections import deque
from tensorflow import keras
import gc

class Agent:

	def __init__(self, load, train):
		self.action_size = 20 # veics can bid between 0 and 20
		self.experience_replay = deque()
		self.gamma = 0.5 # discount rate
		#più gamma è vicino a 1, più si da importanza alle informazioni passate.

		self.training_epsilon = 0.4
		self.exploration_epsilon = 0.6
		self.train = train
		self.model_version = "bidderv1"
		self.q_path = "/home/eros/traffic/models/"+str(self.model_version)+"/q-network"
		self.target_path = "/home/eros/traffic/models/"+str(self.model_version)+"/target-network"        
		if train == False: #we always want to exploit better solution
			self.epsilon = 0
		else:
			self.epsilon = 0.3
		if load == False:
			self.q_network = self._build_model()
			self.target_network = self._build_model()
		else:
			self.load(self.q_path, self.target_path)
	def save(self):
		"""
		Method that saves the weights of the neural network
		"""
		self.q_network.save("q-network")
		self.target_network.save("target-network")
	def set_exploration_epsilon(self):
		"""
		Used when memory is still less big than batch size
		"""
		self.epsilon = self.exploration_epsilon
	def set_training_epsilon(self):
		"""
		Used when memory size is bigger than batch size
		and the model is trying to get new examples in memory
		"""
		self.epsilon = self.training_epsilon
	def load(self,q_path, target_path):
		"""
		Method that loads the models from specified paths
		INPUT: 
		q_path: path of q_network
		target_path: path of target_network
		"""
		self.q_network = keras.models.load_model(q_path)
		self.target_network = keras.models.load_model(target_path)                

	def _build_optv1_model(self):
		"""		
		"""
		model = Sequential()
		model.add(Embedding(9, 4, input_length=1)) #ritorna 1 array lungo 4
		model.add(Reshape((4,4)))
		model.add(Flatten(input_shape=(4,4)))
		model.add(Dense(64, activation='relu'))
		model.add(Dense(32, activation='relu'))
		model.add(Dense(self.action_size, activation='softmax'))
		model.compile(loss='mse', optimizer="adam")
		
		return model        	
	
	def remember(self, state, action, reward, next_state, done):
		self.experience_replay.append((state, action, reward, next_state, done))

	def act(self, state):
		"""        
		function used to build experience, by either using random action or current optimal
		INPUT
		tate: state of the environment
		
		OUTPUT: integer (0-14) to either a random action or the 
				action with the highest q-value
		"""        
		if np.random.rand() <= self.epsilon:
			print("EXPLORING.......")
			return random.randrange(self.action_size) #int between 0 and 14
		print("MAXIMIZING.....")
		q_values = self.q_network.predict(state, verbose=0)
		print("Q-VALUES: " + str(q_values))
		gc.collect()
		keras.backend.clear_session()
		print("PICKING action with index:  " + str(np.argmax(q_values[0])))
		return np.argmax(q_values[0])
	
	def alighn_target_model(self):
		self.target_network.set_weights(self.q_network.get_weights())
		
	def retrain(self, batch_size): #network learns from past experience        
		minibatch = random.sample(self.experience_replay, batch_size)
		for state, action, reward, next_state in minibatch:
			print("DEBUG:" + str(state))
			target = self.q_network.predict(state,verbose=0)        
			t = self.target_network.predict(next_state,verbose=0) #retrieve data from past experience
			#here we sum reward and q-value. This means that the reward
			#function and the neural network must return "compatible" values.
			target[0][action] = reward + self.gamma * np.amax(t)
			
			#train the network giving input from memory and        
			self.q_network.fit(state, target, epochs=1)
		gc.collect()
		keras.backend.clear_session()