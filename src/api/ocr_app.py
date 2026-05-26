import streamlit as st
from PIL import Image
import io
import sys
from pathlib import Path

# Add project root to sys.path to import from src
project_root = Path(__file__).resolve().parent.parent.parent
sys.path.append(str(project_root))

from src.models.ocr_engine import KoreanTROCR

st.set_page_config(
    page_title="고문헌 OCR 추출기", 
    page_icon="📜", 
    layout="wide"
)

# Custom CSS for the "premium but simple" PNU spellchecker-like look
st.markdown("""
<style>
    /* Clean layout, modern typography */
    body {
        font-family: 'Inter', 'Noto Sans KR', sans-serif;
    }
    .main .block-container {
        padding-top: 2rem;
    }
    .stTextArea textarea {
        font-size: 1.1rem !important;
        line-height: 1.6;
        border-radius: 8px;
        border: 1px solid #ddd;
    }
    /* Subtle hover animations */
    .stButton>button {
        transition: all 0.2s ease-in-out;
        border-radius: 8px;
    }
    .stButton>button:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 12px rgba(0,0,0,0.1);
    }
</style>
""", unsafe_allow_html=True)

@st.cache_resource
def load_model():
    return KoreanTROCR()

st.title("📜 중세국어 고문헌 OCR 추출기")
st.markdown("이미지를 업로드하면 인공지능이 옛 문헌의 텍스트를 분석하여 추출합니다.")

with st.sidebar:
    st.header("⚙️ 설정")
    st.info("현재 모델: **ddobokki/ko-trocr**\n\n(로컬 GPU/CPU 추론 중)")
    engine_choice = st.selectbox(
        "OCR 엔진 선택",
        ["Hugging Face TrOCR (Local)", "CLOVA API (준비중)"]
    )

st.markdown("---")

col1, col2 = st.columns(2)

with col1:
    st.subheader("1. 이미지/PDF 업로드")
    uploaded_file = st.file_uploader("문헌 이미지(PNG, JPG)나 PDF 파일을 드래그 앤 드롭하세요.", type=["png", "jpg", "jpeg", "pdf"])
    
    image = None
    if uploaded_file is not None:
        if uploaded_file.name.lower().endswith(".pdf"):
            import fitz  # PyMuPDF
            # PyMuPDF로 PDF 열기
            pdf_bytes = uploaded_file.read()
            doc = fitz.open(stream=pdf_bytes, filetype="pdf")
            
            # 페이지 선택 기능
            if len(doc) > 1:
                page_num = st.number_input(f"페이지 선택 (1 ~ {len(doc)})", min_value=1, max_value=len(doc), value=1)
            else:
                page_num = 1
                
            page = doc[page_num - 1]
            pix = page.get_pixmap(dpi=150)  # OCR에 적합한 해상도로 렌더링
            image = Image.open(io.BytesIO(pix.tobytes("png")))
            st.image(image, caption=f"PDF {page_num}페이지 미리보기", use_container_width=True)
        else:
            image = Image.open(uploaded_file)
            st.image(image, caption="업로드된 원본 이미지", use_container_width=True)

with col2:
    st.subheader("2. 텍스트 추출 결과")
    
    extracted_text = ""
    
    if image is not None:
        if engine_choice == "Hugging Face TrOCR (Local)":
            with st.spinner("OCR 분석 중입니다... 잠시만 기다려주세요 ⏳ (첫 구동 시 모델 다운로드로 시간이 걸릴 수 있습니다)"):
                try:
                    ocr_engine = load_model()
                    extracted_text = ocr_engine.extract_text(image)
                except Exception as e:
                    st.error(f"OCR 처리 중 오류가 발생했습니다: {e}")
        else:
            st.warning("선택하신 엔진은 현재 준비 중입니다.")
            
        st.text_area("결과 텍스트 (자유롭게 수정/복사 가능)", value=extracted_text, height=400)
    else:
        st.info("👈 왼쪽에 이미지를 업로드하면 추출 결과가 여기에 표시됩니다.")
