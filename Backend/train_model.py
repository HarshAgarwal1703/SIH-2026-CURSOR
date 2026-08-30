import pandas as pd
import joblib
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_absolute_error

# Load dataset
df = pd.read_csv("data/ETTh1.csv")

# Input features (Transformer load values)
FEATURES = ["HUFL", "HULL", "MUFL", "MULL", "LUFL", "LULL"]

# Target = Oil Temperature
TARGET = "OT"

X = df[FEATURES]
y = df[TARGET]

# 80% train, 20% test (time-series split)
split = int(len(df) * 0.8)

X_train = X[:split]
X_test = X[split:]

y_train = y[:split]
y_test = y[split:]

# Train model
model = RandomForestRegressor(
    n_estimators=200,
    random_state=42
)

model.fit(X_train, y_train)

# Evaluate
predictions = model.predict(X_test)
mae = mean_absolute_error(y_test, predictions)

print(f"Model trained successfully")
print(f"Mean Absolute Error: {mae:.3f} °C")

# Save model
joblib.dump(model, "model.pkl")
print("model.pkl saved successfully")