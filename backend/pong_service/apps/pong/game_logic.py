import math
import random

# Constants
GAME_WIDTH = 1200
GAME_HEIGHT = 800
PADDLE_WIDTH = 20
PADDLE_HEIGHT = 100
BALL_SIZE = 10
INITIAL_VELOCITY = 0.025
VELOCITY_INCREASE = 0.000001
PADDLE_SPEED = 0.02


class Ball:
    def __init__(self):
        self.reset()

    def reset(self):
        self.x = GAME_WIDTH / 2
        self.y = GAME_HEIGHT / 2
        self.direction = {'x': 0, 'y': 0}
        while abs(self.direction['x']) <= 0.3 or abs(self.direction['y']) <= 0.7:
            heading = random.uniform(0, 2 * math.pi)
            self.direction = {'x': math.cos(heading), 'y': math.sin(heading)}
        self.velocity = INITIAL_VELOCITY

    def update(self, delta, paddle1_rect, paddle2_rect):
        self.x += self.direction['x'] * self.velocity * delta
        self.y += self.direction['y'] * self.velocity * delta
        self.velocity += VELOCITY_INCREASE * delta

        if self.y <= 0 or self.y >= GAME_HEIGHT:
            self.direction['y'] *= -1

        if self.is_collision(paddle1_rect) or self.is_collision(paddle2_rect):
            self.direction['x'] *= -1

    def is_collision(self, paddle_rect):
        return (
            self.x - BALL_SIZE / 2 <= paddle_rect['right'] and
            self.x + BALL_SIZE / 2 >= paddle_rect['left'] and
            self.y - BALL_SIZE / 2 <= paddle_rect['bottom'] and
            self.y + BALL_SIZE / 2 >= paddle_rect['top']
        )


class Paddle:
    def __init__(self, is_left):
        self.y = GAME_HEIGHT / 2
        self.is_left = is_left
        
    def update(self, delta, ball_y):
        self.y += PADDLE_SPEED * delta * (ball_y - self.y)
        
    def rect(self):
        if self.is_left:
            left = 0
        else:
            left = GAME_WIDTH - PADDLE_WIDTH
        return {
			'top': self.y - PADDLE_HEIGHT / 2,
			'bottom': self.y + PADDLE_HEIGHT / 2,
			'left': left,
			'right': left + PADDLE_WIDTH
		}


class PongGame:
    def __init__(self, player1, player2):
        self.ball = Ball()
        self.paddle1 = Paddle(True)
        self.paddle2 = Paddle(False)
        self.player1 = player1
        self.player2 = player2
        self.score1 = 0
        self.score2 = 0
        self.last_update_time = None
        
    def update(self, current_time):
        if self.last_update_time is None:
            self.last_update_time = current_time
            return False
        
        delta = current_time - self.last_update_time
        self.last_update_time = current_time
        
        self.ball.update(delta, self.paddle1.rect(), self.paddle2.rect())
        self.paddle2.update(delta, self.ball.y)
        
        if self.is_lost():
            self.handle_lost()
            return True
        return False
    
    def is_lost(self):
        return self.ball.x <= 0 or self.ball.x >= GAME_WIDTH
    
    def handle_lost(self):
        if self.ball.x <= 0:
            self.score2 += 1
        else:
            self.score1 += 1
        self.ball.reset()
        self.paddle1.y = GAME_HEIGHT / 2
        self.paddle2.y = GAME_HEIGHT / 2
        
    def get_state(self):
        return {
			'ball_x': self.ball.x,
			'ball_y': self.ball.y,
			'paddle1_y': self.paddle1.y,
			'paddle2_y': self.paddle2.y,
			'score1': self.score1,
			'score2': self.score2
		}
