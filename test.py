import pickle
import pandas as pd

# Load Model
with open('GrowthForecast.pkl', 'rb') as f:
    model = pickle.load(f)

# Define 3 Clear Cases
# Case A: Normal (12 months, 76cm) -> Should be Normal
case_normal = pd.DataFrame([[12, 76.0, 0]], columns=['Umur (bulan)', 'Tinggi Badan (cm)', 'Jenis Kelamin'])

# Case B: Stunted (12 months, 68cm) -> Should be Stunted
case_stunted = pd.DataFrame([[12, 68.0, 0]], columns=['Umur (bulan)', 'Tinggi Badan (cm)', 'Jenis Kelamin'])

# Case C: Tall (12 months, 85cm) -> Should be Tall
case_tall = pd.DataFrame([[12, 85.0, 0]], columns=['Umur (bulan)', 'Tinggi Badan (cm)', 'Jenis Kelamin'])

print(f"Normal Input (12mo, 76cm) Prediction: {model.predict(case_normal)[0]}")
print(f"Stunted Input (12mo, 68cm) Prediction: {model.predict(case_stunted)[0]}")
print(f"Tall Input (12mo, 85cm) Prediction:    {model.predict(case_tall)[0]}")