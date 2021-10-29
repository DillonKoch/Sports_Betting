# ==============================================================================
# File: model_nn.py
# Project: allison
# File Created: Friday, 17th September 2021 9:16:11 pm
# Author: Dillon Koch
# -----
# Last Modified: Friday, 17th September 2021 9:16:13 pm
# Modified By: Dillon Koch
# -----
#
# -----
# Training a neural network with keras to fit data
# ==============================================================================


import sys
from os.path import abspath, dirname

import numpy as np
from tensorflow import keras

ROOT_PATH = dirname(dirname(abspath(__file__)))
if ROOT_PATH not in sys.path:
    sys.path.append(ROOT_PATH)

from Modeling.modeling_data import Modeling_Data

features = ['1st_Downs']
targets = ['Home_ML']
x = Modeling_Data("NFL")
X_train, X_test, y_train, y_test, scaler_y = x.run(features, targets)


model = keras.models.Sequential()
model.add(keras.layers.Dense(10, input_dim=8, activation='relu'))
model.add(keras.layers.Dense(8, activation='relu'))
model.add(keras.layers.Dense(1, activation='sigmoid'))

model.compile(loss='binary_crossentropy', optimizer='adam', metrics=['accuracy'])


model.fit(np.array(X_train), y_train, epochs=10, batch_size=10)
