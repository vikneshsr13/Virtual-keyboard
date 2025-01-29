import cv2
import numpy as np
import mediapipe as mp

mp_hands = mp.solutions.hands
mp_drawing = mp.solutions.drawing_utils
hands = mp_hands.Hands(min_detection_confidence=0.8, min_tracking_confidence=0.8)

keys = [['Q', 'W', 'E', 'R', 'T', 'Y', 'U', 'I', 'O', 'P'],
        ['A', 'S', 'D', 'F', 'G', 'H', 'J', 'K', 'L'],
        ['Z', 'X', 'C', 'V', 'B', 'N', 'M'],
        ['CLEAR']]  # Changed delete button to clear all text

key_size = 80
margin = 10
text = ""
last_pressed_key = None
key_cooldown = 20  # Frames to wait before registering another key press
frame_counter = 0

def draw_keyboard(frame):
    y_offset = 50
    for row in keys:
        x_offset = 50
        for key in row:
            cv2.rectangle(frame, (x_offset, y_offset), (x_offset + key_size, y_offset + key_size), (255, 255, 255), 2)
            cv2.putText(frame, key, (x_offset + 15, y_offset + 55), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)
            x_offset += key_size + margin
        y_offset += key_size + margin

def get_key_pressed(x, y):
    y_offset = 50
    for row in keys:
        x_offset = 50
        for key in row:
            if x_offset < x < x_offset + key_size and y_offset < y < y_offset + key_size:
                return key
            x_offset += key_size + margin
        y_offset += key_size + margin
    return None

cv2.namedWindow("Virtual Keyboard")

cap = cv2.VideoCapture(0)

while cap.isOpened():
    ret, frame = cap.read()
    if not ret:
        break
    frame = cv2.flip(frame, 1)
    frame = cv2.resize(frame, (1000, 600))  # Enlarged background
    rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    results = hands.process(rgb_frame)
    
    draw_keyboard(frame)
    frame_counter += 1  # Increase frame counter
    
    if results.multi_hand_landmarks:
        for hand_landmarks in results.multi_hand_landmarks:
            mp_drawing.draw_landmarks(frame, hand_landmarks, mp_hands.HAND_CONNECTIONS)
            index_finger_tip = hand_landmarks.landmark[8]
            x, y = int(index_finger_tip.x * frame.shape[1]), int(index_finger_tip.y * frame.shape[0])
            key = get_key_pressed(x, y)
            
            if key and key != last_pressed_key and frame_counter > key_cooldown:
                if key == 'CLEAR':
                    text = ""  # Clear all text
                else:
                    text += key
                last_pressed_key = key
                frame_counter = 0  # Reset counter after key press
            elif key is None:
                last_pressed_key = None  # Reset last_pressed_key when no key is being pressed
    
    cv2.putText(frame, text, (50, 500), cv2.FONT_HERSHEY_SIMPLEX, 2, (0, 255, 0), 3)
    cv2.imshow("Virtual Keyboard", frame)
    
    if cv2.waitKey(1) & 0xFF == 27:
        break

cap.release()
cv2.destroyAllWindows()
