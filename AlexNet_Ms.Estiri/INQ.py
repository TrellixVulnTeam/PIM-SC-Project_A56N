# -*- coding: utf-8 -*-
"""INQ

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1b6HzSN9vKz17vrUKdvFNsNklmxRhpQQl
"""



from keras.datasets import cifar10
from keras.utils import np_utils
import numpy as np
from keras.models import Sequential
from keras.layers.core import Dense, Dropout, Activation, Flatten
from keras.layers.convolutional import Conv2D, MaxPooling2D, ZeroPadding2D
from keras.layers.normalization import BatchNormalization
from keras.optimizers import rmsprop
from keras.regularizers import l2
import matplotlib.pyplot as plt
import matplotlib.image as mpimg
import tensorflow as tf
from keras.preprocessing.image import ImageDataGenerator
from keras.optimizers import SGD
from keras.optimizers import Optimizer
import random
import math

from tensorflow.python.client import device_lib
#print(device_lib.list_lo             cal_devices())

from keras import backend as K
from keras.legacy import interfaces
K.tensorflow_backend._get_available_gpus()
import os

NO_EPOCHS = 1

CLASSES = ["airplane", "automobile", "bird", "cat", "deer", "dog", "frog",
           "horse", "ship", "truck"]


RUN_FLAG = False

create_dirs = False

load_weights_A1_T = False

if create_dirs:
    os.mkdir("/content/weights")
    os.mkdir('/content/result')
    

A1 = []
T = []
if load_weights_A1_T:
    
    for i in range(8):
        t_name = "/content/result/1T_{0}.txt".format(i)
        a_name = '/content/result/new_1A1_layer_{0}.txt'.format(i)
        A1.append(np.loadtxt(a_name))
        T.append(np.loadtxt(t_name))
        print('loading weights ... no {0}'.format(i))

class MyOptimizer(Optimizer):

    def __init__(self, lr=0.01, momentum=0., decay=0.,
                 nesterov=False, T=[], **kwargs):
        super(MyOptimizer, self).__init__(**kwargs)
        with K.name_scope(self.__class__.__name__):
            self.iterations = K.variable(0, dtype='int64', name='iterations')
            self.lr = K.variable(lr, name='lr')
            self.momentum = K.variable(momentum, name='momentum')
            self.decay = K.variable(decay, name='decay')
        self.initial_decay = decay
        self.nesterov = nesterov
        self.T_WITH_ZEROS = T
        self.T = []
        self.is_T = False
    
    def calc_t(self, params):
        indexes = [0, 4, 8, 12, 16, 20, 24, 28]
        for i in params:
            self.T.append(np.ones(i.shape))
            # print(i.shape)
        if self.T_WITH_ZEROS != []:
            for i in range(8):
                self.T_WITH_ZEROS[i] = self.T_WITH_ZEROS[i].reshape(params[indexes[i]].shape)
                self.T[indexes[i]] = self.T_WITH_ZEROS[i] 
        print("T matrix is loaded in optimizer")
                
        
    @interfaces.legacy_get_updates_support
    def get_updates(self, loss, params):
        grads = self.get_gradients(loss, params)
        
        if not self.is_T:
            self.calc_t(params)
            self.is_t = True
        
        
        self.updates = [K.update_add(self.iterations, 1)]

        lr = self.lr
        if self.initial_decay > 0:
            lr = lr * (1. / (1. + self.decay * K.cast(self.iterations,
                                                      K.dtype(self.decay))))
        # momentum
        shapes = [K.int_shape(p) for p in params]
        moments = [K.zeros(shape) for shape in shapes]
        self.weights = [self.iterations] + moments
        for p, g, m , t in zip(params, grads, moments, self.T):
            v = self.momentum * m - lr * g * t # velocity
            self.updates.append(K.update(m, v))
     
            if self.nesterov:
                new_p = p + self.momentum * v - lr * g * t
            else:
                new_p = p + v

            # Apply constraints.
            if getattr(p, 'constraint', None) is not None:
                new_p = p.constraint(new_p)
                
            self.updates.append(K.update(p, new_p))        

            
        return self.updates

    def get_config(self):
        config = {'lr': float(K.get_value(self.lr)),
                  'momentum': float(K.get_value(self.momentum)),
                  'decay': float(K.get_value(self.decay)),
                  'nesterov': self.nesterov}
        base_config = super(SGD, self).get_config()
        return dict(list(base_config.items()) + list(config.items()))

