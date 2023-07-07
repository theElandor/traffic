import tensorflow as tf
from tensorflow.keras.models import Model
from tensorflow.keras.layers import Input, Dense, Concatenate

class Agent:
    def __init__(self):
        self.action_size = 15
        self.memory = []
        self.gamma = 0.95  # discount rate
        self.epsilon = 1.0  # exploration rate
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
        direction_input_hidden = Dense(64, activation='relu')(direction_input)
        queue_length_hidden = Dense(units=64, activation='relu')(queue_length_input)
        mean_waiting_time_hidden = Dense(units=64, activation='relu')(mean_waiting_time_input)

        #merge layer
        merged_layer = Concatenate()([direction_input_hidden,queue_length_hidden, mean_waiting_time_hidden])
        # Additional Dense layers
        # dense_layer = Dense(units=128, activation='relu')(merged_layer)
        # dense_layer = Dense(units=64, activation='relu')(dense_layer)
        output = Dense(128, activation='relu')(merged_layer)
        output = Dense(self.action_size, activation='sigmoid')(output)
        model = Model(inputs=[direction_input, queue_length_input, mean_waiting_time_input], outputs=output)
        model.compile(optimizer='adam', loss='mse') # Mean Squared Error is commonly used for Q-learning
        return model
        #model.summary()
    def remember(self, state, action, reward, next_state, done):
        self.memory.append((state, action, reward, next_state, done))

    def act(self, state):
        """
        Function that returns an action
        """
        if np.random.rand() <= self.epsilon:
            return random.randrange(self.action_size) #int between 0 and 14
        q_values = self.q_network.predict(state)
        return np.argmax(q_values[0])
    
    def alighn_target_model(self):
        self.target_network.set_weights(self.q_network.get_weights())
        
    def retrain(self, bactch_size): #network learns from past experience
        minibatch = random.sample(self.memory, batch_size)
        for state, action, reward, next_state, done in minibatch:
            target = self.q_network.predict(state)
            if done:
                target[0][action] = reward
            else:
                t = self.target_network.predict(next_state) #retrieve data from past experience
                target[0][action] = reward + self.gamma * np·amax(t)
            #train the network giving input from memory and 
            self.q_network.fit(state, target, epochs=1, verbose=0)
