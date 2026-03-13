import streamlit as st
from google import genai
import PIL.Image
import io

st.set_page_config(page_title="Design Ghost Studio PRO", layout="wide", page_icon="🎨")
st.title("🎨 AI Design Generator - Pro Studio")
st.markdown("##### *Optimized for Creation (Upscaling & BG Removal handled in Canva)*")

with st.sidebar:
    st.header("⚙️ Configuration")
    api_key = st.text_input("Enter Google API Key", type="password")
    num_vars = st.slider("Number of Variations", 1, 4, 4)
    st.divider()
    
    # ✅ ميزة جديدة: اختيار لون الكروما (Chroma Key) لتسهيل العزل في كانفا
    st.header("🎨 Chroma Background")
    bg_color = st.selectbox(
        "Force Background Color:", 
        ["Dark Grey", "Neon Green", "Hot Pink", "Pitch Black"],
        help="Choose a background color that is NOT in your design to make Canva's BG Remover work perfectly."
    )
    st.info("💡 Tip: Download the results and use Canva's BG Remover.")

# تخزين الصور في الذاكرة
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
                with st.spinner(f"Drawing on a {bg_color} background..."):
                    # ✅ أوامر قاهرة للموديل باش يتفادى اللون الأبيض
                    prompt = f"Vector illustration for a T-shirt, '{niche_text}', style: {pod_style}. CRITICAL INSTRUCTION: The background of the entire image MUST be a completely solid, flat {bg_color.upper()}. ABSOLUTELY NO WHITE BACKGROUND. NO gradients, NO scenery, NO shadows on the background. The subject must be perfectly isolated against this flat {bg_color.upper()} color."
                    
                    res = client.models.generate_images(model="imagen-4.0-generate-001", prompt=prompt, config={"number_of_images": num_vars})
                    save_designs(res.generated_images)
                    st.success("Designs Ready!")
            except Exception as e:
                st.error(f"Generation Error: {e}")
        else:
            st.error("Please enter API Key and Niche.")

# ==========================================
# TAB 2: NICHE + STYLE MIXER
# ==========================================
with tab2:
    st.header("Mix Images (Style Transfer)")
    col_niche, col_style = st.columns(2)
    with col_niche:
        niche_file = st.file_uploader("1️⃣ Upload Niche Image (Subject)", type=["png", "jpg", "jpeg"])
        if niche_file: st.image(niche_file, caption="Subject Preview", width=150)
            
    with col_style:
        style_file = st.file_uploader("2️⃣ Upload Style Image (Reference)", type=["png", "jpg", "jpeg"])
        if style_file: st.image(style_file, caption="Style Preview", width=150)
        
    if st.button("Mix & Generate Design 🪄", key="btn_tab2"):
        if api_key and niche_file and style_file:
            try:
                client = genai.Client(api_key=api_key)
                niche_img = PIL.Image.open(niche_file)
                style_img = PIL.Image.open(style_file)
                
                with st.spinner("Analyzing style & enforcing background color..."):
                    # ✅ إجبار Gemini باش يكتب الـ Prompt وفيه أوامر الخلفية الصارمة
                    vision_prompt = f"You are an expert Print-on-Demand designer. Look at Image 1 (Subject) and Image 2 (Style). Write a prompt to generate a vector T-shirt design. The design MUST feature the main subject from Image 1, drawn entirely in the artistic style of Image 2. CRITICAL RULES: 1. Completely IGNORE the background of Image 2. 2. You MUST end your prompt exactly with this sentence: 'The entire background MUST be a completely solid, flat {bg_color.upper()}. ABSOLUTELY NO WHITE BACKGROUND. NO gradients or scenery. The subject is isolated on this {bg_color.upper()} background.'"
                    
                    vision_res = client.models.generate_content(
                        model="gemini-2.5-flash",
                        contents=[niche_img, style_img, vision_prompt]
                    )
                    smart_prompt = vision_res.text
                    
                    res = client.models.generate_images(model="imagen-4.0-generate-001", prompt=smart_prompt, config={"number_of_images": num_vars})
                    save_designs(res.generated_images)
                    st.success("Mixed Designs Ready!")
            except Exception as e:
                st.error(f"Generation Error: {e}")
        else:
            st.error("Please enter API Key and upload BOTH images.")

# ==========================================
# RESULTS GALLERY
# ==========================================
if st.session_state.generated_designs:
    st.markdown("---")
    st.subheader("🖼️ Your Generated Designs")
    cols = st.columns(2)
    for idx, pil_img in enumerate(st.session_state.generated_designs):
        with cols[idx % 2]:
            st.image(pil_img, caption=f"Variation {idx+1}", use_container_width=True)
            
            buf = io.BytesIO()
            pil_img.save(buf, format="PNG")
            st.download_button(
                label=f"📥 Download Design {idx+1}",
                data=buf.getvalue(),
                file_name=f"Design_Raw_v{idx+1}.png",
                mime="image/png",
                key=f"dl_btn_{idx}"
            )
