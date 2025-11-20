# This file is for model Machine Learning
from pydantic import BaseModel, Field
from typing import Optional

class PredictionInput(BaseModel):
    input_text: str
    numeric_factor: float = 1.0

class PredictionOutput(BaseModel):
    input_received: str
    prediction_score: float
    analysis: str

class BlogPost(BaseModel):
    title: str
    content: str
    author: str
    date: str
    
    class Config:
        json_schema_extra = {
            "example": {
                "title": "FastAPI is Awesome",
                "content": "Here is why...",
                "author": "Dev Team",
                "date": "2023-10-27"
            }
        }