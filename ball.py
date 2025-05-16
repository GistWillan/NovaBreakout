import pygame
import random
from pygame.math import Vector2

pygame.init()

# 游戏常量
WIDTH, HEIGHT = 800, 600
FPS = 60
PADDLE_WIDTH = 100
PADDLE_HEIGHT = 20
BALL_RADIUS = 10
BRICK_WIDTH = 75
BRICK_HEIGHT = 30
PADDLE_SPEED = 8
BALL_SPEED = 5

COLORS = {
    "background": (30, 30, 30),
    "paddle": (0, 150, 255),
    "ball": (255, 215, 0),
    "text": (255, 255, 255),
    "bricks": [
        (255, 50, 50), (50, 255, 50),
        (50, 50, 255), (255, 255, 50),
        (255, 50, 255)
    ]
}

class Paddle:
    def __init__(self):
        self.rect = pygame.Rect(WIDTH//2 - PADDLE_WIDTH//2, HEIGHT-50, PADDLE_WIDTH, PADDLE_HEIGHT)
        self.speed = PADDLE_SPEED

    def move(self, direction):
        if direction == "left" and self.rect.left > 0:
            self.rect.x -= self.speed
        if direction == "right" and self.rect.right < WIDTH:
            self.rect.x += self.speed

    def draw(self, surface):
        pygame.draw.rect(surface, COLORS["paddle"], self.rect)
        pygame.draw.rect(surface, (255,255,255), self.rect, 2)

class Ball:
    def __init__(self):
        self.speed = BALL_SPEED
        self.radius = BALL_RADIUS
        self.reset()

    def reset(self):
        self.rect = pygame.Rect(WIDTH//2-BALL_RADIUS, HEIGHT//2-BALL_RADIUS, BALL_RADIUS*2, BALL_RADIUS*2)
        # 生成30-150度之间的角度，保证垂直分量充足
        base_angle = random.uniform(30, 150)
        # 随机左右方向
        if random.random() < 0.5:
            base_angle = 180 - base_angle
        
        direction = Vector2(1, 0).rotate(base_angle)
        direction.y = -abs(direction.y)  # 确保始终向上
        self.velocity = direction * self.speed

    def update(self):
        self.rect.x += self.velocity.x
        self.rect.y += self.velocity.y

        # 边界反弹
        if self.rect.left <= 0 or self.rect.right >= WIDTH:
            self.velocity.x *= -1
        if self.rect.top <= 0:
            self.velocity.y *= -1

    def draw(self, surface):
        pygame.draw.circle(surface, COLORS["ball"], self.rect.center, self.radius)
        pygame.draw.circle(surface, (255,255,255), self.rect.center, self.radius, 2)

class Brick:
    def __init__(self, x, y, color_index):
        self.rect = pygame.Rect(x, y, BRICK_WIDTH, BRICK_HEIGHT)
        self.color = COLORS["bricks"][color_index]
        self.active = True

    def draw(self, surface):
        if self.active:
            pygame.draw.rect(surface, self.color, self.rect)
            pygame.draw.rect(surface, (255,255,255), self.rect, 2)

class Game:
    def __init__(self):
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        pygame.display.set_caption("Modern Breakout")
        self.clock = pygame.time.Clock()
        self.font = pygame.font.Font(None, 36)
        self.reset_game()

    def reset_game(self):
        self.paddle = Paddle()
        self.ball = Ball()
        self.score = 0
        self.lives = 3
        self.bricks = []
        self.create_bricks()
        self.game_over = False
        self.win = False

    def create_bricks(self):
        for row in range(4):
            for col in range(WIDTH // BRICK_WIDTH):
                color_index = row % len(COLORS["bricks"])
                brick = Brick(col*BRICK_WIDTH, row*BRICK_HEIGHT+50, color_index)
                self.bricks.append(brick)

    def handle_input(self):
        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT] or keys[pygame.K_a]:
            self.paddle.move("left")
        if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            self.paddle.move("right")

    def check_collisions(self):
        # 球和挡板碰撞
        if self.ball.rect.colliderect(self.paddle.rect):
            # 计算碰撞点偏移量
            offset = (self.ball.rect.centerx - self.paddle.rect.centerx) / (PADDLE_WIDTH/2)
            # 保持垂直速度，调整水平速度
            self.ball.velocity.y = -abs(self.ball.velocity.y)  # 确保向上
            self.ball.velocity.x = offset * BALL_SPEED * 1.2  # 限制水平速度
            
            # 防止粘在挡板上
            self.ball.rect.bottom = self.paddle.rect.top

        # 球和砖块碰撞
        for brick in [b for b in self.bricks if b.active]:
            if self.ball.rect.colliderect(brick.rect):
                brick.active = False
                self.score += 10
                
                # 精确碰撞方向检测
                overlap_x = min(self.ball.rect.right, brick.rect.right) - max(self.ball.rect.left, brick.rect.left)
                overlap_y = min(self.ball.rect.bottom, brick.rect.bottom) - max(self.ball.rect.top, brick.rect.top)
                
                if overlap_x < overlap_y:
                    self.ball.velocity.x *= -1
                else:
                    self.ball.velocity.y *= -1
                break  # 每次只处理一个碰撞

        # 球掉出屏幕
        if self.ball.rect.bottom > HEIGHT:
            self.lives -= 1
            if self.lives > 0:
                self.ball.reset()
            else:
                self.game_over = True

        # 胜利条件
        if all(not brick.active for brick in self.bricks):
            self.win = True
            self.game_over = True

    def draw_ui(self):
        score_text = self.font.render(f"Score: {self.score}", True, COLORS["text"])
        lives_text = self.font.render(f"Lives: {self.lives}", True, COLORS["text"])
        self.screen.blit(score_text, (10, 10))
        self.screen.blit(lives_text, (WIDTH-120, 10))

        if self.game_over:
            text = "You Win!" if self.win else "Game Over!"
            text_render = self.font.render(text, True, COLORS["text"])
            restart_text = self.font.render("Press R to restart", True, COLORS["text"])
            self.screen.blit(text_render, (WIDTH//2 - text_render.get_width()//2, HEIGHT//2 - 30))
            self.screen.blit(restart_text, (WIDTH//2 - restart_text.get_width()//2, HEIGHT//2 + 10))

    def run(self):
        running = True
        while running:
            self.clock.tick(FPS)
            self.screen.fill(COLORS["background"])

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_r and self.game_over:
                        self.reset_game()

            if not self.game_over:
                self.handle_input()
                self.check_collisions()
                self.ball.update()

                self.paddle.draw(self.screen)
                self.ball.draw(self.screen)
                for brick in self.bricks:
                    brick.draw(self.screen)

            self.draw_ui()
            pygame.display.flip()

        pygame.quit()

if __name__ == "__main__":
    game = Game()
    game.run()
