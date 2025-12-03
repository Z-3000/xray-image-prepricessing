# api.py
"""
의료영상 전처리 REST API

DICOM 및 일반 이미지에 대한 전처리를 HTTP API로 제공합니다.
preprocess_core.py의 함수를 재사용하여 로직 중복을 방지합니다.

실행 방법:
    uvicorn api:app --reload

API 문서:
    http://localhost:8000/docs (Swagger UI)
"""
from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.responses import JSONResponse
from preprocess_core import dicom_to_pil, apply_clahe, apply_edge
import base64
from io import BytesIO
from typing import Literal

# FastAPI 앱 초기화
app = FastAPI(
    title="의료영상 전처리 API",
    description="DICOM/이미지 파일에 CLAHE, Canny Edge 전처리를 적용하고 Base64 PNG로 반환",
    version="1.0.0"
)

# 유효한 전처리 모드 정의
ValidModes = Literal["원본만 보기", "CLAHE 대비 향상", "에지 검출(Canny)"]
ValidNormalizeModes = Literal["minmax", "window"]

@app.post("/preprocess")
async def preprocess_dicom(
    file: UploadFile = File(..., description="DICOM 파일 (.dcm)"),
    mode: ValidModes = Form("원본만 보기", description="전처리 모드"),
    normalize_mode: ValidNormalizeModes = Form("minmax", description="정규화 방식"),
    clip_limit: float = Form(2.0, description="CLAHE clip limit (1.0~5.0)"),
    tile_grid_size: int = Form(8, description="CLAHE tile size (4~16)"),
    canny_t1: int = Form(50, description="Canny 하위 임계값"),
    canny_t2: int = Form(150, description="Canny 상위 임계값"),
):
    """
    DICOM 파일 전처리 API

    업로드된 DICOM 파일에 전처리를 적용하고 Base64 PNG로 반환합니다.

    Returns:
        - status: 처리 결과 ("success")
        - mode: 적용된 전처리 모드
        - params: 적용된 파라미터
        - dicom_metadata: DICOM 메타데이터 (patient_id, modality, window_center, window_width)
        - image_data: Base64 인코딩된 PNG 이미지
    """
    # Step 1: 파일 읽기
    try:
        file_bytes = await file.read()
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"파일 읽기 오류: {e}")

    # Step 2: DICOM → PIL 변환
    try:
        original_img, dcm_data = dicom_to_pil(file_bytes, normalize_mode=normalize_mode)
    except ValueError as e:
        raise HTTPException(status_code=422, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"처리 중 오류: {e}")

    # Step 3: 전처리 적용
    processed_img = original_img
    applied_params = {}

    if mode == "CLAHE 대비 향상":
        processed_img = apply_clahe(
            original_img,
            clip_limit=clip_limit,
            tile_grid_size=tile_grid_size
        )
        applied_params = {"clip_limit": clip_limit, "tile_grid_size": tile_grid_size}

    elif mode == "에지 검출(Canny)":
        processed_img = apply_edge(
            original_img,
            threshold1=canny_t1,
            threshold2=canny_t2
        )
        applied_params = {"threshold1": canny_t1, "threshold2": canny_t2}

    # Step 4: PNG → Base64 변환
    output_buffer = BytesIO()
    processed_img.save(output_buffer, format="PNG")
    img_base64 = base64.b64encode(output_buffer.getvalue()).decode("utf-8")

    # Step 5: 메타데이터 추출
    wc_value = dcm_data.get('WindowCenter', 'N/A')
    ww_value = dcm_data.get('WindowWidth', 'N/A')
    if isinstance(wc_value, (list, tuple)):
        wc_value = wc_value[0]
    if isinstance(ww_value, (list, tuple)):
        ww_value = ww_value[0]

    metadata = {
        "patient_id": dcm_data.get('PatientID', 'N/A'),
        "modality": dcm_data.get('Modality', 'N/A'),
        "window_center": wc_value,
        "window_width": ww_value,
    }

    # Step 6: JSON 응답
    return JSONResponse(content={
        "status": "success",
        "mode": mode,
        "params": applied_params,
        "dicom_metadata": metadata,
        "image_data": {
            "mime_type": "image/png",
            "base64_string": img_base64
        }
    })