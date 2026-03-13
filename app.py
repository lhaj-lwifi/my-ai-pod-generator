import streamlit as st
from google import genai
import PIL.Image
import io

# ==========================================
# PAGE CONFIG & HARDCORE CSS HACKS
# ==========================================
st.set_page_config(page_title="AI Design Studio PRO", layout="wide", page_icon="🎨")

st.markdown("""
    <style>
        /* Compact layout */
        .block-container { padding-top: 1.5rem !important; padding-bottom: 1rem !important; max-width: 95% !important; }
        
        /* 🪄 HIDE ANNOYING UPLOADER TEXT (Drag & Drop, Size Limit) */
        [data-testid="stFileUploadDropzone"] > div > div > span,
        [data-testid="stFileUploadDropzone"] > div > div > small { display: none !important; }
        
        /* Make the uploader box look like a compact button area */
        [data-testid="stFileUploadDropzone"] {
            padding: 5px !important;
            min-height: auto !important;
            border: 1px dashed #555 !important;
        }
        
        /* Center download buttons perfectly under images */
        .stDownloadButton { text-align: center; }
        .stDownloadButton button { width: 100%; border-radius: 5px; }
    </style>
""", unsafe_allow_html=True)

# ==========================================
# STATE MANAGEMENT
# ==========================================
if 'generated_designs' not in st.session_state: st.session_state.generated_designs = []
if 'smart_prompt' not in st.session_state: st.session_state.smart_prompt = ""

def save_designs(response_images):
    st.session_state.generated_designs = []
    for g_img in response_images:
        try:
            if hasattr(g_img, 'image') and hasattr(g_img.image, 'image_bytes'):
                pil_img = PIL.Image.open(io.BytesIO(g_img.image.image_bytes))
            elif isinstance(g_img.image, bytes):
                pil_img = PIL.Image.open(io.BytesIO(g_img.image))
            else:
                pil_img = g_img.image 
            st.session_state.generated_designs.append(pil_img)
        except Exception as e:
            st.error(f"Error extracting image: {e}")

# ==========================================
# SIDEBAR
# ==========================================
with st.sidebar:
    st.header("⚙️ Configuration")
    api_key = st.text_input("Enter Google API Key", type="password")
    num_vars = st.slider("Number of Variations", 1, 4, 4)
    st.write("---")
    st.info("💡 **Tip**\n\nUse Canva's background remover to get perfect clean edges for your designs. Upscaling can also be handled there.")

# ==========================================
# MAIN HEADER
# ==========================================
st.title("🎨 AI Design Generator - Pro Studio")
st.markdown("##### *Optimized for Creation (Upscaling & BG Removal handled in Canva)*")

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
                    st.session_state.smart_prompt = prompt
            except Exception as e:
                st.error(f"Generation Error: {e}")
        else:
            st.error("Please enter API Key and Niche.")

# ------------------------------------------
# TAB 2: NICHE + STYLE MIXER (EXACTLY AS MOCKUP)
# ------------------------------------------
with tab2:
    st.write("This area allows you to upload subject (Niche) and a reference (Style) to create something unique.")
    
    col_niche, col_style = st.columns(2)
    
    with col_niche:
        st.markdown("**Niche**")
        niche_file = st.file_uploader("Niche Upload", type=["png", "jpg", "jpeg"], label_visibility="collapsed")
        if niche_file: 
            st.image(niche_file, width=150) # Thumbnail if needed
            
    with col_style:
        st.markdown("**Style**")
        style_file = st.file_uploader("Style Upload", type=["png", "jpg", "jpeg"], label_visibility="collapsed")
        if style_file: 
            st.image(style_file, width=150) # Thumbnail if needed
        
    st.write("")
    btn_mix = st.button("Mix & Generate Design 🪄")
        
    # The Expander exactly like your screenshot
    with st.expander("🧠 Intermediate Prompt Generation Box"):
        if st.session_state.smart_prompt:
            st.write(st.session_state.smart_prompt)
        else:
            st.caption("The AI-generated prompt will appear here after processing.")

    if btn_mix:
        if api_key and niche_file and style_file:
            try:
                client = genai.Client(api_key=api_key)
                niche_img = PIL.Image.open(niche_file)
                style_img = PIL.Image.open(style_file)
                
                with st.spinner("Analyzing images and generating prompt..."):
                    vision_prompt = "You are an expert Print-on-Demand designer. Look at Image 1 (Subject) and Image 2 (Style). Write a prompt to generate a vector T-shirt design featuring the subject from Image 1 in the exact style of Image 2. IMPORTANT: Do not describe the background of Image 2. End your prompt exactly with: 'The entire design is placed on a simple, flat, solid grey background.'"
                    
                    vision_res = client.models.generate_content(
                        model="gemini-2.5-flash",
                        contents=[niche_img, style_img, vision_prompt]
                    )
                    st.session_state.smart_prompt = vision_res.text
                
                with st.spinner("Drawing your mixed design..."):
                    res = client.models.generate_images(model="imagen-4.0-generate-001", prompt=st.session_state.smart_prompt, config={"number_of_images": num_vars})
                    save_designs(res.generated_images)
                    st.rerun() # Refresh to show the new prompt in the expander immediately
            except Exception as e:
                st.error(f"Generation Error: {e}")
        else:
            st.error("Please enter API Key and upload BOTH images.")

# ==========================================
# RESULTS GALLERY (EXACTLY AS MOCKUP)
# ==========================================
if st.session_state.generated_designs:
    st.markdown("---")
    
    col_title, col_clear = st.columns([4, 1])
    with col_title:
        st.markdown("#### 🖼️ Your Generated Designs")
    with col_clear:
        if st.button("🧹 Clear Gallery", use_container_width=True):
            st.session_state.generated_designs = []
            st.session_state.smart_prompt = ""
            st.rerun()

    # 4 Columns for the grid, mirroring the screenshot perfectly
    cols = st.columns(len(st.session_state.generated_designs))
    
    for idx, pil_img in enumerate(st.session_state.generated_designs):
        with cols[idx]:
            # Image perfectly contained
            st.image(pil_img, use_container_width=True)
            
            # Button right underneath
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
