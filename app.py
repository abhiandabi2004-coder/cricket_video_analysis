import streamlit as st
import cv2
import mediapipe as mp
import numpy as np
import tempfile

st.title("🏏 Cricket Shot Technique Analyzer")

uploaded_file = st.file_uploader("Upload a cricket batting video", type=["mp4","mov","avi"])

mp_pose = mp.solutions.pose
pose = mp_pose.Pose()
mp_draw = mp.solutions.drawing_utils


# angle calculation
def calculate_angle(a,b,c):

    a = np.array(a)
    b = np.array(b)
    c = np.array(c)

    radians = np.arctan2(c[1]-b[1], c[0]-b[0]) - np.arctan2(a[1]-b[1], a[0]-b[0])
    angle = np.abs(radians*180/np.pi)

    if angle > 180:
        angle = 360-angle

    return angle


if uploaded_file:

    st.video(uploaded_file)

    if st.button("Process Video"):

        temp_file = tempfile.NamedTemporaryFile(delete=False)
        temp_file.write(uploaded_file.read())

        cap = cv2.VideoCapture(temp_file.name)

        frame_count = 0
        swing_angles = []
        head_movements = []

        prev_nose = None

        progress = st.progress(0)

        while cap.isOpened():

            ret, frame = cap.read()
            if not ret:
                break

            frame_count += 1

            # process every 5th frame for speed
            if frame_count % 5 != 0:
                continue

            rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            results = pose.process(rgb)

            if results.pose_landmarks:

                landmarks = results.pose_landmarks.landmark

                shoulder = [landmarks[11].x, landmarks[11].y]
                elbow = [landmarks[13].x, landmarks[13].y]
                wrist = [landmarks[15].x, landmarks[15].y]

                angle = calculate_angle(shoulder, elbow, wrist)
                swing_angles.append(angle)

                knee = landmarks[25]
                ankle = landmarks[27]

                if abs(knee.x - ankle.x) < 0.05:
                    foot_position = "Good"
                else:
                    foot_position = "Misaligned"

                nose = landmarks[0]

                if prev_nose is not None:
                    movement = abs(prev_nose - nose.x)
                    head_movements.append(movement)

                prev_nose = nose.x

                mp_draw.draw_landmarks(
                    frame,
                    results.pose_landmarks,
                    mp_pose.POSE_CONNECTIONS
                )

            progress.progress(min(frame_count/100,1.0))

        cap.release()

        avg_swing = np.mean(swing_angles) if swing_angles else 0
        avg_head_move = np.mean(head_movements) if head_movements else 0

        if avg_head_move < 0.02:
            head_status = "Stable"
        else:
            head_status = "Unstable"

        if avg_swing > 45 and foot_position == "Good":
            shot = "Cover Drive"
        elif avg_swing > 30:
            shot = "Pull Shot"
        else:
            shot = "Unknown"

        score = 0

        if head_status == "Stable":
            score += 3

        if foot_position == "Good":
            score += 3

        if 40 < avg_swing < 70:
            score += 4

        st.success(f"Processing complete! Frames analyzed: {frame_count}")

        st.subheader("🏏 Technique Analysis")

        st.write("Shot Type:", shot)
        st.write("Head Stability:", head_status)
        st.write("Front Foot Alignment:", foot_position)
        st.write("Backlift Angle:", round(avg_swing,2))
        st.write("Technique Score:", score,"/ 10")
