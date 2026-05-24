"""
FastAPI 수강기록 관리 서버
- GET /courses  : 전체 수강기록 반환
- POST /courses : 새 수강기록 추가 (JSON 파일에 반영)
"""

import json
import os
from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field
from fastapi.exceptions import RequestValidationError
import uvicorn

app = FastAPI(title="Course Records API")

# JSON 파일 경로 (main.py 와 같은 폴더에 위치)
DATA_FILE = os.path.join(os.path.dirname(__file__), "courses.json")


# ---------- Pydantic 모델 ----------
class Course(BaseModel):
    course_name: str = Field(..., min_length=1, description="과목명")
    year: str = Field(..., description="이수연도")
    semester: str = Field(..., description="이수학기")
    grade: str = Field(..., description="성적")


# ---------- 파일 입출력 헬퍼 ----------
def load_courses() -> list:
    """JSON 파일에서 수강기록 불러오기. 파일이 없으면 빈 리스트를 만들어 반환."""
    if not os.path.exists(DATA_FILE):
        with open(DATA_FILE, "w", encoding="utf-8") as f:
            json.dump([], f, ensure_ascii=False, indent=2)
        return []

    try:
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
            if not isinstance(data, list):
                # 데이터가 손상되었을 경우 빈 리스트로 복구
                return []
            return data
    except (json.JSONDecodeError, OSError):
        # JSON 파싱 오류 등이 발생해도 서버는 죽지 않도록 빈 리스트 반환
        return []


def save_courses(data: list) -> None:
    """수강기록 리스트를 JSON 파일에 저장."""
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


# ---------- 전역 예외 처리 (서버가 죽지 않도록) ----------
@app.exception_handler(Exception)
async def global_exception_handler(request, exc: Exception):
    """예상치 못한 예외가 발생하더라도 서버가 계속 실행되도록 처리."""
    return JSONResponse(
        status_code=500,
        content={"msg": "internal server error", "detail": str(exc)},
    )


# ---------- 라우트 ----------
@app.get("/")
async def root() -> dict:
    return {"msg": "Course Records API. Use GET/POST /courses"}


@app.get("/courses")
async def get_courses():
    """저장되어 있는 전체 수강기록(JSON list) 반환."""
    courses = load_courses()
    return courses


@app.post("/courses")
async def add_course(course: Course):
    """새 과목 정보를 받아 JSON list 끝에 추가하고 파일에 저장."""
    courses = load_courses()
    courses.append(course.model_dump())
    save_courses(courses)
    return {
        "msg": "course added successfully",
        "added": course.model_dump(),
        "total": len(courses),
    }


if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)