# X-ray DICOM Preprocessing Viewer

OpenCV 기반 의료 영상(DICOM, X-ray) 전처리 알고리즘 비교 및 시각화 도구

## 프로젝트 개요

의료 영상 분석을 위한 **전처리 파이프라인 시각화 도구**입니다.
DICOM 및 일반 이미지(PNG/JPEG)에 다양한 전처리 알고리즘을 적용하고 Before/After를 비교할 수 있습니다.

### 주요 기능
- **DICOM Window Level**: 의료 표준 시각화 (RescaleSlope/Intercept 자동 적용)
- **CLAHE**: Contrast Limited Adaptive Histogram Equalization (저대비 영역 개선)
- **Canny Edge Detection**: 해부학적 구조 경계 추출
- **실시간 파라미터 튜닝**: 슬라이더로 즉시 결과 확인
- **REST API**: FastAPI 기반 외부 시스템 연동 지원

## 기술 스택

| 구분 | 기술 | 버전 |
|------|------|------|
| Frontend | Streamlit | 1.51.0 |
| Backend | FastAPI | 0.121.1 |
| 이미지 처리 | OpenCV, Pillow | 4.12.0, 12.0.0 |
| DICOM 처리 | pydicom | 3.0.1 |
| 언어 | Python | 3.8+ |

## 아키텍처

```
┌─────────────────────────────────────────────────────────────┐
│  사용자 브라우저                                              │
│       │                                                     │
│       ▼                                                     │
│  ┌─────────────┐     ┌─────────────┐     ┌─────────────┐   │
│  │  Streamlit  │     │preprocess_  │     │  FastAPI    │   │
│  │  (app.py)   │────▶│  core.py    │◀────│  (api.py)   │   │
│  │  웹 UI      │     │  핵심 로직   │     │  REST API   │   │
│  └─────────────┘     └─────────────┘     └─────────────┘   │
└─────────────────────────────────────────────────────────────┘
```

## 프로젝트 구조

```
open_cv_app/
├── app.py                 # Streamlit UI (파일 업로드, 파라미터 조절, Before/After)
├── api.py                 # FastAPI REST API (Base64 PNG 반환)
├── preprocess_core.py     # 핵심 로직 (DICOM 변환, CLAHE, Canny)
├── requirements.txt       # 의존성 목록
└── docs/                  # 문서
    ├── 00_포트폴리오_요약.md
    └── 01_프로젝트_학습자료.md
```

### 모듈 역할
| 모듈 | 역할 |
|------|------|
| `preprocess_core.py` | 순수 함수로 이미지 처리 로직 구현 (재사용성) |
| `app.py` | 웹 UI, `@st.cache_data` 캐싱으로 대용량 파일 최적화 |
| `api.py` | HTTP API, 외부 시스템 연동용 |

## 실행 방법

### 1. 환경 설정

```bash
# 가상환경 생성 및 활성화
python -m venv venv
venv\Scripts\activate  # Windows

# 패키지 설치
pip install -r requirements.txt
```

### 2. Streamlit 앱 실행

```bash
streamlit run app.py
# → http://localhost:8501
```

### 3. FastAPI 서버 실행 (선택)

```bash
uvicorn api:app --reload
# → http://localhost:8000/docs (Swagger UI)
```

## 사용 방법

### Streamlit 웹 UI

1. **파일 업로드**: 좌측 사이드바에서 DICOM(.dcm) 또는 PNG/JPG 업로드
2. **정규화 모드 선택**:
   - `Min/Max Normalization`: 전체 범위 스케일링
   - `DICOM Window Level`: 의료 표준 (특정 조직 강조)
3. **전처리 모드 선택**:
   - `View original`: 원본 확인
   - `Local Contrast(CLAHE)`: 대비 향상
   - `Edge Detection (Canny)`: 경계 추출
4. **파라미터 튜닝**: 슬라이더로 실시간 조정
5. **결과 확인**: Before/After 비교

### REST API 사용 예시

```python
import requests

with open("sample.dcm", "rb") as f:
    response = requests.post(
        "http://localhost:8000/preprocess",
        files={"file": f},
        data={
            "mode": "CLAHE 대비 향상",
            "normalize_mode": "window",
            "clip_limit": 2.0,
            "tile_grid_size": 8
        }
    )

result = response.json()
image_base64 = result["image_data"]["base64_string"]
```

## 전처리 알고리즘

### CLAHE (Contrast Limited Adaptive Histogram Equalization)
- **용도**: 저대비 의료 영상의 국소 대비 향상
- **파라미터**:
  - `Clip Limit`: 대비 증폭 제한 (1.0-5.0, 기본값 2.0)
  - `Tile Grid Size`: 타일 크기 (4-16, 기본값 8)

### Canny Edge Detection
- **용도**: 해부학적 구조 경계 추출
- **파라미터**:
  - `Threshold 1`: 하위 임계값 (0-200, 기본값 50)
  - `Threshold 2`: 상위 임계값 (0-300, 기본값 150)

### DICOM Window Level
- **용도**: 특정 조직 강조 (폐, 뼈, 연조직 등)
- **원리**: `[WC - WW/2, WC + WW/2]` 범위를 0-255로 매핑
- **처리**: RescaleSlope/Intercept 자동 적용, 다중값은 첫 번째 사용

## API 문서

### POST `/preprocess`

| 파라미터 | 타입 | 설명 |
|----------|------|------|
| file | File | DICOM/이미지 파일 |
| mode | string | "원본만 보기", "CLAHE 대비 향상", "에지 검출(Canny)" |
| normalize_mode | string | "minmax" 또는 "window" |
| clip_limit | float | CLAHE clip limit (1.0~5.0) |
| tile_grid_size | int | CLAHE tile size (4~16) |
| canny_t1, canny_t2 | int | Canny 임계값 |

**Response**: `{status, mode, params, dicom_metadata, image_data: {base64_string}}`

## 향후 개선 방향

- [ ] 추가 알고리즘 (Gaussian Blur, Morphology)
- [ ] 배치 처리 기능
- [ ] GPU 가속 지원

## 라이선스

MIT License
