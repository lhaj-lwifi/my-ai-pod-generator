import streamlit as st
from google import genai
import PIL.Image
import io

st.set_page_config(page_title="Design Ghost Studio PRO", layout="wide", page_icon="🎨")
st.title("🎨 AI Design Generator - Pro Studio")
st.markdown("##### *Optimized for Creation (Upscaling & BG Removal handled externally)*")

with st.sidebar:
    st.header("⚙️ Configuration")
    api_key = st.text_input("Enter Google API Key", type="password")
    num_vars = st.slider("Number of Variations", 1, 4, 4)
    st.info("💡 Tip: Use Canva for background removal for perfect results.")

# دوال لتخزين الصور في الذاكرة باش ما يغبروش
if 'generated_designs' not in st.session_state:
    st.session_state.generated_designs = []

def save_designs(response_images):
    st.session_state.generated_designs = []
    for g_img in response_images:
        raw_bytes = g_img.image.image_bytes
        pil_img = PIL.Image.open(io.BytesIO(raw_bytes))
        st.session_state.generated_designs.append(pil_img)

# تقسيم الواجهة لجوج تبويبات (Tabs)
tab1, tab2 = st.tabs(["✍️ 1. Text to Design", "🖼️ 2. Niche + Style Mixer (PRO)"])

# ==========================================
# TAB 1: TEXT TO DESIGN
# ==========================================
with tab1:
    st.header("Create from Text")
    col1, col2 = st.columns([3, 1])
    with col1:
        niche_text = st.text_input("Design Niche:", placeholder="e.g. SCP-049 Plague Doctor minimalist")
    with col2:
        pod_style = st.selectbox("Style Preset", ["Vector Sticker", "Vintage Retro", "Dark Indie Horror", "Cute Kawaii"])
    
    if st.button("Generate from Text 🚀", key="btn_tab1"):
        if api_key and niche_text:
            try:
                client = genai.Client(api_key=api_key)
                with st.spinner("Drawing your idea..."):
                    prompt = f"Professional T-shirt design, '{niche_text}', {pod_style}, centered completely within frame, isolated on a solid flat neutral grey background (#808080), vector art style, clean edges."
                    res = client.models.generate_images(model="imagen-4.0-generate-001", prompt=prompt, config={"number_of_images": num_vars})
                    save_designs(res.generated_images)
                    st.success("Designs Ready!")
            except Exception as e:
                st.error(f"Error: {e}")
        else:
            st.error("Please enter API Key and Niche.")

# ==========================================
# TAB 2: NICHE + STYLE MIXER
# ==========================================
with tab2:
    st.header("Mix Images (Style Transfer)")
    st.write("Upload a subject (Niche) and a reference (Style) to create something unique.")
    
    col_niche, col_style = st.columns(2)
    with col_niche:
        niche_file = st.file_uploader("1️⃣ Upload Niche Image (Subject)", type=["png", "jpg", "jpeg"])
    with col_style:
        style_file = st.file_uploader("2️⃣ Upload Style Image (Reference)", type=["png", "jpg", "jpeg"])
        
    if st.button("Mix & Generate Design 🪄", key="btn_tab2"):
        if api_key and niche_file and style_file:
            try:
                client = genai.Client(api_key=api_key)
                niche_img = PIL.Image.open(niche_file)
                style_img = PIL.Image.open(style_file)
                
                with st.spinner("1. Analyzing images & writing smart prompt..."):
                    # استعمال Gemini 2.5 Flash باش يحلل الصور ويستخرج السر ديالهم
                    vision_prompt = "You are an expert Print-on-Demand designer. Look at Image 1 (Subject) and Image 2 (Style Reference). Write a highly detailed image generation prompt to create a professional T-shirt vector design. The design MUST feature the main subject from Image 1, but it MUST be drawn entirely in the artistic style, color palette, and mood of Image 2. End the prompt with: 'centered, isolated on a solid flat neutral grey background (#808080), clean vector edges.'"
                    
                    vision_res = client.models.generate_content(
                        model="gemini-2.5-flash",
                        contents=[niche_img, style_img, vision_prompt]
                    )
                    smart_prompt = vision_res.text
                    st.info(f"🧠 AI Created Prompt: {smart_prompt}")
                
                with st.spinner("2. Drawing mixed design..."):
                    # رسم التصميم بناء على الـ Prompt الذكي
                    res = client.models.generate_images(model="imagen-4.0-generate-001", prompt=smart_prompt, config={"number_of_images": num_vars})
                    save_designs(res.generated_images)
                    st.success("Mixed Designs Ready!")
            except Exception as e:
                st.error(f"Error: {e}")
        else:
            st.error("Please enter API Key and upload BOTH images.")

# ==========================================
# RESULTS GALLERY (Shared for both tabs)
# ==========================================
if st.session_state.generated_designs:
    st.markdown("---")
    st.subheader("🖼️ Your Generated Designs")
    cols = st.columns(2)
    for idx, pil_img in enumerate(st.session_state.generated_designs):
        with cols[idx % 2]:
            st.image(pil_img, caption=f"Variation {idx+1}", use_container_width=True)
            
            # زر التحميل المباشر للصورة (1024x1024 بخلفية رمادية) واجدة لكانفا
            buf = io.BytesIO()
            pil_img.save(buf, format="PNG")
            st.download_button(
                label=f"📥 Download Design {idx+1}",
                data=buf.getvalue(),
                file_name=f"Design_Raw_v{idx+1}.png",
                mime="image/png",
                key=f"dl_btn_{idx}"
            )
