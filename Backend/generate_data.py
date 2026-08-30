import numpy as np
import pandas as pd

np.random.seed(42)
N_TRANSFORMERS = 60
READINGS_PER_TRANSFORMER = 200

all_rows = []

for transformer_id in range(1, N_TRANSFORMERS + 1):
    # Each virtual transformer gets its own randomized physical characteristics
    baseline_temp = np.random.uniform(28, 35)        # idle temp varies per unit/site
    peak_capability = np.random.uniform(46, 56)       # max temp under full load, per unit
    cooling_rate = np.random.uniform(2.3, 3.4)        # °C/min, per unit's mist efficiency
    trigger_threshold = np.random.uniform(32, 34)     # slight variation around your measured 33.0
    hold_threshold = trigger_threshold - 5.0          # hysteresis gap, scaled per unit

    ds_temp = baseline_temp
    mist_state = 0

    for i in range(READINGS_PER_TRANSFORMER):
        ambient_temp = np.random.uniform(baseline_temp - 2, baseline_temp + 2)
        humidity = np.random.uniform(65, 92)
        load_percent = np.random.uniform(0, 100)
        load_efficiency_index = 1.0 - (load_percent / 100.0) * 0.35

        heating_rate = 0.05 + (load_percent / 100) * ((peak_capability - baseline_temp) / 50)
        ds_temp += np.random.normal(heating_rate, 0.3)

        if mist_state == 0 and ds_temp > trigger_threshold:
            mist_state = 1
        elif mist_state == 1 and ds_temp <= hold_threshold:
            mist_state = 0

        if mist_state == 1:
            ds_temp -= cooling_rate / 6

        ds_temp = np.clip(ds_temp, baseline_temp - 1, peak_capability + 3)

        all_rows.append([transformer_id, ambient_temp, humidity, ds_temp, load_percent, load_efficiency_index, mist_state])

df = pd.DataFrame(all_rows, columns=[
    "transformer_id", "ambient_temp", "humidity", "hotspot_temp",
    "load_percent", "load_efficiency_index", "mist_on"
])
df.to_csv("dataset.csv", index=False)

print(f"Generated {len(df)} rows across {N_TRANSFORMERS} simulated transformers")
print(df.groupby("transformer_id")["hotspot_temp"].max().describe())