
import os
import urllib.request as request
import tensorflow as tf

from zipfile import ZipFile
from pathlib import Path
from ImageClassification.entity.config_entity import PrepareBaseModelConfig

class PrepareBaseModel:
    def __init__(self, config:PrepareBaseModelConfig):
        self.config = config
    
    def get_base_model(self):
        self.model = tf.keras.applications.vgg16.VGG16(
            input_shape = self.config.params_image_size,
            weights = self.config.params_weights,
            include_top = self.config.params_include_top
        )

    @staticmethod
    def _prepare_full_model(model, classes, freez_all, freeze_till, learning_rate):
        if freez_all:
            for layer in model.layers:
                model.trainable = False
        elif(freeze_till is not None) and (freeze_till>0):
            for layer in model.layer[:-freeze_till]:
                model.trainable = False
        
        flatten_in = tf.keras.layers.Flatten()(model.output)
        
        prediction = tf.keras.layers.Dense(
            units = classes,
            activation = 'softmax'
        )(flatten_in)

        full_model = tf.keras.models.Model(
            inputs = model.input,
            outputs = prediction)

        full_model.compile(
            optimizer = tf.keras.optimizers.SGD(learning_rate=learning_rate),
            loss = tf.keras.losses.CategoricalCrossentropy(),
            metrics = ['accuracy'])
        
        full_model.summary()
        
        return full_model
    
    def update_base_model(self):
        self.full_model = self._prepare_full_model(
            model = self.model,
            classes = self.config.params_classes,
            freez_all = True,
            freeze_till = None,
            learning_rate = self.config.params_learning_rate)
        
        self.save_model(model = self.full_model,
                        path = self.config.update_base_model_path)
        
    @staticmethod
    def save_model(model:tf.keras.Model, path:Path):
        filepath = str(path)
        model.save(filepath)

