import cv2
import mediapipe as mp
import pyautogui
import math
import time

# Webcam and hand detector setup
cap = cv2.VideoCapture(0)
hands = mp.solutions.hands.Hands(max_num_hands=1)
draw = mp.solutions.drawing_utils

screen_w, screen_h = pyautogui.size()

last_click_time = 0
click_cooldown = 0.6  # seconds
tap_count = 0
tap_timer_start = None
action_text = ""
prev_distance = None
zoom_threshold = 20  # pixel change to trigger zoom

while True:
    _, frame = cap.read()
    frame = cv2.flip(frame, 1)
    h, w, _ = frame.shape
    rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

    output = hands.process(rgb)
    hand_landmarks = output.multi_hand_landmarks

    if hand_landmarks:
        for hand in hand_landmarks:
            draw.draw_landmarks(frame, hand)
            lm = hand.landmark

            # Get coordinates of index tip and thumb tip
            index_finger = lm[8]
            thumb_finger = lm[4]

            ix, iy = int(index_finger.x * w), int(index_finger.y * h)
            tx, ty = int(thumb_finger.x * w), int(thumb_finger.y * h)

            screen_x = int(index_finger.x * screen_w)
            screen_y = int(index_finger.y * screen_h)

            # Move the cursor
            pyautogui.moveTo(screen_x, screen_y)
            cv2.circle(frame, (ix, iy), 10, (0, 255, 255), -1)
            cv2.circle(frame, (tx, ty), 10, (0, 255, 255), -1)

            # Calculate distance
            distance = math.hypot(ix - tx, iy - ty)

            # 🖱 Tap Detection (Left Click)
            if distance < 30:
                current_time = time.time()

                if tap_timer_start is None:
                    tap_timer_start = current_time
                    tap_count = 1
                elif current_time - tap_timer_start < 0.5:
                    tap_count += 1
                else:
                    tap_timer_start = current_time
                    tap_count = 1

                # Single tap = Left Click
                if tap_count == 1 and current_time - last_click_time > click_cooldown:
                    pyautogui.click()
                    action_text = "🖱 Left Click"
                    last_click_time = current_time

                # Double tap = Right Click
                if tap_count == 2:
                    pyautogui.rightClick()
                    action_text = "🖱 Right Click"
                    last_click_time = current_time
                    tap_count = 0
                    tap_timer_start = None

            #  Zoom In / Out detection
            if prev_distance is not None:
                diff = distance - prev_distance

                if abs(diff) > zoom_threshold:
                    if diff > 0:
                        pyautogui.hotkey('ctrl', '+')
                        action_text = " Zooming In"
                    else:
                        pyautogui.hotkey('ctrl', '-')
                        action_text = " Zooming Out"

            prev_distance = distance

    # Show action text
    if action_text:
        cv2.putText(frame, action_text, (30, 50), cv2.FONT_HERSHEY_SIMPLEX,
                    1.2, (0, 255, 0), 3)
        action_text = ""

    cv2.imshow(" Virtual Mouse + Zoom", frame)
    cv2.waitKey(1)
