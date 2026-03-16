import streamlit as st
import cv2
import mediapipe as mp
import numpy as np
import plotly.graph_objects as go
import tempfile
import random

st.title("🏏 Cricket AI Batting Analyzer")

uploaded_file = st.file_uploader("Upload Batting Video", type=["mp4","mov","avi"])

mp_pose = mp.solutions.pose
pose = mp_pose.Pose()

# -----------------------------
# Angle Calculation
# -----------------------------

def calculate_angle(a,b,c):

    a=np.array(a)
    b=np.array(b)
    c=np.array(c)

    radians=np.arctan2(c[1]-b[1],c[0]-b[0])-np.arctan2(a[1]-b[1],a[0]-b[0])
    angle=np.abs(radians*180/np.pi)

    if angle>180:
        angle=360-angle

    return angle


# -----------------------------
# Field Placement UI
# -----------------------------

st.subheader("⚙ Field Placement Simulator")

fielder_count = st.slider("Number of fielders",1,11,5)

fig = go.Figure()

# batsman position
fig.add_trace(go.Scatter(
    x=[0],
    y=[0],
    mode="markers",
    marker=dict(size=20,color="red"),
    name="Batsman"
))

# random fielders (user concept demo)
fielder_positions=[]

for i in range(fielder_count):

    x=random.uniform(-10,10)
    y=random.uniform(0,10)

    fielder_positions.append((x,y))

    fig.add_trace(go.Scatter(
        x=[x],
        y=[y],
        mode="markers",
        marker=dict(size=15,color="blue"),
        name="Fielder"
    ))

fig.update_layout(
    title="Cricket Field Layout",
    xaxis=dict(range=[-10,10]),
    yaxis=dict(range=[0,10]),
    height=500
)

st.plotly_chart(fig)


# -----------------------------
# Video Analysis
# -----------------------------

if uploaded_file:

    st.video(uploaded_file)

    process = st.button("Process Video")

    if process:

        temp_file = tempfile.NamedTemporaryFile(delete=False)
        temp_file.write(uploaded_file.read())

        cap=cv2.VideoCapture(temp_file.name)

        frame_count=0
        swing_angles=[]
        head_moves=[]
        prev_nose=None

        max_frames=80

        while cap.isOpened() and frame_count<max_frames:

            ret,frame=cap.read()

            if not ret:
                break

            frame_count+=1

            if frame_count%8!=0:
                continue

            rgb=cv2.cvtColor(frame,cv2.COLOR_BGR2RGB)
            results=pose.process(rgb)

            if results.pose_landmarks:

                landmarks=results.pose_landmarks.landmark

                shoulder=[landmarks[11].x,landmarks[11].y]
                elbow=[landmarks[13].x,landmarks[13].y]
                wrist=[landmarks[15].x,landmarks[15].y]

                angle=calculate_angle(shoulder,elbow,wrist)

                swing_angles.append(angle)

                nose=landmarks[0]

                if prev_nose:
                    head_moves.append(abs(prev_nose-nose.x))

                prev_nose=nose.x

        cap.release()

        avg_angle=np.mean(swing_angles) if swing_angles else 0
        head_move=np.mean(head_moves) if head_moves else 0


# -----------------------------
# Technique Analysis
# -----------------------------

        if head_move<0.02:
            head_status="Stable"
        else:
            head_status="Unstable"

        if avg_angle>40:
            shot="Cover Drive"
            direction="Cover Region"
        else:
            shot="Straight Drive"
            direction="Straight"


# -----------------------------
# Run Prediction Engine
# -----------------------------

        runs=0

        if direction=="Cover Region" and fielder_count<3:
            runs=random.choice([4,4,2,1])
        elif direction=="Cover Region":
            runs=random.choice([0,1,1])
        else:
            runs=random.choice([1,2])


# -----------------------------
# Technique Score
# -----------------------------

        score=0

        if head_status=="Stable":
            score+=3

        if 40<avg_angle<70:
            score+=4

        if fielder_count<5:
            score+=3


# -----------------------------
# Output Dashboard
# -----------------------------

        st.success(f"Processing complete! Frames analyzed: {frame_count}")

        st.subheader("🏏 Technique Analysis")

        st.write("Shot Type:",shot)
        st.write("Head Stability:",head_status)
        st.write("Backlift Angle:",round(avg_angle,2))

        st.subheader("🎯 Shot Prediction")

        st.write("Shot Direction:",direction)

        st.subheader("📊 Run Prediction")

        st.write("Predicted Runs:",runs)

        st.subheader("⭐ Technique Score")

        st.write(score,"/10")
