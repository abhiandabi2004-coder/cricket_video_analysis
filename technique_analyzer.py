import numpy as np

def analyze_batting(angles):

    if len(angles) == 0:
        return "No pose detected"

    avg_angle = np.mean(angles)

    if avg_angle < 70:
        feedback = "Backlift too low"
    elif avg_angle > 100:
        feedback = "Backlift too high"
    else:
        feedback = "Backlift looks good"

    return {
        "average_angle": avg_angle,
        "feedback": feedback
    }