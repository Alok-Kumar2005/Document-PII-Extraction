import streamlit as st
import os
from PIL import Image
import sys
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from src.pipeline import OCRPIIPipeline

# Page config
st.set_page_config(
    page_title="OCR PII Extraction Pipeline",
    page_icon="📄",
    layout="wide"
)

# Title
st.title("📄 OCR PII Extraction Pipeline")
st.markdown("**Extract and redact PII from handwritten documents**")

# Sidebar - OCR Method Selection
st.sidebar.header("⚙️ Configuration")

ocr_method = st.sidebar.radio(
    "Select OCR Method:",
    options=["Tesseract OCR", "Gemini Vision (LLM)"],
    help="Choose between traditional Tesseract OCR or AI-powered Gemini Vision"
)

# Convert display name to internal name
ocr_method_internal = "tesseract" if ocr_method == "Tesseract OCR" else "gemini"

# API Key input for Gemini
gemini_api_key = None
if ocr_method_internal == "gemini":
    gemini_api_key = st.sidebar.text_input(
        "Google Gemini API Key:",
        type="password",
        help="Enter your Google Gemini API key. Get one at https://makersuite.google.com/app/apikey"
    )
    
    if not gemini_api_key:
        st.sidebar.warning("⚠️ Gemini API key required for LLM-based OCR")
        st.sidebar.info("You can also set the GOOGLE_API_KEY environment variable")

# Initialize pipeline
@st.cache_resource
def load_pipeline(ocr_method, api_key):
    """Load pipeline with caching based on OCR method"""
    try:
        return OCRPIIPipeline(ocr_method=ocr_method, gemini_api_key=api_key)
    except Exception as e:
        st.error(f"Failed to initialize pipeline: {str(e)}")
        return None

# Sidebar - About
st.sidebar.header("ℹ️ About")
st.sidebar.info(
    f"""
    **Current OCR Method:** {ocr_method}
    
    This pipeline:
    1. Preprocesses handwritten images
    2. Extracts text using {'AI-powered Gemini Vision' if ocr_method_internal == 'gemini' else 'Tesseract OCR'}
    3. Cleans the extracted text
    4. Detects PII (names, emails, phones, etc.)
    5. Generates redacted outputs
    
    **OCR Methods:**
    - **Tesseract**: Traditional OCR, good for printed text
    - **Gemini Vision**: AI-powered, better for handwritten text
    """
)

# Main content
pipeline = load_pipeline(ocr_method_internal, gemini_api_key)

if pipeline is None and ocr_method_internal == "gemini" and not gemini_api_key:
    st.warning("⚠️ Please enter your Gemini API key in the sidebar to use LLM-based OCR")
    st.stop()

# File uploader
uploaded_file = st.file_uploader(
    "Upload a handwritten document (JPEG/PNG)", 
    type=['jpg', 'jpeg', 'png']
)

if uploaded_file and pipeline:
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("📷 Original Image")
        image = Image.open(uploaded_file)
        st.image(image, use_container_width=True)
    
    with col2:
        st.subheader("🔧 Processing Settings")
        st.info(f"**OCR Method:** {ocr_method}")
        
        if ocr_method_internal == "gemini":
            st.success("✨ Using AI-powered text extraction")
        else:
            st.info("📝 Using traditional Tesseract OCR")
    
    # Save uploaded file temporarily
    temp_path = os.path.join("output", uploaded_file.name)
    os.makedirs("output", exist_ok=True)
    
    with open(temp_path, "wb") as f:
        f.write(uploaded_file.getbuffer())
    
    # Process button
    if st.button("🚀 Process Document", type="primary", use_container_width=True):
        with st.spinner(f"Processing document using {ocr_method}..."):
            try:
                results = pipeline.process(temp_path)
                
                # Display results
                st.success(f"✅ Processing complete using {ocr_method}!")
                
                # Show OCR comparison info
                st.info(f"📊 Text extracted using: **{results.get('ocr_method', 'unknown').upper()}**")
                
                # Tabs for different outputs
                tab1, tab2, tab3, tab4, tab5 = st.tabs(
                    ["📝 Raw Text", "🧹 Cleaned Text", "🔍 Detected PII", "🔒 Redacted Text", "🖼️ Redacted Image"]
                )
                
                with tab1:
                    st.subheader("Raw Extracted Text")
                    st.text_area("Raw OCR Output", results.get('raw_text', ''), height=300, key="raw")
                    st.caption(f"Extracted using {ocr_method}")
                
                with tab2:
                    st.subheader("Cleaned Extracted Text")
                    st.text_area("Cleaned Text", results.get('cleaned_text', ''), height=300, key="cleaned")
                    
                with tab3:
                    st.subheader("PII Entities Detected")
                    if results.get('pii_entities'):
                        # Summary metrics
                        col1, col2, col3 = st.columns(3)
                        with col1:
                            st.metric("Total PII Found", len(results['pii_entities']))
                        with col2:
                            entity_types = set([e['type'] for e in results['pii_entities']])
                            st.metric("Entity Types", len(entity_types))
                        with col3:
                            avg_confidence = sum([e['score'] for e in results['pii_entities']]) / len(results['pii_entities'])
                            st.metric("Avg Confidence", f"{avg_confidence:.1%}")
                        
                        st.markdown("---")
                        
                        # Detailed list
                        for idx, entity in enumerate(results['pii_entities'], 1):
                            with st.expander(f"{idx}. {entity['type']} - `{entity['text']}`"):
                                col1, col2 = st.columns(2)
                                with col1:
                                    st.write(f"**Type:** {entity['type']}")
                                    st.write(f"**Text:** `{entity['text']}`")
                                with col2:
                                    st.write(f"**Confidence:** {entity['score']:.2%}")
                                    st.write(f"**Position:** {entity['start']}-{entity['end']}")
                    else:
                        st.info("✨ No PII entities detected in the document")
                
                with tab4:
                    st.subheader("Redacted Text")
                    st.text_area("Redacted Output", results.get('redacted_text', ''), height=300, key="redacted")
                    
                    # Download button
                    st.download_button(
                        label="📥 Download Redacted Text",
                        data=results.get('redacted_text', ''),
                        file_name="redacted_text.txt",
                        mime="text/plain",
                        use_container_width=True
                    )
                
                with tab5:
                    if 'redacted_image_path' in results:
                        st.subheader("Redacted Image")
                        redacted_img = Image.open(results['redacted_image_path'])
                        st.image(redacted_img, use_container_width=True)
                        
                        # Download button
                        with open(results['redacted_image_path'], "rb") as f:
                            st.download_button(
                                label="📥 Download Redacted Image",
                                data=f,
                                file_name="redacted_image.jpg",
                                mime="image/jpeg",
                                use_container_width=True
                            )
                    else:
                        st.warning("⚠️ Image redaction not available")
                        if 'redaction_error' in results:
                            st.error(f"Error: {results['redaction_error']}")
                
            except Exception as e:
                st.error(f"❌ Error processing document: {str(e)}")
                with st.expander("Show error details"):
                    st.exception(e)
