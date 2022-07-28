
from tensorflow.keras.preprocessing.image import ImageDataGenerator
import tensorflow as tf
from tensorflow.keras.optimizers import RMSprop

training_dir = 'cover_catagories/'
# All images will be rescaled by 1./255
train_datagen = ImageDataGenerator(rescale=1/255)


# images dimensions
# height  = 600
# width = 392


train_generator = train_datagen.flow_from_directory(
 training_dir,
 batch_size = 2,
 target_size=(600, 392),
 class_mode='binary'
)


model = tf.keras.models.Sequential([
 tf.keras.layers.Conv2D(64, (3,3), activation='relu',
 input_shape=(600, 392, 3)),
 tf.keras.layers.MaxPooling2D(2, 2),
 # The second convolution
 tf.keras.layers.Conv2D(64, (3,3), activation='relu'),
 tf.keras.layers.MaxPooling2D(2,2),
 # The third convolution
 tf.keras.layers.Conv2D(128, (3,3), activation='relu'),
 tf.keras.layers.MaxPooling2D(2,2),
 # The fourth convolution
 tf.keras.layers.Conv2D(128, (3,3), activation='relu'),
 tf.keras.layers.MaxPooling2D(2,2),
 # Flatten the results to feed into a DNN
 tf.keras.layers.Flatten(),
 # 512 neuron hidden layer
 tf.keras.layers.Dense(512, activation='relu'),
 tf.keras.layers.Dense(1, activation='sigmoid')
])

model.compile(loss='binary_crossentropy',
 optimizer=RMSprop(lr=0.001),
 metrics=['accuracy'])

history = model.fit_generator(
 train_generator,
 epochs=15, 
)

model.save("trained_model")

