from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import classification_report, confusion_matrix
import pandas as pd
import joblib

# Data Loading and basic cleaning 
df_raw = pd.read_csv("data/kepler_data.csv", comment="#")
feature_list = ["koi_disposition","koi_period","koi_time0bk","koi_depth","koi_prad","koi_sma","koi_incl","koi_teq","koi_insol","koi_impact","koi_ror","koi_srho","koi_dor","koi_num_transits"]
df_selected = df_raw[feature_list]

df_cleaned = df_selected.dropna().drop_duplicates()
df = df_cleaned.copy()

# Input-output separation
X = df.iloc[:,1:].to_numpy()
y = df["koi_disposition"].map({"FALSE POSITIVE":0,"CANDIDATE":1,"CONFIRMED":2}).to_numpy()

# Feature scaling 
scaler = StandardScaler()
X_scaled = scaler.fit_transform(X)

# Train-test split
X_train, X_test, y_train, y_test = train_test_split(
    X_scaled, y, test_size=1/3, shuffle=True, random_state=91, stratify=y
)

# Model Development
model = RandomForestClassifier(n_estimators=500,max_depth=None,random_state=91,class_weight="balanced")
model.fit(X_train, y_train)

# Model Performence Evaluation
y_pred = model.predict(X_test)
print("Confusion Matrix:")
print(confusion_matrix(y_test, y_pred))
print("\nClassification Report:")
print(classification_report(y_test, y_pred, target_names=["FALSE POSITIVE","CANDIDATE","CONFIRMED"]))

# Saving the model for pipeline (NOTE: This code should be run only once)
joblib.dump(model, "model.pkl")
joblib.dump(scaler, "scaler.pkl")

# Model Performence Evaluation Result 
# Classification Report:
#                 precision    recall  f1-score   support
# 
# FALSE POSITIVE       0.85      0.86      0.85      1363
#      CANDIDATE       0.50      0.35      0.41       498
#      CONFIRMED       0.72      0.82      0.76       911
# 
#       accuracy                           0.76      2772
#      macro avg       0.69      0.68      0.68      2772
#   weighted avg       0.74      0.76      0.75      2772