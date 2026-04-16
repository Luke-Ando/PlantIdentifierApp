# preload_features.py
import os
import numpy as np
from skimage import io, transform, feature
import joblib

def load_plant_features(data_dir, target_size=(128, 128)):
    X = []
    y = []

    for label_name in sorted(os.listdir(data_dir)):
        label_path = os.path.join(data_dir, label_name)
        if not os.path.isdir(label_path):
            continue

        print(f"Loading {label_name}...")

        for fname in os.listdir(label_path):
            fpath = os.path.join(label_path, fname)
            try:
                img = io.imread(fpath)
                if img.ndim == 3:
                    from skimage.color import rgb2gray
                    img = rgb2gray(img)
                img_resized = transform.resize(img, target_size, anti_aliasing=True)
                hog = feature.hog(
                    img_resized,
                    orientations=9,
                    pixels_per_cell=(8, 8),
                    cells_per_block=(2, 2),
                    block_norm="L2-Hys"
                )
                X.append(hog)
                y.append(label_name)
            except Exception as e:
                print(f"Skipping {fpath}: {e}")

    return np.array(X), np.array(y)


if __name__ == "__main__":
    DATA_DIR = "plants"  # change to your folder

    print("Loading and extracting features...")
    X, y = load_plant_features(DATA_DIR)

    if len(X) == 0:
        raise ValueError("No valid images found.")

    print(f"Extracted features from {len(X)} images.")

    # Save features and labels
    joblib.dump((X, y), "plant_features.pkl")
    print("Saved features to 'plant_features.pkl'.")
