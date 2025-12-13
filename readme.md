# How to run
## Create enviroment

python -m venv venv

for window

venv\Scripts\activate 

## Create variable enviroment
create .env file contain
MONGO_URI= <your-mongouri>
## Install Requirements

pip install -r requirements.txt

## Run
uvicorn app.main:app --reload

## Open Browser
http://127.0.0.1:8000/trangchu

## When navigate to /analytic/dashboard
You must use hcmut.edu.vn email (already registered to microsoft) to log in to see the dashboard
