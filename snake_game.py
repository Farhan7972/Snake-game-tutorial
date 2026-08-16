import cv2
import random
import time


class SnakeGame:

    def __init__(self, width=760, height=560):

        self.width = width
        self.height = height

        # Grid settings
        self.cell = 20

        self.cols = self.width // self.cell
        self.rows = self.height // self.cell

        self.reset()

    # =========================================================
    # RESET
    # =========================================================

    def reset(self):

        center_x = self.cols // 2
        center_y = self.rows // 2

        self.snake = [
            (center_x, center_y),
            (center_x - 1, center_y),
            (center_x - 2, center_y),
            (center_x - 3, center_y),
        ]

        self.direction = (1, 0)

        self.next_direction = (1, 0)

        self.food = self.random_food()

        self.score = 0

        self.level = 1

        self.game_over = False

        self.move_delay = 0.13

        self.last_move = time.time()

    # =========================================================
    # FOOD
    # =========================================================

    def random_food(self):

        while True:

            food = (
                random.randint(1, self.cols - 2),
                random.randint(2, self.rows - 2)
            )

            if food not in self.snake:
                return food

    # =========================================================
    # CHANGE DIRECTION
    # =========================================================

    def set_direction(self, gesture):

        if self.game_over:
            return

        directions = {

            "UP": (0, -1),

            "DOWN": (0, 1),

            "LEFT": (-1, 0),

            "RIGHT": (1, 0)
        }

        if gesture not in directions:
            return

        new_direction = directions[gesture]

        # Prevent 180-degree turns
        if (
            new_direction[0] == -self.direction[0]
            and
            new_direction[1] == -self.direction[1]
        ):
            return

        self.next_direction = new_direction

    # =========================================================
    # MOVE ONE BLOCK
    # =========================================================

    def move(self):

        if self.game_over:
            return

        current_time = time.time()

        if current_time - self.last_move < self.move_delay:
            return

        self.last_move = current_time

        self.direction = self.next_direction

        head_x, head_y = self.snake[0]

        dx, dy = self.direction

        new_head = (
            head_x + dx,
            head_y + dy
        )

        # -----------------------------------------------------
        # WALL COLLISION
        # -----------------------------------------------------

        if (
            new_head[0] < 0
            or new_head[0] >= self.cols
            or new_head[1] < 0
            or new_head[1] >= self.rows
        ):

            self.game_over = True
            return

        # -----------------------------------------------------
        # SELF COLLISION
        # -----------------------------------------------------

        if new_head in self.snake:

            self.game_over = True
            return

        # Add new head
        self.snake.insert(
            0,
            new_head
        )

        # -----------------------------------------------------
        # FOOD
        # -----------------------------------------------------

        if new_head == self.food:

            self.score += 1

            self.level = (
                self.score // 5
            ) + 1

            # Increase speed
            self.move_delay = max(
                0.055,
                0.13 - (
                    self.level - 1
                ) * 0.01
            )

            self.food = self.random_food()

        else:

            # Remove tail
            self.snake.pop()

    # =========================================================
    # DRAW BLOCK
    # =========================================================

    def draw_block(
        self,
        frame,
        x,
        y,
        color,
        border=(30, 40, 55)
    ):

        px = x * self.cell
        py = y * self.cell

        cv2.rectangle(
            frame,
            (
                px + 1,
                py + 1
            ),
            (
                px + self.cell - 2,
                py + self.cell - 2
            ),
            border,
            -1
        )

        cv2.rectangle(
            frame,
            (
                px + 3,
                py + 3
            ),
            (
                px + self.cell - 4,
                py + self.cell - 4
            ),
            color,
            -1
        )

    # =========================================================
    # DRAW
    # =========================================================

    def draw(
        self,
        frame,
        gesture="NONE",
        tracking=False
    ):

        # =====================================================
        # BACKGROUND
        # =====================================================

        frame[:] = (
            8,
            14,
            30
        )

        # =====================================================
        # GRID
        # =====================================================

        for x in range(
            self.cols
        ):

            px = x * self.cell

            cv2.line(
                frame,
                (
                    px,
                    0
                ),
                (
                    px,
                    self.height
                ),
                (
                    25,
                    36,
                    57
                ),
                1
            )

        for y in range(
            self.rows
        ):

            py = y * self.cell

            cv2.line(
                frame,
                (
                    0,
                    py
                ),
                (
                    self.width,
                    py
                ),
                (
                    25,
                    36,
                    57
                ),
                1
            )

        # =====================================================
        # SNAKE
        # =====================================================

        for i, segment in enumerate(
            self.snake
        ):

            x, y = segment

            # Head
            if i == 0:

                color = (
                    80,
                    230,
                    70
                )

                border = (
                    130,
                    255,
                    90
                )

            else:

                color = (
                    75,
                    190,
                    55
                )

                border = (
                    45,
                    110,
                    40
                )

            self.draw_block(
                frame,
                x,
                y,
                color,
                border
            )

        # =====================================================
        # FOOD
        # =====================================================

        fx, fy = self.food

        self.draw_block(
            frame,
            fx,
            fy,
            (
                60,
                70,
                245
            ),
            (
                100,
                100,
                255
            )
        )

        # =====================================================
        # TOP HUD
        # =====================================================

        cv2.rectangle(
            frame,
            (
                8,
                8
            ),
            (
                self.width - 8,
                58
            ),
            (
                35,
                48,
                75
            ),
            -1
        )

        cv2.rectangle(
            frame,
            (
                8,
                8
            ),
            (
                self.width - 8,
                58
            ),
            (
                55,
                75,
                110
            ),
            2
        )

        # Score

        cv2.putText(
            frame,
            f"SCORE:{self.score:03d}",
            (
                25,
                42
            ),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.62,
            (
                130,
                170,
                245
            ),
            2,
            cv2.LINE_AA
        )

        # Level

        cv2.putText(
            frame,
            f"LEVEL:{self.level:02d}",
            (
                225,
                42
            ),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.62,
            (
                130,
                170,
                245
            ),
            2,
            cv2.LINE_AA
        )

        # =====================================================
        # HEARTS
        # =====================================================

        hearts_x = self.width - 90

        for i in range(3):

            color = (
                50,
                60,
                80
            )

            if not self.game_over:

                color = (
                    50,
                    70,
                    240
                )

            cv2.circle(
                frame,
                (
                    hearts_x + i * 24,
                    30
                ),
                8,
                color,
                -1
            )

        # =====================================================
        # CURRENT GESTURE
        # =====================================================

        if gesture != "NONE":

            cv2.putText(
                frame,
                gesture,
                (
                    self.width - 110,
                    self.height - 15
                ),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.4,
                (
                    100,
                    230,
                    160
                ),
                1,
                cv2.LINE_AA
            )

        # =====================================================
        # GAME OVER
        # =====================================================

        if self.game_over:

            overlay = frame.copy()

            cv2.rectangle(
                overlay,
                (
                    0,
                    0
                ),
                (
                    self.width,
                    self.height
                ),
                (
                    5,
                    8,
                    15
                ),
                -1
            )

            cv2.addWeighted(
                overlay,
                0.70,
                frame,
                0.30,
                0,
                frame
            )

            box_x1 = self.width // 2 - 180
            box_y1 = self.height // 2 - 90

            box_x2 = self.width // 2 + 180
            box_y2 = self.height // 2 + 90

            cv2.rectangle(
                frame,
                (
                    box_x1,
                    box_y1
                ),
                (
                    box_x2,
                    box_y2
                ),
                (
                    30,
                    40,
                    65
                ),
                -1
            )

            cv2.rectangle(
                frame,
                (
                    box_x1,
                    box_y1
                ),
                (
                    box_x2,
                    box_y2
                ),
                (
                    100,
                    130,
                    220
                ),
                2
            )

            cv2.putText(
                frame,
                "GAME OVER",
                (
                    box_x1 + 55,
                    box_y1 + 55
                ),
                cv2.FONT_HERSHEY_SIMPLEX,
                1.0,
                (
                    100,
                    120,
                    255
                ),
                3,
                cv2.LINE_AA
            )

            cv2.putText(
                frame,
                f"FINAL SCORE: {self.score}",
                (
                    box_x1 + 65,
                    box_y1 + 100
                ),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.55,
                (
                    220,
                    225,
                    235
                ),
                1,
                cv2.LINE_AA
            )

            cv2.putText(
                frame,
                "PRESS R TO RESTART",
                (
                    box_x1 + 65,
                    box_y1 + 130
                ),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.4,
                (
                    140,
                    160,
                    190
                ),
                1,
                cv2.LINE_AA
            )

        return frame