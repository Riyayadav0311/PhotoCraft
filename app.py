import streamlit as st
from PIL import Image, ImageEnhance
from rembg import remove
import io

st.title("🪄 PhotoCraft")

# --- Upload image ---
uploaded_file = st.file_uploader("Upload an image", type=["jpg", "jpeg", "png"])

if uploaded_file:
    img = Image.open(uploaded_file)
    st.image(img, caption="Original Image", use_container_width=True)

    # --- Select operation ---
    option = st.radio(
        "Choose an operation",
        ["None", "Remove Background", "Adjust Brightness"]
    )

    output_img = img  # default

    # --- Remove background ---
    if option == "Remove Background":
        with st.spinner("Removing background..."):
            output_img = remove(img)
        st.image(output_img, caption="Background Removed", use_container_width=True)

    # --- Adjust brightness ---
    elif option == "Adjust Brightness":
        brightness = st.slider("Brightness", 0.1, 3.0, 1.0)
        enhancer = ImageEnhance.Brightness(img)
        output_img = enhancer.enhance(brightness)
        st.image(output_img, caption="Brightness Adjusted", use_container_width=True)

    # --- Download section ---
    if option != "None":
        st.subheader("💾 Download Edited Image")

        # Radio button for selecting format
        format_choice = st.radio(
            "Select download format:",
            ["PNG", "JPEG"],
            horizontal=True
        )

        # Save image to buffer in chosen format
        buf = io.BytesIO()
        output_format = format_choice.upper()
        output_img.convert("RGB").save(buf, format=output_format)
        buf.seek(0)

        st.download_button(
            label=f"⬇️ Download as {output_format}",
            data=buf,
            file_name=f"edited_image.{format_choice.lower()}",
            mime=f"image/{format_choice.lower()}"
        )
