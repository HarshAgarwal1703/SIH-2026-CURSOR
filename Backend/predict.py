import os
import joblib
import numpy as np

# Path to model.pkl
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
MODEL_PATH = os.path.join(BASE_DIR, "model.pkl")

# Load trained model
model = joblib.load(MODEL_PATH)


def predict_oil_temp(features):
    """
    Predict transformer oil hot-spot temperature.

    Input: List of 6 numerical features
    Output: Predicted temperature (float)
    """
    if len(features) != 6:
        raise ValueError(f"Expected 6 features, got {len(features)}")

    x = np.array(features, dtype=float).reshape(1, -1)
    prediction = model.predict(x)

    return float(prediction[0])


# Test
if __name__ == "__main__":
    sample = [30, 10, 20, 30, 10, 20]
    temp = predict_oil_temp(sample)
    print(f"Predicted Oil Temperature: {temp:.2f} °C")