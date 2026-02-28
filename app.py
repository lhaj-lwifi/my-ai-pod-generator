import streamlit as st
from google import genai
from rembg import remove
import PIL.Image
import io

# إعداد الصفحة
st.set_page_config(page_title="Design Ghost PRO", layout="wide", page_icon="🎨")
st.title("🎨 Professional AI Design Studio")

# القائمة الجانبية
with st.sidebar:
    st.header("⚙️ Configuration")
    api_key = st.text_input("Enter Google API Key", type="password")
    st.divider()
    pod_style = st.selectbox("Style Preset", 
        ["Vector Sticker", "Vintage Illustration", "Cute Kawaii", "Dark Indie Horror", "SCP Style"])
    num_images = st.slider("Number of Variations", 1, 4, 4)

# 1. إدارة حالة الصور (Session State) باش ما يغبروش ملي نضغطو على زر
if 'generated_images' not in st.session_state:
    st.session_state.generated_images = []
if 'last_niche' not in st.session_state:
    st.session_state.last_niche = ""

# واجهة إدخال النيش
niche_input = st.text_input("Enter your Niche:", placeholder="e.g. SCP-049 Mascot")

if st.button("Generate Variations 🚀"):
    if api_key and niche_input:
        try:
            client = genai.Client(api_key=api_key)
            with st.spinner(f"Generating {num_images} variations..."):
                prompt_task = f"High-quality T-shirt design, '{niche_input}', {pod_style}, white background, bold lines, vector art."
                res = client.models.generate_content(model="gemini-2.5-flash", contents=prompt_task)
                
                img_res = client.models.generate_images(
                    model="imagen-4.0-generate-001", 
                    prompt=res.text,
                    config={"number_of_images": num_images}
                )
                
                # حفظ الصور في الـ Session State
                st.session_state.generated_images = [img.image for img in img_res.generated_images]
                st.session_state.last_niche = niche_input
                st.session_state.seo_text = res.text
        except Exception as e:
            st.error(f"Error: {e}")
    else:
        st.error("Please provide API Key and Niche.")

# 2. عرض الصور (الـ Gallery) ومعالجتها بشكل منفصل
if st.session_state.generated_images:
    st.divider()
    st.subheader(f"Results for: {st.session_state.last_niche}")
    
    cols = st.columns(2)
    for idx, img_data in enumerate(st.session_state.generated_images):
        with cols[idx % 2]:
            # تحويل البيانات لصورة PIL للعرض
            pil_img = PIL.Image.open(io.BytesIO(img_data))
            st.image(pil_img, caption=f"Option {idx+1}", use_container_width=True)
            
            # زر معالجة هاد الصورة بوحدها
            if st.button(f"🪄 Process Option {idx+1}", key=f"proc_{idx}"):
                with st.spinner("Removing background & Upscaling to 4500x5400px..."):
                    # إزالة الخلفية
                    no_bg = remove(pil_img)
                    # التكبير لمقاسات Merch by Amazon
                    final_img = no_bg.resize((4500, 5400), PIL.Image.LANCZOS)
                    
                    st.success("Ready for Upload!")
                    st.image(final_img, caption="Final Transparent PNG", width=300)
                    
                    # زر التحميل النهائي
                    buf = io.BytesIO()
                    final_img.save(buf, format="PNG")
                    st.download_button(
                        label=f"💾 Download Final PNG",
                        data=buf.getvalue(),
                        file_name=f"{st.session_state.last_niche}_final.png",
                        mime="image/png",
                        key=f"dl_{idx}"
                    )

    st.divider()
    st.subheader("SEO Metadata")
    st.info(st.session_state.get('seo_text', ''))
