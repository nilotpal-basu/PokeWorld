from io import BytesIO
from tensorflow.keras.preprocessing.image import load_img, img_to_array
import tensorflow as tf
import numpy as np
from flask import Flask, request, jsonify

app = Flask(__name__)

# Load your model once
model = tf.keras.models.load_model("model/my_model.h5")

@app.route('/predict', methods=['POST'])
def predict():
    if 'image' not in request.files:
        return jsonify({'error': 'No image uploaded'}), 400
    
    file = request.files['image']
    
    try:
        # Wrap in BytesIO
        image = load_img(BytesIO(file.read()), target_size=(128, 128))
        img_array = img_to_array(image) / 255.0
        img_array = np.expand_dims(img_array, axis=0)

        prediction = model.predict(img_array)
        class_id = int(np.argmax(prediction))

        return jsonify({'class_id': class_id}), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__=="__main__":
    app.run(debug=True)