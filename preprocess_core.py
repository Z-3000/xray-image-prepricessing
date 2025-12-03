# preprocess_core.py
"""
의료영상 전처리 핵심 모듈

이 모듈은 DICOM 및 일반 이미지에 대한 전처리 알고리즘을 제공합니다.
Streamlit UI(app.py)와 FastAPI(api.py)에서 공통으로 사용됩니다.

주요 기능:
    - DICOM → PIL 변환 (Window Level / Min-Max 정규화)
    - PNG/JPG/BMP → PIL 변환
    - CLAHE 대비 향상
    - Canny 에지 검출
"""
import pydicom
import numpy as np
import cv2
from PIL import Image
from io import BytesIO
from typing import Tuple, Literal

# 타입 힌트 정의
NormalizationMode = Literal["minmax", "window"]


def apply_window_level(
    img_array: np.ndarray,
    window_center: float,
    window_width: float
) -> np.ndarray:
    """
    DICOM Window Level 적용

    의료영상에서 특정 조직을 강조하기 위해 픽셀값 범위를 조절합니다.
    예: 폐(WC=-600, WW=1500), 뼈(WC=300, WW=1500)

    Args:
        img_array: 입력 이미지 배열 (RescaleSlope/Intercept 적용 후)
        window_center: 관심 영역의 중심 픽셀값
        window_width: 표시할 픽셀값 범위

    Returns:
        0-255 범위로 정규화된 uint8 배열
    """
    if window_width <= 0:
        return np.zeros(img_array.shape, dtype=np.uint8)

    # Window 범위 계산: [WC - WW/2, WC + WW/2]
    min_val = window_center - (window_width / 2.0)
    max_val = window_center + (window_width / 2.0)

    # 범위 밖 값 클리핑 후 0-255로 스케일링
    windowed_img = np.clip(img_array, min_val, max_val)
    windowed_img = (windowed_img - min_val) / window_width * 255.0

    return windowed_img.astype(np.uint8)

def load_image(file_bytes: bytes) -> Image.Image:
    """
    일반 이미지 파일을 RGB PIL 이미지로 로드

    Args:
        file_bytes: PNG/JPG/BMP 파일의 바이트 데이터

    Returns:
        RGB 모드의 PIL Image 객체

    Raises:
        ValueError: 이미지 파일 파싱 실패 시
    """
    try:
        img = Image.open(BytesIO(file_bytes)).convert("RGB")
        return img
    except Exception as e:
        raise ValueError(f"이미지 파일 처리 실패: {e}")

def dicom_to_pil(
    file_bytes: bytes,
    normalize_mode: NormalizationMode = "minmax"
) -> Tuple[Image.Image, pydicom.Dataset]:
    """
    DICOM 파일을 PIL 이미지로 변환

    DICOM 표준에 따라 RescaleSlope/Intercept를 적용하고,
    선택한 정규화 모드로 0-255 범위의 이미지를 생성합니다.

    Args:
        file_bytes: DICOM 파일의 바이트 데이터
        normalize_mode: 정규화 방식
            - "minmax": 전체 픽셀값 범위를 0-255로 스케일링
            - "window": DICOM 메타데이터의 Window Center/Width 적용

    Returns:
        (PIL.Image, pydicom.Dataset) 튜플
            - RGB 모드의 PIL Image
            - 원본 DICOM Dataset (메타데이터 접근용)

    Raises:
        ValueError: DICOM 파일 파싱 실패 시
    """
    try:
        dcm = pydicom.dcmread(BytesIO(file_bytes))
        img_raw = dcm.pixel_array.astype(np.float32)

        # Step 1: RescaleSlope/Intercept 적용 (DICOM 표준)
        # CT/MR 등에서 저장된 픽셀값을 실제 물리값(HU 등)으로 변환
        if 'RescaleSlope' in dcm and 'RescaleIntercept' in dcm:
            slope = float(dcm.RescaleSlope)
            intercept = float(dcm.RescaleIntercept)
            img = img_raw * slope + intercept
        else:
            img = img_raw

        # Step 2: 정규화 (Window Level 또는 Min/Max)
        img_normalized = None

        if normalize_mode == "window":
            # Window Center/Width가 다중값일 경우 첫 번째 사용
            wc = dcm.get('WindowCenter', None)
            ww = dcm.get('WindowWidth', None)
            if isinstance(wc, (list, tuple)):
                wc = wc[0]
            if isinstance(ww, (list, tuple)):
                ww = ww[0]

            if wc is not None and ww is not None and float(ww) > 0:
                img_normalized = apply_window_level(img, float(wc), float(ww))
            else:
                # Window 정보 없으면 Min/Max로 fallback
                normalize_mode = "minmax"

        # Min/Max 정규화 (기본값 또는 fallback)
        if img_normalized is None or normalize_mode == "minmax":
            img_normalized = img - img.min()
            max_val = img_normalized.max()
            if max_val > 0:
                img_normalized = (img_normalized / max_val) * 255.0
            img_normalized = img_normalized.astype(np.uint8)

        # Step 3: 그레이스케일 → RGB 변환 (Streamlit/FastAPI 호환)
        if img_normalized.ndim == 2:
            img_rgb = cv2.cvtColor(img_normalized, cv2.COLOR_GRAY2RGB)
        elif img_normalized.ndim == 3 and img_normalized.shape[2] == 1:
            img_rgb = cv2.cvtColor(img_normalized.squeeze(2), cv2.COLOR_GRAY2RGB)
        else:
            img_rgb = img_normalized

        return Image.fromarray(img_rgb), dcm

    except Exception as e:
        raise ValueError(f"DICOM 파일 처리 실패: {e}")

