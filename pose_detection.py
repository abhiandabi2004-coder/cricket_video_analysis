import mediapipe as mp
import cv2

mp_pose = mp.solutions.pose
pose = mp_pose.Pose()

def detect_pose_landmarks(frame):

    rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

    results = pose.process(rgb)

    if results.pose_landmarks:

        landmarks = []

        for lm in results.pose_landmarks.landmark:
            landmarks.append((lm.x, lm.y))

        return landmarks

    return None