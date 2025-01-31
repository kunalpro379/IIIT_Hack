from tensorflow.keras.preprocessing.image import ImageDataGenerator
from tensorflow.keras.callbacks import EarlyStopping

train_gen = ImageDataGenerator(rescale=1./255,
                               width_shift_range=0.4,
                               height_shift_range=0.4,
                               fill_mode='nearest',
                               shear_range=0.15,
                               horizontal_flip=True)
test_gen = ImageDataGenerator(rescale=1./255)

from tensorflow.keras.layers import Conv2D, Dense, MaxPooling2D, Input, Flatten
from tensorflow.keras.models import Model

train_set = train_gen.flow_from_directory(directory='Train',
                                          target_size=(64, 64),
                                          color_mode='rgb',
                                          class_mode='categorical',
                                          batch_size=32,
                                          shuffle=True,
                                          seed=42)

test_set = test_gen.flow_from_directory(directory='Test',
                                        target_size=(64, 64),
                                        color_mode='rgb',
                                        class_mode='categorical',
                                        batch_size=32,
                                        shuffle=True,
                                        seed=42)

inp = Input(shape=(64, 64, 3))
x = Conv2D(32, (3, 3), kernel_initializer='glorot_normal', input_shape=(64, 64, 3), activation='relu')(inp)
x = MaxPooling2D((2, 2))(x)
x = Conv2D(32, (3, 3), kernel_initializer='glorot_normal', input_shape=(64, 64, 3), activation='relu')(x)
x = MaxPooling2D((2, 2))(x)
x = Flatten()(x)
x = Dense(64, activation='relu', kernel_initializer='glorot_normal')(x)
pred = Dense(3, activation='softmax')(x)

model = Model(inputs=inp, outputs=pred)

model.compile(loss='categorical_crossentropy', optimizer='adam', metrics=['accuracy'])
early = EarlyStopping(monitor='val_accuracy', patience=10, mode='max')
H = model.fit(train_set,
              steps_per_epoch=train_set.n // train_set.batch_size,
              validation_data=test_set,
              epochs=15,
              callbacks=[early],
              validation_steps=test_set.n // test_set.batch_size)

model.evaluate(test_set, steps=test_set.n // test_set.batch_size)

steps_test = test_set.n // test_set.batch_size
steps_train = train_set.n // train_set.batch_size

test_set.reset()
pred = model.predict(test_set)
import numpy as np
pred = np.argmax(pred, axis=1)

labels = (test_set.class_indices)
labels = dict((v, k) for k, v in labels.items())
pred = [labels[k] for k in pred]

from sklearn.metrics import classification_report, confusion_matrix
filenames = test_set.filenames
import pandas as pd
results = pd.DataFrame({'Filenames': filenames,
                        'Predictions': pred})
results.to_csv("results.csv", index=False)

import matplotlib.pyplot as plt

plt.style.use("ggplot")
plt.figure()
plt.plot(np.arange(0, 15), H.history['accuracy'], label="train_acc")
plt.plot(np.arange(0, 15), H.history['val_accuracy'], label="val_acc")
plt.title("Accuracy v/s Epochs")
plt.xlabel("Epoch#")
plt.ylabel("Accuracy")
plt.legend()
plt.show()

plt.style.use("ggplot")
plt.figure()
plt.plot(np.arange(0, 15), H.history['loss'], label="train_loss")
plt.plot(np.arange(0, 15), H.history['val_loss'], label="val_loss")
plt.title("Loss v/s Epochs")
plt.xlabel("Epoch#")
plt.ylabel("Loss")
plt.legend()
plt.show()