def apply_clahe(
    pil_img: Image.Image,
    clip_limit: float = 2.0,
    tile_grid_size: int = 8
) -> Image.Image:
    """
    CLAHE (Contrast Limited Adaptive Histogram Equalization) 적용

    이미지를 타일로 나눠 각 영역별로 히스토그램 평활화를 수행합니다.
    clip_limit으로 과도한 대비 증폭을 제한하여 노이즈 증폭을 방지합니다.

    Args:
        pil_img: 입력 PIL 이미지 (RGB)
        clip_limit: 대비 제한 임계값 (기본값 2.0, 범위 1.0~5.0 권장)
            - 높을수록 대비 증가, 낮을수록 노이즈 억제
        tile_grid_size: 타일 크기 (기본값 8x8)
            - 작을수록 국소적 대비 향상, 클수록 전역적 효과

    Returns:
        CLAHE가 적용된 RGB PIL 이미지
    """
    if tile_grid_size < 1:
        tile_grid_size = 1

    img = np.array(pil_img)
    gray = cv2.cvtColor(img, cv2.COLOR_RGB2GRAY)

    # CLAHE 객체 생성 및 적용
    clahe = cv2.createCLAHE(
        clipLimit=clip_limit,
        tileGridSize=(tile_grid_size, tile_grid_size)
    )
    cl = clahe.apply(gray)

    # RGB로 변환하여 반환
    cl_rgb = cv2.cvtColor(cl, cv2.COLOR_GRAY2RGB)
    return Image.fromarray(cl_rgb)

def apply_edge(
    pil_img: Image.Image,
    threshold1: int = 50,
    threshold2: int = 150
) -> Image.Image:
    """
    Canny 에지 검출 적용

    이미지에서 경계선(에지)을 추출합니다.
    의료영상에서 해부학적 구조의 윤곽을 확인하는 데 유용합니다.

    Args:
        pil_img: 입력 PIL 이미지 (RGB)
        threshold1: 하위 임계값 (기본값 50)
            - 이 값 이하의 그래디언트는 에지 아님
        threshold2: 상위 임계값 (기본값 150)
            - 이 값 이상의 그래디언트는 확실한 에지
            - 사이값은 강한 에지와 연결된 경우에만 에지로 인정

    Returns:
        에지가 검출된 RGB PIL 이미지 (흰색 에지, 검은색 배경)
    """
    img = np.array(pil_img)
    gray = cv2.cvtColor(img, cv2.COLOR_RGB2GRAY)

    # Canny 에지 검출
    edges = cv2.Canny(gray, threshold1, threshold2)

    # RGB로 변환하여 반환
    edges_rgb = cv2.cvtColor(edges, cv2.COLOR_GRAY2RGB)
    return Image.fromarray(edges_rgb)