from pydantic import BaseModel, Field

class PredictionInput(BaseModel):
    country: str
    current_avg_7d: float = Field(..., description="Current 7-day moving average cases")
    last_week_avg_7d: float = Field(..., description="7-day moving average from 7 days ago")
    two_weeks_ago_avg_7d: float = Field(..., description="7-day moving average from 14 days ago")
    # We can calculate growth rates from the values above, 
    # but if you want manual input, we can keep them. 
    # Ideally, ML models calculate derived features automatically.
    # For this demo, we will calculate growth inside the backend to save user effort.

class PredictionOutput(BaseModel):
    country: str
    prediction_class: int # 0 or 1
    prediction_label: str # "Normal" or "Outbreak"
    probability: str # e.g. "85%"
    explanation: str