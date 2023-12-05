import pygame
import sys
import random

import cv2

# Initialize Pygame
pygame.init()

# Constants
WIDTH, HEIGHT = 1200, 1000
BALL_RADIUS = 20
PADDLE_WIDTH, PADDLE_HEIGHT = 200, 40
BRICK_WIDTH, BRICK_HEIGHT = 150, 40
BRICK_HEIGHT_Q = 3
PADDLE_SPEED = 20
BALL_SPEED = 15

# Colors
WHITE = (255, 255, 255)
RED = (255, 0, 0)
BLUE = (0, 0, 255)

TARGET_FPS = 60

# Background Subtractor settings
BG_SUB_HISTORY = 500
BG_SUB_VAR_THRESHOLD = 10
BG_SUB_DETECT_SHADOWS = False

# Minimum area threshold for a valid moving object
MIN_CONTOUR_AREA = 40000

# Smoothing factor for the dot's movement (adjust as needed)
SMOOTHING_FACTOR = 0.1

KSIZE = (7, 7)

# Create a background subtractor object
bg_subtractor = cv2.createBackgroundSubtractorMOG2(
    history=BG_SUB_HISTORY,
    varThreshold=BG_SUB_VAR_THRESHOLD,
    detectShadows=BG_SUB_DETECT_SHADOWS
)

cap = cv2.VideoCapture(0)

last_contour = None
smoothed_center = None


def get_new_center(bounding_rect, prev_smoothed_center=None):
    x, y, w, h = bounding_rect

    center_x = x + w // 2
    center_y = y + h // 2

    if prev_smoothed_center is None:
        return center_x, center_y
    else:
        return (
            int((1 - SMOOTHING_FACTOR) * prev_smoothed_center[0] + SMOOTHING_FACTOR * center_x),
            int((1 - SMOOTHING_FACTOR) * prev_smoothed_center[1] + SMOOTHING_FACTOR * center_y)
        )


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
pygame.display.set_caption("Paranoid arkanoid")

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
            # Release the video capture object and close all windows
            cap.release()
            cv2.destroyAllWindows()

            pygame.quit()
            sys.exit()
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE and not game_over:
                paused = not paused
            if event.key == pygame.K_r:
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
        pygame.draw.rect(screen, RED, brick)


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

    # Handle CV stuff
    # Read a frame from the video feed
    ret, frame = cap.read()
    if not ret:
        break

    # Apply the background subtractor to get the foreground mask
    fg_mask_raw = bg_subtractor.apply(frame)

    # Apply some morphological operations to reduce noise
    kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, KSIZE)
    fg_mask = cv2.morphologyEx(fg_mask_raw, cv2.MORPH_OPEN, kernel)
    fg_mask = cv2.morphologyEx(fg_mask, cv2.MORPH_CLOSE, kernel)

    # Find contours in the foreground mask
    contours, _ = cv2.findContours(fg_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    # Filter contours based on minimum area
    valid_contours = [contour for contour in contours if cv2.contourArea(contour) > MIN_CONTOUR_AREA]

    # Find the contour with the maximum area
    max_contour = max(valid_contours, key=cv2.contourArea, default=None)

    if max_contour is not None:
        last_contour = max_contour

    active_contour = last_contour

    if active_contour is not None:
        # Calculate the center of the bounding area
        x, y, w, h = cv2.boundingRect(active_contour)

        # Smooth the movement of the dot
        smoothed_center = get_new_center((x, y, w, h), smoothed_center)

        if smoothed_center is not None:
            # Update the paddle X position
            paddle.x = WIDTH - (smoothed_center[0] - PADDLE_WIDTH // 2)
            paddle.x = max(0, min(WIDTH - PADDLE_WIDTH, paddle.x))

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
    pygame.time.Clock().tick(TARGET_FPS)
