from fastapi import FastAPI, Request
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse, RedirectResponse
from app.models.schemas import PredictionInput, PredictionOutput
import random

app = FastAPI(title="FastAPI Analytics Platform")

# Setup Templates
templates = Jinja2Templates(directory="app/templates")

# Mount Static Files (CSS/JS/Images)
app.mount("/static", StaticFiles(directory="app/templates"), name="static")

# --- API Logic ---

@app.post("/predict", response_model=PredictionOutput)
async def predict_model(data: PredictionInput):
    """
    Dummy ML Endpoint.
    """
    score = len(data.input_text) * data.numeric_factor * random.uniform(0.8, 1.2)
    analysis_result = "Positive" if score > 20 else "Neutral"
    
    return {
        "input_received": data.input_text,
        "prediction_score": round(score, 2),
        "analysis": analysis_result
    }

# --- Page Routes ---

@app.get("/", response_class=HTMLResponse)
async def root():
    return RedirectResponse(url="/trangchu")

@app.get("/trangchu", response_class=HTMLResponse)
async def home(request: Request):
    return templates.TemplateResponse("home.html", {"request": request})

@app.get("/analytic", response_class=HTMLResponse)
async def analytic_root():
    return RedirectResponse(url="/analytic/Blog")

@app.get("/analytic/Blog", response_class=HTMLResponse)
async def analytic_blog(request: Request):
    # STATIC DATA - No Database Connection needed
    blogs = [
        {
            "title": "Understanding FastAPI", 
            "content": "FastAPI is a modern, fast (high-performance), web framework for building APIs with Python 3.7+ based on standard Python type hints.", 
            "date": "Oct 2023", 
            "author": "Admin"
        },
        {
            "title": "The Power of Static Content", 
            "content": "Sometimes you don't need a database. Static content is faster to load, easier to cache, and much simpler to deploy.", 
            "date": "Nov 2023", 
            "author": "Editor"
        },
        {
            "title": "Machine Learning Integration", 
            "content": " integrating ML models into web apps allows for real-time predictions and smarter user interactions.", 
            "date": "Dec 2023", 
            "author": "AI Team"
        }
    ]

    return templates.TemplateResponse("blog.html", {
        "request": request, 
        "active_tab": "blog",
        "blogs": blogs
    })

@app.get("/analytic/Dashboard", response_class=HTMLResponse)
async def analytic_dashboard(request: Request):
    # UPDATED URL: Added &navContentPaneEnabled=false to hide left bars
    # Added &fitToWidth=true to try and force fit
    base_url = "https://app.powerbi.com/reportEmbed?reportId=675d8cb0-2267-4b01-aeec-24279f2ef21d&autoAuth=true&ctid=7bbbced8-b31a-4a36-95bb-9f06bc9d72a6&actionBarEnabled=true"
    powerbi_url = f"{base_url}&navContentPaneEnabled=false"
    
    return templates.TemplateResponse("dashboard.html", {
        "request": request, 
        "active_tab": "dashboard",
        "powerbi_url": powerbi_url
    })

@app.get("/analytic/Machine_Learning", response_class=HTMLResponse)
async def analytic_ml(request: Request):
    return templates.TemplateResponse("ml.html", {
        "request": request, 
        "active_tab": "ml"
    })