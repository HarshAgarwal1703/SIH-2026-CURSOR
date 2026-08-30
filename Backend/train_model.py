import os
import joblib
import pandas as pd

from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_absolute_error

# =====================================================
# SMART MIST COOLING SYSTEM - MODEL TRAINING
# =====================================================

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

DATASET_PATH = os.path.join(BASE_DIR, "dataset.csv")
MODEL_PATH = os.path.join(BASE_DIR, "model.pkl")

# ---------------- LOAD DATASET ----------------

df = pd.read_csv(DATASET_PATH)

# Create target (next hotspot temperature)
df["next_hotspot_temp"] = (
    df.groupby("transformer_id")["hotspot_temp"].shift(-1)
)

# Remove last row of every transformer
df = df.dropna().reset_index(drop=True)

# ---------------- FEATURES ----------------

FEATURES = [
    "ambient_temp",
    "hotspot_temp",
    "load_percent",
    "load_efficiency_index",
]

TARGET = "next_hotspot_temp"

X = df[FEATURES]
y = df[TARGET]

# ---------------- TRAIN / TEST SPLIT ----------------

X_train, X_test, y_train, y_test = train_test_split(
    X,
    y,
    test_size=0.20,
    random_state=42,
    shuffle=True,
)

# ---------------- TRAIN MODEL ----------------

model = RandomForestRegressor(
    n_estimators=200,
    random_state=42,
)

model.fit(X_train, y_train)

# ---------------- EVALUATION ----------------

predictions = model.predict(X_test)
mae = mean_absolute_error(y_test, predictions)

# ---------------- SAVE MODEL ----------------

joblib.dump(model, MODEL_PATH)

# ---------------- OUTPUT ----------------

print("=" * 50)
print(" SMART MIST COOLING SYSTEM ML MODEL")
print("=" * 50)
print(f"Dataset           : {os.path.basename(DATASET_PATH)}")
print(f"Training Samples  : {len(X_train)}")
print(f"Testing Samples   : {len(X_test)}")
print(f"Features          : {len(FEATURES)}")
print(f"MAE               : {mae:.3f} °C")
print("-" * 50)
print(f"Model saved at    : {MODEL_PATH}")
print("=" * 50)