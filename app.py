import streamlit as st
import tempfile

from video_processing import extract_frames
from pose_detection import detect_pose_landmarks
from angle_calculator import calculate_angle
from technique_analyzer import analyze_batting
from visualization import show_results

st.title("🏏 AI Cricket Technique Analyzer")

video_file = st.file_uploader("Upload batting/bowling video", type=["mp4","mov","avi"])

analysis_type = st.selectbox(
    "Select Analysis Type",
    ["Batting"]
)

if video_file is not None:

    tfile = tempfile.NamedTemporaryFile(delete=False)
    tfile.write(video_file.read())

    st.video(tfile.name)

    if st.button("Analyze Technique"):

        st.write("Processing video...")

        frames = extract_frames(tfile.name)

        angles = []

        for frame in frames:

            landmarks = detect_pose_landmarks(frame)

            if landmarks:

                shoulder = landmarks[12]
                elbow = landmarks[14]
                wrist = landmarks[16]

                angle = calculate_angle(shoulder, elbow, wrist)
                angles.append(angle)

        result = analyze_batting(angles)

        show_results(angles, result)