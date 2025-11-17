# preprocess_core.py
import pydicom
import numpy as np
import cv2
from PIL import Image
from io import BytesIO
from typing import Tuple, Literal, Optional

# 타입 힌트를 위한 정의
NormalizationMode = Literal["minmax", "window"]

def apply_window_level(img_array: np.ndarray, window_center: float, window_width: float) -> np.ndarray:
    """
    DICOM Window Level (Center/Width)을 사용하여 픽셀 데이터를 0-255 범위로 변환합니다.
    """
    if window_width <= 0:
        # Window Width가 0 이하일 경우 검은 이미지 반환
        return np.zeros(img_array.shape, dtype=np.uint8)

    # 윈도우링 공식 적용을 위한 min/max 값 계산
    min_val = window_center - (window_width / 2.0)
    max_val = window_center + (window_width / 2.0)

    # 클리핑 및 0-255 스케일링
    windowed_img = np.clip(img_array, min_val, max_val)
    windowed_img = (windowed_img - min_val) / window_width * 255.0
    
    return windowed_img.astype(np.uint8)

def load_image(file_bytes: bytes) -> Image.Image:
    """
    일반 이미지 파일(PNG, JPG, BMP 등)을 RGB PIL 이미지로 로드
    """
    try:
        img = Image.open(BytesIO(file_bytes)).convert("RGB")
        return img
    except Exception as e:
        raise ValueError(f"이미지 파일 처리 실패: {e}")

def dicom_to_pil(file_bytes: bytes, normalize_mode: NormalizationMode = "minmax") -> Tuple[Image.Image, pydicom.Dataset]:
    """업로드된 DICOM 바이트 → 표준화된 PIL 이미지(RGB, 0-255) 및 DICOM 데이터셋으로 변환"""
    try:
        dcm = pydicom.dcmread(BytesIO(file_bytes))
        img_raw = dcm.pixel_array.astype(np.float32)

        # Rescale Slope/Intercept 적용
        if 'RescaleSlope' in dcm and 'RescaleIntercept' in dcm:
            slope = float(dcm.RescaleSlope)
            intercept = float(dcm.RescaleIntercept)
            img = img_raw * slope + intercept
        else:
            img = img_raw

        img_normalized = None
        
        # Window Level 시각화 모드 적용
        if normalize_mode == "window":
            wc = dcm.get('WindowCenter', None)
            ww = dcm.get('WindowWidth', None)
            if isinstance(wc, (list, tuple)): wc = wc[0]
            if isinstance(ww, (list, tuple)): ww = ww[0]
            
            if wc is not None and ww is not None and float(ww) > 0:
                img_normalized = apply_window_level(img, float(wc), float(ww))
            else:
                normalize_mode = "minmax" # Windowing 정보가 없으면 Min/Max로 대체
                        
        # Min/Max Normalization (일반 보기 또는 Fallback)
        if img_normalized is None or normalize_mode == "minmax":
            img_normalized = img - img.min()
            max_val = img_normalized.max()
            if max_val > 0:
                img_normalized = (img_normalized / max_val) * 255.0
            img_normalized = img_normalized.astype(np.uint8)


        # 단일 채널(Gray) 이미지를 RGB로 변환
        if img_normalized.ndim == 2:
            img_rgb = cv2.cvtColor(img_normalized, cv2.COLOR_GRAY2RGB)
        elif img_normalized.ndim == 3 and img_normalized.shape[2] == 1:
            img_rgb = cv2.cvtColor(img_normalized.squeeze(2), cv2.COLOR_GRAY2RGB)
        else:
            img_rgb = img_normalized

        return Image.fromarray(img_rgb), dcm
    except Exception as e:
        raise ValueError(f"DICOM 파일 처리 실패: {e}")

def apply_clahe(pil_img: Image.Image, clip_limit: float = 2.0, tile_grid_size: int = 8) -> Image.Image:
    """
    CLAHE (Contrast Limited Adaptive Histogram Equalization) 적용
    """
    if tile_grid_size < 1: tile_grid_size = 1
    
    img = np.array(pil_img)
    gray = cv2.cvtColor(img, cv2.COLOR_RGB2GRAY)
    
    # CLAHE 객체 생성 및 적용
    clahe = cv2.createCLAHE(clipLimit=clip_limit, tileGridSize=(tile_grid_size, tile_grid_size))
    cl = clahe.apply(gray)
    
    # 결과 이미지를 다시 RGB로 변환하여 반환
    cl_rgb = cv2.cvtColor(cl, cv2.COLOR_GRAY2RGB)
    return Image.fromarray(cl_rgb)

def apply_edge(pil_img: Image.Image, threshold1: int = 50, threshold2: int = 150, method: str = "canny") -> Image.Image:
    """
    에지 검출 (Canny) 적용
    """
    img = np.array(pil_img)
    gray = cv2.cvtColor(img, cv2.COLOR_RGB2GRAY)
    
    # Canny 에지 검출 적용
    if method == "canny":
        edges = cv2.Canny(gray, threshold1, threshold2)
    else:
        edges = cv2.Canny(gray, threshold1, threshold2) 
    
    # 에지 검출 결과(단일 채널)를 RGB로 변환
    edges_rgb = cv2.cvtColor(edges, cv2.COLOR_GRAY2RGB)
    return Image.fromarray(edges_rgb)