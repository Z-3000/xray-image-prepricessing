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
    
}

/* 비활성 탭 스타일 */
.stTabs [data-baseweb="tab-list"] button[aria-selected="false"] {
    color: #999999 !important;
    font-weight: 400 !important;
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
    border-bottom: 3px solid #004A99 !important;
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
st.title("X-ray DICOM / Image Preprocessing Viewer")
st.markdown("""
OpenCV 기반으로 전처리 알고리즘의 효과를 비교 사전에 확인하고,  
DICOM Window Level 및 일반 PNG/JPEG 이미지에 대해 시각화를 지원합니다.
""")
st.markdown("---")


# *****************************************************************
# 3. 사이드바: 파일 업로드 & 전처리 설정
# *****************************************************************
st.sidebar.header("의료 영상 파일 업로드 (DICOM / PNG / JPEG)")

uploaded_file = st.sidebar.file_uploader(
    "의료 영상 파일 선택",
    type=["dcm", "png", "jpg", "jpeg", "bmp"]
)

# DICOM 정규화/시각화 모드 선택 (DICOM에만 의미)
st.sidebar.markdown("---")
st.sidebar.subheader("DICOM 시각화 모드 (DICOM 파일일 때만 적용)")
normalize_mode = st.sidebar.radio(
    "원본 이미지 로딩 방식",
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
    st.info("좌측 패널에서 DICOM 또는 PNG/JPEG 파일을 업로드하고 전처리 옵션을 선택하세요.")
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
    tab1, tab2 = st.tabs(["Before / After 비교", "알고리즘 설명 및 메타데이터"])

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
            st.subheader("원본 이미지 (Original)")
            st.image(original_img, caption=f"로딩 방식: {caption_text}", use_container_width=True)

        with col2:
            st.subheader(f"전처리 결과: {mode}")
            st.image(processed_img, caption=f"적용 파라미터: {params}", use_container_width=True)

    # -----------------
    # TAB 2: 설명 & 메타데이터
    # -----------------
    with tab2:
        st.header("알고리즘 및 프로젝트 노트")
        st.markdown("---")

        # 전처리 모드 설명
        if mode == "Local Contrast(CLAHE)":
            st.markdown("""
                ### CLAHE (Contrast Limited Adaptive Histogram Equalization)
                - **목표:** 의료 영상(특히 X-ray)의 국소 대비(contrast)를 향상시켜 병변이나 구조를 더 잘 보이게 함
                - **작동 원리:** 이미지 전체가 아닌 작은 타일(Tile) 단위로 히스토그램 평활화 수행  
                  `Clip Limit`로 대비 증폭을 제한해 과도한 노이즈 발생을 방지
                - **활용:** 낮은 대비의 의료 영상에서 딥러닝/머신러닝 입력 품질을 개선하는 전처리로 사용 가능
            """)
        elif mode == "Edge Detection (Canny)":
            st.markdown("""
                ### Canny Edge Detection
                - **목표:** 해부학적 구조나 병변의 경계를 선명하게 추출
                - **작동 원리:** 가우시안 블러로 노이즈 제거 → 그래디언트 계산 →  
                  두 개의 임계값(Threshold 1, 2)으로 약한/강한 에지를 분류해 최종 에지 결정
                - **활용:** 윤곽 기반 특징추출, 세그멘테이션, 규칙기반 분석(Rule-based) 등에 활용 가능
            """)
        else:
            st.markdown("""
                원본 영상 로딩 및 기본 메타데이터 확인용 모드입니다.  
                좌측 사이드바에서 다른 전처리 모드를 선택하여 효과를 비교할 수 있습니다.
            """)

        st.markdown("---")

        # 메타데이터 영역
        if is_dicom and dcm_data is not None:
            st.subheader("DICOM 메타데이터 (주요 Tag)")

            wc_value = dcm_data.get('WindowCenter', 'N/A')
            ww_value = dcm_data.get('WindowWidth', 'N/A')

            if isinstance(wc_value, (list, tuple)):
                wc_value = wc_value[0]
            if isinstance(ww_value, (list, tuple)):
                ww_value = ww_value[0]

            meta_data = {
                "환자 ID (Patient ID)": str(dcm_data.get('PatientID', 'N/A')),
                "검사 종류 (Modality)": str(dcm_data.get('Modality', 'N/A')),
                "연구 설명 (Study Desc)": str(dcm_data.get('StudyDescription', 'N/A')),
                "획득 날짜 (Acquisition Date)": str(dcm_data.get('AcquisitionDate', 'N/A')),
                "이미지 크기 (Rows/Cols)": f"{dcm_data.get('Rows', 'N/A')} x {dcm_data.get('Columns', 'N/A')}",
                "비트 수 (Bits Stored)": str(dcm_data.get('BitsStored', 'N/A')),
                "Window Center": str(wc_value),
                "Window Width": str(ww_value),
                "Rescale Slope/Intercept": f"{dcm_data.get('RescaleSlope', '1.0')} / {dcm_data.get('RescaleIntercept', '0.0')}",
            }

            st.dataframe(
                list(meta_data.items()),
                column_config={0: "Tag", 1: "Value"},
                hide_index=True,
                use_container_width=True
            )

            if normalize_mode == 'window':
                st.info(
                    f"현재 이미지는 DICOM 파일에 명시된 Window Center ({wc_value}) 및 "
                    f"Width ({ww_value})를 적용하여 시각화되었습니다. "
                    "이는 실제 임상 뷰어의 동작과 유사합니다."
                )
            else:
                st.info(
                    "현재 이미지는 Min/Max Normalization을 적용하여 픽셀을 0-255 범위로 스케일링했습니다. "
                    "DICOM Window Level (의료 표준) 모드와 비교하여 차이를 확인할 수 있습니다."
                )

            with st.expander("전체 DICOM 정보 보기"):
                try:
                    st.json(dcm_data.to_json_dict())
                except Exception:
                    st.text(str(dcm_data))

        else:
            # 일반 PNG/JPEG/BMP 이미지 메타데이터
            st.subheader("이미지 메타데이터 (일반 이미지)")
            if basic_meta is not None:
                st.dataframe(
                    list(basic_meta.items()),
                    column_config={0: "항목", 1: "값"},
                    hide_index=True,
                    use_container_width=True
                )
                st.info("일반 이미지의 경우 DICOM Tag 대신 파일/해상도 기반 기본 정보를 제공합니다.")
            else:
                st.write("메타데이터를 불러올 수 없습니다.")

        with st.expander("프로젝트 구조 및 유지보수 메모"):
            st.markdown("""
                이 애플리케이션은 다음과 같이 모듈을 분리했습니다.
                - **app.py**: Streamlit UI 및 입출력/레이아웃
                - **preprocess_core.py**: DICOM 윈도우링, CLAHE, Canny 등 전처리 핵심 로직

                전처리 알고리즘을 바꾸거나 추가하고 싶다면 `preprocess_core.py`에 새로운 함수를 추가한 뒤  
                `app.py`의 `apply_preprocess()`에 분기 로직을 추가하는 방식으로 확장할 수 있습니다.
            """)