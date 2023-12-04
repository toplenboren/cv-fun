import pygame
import sys
import random

# Initialize Pygame
pygame.init()

# Constants
WIDTH, HEIGHT = 800, 600
BALL_RADIUS = 10
PADDLE_WIDTH, PADDLE_HEIGHT = 100, 20
BRICK_WIDTH, BRICK_HEIGHT = 80, 30
PADDLE_SPEED = 10
BALL_SPEED = 5
TRAIL_LENGTH = 100  # Number of frames for the trail effect

# Colors
WHITE = (255, 255, 255)
RED = (255, 0, 0)
BLUE = (0, 0, 255)

# Create the game window
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Arkanoid Game")

# Create the paddle
paddle = pygame.Rect(WIDTH // 2 - PADDLE_WIDTH // 2, HEIGHT - PADDLE_HEIGHT - 10, PADDLE_WIDTH, PADDLE_HEIGHT)

# Create the ball
ball = pygame.Rect(WIDTH // 2 - BALL_RADIUS, HEIGHT // 2 - BALL_RADIUS, BALL_RADIUS * 2, BALL_RADIUS * 2)
ball_speed = [random.choice([-1, 1]) * BALL_SPEED, -BALL_SPEED]

# Create the bricks
bricks = []
for row in range(5):
    for col in range(WIDTH // BRICK_WIDTH):
        brick = pygame.Rect(col * BRICK_WIDTH, row * BRICK_HEIGHT + 50, BRICK_WIDTH, BRICK_HEIGHT)
        bricks.append(brick)

# Create a font for the game over screen
font = pygame.font.Font(None, 48)

# Game state
game_over = False
paused = False
trail_frames = 0


def handle_input():
    global paused, game_over

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE and not game_over:
                paused = not paused


def move_paddle():
    keys = pygame.key.get_pressed()
    if keys[pygame.K_LEFT] and paddle.left > 0:
        paddle.move_ip(-PADDLE_SPEED, 0)
    if keys[pygame.K_RIGHT] and paddle.right < WIDTH:
        paddle.move_ip(PADDLE_SPEED, 0)


def move_ball():
    ball.move_ip(ball_speed[0], ball_speed[1])


def check_collisions():
    global trail_frames

    # Ball collision with walls
    if ball.left < 0 or ball.right > WIDTH:
        ball_speed[0] = -ball_speed[0]
    if ball.top < 0:
        ball_speed[1] = -ball_speed[1]

    # Ball collision with paddle
    if ball.colliderect(paddle) and ball_speed[1] > 0:
        ball_speed[1] = -ball_speed[1]

        # Apply the trail effect
        trail_frames = TRAIL_LENGTH

    # Ball collision with bricks
    for brick in bricks[:]:
        if ball.colliderect(brick):
            bricks.remove(brick)
            ball_speed[1] = -ball_speed[1]


def draw_objects():
    screen.fill(WHITE)
    pygame.draw.rect(screen, BLUE, paddle)
    pygame.draw.ellipse(screen, RED, ball)

    for brick in bricks:
        pygame.draw.rect(screen, BLUE, brick)


def draw_game_over_screen():
    game_over_text = font.render("Game Over", True, RED)
    screen.blit(game_over_text, (WIDTH // 2 - 90, HEIGHT // 2))


def draw_pause_screen():
    game_over_text = font.render("Paused. Press <SPACE> to continue", True, RED)
    screen.blit(game_over_text, (WIDTH // 2 - 280, HEIGHT // 2))


# Main game loop
while True:
    handle_input()

    should_continue = not game_over and not paused

    if should_continue:
        move_paddle()
        move_ball()
        check_collisions()
        draw_objects()

        # Check for game over
        if ball.bottom > HEIGHT:
            game_over = True

    if paused:
        draw_pause_screen()

    if game_over:
        draw_game_over_screen()

    pygame.display.flip()

    # Control the frame rate
    pygame.time.Clock().tick(60)  # Adjust the value to control the frames per second
