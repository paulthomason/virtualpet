import pygame
import sys
from dog_park import draw_dog_park
from inventory import draw_inventory
from chat import draw_chat, update_chat
from settings import draw_settings, handle_settings_event
from birdie import draw_birdie
from snake import draw_snake, update_snake, handle_snake_event
from pong import draw_pong, update_pong, handle_pong_event
from typer import draw_type, handle_type_event

pygame.init()
SIZE = 128
screen = pygame.display.set_mode((SIZE, SIZE))
pygame.display.set_caption("Virtual Pet Menu Prototype")

FONT = pygame.font.SysFont("monospace", 12)
BIGFONT = pygame.font.SysFont("monospace", 15)

WHITE = (255,255,255)
BLACK = (0,0,0)

menu_options = ["Birdie", "Dog Park", "Inventory", "Chat", "Settings", "Snake", "Pong", "Type"]
selected = 0
menu_scroll = 0
MAX_VISIBLE = 6
state = "menu"

clock = pygame.time.Clock()
running = True

# For passing state (e.g. chat)
chat_lines = [
    {"user": "syl", "msg": "wat up"},
    {"user": "george", "msg": "yo"},
]
chat_scroll = 0
last_msg_time = 0

while running:
    now = pygame.time.get_ticks() / 1000.0
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        elif event.type == pygame.KEYDOWN:
            if state == "menu":
                if event.key in [pygame.K_UP, pygame.K_DOWN]:
                    if event.key == pygame.K_UP:
                        selected = (selected - 1) % len(menu_options)
                    else:
                        selected = (selected + 1) % len(menu_options)
                    if selected < menu_scroll:
                        menu_scroll = selected
                    elif selected >= menu_scroll + MAX_VISIBLE:
                        menu_scroll = selected - MAX_VISIBLE + 1
                    menu_scroll = max(0, min(menu_scroll, len(menu_options) - MAX_VISIBLE))
                elif event.key in [pygame.K_RETURN, pygame.K_SPACE]:
                    state = menu_options[selected]
            else:
                if state == "Type":
                    if event.key == pygame.K_ESCAPE:
                        state = "menu"
                    else:
                        handle_type_event(event)
                elif event.key in [pygame.K_RETURN, pygame.K_SPACE]:
                    if state == "Chat":
                        chat_scroll = 0
                    state = "menu"
                elif state == "Chat":
                    # Pass arrow key events for scrolling
                    if event.key == pygame.K_UP:
                        chat_scroll += 1
                    elif event.key == pygame.K_DOWN:
                        chat_scroll -= 1
                elif state == "Settings":
                    handle_settings_event(event)
                elif state == "Snake":
                    handle_snake_event(event)
                elif state == "Pong":
                    handle_pong_event(event)
        elif event.type == pygame.KEYUP:
            if state == "Pong":
                handle_pong_event(event)

    # Draw current screen
    if state == "menu":
        screen.fill((120, 180, 255))
        title = BIGFONT.render("Main Menu", True, BLACK)
        screen.blit(title, (10, 5))
        visible_options = menu_options[menu_scroll:menu_scroll + MAX_VISIBLE]
        for idx, option in enumerate(visible_options):
            i = menu_scroll + idx
            color = (50,100,255) if i == selected else BLACK
            text = FONT.render(option, True, color)
            screen.blit(text, (20, 28 + idx*16))
    elif state == "Dog Park":
        draw_dog_park(screen, FONT)
    elif state == "Inventory":
        draw_inventory(screen, FONT)
    elif state == "Chat":
        update_chat(chat_lines, now)
        draw_chat(screen, FONT, chat_lines, chat_scroll)
    elif state == "Settings":
        draw_settings(screen, FONT)
    elif state == "Birdie":
        draw_birdie(screen, FONT)
    elif state == "Snake":
        update_snake(now)
        draw_snake(screen, FONT)
    elif state == "Pong":
        update_pong(now)
        draw_pong(screen, FONT)
    elif state == "Type":
        draw_type(screen, FONT)

    pygame.display.flip()
    clock.tick(30)

pygame.quit()
sys.exit()
