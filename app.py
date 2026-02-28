import streamlit as st
from google import genai
from rembg import remove
import PIL.Image
import io

st.set_page_config(page_title="Design Ghost AI", layout="wide")
st.title("🎨 AI Design Generator - Professional Dashboard")

with st.sidebar:
    st.header("⚙️ Settings")
    api_key = st.text_input("Enter Google API Key", type="password")
    st.divider()
    pod_style = st.selectbox("Style Preset", 
        ["Vector Sticker", "Vintage Illustration", "Cute Kawaii", "Dark Indie Horror"])
    upscale = st.checkbox("Resizing for Amazon (4500x5400px)", value=True)

niches_text = st.text_area("Enter Niches (One per line):", placeholder="Example:\nSCP Foundation Logo\nCute Mushroom")

if st.button("Start Bulk Generation"):
    if api_key and niches_text:
        try:
            client = genai.Client(api_key=api_key)
            for niche in niches_text.split('\n'):
                if not niche.strip(): continue
                with st.status(f"Processing: {niche}"):
                    # 1. تحويل النيش لـ Prompt احترافي
                    prompt_task = f"Create a T-shirt design prompt for: '{niche}'. Style: {pod_style}, white background."
                    res = client.models.generate_content(model="gemini-2.5-flash", contents=prompt_task)
                    
                    # 2. رسم الصورة
                    img_res = client.models.generate_images(model="imagen-4.0-generate-001", prompt=res.text)
                    
                    # التصحيح هنا: زدنا باش ناخدو أول صورة من القائمة
                    raw_image = img_res.generated_images.image
                    
                    # 3. إزالة الخلفية
                    final_img = remove(raw_image)
                    
                    # 4. تغيير المقاسات لـ Amazon (4500x5400)
                    if upscale:
                        final_img = final_img.resize((4500, 5400), PIL.Image.LANCZOS)
                    
                    # عرض النتيجة
                    st.image(final_img, caption=niche, width=300)
                    
                    # إعداد التحميل
                    buf = io.BytesIO()
                    final_img.save(buf, format="PNG")
                    st.download_button(f"Download {niche}", buf.getvalue(), f"{niche}.png", "image/png")
        except Exception as e:
            st.error(f"Error: {e}")
    else:
        st.error("Please fill in the API Key and Niches!")
