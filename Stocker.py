""" training script """

import matplotlib
matplotlib.use('Agg')

import pandas as pd
import numpy as np
import argparse
import tensorflow as tf
from matplotlib import pyplot

import data_helpers as dh

class Stocker:
    def __init__(self, training, training_shape, test, loss='mse', optimizer=tf.keras.optimizers.Adam()):
        """ Creating Stocker instance immediately creates model 

            Model (WIP) is a two-layer LSTM. Defaults to Mean Squared Error
            loss function and ADAM optimizer function.
        """
        self.training_data = training
        self.test_data = test
        self.train_shape = training_shape

        self.model = tf.keras.Sequential()
        self.model.add(tf.keras.layers.LSTM(100, activation='tanh', recurrent_activation='sigmoid', \
                                            input_shape=training_shape[-2:]))
        self.model.add(tf.keras.layers.Dense(5))
        self.model.compile(loss=loss, optimizer=optimizer)
        print(self.model.summary())

    def train(self):
        """ Trains model in data given during Stocker's init.

            All numbers are WIP
        """
        self.history = self.model.fit(self.training_data, epochs=20, \
                            batch_size=60, steps_per_epoch = self.train_shape[0]/60, \
                            validation_data=self.test_data, validation_steps = 50)

        pyplot.figure()
        pyplot.plot(self.history.history['loss'], label='train')
        pyplot.plot(self.history.history['val_loss'], label='test')
        pyplot.xlabel('Epoch')
        pyplot.ylabel('Error')
        pyplot.legend()
        pyplot.suptitle('Loss')
        pyplot.savefig('error.png')



if __name__ == '__main__':

    """ Test/Demo of Stocker module """

    parser = argparse.ArgumentParser(description="Model Training Script")
    parser.add_argument('key', help='User API Key')
    parser.add_argument('-outdir', metavar='out', default='/models/', help="Directory for stored model(s) (one for each symbol).")
    parser.add_argument('symbols', nargs=argparse.REMAINDER, help="List of symbols to train (Place all at end of command)")
    parse = parser.parse_args()

    data = {}

    for symbol in parse.symbols:

        # read historical daily data from alpha_vantage
        # store in python dict
        hist = dh.daily(symbol, parse.key, compact=False)
        hist.head()
        data[symbol] = hist
        #print(hist)
        #print()

        pyplot.figure()
        hist.plot(subplots=True)
        pyplot.suptitle('Input Features')
        pyplot.savefig('input.png')

        """ Data Preprocessing """
        
        split = round(len(hist.index)*7/10)

        # standardize data
        data = dh.standardize(hist, split)

        # convert to tf Datasets
        train_data_set, val_data_set, train_shape = dh.to_dataset(data, split)
        
        """ -------------------------------- """

        model = Stocker(train_data_set, train_shape, val_data_set)
        model.train()