import cv2
import mediapipe as mp
import pyautogui
import time
import math

class HandGestureController:
    def __init__(self):
        self.cap = cv2.VideoCapture(0)
        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)
        self.cap.set(cv2.CAP_PROP_FPS, 60)

        self.screen_w, self.screen_h = pyautogui.size()

        self.mp_hands = mp.solutions.hands
        self.hands = self.mp_hands.Hands(min_detection_confidence=0.7, min_tracking_confidence=0.7)
        self.mp_draw = mp.solutions.drawing_utils

        self.dragging = False
        self.last_hand_time = time.time()
        self.hand_timeout_seconds = 7

        # Initialize previous positions for smooth movement
        self.prev_x, self.prev_y = 0, 0
        self.smoothening = 2

    def fingers_up(self, lm):
        tips = [4, 8, 12, 16, 20]
        fingers = []
        for tip_id in tips:
            if tip_id == 4:
                fingers.append(lm[tip_id].x < lm[3].x)
            else:
                fingers.append(lm[tip_id].y < lm[tip_id - 2].y)
        return fingers

    def distance(self, p1, p2, w, h):
        x1, y1 = int(p1.x * w), int(p1.y * h)
        x2, y2 = int(p2.x * w), int(p2.y * h)
        return math.hypot(x2 - x1, y2 - y1)

    def start(self):
        while True:
            success, img = self.cap.read()
            if not success:
                continue
            
            img = cv2.flip(img, 1)  
            img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
            results = self.hands.process(img_rgb)
            h, w, _ = img.shape
            hand_detected = False

            if results.multi_hand_landmarks:
                hand_detected = True
                self.last_hand_time = time.time()

                for handLms in results.multi_hand_landmarks:
                    lm = handLms.landmark
                    fingers = self.fingers_up(lm)

                    index_tip = lm[8]
                    thumb_tip = lm[4]
                    middle_tip = lm[12]
                    ring_tip = lm[16]

                    # Index position mapped to screen
                    x = int(index_tip.x * self.screen_w * 1.25) #Increase the value to move faster
                    y = int(index_tip.y * self.screen_h * 1.25) 


                    # Smooth movement
                    curr_x = self.prev_x + (x - self.prev_x) / self.smoothening
                    curr_y = self.prev_y + (y - self.prev_y) / self.smoothening
                    self.prev_x, self.prev_y = curr_x, curr_y

                    # Move mouse with only index up
                    if fingers[1] and not any(fingers[i] for i in [0,2,3,4]):
                        pyautogui.moveTo(curr_x, curr_y)

                    # Right Click: Index and middle fingers up
                    elif fingers[1] and fingers[2] and not any(fingers[i] for i in [0,3,4]):
                        pyautogui.rightClick()
                        time.sleep(0.3)


                    # Close all fingers: Left click
                    elif not any(fingers):
                        pyautogui.click()
                        time.sleep(0.3)

                    # Drag: Thumb + Index held close
                    elif fingers[0] and fingers[1]:
                        if self.distance(index_tip, thumb_tip, w, h) < 40:
                            if not self.dragging:
                                pyautogui.mouseDown()
                                self.dragging = True
                        else:
                            if self.dragging:
                                pyautogui.mouseUp()
                                self.dragging = False
                    else:
                        if self.dragging:
                            pyautogui.mouseUp()
                            self.dragging = False

                    # Scroll with all fingers up
                    if all(fingers):
                        if index_tip.y * h < h // 3:
                            pyautogui.scroll(20)
                        elif index_tip.y * h > h * 2 // 3:
                            pyautogui.scroll(-20)
                        time.sleep(0.1)

                    # Zoom: Pinch gesture with thumb and index
                    if fingers[0] and fingers[1]:
                        if self.distance(index_tip, thumb_tip, w, h)< 40:
                            pyautogui.scroll(-20)
                    elif fingers[0] and fingers[1] and fingers[2]:
                        if self.distance(index_tip, thumb_tip, w, h) < 40:
                            pyautogui.scroll(20)

                    # Middle Click: Index and ring fingers up
                    elif fingers[1] and fingers[3] and not any(fingers[i] for i in [0,2,4]):
                        pyautogui.middleClick()
                        time.sleep(0.3)

                    # Show Task View: Index and middle fingers close together
                    dist_im = self.distance(index_tip, middle_tip, w, h)
                    if fingers[1] and fingers[2] and dist_im < 40 and not any(fingers[i] for i in [0,3,4]):
                        pyautogui.hotkey('win', 'tab')
                        time.sleep(0.8)
                    
                    # Show Desktop: index, middle, and ring close together
                    dist_im = self.distance(index_tip, middle_tip, w, h)
                    dist_mr = self.distance(middle_tip, ring_tip, w, h)
                    if dist_im < 40 and dist_mr < 40:
                        pyautogui.hotkey('win', 'd')
                        time.sleep(0.8)

                    self.mp_draw.draw_landmarks(img, handLms, self.mp_hands.HAND_CONNECTIONS)

            elif time.time() - self.last_hand_time > self.hand_timeout_seconds:
                cv2.putText(img, "Hand not detected. Control paused.",
                            (20, 60), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)

            cv2.imshow("Hand Gesture Control", img)
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

        self.cap.release()
        cv2.destroyAllWindows()
