import pygame
import random

WIDTH, HEIGHT = 128, 128
PADDLE_W, PADDLE_H = 4, 20
BALL_SIZE = 4
PLAYER_X = 4
AI_X = WIDTH - PADDLE_W - 4

player_y = HEIGHT // 2 - PADDLE_H // 2
ai_y = HEIGHT // 2 - PADDLE_H // 2
ball_pos = [WIDTH // 2, HEIGHT // 2]
ball_vel = [2, 2]


def reset_pong():
    global player_y, ai_y, ball_pos, ball_vel
    player_y = HEIGHT // 2 - PADDLE_H // 2
    ai_y = HEIGHT // 2 - PADDLE_H // 2
    ball_pos = [WIDTH // 2, HEIGHT // 2]
    ball_vel = [random.choice([-2, 2]), random.choice([-2, 2])]


reset_pong()


def handle_pong_event(event):
    """Move the player paddle."""
    global player_y
    if event.key == pygame.K_UP:
        player_y -= 4
    elif event.key == pygame.K_DOWN:
        player_y += 4
    player_y = max(0, min(HEIGHT - PADDLE_H, player_y))


def update_pong(now):
    """Update pong game state."""
    global ball_pos, ball_vel, ai_y

    # Move ball
    ball_pos[0] += ball_vel[0]
    ball_pos[1] += ball_vel[1]

    # Bounce off top/bottom
    if ball_pos[1] <= 0 or ball_pos[1] >= HEIGHT - BALL_SIZE:
        ball_vel[1] *= -1

    # Player paddle collision
    if (PLAYER_X <= ball_pos[0] <= PLAYER_X + PADDLE_W and
            player_y <= ball_pos[1] <= player_y + PADDLE_H):
        ball_vel[0] = abs(ball_vel[0])

    # AI paddle collision
    if (AI_X <= ball_pos[0] + BALL_SIZE <= AI_X + PADDLE_W and
            ai_y <= ball_pos[1] <= ai_y + PADDLE_H):
        ball_vel[0] = -abs(ball_vel[0])

    # Left or right edge -> reset
    if ball_pos[0] < 0 or ball_pos[0] > WIDTH:
        reset_pong()

    # Simple AI movement (medium difficulty)
    if ball_pos[1] > ai_y + PADDLE_H // 2:
        ai_y += 2
    else:
        ai_y -= 2
    ai_y = max(0, min(HEIGHT - PADDLE_H, ai_y))


def draw_pong(screen, FONT):
    screen.fill((0, 0, 0))
    pygame.draw.rect(screen, (255, 255, 255),
                     (PLAYER_X, player_y, PADDLE_W, PADDLE_H))
    pygame.draw.rect(screen, (255, 255, 255),
                     (AI_X, ai_y, PADDLE_W, PADDLE_H))
    pygame.draw.rect(screen, (255, 255, 255),
                     (ball_pos[0], ball_pos[1], BALL_SIZE, BALL_SIZE))

    tip = FONT.render("Arrows=Move  Enter=Back", True, (200, 200, 200))
    screen.blit(tip, (2, 114))
