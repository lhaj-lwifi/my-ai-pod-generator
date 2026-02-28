import streamlit as st
from google import genai
from rembg import remove
import PIL.Image
import io

# إعداد واجهة الموقع
st.set_page_config(page_title="Design Ghost Gallery PRO", layout="wide")
st.title("🎨 3-Step Workflow: Generate, Upscale & Clear")

# القائمة الجانبية
with st.sidebar:
    st.header("⚙️ Settings")
    api_key = st.text_input("Enter Google API Key", type="password")
    st.divider()
    pod_style = st.selectbox("Style Preset", 
        ["Vector Sticker", "Vintage Illustration", "Cute Kawaii", "Dark Indie Horror", "SCP Concept"])
    num_vars = st.slider("Number of Variations", 1, 4, 4)

# إدارة الذاكرة (Session State) باش الصور ما يغبروش
if 'all_variants' not in st.session_state: st.session_state.all_variants = []
if 'selected_img' not in st.session_state: st.session_state.selected_img = None
if 'upscaled_img' not in st.session_state: st.session_state.upscaled_img = None
if 'final_png' not in st.session_state: st.session_state.final_png = None

# --- STEP 1: GENERATE ALL VARIATIONS ---
st.header("1️⃣ Step: Generate & Choose")
niche_input = st.text_input("Design Niche:", placeholder="e.g. SCP-049 Plague Doctor")

if st.button("Generate Variations 🚀"):
    if api_key and niche_input:
        try:
            client = genai.Client(api_key=api_key)
            with st.spinner(f"Drawing {num_vars} options..."):
                prompt = f"Professional T-shirt design, '{niche_input}', {pod_style}, white background, bold lines, vector art."
                res = client.models.generate_images(model="imagen-4.0-generate-001", prompt=prompt, config={"number_of_images": num_vars})
                
                # تخزين كاع الصور كـ PIL Images في الذاكرة
                st.session_state.all_variants = []
                for g_img in res.generated_images:
                    st.session_state.all_variants.append(PIL.Image.open(io.BytesIO(g_img.image)))
                
                # ريست للمراحل الأخرى
                st.session_state.selected_img = None
                st.session_state.upscaled_img = None
                st.session_state.final_png = None
        except Exception as e:
            st.error(f"Error: {e}")

# عرض معرض الصور (Gallery)
if st.session_state.all_variants:
    cols = st.columns(2)
    for idx, pil_img in enumerate(st.session_state.all_variants):
        with cols[idx % 2]:
            st.image(pil_img, caption=f"Option {idx+1}", use_container_width=True)
            if st.button(f"✅ Select Option {idx+1}", key=f"sel_{idx}"):
                st.session_state.selected_img = pil_img
                st.success(f"Option {idx+1} selected for next steps!")

# --- STEP 2: UPSCALE SELECTED ---
if st.session_state.selected_img:
    st.divider()
    st.header("2️⃣ Step: AI Upscale (4500x5400)")
    st.image(st.session_state.selected_img, caption="Current Selection", width=300)
    
    if st.button("Upscale to 4500x5400px 📐"):
        with st.spinner("Processing High-Res..."):
            st.session_state.upscaled_img = st.session_state.selected_img.resize((4500, 5400), PIL.Image.Resampling.LANCZOS)
            st.success("Upscale Done!")

# --- STEP 3: REMOVE BACKGROUND ---
if st.session_state.upscaled_img:
    st.divider()
    st.header("3️⃣ Step: Make Transparent")
    if st.button("Remove Background ✂️"):
        with st.spinner("Removing background..."):
            st.session_state.final_png = remove(st.session_state.upscaled_img)
            st.success("Design is now Transparent!")

if st.session_state.final_png:
    st.image(st.session_state.final_png, caption="Final Pro Design", width=300)
    buf = io.BytesIO()
    st.session_state.final_png.save(buf, format="PNG")
    st.download_button("📥 Download Final PNG", buf.getvalue(), f"{niche_input}_final.png", "image/png")
