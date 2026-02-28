import streamlit as st
from google import genai
from rembg import remove
import PIL.Image
import io

# إعداد الصفحة
st.set_page_config(page_title="POD Design Master", layout="wide")
st.title("🎨 AI Design Generator - Professional Dashboard")

# القائمة الجانبية
with st.sidebar:
    st.header("⚙️ Configuration")
    api_key = st.text_input("Enter Google API Key", type="password")
    st.divider()
    pod_style = st.selectbox("Style Preset", 
        ["Vector Sticker", "Vintage Illustration", "Cute Kawaii", "Dark Indie Horror", "Science Doodle"])
    upscale = st.checkbox("Resizing for Amazon (4500x5400px)", value=True)

# واجهة إدخال النيشات
niches_text = st.text_area("Enter Niches (One per line):", placeholder="Example:\nSCP-049 Plague Doctor\nFunny Coding Joke")

if st.button("Start Bulk Generation"):
    if api_key and niches_text:
        try:
            client = genai.Client(api_key=api_key)
            for niche in niches_text.split('\n'):
                if not niche.strip(): continue
                
                with st.status(f"Working on: {niche}"):
                    # 1. إنشاء الـ Prompt والـ SEO
                    st.write("Generating Prompt & Tags...")
                    seo_task = f"Create a T-shirt design prompt, an SEO Title, and 15 tags for: '{niche}'. Style: {pod_style}. Return it clearly."
                    res = client.models.generate_content(model="gemini-2.5-flash", contents=seo_task)
                    
                    # 2. رسم الصورة (Imagen 4.0)
                    st.write("Drawing Image...")
                    img_res = client.models.generate_images(model="imagen-4.0-generate-001", prompt=res.text)
                    
                    # ✅ الحل: أخد أول صورة من القائمة باستعمال
                    raw_image = img_res.generated_images.image
                    
                    # 3. إزالة الخلفية
                    st.write("Removing Background...")
                    no_bg_img = remove(raw_image)
                    
                    # 4. التكبير لمقاسات أمازون
                    if upscale:
                        st.write("Upscaling to 4500x5400...")
                        final_img = no_bg_img.resize((4500, 5400), PIL.Image.LANCZOS)
                    else:
                        final_img = no_bg_img
                    
                    # عرض النتائج في الموقع
                    col1, col2 = st.columns()
                    with col1:
                        st.image(final_img, width=250)
                    with col2:
                        st.subheader(f"SEO for: {niche}")
                        st.info(res.text) # عرض التاغات والعنوان
                    
                    # زر التحميل
                    buf = io.BytesIO()
                    final_img.save(buf, format="PNG")
                    st.download_button(f"Download PNG: {niche}", buf.getvalue(), f"{niche}.png", "image/png")
                    
        except Exception as e:
            st.error(f"Error Details: {e}")
    else:
        st.error("Please provide both API Key and Niches.")
