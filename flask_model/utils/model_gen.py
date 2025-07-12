from tensorflow.keras.applications import EfficientNetB0
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Dense , Dropout , BatchNormalization ,GlobalAveragePooling2D

import tensorflow as tf
import random


def model():
    base_model = EfficientNetB0(weights='imagenet', include_top=False, input_shape=(128, 128, 3))

    model = Sequential([
        base_model,  
        GlobalAveragePooling2D(), 
        BatchNormalization(),
        Dense(256, activation='relu', name="Layer1"),
        BatchNormalization(),
        Dropout(0.5), 
        Dense(128, activation='relu', name="Layer2"),
        BatchNormalization(),
        Dropout(0.5),
        Dense(1000, activation='softmax', name="output_layer")
    ])
    
    return model