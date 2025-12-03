# app.py
import streamlit as st
from io import BytesIO
# preprocess_core.py 파일이 같은 폴더에 있어야 합니다.
from preprocess_core import dicom_to_pil, load_image, apply_clahe, apply_edge
from PIL import Image

# 1. 페이지 기본 설정
st.set_page_config(
    page_title="의료 영상 전처리 시각화 도구",
    layout="wide",
    initial_sidebar_state="expanded"
)

# *****************************************************************
# 1) CSS (기존 그대로)
# *****************************************************************
custom_css = """
<style>

:root {
    --med-blue: #0066CC;       /* 포인트 의료 블루 */
    --med-blue-dark: #004A99;  /* 제목용 진한 블루 */
}

/* 전체 배경 (항상 밝은 테마 유지) */
.stApp {
    background-color: #FFFFFF !important;
    color: #333333;
}

/* 상단 헤더바 (선명한 의료청색) */
header {
    background-color: var(--med-blue) !important;
}
header * {
    color: #FFFFFF !important;
}

/* ------ 사이드바 스타일 영역 ------ */

/* 사이드바 접기 버튼 항상 표시 */
[data-testid="stSidebarCollapseButton"],
[data-testid="collapsedControl"],
button[kind="headerNoPadding"],
.stSidebar button[kind="header"],
section[data-testid="stSidebar"] > div:first-child button,
[data-testid="stSidebarNav"] button,
div[data-testid="stSidebarCollapsedControl"] {
    opacity: 1 !important;
    visibility: visible !important;
    display: flex !important;
}

/* 사이드바 영역 호버 시에만 보이는 버튼 강제 표시 */
section[data-testid="stSidebar"]::before,
[data-testid="stSidebarUserContent"]::before {
    opacity: 1 !important;
}

/* 사이드바 배경 */
.stSidebar {
    background-color: #E4F0FF !important;
    border-right: 1px solid #99C2FF !important;
}

/* 사이드바 전체 텍스트 색 */
.stSidebar * {
    color: #003366 !important;
}

/* FileUploader 박스를 흰색으로 변경 */
section[data-testid="stSidebar"] .stFileUploader {
    background-color: #FFFFFF !important;
    padding: 12px;
    border-radius: 10px;
    border: 1px solid #D0D8E3;
}

/* FileUploader 내부 텍스트 색 */
section[data-testid="stSidebar"] .stFileUploader * {
    color: #003366 !important;
}

/* FileUploader 버튼 */
section[data-testid="stSidebar"] .stFileUploader button {
    background-color: #FFFFFF !important;
    color: #003366 !important;
    border: 1px solid #99BBDD !important;
    border-radius: 8px !important;
}

/* ------ 텍스트/제목 스타일 ------ */

h1, h2, h3 {
    color: var(--med-blue-dark);
    font-weight: 600;
}

h1 {
    font-size: 1.9rem;
}

/* Info 박스 */
.stAlert.stAlert--info {
    border-left: 5px solid var(--med-blue);
    background-color: #F0F8FF;
}

/* 구분선 */
hr {
    border-top: 1px solid #D0E0F0;
}

/* Before/After 배지 */
.before-after-badge {
    background-color: var(--med-blue);
    color: #FFFFFF;
    padding: 6px 16px;
    border-radius: 6px;
    text-align: center;
    font-weight: 600;
    font-size: 0.95rem;
    display: inline-block;
    margin-bottom: 16px;
}

/* ------ 탭 메뉴 스타일 ------ */

/* 탭 컨테이너에 테두리 추가 */
.stTabs [data-baseweb="tab-list"] {
    border: 2px solid #D0E0F0 !important;
    border-radius: 8px !important;
    padding: 4px !important;
    background-color: #F8F9FA !important;
}

/* 활성 탭 스타일 */
.stTabs [data-baseweb="tab-list"] button[aria-selected="true"] {
    color: #0066CC !important;
    font-weight: 700 !important;
    border-bottom: none !important;  /* 이 줄 추가 또는 수정 */
}

/* 비활성 탭 스타일 */
.stTabs [data-baseweb="tab-list"] button[aria-selected="false"] {
    color: #999999 !important;
    font-weight: 400 !important;
    border-bottom: none !important;  /* 이 줄 추가 */
}

/* 모든 탭 버튼의 border 제거 */
.stTabs [data-baseweb="tab-list"] button {
    border: none !important;
    border-bottom: none !important;
}

/* 활성 탭 */
.stTabs [data-baseweb="tab-list"] button[aria-selected="true"] {
    color: #0066CC !important;
    font-weight: 700 !important;
    border: none !important;
    border-bottom: none !important;
}

/* 비활성 탭 */
.stTabs [data-baseweb="tab-list"] button[aria-selected="false"] {
    color: #999999 !important;
    font-weight: 400 !important;
    border: none !important;
    border-bottom: none !important;
}

/* 탭 컨테이너 하단 경계선 제거 */
.stTabs [data-baseweb="tab-border"] {
    display: none !important;
}

/* 탭 전체 하단 선 제거 */
.stTabs [data-baseweb="tab-highlight"] {
    display: none !important;
}

</style>
"""
st.markdown(custom_css, unsafe_allow_html=True)


