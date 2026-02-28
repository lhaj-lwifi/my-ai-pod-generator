import streamlit as st
from google import genai
from rembg import remove
import PIL.Image
import io

# إعداد واجهة الموقع
st.set_page_config(page_title="Design Ghost PRO", layout="wide")
st.title("🎨 AI Design Generator - Professional Dashboard")

with st.sidebar:
    st.header("⚙️ Configuration")
    api_key = st.text_input("Enter Google API Key", type="password")
    st.divider()
    pod_style = st.selectbox("Style Preset", 
        ["Vector Sticker", "Vintage Illustration", "Cute Kawaii", "Dark Indie Horror", "SCP Style Concept"])
    upscale = st.checkbox("Resizing for Amazon (4500x5400px)", value=True)

niches_text = st.text_area("Enter Niches (One per line):", placeholder="Example:\nSCP-049 Plague Doctor\nFunny Coding Joke", height=150)

if st.button("Start Bulk Generation 🚀"):
    if api_key and niches_text:
        try:
            client = genai.Client(api_key=api_key)
            niches = [n.strip() for n in niches_text.split('\n') if n.strip()]
            
            for niche in niches:
                with st.status(f"Processing: {niche}"):
                    # 1. إنشاء الـ Prompt
                    st.write("Generating Professional Prompt...")
                    prompt_task = f"High-quality T-shirt design, '{niche}', {pod_style}, white background, bold clean lines, vector art."
                    res = client.models.generate_content(model="gemini-2.5-flash", contents=prompt_task)
                    
                    # 2. رسم الصورة (Imagen 4.0)
                    st.write("Drawing with Imagen 4.0...")
                    img_res = client.models.generate_images(
                        model="imagen-4.0-generate-001", 
                        prompt=res.text,
                        config={"number_of_images": 1}
                    )
                    
                    # ✅ الحل الجذري لمشكل 'list' object
                    # كنتحققوا واش النتيجة قائمة ولا كائن فيه قائمة
                    if hasattr(img_res, 'generated_images'):
                        raw_image = img_res.generated_images.image
                    elif isinstance(img_res, list):
                        raw_image = img_res.image
                    else:
                        # محاولة أخيرة إذا كانت البنية مختلفة
                        raw_image = img_res.image if hasattr(img_res, 'image') else img_res

                    # 3. إزالة الخلفية
                    st.write("Removing Background...")
                    no_bg_img = remove(raw_image)
                    
                    # 4. تغيير المقاسات
                    if upscale:
                        st.write("Upscaling to 4500x5400px...")
                        final_img = no_bg_img.resize((4500, 5400), PIL.Image.LANCZOS)
                    else:
                        final_img = no_bg_img
                    
                    # عرض النتائج
                    st.divider()
                    col1, col2 = st.columns()
                    with col1:
                        st.image(final_img, caption=f"Design: {niche}", use_container_width=True)
                    with col2:
                        st.subheader(f"SEO Metadata: {niche}")
                        st.code(res.text, language="text") # عرض الـ Prompt والـ SEO
                    
                    # زر التحميل
                    buf = io.BytesIO()
                    final_img.save(buf, format="PNG")
                    st.download_button(f"Download PNG: {niche}", buf.getvalue(), f"{niche}.png", "image/png")
            
            st.balloons()
                    
        except Exception as e:
            st.error(f"Error Details: {e}")
            st.info("Check if Imagen 4.0 is enabled in your Google AI Studio account.")
    else:
        st.error("Please fill in all fields.")
