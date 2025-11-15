# app.py
import streamlit as st
# preprocess_core.py 파일이 같은 폴더에 있어야 합니다.
from preprocess_core import dicom_to_pil, apply_clahe, apply_edge
from PIL import Image

# 1. 페이지 기본 설정
st.set_page_config(
    page_title="의료 영상 전처리 시각화 도구",
    layout="wide",
    initial_sidebar_state="expanded"
)

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
# CUSTOM CSS: 의료/병원 테마 (블루/화이트) 적용 및 농도 조정
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

/* 전체 배경: 항상 밝은 테마 유지 */
.stApp {
    background-color: #FFFFFF !important;
    color: #333333;
}

/* 상단 바 색상: 의료 블루 */
header {
    background-color: var(--med-blue) !important;
}
header * {
    color: #FFFFFF !important;
}

/* Sidebar 배경 */
.stSidebar {
    background-color: #E4F0FF !important; 
    border-right: 1px solid #99C2FF;
}

/* 사이드바 텍스트 색 */
.stSidebar * {
    color: #003366 !important;
}

/* 제목 색/크기 */
h1, h2, h3 {
    color: var(--med-blue-dark);
    font-weight: 600;
}
h1 {
    font-size: 1.9rem;
}

/* Info Box Styling */
.stAlert.stAlert--info {
    border-left: 5px solid var(--med-blue);
    background-color: #F0F8FF;
}

/* Markdown Separator */
hr {
    border-top: 1px solid #D0E0F0;
}

/* File Uploader 버튼 색 (버튼만) */
.stFileUploader button {
    background-color: #FFFFFF !important;
    color: #003366 !important;
    border-radius: 8px !important;
    border: 1px solid #99BBDD !important;
}

/* 중앙 Before / After 배지 */
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


/* 🔽 여기서부터 업로더 스타일 오버라이드 🔽 */

/* 업로더 안의 모든 요소 배경을 흰색으로 */
.stSidebar .stFileUploader * {
    background-color: #FFFFFF !important;
}

/* 업로더 전체 카드 모양 */
.stSidebar .stFileUploader > div {
    border: 1px solid #D0D8E0 !important;
    border-radius: 10px !important;
    padding: 12px !important;
}

/* 업로드 버튼 스타일 */
.stSidebar .stFileUploader button {
    background-color: #FFFFFF !important;
    color: #003366 !important;
    border: 1px solid #99BBDD !important;
    border-radius: 8px !important;
}
/* 🔼 여기까지 🔼 */

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
st.markdown(custom_css, unsafe_allow_html=True)
# 2. 메인 제목 및 부제
st.title("🔬 X-ray DICOM Image Preprocessing Viewer")
st.markdown("""
OpenCV 기반으로 전처리 알고리즘의 효과를 비교 사전에 확인하고, 
Window Level 지원으로 의료 영상 표준에 맞게 시각화합니다.
""")

st.markdown("---")


# *****************************************************************
# 3. 사이드바: 전처리 설정 및 파라미터 튜닝
# *****************************************************************
st.sidebar.header("DICOM 파일 업로드 (.dcm)")

# 파일 업로드
uploaded_file = st.sidebar.file_uploader(
    "DICOM 파일 선택",
    type=["dcm"]
)

