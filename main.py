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

# Initialize pipeline
@st.cache_resource
def load_pipeline():
    return OCRPIIPipeline()

pipeline = load_pipeline()

# Sidebar
st.sidebar.header("About")
st.sidebar.info(
    """
    This pipeline:
    1. Preprocesses handwritten images
    2. Extracts text using OCR
    3. Cleans the extracted text
    4. Detects PII (names, emails, phones, etc.)
    5. Generates redacted outputs
    """
)

# File uploader
uploaded_file = st.file_uploader(
    "Upload a handwritten document (JPEG/PNG)", 
    type=['jpg', 'jpeg', 'png']
)

if uploaded_file:
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Original Image")
        image = Image.open(uploaded_file)
        st.image(image, use_container_width=True)
    
    # Save uploaded file temporarily
    temp_path = os.path.join("output", uploaded_file.name)
    os.makedirs("output", exist_ok=True)
    
    with open(temp_path, "wb") as f:
        f.write(uploaded_file.getbuffer())
    
    # Process button
    if st.button("🚀 Process Document", type="primary"):
        with st.spinner("Processing document..."):
            try:
                results = pipeline.process(temp_path)
                
                # Display results
                st.success("✅ Processing complete!")
                
                # Tabs for different outputs
                tab1, tab2, tab3, tab4 = st.tabs(
                    ["📝 Extracted Text", "🔍 Detected PII", "🔒 Redacted Text", "🖼️ Redacted Image"]
                )
                
                with tab1:
                    st.subheader("Cleaned Extracted Text")
                    st.text_area("Text", results['cleaned_text'], height=300)
                    
                with tab2:
                    st.subheader("PII Entities Detected")
                    if results['pii_entities']:
                        for entity in results['pii_entities']:
                            st.markdown(f"""
                            - **Type**: {entity['type']}  
                              **Text**: `{entity['text']}`  
                              **Confidence**: {entity['score']:.2%}
                            """)
                    else:
                        st.info("No PII entities detected")
                
                with tab3:
                    st.subheader("Redacted Text")
                    st.text_area("Redacted", results['redacted_text'], height=300)
                    
                    # Download button
                    st.download_button(
                        label="📥 Download Redacted Text",
                        data=results['redacted_text'],
                        file_name="redacted_text.txt",
                        mime="text/plain"
                    )
                
                with tab4:
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
                                mime="image/jpeg"
                            )
                    else:
                        st.warning("Image redaction not available")
                
            except Exception as e:
                st.error(f"Error processing document: {str(e)}")
                st.exception(e)

# Sample images section
st.sidebar.header("Sample Documents")
sample_dir = "samples"
if os.path.exists(sample_dir):
    samples = [f for f in os.listdir(sample_dir) if f.endswith(('.jpg', '.jpeg', '.png'))]
    if samples:
        selected_sample = st.sidebar.selectbox("Load a sample:", [""] + samples)
        if selected_sample and st.sidebar.button("Load Sample"):
            st.rerun()

# Footer
st.sidebar.markdown("---")
st.sidebar.markdown("Built with Streamlit & Presidio")