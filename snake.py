import pygame
import random

GRID_SIZE = 8
GRID_WIDTH = 16
GRID_HEIGHT = 16

snake = []
direction = (1, 0)
apple = (0, 0)
last_move = 0
MOVE_DELAY = 0.2


def _place_apple():
    global apple
    while True:
        apple = (random.randint(0, GRID_WIDTH - 1),
                 random.randint(0, GRID_HEIGHT - 1))
        if apple not in snake:
            break


def reset_snake():
    """Reset snake game state."""
    global snake, direction, last_move
    snake = [(GRID_WIDTH // 2, GRID_HEIGHT // 2)]
    direction = (1, 0)
    _place_apple()
    last_move = 0


reset_snake()


def handle_snake_event(event):
    """Update direction based on arrow key input."""
    global direction
    if event.key == pygame.K_UP and direction != (0, 1):
        direction = (0, -1)
    elif event.key == pygame.K_DOWN and direction != (0, -1):
        direction = (0, 1)
    elif event.key == pygame.K_LEFT and direction != (1, 0):
        direction = (-1, 0)
    elif event.key == pygame.K_RIGHT and direction != (-1, 0):
        direction = (1, 0)


def update_snake(now):
    """Advance the snake if enough time has passed."""
    global last_move
    if now - last_move < MOVE_DELAY:
        return
    last_move = now

    head_x, head_y = snake[0]
    dx, dy = direction
    new_head = (head_x + dx, head_y + dy)

    # Collision with walls or self resets the game
    if (new_head[0] < 0 or new_head[0] >= GRID_WIDTH or
            new_head[1] < 0 or new_head[1] >= GRID_HEIGHT or
            new_head in snake):
        reset_snake()
        return

    snake.insert(0, new_head)
    if new_head == apple:
        _place_apple()
    else:
        snake.pop()


def draw_snake(screen, FONT):
    """Render the snake game."""
    screen.fill((0, 0, 0))
    for x, y in snake:
        pygame.draw.rect(screen, (0, 200, 0),
                         (x * GRID_SIZE, y * GRID_SIZE, GRID_SIZE, GRID_SIZE))
    pygame.draw.rect(screen, (200, 0, 0),
                     (apple[0] * GRID_SIZE, apple[1] * GRID_SIZE,
                      GRID_SIZE, GRID_SIZE))
    tip = FONT.render("Arrows=Move  Enter=Back", True, (200, 200, 200))
    screen.blit(tip, (2, 114))
