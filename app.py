import streamlit as st
from google import genai
from rembg import remove
import PIL.Image
import io

# إعداد الصفحة واجهة عريضة
st.set_page_config(page_title="Design Ghost Gallery", layout="wide", page_icon="🎨")
st.title("🎨 AI Design Generator - Multi-Choice Gallery")

with st.sidebar:
    st.header("⚙️ Configuration")
    api_key = st.text_input("Enter Google API Key", type="password")
    
    st.divider()
    st.header("🎨 Style & Quantity")
    pod_style = st.selectbox("Style Preset", 
        ["Vector Sticker", "Vintage Illustration", "Cute Kawaii", "Dark Indie Horror", "SCP Style Concept"])
    
    # ميزة اختيار عدد الصور
    num_images = st.slider("Number of Variations per Niche", 1, 4, 4)
    
    upscale = st.checkbox("Resizing for Amazon (4500x5400px)", value=True)

# واجهة إدخال النيشات
niche_input = st.text_input("Enter your Niche:", placeholder="e.g. SCP-173 Mascot")

if st.button("Generate Variations 🚀"):
    if api_key and niche_input:
        try:
            client = genai.Client(api_key=api_key)
            
            with st.status(f"Generating {num_images} variations for: {niche_input}..."):
                # 1. إنشاء الـ Prompt
                st.write("📝 Designing Prompts...")
                prompt_task = f"High-quality T-shirt design, '{niche_input}', {pod_style}, white background, bold clean lines, vector art."
                res = client.models.generate_content(model="gemini-2.5-flash", contents=prompt_task)
                
                # 2. رسم الصور (Imagen 4.0)
                st.write(f"🎨 Drawing {num_images} images...")
                img_res = client.models.generate_images(
                    model="imagen-4.0-generate-001", 
                    prompt=res.text,
                    config={"number_of_images": num_images} # طلب عدد محدد من الصور
                )
                
                # عرض الصور في أعمدة (Grid)
                st.divider()
                st.subheader(f"Results for: {niche_input}")
                
                # إنشاء أعمدة لعرض الصور (مثلاً 2 في كل سطر)
                cols = st.columns(2) 
                
                # 3. معالجة وعرض كل صورة في المجموعة
                for idx, gen_img in enumerate(img_res.generated_images):
                    with cols[idx % 2]: # توزيع الصور على الأعمدة
                        st.write(f"Option {idx + 1}")
                        
                        # إزالة الخلفية لكل صورة
                        raw_image = gen_img.image
                        no_bg_img = remove(raw_image)
                        
                        # التكبير إذا تم تفعيله
                        if upscale:
                            final_img = no_bg_img.resize((4500, 5400), PIL.Image.LANCZOS)
                        else:
                            final_img = no_bg_img
                        
                        # عرض الصورة
                        st.image(final_img, use_container_width=True)
                        
                        # زر التحميل لكل خيار
                        buf = io.BytesIO()
                        final_img.save(buf, format="PNG")
                        st.download_button(
                            label=f"Download Option {idx + 1}", 
                            data=buf.getvalue(), 
                            file_name=f"{niche_input}_v{idx+1}.png", 
                            mime="image/png",
                            key=f"btn_{niche_input}_{idx}" # مفتاح فريد لكل زر
                        )
                
            st.balloons()
            
            # عرض الـ SEO المقترح أسفل الصور
            st.divider()
            st.subheader("SEO Metadata (Suggested)")
            st.code(res.text, language="text")

        except Exception as e:
            st.error(f"Error: {e}")
    else:
        st.error("Please fill in the API Key and Niche.")
