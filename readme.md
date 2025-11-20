# How to run
## Create enviroment

python -m venv venv

venv\Scripts\activate #for window
## Create variable enviroment
create .env contain
MONGO_URI= <your-mongouri>
## Install Requirements

pip install -r requirements.txt

## Replace Mongodb connection (MONGO_DETAILS) in db_config.py

## Run
uvicorn app.main:app --reload

## Open Browser
http://127.0.0.1:8000/trangchu

## When navigate to /analytic/dashboard
You must use hcmut.edu.vn email (already registered to microsoft) to log in to see the dashboard