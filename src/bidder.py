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
from keras import layers
from collections import deque
from tensorflow import keras
from tensorflow.keras.optimizers import Adam
from tensorflow.keras import initializers
import gc

class LossHistory(keras.callbacks.Callback):
    def on_train_begin(self, logs={}):
        self.losses = []

    def on_batch_end(self, batch, logs={}):
        self.losses.append(logs.get('loss'))

class Agent:

        def __init__(self, load, train):
            self.action_size = 11  # index between 0 and 10
            self.experience_replay = deque()
            self.batch_size = 32
            # discount rate --> importanza della reward futura rispetto alla reward attuale            
            self.gamma = 0.3
            self.training_epsilon = 0.1 # epsilon used during training
            self.exploration_epsilon = 1 # epsilon used only for exploration (always explore)
            self.evaluation_epsilon = 0 # (always exploit)
            self.train = train
            self.model_version = "hope"
            self.optimizer = Adam(learning_rate=0.0001)
            self.q_path = "/home/eros/traffic/models/"+str(self.model_version)+"/q-network"
            self.target_path = "/home/eros/traffic/models/"+str(self.model_version)+"/target-network"
            if not load:
                self.q_network = self._build_model()
                self.target_network = self._build_model()
            else:
                self.set_evaluation_epsilon()
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
        def set_evaluation_epsilon(self):
            """
            Used when memory size is bigger than batch size
            and the model is trying to get new examples in memory
            """
            self.epsilon = self.evaluation_epsilon
        def load(self, q_path, target_path):
            """
            Method that loads the models from specified paths
            INPUT:
            q_path: path of q_network
            target_path: path of target_network
            """
            self.q_network = keras.models.load_model(q_path)
            self.target_network = keras.models.load_model(target_path)
        
        def _build_model(self):

            model = Sequential()

            # get number of columns in training

            # add model layers
            model.add(Dense(128, activation='relu', input_shape=(9,),kernel_initializer=initializers.RandomNormal(stddev=0.1),bias_initializer=initializers.Zeros()))
            model.add(Dense(128, activation='relu', kernel_initializer=initializers.RandomNormal(stddev=0.1),bias_initializer=initializers.Zeros()))
            model.add(Dense(128, activation='relu', kernel_initializer=initializers.RandomNormal(stddev=0.1),bias_initializer=initializers.Zeros()))
            model.add(Dense(self.action_size, activation='linear'))
            model.compile(optimizer=self.optimizer, loss='mse')
            return model
    
        def remember(self, state, action, reward, next_state):
            self.experience_replay.append((state, action, reward, next_state))

        def act(self, state):
            """
            state: tensor of length 9
            """
            if np.random.rand() <= self.epsilon:
                # exploring
                return random.randrange(self.action_size)        
            #exploiting
            q_values = self.q_network.predict(state, verbose=0)
            print("Q-VALUES: " + str(q_values))
            gc.collect()
            keras.backend.clear_session()
            return np.argmax(q_values[0])
        
        def alighn_target_model(self):
            """
            function used to copy q-network weights into target-network weights
            """
            self.target_network.set_weights(self.q_network.get_weights())
                
        def retrain(self):
            """
            Train function            
            """
            minibatch = random.sample(self.experience_replay, self.batch_size)
            for state, action, reward, next_state in minibatch:
                print("DEBUG:" + str(state))
                target = self.q_network.predict(state, verbose=0) # Q(s_{t},a_{t})
                t = self.target_network.predict(next_state, verbose=0)  # Q(s_{t+1}, a_{t+1})
                target[0][action] = reward + self.gamma * np.amax(t)
                history = LossHistory() # track loss
                self.q_network.fit(state, target, epochs=1, callbacks=[history])
                # write loss on file
                with open("loss.txt", "a") as f:
                    for n in history.losses:
                        f.write(str(n) + "\n")
            gc.collect()
            keras.backend.clear_session()
