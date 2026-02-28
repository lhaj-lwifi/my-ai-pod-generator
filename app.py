import streamlit as st
from google import genai
from rembg import remove
import PIL.Image
import io

# إعداد واجهة الموقع
st.set_page_config(page_title="Design Ghost 3-Step", layout="wide")
st.title("🛠️ 3-Step Design Workflow (Pro Edition)")

# القائمة الجانبية للإعدادات
with st.sidebar:
    st.header("⚙️ API Configuration")
    api_key = st.text_input("Enter Google API Key", type="password")
    st.divider()
    pod_style = st.selectbox("Style Preset", 
        ["Vector Sticker", "Vintage Illustration", "Cute Kawaii", "Dark Indie Horror", "SCP Concept"])

# إدارة حالة الصور (Memory)
if 'raw_img' not in st.session_state: st.session_state.raw_img = None
if 'upscaled_img' not in st.session_state: st.session_state.upscaled_img = None
if 'final_img' not in st.session_state: st.session_state.final_img = None

# --- STAGE 1: DESIGN GENERATION ---
st.header("1️⃣ Step: Generate Design")
niche_input = st.text_input("Niche Topic:", placeholder="e.g. SCP-049 Plague Doctor")

if st.button("Generate Image 🚀"):
    if api_key and niche_input:
        try:
            client = genai.Client(api_key=api_key)
            with st.spinner("Drawing..."):
                prompt = f"Professional T-shirt design, '{niche_input}', {pod_style}, white background, bold clean lines, vector art."
                res = client.models.generate_images(model="imagen-4.0-generate-001", prompt=prompt, config={"number_of_images": 1})
                
                # حفظ الصورة الخام
                img_data = io.BytesIO(res.generated_images.image)
                st.session_state.raw_img = PIL.Image.open(img_data)
                # ريست للمراحل الجاية
                st.session_state.upscaled_img = None
                st.session_state.final_img = None
        except Exception as e:
            st.error(f"Error: {e}")
    else:
        st.error("Missing API Key or Niche!")

if st.session_state.raw_img:
    st.image(st.session_state.raw_img, caption="Raw Generation (1024x1024)", width=300)

    # --- STAGE 2: UPSCALE ---
    st.divider()
    st.header("2️⃣ Step: Upscale to 4500x5400px")
    if st.button("Upscale for Merch by Amazon 📐"):
        with st.spinner("Resizing to 4500x5400..."):
            # تكبير الصورة باستعمال LANCZOS لأفضل جودة حواف
            st.session_state.upscaled_img = st.session_state.raw_img.resize((4500, 5400), PIL.Image.Resampling.LANCZOS)
            st.success("Upscaling Complete!")

    if st.session_state.upscaled_img:
        st.info("Image is now 4500x5400px. High resolution ready.")

        # --- STAGE 3: REMOVE BACKGROUND ---
        st.divider()
        st.header("3️⃣ Step: Remove Background")
        if st.button("Make Transparent ✂️"):
            with st.spinner("Removing background..."):
                st.session_state.final_img = remove(st.session_state.upscaled_img)
                st.success("Background Removed!")

        if st.session_state.final_img:
            st.image(st.session_state.final_img, caption="Final Transparent PNG", width=300)
            
            # زر التحميل النهائي
            buf = io.BytesIO()
            st.session_state.final_img.save(buf, format="PNG")
            st.download_button(
                label="📥 Download Final Design",
                data=buf.getvalue(),
                file_name=f"{niche_input.replace(' ', '_')}_final.png",
                mime="image/png"
            )
