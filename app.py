import streamlit as st
from google import genai
from rembg import remove
import PIL.Image
import io

st.set_page_config(page_title="Design Ghost Studio PRO", layout="wide", page_icon="🎨")
st.title("🎨 AI Design Generator - Pro Studio")

with st.sidebar:
    st.header("⚙️ Configuration")
    api_key = st.text_input("Enter Google API Key", type="password")
    st.divider()
    pod_style = st.selectbox("Style Preset", 
        ["Vector Sticker", "Vintage Illustration", "Cute Kawaii", "Dark Indie Horror", "Minimalist Typography"])
    num_vars = st.slider("Number of Variations", 1, 4, 4)

if 'all_variants' not in st.session_state: st.session_state.all_variants = []
if 'selected_img' not in st.session_state: st.session_state.selected_img = None
if 'no_bg_img' not in st.session_state: st.session_state.no_bg_img = None
if 'final_png' not in st.session_state: st.session_state.final_png = None

def reset_studio():
    st.session_state.all_variants = []
    st.session_state.selected_img = None
    st.session_state.no_bg_img = None
    st.session_state.final_png = None

# --- STEP 1: GENERATE ---
st.header("1️⃣ Step: Generate Variations")
col_input, col_reset = st.columns([4, 1])
with col_input:
    niche_input = st.text_input("Design Niche:", placeholder="e.g. Funny programming quote")
with col_reset:
    st.write("")
    st.write("")
    if st.button("🔄 Start Fresh"):
        reset_studio()
        st.rerun()

if st.button("Generate Designs 🚀"):
    if api_key and niche_input:
        reset_studio()
        try:
            client = genai.Client(api_key=api_key)
            with st.spinner(f"Drawing {num_vars} pro options..."):
                prompt = f"Professional T-shirt design, '{niche_input}', {pod_style}, centered completely within frame, isolated on a solid flat neutral grey background (#808080), absolutely no gradients or shadows on the background, vector art style, perfect typography and correct spelling."
                
                res = client.models.generate_images(model="imagen-4.0-generate-001", prompt=prompt, config={"number_of_images": num_vars})
                
                for g_img in res.generated_images:
                    raw_bytes = g_img.image.image_bytes
                    pil_img = PIL.Image.open(io.BytesIO(raw_bytes))
                    st.session_state.all_variants.append(pil_img)
                
                st.success("Variations generated!")
        except Exception as e:
            st.error(f"Generation Error: {e}")

# عرض معرض الصور
if st.session_state.all_variants:
    st.write("---")
    st.subheader("Select the best variation:")
    cols = st.columns(2)
    for idx, pil_img in enumerate(st.session_state.all_variants):
        with cols[idx % 2]:
            st.image(pil_img, caption=f"Option {idx+1}", use_container_width=True)
            if st.button(f"✅ Select Option {idx+1}", key=f"sel_{idx}"):
                st.session_state.selected_img = pil_img
                st.session_state.no_bg_img = None 
                st.session_state.final_png = None

# --- STEP 2: REMOVE BACKGROUND FIRST (Smart Move) ---
if st.session_state.selected_img:
    st.divider()
    st.header("2️⃣ Step: Remove Background (Fast & Clean)")
    st.image(st.session_state.selected_img, caption="Original 1024x1024", width=300)
    
    if st.button("✂️ Remove Background Now"):
        with st.spinner("Extracting design with Alpha Matting..."):
            # دابا العزل غيكون طيارة حيت الصورة باقا صغيرة، ومستحيل يطيح السيرفر
            st.session_state.no_bg_img = remove(
                st.session_state.selected_img,
                alpha_matting=True,
                alpha_matting_foreground_threshold=240,
                alpha_matting_background_threshold=10,
                alpha_matting_erode_size=5
            )
            st.success("Background beautifully removed!")

# --- STEP 3: UPSCALE THE TRANSPARENT IMAGE ---
if st.session_state.no_bg_img:
    st.divider()
    st.header("3️⃣ Step: Upscale & Preview")
    
    if st.button("📐 Upscale to 4500x5400px"):
        with st.spinner("Upscaling the transparent PNG for Amazon..."):
            # تكبير الصورة وهي ديجا شفافة
            st.session_state.final_png = st.session_state.no_bg_img.resize((4500, 5400), PIL.Image.Resampling.LANCZOS)
            st.success("High-Res Ready!")

if st.session_state.final_png:
    st.write("---")
    st.subheader("👕 T-Shirt Preview")
    
    preview_col1, preview_col2 = st.columns(2)
    with preview_col1:
        st.write("On Black Background")
        black_bg = PIL.Image.new("RGB", st.session_state.final_png.size, (0, 0, 0))
        black_bg.paste(st.session_state.final_png, (0, 0), st.session_state.final_png)
        st.image(black_bg, use_container_width=True)
        
    with preview_col2:
        st.write("On White Background")
        st.image(st.session_state.final_png, use_container_width=True)

    st.write("---")
    buf = io.BytesIO()
    st.session_state.final_png.save(buf, format="PNG")
    st.download_button(
        label="📥 Download Final 4500x5400 PNG", 
        data=buf.getvalue(), 
        file_name=f"Design_Pro_Final.png", 
        mime="image/png",
        use_container_width=True
    )
