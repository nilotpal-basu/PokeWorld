from sklearn.utils.class_weight import compute_class_weight
import numpy as np
from model_gen import model
from data_loader import *

def image_generator(X, y, batch_size, class_weights):
    while True:
        
        for i in range(0, len(X), batch_size):
            X_batch = X[i:i + batch_size]
            y_batch = y[i:i + batch_size]
            
            
            sample_weights = np.array([class_weights.get(label, 1.0) for label in y_batch])

            yield X_batch, y_batch, sample_weights

def train_model(model , X_train , X_test , y_train , y_test):
    class_weights = compute_class_weight(
        class_weight='balanced',
        classes=np.unique(y_train),
        y=y_train
    )
    class_weights_dict = dict(enumerate(class_weights))

    history = model.fit(
        image_generator(X_train, y_train, batch_size=128, class_weights=class_weights_dict),
        steps_per_epoch=len(X_train) // 128,  
        epochs=15,
        validation_data=image_generator(X_test, y_test, batch_size=128, class_weights=class_weights_dict),
        validation_steps=len(X_test) // 128 ,
        verbose=1
    )
    current_dir = os.path.dirname(__file__)
    parent_dir = os.path.abspath(os.path.join(current_dir, os.pardir))
    model_path = os.path.join(parent_dir,r"model\my_model.h5")
    model.save(model_path)

if __name__=="__main__":
    script_directory = os.path.dirname(os.path.abspath(sys.argv[0])) 
    script_directory = os.path.join(script_directory,'pokemon-dataset-1000')
    script_directory = os.path.join(script_directory,'dataset')
    df = data_ldr(script_directory)
    X_train , X_test , y_train , y_test = data_splitter(df)
    model = model()
    model.compile(optimizer='adam',
              loss='sparse_categorical_crossentropy',
              metrics=['accuracy'])
    
    train_model(model , X_train , X_test , y_train , y_test)