# *****************************************************************
# 2) CSS: 라디오 / 슬라이더 색상 (기존 그대로)
# *****************************************************************
custom_css = """
<style>
:root {
    --med-blue: #0066CC;
    --med-blue-dark: #004A99;
    /* 라디오/슬라이더 등 전역 포인트 컬러 */
    --primary-color: #0066CC;
}

/* 전체 배경 (항상 밝은 테마 유지) */
.stApp {
    background-color: #FFFFFF !important;
    color: #333333;
}

/* 상단 헤더바 (선명한 의료청색) */
header {
    background-color: var(--med-blue) !important;
}
header * {
    color: #FFFFFF !important;
}

/* ------ 사이드바 스타일 영역 ------ */
.stSidebar {
    background-color: #E4F0FF !important; 
    border-right: 1px solid #99C2FF !important;
}

.stSidebar * {
    color: #003366 !important;
}

/* 라디오 버튼 체크 색상 */
.stSidebar .stRadio > div[role="radiogroup"] > label > div:first-child {
    background-color: #FFFFFF !important;
    border: 2px solid #0066CC !important;
}

.stSidebar .stRadio > div[role="radiogroup"] > label[data-baseweb="radio"] > div:first-child > div {
    background-color: #0066CC !important;
}

/* 슬라이더 전체 컨테이너 */
.stSidebar [data-testid="stSlider"] {
    padding: 10px 0;
}

/* 슬라이더 트랙 (전체 바) */
.stSidebar [data-testid="stSlider"] [data-baseweb="slider"] > div > div {
    background-color: #D0E0F0 !important;
}

/* 슬라이더 진행 바 (채워진 부분) */
.stSidebar [data-testid="stSlider"] [data-baseweb="slider"] > div > div > div {
    background-color: #0066CC !important;
}

/* 슬라이더 썸 (손잡이) */
.stSidebar [data-testid="stSlider"] [data-baseweb="slider"] [role="slider"] {
    background-color: #0066CC !important;
    border: 3px solid #FFFFFF !important;
    box-shadow: 0 2px 6px rgba(0, 102, 204, 0.3) !important;
}

/* 슬라이더 썸 호버 */
.stSidebar [data-testid="stSlider"] [data-baseweb="slider"] [role="slider"]:hover {
    background-color: #004A99 !important;
    box-shadow: 0 3px 10px rgba(0, 102, 204, 0.5) !important;
}

/* FileUploader 박스 */
section[data-testid="stSidebar"] .stFileUploader {
    background-color: #FFFFFF !important;
    padding: 12px;
    border-radius: 10px;
    border: 1px solid #D0D8E3;
}

section[data-testid="stSidebar"] .stFileUploader * {
    color: #003366 !important;
}

/* 활성 탭 스타일 */
.stTabs [data-baseweb="tab-list"] button[aria-selected="true"] {
    color: #0066CC !important;
    font-weight: 700 !important;
    border-bottom: none !important;  /* 3px solid 부분을 none으로 변경 */
}

section[data-testid="stSidebar"] .stFileUploader button {
    background-color: #FFFFFF !important;
    color: #003366 !important;
    border: 1px solid #99BBDD !important;
    border-radius: 8px !important;
}

/* 텍스트/제목 */
h1, h2, h3 {
    color: var(--med-blue-dark);
    font-weight: 600;
}

h1 {
    font-size: 1.9rem;
}

.stAlert.stAlert--info {
    border-left: 5px solid var(--med-blue);
    background-color: #F0F8FF;
}

hr {
    border-top: 1px solid #D0E0F0;
}

.before-after-badge {
    background-color: var(--med-blue);
    color: #FFFFFF;
    padding: 6px 16px;
    border-radius: 6px;
    text-align: center;
    font-weight: 600;
    font-size: 0.95rem;
    display: inline-block;
    margin-bottom: 16px;
}

/* 🔽 업로더 오버라이드 🔽 */
.stSidebar .stFileUploader * {
    background-color: #FFFFFF !important;
}
.stSidebar .stFileUploader > div {
    border: 1px solid #D0D8E0 !important;
    border-radius: 8px !important;
}

</style>
"""
st.markdown(custom_css, unsafe_allow_html=True)


