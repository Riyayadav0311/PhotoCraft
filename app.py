import streamlit as st
from PIL import Image, ImageEnhance
from rembg import remove
import io

# --- Custom CSS to limit image preview height safely ---
st.markdown("""
    <style>
    img {
        max-height: 450px !important;
        object-fit: contain !important;
    }
    </style>
""", unsafe_allow_html=True)

st.title("🎨 PhotoCraft – Simple Image Editor")


uploaded_file = st.file_uploader("Upload an image", type=["jpg", "jpeg", "png"])

# --- GIF Creation Section ---
st.sidebar.header("🖼️ Extra Tools")
create_gif_mode = st.sidebar.checkbox("Create GIF from multiple images")

if create_gif_mode:
    st.subheader("🎞️ Create an Animated GIF")
    gif_files = st.file_uploader(
        "Upload multiple images (in order)",
        type=["jpg", "jpeg", "png"],
        accept_multiple_files=True
    )

    if gif_files:
        images = [Image.open(f).convert("RGBA") for f in gif_files]

        # Optional: resize all images to same height for alignment
        desired_height = st.slider("Frame height (px)", 100, 1000, 400)
        resized_images = []
        for img in images:
            w, h = img.size
            new_width = int((desired_height / h) * w)
            resized = img.resize((new_width, desired_height), Image.LANCZOS)
            resized_images.append(resized)

        duration = st.slider("Frame duration (ms)", 100, 2000, 500)
        loop = st.number_input("Loop count (0 = infinite)", 0, 10, 0)

        buf = io.BytesIO()
        resized_images[0].save(
            buf,
            format="GIF",
            save_all=True,
            append_images=resized_images[1:],
            duration=duration,
            loop=loop
        )
        buf.seek(0)

        # ✅ Display preview – clean, aligned, auto-scaled
        st.image(buf, caption="Preview of your GIF", use_container_width=True)
        st.download_button(
            "⬇️ Download GIF",
            data=buf,
            file_name="animated.gif",
            mime="image/gif"
        )

    st.stop()  # Stop the normal editor when in GIF mode

# --- Main editor (single image) ---
if uploaded_file:
    img = Image.open(uploaded_file).convert("RGBA")
    st.image(img, caption="Original Image", use_container_width=True)

    st.subheader("🛠️ Choose an Operation")
    option = st.radio(
        "Select one:",
        ["None", "Remove Background", "Replace Background", "Adjust Brightness"],
        horizontal=True
    )

    output_img = img

    # --- Remove background ---
    if option == "Remove Background":
        with st.spinner("Removing background..."):
            output_img = remove(img)
        st.image(output_img, caption="Background Removed", use_container_width=True)

    # --- Replace background ---
    elif option == "Replace Background":
        with st.spinner("Removing background..."):
            fg = remove(img)

        bg_option = st.radio(
            "Choose background type:",
            ["Solid Color", "Upload Image"],
            horizontal=True
        )

        if bg_option == "Solid Color":
            color = st.color_picker("Pick a background color", "#ffffff")
            bg = Image.new("RGBA", fg.size, color)
        else:
            bg_file = st.file_uploader("Upload background image", type=["jpg", "jpeg", "png"], key="bg")
            if bg_file:
                bg = Image.open(bg_file).convert("RGBA")
                bg = bg.resize(fg.size)
            else:
                bg = Image.new("RGBA", fg.size, "#ffffff")

        output_img = Image.alpha_composite(bg, fg)
        st.image(output_img, caption="Background Replaced", use_container_width=True)

    # --- Adjust brightness ---
    elif option == "Adjust Brightness":
        brightness = st.slider("Brightness", 0.1, 3.0, 1.0)
        enhancer = ImageEnhance.Brightness(img)
        output_img = enhancer.enhance(brightness)
        st.image(output_img, caption="Brightness Adjusted", use_container_width=True)

    # --- Download the result ---
    if option != "None":
        st.subheader("💾 Download Edited Image")
        format_choice = st.radio(
            "Select download format:",
            ["PNG", "JPEG", "JPG"],
            horizontal=True
        )

        buf = io.BytesIO()
        output_img.convert("RGB").save(buf, format=format_choice.upper())
        buf.seek(0)

        st.download_button(
            label=f"⬇️ Download as {format_choice.upper()}",
            data=buf,
            file_name=f"edited_image.{format_choice.lower()}",
            mime=f"image/{format_choice.lower()}"
        )
