import streamlit as st
from google import genai
import PIL.Image
import io

# ==========================================
# PAGE CONFIG & CSS HACKS (UI Polish)
# ==========================================
st.set_page_config(page_title="AI Design Studio PRO", layout="wide", page_icon="🎨")

st.markdown("""
    <style>
        /* Compact layout */
        .block-container {
            padding-top: 1.5rem !important;
            padding-bottom: 1rem !important;
            max-width: 98% !important;
        }
        
        /* 🪄 HIDE ANNOYING UPLOADER TEXT */
        [data-testid="stFileUploadDropzone"] > div > div > span { display: none !important; }
        [data-testid="stFileUploadDropzone"] > div > div > small { display: none !important; }
        
        /* Make the uploader box smaller and cleaner */
        [data-testid="stFileUploadDropzone"] {
            padding: 5px !important;
            min-height: 50px !important;
            display: flex;
            align-items: center;
            justify-content: center;
        }
    </style>
""", unsafe_allow_html=True)

st.title("🎨 AI Design Generator - Pro Studio")
st.markdown("##### *Optimized for Creation (Upscaling & BG Removal handled in Canva)*")

# ==========================================
# SIDEBAR CONFIGURATION
# ==========================================
with st.sidebar:
    st.header("⚙️ Configuration")
    api_key = st.text_input("Enter Google API Key", type="password")
    num_vars = st.slider("Number of Variations", 1, 4, 4)
    st.info("💡 Tip: Download the results and use Canva's BG Remover for perfect edges.")

# ==========================================
# STATE MANAGEMENT & IMAGE PROCESSING
# ==========================================
if 'generated_designs' not in st.session_state:
    st.session_state.generated_designs = []

def save_designs(response_images):
    st.session_state.generated_designs = []
    for g_img in response_images:
        try:
            if hasattr(g_img, 'image') and hasattr(g_img.image, 'image_bytes'):
                raw_bytes = g_img.image.image_bytes
                pil_img = PIL.Image.open(io.BytesIO(raw_bytes))
            elif isinstance(g_img.image, bytes):
                pil_img = PIL.Image.open(io.BytesIO(g_img.image))
            else:
                pil_img = g_img.image 
            st.session_state.generated_designs.append(pil_img)
        except Exception as e:
            st.error(f"Error extracting image: {e}")

# ==========================================
# TABS INTERFACE
# ==========================================
tab1, tab2 = st.tabs(["✍️ 1. Text to Design", "🖼️ 2. Niche + Style Mixer (PRO)"])

# ------------------------------------------
# TAB 1: TEXT TO DESIGN
# ------------------------------------------
with tab1:
    col1, col2, col3 = st.columns([3, 1, 1])
    with col1:
        niche_text = st.text_input("Design Niche:", placeholder="e.g. SCP-049 Plague Doctor minimalist")
    with col2:
        pod_style = st.selectbox("Style Preset", ["Vector Sticker", "Vintage Retro", "Dark Indie Horror", "Cute Kawaii"])
    with col3:
        st.write("") 
        st.write("")
        btn_generate_text = st.button("Generate 🚀", use_container_width=True)
    
    if btn_generate_text:
        if api_key and niche_text:
            try:
                client = genai.Client(api_key=api_key)
                with st.spinner("Drawing on a solid grey background..."):
                    prompt = f"Professional T-shirt design, '{niche_text}', {pod_style}, clean vector art. The design is placed completely on a flat, solid grey background."
                    res = client.models.generate_images(model="imagen-4.0-generate-001", prompt=prompt, config={"number_of_images": num_vars})
                    save_designs(res.generated_images)
            except Exception as e:
                st.error(f"Generation Error: {e}")
        else:
            st.error("Please enter API Key and Niche.")

# ------------------------------------------
# TAB 2: NICHE + STYLE MIXER
# ------------------------------------------
with tab2:
    st.caption("Upload subject (Niche) and reference (Style) to create something unique.")
    
    col_niche, col_style = st.columns(2)
    
    with col_niche:
        niche_file = st.file_uploader("Niche", type=["png", "jpg", "jpeg"])
        # Preview the uploaded image exactly where you wanted it
        if niche_file: 
            st.image(niche_file, use_container_width=True)
            
    with col_style:
        style_file = st.file_uploader("Style", type=["png", "jpg", "jpeg"])
        # Preview the uploaded image exactly where you wanted it
        if style_file: 
            st.image(style_file, use_container_width=True)
        
    st.write("") # Spacing
    btn_mix = st.button("Mix & Generate Design 🪄", use_container_width=True)
        
    if btn_mix:
        if api_key and niche_file and style_file:
            try:
                client = genai.Client(api_key=api_key)
                niche_img = PIL.Image.open(niche_file)
                style_img = PIL.Image.open(style_file)
                
                with st.spinner("Analyzing and drawing..."):
                    vision_prompt = "You are an expert Print-on-Demand designer. Look at Image 1 (Subject) and Image 2 (Style). Write a prompt to generate a vector T-shirt design featuring the subject from Image 1 in the exact style of Image 2. IMPORTANT: Do not describe the background of Image 2. End your prompt exactly with: 'The entire design is placed on a simple, flat, solid grey background.'"
                    
                    vision_res = client.models.generate_content(
                        model="gemini-2.5-flash",
                        contents=[niche_img, style_img, vision_prompt]
                    )
                    smart_prompt = vision_res.text
                    
                    res = client.models.generate_images(model="imagen-4.0-generate-001", prompt=smart_prompt, config={"number_of_images": num_vars})
                    save_designs(res.generated_images)
            except Exception as e:
                st.error(f"Generation Error: {e}")
        else:
            st.error("Please enter API Key and upload BOTH images.")

# ==========================================
# RESULTS GALLERY (4 IN A ROW + CLEAR BTN)
# ==========================================
if st.session_state.generated_designs:
    st.markdown("---")
    
    col_title, col_empty, col_clear = st.columns([3, 5, 2])
    with col_title:
        st.markdown("#### 🖼️ Your Generated Designs")
    with col_clear:
        if st.button("🧹 Clear Gallery", use_container_width=True):
            st.session_state.generated_designs = []
            st.rerun()

    # Dynamic columns based on number of variations
    cols = st.columns(len(st.session_state.generated_designs))
    for idx, pil_img in enumerate(st.session_state.generated_designs):
        with cols[idx]:
            st.image(pil_img, use_container_width=True)
            
            buf = io.BytesIO()
            pil_img.save(buf, format="PNG")
            st.download_button(
                label=f"📥 Download {idx+1}",
                data=buf.getvalue(),
                file_name=f"Design_Raw_v{idx+1}.png",
                mime="image/png",
                key=f"dl_btn_{idx}",
                use_container_width=True
            )
