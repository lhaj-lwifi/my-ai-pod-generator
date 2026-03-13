import streamlit as st
from google import genai
import PIL.Image
import io

st.set_page_config(page_title="Design Ghost Studio PRO", layout="wide", page_icon="🎨")
st.title("🎨 AI Design Generator - Pro Studio")
st.markdown("##### *Optimized for Creation (Upscaling & BG Removal handled in Canva)*")

with st.sidebar:
    st.header("⚙️ Configuration")
    api_key = st.text_input("Enter Google API Key", type="password")
    num_vars = st.slider("Number of Variations", 1, 4, 4)
    st.info("💡 Tip: Download the results and use Canva's BG Remover for perfect edges.")

# تخزين الصور في الذاكرة
if 'generated_designs' not in st.session_state:
    st.session_state.generated_designs = []

# دالة ذكية ومحمية لاستخراج الصور (كتمنع أخطاء bytes و list)
def save_designs(response_images):
    st.session_state.generated_designs = []
    for g_img in response_images:
        try:
            # التحقق من بنية البيانات باش نتفاداو الأخطاء
            if hasattr(g_img, 'image') and hasattr(g_img.image, 'image_bytes'):
                raw_bytes = g_img.image.image_bytes
                pil_img = PIL.Image.open(io.BytesIO(raw_bytes))
            elif isinstance(g_img.image, bytes):
                pil_img = PIL.Image.open(io.BytesIO(g_img.image))
            else:
                pil_img = g_img.image 
            
            st.session_state.generated_designs.append(pil_img)
        except Exception as e:
            st.error(f"Error extracting image: {e}")

tab1, tab2 = st.tabs(["✍️ 1. Text to Design", "🖼️ 2. Niche + Style Mixer (PRO)"])

# ==========================================
# TAB 1: TEXT TO DESIGN
# ==========================================
with tab1:
    st.header("Create from Text")
    col1, col2 = st.columns([3, 1])
    with col1:
        niche_text = st.text_input("Design Niche:", placeholder="e.g. SCP-049 Plague Doctor minimalist")
    with col2:
        pod_style = st.selectbox("Style Preset", ["Vector Sticker", "Vintage Retro", "Dark Indie Horror", "Cute Kawaii"])
    
    if st.button("Generate from Text 🚀", key="btn_tab1"):
        if api_key and niche_text:
            try:
                client = genai.Client(api_key=api_key)
                with st.spinner("Drawing your idea..."):
                    prompt = f"Professional T-shirt design, '{niche_text}', {pod_style}, centered completely within frame, STRICTLY isolated on a solid flat neutral grey background (#808080), absolutely no gradients, no scenery, vector art style, clean edges."
                    res = client.models.generate_images(model="imagen-4.0-generate-001", prompt=prompt, config={"number_of_images": num_vars})
                    save_designs(res.generated_images)
                    st.success("Designs Ready!")
            except Exception as e:
                st.error(f"Generation Error: {e}")
        else:
            st.error("Please enter API Key and Niche.")

# ==========================================
# TAB 2: NICHE + STYLE MIXER
# ==========================================
with tab2:
    st.header("Mix Images (Style Transfer)")
    st.write("Upload a subject (Niche) and a reference (Style). The AI will work its magic in the background.")
    
    col_niche, col_style = st.columns(2)
    with col_niche:
        niche_file = st.file_uploader("1️⃣ Upload Niche Image (Subject)", type=["png", "jpg", "jpeg"])
        # ✅ إضافة الريفيو ديال النيش
        if niche_file:
            st.image(niche_file, caption="Subject Preview", width=150)
            
    with col_style:
        style_file = st.file_uploader("2️⃣ Upload Style Image (Reference)", type=["png", "jpg", "jpeg"])
        # ✅ إضافة الريفيو ديال الستايل
        if style_file:
            st.image(style_file, caption="Style Preview", width=150)
        
    if st.button("Mix & Generate Design 🪄", key="btn_tab2"):
        if api_key and niche_file and style_file:
            try:
                client = genai.Client(api_key=api_key)
                niche_img = PIL.Image.open(niche_file)
                style_img = PIL.Image.open(style_file)
                
                with st.spinner("Analyzing style and drawing in the background..."):
                    # ✅ هندسة أوامر صارمة جداً لفرض الخلفية الرمادية ومنع وصف خلفية الستايل
                    vision_prompt = "You are an expert Print-on-Demand designer. Look at Image 1 (Subject) and Image 2 (Style). Write a prompt to generate a vector T-shirt design. The design MUST feature the main subject from Image 1, drawn entirely in the artistic style, colors, and mood of Image 2. CRITICAL INSTRUCTION: Completely IGNORE the background of Image 2. Do NOT describe any background elements, scenes, or environments. The final design MUST be strictly isolated. End your prompt with: 'isolated perfectly on a solid flat neutral grey background (#808080), vector art style, clean edges, ready for background removal'."
                    
                    # الـ AI كيصاوب الوصف في الخفاء (مابقاش كيبان في الموقع)
                    vision_res = client.models.generate_content(
                        model="gemini-2.5-flash",
                        contents=[niche_img, style_img, vision_prompt]
                    )
                    smart_prompt = vision_res.text
                    
                    # الرسم مباشرة بالوصف السري
                    res = client.models.generate_images(model="imagen-4.0-generate-001", prompt=smart_prompt, config={"number_of_images": num_vars})
                    save_designs(res.generated_images)
                    st.success("Mixed Designs Ready!")
            except Exception as e:
                st.error(f"Generation Error: {e}")
        else:
            st.error("Please enter API Key and upload BOTH images.")

# ==========================================
# RESULTS GALLERY
# ==========================================
if st.session_state.generated_designs:
    st.markdown("---")
    st.subheader("🖼️ Your Generated Designs")
    cols = st.columns(2)
    for idx, pil_img in enumerate(st.session_state.generated_designs):
        with cols[idx % 2]:
            st.image(pil_img, caption=f"Variation {idx+1}", use_container_width=True)
            
            buf = io.BytesIO()
            pil_img.save(buf, format="PNG")
            st.download_button(
                label=f"📥 Download Design {idx+1}",
                data=buf.getvalue(),
                file_name=f"Design_Raw_v{idx+1}.png",
                mime="image/png",
                key=f"dl_btn_{idx}"
            )