# DICOM 정규화/시각화 모드 선택 (추가된 부분)
st.sidebar.markdown("---")
st.sidebar.subheader("DICOM 시각화 모드")
normalize_mode = st.sidebar.radio(
    "원본 이미지 로딩 방식",
    [
        "minmax",  # Min/Max Normalization (일반 보기)
        "window"   # DICOM Window Level (의료 표준)
    ],
    # 사용자에게 보이는 텍스트를 포맷팅
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
    # 파라미터 저장
    params = {'clip_limit': clip_limit, 'tile_grid_size': tile_grid}

# 파라미터: Canny
elif mode == "Edge Detection (Canny)":
    st.sidebar.markdown("##### Canny Edge 설정")
    canny_t1 = st.sidebar.slider("Threshold 1 (낮은 임계값)", 0, 200, 50, 5)
    canny_t2 = st.sidebar.slider("Threshold 2 (높은 임계값)", 0, 300, 150, 5)
    # 파라미터 저장
    params = {'threshold1': canny_t1, 'threshold2': canny_t2}
    
# 파라미터: 원본만 보기 (튜닝바 누락 방지 안내 문구 추가)
else: # mode == "원본만 보기"
    st.sidebar.markdown("<p style='font-size: 14px; color: #003366;'>선택된 모드에서는 파라미터 튜닝이 필요하지 않습니다.</p>", unsafe_allow_html=True)
    params = {}


# *****************************************************************
# 4. 메인 콘텐츠: 이미지 처리 및 표시
# *****************************************************************

if uploaded_file is None:
    st.info("좌측 패널에서 DICOM 파일을 업로드하고 전처리 옵션을 선택하세요")
else:
    # 4.1. DICOM 파일 읽기 및 변환
    @st.cache_data(hash_funcs={type(uploaded_file): lambda x: (x.name, x.size, normalize_mode)})
    def load_and_convert_dicom(file, mode):
        """DICOM 로딩 및 변환을 캐시하여 성능 최적화. DICOM 데이터셋도 함께 반환"""
        from preprocess_core import dicom_to_pil
        file.seek(0)
        file_bytes = file.read()
        return dicom_to_pil(file_bytes, mode)
    
    try:
        # 반환된 튜플을 이미지와 DICOM 데이터셋으로 언패킹
        original_img, dcm_data = load_and_convert_dicom(uploaded_file, normalize_mode)
        
    except ValueError as e:
        st.error(f"⚠️ DICOM 파일 처리 중 오류가 발생했습니다: {e}")
        st.stop()
    except Exception as e:
        st.error(f"예상치 못한 오류 발생: {e}")
        st.stop()
    
    # 4.2. 전처리 적용
    @st.cache_data
    def apply_preprocess(img, mode, params, file_name, file_size, norm_mode):
        """선택된 모드와 파라미터를 적용하여 이미지 처리 (캐시 키에 로딩 정보 포함)"""
        from preprocess_core import apply_clahe, apply_edge
        
        if mode == "Local Contrast(CLAHE)":
            return apply_clahe(img, params.get('clip_limit', 2.0), params.get('tile_grid_size', 8))
        elif mode == "Edge Detection (Canny)":
            return apply_edge(img, params.get('threshold1', 50), params.get('threshold2', 150))
        return img

    processed_img = apply_preprocess(
        original_img, 
        mode, 
        params, 
        uploaded_file.name, 
        uploaded_file.size, 
        normalize_mode
    )

    # 4.3. 탭 구성
    tab1, tab2 = st.tabs(["Before / After 비교", "알고리즘 설명 및 메타데이터"])

    with tab1:
        # Before / After 동시 비교 레이아웃
        col1, col2 = st.columns(2)
        
        # 원본 이미지 캡션에 로딩 방식 추가
        caption_text = "DICOM Window Level (의료 표준)" if normalize_mode == 'window' else "Min/Max Normalization (일반 보기)"
        
        with col1:
            st.subheader("원본 이미지 (Original)")
            st.image(original_img, caption=f"로딩 방식: {caption_text}", use_container_width=True)

        with col2:
            st.subheader(f"전처리 결과: {mode}")
            st.image(processed_img, caption=f"적용 파라미터: {params}", use_container_width=True)

    with tab2:
        st.header("알고리즘 및 프로젝트 노트")
        
        # 전처리 모드별 설명
        st.markdown("---")
        if mode == "Local Contrast(CLAHE)":
            st.markdown("""
                ### CLAHE (Contrast Limited Adaptive Histogram Equalization)
                - **목표:** 의료 영상(특히 X-ray)에서 발생하는 낮은 대비(Contrast)를 국소적으로 향상시켜 병변이나 구조를 더 잘 보이게 합니다.
                - **작동 원리:** 전체 이미지가 아닌 작은 영역(Tile Grid) 단위로 히스토그램 평활화를 수행합니다. `Clip Limit`를 설정하여 대비 증폭이 과도하게 되는 것을 막고 노이즈 생성을 억제합니다.
                - **학습 목적:** 낮은 대비의 의료 영상 데이터셋을 사용하는 딥러닝 모델의 성능 향상 전처리 기법으로 활용될 수 있습니다.
            """)
        elif mode == "Edge Detection (Canny)":
            st.markdown("""
                ### Canny Edge Detection
                - **목표:** 이미지에서 객체의 경계를 정확하게 검출합니다.
                - **작동 원리:** 가우시안 블러로 노이즈를 제거한 후, 그래디언트를 계산하고, 두 개의 임계값(Threshold 1, 2)을 사용하여 약한 에지와 강한 에지를 구분하여 최종 에지를 확정합니다.
                - **학습 목적:** 객체 분할(Segmentation)이나 특징 추출(Feature Extraction)의 기반 작업으로 유용하며, 전처리 파이프라인의 초기 단계로 활용될 수 있습니다.
            """)
        else:
            st.markdown("""
                DICOM 파일 로딩 및 DICOM Tag 확인 등 기본적인 기능을 확인합니다.
                좌측 사이드바에서 다른 전처리 모드를 선택하여 효과를 비교해 보세요.
            """)
        
        # DICOM 메타데이터 표시 (시연에 필수적인 정보)
        st.markdown("---")
        st.subheader("DICOM 메타데이터 (주요 Tag)")
        
        # Window Center/Width 값을 DICOM에서 가져오고, 리스트 형태일 경우 첫 번째 값만 표시
        wc_value = dcm_data.get('WindowCenter', 'N/A')
        ww_value = dcm_data.get('WindowWidth', 'N/A')
        
        if isinstance(wc_value, (list, tuple)): wc_value = wc_value[0]
        if isinstance(ww_value, (list, tuple)): ww_value = ww_value[0]

        # PyArrow 에러 수정: 모든 값을 문자열로 변환
        meta_data = {
            "환자 ID (Patient ID)": str(dcm_data.get('PatientID', 'N/A')),
            "검사 종류 (Modality)": str(dcm_data.get('Modality', 'N/A')),
            "연구 설명 (Study Desc)": str(dcm_data.get('StudyDescription', 'N/A')),
            "획득 날짜 (Acquisition Date)": str(dcm_data.get('AcquisitionDate', 'N/A')),
            "이미지 크기 (Rows/Cols)": f"{dcm_data.get('Rows', 'N/A')} x {dcm_data.get('Columns', 'N/A')}",
            "비트 수 (Bits Stored)": str(dcm_data.get('BitsStored', 'N/A')),
            # DICOM Windowing 정보를 별도로 표시하여 강조
            "Window Center": str(wc_value),
            "Window Width": str(ww_value),
            "Rescale Slope/Intercept": f"{dcm_data.get('RescaleSlope', '1.0')} / {dcm_data.get('RescaleIntercept', '0.0')}",
        }
        
        # 메타데이터를 깔끔한 표 형태로 표시
        st.dataframe(
            list(meta_data.items()),
            column_config={0: "Tag", 1: "Value"},
            hide_index=True,
            use_container_width=True
        )
        
        # DICOM 로딩 방식에 대한 설명 추가
        if normalize_mode == 'window':
            st.info(f"현재 이미지는 DICOM 파일에 명시된 Window Center ({wc_value}) 및 Width ({ww_value})를 적용하여 시각화되었습니다. 이는 실제 임상 뷰어의 동작과 유사합니다.")
        else:
            st.info("현재 이미지는 Min/Max Normalization을 적용하여 픽셀을 0-255 범위로 스케일링했습니다. DICOM Window Level (의료 표준) 모드를 선택하여 비교해 보세요.")

        with st.expander("전체 DICOM 정보 보기"):
            # dcm_data를 Streamlit의 st.json 기능을 사용하여 전체 구조를 표시합니다.
            try:
                # pydicom Dataset을 dict로 변환하여 JSON으로 출력
                st.json(dcm_data.to_json_dict())
            except Exception as e:
                st.write("전체 DICOM 정보를 JSON으로 변환하는 중 오류 발생.")
                st.text(str(dcm_data)) # 변환이 안될 경우 텍스트로 대체
            
        with st.expander("프로젝트 개요 및 유지보수 계획"):
            st.markdown("""
                이 애플리케이션은 `app.py` (Streamlit UI)와 `preprocess_core.py` (Core Logic)로 역할을 분리하여 개발되었습니다.
                * **알고리즘 개선:** `preprocess_core.py`만 수정하여 새 전처리 함수를 추가하거나 기존 함수를 개선할 수 있습니다.
                * **UI 개선:** `app.py`만 수정하여 레이아웃, 슬라이더, 비교 방식 등을 변경할 수 있습니다.
                * **배포:** `requirements.txt`와 함께 GitHub에 푸시하여 Streamlit Community Cloud에 즉시 배포 가능합니다.
            """)