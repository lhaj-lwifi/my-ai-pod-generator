import streamlit as st
from google import genai
from rembg import remove
import PIL.Image
import io

# إعداد واجهة الموقع
st.set_page_config(page_title="Design Ghost Gallery PRO", layout="wide")
st.title("🎨 3-Step Workflow: View All, Upscale & Clear")

# القائمة الجانبية للإعدادات
with st.sidebar:
    st.header("⚙️ Configuration")
    api_key = st.sidebar.text_input("Enter Google API Key", type="password")
    st.divider()
    pod_style = st.selectbox("Style Preset", 
        ["Vector Sticker", "Vintage Illustration", "Cute Kawaii", "Dark Indie Horror", "SCP Style Concept"])
    num_vars = st.slider("Number of Variations", 1, 4, 4)

# إدارة الذاكرة (Session State) باش الصور ما يغبروش
if 'all_variants' not in st.session_state: st.session_state.all_variants = []
if 'selected_img' not in st.session_state: st.session_state.selected_img = None
if 'upscaled_img' not in st.session_state: st.session_state.upscaled_img = None
if 'final_png' not in st.session_state: st.session_state.final_png = None

# --- STEP 1: GENERATE ALL VARIATIONS ---
st.header("1️⃣ Step: Generate & Choose Your Design")
niche_input = st.text_input("Design Niche:", placeholder="e.g. SCP-049 Plague Doctor")

if st.button("Generate Variations 🚀"):
    if api_key and niche_input:
        try:
            client = genai.Client(api_key=api_key)
            with st.spinner(f"Drawing {num_vars} options for you..."):
                prompt = f"Professional T-shirt design, '{niche_input}', {pod_style}, white background, bold lines, vector art."
                res = client.models.generate_images(model="imagen-4.0-generate-001", prompt=prompt, config={"number_of_images": num_vars})
                
                # تخزين كاع الصور كـ PIL Images في الذاكرة لتفادي خطأ 'bytes-like'
                st.session_state.all_variants = []
                for g_img in res.generated_images:
                    # ✅ الحل: كنتأكدو واش البيانات bytes أو صورة واجدة
                    if isinstance(g_img.image, bytes):
                        pil_img = PIL.Image.open(io.BytesIO(g_img.image))
                    else:
                        pil_img = g_img.image # هي أصلاً PIL Image
                    st.session_state.all_variants.append(pil_img)
                
                # ريست للمراحل الأخرى
                st.session_state.selected_img = None
                st.session_state.upscaled_img = None
                st.session_state.final_png = None
                st.success(f"Successfully generated {len(st.session_state.all_variants)} options!")
        except Exception as e:
            st.error(f"Error in Step 1: {e}")
    else:
        st.error("Please provide both API Key and Niche.")

# عرض معرض الصور (Gallery)
if st.session_state.all_variants:
    st.write("---")
    st.subheader("Select the best variation to continue:")
    cols = st.columns(2)
    for idx, pil_img in enumerate(st.session_state.all_variants):
        with cols[idx % 2]:
            st.image(pil_img, caption=f"Option {idx+1}", use_container_width=True)
            if st.button(f"✅ Select Option {idx+1}", key=f"sel_{idx}"):
                st.session_state.selected_img = pil_img
                st.session_state.upscaled_img = None # ريست للمرحلة الجاية
                st.session_state.final_png = None
                st.success(f"Option {idx+1} selected!")

# --- STEP 2: UPSCALE SELECTED ---
if st.session_state.selected_img:
    st.divider()
    st.header("2️⃣ Step: AI Upscale (4500x5400)")
    st.image(st.session_state.selected_img, caption="Ready for High-Res", width=300)
    
    if st.button("Upscale to 4500x5400px 📐"):
        with st.spinner("Processing High Resolution..."):
            # تكبير الصورة باستعمال LANCZOS لأفضل جودة حواف
            st.session_state.upscaled_img = st.session_state.selected_img.resize((4500, 5400), PIL.Image.Resampling.LANCZOS)
            st.success("Upscale Complete! Design is now 4500x5400px.")

# --- STEP 3: REMOVE BACKGROUND ---
if st.session_state.upscaled_img:
    st.divider()
    st.header("3️⃣ Step: Transparent Background")
    if st.button("Remove Background ✂️"):
        with st.spinner("Cutting out the design..."):
            # إزالة الخلفية
            st.session_state.final_png = remove(st.session_state.upscaled_img)
            st.success("Design is now Transparent!")

if st.session_state.final_png:
    st.image(st.session_state.final_png, caption="Final Pro Design", width=300)
    buf = io.BytesIO()
    st.session_state.final_png.save(buf, format="PNG")
    st.download_button("📥 Download Final PNG (High Quality)", buf.getvalue(), f"{niche_input}_final.png", "image/png")
