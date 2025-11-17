# 🔬 X-ray DICOM Preprocessing Viewer

OpenCV 기반 의료 영상(DICOM, X-ray) 전처리 알고리즘 비교 및 시각화 도구

<br>

## 📋 프로젝트 개요

의료 영상 분석을 위한 **전처리 파이프라인 시각화 도구**로, DICOM 및 일반 이미지(PNG/JPEG)에 다양한 전처리 알고리즘을 적용하고 Before/After를 비교할 수 있는 웹 애플리케이션입니다.

### 주요 기능
- **DICOM Window Level** 표준 시각화 지원
- **CLAHE**(Contrast Limited Adaptive Histogram Equalization) 대비 향상
- **Canny Edge Detection** 경계 검출
- 실시간 파라미터 튜닝 및 결과 비교
- DICOM 메타데이터 자동 추출 및 표시
- FastAPI 기반 REST API 제공

<br>

## 🛠️ 기술 스택

| 구분 | 기술 |
|------|------|
| Frontend | Streamlit |
| Backend | FastAPI |
| 이미지 처리 | OpenCV, Pillow |
| DICOM 처리 | pydicom |
| 언어 | Python 3.8+ |

<br>

## 📂 프로젝트 구조

```
.
├── app.py                 # Streamlit UI 메인 애플리케이션
├── api.py                 # FastAPI REST API 서버
├── preprocess_core.py     # 전처리 핵심 로직 (DICOM, CLAHE, Canny)
└── README.md
```

### 모듈 설명
- `app.py`: 웹 인터페이스 및 사용자 인터랙션 처리
- `preprocess_core.py`: 전처리 알고리즘 구현체 (재사용 가능한 순수 함수)
- `api.py`: HTTP 기반 이미지 전처리 서비스 (외부 연동 가능)

<br>

## 🚀 사용법

### 1. 환경 설정

```bash
# 필수 패키지 설치
pip install streamlit fastapi uvicorn pydicom pillow opencv-python numpy
```

### 2. Streamlit 앱 실행

```bash
streamlit run app.py
```
브라우저에서 `http://localhost:8501` 자동 실행됩니다.

### 3. FastAPI 서버 실행 (선택)

```bash
uvicorn api:app --reload
```
API 문서는 `http://localhost:8000/docs`에서 확인 가능합니다.

<br>

## 💡 활용 방법

### Streamlit 앱 사용 순서

1. **파일 업로드**: 좌측 사이드바에서 DICOM(.dcm) 또는 이미지 파일 업로드
2. **시각화 모드 선택** (DICOM 전용):
   - `Min/Max Normalization`: 전체 픽셀값 범위를 0-255로 스케일링
   - `DICOM Window Level`: 의료 표준 윈도우링 적용
3. **전처리 모드 선택**:
   - `View original`: 원본 이미지 확인
   - `Local Contrast(CLAHE)`: 국소 대비 향상
   - `Edge Detection (Canny)`: 경계 추출
4. **파라미터 튜닝**: 슬라이더로 실시간 조정
5. **결과 확인**: Before/After 탭에서 비교 분석

### FastAPI 사용 예시

```python
import requests

# DICOM 파일 전처리 요청
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
metadata = result["dicom_metadata"]
```

<br>

## 📊 전처리 알고리즘 설명

### CLAHE (Contrast Limited Adaptive Histogram Equalization)
- **용도**: 저대비 의료 영상의 국소 대비 향상
- **파라미터**:
  - `Clip Limit`: 대비 증폭 제한 (1.0-5.0, 기본값 2.0)
  - `Tile Grid Size`: 타일 크기 (4-16, 기본값 8)

### Canny Edge Detection
- **용도**: 해부학적 구조 경계 추출
- **파라미터**:
  - `Threshold 1`: 약한 에지 임계값 (0-200, 기본값 50)
  - `Threshold 2`: 강한 에지 임계값 (0-300, 기본값 150)

<br>

## 📌 주요 특징

### DICOM 처리
- `RescaleSlope/Intercept` 자동 적용
- Window Center/Width 기반 의료 표준 시각화
- 주요 메타데이터 자동 추출 (Patient ID, Modality 등)

### 확장성
- `preprocess_core.py`에 새 함수 추가 → `app.py`에 모드 연결
- FastAPI로 외부 시스템과 통합 가능
- Streamlit 캐싱으로 대용량 파일 처리 최적화

<br>

## 🔍 API 문서

### POST `/preprocess`

**Request**:
```json
{
  "file": "DICOM binary file",
  "mode": "CLAHE 대비 향상" | "에지 검출(Canny)" | "원본만 보기",
  "normalize_mode": "minmax" | "window",
  "clip_limit": 2.0,
  "tile_grid_size": 8,
  "canny_t1": 50,
  "canny_t2": 150
}
```

**Response**:
```json
{
  "status": "success",
  "mode": "CLAHE 대비 향상",
  "params": {"clip_limit": 2.0, "tile_grid_size": 8},
  "dicom_metadata": {
    "patient_id": "...",
    "modality": "CR",
    "window_center": 40,
    "window_width": 400
  },
  "image_data": {
    "mime_type": "image/png",
    "base64_string": "iVBORw0KGgo..."
  }
}
```

<br>

## 🎯 향후 개선 방향

- [ ] 추가 전처리 알고리즘 (Gaussian Blur, Morphology 등)
- [ ] 배치 처리 기능
- [ ] 전처리 파이프라인 저장/불러오기
- [ ] DICOM 시리즈 전체 처리
- [ ] GPU 가속 지원

<br>

## 📝 라이선스

MIT License

---

**개발**: 의료 영상 분석 교육 프로젝트  
**문의**: 프로젝트 관련 질문은 Issues 탭을 이용해주세요.
