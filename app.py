import streamlit as st

# Page configuration
st.set_page_config(
    page_title="Cricket Video Analyzer",
    page_icon="🏏",
    layout="centered"
)

# App title
st.title("🏏 Cricket Video Analyzer")

st.write(
    "Upload a cricket video to test the application. "
    "Pose detection is temporarily disabled for deployment testing."
)

# Video uploader
video = st.file_uploader(
    "Upload cricket video",
    type=["mp4", "mov", "avi"]
)

# If user uploads video
if video is not None:

    st.success("Video uploaded successfully!")

    st.subheader("Video Preview")

    # Display the video
    st.video(video)

    st.info("Video processing modules will be enabled after deployment is stable.")
