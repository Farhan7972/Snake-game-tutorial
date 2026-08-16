import cv2
import mediapipe as mp

mp_hands = mp.solutions.hands
mp_draw = mp.solutions.drawing_utils

class HandTracker:

    def __init__(
        self,
        detection_con=0.7,
        track_con=0.7
    ):

        self.mp_hands = mp_hands

        self.hands = self.mp_hands.Hands(
            max_num_hands=1,
            min_detection_confidence=detection_con,
            min_tracking_confidence=track_con
        )

        self.mp_draw = mp_draw

        self.prev_position = None

        self.gesture = "NONE"

        self.cooldown = 0

    # =========================================================
    # TRACK
    # =========================================================

    def get_finger_position(
        self,
        frame
    ):

        rgb = cv2.cvtColor(
            frame,
            cv2.COLOR_BGR2RGB
        )

        results = self.hands.process(
            rgb
        )

        if self.cooldown > 0:

            self.cooldown -= 1

        if results.multi_hand_landmarks:

            hand = results.multi_hand_landmarks[0]

            # Draw hand skeleton
            self.mp_draw.draw_landmarks(
                frame,
                hand,
                self.mp_hands.HAND_CONNECTIONS
            )

            h, w, _ = frame.shape

            index_tip = hand.landmark[
                self.mp_hands.HandLandmark.INDEX_FINGER_TIP
            ]

            x = int(
                index_tip.x * w
            )

            y = int(
                index_tip.y * h
            )

            # Tracking marker ONLY on camera
            cv2.circle(
                frame,
                (
                    x,
                    y
                ),
                6,
                (
                    80,
                    255,
                    150
                ),
                -1
            )

            current_position = (
                x,
                y
            )

            # -------------------------------------------------
            # FIRST FRAME
            # -------------------------------------------------

            if self.prev_position is None:

                self.prev_position = current_position

                self.gesture = "NONE"

                return frame, current_position

            old_x, old_y = self.prev_position

            dx = x - old_x
            dy = y - old_y

            self.prev_position = current_position

            # -------------------------------------------------
            # WAIT FOR COOLDOWN
            # -------------------------------------------------

            if self.cooldown > 0:

                self.gesture = "NONE"

                return frame, current_position

            # -------------------------------------------------
            # MOVEMENT
            # -------------------------------------------------

            threshold = 18

            if abs(dx) < threshold and abs(dy) < threshold:

                self.gesture = "NONE"

                return frame, current_position

            # -------------------------------------------------
            # HORIZONTAL
            # -------------------------------------------------

            if abs(dx) > abs(dy):

                if dx > 0:

                    self.gesture = "RIGHT"

                else:

                    self.gesture = "LEFT"

            # -------------------------------------------------
            # VERTICAL
            # -------------------------------------------------

            else:

                if dy > 0:

                    self.gesture = "DOWN"

                else:

                    self.gesture = "UP"

            # Prevent the same hand movement from
            # generating many directions.
            self.cooldown = 8

            return frame, current_position

        # -----------------------------------------------------
        # NO HAND
        # -----------------------------------------------------

        self.gesture = "NONE"

        self.prev_position = None

        return frame, None

    # =========================================================
    # CLOSE
    # =========================================================

    def close(self):

        self.hands.close()