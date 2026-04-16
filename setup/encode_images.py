# train_model.py
import numpy as np
from skimage import io, transform, feature
from skimage.color import rgb2gray
import joblib
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, classification_report
from sklearn.preprocessing import LabelEncoder

# ---------------------------------------------------------
# 1. Load precomputed features
# ---------------------------------------------------------
print("Loading features...")
X, y = joblib.load("plant_features.pkl")
print(f"Loaded features for {len(X)} images.")

# ---------------------------------------------------------
# 2. Encode labels
# ---------------------------------------------------------
le = LabelEncoder()
y_encoded = le.fit_transform(y)
class_names = list(le.classes_)
print(f"Classes: {class_names}")

# ---------------------------------------------------------
# 3. Train/test split
# ---------------------------------------------------------
X_train, X_test, y_train, y_test = train_test_split(
    X, y_encoded, test_size=0.1, random_state=42, stratify=y_encoded
)

# ---------------------------------------------------------
# 4. Train classifier
# ---------------------------------------------------------
print("Training RandomForest model...")
clf = RandomForestClassifier(
    n_estimators=100,
    random_state=42,
    n_jobs=-1
)
clf.fit(X_train, y_train)

# ---------------------------------------------------------
# 5. Evaluate model
# ---------------------------------------------------------
y_pred = clf.predict(X_test)
acc = accuracy_score(y_test, y_pred)
print(f"\nTest accuracy: {acc:.3f}")
print("\nClassification report:")
print(classification_report(y_test, y_pred, target_names=class_names))

# ---------------------------------------------------------
# 6. Save model + label encoder separately
# ---------------------------------------------------------
print("\nSaving model and label encoder...")

joblib.dump(clf, "model.pkl")
joblib.dump(le, "label_encoder.pkl")

print("Saved model.pkl and label_encoder.pkl successfully!")

# ---------------------------------------------------------
# 7. Optional: test prediction on a single image
# ---------------------------------------------------------
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

        class_name = le.inverse_transform([pred])[0]
        confidence = float(np.max(prob))

        return class_name, confidence

    except Exception as e:
        print(f"Error processing {path}: {e}")
        return None, None

# Example test
test_image = "test1.jpg"
try:
    cname, conf = predict_single_image(test_image, clf, le)
    if cname:
        print(f"\nTest image prediction: {cname} ({conf:.3f})")
except:
    pass
