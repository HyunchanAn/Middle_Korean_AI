from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Optional
import os
import json
import uvicorn
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse

# Import evaluator to show metrics
# In a real scenario, we would import the model loader here
# from src.models.loader import load_model

app = FastAPI(title="Middle Korean AI Translator")

# Serve static files for frontend
# Ensure the directory exists
static_dir = os.path.join(os.path.dirname(__file__), "static")
os.makedirs(static_dir, exist_ok=True)

class TranslationRequest(BaseModel):
    text: str

class TranslationResponse(BaseModel):
    original: str
    translated: str
    hallucinations: List[str]

# Mock Translator Logic (To be replaced with real model inference)
def translate_mk_to_ko(text: str):
    # This is where the model.generate() would happen
    # Placeholder: simple character replacement + domain persona simulation
    translated = text.replace("ᄒᆞ", "하").replace("ᄂᆞ", "나").replace("ᅵ", "이")
    # Simulate a hallucination if "신고" is in the text (for demo)
    h_matches = []
    if "신고" in translated:
        h_matches.append("신고 (Modern Admin Term)")
    return translated, h_matches

@app.post("/translate", response_model=TranslationResponse)
async def translate(request: TranslationRequest):
    if not request.text:
        raise HTTPException(status_code=400, detail="Empty text")
    
    translated, h_matches = translate_mk_to_ko(request.text)
    
    return TranslationResponse(
        original=request.text,
        translated=translated,
        hallucinations=h_matches
    )

@app.get("/metrics")
async def get_metrics():
    # In a real app, this would load the latest evaluation report
    report_path = r"e:\Github\Middle_Korean_AI\data\processed\eval_report_mock.json"
    if os.path.exists(report_path):
        with open(report_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {"error": "Report not found"}

@app.get("/")
async def read_index():
    return FileResponse(os.path.join(static_dir, "index.html"))

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
