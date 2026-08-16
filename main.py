import cv2
import numpy as np
import math
import random
import time

from snake_game import SnakeGame
from hand_tracker import HandTracker


# ============================================================
# SETTINGS
# ============================================================

WINDOW_W = 1280
WINDOW_H = 720

CAM_W = 430
CAM_H = 300

GAME_W = 760
GAME_H = 560


# ============================================================
# COLORS
# ============================================================

BG = (8, 10, 13)

PANEL = (18, 21, 27)

WHITE = (235, 238, 240)

GRAY = (145, 150, 160)

LIGHT_GRAY = (190, 195, 200)

GREEN = (90, 230, 160)

NEON_GREEN = (120, 255, 175)


# ============================================================
# HELPERS
# ============================================================

def clamp(
    value,
    minimum,
    maximum
):

    return max(
        minimum,
        min(
            maximum,
            value
        )
    )


def text(
    img,
    value,
    position,
    size=0.5,
    color=WHITE,
    thickness=1
):

    cv2.putText(
        img,
        str(value),
        position,
        cv2.FONT_HERSHEY_SIMPLEX,
        size,
        color,
        thickness,
        cv2.LINE_AA
    )


def rounded_rect(
    img,
    p1,
    p2,
    radius,
    color
):

    x1, y1 = p1
    x2, y2 = p2

    cv2.rectangle(
        img,
        (
            x1 + radius,
            y1
        ),
        (
            x2 - radius,
            y2
        ),
        color,
        -1
    )

    cv2.rectangle(
        img,
        (
            x1,
            y1 + radius
        ),
        (
            x2,
            y2 - radius
        ),
        color,
        -1
    )

    cv2.circle(
        img,
        (
            x1 + radius,
            y1 + radius
        ),
        radius,
        color,
        -1
    )

    cv2.circle(
        img,
        (
            x2 - radius,
            y1 + radius
        ),
        radius,
        color,
        -1
    )

    cv2.circle(
        img,
        (
            x1 + radius,
            y2 - radius
        ),
        radius,
        color,
        -1
    )

    cv2.circle(
        img,
        (
            x2 - radius,
            y2 - radius
        ),
        radius,
        color,
        -1
    )


# ============================================================
# ANIMATED BORDER
# ============================================================

def animated_border(
    img,
    x1,
    y1,
    x2,
    y2
):

    pulse = (
        math.sin(
            time.time() * 3
        ) + 1
    ) / 2

    overlay = img.copy()

    cv2.rectangle(
        overlay,
        (
            x1,
            y1
        ),
        (
            x2,
            y2
        ),
        (
            90,
            230,
            160
        ),
        2
    )

    cv2.addWeighted(
        overlay,
        0.25 + pulse * 0.55,
        img,
        0.45 - pulse * 0.25,
        0,
        img
    )


# ============================================================
# SCAN LINE
# ============================================================

def scan_line(
    img,
    x1,
    y1,
    x2,
    y2,
    speed=0.4
):

    height = y2 - y1

    if height <= 0:
        return

    position = (
        time.time() *
        speed
    ) % 1

    y = int(
        y1 +
        height * position
    )

    overlay = img.copy()

    cv2.line(
        overlay,
        (
            x1,
            y
        ),
        (
            x2,
            y
        ),
        (
            80,
            230,
            170
        ),
        2
    )

    cv2.addWeighted(
        overlay,
        0.25,
        img,
        0.75,
        0,
        img
    )


# ============================================================
# PARTICLES
# ============================================================

class Particle:

    def __init__(
        self,
        x,
        y
    ):

        self.x = x
        self.y = y

        self.vx = random.uniform(
            -4,
            4
        )

        self.vy = random.uniform(
            -4,
            4
        )

        self.life = random.randint(
            20,
            45
        )

        self.max_life = self.life

    def update(self):

        self.x += self.vx

        self.y += self.vy

        self.life -= 1

    def draw(
        self,
        image
    ):

        if self.life <= 0:
            return

        alpha = (
            self.life /
            self.max_life
        )

        color = (
            int(70 * alpha),
            int(220 * alpha),
            int(150 * alpha)
        )

        cv2.circle(
            image,
            (
                int(self.x),
                int(self.y)
            ),
            2,
            color,
            -1
        )


