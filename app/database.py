import json
import sqlite3
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional


ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = ROOT / "data"
DB_PATH = DATA_DIR / "matcher.db"


def get_connection() -> sqlite3.Connection:
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db() -> None:
    with get_connection() as conn:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS analyses (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                resume_text TEXT NOT NULL,
                jd_text TEXT NOT NULL,
                score INTEGER NOT NULL,
                level TEXT NOT NULL,
                result_json TEXT NOT NULL,
                created_at TEXT NOT NULL
            )
            """
        )
        conn.commit()


def save_analysis(resume_text: str, jd_text: str, result: Dict) -> int:
    created_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with get_connection() as conn:
        cursor = conn.execute(
            """
            INSERT INTO analyses (resume_text, jd_text, score, level, result_json, created_at)
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (
                resume_text,
                jd_text,
                int(result["score"]),
                result["level"],
                json.dumps(result, ensure_ascii=False),
                created_at,
            ),
        )
        conn.commit()
        return int(cursor.lastrowid)


def list_analyses(limit: int = 20) -> List[Dict]:
    with get_connection() as conn:
        rows = conn.execute(
            """
            SELECT id, score, level, resume_text, jd_text, created_at
            FROM analyses
            ORDER BY id DESC
            LIMIT ?
            """,
            (limit,),
        ).fetchall()
    return [
        {
            "id": row["id"],
            "score": row["score"],
            "level": row["level"],
            "resume_preview": row["resume_text"][:80],
            "jd_preview": row["jd_text"][:80],
            "created_at": row["created_at"],
        }
        for row in rows
    ]


def get_analysis(analysis_id: int) -> Optional[Dict]:
    with get_connection() as conn:
        row = conn.execute(
            """
            SELECT id, resume_text, jd_text, score, level, result_json, created_at
            FROM analyses
            WHERE id = ?
            """,
            (analysis_id,),
        ).fetchone()
    if row is None:
        return None
    return {
        "id": row["id"],
        "resume_text": row["resume_text"],
        "jd_text": row["jd_text"],
        "score": row["score"],
        "level": row["level"],
        "result": json.loads(row["result_json"]),
        "created_at": row["created_at"],
    }


def delete_analysis(analysis_id: int) -> bool:
    with get_connection() as conn:
        cursor = conn.execute("DELETE FROM analyses WHERE id = ?", (analysis_id,))
        conn.commit()
        return cursor.rowcount > 0
