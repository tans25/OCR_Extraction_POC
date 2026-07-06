import streamlit as st
from ocr import run_ocr
import io 
from extractor import extract_medications, extract_from_image
from fda_client import fetch_all_labels
from analyzer import analyze_medications

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
        color: #1e1b4b !important;
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

    /* Results page styles */
    .results-header {
        display: flex;
        align-items: center;
        justify-content: space-between;
        padding: 0.5rem 0 1rem;
    }

    .results-title {
        font-family: 'Montserrat', sans-serif;
        font-weight: 900;
        font-size: 2.2rem;
        background: linear-gradient(135deg, #6c3ce0, #22a7d1);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }

    .section-label {
        font-family: 'Montserrat', sans-serif;
        font-weight: 700;
        font-size: 1rem;
        color: #4a5578;
        margin-bottom: 0.8rem;
        letter-spacing: 0.5px;
    }

    .image-card {
        background: white;
        border-radius: 16px;
        padding: 1rem;
        box-shadow: 0 2px 12px rgba(108, 60, 224, 0.08);
        border: 1px solid rgba(108, 60, 224, 0.1);
    }

    .text-card {
        background: white;
        border-radius: 16px;
        padding: 1.5rem;
        box-shadow: 0 2px 12px rgba(108, 60, 224, 0.08);
        border: 1px solid rgba(108, 60, 224, 0.1);
        min-height: 350px;
    }

    .text-card pre {
        font-family: 'Noto Sans', sans-serif;
        font-size: 0.95rem;
        color: #2d2b55;
        line-height: 1.8;
        white-space: pre-wrap;
        word-wrap: break-word;
        margin: 0;
    }

    /* Style the Streamlit text area on results page */
    .st-key-ocr_output textarea {
        background: white !important;
        color: #2d2b55 !important;
        border: 1px solid rgba(108, 60, 224, 0.15) !important;
        border-radius: 12px !important;
        font-family: 'Noto Sans', sans-serif !important;
        font-size: 0.95rem !important;
        line-height: 1.8 !important;
        padding: 1.2rem !important;
        box-shadow: 0 2px 12px rgba(108, 60, 224, 0.06) !important;
    }

    .st-key-ocr_output textarea:focus {
        border-color: #6c3ce0 !important;
        box-shadow: 0 0 0 2px rgba(108, 60, 224, 0.15) !important;
    }

    /* New Scan button — vertically centered with title */
    .st-key-new_scan {
        display: flex !important;
        align-items: center !important;
        height: 100% !important;
        justify-content: flex-end !important;
    }

    .st-key-new_scan button {
        background: linear-gradient(135deg, #6c3ce0, #22a7d1) !important;
        color: white !important;
        border: none !important;
        border-radius: 12px !important;
        font-family: 'Montserrat', sans-serif !important;
        font-weight: 600 !important;
        padding: 0.5rem 1.5rem !important;
        font-size: 0.9rem !important;
        transition: all 0.3s ease !important;
        box-shadow: 0 2px 8px rgba(108, 60, 224, 0.2) !important;
    }

    .st-key-new_scan button:hover {
        box-shadow: 0 4px 16px rgba(108, 60, 224, 0.3) !important;
        transform: translateY(-1px);
    }

    /* Header row alignment */
    .results-header-row {
        display: flex;
        align-items: center;
        justify-content: space-between;
        padding-bottom: 0.8rem;
        border-bottom: 1.5px solid rgba(108, 60, 224, 0.1);
        margin-bottom: 1.5rem;
    }

    /* Divider styling */
    [data-testid="stHorizontalRule"] {
        border-color: rgba(108, 60, 224, 0.12) !important;
    }

    /* Image styling */
    .st-key-prescription_img img {
        border-radius: 12px !important;
    }
    /* Dark processing overlay */
            
    .processing-overlay {
        position: fixed;
        top: 0;
        left: 0;
        width: 100%;
        height: 100%;
        background: rgba(10, 10, 30, 0.35);
        backdrop-filter: blur(6px);
        z-index: 9999;
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
        gap: 1.5rem;
    }

    .scanner-spinner {
        width: 60px;
        height: 60px;
        border: 4px solid rgba(123, 47, 247, 0.2);
        border-top: 4px solid #7b2ff7;
        border-radius: 50%;
        animation: spin 0.9s linear infinite;
    }

    @keyframes spin {
        to { transform: rotate(360deg); }
    }

    .processing-text {
        font-family: 'Montserrat', sans-serif;
        font-weight: 600;
        font-size: 1.1rem;
        color: #d4c6f7;
        letter-spacing: 0.5px;
    }

    /* Patient info card */
    .patient-card {
        background: white;
        border-radius: 14px;
        padding: 1.2rem 1.5rem;
        margin-top: 1rem;
        box-shadow: 0 2px 12px rgba(108, 60, 224, 0.08);
        border: 1px solid rgba(108, 60, 224, 0.1);
    }

    .patient-card-title {
        font-family: 'Montserrat', sans-serif;
        font-weight: 700;
        font-size: 0.85rem;
        color: #6c3ce0;
        text-transform: uppercase;
        letter-spacing: 1px;
        margin-bottom: 0.8rem;
    }

    .patient-row {
        display: flex;
        justify-content: space-between;
        padding: 0.35rem 0;
        border-bottom: 1px solid rgba(108, 60, 224, 0.06);
    }

    .patient-row:last-child {
        border-bottom: none;
    }

    .patient-label {
        font-family: 'Noto Sans', sans-serif;
        font-weight: 500;
        font-size: 0.85rem;
        color: #6b7ba0;
    }

    .patient-value {
        font-family: 'Noto Sans', sans-serif;
        font-weight: 500;
        font-size: 0.85rem;
        color: #1e1b4b;
    }

    /* Pipeline toggle */
    .st-key-pipeline_toggle [role="radiogroup"] {
        gap: 0 !important;
        display: flex !important;
    }
    .st-key-pipeline_toggle [role="radiogroup"] label > div {
        display: none !important;
    }
            
    .st-key-pipeline_toggle [role="radiogroup"] label > div:has([data-testid="stMarkdownContainer"]) {
        display: flex !important;
    }

    .st-key-pipeline_toggle [role="radiogroup"] label [data-testid="stMarkdownContainer"] p {
        padding: 0.55rem 0.55rem !important;
        font-family: 'Montserrat', sans-serif !important;
        font-weight: 600 !important;
        font-size: 1rem !important;
        color: #a78bfa !important;
    }     

    .st-key-pipeline_toggle [role="radiogroup"] label{
        background: transparent !important;
        border: none !important;
        border-radius: 0 !important;
        border-bottom: 3px solid transparent !important;
        cursor: pointer !important;
        transition: all 0.2s ease !important;
    }
            
    .st-key-pipeline_toggle [role="radiogroup"] label [data-testid="stMarkdownContainer"] p:hover {
        color: #7c3aed !important;
    }

    .st-key-pipeline_toggle [role="radiogroup"] label:has(input:checked) {
        border-bottom-style: solid !important;
        border-bottom-width: 3px !important;
        border-image: linear-gradient(135deg, #6c3ce0, #22a7d1) !important;
        border-color: transparent !important;
        border-image-slice: 1 !important;
    }
            
    .st-key-pipeline_toggle [role="radiogroup"] label:has(input:checked) [data-testid="stMarkdownContainer"] p {
        color: #4c1d95 !important;
    }

    .st-key-pipeline_toggle [role="radiogroup"] label [data-testid="stMarkdownContainer"] span {
        color: inherit !important;
    }

    # .st-key-pipeline_toggle [role="radiogroup"] {
    #     display: none !important;
    # }

    /* Confidence badge */
    .confidence-badge {
        display: inline-block;
        padding: 0.25rem 0.8rem;
        border-radius: 20px;
        font-family: 'Montserrat', sans-serif;
        font-weight: 600;
        font-size: 0.75rem;
        letter-spacing: 0.5px;
        text-transform: uppercase;
        margin-left: 0.5rem;
        vertical-align: middle;
    }

    .confidence-high {
        background: rgba(34, 197, 94, 0.12);
        color: #16a34a;
    }

    .confidence-medium {
        background: rgba(234, 179, 8, 0.12);
        color: #ca8a04;
    }

    .confidence-low {
        background: rgba(239, 68, 68, 0.12);
        color: #dc2626;
    }

    /* Medication card */
    .med-card {
        background: white;
        border-radius: 10px;
        padding: 0.7rem 1rem;
        margin-bottom: 0.5rem;
        box-shadow: 0 2px 12px rgba(108, 60, 224, 0.08);
        border: 1px solid rgba(108, 60, 224, 0.1);
        transition: all 0.2s ease;
    }

    .med-card:hover {
        box-shadow: 0 4px 18px rgba(108, 60, 224, 0.12);
        border-color: rgba(108, 60, 224, 0.18);
    }

    .med-name {
        font-family: 'Montserrat', sans-serif;
        font-weight: 700;
        font-size: 0.9rem;
        color: #1e1b4b;
        margin-bottom: 0.3rem;
        padding-bottom: 0.25rem;
        border-bottom: 2px solid rgba(108, 60, 224, 0.08);
    }

    .med-details {
        display: grid;
        grid-template-columns: 1fr 1fr;
        gap: 0.2rem 1rem;
    }

    .med-field {
        display: flex;
        flex-direction: column;
    }

    .med-field-label {
        font-family: 'Noto Sans', sans-serif;
        font-weight: 500;
        font-size: 0.65rem;
        color: #6b7ba0;
        text-transform: uppercase;
        letter-spacing: 0.5px;
        margin-bottom: 0.05rem;
    }

    .med-field-value {
        font-family: 'Noto Sans', sans-serif;
        font-weight: 500;
        font-size: 0.78rem;
        color: #1e1b4b;
    }

    .med-instructions {
        grid-column: 1 / -1;
    }

    /* No data state */
    .no-data {
        text-align: center;
        padding: 2rem;
        color: #6b7ba0;
        font-size: 0.95rem;
    }

    .interaction-card {
        border: 1px solid;
        border-radius: 10px;
        padding: 0.6rem 0.9rem;
        margin: 0.5rem 0;
    }

    .interaction-card.high {
        background: rgba(220, 50, 50, 0.12);
        border-color: rgba(220, 50, 50, 0.3);
    }

    .interaction-card.moderate {
        background: rgba(180, 120, 20, 0.12);
        border-color: rgba(180, 120, 20, 0.3);
    }

    .interaction-card.low {
        background: rgba(34, 160, 90, 0.12);
        border-color: rgba(34, 160, 90, 0.3);
    }

    .interaction-card.moderate .interaction-card-header span,
    .interaction-card.moderate .interaction-card-body {
        color: #c89220;
    }


</style>
""", unsafe_allow_html=True)

if st.session_state.get("processing"):
    st.markdown("""
        <div class="processing-overlay">
            <div class="scanner-spinner"></div>
            <div class="processing-text">Scanning prescription...</div>
        </div>
    """, unsafe_allow_html=True)
    try:
        file_bytes = st.session_state["file_bytes"]

        file_obj = io.BytesIO(file_bytes)
        ocr_obj = run_ocr(file_obj)

        if not ocr_obj["raw_text"]:
            raise ValueError("No text detected.")
        
        text_extraction = extract_medications(ocr_obj["raw_text"])
        image_extraction = extract_from_image(file_bytes, "image/png")
        fda_labels = fetch_all_labels(image_extraction.get("medications", []))
        analysis = analyze_medications(image_extraction.get("medications", []), fda_labels)

        st.session_state["ocr_result"] = ocr_obj
        st.session_state["text_extraction"] = text_extraction
        st.session_state["image_extraction"] = image_extraction
        st.session_state["fda_labels"] = fda_labels
        st.session_state["analysis"] = analysis 

        st.session_state.pop("upload_error", None)
    except Exception as e:
        st.session_state["upload_error"] = True 
    st.session_state.pop("processing", None)
    st.session_state.pop("file_bytes", None)
    st.rerun()


elif "ocr_result" not in st.session_state:
    if st.session_state.pop("upload_error", False):
        st.error("Something went wrong. Please try again.")
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
            if uploaded_file:
                st.session_state["file_bytes"] = uploaded_file.read()
                st.session_state["processing"] = True
                st.rerun()

    # if uploaded_file is not None:
    #     st.session_state["file_bytes"] = uploaded_file.read()
    #     with st.spinner("Scanning prescription...."):
    #         try:
    #             file_bytes = st.session_state["file_bytes"]

    #             file_obj = io.BytesIO(file_bytes)
    #             ocr_obj = run_ocr(file_obj)

    #             if not ocr_obj["raw_text"]:
    #                 raise ValueError("No text detected.")
                
    #             text_extraction = extract_medications(ocr_obj["raw_text"])
    #             image_extraction = extract_from_image(file_bytes, "image/png")
    #             fda_labels = fetch_all_labels(image_extraction.get("medications", []))
    #             analysis = analyze_medications(image_extraction.get("medications", []), fda_labels)

    #             st.session_state["ocr_result"] = ocr_obj
    #             st.session_state["text_extraction"] = text_extraction
    #             st.session_state["image_extraction"] = image_extraction
    #             st.session_state["fda_labels"] = fda_labels
    #             st.session_state["analysis"] = analysis 

    #             st.session_state.pop("upload_error", None)
    #         except Exception as e:
    #             st.session_state["upload_error"] = True 
    #     st.rerun()
else:
    import json

    result = st.session_state["ocr_result"]
    text_extraction = st.session_state["text_extraction"]
    image_extraction = st.session_state["image_extraction"]

    def parse_extraction(data):
        if isinstance(data, str):
            try:
                return json.loads(data)
            except (json.JSONDecodeError, TypeError):
                return None
        return data if isinstance(data, dict) else None

    text_data = parse_extraction(text_extraction)
    image_data = parse_extraction(image_extraction)

    header_left, header_right = st.columns([3, 1])
    with header_left:
        st.markdown('<div class="results-title">MedSight</div>', unsafe_allow_html=True)
    with header_right:
        with st.container(key="new_scan"):
            if st.button("New Scan"):
                for key in ["ocr_result", "text_extraction", "image_extraction", "file_bytes"]:
                    st.session_state.pop(key, None)
                st.rerun()
    st.markdown('<hr style="border: none; border-top: 1.5px solid rgba(108, 60, 224, 0.1); margin: 0.2rem 0 1.5rem;">', unsafe_allow_html=True)

    left_col, spacer, right_col = st.columns([1, 0.15, 1.3])

    with left_col:
        st.markdown('<div class="section-label">Uploaded Prescription</div>', unsafe_allow_html=True)
        with st.container(key="prescription_img"):
            st.image(result["original"], use_container_width=True)

        active = image_data or text_data
        if active:
            patient_name = active.get("patient_name", "N/A")
            prescriber = active.get("prescriber", "N/A")
            date = active.get("date", "N/A")
            st.markdown(f"""
                <div class="patient-card">
                    <div class="patient-card-title">Patient Information</div>
                    <div class="patient-row">
                        <span class="patient-label">Patient</span>
                        <span class="patient-value">{patient_name}</span>
                    </div>
                    <div class="patient-row">
                        <span class="patient-label">Prescriber</span>
                        <span class="patient-value">{prescriber}</span>
                    </div>
                    <div class="patient-row">
                        <span class="patient-label">Date</span>
                        <span class="patient-value">{date}</span>
                    </div>
                </div>
            """, unsafe_allow_html=True)

    with right_col:
        with st.container(key="pipeline_toggle"):
            pipeline = st.radio(
                "Pipeline",
                ["⚙️ OCR Pipeline", "🪄 LLM Pipeline"],
                horizontal=True,
                label_visibility="collapsed"
            )

        data = text_data if "OCR" in pipeline else image_data
        
        if data and data.get("is_valid"):
            confidence = data.get("confidence", "unknown")
            confidence_class = f"confidence-{confidence}" if confidence in ("high", "medium", "low") else ""
            st.markdown(f"""
                <div style="margin: 0.8rem 0 1rem;">
                    <span class="section-label" style="margin: 0;">Medications</span>
                    <span class="confidence-badge {confidence_class}">{confidence} confidence</span>
                </div>
            """, unsafe_allow_html=True)

            medications = data.get("medications", [])
            if medications:
                for med in medications:
                    name = med.get("name", "Unknown Medication")
                    dosage = med.get("dosage", "N/A")
                    frequency = med.get("frequency", "N/A")
                    instructions = med.get("instructions", "N/A")
                    quantity = med.get("quantity", "N/A")
                    refills = med.get("refills", "N/A")

                    st.markdown(f"""
                        <div class="med-card">
                            <div class="med-name">{name}</div>
                            <div class="med-details">
                                <div class="med-field">
                                    <span class="med-field-label">Dosage</span>
                                    <span class="med-field-value">{dosage}</span>
                                </div>
                                <div class="med-field">
                                    <span class="med-field-label">Frequency</span>
                                    <span class="med-field-value">{frequency}</span>
                                </div>
                                <div class="med-field">
                                    <span class="med-field-label">Quantity</span>
                                    <span class="med-field-value">{quantity}</span>
                                </div>
                                <div class="med-field">
                                    <span class="med-field-label">Refills</span>
                                    <span class="med-field-value">{refills}</span>
                                </div>
                                <div class="med-field med-instructions">
                                    <span class="med-field-label">Instructions</span>
                                    <span class="med-field-value">{instructions}</span>
                                </div>
                            </div>
                        </div>
                    """, unsafe_allow_html=True)
            else:
                st.markdown('<div class="no-data">No medications found.</div>', unsafe_allow_html=True)
            
            if "OCR" not in pipeline:
                analysis = st.session_state.get("analysis", {})
                for interaction in analysis.get("interactions", []):
                    drugs = " + ".join(interaction.get("drugs", []))
                    description = interaction.get("description", "")
                    recommendation = interaction.get("recommendation", "")
                    severity = interaction.get("severity", "moderate")

                    st.markdown(f"""
                        <div class="interaction-card {severity}">
                            <div class="interaction-card-header">
                                <span>⚠️ Interaction Warning</span>
                            </div>
                            <div class="interaction-card-body">
                                <strong>{drugs}</strong> — {description} {recommendation}
                            </div>
                        </div>
                    """, unsafe_allow_html=True)
        elif data and not data.get("is_valid"):
            st.markdown('<div class="no-data">This prescription could not be validated. Try uploading a clearer image.</div>', unsafe_allow_html=True)
        else:
            st.markdown('<div class="no-data">No data available for this pipeline.</div>', unsafe_allow_html=True)
        