# 2. 메인 제목 및 부제
st.title("폐렴 진단용 의료 영상 전처리 시각화 도구")
st.markdown("""
DICOM 및 일반 의료영상 이미지 파일에 대해 전처리 알고리즘(CLAHE, Canny Edge)을 실시간으로 시각화합니다.

- **DICOM**: 의료 영상 표준 포맷으로, 픽셀 데이터와 함께 환자 정보 등의 메타데이터를 포함합니다.
- **지원 파일 형식**: .dcm (DICOM), .png, .jpg, .jpeg, .bmp
""")
st.markdown("---")


# *****************************************************************
# 3. 사이드바: 파일 업로드 & 전처리 설정
# *****************************************************************
st.sidebar.header("영상 파일 업로드")

uploaded_file = st.sidebar.file_uploader(
    "의료 영상 파일 선택",
    type=["dcm", "png", "jpg", "jpeg", "bmp"]
)

# DICOM 정규화/시각화 모드 선택 (DICOM에만 의미)
st.sidebar.markdown("---")
st.sidebar.subheader("이미지 로딩 및 전처리 모드")
normalize_mode = st.sidebar.radio(
    "이미지 로딩 방식",
    [
        "minmax",  # Min/Max Normalization (일반 보기)
        "window"   # DICOM Window Level (의료 표준)
    ],
    format_func=lambda x: "Min/Max Normalization (일반 보기)" if x == "minmax" else "DICOM Window Level (의료 표준)"
)
st.sidebar.markdown("---")

# 전처리 모드 선택
mode = st.sidebar.radio(
    "전처리 모드 선택",
    ["View original", "Local Contrast(CLAHE)", "Edge Detection (Canny)"]
)

st.sidebar.markdown("---")
st.sidebar.subheader("전처리 파라미터 튜닝")

# 파라미터: CLAHE
params = {}
if mode == "Local Contrast(CLAHE)":
    st.sidebar.markdown("##### CLAHE 설정")
    clip_limit = st.sidebar.slider("Clip Limit(클립 한계)", 1.0, 5.0, 2.0, 0.1)
    tile_grid = st.sidebar.slider("Tile Grid Size(타일 그리드 크기)", 4, 16, 8, 1)
    params = {'clip_limit': clip_limit, 'tile_grid_size': tile_grid}

