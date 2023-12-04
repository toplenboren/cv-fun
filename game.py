import pygame
import sys
import random

# Initialize Pygame
pygame.init()

# Constants
WIDTH, HEIGHT = 1200, 1000
BALL_RADIUS = 20
PADDLE_WIDTH, PADDLE_HEIGHT = 200, 40
BRICK_WIDTH, BRICK_HEIGHT = 150, 40
BRICK_HEIGHT_Q = 1
PADDLE_SPEED = 20
BALL_SPEED = 10
TRAIL_LENGTH = 100  # Number of frames for the trail effect

# Colors
WHITE = (255, 255, 255)
RED = (255, 0, 0)
BLUE = (0, 0, 255)


def get_initial_paddle():
    return pygame.Rect(WIDTH // 2 - PADDLE_WIDTH // 2, HEIGHT - PADDLE_HEIGHT - 10, PADDLE_WIDTH, PADDLE_HEIGHT)


def get_initial_ball():
    return pygame.Rect(WIDTH // 2 - BALL_RADIUS, HEIGHT // 2 - BALL_RADIUS, BALL_RADIUS * 2, BALL_RADIUS * 2)


def get_initial_ball_speed():
    return [random.choice([-1, 1]) * BALL_SPEED, -BALL_SPEED]


def get_initial_bricks():
    bricks = []
    for row in range(BRICK_HEIGHT_Q):
        for col in range(WIDTH // BRICK_WIDTH):
            brick = pygame.Rect(col * BRICK_WIDTH, row * BRICK_HEIGHT + 50, BRICK_WIDTH, BRICK_HEIGHT)
            bricks.append(brick)
    return bricks


# Create the game window
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Arkanoid Game")

# Create the paddle
paddle = get_initial_paddle()

# Create the ball
ball = get_initial_ball()
ball_speed = get_initial_ball_speed()

# Create the bricks
bricks = get_initial_bricks()

# Create a font for the game over screen
font = pygame.font.Font(None, 48)

# Game state
game_over = False
paused = False
win = False


def handle_input():
    global paused, game_over

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE and not game_over:
                paused = not paused
            if event.key == pygame.K_r:
                # Restart the game
                game_over = False
                reset_game()


def reset_game():
    global game_over, win
    global paddle, ball, ball_speed, bricks

    win = False
    game_over = False

    # Reset paddle position
    paddle = get_initial_paddle()

    # Reset ball position and speed
    ball = get_initial_ball()
    ball_speed = get_initial_ball_speed()

    bricks = get_initial_bricks()


def move_paddle():
    keys = pygame.key.get_pressed()
    if keys[pygame.K_LEFT] and paddle.left > 0:
        paddle.move_ip(-PADDLE_SPEED, 0)
    if keys[pygame.K_RIGHT] and paddle.right < WIDTH:
        paddle.move_ip(PADDLE_SPEED, 0)


def move_ball():
    ball.move_ip(ball_speed[0], ball_speed[1])


def check_collisions():
    # Ball collision with walls
    if ball.left < 0 or ball.right > WIDTH:
        ball_speed[0] = -ball_speed[0]
    if ball.top < 0:
        ball_speed[1] = -ball_speed[1]

    # Ball collision with paddle
    if ball.colliderect(paddle) and ball_speed[1] > 0:
        ball_speed[1] = -ball_speed[1]

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
    game_over_text = font.render("Game Over. Press <R> to restart", True, RED)
    screen.blit(game_over_text, (WIDTH // 2 - 270, HEIGHT // 2))


def draw_pause_screen():
    game_over_text = font.render("Paused. Press <SPACE> to continue", True, RED)
    screen.blit(game_over_text, (WIDTH // 2 - 280, HEIGHT // 2))


def draw_win_screen():
    game_over_text = font.render("You won. Press <R> to start again", True, RED)
    screen.blit(game_over_text, (WIDTH // 2 - 280, HEIGHT // 2))


# Main game loop
while True:
    handle_input()

    should_continue = not game_over and not paused and not win

    if should_continue:
        move_paddle()
        move_ball()
        check_collisions()
        draw_objects()

        # Check for game over
        if ball.bottom > HEIGHT:
            game_over = True

        # Check for win
        if len(bricks) == 0:
            win = True

    if paused:
        draw_pause_screen()

    if game_over:
        draw_game_over_screen()

    if win:
        draw_win_screen()

    pygame.display.flip()

    # Control the frame rate
    pygame.time.Clock().tick(60)
