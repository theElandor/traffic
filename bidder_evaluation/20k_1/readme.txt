----settings---
gamma = 0.2
training_epsilon = 0.1
optimizer = Adam(learning_rate=0.0001)
-----Model-----
model.add(Dense(128, activation='relu', input_shape=(9,)))
model.add(Dense(128, activation='relu'))
model.add(Dense(128, activation='relu'))
----Reward-----
+0.5 if pos is increased
-0,5 if pos is the same
+1 if veic uses the crossing
if r > 0, *1-discount
if r < 0, *discount
