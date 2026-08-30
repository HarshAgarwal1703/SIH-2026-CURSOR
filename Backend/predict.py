import joblib
import numpy as np

model = joblib.load("model.pkl")

def predict_oil_temp(features):
    x = np.array(features).reshape(1, -1)
    return float(model.predict(x)[0])

if __name__ == "__main__":
    sample = [30, 10, 20, 10, 15, 5]
    print(predict_oil_temp(sample))