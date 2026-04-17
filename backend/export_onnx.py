import tensorflow as tf
import tf2onnx

# Load your Keras model
model = tf.keras.models.load_model("static/native_invasive_classifier.keras")

# Convert directly from Keras model
onnx_model, _ = tf2onnx.convert.from_keras(
    model,
    opset=17,
    output_path="static/model.onnx"
)

print("Export complete!")
