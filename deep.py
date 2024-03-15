import tensorflow as tf
import keras
from keras.applications.vgg16 import VGG16


def load_model(model_path):
    with tf.device("/gpu:0"):
        model = keras.models.load_model(model_path)
        return model


def model_from_json(model_path):
    with open(model_path, "r") as json_file:
        loaded_model_json = json_file.read()
        return keras.models.model_from_json(loaded_model_json)
    return None


def vgg16():
    return VGG16(include_top=True, weights="imagenet")
