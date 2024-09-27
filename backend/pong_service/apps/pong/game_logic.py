import time
import random


class PongGame:
    def __init__(self, player1, player2, canvas_width=800, canvas_height=600):
        self.canvas_width = canvas_width
        self.canvas_height = canvas_height
        self.grid = 15
        self.paddle_height = self.grid * 5
        self.max_paddle_y = self.canvas_height - self.grid - self.paddle_height

        self.paddle_speed = 6
        self.ball_speed = 5

        self.player1 = player1
        self.player2 = player2

        self.left_paddle = {
            "x": self.grid * 2,
            "y": self.canvas_height / 2 - self.paddle_height / 2,
            "width": self.grid,
            "height": self.paddle_height,
            "dy": 0,
        }

        self.right_paddle = {
            "x": self.canvas_width - self.grid * 3,
            "y": self.canvas_height / 2 - self.paddle_height / 2,
            "width": self.grid,
            "height": self.paddle_height,
            "dy": 0,
        }

        self.ball = {
            "x": self.canvas_width / 2,
            "y": self.canvas_height / 2,
            "width": self.grid,
            "height": self.grid,
            "resetting": False,
            "dx": self.ball_speed,
            "dy": -self.ball_speed,
        }

        self.scores = {player1.id: 0, player2.id: 0}
        self.last_update_time = time.time()

    def collides(self, obj1, obj2):
        return (
            obj1["x"] < obj2["x"] + obj2["width"] and
            obj1["x"] + obj1["width"] > obj2["x"] and
            obj1["y"] < obj2["y"] + obj2["height"] and
            obj1["y"] + obj1["height"] > obj2["y"]
        )

    def update(self, current_time):
        dt = current_time - self.last_update_time
        self.last_update_time = current_time

        # Update paddle positions
        self.left_paddle["y"] += self.left_paddle["dy"] * dt * 60
        self.right_paddle["y"] += self.right_paddle["dy"] * dt * 60

        # Constrain paddles to canvas
        self.left_paddle["y"] = max(self.grid, min(
            self.max_paddle_y, self.left_paddle["y"]))
        self.right_paddle["y"] = max(self.grid, min(
            self.max_paddle_y, self.right_paddle["y"]))

        # Update ball position
        if not self.ball["resetting"]:
            self.ball["x"] += self.ball["dx"] * dt * 60
            self.ball["y"] += self.ball["dy"] * dt * 60

        # Ball collision with top and bottom
        if self.ball["y"] < self.grid or self.ball["y"] + self.grid > self.canvas_height - self.grid:
            self.ball["dy"] *= -1

        # Ball out of bounds
        if self.ball["x"] < 0 or self.ball["x"] > self.canvas_width:
            if self.ball["x"] < 0:
                self.scores[self.player2.id] += 1
            else:
                self.scores[self.player1.id] += 1
            self.reset_ball()

        # Ball collision with paddles
        if self.collides(self.ball, self.left_paddle):
            self.ball["dx"] = abs(self.ball["dx"])
            self.ball["x"] = self.left_paddle["x"] + self.left_paddle["width"]
        elif self.collides(self.ball, self.right_paddle):
            self.ball["dx"] = -abs(self.ball["dx"])
            self.ball["x"] = self.right_paddle["x"] - self.ball["width"]

        return max(self.scores.values()) >= 11

    def reset_ball(self):
        self.ball["resetting"] = True
        self.ball["x"] = self.canvas_width / 2
        self.ball["y"] = self.canvas_height / 2
        self.ball["resetting"] = False
        self.ball["dx"] = self.ball_speed * random.choice([-1, 1])
        self.ball["dy"] = self.ball_speed * random.choice([-1, 1])

    def move_paddle(self, player_id, direction):
        paddle = self.left_paddle if player_id == self.player1.id else self.right_paddle
        if direction == "up":
            paddle["dy"] = -self.paddle_speed
        elif direction == "down":
            paddle["dy"] = self.paddle_speed
        else:
            paddle["dy"] = 0

    def get_winner(self):
        if self.scores[self.player1.id] >= 11:
            return self.player1
        elif self.scores[self.player2.id] >= 11:
            return self.player2
        return None

    def get_state(self):
        return {
            "ball_x": self.ball["x"],
            "ball_y": self.ball["y"],
            "paddle1_y": self.left_paddle["y"],
            "paddle2_y": self.right_paddle["y"],
            "score1": self.scores[self.player1.id],
            "score2": self.scores[self.player2.id],
        }
