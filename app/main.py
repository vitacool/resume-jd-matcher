from dataclasses import asdict
from pathlib import Path
from typing import List

from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field

from .analyzer import TECH_KEYWORDS, analyze_resume_jd
from .database import delete_analysis, get_analysis, init_db, list_analyses, save_analysis


ROOT = Path(__file__).resolve().parents[1]
STATIC_DIR = ROOT / "static"

app = FastAPI(
    title="Resume JD Matcher",
    description="智能简历匹配与岗位分析系统，支持岗位关键词提取、匹配度评分和简历优化建议。",
    version="1.0.0",
)

app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")


class AnalyzeRequest(BaseModel):
    resume_text: str = Field(..., min_length=20, description="简历文本")
    jd_text: str = Field(..., min_length=20, description="岗位 JD 文本")


class AnalyzeResponse(BaseModel):
    id: int
    score: int
    level: str
    similarity: float
    resume_keywords: List[str]
    jd_keywords: List[str]
    matched_keywords: List[str]
    missing_keywords: List[str]
    strengths: List[str]
    suggestions: List[str]
    route: dict


@app.on_event("startup")
def startup() -> None:
    init_db()


@app.get("/")
def index() -> FileResponse:
    return FileResponse(STATIC_DIR / "index.html")


@app.get("/history")
def history_page() -> FileResponse:
    return FileResponse(STATIC_DIR / "history.html")


@app.get("/health")
def health() -> dict:
    return {"status": "ok"}


@app.get("/api/keywords")
def keywords() -> dict:
    return {"keywords": sorted(TECH_KEYWORDS.keys())}


@app.post("/api/analyze", response_model=AnalyzeResponse)
def analyze(payload: AnalyzeRequest) -> dict:
    result = analyze_resume_jd(payload.resume_text, payload.jd_text)
    data = asdict(result)
    analysis_id = save_analysis(payload.resume_text, payload.jd_text, data)
    return {"id": analysis_id, **data}


@app.get("/api/history")
def history(limit: int = 20) -> dict:
    limit = max(1, min(limit, 100))
    return {"items": list_analyses(limit)}


@app.get("/api/history/{analysis_id}")
def history_detail(analysis_id: int) -> dict:
    item = get_analysis(analysis_id)
    if item is None:
        raise HTTPException(status_code=404, detail="analysis not found")
    return item


@app.delete("/api/history/{analysis_id}")
def remove_history(analysis_id: int) -> dict:
    deleted = delete_analysis(analysis_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="analysis not found")
    return {"deleted": True}
