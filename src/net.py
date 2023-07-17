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
        self.action_size = 15
        self.experience_replay = deque()
        self.gamma = 0.6  # discount rate
        #più gamma è vicino a 1, più si da importanza alle informazioni passate.
        self.training_epsilon = 0.2
        self.exploration_epsilon = 0.9
        self.train = train
        self.q_path = "/home/eros/traffic/models/ql_wtv2/q-network"
        self.target_path = "/home/eros/traffic/models/ql_wtv2/target-network"
        #
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
        self.epsilon = self.exploration_epsilon
    def set_training_epsilon(self):
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
        Function that builds simple model that optimizes crossing
        throughput
        """
        model = Sequential()
        model.add(Embedding(5, 4, input_length=4)) #ritorna 4 array lunghi 4 in output
        model.add(Reshape((4,4)))
        model.add(Flatten(input_shape=(4,4)))
        model.add(Dense(50, activation='relu'))
        model.add(Dense(50, activation='relu'))
        model.add(Dense(self.action_size, activation='linear'))
        model.compile(loss='mse', optimizer="adam")
        
        return model        
    def _build_model(self):
        """
        This function creates the "brain" of the agent, which is the intersection manager.
        """
        directions_input = Input(shape=(4), name='directions_input_layer')
        directions_input_embedder = Embedding(5,4,input_length=4)(directions_input)
        reshaper = Reshape((4,4))(directions_input_embedder)
        flattener = Flatten(input_shape=(4,4))(reshaper)
        x = Dense(64, activation="relu")(flattener)
        x = Dense(32, activation="relu")(x)
        output_x = Dense(self.action_size, activation='linear')(x)
        model_x = Model(inputs=[directions_input],outputs=output_x)
      
        queue_input = Input(shape=(4), name='queue_input_layer')
        y = Dense(64, activation="relu")(queue_input)
        y = Dense(32, activation="relu")(y)
        y = Dense(4, activation="sigmoid")(y)
        model_y = Model(inputs=[queue_input],outputs=y)

        waiting_time_input = Input(shape=(4), name='wt_input_layer')
        w = Dense(64, activation="relu")(waiting_time_input)
        w = Dense(32, activation="relu")(w)
        w = Dense(4, activation="sigmoid")(w)
        model_w = Model(inputs=[waiting_time_input],outputs=w)
        

        combined = keras.layers.concatenate([model_x.output, model_y.output, model_w.output])
        # combined = keras.layers.concatenate([model_x.output, multiplied])
        z = Dense(32, activation="relu")(combined)
        z = Dense(32, activation="relu")(z)
        z = Dense(self.action_size, activation="linear")(z)                

        model = Model(inputs=[model_x.input, queue_input, waiting_time_input], outputs=z)
        model.compile(optimizer='adam', loss='mse')
        
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
        for state, action, reward, next_state, done in minibatch:
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
