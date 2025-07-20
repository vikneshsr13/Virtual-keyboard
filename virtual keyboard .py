import cv2
import numpy as np
import mediapipe as mp


mp_hands = mp.solutions.hands
mp_drawing = mp.solutions.drawing_utils
hands = mp_hands.Hands(min_detection_confidence=0.8, min_tracking_confidence=0.8)


keys = [['Q', 'W', 'E', 'R', 'T', 'Y', 'U', 'I', 'O', 'P'],
        ['A', 'S', 'D', 'F', 'G', 'H', 'J', 'K', 'L'],
        ['Z', 'X', 'C', 'V', 'B', 'N', 'M'],
        ['SPACE', 'BACKSPACE']]

key_size = 80
margin = 10
text = ""


hover_key = None
hover_start_frame = 0
required_hover_frames = 20  # ~1 sec at 20 FPS
current_hover_coords = (0, 0, 0, 0)  # (x1, y1, x2, y2)

def draw_keyboard(frame):
    global current_hover_coords
    y_offset = 50
    for row in keys:
        x_offset = 50
        for key in row:
            w = key_size * 2 if key == "SPACE" else key_size
            x1, y1 = x_offset, y_offset
            x2, y2 = x_offset + w, y_offset + key_size

            if hover_key == key:
                cv2.rectangle(frame, (x1, y1), (x2, y2), (255, 255, 255), -1)  
                cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 0, 255), 3)       
                cv2.putText(frame, key, (x1 + 15, y1 + 55), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)
                current_hover_coords = (x1, y1, x2, y2)
            else:
                cv2.rectangle(frame, (x1, y1), (x2, y2), (255, 255, 255), 2)
                cv2.putText(frame, key, (x1 + 15, y1 + 55), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)
            
            x_offset += w + margin
        y_offset += key_size + margin

def get_key_pressed(x, y):
    y_offset = 50
    for row in keys:
        x_offset = 50
        for key in row:
            w = key_size * 2 if key == "SPACE" else key_size
            if x_offset < x < x_offset + w and y_offset < y < y_offset + key_size:
                return key
            x_offset += w + margin
        y_offset += key_size + margin
    return None

cv2.namedWindow("Virtual Keyboard")
cap = cv2.VideoCapture(0)

frame_count = 0

while cap.isOpened():
    ret, frame = cap.read()
    if not ret:
        break
    frame = cv2.flip(frame, 1)
    frame = cv2.resize(frame, (1000, 600))
    rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    results = hands.process(rgb_frame)

    frame_count += 1
    current_hover_coords = (0, 0, 0, 0)

    if results.multi_hand_landmarks:
        for hand_landmarks in results.multi_hand_landmarks:
            mp_drawing.draw_landmarks(frame, hand_landmarks, mp_hands.HAND_CONNECTIONS)

            index_finger_tip = hand_landmarks.landmark[8]
            x = int(index_finger_tip.x * frame.shape[1])
            y = int(index_finger_tip.y * frame.shape[0])

            key = get_key_pressed(x, y)

            if key == hover_key:
                if frame_count - hover_start_frame >= required_hover_frames:
                    if key == 'BACKSPACE':
                        text = text[:-1] if text else text
                    elif key == 'SPACE':
                        text += " "
                    elif key is not None:
                        text += key
                    hover_key = None
                    hover_start_frame = 0
            else:
                hover_key = key
                hover_start_frame = frame_count
    else:
        hover_key = None
        hover_start_frame = 0

    draw_keyboard(frame)

    
    cv2.putText(frame, text, (50, 550), cv2.FONT_HERSHEY_SIMPLEX, 2, (0, 255, 0), 3)

    cv2.imshow("Virtual Keyboard", frame)
    if cv2.waitKey(1) & 0xFF == 27:
        break

cap.release()
cv2.destroyAllWindows()