# 파라미터: Canny
elif mode == "Edge Detection (Canny)":
    st.sidebar.markdown("##### Canny Edge 설정")
    canny_t1 = st.sidebar.slider("Threshold 1 (낮은 임계값)", 0, 200, 50, 5)
    canny_t2 = st.sidebar.slider("Threshold 2 (높은 임계값)", 0, 300, 150, 5)
    params = {'threshold1': canny_t1, 'threshold2': canny_t2}

# 파라미터: 원본 보기
else:
    st.sidebar.markdown(
        "<p style='font-size: 14px; color: #003366;'>선택된 모드에서는 파라미터 튜닝이 필요하지 않습니다.</p>",
        unsafe_allow_html=True
    )
    params = {}


# *****************************************************************
# 4. 메인 콘텐츠: 이미지 로딩 & 전처리
# *****************************************************************
if uploaded_file is None:
    st.info("""
    좌측 패널에서 이미지 파일을 업로드하고 전처리 옵션을 선택하세요
      
    **이미지 로딩**
    - **Min/Max Normalization**: 전체 이미지의 최소/최대 픽셀값을 0-255로 정규화
    - **DICOM Window Level**: 특정 조직을 강조하는 의료 영상 표준 방식, DICOM 이미지의 메타데이터에서 설정값을 가져옵니다.

    **전처리 모드**
    - **Local Contrast (CLAHE)**: 타일 단위로 국소 대비를 향상시켜 저대비 영역의 세부사항 개선
    - **Edge Detection (Canny)**: 해부학적 구조의 경계선을 추출하여 윤곽 분석
                """)
