import tensorflow as tf
import tf2onnx

MODEL_PATH = "native_invasive_classifier.keras"
ONNX_PATH = "../backend/static/model.onnx"

print("Loading Keras model...")
model = tf.keras.models.load_model(MODEL_PATH)

print("Converting to ONNX...")
spec = (tf.TensorSpec((1, 300, 300, 3), tf.float32, name="input"),)

onnx_model, _ = tf2onnx.convert.from_keras(
    model,
    input_signature=spec,
    opset=13,
    output_path=ONNX_PATH
)

print("Saved ONNX model to:", ONNX_PATH)