def get_class_name (array):
  
  array2= []
  for i in array :
    array2.append(CLASSES[i])
    
  return array2

def get_data(num_classes=10):

  print('[INFO] Loading the CIFAR10 dataset...')
  (train_data, train_labels), (test_data, test_labels) = cifar10.load_data()

  train_labels = np_utils.to_categorical(train_labels, num_classes)
  test_labels = np_utils.to_categorical(test_labels, num_classes)
  #print (train_labels)
  #print (test_labels)
 
  train_data = train_data.astype('float32')
  test_data = test_data.astype('float32')
  train_data /= 255
  test_data /= 255

  return train_data, train_labels, test_data, test_labels

train_data, train_labels, test_data, test_labels = get_data()

#get_data(num_classes=10)
train_datagen = ImageDataGenerator(
        width_shift_range=0.1,  # randomly shift images horizontally (fraction of total width)
        height_shift_range=0.1,  # randomly shift images vertically (fraction of total height)
        horizontal_flip=True)   # flip images horizontally

validation_datagen = ImageDataGenerator()

train_generator = train_datagen.flow(train_data[:40000],train_labels[:40000], batch_size=32)
validation_generator = validation_datagen.flow(train_data[40000:], train_labels[40000:], batch_size=32)



def alexnet_model(img_shape=(32, 32, 3),n_classes=10, l2_reg=0.01 ,weights=None):

  
  alexnet = Sequential()

  # Layer 1
  alexnet.add(Conv2D(96, (11, 11), input_shape=img_shape,
    padding='same', kernel_regularizer=l2(l2_reg)))
  
  alexnet.add(BatchNormalization())
  alexnet.add(Activation('relu'))
  alexnet.add(MaxPooling2D(pool_size=(2, 2)))
  alexnet.add(Dropout(0.25))

  # Layer 2
  alexnet.add(Conv2D(256, (5, 5), padding='same',name ='convolution'))
  alexnet.add(BatchNormalization())
  alexnet.add(Activation('relu'))
  alexnet.add(MaxPooling2D(pool_size=(2, 2)))

  # Layer 3
  alexnet.add(ZeroPadding2D((1, 1)))
  alexnet.add(Conv2D(384, (3, 3), padding='same'))
  alexnet.add(BatchNormalization())
  alexnet.add(Activation('relu'))
  alexnet.add(MaxPooling2D(pool_size=(2, 2)))

  # Layer 4
  alexnet.add(ZeroPadding2D((1, 1)))
  alexnet.add(Conv2D(384, (3, 3), padding='same'))
  alexnet.add(BatchNormalization())
  alexnet.add(Activation('relu'))

  # Layer 5
  alexnet.add(ZeroPadding2D((1, 1)))
  alexnet.add(Conv2D(256, (3, 3), padding='same'))
  alexnet.add(BatchNormalization())
  alexnet.add(Activation('relu'))
  alexnet.add(MaxPooling2D(pool_size=(2, 2)))

  # Layer 6
  alexnet.add(Flatten())
  alexnet.add(Dense(4096))
  alexnet.add(BatchNormalization())
  alexnet.add(Activation('relu'))
  alexnet.add(Dropout(0.5))

  # Layer 7
  alexnet.add(Dense(4096))
  alexnet.add(BatchNormalization())
  alexnet.add(Activation('relu'))
  alexnet.add(Dropout(0.5))
  
  # Layer 8
  alexnet.add(Dense(n_classes))
  alexnet.add(BatchNormalization())
  alexnet.add(Activation('softmax'))

  if weights is not None:
    alexnet.load_weights(weights)

  return alexnet

model = alexnet_model(weights='/content/w15epoch')

import numpy as np


iterate = '1'


def read_weights_from_file(file_name):
    weights = np.loadtxt(file_name)
    return weights

  
