def normalize_coordinates(landmarks):

    normalized = []

    for x, y in landmarks:
        normalized.append((round(x,3), round(y,3)))

    return normalized