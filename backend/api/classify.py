# classify_plants.py
import numpy as np
from skimage import io, transform, feature
from skimage.color import rgb2gray
import os
import joblib
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, classification_report
from sklearn.preprocessing import LabelEncoder

# Load pre‑computed features
X, y = joblib.load("plant_features.pkl")
print(f"Loaded features for {len(X)} images.")

# Convert labels to integers
le = LabelEncoder()
y = le.fit_transform(y)
class_names = list(le.classes_)
print(f"Classes: {class_names}")

# Split into train/test
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.01, random_state=42, stratify=y
)

# Train classifier
clf = RandomForestClassifier(n_estimators=50, random_state=42)
clf.fit(X_train, y_train)

# Evaluate
y_pred = clf.predict(X_test)
acc = accuracy_score(y_test, y_pred)
print(f"Test accuracy: {acc:.3f}")
print("\nClassification report:")
print(classification_report(y_test, y_pred, target_names=class_names))

# Example: classify a new image
def predict_single_image(path, model, le, target_size=(128, 128)):
    try:
        img = io.imread(path)
        if img.ndim == 3:
            img = rgb2gray(img)
        img_resized = transform.resize(img, target_size, anti_aliasing=True)
        hog = feature.hog(
            img_resized,
            orientations=9,
            pixels_per_cell=(8, 8),
            cells_per_block=(2, 2),
            block_norm="L2-Hys"
        )
        pred = model.predict([hog])[0]
        prob = model.predict_proba([hog])[0]
        class_name = le.inverse_transform([pred])[0]  # this is the safe way
        conf = max(prob)
        return class_name, conf
    except Exception as e:
        print(f"Error processing {path}: {e}")
        return None, None


# Uncomment below and set your own image path
new_path = "test1.jpg"
class_name, conf = predict_single_image(new_path, clf, le, target_size=(128, 128))
if class_name is not None:
    print(f"Predicted class: {class_name} (confidence: {conf:.3f})")