def read_weights_online(weights):
  return weights
  

def generate_seed(size, s):
    np.random.seed(s)
    rand = np.arange(size)
    np.random.shuffle(rand)
    return rand


def generate_A1_A2_T(weights):
    seed = generate_seed(len(weights), 0)
    a = (len(weights)) // 2 + 1
    A1 = weights[seed[:a]]
    A2 = weights[seed[a:]]
    T = np.ones(len(weights))
    T[seed[:a]] = np.zeros(a)

    return A1, A2, T

# w = np.array([1,2,3,4,5,67,8,9,2,32,23,2,12])
# s = generate_seed(len(w), 0)
# generate_A1_A2_T(w, s)


def generate_n1_n2(weights, bit_width):
    s = max(abs(weights))
    n1 = np.floor(np.log2(4*s/3))
    n2 = (n1 + 1 - (2**(bit_width-2)))

    return n1, n2

def generate_P(n1, n2):
    result = [0]

    for i in range(int(n2), int(n1+1)):
        result.append(2**i)
        result.append(-2**i)

    result.sort()
    return result


def quantization(A1, P):

    for i in range(len(A1)):
        flag = False
        for j in range(len(P)-1):
            alpha = P[j]
            beta = P[j+1]
            if (alpha + beta) / 2 <= abs(A1[i]) and abs(A1[i]) < 3 * beta / 2:
                A1[i] = beta * np.sign(A1[i])
                flag = True
                break
        if not flag:
            A1[i] = 0
    return A1


def run (layer_i, weights):
    # weights = read_weights('weights/weight' + str(layer_i) + '.txt')
    weights = read_weights_online(weights)
    n1, n2 = generate_n1_n2(weights, 5)
    P = generate_P(n1, n2)
    A1, A2, T = generate_A1_A2_T(weights)

    new_A1 = quantization(A1, P)

    np.savetxt('/content/result/new_' + iterate + 'A1_layer_' + str(layer_i) + '.txt', new_A1,  fmt='%5s')
    np.savetxt('/content/result/' + iterate + 'T_' + str(layer_i) + '.txt',  T, fmt='%5s')
    
    return new_A1, T

w_f = ["conv2d_1", "convolution", "conv2d_2", "conv2d_3", "conv2d_4","dense_1", "dense_2", "dense_3"]

if RUN_FLAG:
    cc = 0
    for i in w_f:
        a1, t = run(cc, model.get_layer(i).get_weights()[0].flatten())
        A1.append(a1)
        T.append(t)
        print(i)
        cc += 1



if not RUN_FLAG:
  mo = MyOptimizer(lr=0.01, decay=1e-6, momentum=0.9, nesterov=True, T=T)
  model.compile(loss='categorical_crossentropy',
		optimizer=mo,
  history = model.fit_generator(train_generator,    
                      validation_data=validation_generator,
                      validation_steps=len(train_data[40000:]) / 32,
                      steps_per_epoch=len(train_data[:40000]) / 32,
                      epochs=2,
                      verbose=2)

  (loss, accuracy) = model.evaluate(test_data, test_labels,
        batch_size=128,
        verbose=1)
  print('[INFO] accuracy: {:.2f}%'.format(accuracy * 100))

def save_weights(layer_name,file_name):
#   print(len(model.get_layer(layer_name).get_weights()))
#   print(model.get_layer(layer_name).get_weights()[0])
#   print(len(model.get_layer(layer_name).get_weights()[0][0]))
#   print(len(model.get_layer(layer_name).get_weights()[0][1]))
#   print(len(model.get_layer(layer_name).get_weights()[1]))

    np.savetxt("/content/weights"+file_name+".txt",model.get_layer(layer_name).get_weights()[0].flatten() , fmt='%5s')
    
w_f = [("conv2d_1" , "weight1"), ("convolution", "weight2"),("conv2d_2","weight3"),("conv2d_3","weight4"),("conv2d_4","weight5"),("dense_1","weight6"),("dense_2","weight7"),("dense_3","weight8")]
for i,j in w_f:
    continue
    save_weights(i,j)
    print(i)



