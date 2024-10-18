from dataclasses import dataclass
import time
import random
import math
from typing import Dict, Optional


@dataclass
class Paddle:
    x: float
    y: float
    width: float
    height: float
    dy: float = 0


@dataclass
class Ball:
    x: float
    y: float
    width: float
    height: float
    dx: float
    dy: float
    resetting: bool = False


class PongGame:
    def __init__(self, player1, player2, canvas_width: int = 1000, canvas_height: int = 600):
        self.canvas_width = canvas_width
        self.canvas_height = canvas_height
        self.grid = 15
        self.paddle_height = self.grid * 5
        self.max_paddle_y = self.canvas_height - self.grid - self.paddle_height

        self.paddle_speed = 6
        self.ball_speed = 5

        self.player1 = player1
        self.player2 = player2

        self.left_paddle = self._create_paddle(self.grid * 2)
        self.right_paddle = self._create_paddle(
            self.canvas_width - self.grid * 3)
        self.ball = self._create_ball()

        self.scores = {player1.id: 0, player2.id: 0}
        self.last_update_time = time.time()

    def _create_paddle(self, x: float) -> Paddle:
        return Paddle(
            x=x,
            y=self.canvas_height / 2 - self.paddle_height / 2,
            width=self.grid,
            height=self.paddle_height
        )

    def _create_ball(self) -> Ball:
        return Ball(
            x=self.canvas_width / 2,
            y=self.canvas_height / 2,
            width=self.grid,
            height=self.grid,
            dx=0,
            dy=0
        )

    def start_ball_movement(self) -> None:
        angle = random.uniform(-math.pi/4, math.pi/4)
        self.ball.dx = self.ball_speed * \
            math.cos(angle) * random.choice([-1, 1])
        self.ball.dy = self.ball_speed * math.sin(angle)

    def collides(self, obj1: Dict[str, float], obj2: Dict[str, float]) -> bool:
        return (
            obj1["x"] < obj2["x"] + obj2["width"] and
            obj1["x"] + obj1["width"] > obj2["x"] and
            obj1["y"] < obj2["y"] + obj2["height"] and
            obj1["y"] + obj1["height"] > obj2["y"]
        )

    def update(self, current_time: float) -> bool:
        dt = current_time - self.last_update_time
        self.last_update_time = current_time

        self._update_paddles(dt)
        return self._update_ball(dt)

    def _update_paddles(self, dt: float) -> None:
        for paddle in (self.left_paddle, self.right_paddle):
            paddle.y += paddle.dy * dt * 60
            paddle.y = max(self.grid, min(self.max_paddle_y, paddle.y))

    def _update_ball(self, dt: float) -> bool:
        if self.ball.dx == 0 and self.ball.dy == 0:
            return False

        if not self.ball.resetting:
            self.ball.x += self.ball.dx * dt * 60
            self.ball.y += self.ball.dy * dt * 60

        if self.ball.y < self.grid or self.ball.y + self.grid > self.canvas_height - self.grid:
            self.ball.dy *= -1

        if self.ball.x < 0 or self.ball.x > self.canvas_width:
            if self.ball.x < 0:
                self.scores[self.player2.id] += 1
            else:
                self.scores[self.player1.id] += 1
            self.reset_ball()

        self._handle_paddle_collisions()

        return max(self.scores.values()) >= 11

    def _handle_paddle_collisions(self) -> None:
        ball_dict = self.ball.__dict__
        left_paddle_dict = self.left_paddle.__dict__
        right_paddle_dict = self.right_paddle.__dict__

        if self.collides(ball_dict, left_paddle_dict):
            self.ball.dx = abs(self.ball.dx)
            self.ball.x = self.left_paddle.x + self.left_paddle.width
        elif self.collides(ball_dict, right_paddle_dict):
            self.ball.dx = -abs(self.ball.dx)
            self.ball.x = self.right_paddle.x - self.ball.width

    def reset_ball(self) -> None:
        self.ball.resetting = True
        self.ball.x = self.canvas_width / 2
        self.ball.y = self.canvas_height / 2
        self.ball.resetting = False
        self.ball.dx = self.ball_speed * random.choice([-1, 1])
        self.ball.dy = self.ball_speed * random.choice([-1, 1])

    def move_paddle(self, player_id: int, direction: str) -> None:
        paddle = self.left_paddle if player_id == self.player1.id else self.right_paddle
        if direction == "up":
            paddle.dy = -self.paddle_speed
        elif direction == "down":
            paddle.dy = self.paddle_speed
        else:
            paddle.dy = 0

    def get_winner(self, disconnected_player: Optional[int] = None) -> Optional[int]:
        if disconnected_player:
            return self.player1 if self.player1.id != disconnected_player else self.player2
        if self.scores[self.player1.id] >= 11:
            return self.player1
        elif self.scores[self.player2.id] >= 11:
            return self.player2
        return None

    def get_state(self) -> Dict[str, float]:
        return {
            "ball_x": self.ball.x,
            "ball_y": self.ball.y,
            "paddle1_y": self.left_paddle.y,
            "paddle2_y": self.right_paddle.y,
            "score1": self.scores[self.player1.id],
            "score2": self.scores[self.player2.id],
        }
