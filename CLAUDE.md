# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Claude Code 작업 지침

> 전역 지침(`~/.claude/CLAUDE.md`) 항상 준수

- **CLAUDE.md 수정 시**: 사용자 확인 필수, 백업 후 진행
- **문서 작성**: 간결성, Bullet 스타일, 토큰 효율성
- **응답 스타일**: 초보자 친화적, 한국어 주석, 단계별 설명
- **코드 제시**: 한 번에 많이 X, 단계별로 나눠서
- **경로**: Windows 형식(`\`) 사용

## 기술 스택

| 구분 | 기술 | 버전 |
|------|------|------|
| Frontend | Streamlit | 1.51.0 |
| Backend | FastAPI | 0.121.1 |
| 이미지 처리 | opencv-python-headless, Pillow | 4.12.0, 12.0.0 |
| DICOM | pydicom | 3.0.1 |
| 언어 | Python | 3.8+ |

## 프로젝트 구조

```
open_cv_app/
├── app.py              # Streamlit UI (사용자 인터페이스)
├── api.py              # FastAPI REST API (외부 연동용)
├── preprocess_core.py  # 핵심 이미지 처리 로직 (순수 함수)
├── requirements.txt    # 의존성 목록
└── venv/               # 가상환경
```

## 핵심 명령어

```bash
# 가상환경 활성화
venv\Scripts\activate

# Streamlit 실행 → http://localhost:8501
streamlit run app.py

# FastAPI 실행 → http://localhost:8000/docs
uvicorn api:app --reload
```

## 코딩 스타일

- 파일명/함수명: snake_case
- 주석: 한국어
- 타입 힌트 사용 (`Literal`, `Tuple`, `Optional`)

## 아키텍처

```
[app.py / api.py] ──► preprocess_core.py
                          │
                          ├─ dicom_to_pil()  : DICOM → PIL (Window Level / Min-Max)
                          ├─ load_image()    : PNG/JPG/BMP → PIL
                          ├─ apply_clahe()   : CLAHE 대비 향상
                          └─ apply_edge()    : Canny 에지 검출
```

- `preprocess_core.py`: 새 알고리즘 추가 시 여기에 함수 작성 → `app.py` 모드 연결
- `app.py`: `@st.cache_data` 캐싱으로 대용량 파일 최적화
- `api.py`: Base64 PNG 반환

## DICOM 처리 참고

- `RescaleSlope/Intercept` 자동 적용
- `WindowCenter/Width` 리스트면 첫 번째 값 사용
- Window 정보 없으면 Min/Max fallback
