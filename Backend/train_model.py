import os
import pandas as pd
import joblib
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_absolute_error

# ---------------- PATHS ----------------
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_PATH = os.path.join(BASE_DIR, "data", "ETTh1.csv")
MODEL_PATH = os.path.join(BASE_DIR, "model.pkl")

# ---------------- LOAD DATASET ----------------
df = pd.read_csv(DATA_PATH)

# Input Features
FEATURES = [
    "HUFL",
    "HULL",
    "MUFL",
    "MULL",
    "LUFL",
    "LULL"
]

# Target
TARGET = "OT"

X = df[FEATURES]
y = df[TARGET]

# ---------------- TRAIN / TEST SPLIT ----------------
split = int(len(df) * 0.8)

X_train = X[:split]
X_test = X[split:]

y_train = y[:split]
y_test = y[split:]

# ---------------- TRAIN MODEL ----------------
model = RandomForestRegressor(
    n_estimators=200,
    random_state=42
)

model.fit(X_train, y_train)

# ---------------- EVALUATE ----------------
predictions = model.predict(X_test)
mae = mean_absolute_error(y_test, predictions)

print("=" * 40)
print(" SMART MIST COOLING ML MODEL")
print("=" * 40)
print(f"Training Samples : {len(X_train)}")
print(f"Testing Samples  : {len(X_test)}")
print(f"Mean Absolute Error : {mae:.3f} °C")

# ---------------- SAVE MODEL ----------------
joblib.dump(model, MODEL_PATH)

print(f"\nModel saved successfully!")
print(f"Location : {MODEL_PATH}")