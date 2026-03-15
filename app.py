import streamlit as st
import cv2
import tempfile

st.set_page_config(page_title="Cricket Video Analyzer", page_icon="🏏")

st.title("🏏 Cricket Video Analyzer")

st.write("Upload a cricket video to analyze movement.")

video = st.file_uploader("Upload Video", type=["mp4","mov","avi"])

if video is not None:

    st.success("Video uploaded successfully!")

    st.video(video)

    # Save video temporarily
    tfile = tempfile.NamedTemporaryFile(delete=False)
    tfile.write(video.read())

    if st.button("Process Video"):

        cap = cv2.VideoCapture(tfile.name)

        frame_count = 0
        processed_frames = 0

        progress = st.progress(0)

        while cap.isOpened():

            ret, frame = cap.read()

            if not ret:
                break

            frame_count += 1

            # Process every 5th frame to reduce load
            if frame_count % 5 != 0:
                continue

            processed_frames += 1

            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

            progress.progress(min(frame_count / 200, 1.0))

        cap.release()

        st.success(f"Processing complete! Frames analyzed: {processed_frames}")