else:
    file_name = uploaded_file.name
    lower_name = file_name.lower()
    is_dicom = lower_name.endswith(".dcm")

    # 공통: 파일 바이트
    file_bytes = uploaded_file.getvalue()
    file_size = uploaded_file.size

    # 4.1. DICOM / 일반 이미지 분기 로딩
    @st.cache_data
    def load_dicom_image(file_bytes: bytes, norm_mode: str):
        """DICOM 로딩 (dicom_to_pil 사용)"""
        img, dcm = dicom_to_pil(file_bytes, norm_mode)
        return img, dcm

    @st.cache_data
    def load_standard_image(file_bytes: bytes, name: str, size: int):
        """PNG/JPEG/BMP 등 일반 이미지 로딩"""
        img = load_image(file_bytes)
        meta = {
            "파일명 (File Name)": name,
            "형식 (Format)": img.format if img.format is not None else "N/A",
            "모드 (Mode)": img.mode,
            "이미지 크기 (W x H)": f"{img.width} x {img.height}",
            "파일 크기 (Bytes)": size,
        }
        return img, meta

    try:
        if is_dicom:
            original_img, dcm_data = load_dicom_image(file_bytes, normalize_mode)
            basic_meta = None
        else:
            original_img, basic_meta = load_standard_image(file_bytes, file_name, file_size)
            dcm_data = None
    except ValueError as e:
        st.error(f"⚠️ 파일 처리 중 오류가 발생했습니다: {e}")
        st.stop()
    except Exception as e:
        st.error(f"예상치 못한 오류 발생: {e}")
        st.stop()

    # 4.2. 전처리 적용 (DICOM/일반 공통)
    @st.cache_data
    def apply_preprocess(
        img: Image.Image,
        mode: str,
        params: dict,
        name: str,
        size: int,
        norm_mode: str,
        is_dicom_flag: bool
    ):
        """선택된 모드와 파라미터를 적용하여 이미지 처리"""
        if mode == "Local Contrast(CLAHE)":
            return apply_clahe(img, params.get('clip_limit', 2.0), params.get('tile_grid_size', 8))
        elif mode == "Edge Detection (Canny)":
            return apply_edge(img, threshold1=params.get('threshold1', 50), threshold2=params.get('threshold2', 150))
        return img

    processed_img = apply_preprocess(
        original_img,
        mode,
        params,
        file_name,
        file_size,
        normalize_mode,
        is_dicom
    )

    # 4.3. 탭 구성
    tab1, tab2 = st.tabs(["Before / After 비교", "이미지정보"])

    # -----------------
    # TAB 1: Before / After
    # -----------------
    with tab1:
        col1, col2 = st.columns(2)

        if is_dicom:
            caption_text = (
                "DICOM Window Level (의료 표준)"
                if normalize_mode == 'window'
                else "Min/Max Normalization (일반 보기)"
            )
        else:
            caption_text = "일반 이미지 (PNG/JPEG/BMP)"

        with col1:
            st.subheader("Before: 원본 이미지")
            st.image(original_img, caption=f"로딩 방식: {caption_text}", use_container_width=True)

        with col2:
            st.subheader(f"After: {mode}")
            st.image(processed_img, caption=f"적용 파라미터: {params}", use_container_width=True)

    # -----------------
    # TAB 2: 설명 & 메타데이터
    # -----------------
    with tab2:

        # 메타데이터 영역
        if is_dicom and dcm_data is not None:

            wc_value = dcm_data.get('WindowCenter', 'N/A')
            ww_value = dcm_data.get('WindowWidth', 'N/A')

            if isinstance(wc_value, (list, tuple)):
                wc_value = wc_value[0]
            if isinstance(ww_value, (list, tuple)):
                ww_value = ww_value[0]

            meta_data = {
                "환자 ID (Patient ID)": str(dcm_data.get('PatientID', 'N/A')),
                "이미지 크기 (Rows/Cols)": f"{dcm_data.get('Rows', 'N/A')} x {dcm_data.get('Columns', 'N/A')}",
                "비트 수 (Bits Stored)": str(dcm_data.get('BitsStored', 'N/A')),
                "Window Center": str(wc_value),
                "Window Width": str(ww_value),
            }

            # 데이터를 HTML 테이블로 변환
            table_html = """
            <style>
            .meta-table {
                width: 100%;
                border-collapse: collapse;
                background-color: white;
            }
            .meta-table td {
                padding: 12px;
                border: 1px solid #B3D9FF;
                color: #333333;
            }
            .meta-table td:first-child {
                font-weight: 600;
                background-color: #F0F8FF;
            }
            </style>
            <table class="meta-table">
            """
            for key, value in meta_data.items():
                table_html += f"<tr><td>{key}</td><td>{value}</td></tr>"
            table_html += "</table>"

            st.markdown(table_html, unsafe_allow_html=True)

            if normalize_mode == 'window':
                st.info(
                    f"현재 이미지는 DICOM 파일에 명시된 Window Center ({wc_value}) 및 "
                    f"Width ({ww_value})를 적용하여 시각화되었습니다. "
                    "이는 실제 임상 뷰어의 동작과 유사합니다."
                )
            else:
                st.info(
                    "현재 이미지는 Min/Max Normalization을 적용하여 픽셀을 0-255 범위로 스케일링했습니다. "
                    
                )
        else:
            # 일반 PNG/JPEG/BMP 이미지 메타데이터
            if basic_meta is not None:
                # HTML 테이블로 변환
                table_html = """
                <style>
                .meta-table {
                    width: 100%;
                    border-collapse: collapse;
                    background-color: white;
                }
                .meta-table td {
                    padding: 12px;
                    border: 1px solid #B3D9FF;
                    color: #333333;
                }
                .meta-table td:first-child {
                    font-weight: 600;
                    background-color: #F0F8FF;
                }
                </style>
                <table class="meta-table">
                """
                for key, value in basic_meta.items():
                    table_html += f"<tr><td>{key}</td><td>{value}</td></tr>"
                table_html += "</table>"
                
                st.markdown(table_html, unsafe_allow_html=True)
                st.info("일반 이미지의 경우 DICOM 메타데이터 대신 파일/해상도 기반 기본 정보를 제공합니다.")
            else:
                st.write("메타데이터를 불러올 수 없습니다.")