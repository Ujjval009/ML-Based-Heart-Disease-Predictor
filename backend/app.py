from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import joblib
import pandas as pd
import numpy as np

app = FastAPI(title="CardioRisk Predictor API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

model = joblib.load("model.pkl")
scaler = joblib.load("scaler.pkl")
feature_columns = joblib.load("feature_columns.pkl")

class PatientData(BaseModel):
    Age: int
    Sex: str
    ChestPainType: str
    RestingBP: float
    Cholesterol: float
    FastingBS: int
    RestingECG: str
    MaxHR: int
    ExerciseAngina: str
    Oldpeak: float
    ST_Slope: str

def preprocess_input(data: PatientData):
    raw = pd.DataFrame([data.model_dump()])

    ch_mean = 242.7
    raw['Cholesterol'] = raw['Cholesterol'].replace(0, ch_mean).round(2)
    resting_bp_mean = 132.4
    raw['RestingBP'] = raw['RestingBP'].replace(0, resting_bp_mean).round(2)

    encoded = pd.get_dummies(raw, drop_first=True)

    num_cols = ['Age', 'RestingBP', 'Cholesterol', 'MaxHR', 'Oldpeak']
    encoded[num_cols] = scaler.transform(encoded[num_cols])

    encoded = encoded.reindex(columns=feature_columns, fill_value=0)
    encoded = encoded.astype(float)

    return encoded

@app.get("/")
def root():
    return {"message": "CardioRisk Predictor API is running"}

@app.post("/predict")
def predict(data: PatientData):
    processed = preprocess_input(data)
    pred = model.predict(processed)[0]
    prob = model.predict_proba(processed)[0].tolist()

    return {
        "prediction": int(pred),
        "risk": "High" if pred == 1 else "Low",
        "probability_no_disease": round(prob[0], 4),
        "probability_disease": round(prob[1], 4),
    }
