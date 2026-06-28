import streamlit as st

st.set_page_config(
    page_title="MedSight",
    page_icon="📝",
    layout="wide",
    initial_sidebar_state="collapsed"
)

st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Montserrat:wght@400;600;800;900&family=Noto+Sans:wght@300;400;500&display=swap');
    *, *::before, *::after { box-sizing: border-box; }

    html, body, [data-testid="stAppViewContainer"] {
        background: linear-gradient(135deg, #e8f0fe 0%, #d5e6f7 30%, #e0d7f5 70%, #daf0ed 100%) !important;
        color: #e0e7ff !important;
        font-family: 'Noto Sans', sans-serif !important;
        min-height: 100vh;
    }

    [data-testid="stHeader"] {
        background: transparent !important;
    }

    [data-testid="stMainBlockContainer"] {
        padding-top: 6rem !important;
    }

    .title-neon {
        font-family: 'Montserrat', sans-serif;
        font-weight: 900;
        font-size: 5.0rem;
        letter-spacing: 2px;
        background: linear-gradient(135deg, #00f0ff, #7b2ff7, #00f0ff, #22d1ee);
        background-size: 300% 300%;
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        text-shadow: none;
        margin-bottom: 0.3rem;
        line-height: 1.1;
    }

    @keyframes gradient-shift {
        0% { background-position: 0% 50%; }
        50% { background-position: 100% 50%; }
        100% { background-position: 0% 50%; }
    }

    .subtitle {
        font-family: 'Noto Sans', sans-serif;
        font-weight: 300;
        font-size: 1.20rem;
        color: #4a5578;
        line-height: 1.7;
        margin-top: 1rem;
        max-width: 440px;
    }
    
    /* Style upload zone */
            
    .st-key-upload_zone {
        border: 2.5px dashed #7b2ff7;
        border-radius: 18px;
        background: rgba(123, 47, 247, 0.06);
        padding: 3rem 2rem;
        text-align: center;
        transition: all 0.3s ease;
        aspect-ratio: 1 / 1;
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
        max-width: 400px;
        margin: 0 auto;
    }
            
    .st-key-upload_zone * {
        text-align: center !important;
    }

    .st-key-upload_zone:hover {
        border-color: #00f0ff;
        background: rgba(0, 240, 255, 0.05);
        box-shadow: 0 0 30px rgba(0, 240, 255, 0.08);
    }

    .upload-icon {
        font-size: 3rem;
        margin-bottom: 1rem;
        color: #7b2ff7;
    }

    .upload-title {
        font-family: 'Montserrat', sans-serif;
        font-weight: 600;
        font-size: 1.1rem;
        color: #5b3ab5;
        margin-bottom: 0.5rem;
    }

    .upload-desc {
        font-size: 0.85rem;
        color: #6b7ba0;
        line-height: 1.5;
    }

    .upload-formats {
        display: inline-block;
        margin-top: 0.8rem;
        padding: 0.35rem 1rem;
        background: rgba(108, 60, 224, 0.1);
        border-radius: 20px;
        font-size: 0.78rem;
        color: #6c3ce0;
        letter-spacing: 0.5px;
        font-family: 'Montserrat', sans-serif;
        font-weight: 600;
    }

    /* Hide Streamlit's default file uploader label */
    .st-key-upload_zone [data-testid="stFileUploader"] > label {
        display: none !important;
        visibility: hidden !important;
    }
            
    [data-testid="stFileUploader"] > div {
        border: none !important;
        background: transparent !important;
        padding: 0 !important;
    }


    [data-testid="stFileUploader"] button {
        background: linear-gradient(135deg, #6c3ce0, #22a7d1) !important;
        color: white !important;
        border: none !important;
        border-radius: 10px !important;
        font-family: 'Montserrat', sans-serif !important;
        font-weight: 600 !important;
    }

    [data-testid="stFileUploaderDropzone"] {
        background: transparent !important;
        border: none !important;
        display: flex !important;
        flex-direction: row !important;
        align-items: center !important;
        justify-content: center !important;
        gap: 0.5rem !important;
    }

    /* Style the small text in uploader */
    [data-testid="stFileUploader"] small {
        color: #6b7ba0 !important;
    }
    
    [data-testid="stFileUploader"] span  {
        color: #5b3ab5 !important;
    }
            
</style>
""", unsafe_allow_html=True)

left_col, spacer, right_col = st.columns([1.1, 0.2, 1])

with left_col:
    st.markdown("""
        <div style="padding-top: 2rem;">
            <div class="title-neon">MedSight</div>
            <p class="subtitle">
                Instantly extract and digitize medical prescription data using intelligent OCR.
                Upload a photo of any prescription and let MedSight do the rest.
            </p>
        </div>
    """, unsafe_allow_html=True)

with right_col:
    with st.container(key='upload_zone'):
        st.markdown("""
                <div class="upload-icon">⬆</div>
                <div class="upload-title">Upload Prescription Image</div>
                <div class="upload-desc">Drag & drop or click to browse your files</div>
                <div class="upload-formats">.jpeg &nbsp;·&nbsp; .jpg &nbsp;·&nbsp; .png &nbsp;·&nbsp; .svg</div>
        """, unsafe_allow_html=True)

        uploaded_file = st.file_uploader(
            " ",
            type=["jpeg", "jpg", "png", "svg"],
        )