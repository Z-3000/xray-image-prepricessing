# api.py
from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.responses import JSONResponse
from preprocess_core import dicom_to_pil, apply_clahe, apply_edge
from PIL import Image
import base64
from io import BytesIO
from typing import Literal

# FastAPI 애플리케이션 초기화 (이 'app' 변수가 핵심입니다)
app = FastAPI(
    title="DICOM Preprocessing Service",
    description="DICOM 파일을 업로드하여 CLAHE, Canny Edge 등의 전처리를 적용하고 결과를 반환하는 API.",
    version="1.0.0"
)

# 유효한 전처리 모드 정의
ValidModes = Literal["원본만 보기", "CLAHE 대비 향상", "에지 검출(Canny)"]
ValidNormalizeModes = Literal["minmax", "window"]

@app.post("/preprocess")
async def preprocess_dicom(
    file: UploadFile = File(..., description="업로드할 DICOM 파일 (.dcm)"),
    mode: ValidModes = Form("원본만 보기", description="적용할 전처리 모드"),
    normalize_mode: ValidNormalizeModes = Form("minmax", description="원본 DICOM 시각화 모드 (minmax 또는 window)"),
    # CLAHE 파라미터 (기본값)
    clip_limit: float = Form(2.0, description="CLAHE 클립 한계 (Clip Limit)"),
    tile_grid_size: int = Form(8, description="CLAHE 타일 그리드 크기"),
    # Canny 파라미터 (기본값)
    canny_t1: int = Form(50, description="Canny Threshold 1 (낮은 임계값)"),
    canny_t2: int = Form(150, description="Canny Threshold 2 (높은 임계값)"),
):
    """
    업로드된 DICOM 파일에 대해 지정된 전처리 알고리즘을 적용하고, 
    결과 이미지를 Base64 인코딩된 문자열로 반환합니다.
    """
    
    # 1. 파일 내용 읽기
    try:
        file_bytes = await file.read()
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"파일 읽기 오류: {e}")

    # 2. DICOM 로딩 및 변환 (dicom_to_pil 함수 사용)
    try:
        original_img, dcm_data = dicom_to_pil(file_bytes, normalize_mode=normalize_mode)
    except ValueError as e:
        raise HTTPException(status_code=422, detail=f"DICOM 파일 처리 실패: {e}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"DICOM 처리 중 예상치 못한 오류 발생: {e}")

    # 3. 전처리 적용
    processed_img = original_img
    applied_params = {}
    
    if mode == "CLAHE 대비 향상":
        processed_img = apply_clahe(original_img, clip_limit=clip_limit, tile_grid_size=tile_grid_size)
        applied_params = {'clip_limit': clip_limit, 'tile_grid_size': tile_grid_size}
        
    elif mode == "에지 검출(Canny)":
        processed_img = apply_edge(original_img, threshold1=canny_t1, threshold2=canny_t2)
        applied_params = {'threshold1': canny_t1, 'threshold2': canny_t2}
        
    # 4. 결과 이미지를 PNG 바이트로 변환 후 Base64 인코딩
    output_buffer = BytesIO()
    processed_img.save(output_buffer, format="PNG")
    img_base64 = base64.b64encode(output_buffer.getvalue()).decode("utf-8")

    # 5. DICOM 메타데이터 정리
    wc_value = dcm_data.get('WindowCenter', 'N/A')
    ww_value = dcm_data.get('WindowWidth', 'N/A')
    if isinstance(wc_value, (list, tuple)): wc_value = wc_value[0]
    if isinstance(ww_value, (list, tuple)): ww_value = ww_value[0]
    
    metadata = {
        "patient_id": dcm_data.get('PatientID', 'N/A'),
        "modality": dcm_data.get('Modality', 'N/A'),
        "window_center": wc_value,
        "window_width": ww_value,
    }

    # 6. JSON 응답 반환
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