class ParticleManager:

    def __init__(self):

        self.particles = []

    def explode(
        self,
        x,
        y
    ):

        for _ in range(35):

            self.particles.append(
                Particle(
                    x,
                    y
                )
            )

    def update(self):

        for particle in self.particles:

            particle.update()

        self.particles = [
            p
            for p in self.particles
            if p.life > 0
        ]

    def draw(
        self,
        image
    ):

        for particle in self.particles:

            particle.draw(
                image
            )


# ============================================================
# ACTION ICONS
# ============================================================

def draw_action_button(
    canvas,
    x,
    y,
    icon
):

    pulse = (
        math.sin(
            time.time() * 4
        ) + 1
    ) / 2

    radius = int(
        26 +
        pulse * 2
    )

    cv2.circle(
        canvas,
        (
            x,
            y
        ),
        radius,
        (
            28,
            31,
            38
        ),
        -1
    )

    cv2.circle(
        canvas,
        (
            x,
            y
        ),
        radius,
        (
            70,
            73,
            80
        ),
        1
    )

    # HEART
    if icon == "heart":

        pts = np.array([
            [x - 14, y - 4],
            [x - 8, y - 12],
            [x, y - 6],
            [x + 8, y - 12],
            [x + 14, y - 4],
            [x, y + 15]
        ])

        cv2.polylines(
            canvas,
            [pts],
            True,
            WHITE,
            2
        )

    # COMMENT
    elif icon == "comment":

        cv2.rectangle(
            canvas,
            (
                x - 14,
                y - 10
            ),
            (
                x + 14,
                y + 9
            ),
            WHITE,
            2
        )

        cv2.line(
            canvas,
            (
                x - 5,
                y + 9
            ),
            (
                x - 11,
                y + 15
            ),
            WHITE,
            2
        )

    # SHARE
    elif icon == "share":

        cv2.line(
            canvas,
            (
                x - 13,
                y + 7
            ),
            (
                x + 13,
                y - 9
            ),
            WHITE,
            2
        )

        cv2.line(
            canvas,
            (
                x + 13,
                y - 9
            ),
            (
                x + 3,
                y - 13
            ),
            WHITE,
            2
        )

    # SEND
    elif icon == "send":

        pts = np.array([
            [x - 16, y + 7],
            [x + 16, y - 14],
            [x + 7, y + 15],
            [x - 2, y + 2]
        ])

        cv2.polylines(
            canvas,
            [pts],
            True,
            WHITE,
            2
        )


# ============================================================
# CAMERA PANEL
# ============================================================

def camera_panel(
    canvas,
    camera
):

    x = 32
    y = 75

    rounded_rect(
        canvas,
        (
            x - 3,
            y - 3
        ),
        (
            x + CAM_W + 3,
            y + CAM_H + 3
        ),
        18,
        PANEL
    )

    camera = cv2.resize(
        camera,
        (
            CAM_W,
            CAM_H
        )
    )

    canvas[
        y:y + CAM_H,
        x:x + CAM_W
    ] = camera

    scan_line(
        canvas,
        x,
        y,
        x + CAM_W,
        y + CAM_H,
        0.45
    )

    animated_border(
        canvas,
        x,
        y,
        x + CAM_W,
        y + CAM_H
    )

    cv2.rectangle(
        canvas,
        (
            x,
            y
        ),
        (
            x + CAM_W,
            y + 38
        ),
        (
            10,
            13,
            16
        ),
        -1
    )

    text(
        canvas,
        "LIVE HAND TRACKING",
        (
            x + 14,
            y + 25
        ),
        0.42,
        GREEN,
        1
    )

    text(
        canvas,
        "CAMERA",
        (
            x + CAM_W - 80,
            y + 25
        ),
        0.34,
        GRAY,
        1
    )


# ============================================================
# HEADER
# ============================================================

def header(canvas):

    # Back arrow

    cv2.line(
        canvas,
        (
            30,
            38
        ),
        (
            55,
            38
        ),
        WHITE,
        3
    )

    cv2.line(
        canvas,
        (
            30,
            38
        ),
        (
            43,
            25
        ),
        WHITE,
        3
    )

    cv2.line(
        canvas,
        (
            30,
            38
        ),
        (
            43,
            51
        ),
        WHITE,
        3
    )

    text(
        canvas,
        "GESTURE ARCADE",
        (
            75,
            43
        ),
        0.58,
        WHITE,
        1
    )

    text(
        canvas,
        "1 DEVICE",
        (
            1100,
            40
        ),
        0.43,
        GRAY,
        1
    )


