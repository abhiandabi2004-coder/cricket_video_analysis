import streamlit as st
import cv2
import mediapipe as mp
import numpy as np
import plotly.graph_objects as go
import tempfile
import random

st.title("🏏 Cricket AI Batting Analyzer")

# --------------------------------
# Upload Video
# --------------------------------

uploaded_file = st.file_uploader("Upload Batting Video", type=["mp4","mov","avi"])

# --------------------------------
# Field Placement Section
# --------------------------------

st.subheader("⚙ Field Placement Simulator")

fielder_count = st.slider("Number of Fielders",1,11,5)

fielder_positions=[]

fig = go.Figure()

# batsman
fig.add_trace(go.Scatter(
    x=[0],
    y=[0],
    mode="markers",
    marker=dict(size=20,color="red"),
    name="Batsman"
))

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

# --------------------------------
# Angle Function
# --------------------------------

def calculate_angle(a,b,c):

    a=np.array(a)
    b=np.array(b)
    c=np.array(c)

    radians=np.arctan2(c[1]-b[1],c[0]-b[0]) - np.arctan2(a[1]-b[1],a[0]-b[0])
    angle=np.abs(radians*180/np.pi)

    if angle>180:
        angle=360-angle

    return angle


# --------------------------------
# Run Prediction
# --------------------------------

def predict_runs(direction, fielders):

    if direction=="Cover":

        if len(fielders)<3:
            return random.choice([4,4,2,1])
        else:
            return random.choice([0,1,1])

    elif direction=="Straight":
        return random.choice([1,2])

    else:
        return random.choice([0,1])


# --------------------------------
# Video Processing
# --------------------------------

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

        max_frames=60

        mp_pose = mp.solutions.pose

        with mp_pose.Pose() as pose:

            while cap.isOpened() and frame_count < max_frames:

                ret,frame=cap.read()

                if not ret:
                    break

                frame_count+=1

                if frame_count % 10 != 0:
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

# --------------------------------
# Technique Analysis
# --------------------------------

        if head_move<0.02:
            head_status="Stable"
        else:
            head_status="Unstable"

        if avg_angle>45:
            shot="Cover Drive"
            shot_direction="Cover"
        elif avg_angle>25:
            shot="Square Shot"
            shot_direction="Point"
        else:
            shot="Straight Drive"
            shot_direction="Straight"

# --------------------------------
# Run Prediction
# --------------------------------

        runs = predict_runs(shot_direction,fielder_positions)

# --------------------------------
# Technique Score
# --------------------------------

        score=0

        if head_status=="Stable":
            score+=3

        if 40<avg_angle<70:
            score+=4

        if fielder_count<6:
            score+=3

# --------------------------------
# Dashboard Output
# --------------------------------

        st.success(f"Processing complete! Frames analyzed: {frame_count}")

        st.subheader("🏏 Technique Analysis")

        st.metric("Shot Type",shot)
        st.metric("Head Stability",head_status)
        st.metric("Backlift Angle",round(avg_angle,2))

        st.subheader("🎯 Shot Prediction")

        st.metric("Shot Direction",shot_direction)

        st.subheader("📊 Run Prediction")

        st.metric("Predicted Runs",runs)

        st.subheader("⭐ Technique Score")

        st.metric("Score",f"{score}/10")
