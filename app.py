import traceback
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from main import process_day, init_db

app = FastAPI()

@app.on_event("startup")
def startup_event():
    init_db()

class DayInput(BaseModel):
    user_name: str
    training_summary: str
    feel_text: str
    food_text: str

@app.post("/log")
def log_day(data: DayInput):
    try:
        result = process_day(data.user_name, data.training_summary, data.feel_text, data.food_text)
    except Exception as e:
        traceback.print_exc()
        raise HTTPException(status_code=400, detail=f"Could not process day log: {e}")
    return result