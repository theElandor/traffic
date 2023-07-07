import tensorflow as tf
from tensorflow.keras.models import Model
from tensorflow.keras.layers import Input, Dense, Concatenate
import numpy as np
import random
from collections import deque

class Agent:
    def __init__(self):
        self.action_size = 15
        self.experience_replay = deque(maxlen=2000)
        self.gamma = 0.95  # discount rate
        self.epsilon = 0.5  # exploration rate
        self.epsilon_decay = 0.995
        self.epsilon_min = 0.01
        self.learning_rate = 0.001
        self.q_network = self._build_model()
        self.target_network = self._build_model()
    def _build_model(self):
        """
        This function creates the "brain" of the agent, which is the intersection manager.
        """
        #input layers
        direction_input = Input(shape=(16), name='input_layer')
        queue_length_input = Input(shape=(4,), name='queue_length_input')
        mean_waiting_time_input = Input(shape=(4,), name='mean_waiting_time_input')

        # hidden layers
        direction_input_hidden = Dense(30, activation='relu')(direction_input)
        queue_length_hidden = Dense(units=30, activation='relu')(queue_length_input)
        mean_waiting_time_hidden = Dense(units=30, activation='relu')(mean_waiting_time_input)

        #merge layer
        merged_layer = Concatenate()([direction_input_hidden,queue_length_hidden, mean_waiting_time_hidden])
        # Additional Dense layers
        output = Dense(10, activation='relu')(merged_layer)
        output = Dense(self.action_size, activation='sigmoid')(output)
        model = Model(inputs=[direction_input, queue_length_input, mean_waiting_time_input], outputs=output)
        model.compile(optimizer='adam', loss='mse') # Mean Squared Error is commonly used for Q-learning
        return model
        #model.summary()
    def remember(self, state, action, reward, next_state, done):
        self.experience_replay.append((state, action, reward, next_state, done))

    def act(self, state):
        """
        INPUT
        tate: state of the environment
        
        OUTPUT: integer (0-14) to either a random action or the 
                action with the highest q-value
        """        
        if np.random.rand() <= self.epsilon:
            return random.randrange(self.action_size) #int between 0 and 14
        print("Predicting.....")
        q_values = self.q_network.predict(state, verbose=0)
        return np.argmax(q_values[0])
    
    def alighn_target_model(self):
        self.target_network.set_weights(self.q_network.get_weights())
        
    def retrain(self, batch_size): #network learns from past experience
        minibatch = random.sample(self.experience_replay, batch_size)
        for state, action, reward, next_state, done in minibatch:
            target = self.q_network.predict(state,verbose=0)
            if done:
                target[0][action] = reward
            else:
                t = self.target_network.predict(next_state,verbose=0) #retrieve data from past experience
                # print("target[0][action] --> " + str(target[0][action]))
                # print("t --> " + str(t))
                # print("amax(t) --> " + str(np.amax(t)))
                # print("reward: --> " + str(reward))
                target[0][action] = reward + self.gamma * np.amax(t)
            #train the network giving input from memory and        
            self.q_network.fit(state, target, epochs=1)