# ============================================================
# MAIN
# ============================================================

def main():

    cap = cv2.VideoCapture(
        0
    )

    cap.set(
        cv2.CAP_PROP_FRAME_WIDTH,
        CAM_W
    )

    cap.set(
        cv2.CAP_PROP_FRAME_HEIGHT,
        CAM_H
    )

    if not cap.isOpened():

        print(
            "ERROR: Camera could not be opened."
        )

        return

    tracker = HandTracker()

    game = SnakeGame(
        GAME_W,
        GAME_H
    )

    particles = ParticleManager()

    cv2.namedWindow(
        "Nokia Snake - AI Gesture Control",
        cv2.WINDOW_NORMAL
    )

    cv2.resizeWindow(
        "Nokia Snake - AI Gesture Control",
        WINDOW_W,
        WINDOW_H
    )

    previous_score = 0

    gesture = "NONE"

    gesture_timer = 0

    while True:

        success, camera = cap.read()

        if not success:
            break

        # Mirror camera
        camera = cv2.flip(
            camera,
            1
        )

        # -----------------------------------------------------
        # HAND TRACKING
        # -----------------------------------------------------

        camera, finger = (
            tracker.get_finger_position(
                camera
            )
        )

        detected_gesture = (
            tracker.gesture
        )

        if detected_gesture != "NONE":

            gesture = detected_gesture

            gesture_timer = 10

        else:

            if gesture_timer > 0:

                gesture_timer -= 1

            else:

                gesture = "NONE"

        # -----------------------------------------------------
        # SNAKE CONTROL
        # -----------------------------------------------------

        if detected_gesture != "NONE":

            game.set_direction(
                detected_gesture
            )
        #Snake automatically moves
        #one grid block at a time.
        game.move()

        # -----------------------------------------------------
        # SCORE EFFECT
        # -----------------------------------------------------

        if game.score > previous_score:

            particles.explode(
                GAME_W // 2,
                GAME_H // 2
            )

            previous_score = game.score

        particles.update()

        # -----------------------------------------------------
        # GAME FRAME
        # -----------------------------------------------------

        game_frame = np.zeros(
            (
                GAME_H,
                GAME_W,
                3
            ),
            dtype=np.uint8
        )

        game.draw(
            game_frame,
            gesture,
            finger is not None
        )

        particles.draw(
            game_frame
        )

        # -----------------------------------------------------
        # MAIN CANVAS
        # -----------------------------------------------------

        canvas = np.zeros(
            (
                WINDOW_H,
                WINDOW_W,
                3
            ),
            dtype=np.uint8
        )

        canvas[:] = BG

        # Header
        header(
            canvas
        )

        # Camera
        camera_panel(
            canvas,
            camera
        )

        # Game panel

        game_x = 485
        game_y = 75

        rounded_rect(
            canvas,
            (
                game_x - 3,
                game_y - 3
            ),
            (
                game_x + GAME_W + 3,
                game_y + GAME_H + 3
            ),
            18,
            PANEL
        )

        canvas[
            game_y:game_y + GAME_H,
            game_x:game_x + GAME_W
        ] = game_frame

        animated_border(
            canvas,
            game_x,
            game_y,
            game_x + GAME_W,
            game_y + GAME_H
        )

        # -----------------------------------------------------
        # RIGHT BUTTONS
        # -----------------------------------------------------

        rail_x = 1235

        draw_action_button(
            canvas,
            rail_x,
            210,
            "heart"
        )

        draw_action_button(
            canvas,
            rail_x,
            305,
            "comment"
        )

        draw_action_button(
            canvas,
            rail_x,
            400,
            "share"
        )

        draw_action_button(
            canvas,
            rail_x,
            495,
            "send"
        )

        text(
            canvas,
            game.score,
            (
                rail_x - 5,
                250
            ),
            0.35,
            GRAY,
            1
        )

        # -----------------------------------------------------
        # TRACKING INDICATOR
        # -----------------------------------------------------

        pulse = (
            math.sin(
                time.time() * 6
            ) + 1
        ) / 2

        cv2.circle(
            canvas,
            (
                1170,
                330
            ),
            int(
                5 +
                pulse * 4
            ),
            GREEN,
            -1
        )

        text(
            canvas,
            "TRACKING",
            (
                1085,
                336
            ),
            0.35,
            GREEN,
            1
        )

        # -----------------------------------------------------
        # BOTTOM PROJECT INFO
        # -----------------------------------------------------

        text(
            canvas,
            "NOKIA SNAKE",
            (
                32,
                620
            ),
            0.72,
            WHITE,
            2
        )

        # Verification badge

        cv2.circle(
            canvas,
            (
                195,
                613
            ),
            10,
            GREEN,
            -1
        )

        cv2.line(
            canvas,
            (
                190,
                613
            ),
            (
                194,
                617
            ),
            BG,
            2
        )

        cv2.line(
            canvas,
            (
                194,
                617
            ),
            (
                201,
                609
            ),
            BG,
            2
        )

        text(
            canvas,
            "Computer Vision  |  Python  |  MediaPipe",
            (
                32,
                650
            ),
            0.42,
            GRAY,
            1
        )

        text(
            canvas,
            "Control the snake using your index finger.",
            (
                32,
                677
            ),
            0.39,
            LIGHT_GRAY,
            1
        )

        text(
            canvas,
            "R = RESTART",
            (
                720,
                650
            ),
            0.38,
            GREEN,
            1
        )

        text(
            canvas,
            "Q = EXIT",
            (
                860,
                650
            ),
            0.38,
            GRAY,
            1
        )

        # -----------------------------------------------------
        # PROGRESS BAR
        # -----------------------------------------------------

        cv2.line(
            canvas,
            (
                32,
                700
            ),
            (
                WINDOW_W - 32,
                700
            ),
            (
                42,
                45,
                52
            ),
            5
        )

        progress = min(
            game.score / 10,
            1
        )

        progress_x = int(
            32 +
            (
                WINDOW_W - 64
            ) *
            progress
        )

        cv2.line(
            canvas,
            (
                32,
                700
            ),
            (
                progress_x,
                700
            ),
            GREEN,
            5
        )

        # -----------------------------------------------------
        # GAME OVER OVERLAY
        # -----------------------------------------------------

        if game.game_over:

            overlay = canvas.copy()

            cv2.rectangle(
                overlay,
                (
                    0,
                    0
                ),
                (
                    WINDOW_W,
                    WINDOW_H
                ),
                (
                    0,
                    0,
                    0
                ),
                -1
            )

            cv2.addWeighted(
                overlay,
                0.60,
                canvas,
                0.40,
                0,
                canvas
            )

            cx = WINDOW_W // 2
            cy = WINDOW_H // 2

            rounded_rect(
                canvas,
                (
                    cx - 210,
                    cy - 110
                ),
                (
                    cx + 210,
                    cy + 110
                ),
                20,
                (
                    20,
                    23,
                    30
                )
            )

            animated_border(
                canvas,
                cx - 210,
                cy - 110,
                cx + 210,
                cy + 110
            )

            text(
                canvas,
                "GAME OVER",
                (
                    cx - 115,
                    cy - 35
                ),
                1.1,
                (
                    100,
                    115,
                    255
                ),
                3
            )

            text(
                canvas,
                "FINAL SCORE: " +
                str(game.score),
                (
                    cx - 105,
                    cy + 15
                ),
                0.55,
                WHITE,
                1
            )

            text(
                canvas,
                "PRESS R TO RESTART",
                (
                    cx - 105,
                    cy + 60
                ),
                0.43,
                GRAY,
                1
            )

        # -----------------------------------------------------
        # SHOW
        # -----------------------------------------------------

        cv2.imshow(
            "Nokia Snake - AI Gesture Control",
            canvas
        )

        key = (
            cv2.waitKey(1)
            & 0xFF
        )

        if key in (
            27,
            ord("q"),
            ord("Q")
        ):

            break

        if key in (
            ord("r"),
            ord("R")
        ):

            game.reset()

            previous_score = 0

            particles.particles.clear()

    # Cleanup

    tracker.close()

    cap.release()

    cv2.destroyAllWindows()


if __name__ == "__main__":

    main()
