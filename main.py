import dataloader as d
import tensorflow as tf
from tensorflow.keras.models import Model
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import AveragePooling2D, Conv2D, Dense
from tensorflow.keras.layers import Dropout, Flatten, Input
from tensorflow.keras import regularizers
from tensorflow.keras import metrics
from visualize import confusion
from filters import compute_glcm_results
import numpy as np

#We expect tensorflow >2.3.2, preferably 2.4 or greater
print(tf.__version__)

##any config values
test_percentage = 0.2
input_shape = (100,100,1)
band = 0

#train_ds, validation_ds = d.rgb_loader()
#train_ds, val_ds = d.calib_loader()
#d.get_manual_calib_data(test_percentage, band)

#I heard that laziness is a virtue and programmers are lazy people
x_train, y_train, x_test, y_test = d.get_prepared_data()


##this section will include glcm+gabor filter computation / loading ##
#compute glcm mea+varn and store in file for later use, laziness level 2.0
#compute_glcm_results(x_train, x_test)
#mean_train, var_train, mean_test, var_test = d.get_prepared_glcm()
d.gabor(x_train, x_test)

### START NETWORK ######
inputs = Input(shape=input_shape)

#convolutional layer
conv = Conv2D(32, kernel_size=3, activation='relu')(inputs)
#pool size was not specified we can probably use 2x2 or 3x3 pooling
pooling = AveragePooling2D(pool_size=(3,3))(conv)

#first auto encoder
encoded1 = Dense(16, activation='relu', #non-linear activation
                activity_regularizer=regularizers.l1(10e-5))(pooling)#more sparse than 2nd autoencoder
decoded1 = Dense(32, activation='softmax')(encoded1)#softmax applied
dropout1 = Dropout((0.2))(decoded1)#dropout with 0.2 rate

#second auto encoder
encoded2 = Dense(8, activation='relu') (dropout1)#non-linear activation
decoded2 = Dense(16, activation='softmax')(encoded2)#softmax applied
dropout2 = Dropout((0.2))(decoded2)
#classification
flatten = Flatten()(dropout2)
#changed from 1 to 10 due to one-hot
output = Dense(10, activation='sigmoid')(flatten)
model = Model(inputs=inputs, outputs=output)

print(model.summary())
##end of summary should be (None, 10) in order to make model work,
##one-hot changed the output requirement
metrics = [metrics.Accuracy()]
model.compile(optimizer='rmsprop', loss='categorical_crossentropy', metrics=metrics)

#one-hot encoded labels, required by categorical_crossentropy
fitting = model.fit(x_train,y_train, validation_data=(test_x, test_y), epochs=1)

#currently output is only 1 values?
out = model.predict(x_test)
classes = out.argmax(axis=-1)
for i in range(3):
    print("Out:", out[i], "classes", classes[i], "test", y_test[i], "idx", i)
    print("----")

confusion(classes, y_test)
