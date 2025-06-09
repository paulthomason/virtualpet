import pygame
import random

GRID_SIZE = 8
COLS = 10
ROWS = 16
BOARD_X = 24

# Define tetromino shapes with rotation states
SHAPES = [
    # O
    [[(0,0),(1,0),(0,1),(1,1)]],
    # I
    [[(0,0),(1,0),(2,0),(3,0)],
     [(1,-1),(1,0),(1,1),(1,2)]],
    # T
    [[(0,0),(1,0),(2,0),(1,1)],
     [(1,0),(1,1),(1,2),(2,1)],
     [(0,1),(1,1),(2,1),(1,0)],
     [(0,1),(1,0),(1,1),(1,2)]],
    # L
    [[(0,0),(0,1),(0,2),(1,2)],
     [(0,1),(1,1),(2,1),(0,2)],
     [(0,0),(1,0),(1,1),(1,2)],
     [(0,1),(1,1),(2,1),(2,0)]],
]

board = [[0]*COLS for _ in range(ROWS)]
current = None
rotation = 0
position = [COLS//2-2, 0]
last_drop = 0
DROP_DELAY = 0.5
score = 0
high_score = 0


def _new_piece():
    """Spawn a new random piece"""
    global current, rotation, position, high_score, score
    current = random.choice(SHAPES)
    rotation = 0
    position = [COLS//2-2, 0]
    if _collision(position, rotation):
        if score > high_score:
            high_score = score
        _reset_board()


def _reset_board():
    """Clear the board and reset score"""
    global board, score
    board = [[0]*COLS for _ in range(ROWS)]
    score = 0
    _new_piece()


def reset_tetris():
    _reset_board()


def _collision(pos, rot):
    for x,y in current[rot]:
        px = pos[0]+x
        py = pos[1]+y
        if px < 0 or px >= COLS or py >= ROWS:
            return True
        if py >=0 and board[py][px]:
            return True
    return False


def _merge_piece():
    for x,y in current[rotation]:
        px = position[0]+x
        py = position[1]+y
        if py >=0:
            board[py][px] = 1


def _clear_lines():
    global board, score
    new_board = [row for row in board if not all(row)]
    cleared = ROWS - len(new_board)
    if cleared:
        score += cleared * 100
        for _ in range(cleared):
            new_board.insert(0,[0]*COLS)
    board = new_board


def handle_tetris_event(event):
    global position, rotation
    if event.key == pygame.K_LEFT:
        new_pos = [position[0]-1, position[1]]
        if not _collision(new_pos, rotation):
            position = new_pos
    elif event.key == pygame.K_RIGHT:
        new_pos = [position[0]+1, position[1]]
        if not _collision(new_pos, rotation):
            position = new_pos
    elif event.key == pygame.K_UP:
        new_rot = (rotation+1)%len(current)
        if not _collision(position, new_rot):
            rotation = new_rot
    elif event.key == pygame.K_DOWN:
        # drop faster
        new_pos = [position[0], position[1]+1]
        if not _collision(new_pos, rotation):
            position = new_pos
        else:
            _merge_piece()
            _clear_lines()
            _new_piece()


def update_tetris(now):
    global last_drop, position
    if now - last_drop < DROP_DELAY:
        return
    last_drop = now
    new_pos = [position[0], position[1]+1]
    if _collision(new_pos, rotation):
        _merge_piece()
        _clear_lines()
        _new_piece()
    else:
        position = new_pos


def draw_tetris(screen, FONT):
    screen.fill((0,0,0))
    # draw settled blocks
    for y,row in enumerate(board):
        for x,val in enumerate(row):
            if val:
                pygame.draw.rect(screen, (200,200,200),
                                 (BOARD_X+x*GRID_SIZE, y*GRID_SIZE,
                                  GRID_SIZE, GRID_SIZE))
    # draw current piece
    for x,y in current[rotation]:
        px = position[0]+x
        py = position[1]+y
        if py >= 0:
            pygame.draw.rect(screen, (0,200,200),
                             (BOARD_X+px*GRID_SIZE, py*GRID_SIZE,
                              GRID_SIZE, GRID_SIZE))
    sc = FONT.render(f"Score:{score} High:{high_score}", True, (200,200,200))
    screen.blit(sc,(2,2))
    tip = FONT.render("Arrows Move Up Rot Enter Back", True,(200,200,200))
    screen.blit(tip,(2,114))

# initialise first piece
_new_piece()
