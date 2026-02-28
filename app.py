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
        client = genai.Client(api_key=api_key)
        for niche in niches_text.split('\n'):
            if not niche.strip(): continue
            with st.status(f"Processing: {niche}"):
                # Prompt Generation
                prompt = f"Professional T-shirt design, '{niche}', {pod_style}, white background, high contrast."
                res = client.models.generate_content(model="gemini-2.5-flash", contents=prompt)
                
                # Image Generation
                img_res = client.models.generate_images(model="imagen-4.0-generate-001", prompt=res.text)
                final_img = remove(img_res.generated_images.image)
                
                if upscale:
                    final_img = final_img.resize((4500, 5400), PIL.Image.LANCZOS)
                
                st.image(final_img, caption=niche, width=250)
                buf = io.BytesIO()
                final_img.save(buf, format="PNG")
                st.download_button(f"Download {niche}", buf.getvalue(), f"{niche}.png", "image/png")
    else:
        st.error("Please fill in the API Key and Niches!")
