from functools import reduce

from typing import Union
from typing import Annotated
from fastapi import FastAPI, File, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from keras.utils import plot_model

# models
# from keras.applications import InceptionResNetV2

# from keras.applications.vgg16 import VGG16
# from keras.applications.vgg19 import VGG19

from keras.optimizers import Adam
from keras.callbacks import ModelCheckpoint, EarlyStopping
from sklearn.metrics import (
    roc_curve,
    auc,
    precision_recall_curve,
    average_precision_score,
    # plot_precision_recall_curve,
    f1_score,
    confusion_matrix,
)
from keras.layers import (
    GlobalAveragePooling2D,
    Dense,
    Dropout,
    Flatten,
    Conv2D,
    MaxPooling2D,
)
from keras.models import Sequential, Model

# from keras.applications import VGG16  # , VGG19
from models import VGG

# inception_resnet_v2 = InceptionResNetV2(
#     weights="imagenet",
#     include_top=False,
#     input_shape=(299, 299, 3),
# )


def build_my_model():
    vgg_model = VGG.get_vgg16()
    for layer in vgg_model.layers:
        layer.trainable = False

    my_model = Sequential()
    my_model.add(vgg_model)
    my_model.add(Flatten())

    my_model.add(Dense(4096, activation="relu"))
    my_model.add(Dropout(0.6))
    my_model.add(Dense(128, activation="relu"))
    my_model.add(Dropout(0.5))
    my_model.add(Dense(1, activation="sigmoid"))

    # metricas
    optimizer = Adam(lr=5e-5)
    loss = "binary_crossentropy"
    metrics = ["binary_accuracy"]

    my_model.compile(optimizer=optimizer, loss=loss, metrics=metrics)
    return my_model


vgg_16 = VGG.get_vgg16()
vgg_16_mod = build_my_model()
vgg_16_mod.summary()
# plot_model(
#     vgg_16_mod, to_file="model_plot.png"  # , show_shapes=True, show_layer_names=True
# )
transfer_learning_models = {
    "VGG16": vgg_16,
    "VGG19": VGG.get_vgg19(),
    "MyVGG16": vgg_16_mod,
}


def layers_info(model):
    return list(
        map(
            lambda sub: {
                "name": sub.name,
                "class": sub.__class__.__name__,
                "dtype": sub.dtype,
                "count_params": sub.count_params(),
            },
            model.layers,
        )
    )


def gen_definitions(model):
    defs = model.get_config()
    defs["sizes"] = [
        (
            layer.output_shape[1:]
            if layer.output_shape[0] is None
            else layer.output_shape[0][1:]
        )
        for layer in model.layers
    ]
    return defs


transformed_models = {
    name: gen_definitions(model) for name, model in transfer_learning_models.items()
}


# transfer_learning_models = reduce(
#     lambda acc, obj: {**acc, "a": obj.name},
#     [inception_resnet_v2, vgg_16, vgg_19],
#     {},
# )
# transfer_learning_models = [
#     {nome: layers_info(modelo)} for modelo, nome in modelos.items()
# ]


def count_layers(mod):
    num_layers_with_params = sum(
        [1 for layer in mod.layers if layer.count_params() > 0]
    )
    return num_layers_with_params


app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
def read_root():
    return {"Hello": "World"}


@app.get("/items/{item_id}")
def read_item(item_id: int, q: Union[str, None] = None):
    return {"item_id": item_id, "q": q}


@app.get("/models")
def models():
    # list(
    #     map(
    #         lambda item: {
    #             item["name"]: list(
    #                 map(
    #                     lambda sub: {
    #                         "name": sub.name,
    #                         "class": sub.__class__.__name__,
    #                         "dtype": sub.dtype,
    #                         "count_params": sub.count_params(),
    #                     },
    #                     item["value"].layers
    #                     # [layer for layer in item.layers if layer.count_params() > 0],
    #                 )
    #             )
    #         },
    #         transfer_learning_models,
    #     )
    # ))
    return transformed_models


@app.post("/files/")
async def create_file(file: Annotated[bytes, File()]):
    return {"file_size": len(file)}


@app.post("/uploadfile/")
async def create_upload_file(file: UploadFile):
    return {"filename": file.filename}
