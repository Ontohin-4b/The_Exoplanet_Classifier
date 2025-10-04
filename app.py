from flask import render_template,request,jsonify,Flask
import numpy as np
import joblib

model = joblib.load("model.pkl")
scaler = joblib.load("scaler.pkl")

reverse_mapping = {0:"FALSE POSITIVE",1:"CANDIDATE",2:"CONFIRMED"}

app = Flask(__name__)

@app.route("/")
def home():
  return render_template("index.html")

@app.route("/predict",methods=["POST"])
def predict():
  try:
    data = request.json["features"]
    arr = np.array(data).reshape(1,-1)
    arr_scaled = scaler.transform(arr)
    pred = model.predict(arr_scaled)[0]
    proba_pred = model.predict_proba(arr_scaled)[0]
    proba_dict = {reverse_mapping[i]: round(p,3) for i,p in enumerate(proba_pred)}
    return jsonify({"prediction":reverse_mapping[pred],"probabilities":proba_dict})
  except Exception as e:
    return jsonify({"error":e})

@app.route("/about")
def about():
  return render_template("about.html")

if __name__ == "__main__":
  app.run(debug=True)