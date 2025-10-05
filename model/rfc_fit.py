from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import classification_report, confusion_matrix
from sklearn.impute import SimpleImputer
import pandas as pd
import numpy as np
import joblib

# Loading and processing 1st Dataset (NASA Kepler Objects of Interest)
df_raw = pd.read_csv("data/kepler_data.csv", comment="#")
feature_list = ["koi_disposition","koi_period","koi_time0bk","koi_depth","koi_prad","koi_sma","koi_incl","koi_teq","koi_insol","koi_impact","koi_ror","koi_srho","koi_dor","koi_num_transits"]
df_selected = df_raw[feature_list]

df_1 = df_selected.copy()

# Loading and processing 2nd dataset (NASA K2 Objects of Interest)
df_2 = pd.read_csv("data/k2_data.csv",comment="#")

## Feature Engineering missing column in K2 (koi_num_transits) 
#### This part was generated with an AI tool (a LLM service named Grok, URL: https://grok.com)

# Campaign dates dictionary (BJD)
campaign_dates = {
    0: (2456725.0, 2456805.0),
    1: (2456808.0, 2456891.0),
    2: (2456893.0, 2456975.0),
    3: (2456976.0, 2457064.0),
    4: (2457065.0, 2457159.0),
    5: (2457159.0, 2457246.0),
    6: (2457250.0, 2457338.0),
    7: (2457339.0, 2457420.0),
    8: (2457421.0, 2457530.0),
    9: (2457504.0, 2457579.0),
    10: (2457577.0, 2457653.0),
    11: (2457657.0, 2457732.0),
    12: (2457731.0, 2457819.0),
    13: (2457820.0, 2457900.0),
    14: (2457898.0, 2457942.0),
    15: (2457941.0, 2458022.0),
    16: (2458020.0, 2458074.0),
    17: (2458074.0, 2458176.0),
    18: (2458151.0, 2458201.0),
    19: (2458232.0, 2458348.0)
}

def get_window(camps):
    if pd.isna(camps) or not camps:
        return np.nan, np.nan
    
    camps = str(camps).split(',') if isinstance(camps, str) else camps
    
    # Filter valid campaign numbers and get start/end times
    starts = []
    ends = []
    for c in camps:
        try:
            camp_num = int(c.strip())
            if camp_num in campaign_dates:
                start, end = campaign_dates[camp_num]
                starts.append(start)
                ends.append(end)
        except (ValueError, KeyError):
            continue  
    
    return (min(starts) if starts else np.nan, max(ends) if ends else np.nan)


df_2['campaigns'] = df_2['k2_campaigns']
df_2[['obs_start_bjd', 'obs_end_bjd']] = df_2['campaigns'].apply(lambda x: pd.Series(get_window(x)))

# For transit counting (as before)
df_2['n_min'] = np.ceil((df_2['obs_start_bjd'] - df_2['pl_tranmid']) / df_2['pl_orbper'])
df_2['n_max'] = np.floor((df_2['obs_end_bjd'] - df_2['pl_tranmid']) / df_2['pl_orbper'])
df_2['num_transits'] = (df_2['n_max'] - df_2['n_min'] + 1).clip(lower=0)
df_2 = df_2[["disposition","pl_orbper","pl_tranmid","pl_trandep","pl_rade","pl_orbsmax","pl_orbincl","pl_eqt","pl_insol","pl_imppar","pl_ratror","pl_dens","pl_ratdor","num_transits"]]

#### AI written part ends here

# Concatenating df_1 and df_2
mapping = {"disposition":"koi_disposition","pl_orbper":"koi_period","pl_tranmid":"koi_time0bk",
           "pl_trandep":"koi_depth","pl_rade":"koi_prad","pl_orbsmax":"koi_sma",
           "pl_orbincl":"koi_incl","pl_eqt":"koi_teq","pl_insol":"koi_insol","pl_imppar":"koi_impact",
           "pl_ratror":"koi_ror","pl_dens":"koi_srho","pl_ratdor":"koi_dor","num_transits":"koi_num_transits"
           }
df_2 = df_2.rename(columns=mapping)

df = pd.concat([df_1,df_2])
print(df.shape)               # Output: (13568, 14)

# Input-output separation
X = df.iloc[:,1:].to_numpy()
y = df["koi_disposition"].map({"FALSE POSITIVE":0,"CANDIDATE":1,"CONFIRMED":2,"REFUTED":0}).to_numpy()

# Imputation
imputer = SimpleImputer(strategy="median")
X = imputer.fit_transform(X)

# Feature scaling 
scaler = StandardScaler()
X_scaled = scaler.fit_transform(X)

# Train-test split
X_train, X_test, y_train, y_test = train_test_split(
    X_scaled, y, test_size=1/3, shuffle=True, random_state=91, stratify=y
)

# Model Development
model = RandomForestClassifier(n_estimators=1000,max_depth=None,random_state=91,class_weight="balanced")
model.fit(X_train, y_train)

# Model Performence Evaluation
y_pred = model.predict(X_test)
print("Confusion Matrix:")
print(confusion_matrix(y_test, y_pred))
print("\nClassification Report:")
print(classification_report(y_test, y_pred, target_names=["FALSE POSITIVE","CANDIDATE","CONFIRMED"]))

## Saving the model for pipeline (NOTE: This code should be run only once)
joblib.dump(model, "model.pkl")
joblib.dump(scaler, "scaler.pkl")

# Model Performence Evaluation Result 
# Classification Report:
#                 precision    recall  f1-score   support

# FALSE POSITIVE       0.81      0.84      0.82      1718
#      CANDIDATE       0.59      0.47      0.53      1118
#      CONFIRMED       0.77      0.83      0.80      1687
# 
#       accuracy                           0.75      4523
#      macro avg       0.72      0.72      0.72      4523
#   weighted avg       0.74      0.75      0.74      4523