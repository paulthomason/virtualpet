import pygame
import sys
import settings
from dog_park import draw_dog_park
from inventory import draw_inventory
from chat import draw_chat, update_chat, init_chat, chat_lines, handle_chat_event
from settings import (
    draw_settings,
    handle_settings_event,
    draw_sound_settings,
    handle_sound_event,
)
from birdie import draw_birdie
from snake import draw_snake, update_snake, handle_snake_event
from pong import draw_pong, update_pong, handle_pong_event
from tetris import draw_tetris, update_tetris, handle_tetris_event, reset_tetris
from typer import draw_type, handle_type_event
from battle import (
    draw_battle_menu,
    handle_battle_menu_event,
    start_practice_battle,
    draw_practice_battle,
    handle_practice_event,
    draw_gamelink,
    handle_gamelink_event,
)

pygame.init()
SIZE = 128
screen = pygame.display.set_mode((SIZE, SIZE))
pygame.display.set_caption("Virtual Pet Menu Prototype")

FONT = pygame.font.SysFont("monospace", 12)
BIGFONT = pygame.font.SysFont("monospace", 15)

WHITE = (255,255,255)
BLACK = (0,0,0)

menu_options = [
    "Birdie",
    "Dog Park",
    "Inventory",
    "Chat",
    "Settings",
    "Battle",
    "Snake",
    "Pong",
    "Tetris",
    "Type",
]
selected = 0
menu_scroll = 0
MAX_VISIBLE = 6
state = "menu"

clock = pygame.time.Clock()
running = True

# For passing state (e.g. chat)
chat_scroll = 0

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
                    if state == "Chat":
                        init_chat()
            else:
                if state == "Type":
                    if event.key == pygame.K_ESCAPE:
                        state = "menu"
                    else:
                        handle_type_event(event)
                elif state == "Battle":
                    selection = handle_battle_menu_event(event)
                    if selection == "Practice":
                        start_practice_battle()
                        state = "BattlePractice"
                    elif selection == "GameLink":
                        state = "BattleGameLink"
                    elif event.key == pygame.K_ESCAPE:
                        state = "menu"
                elif state == "BattlePractice":
                    if handle_practice_event(event):
                        state = "Battle"
                elif state == "BattleGameLink":
                    if handle_gamelink_event(event):
                        state = "Battle"
                elif state == "Settings":
                    if event.key == pygame.K_RETURN:
                        option = settings.settings_options[settings.selected_option]
                        if option["name"] == "Sound":
                            state = "SoundSettings"
                        else:
                            state = "menu"
                    else:
                        handle_settings_event(event)
                elif state == "SoundSettings":
                    if event.key == pygame.K_RETURN:
                        state = "Settings"
                    else:
                        handle_sound_event(event)
                elif state == "Chat":
                    if event.key == pygame.K_ESCAPE:
                        chat_scroll = 0
                        state = "menu"
                    elif event.key == pygame.K_PAGEUP:
                        chat_scroll += 1
                    elif event.key == pygame.K_PAGEDOWN:
                        chat_scroll -= 1
                    else:
                        handle_chat_event(event)
                elif event.key in [pygame.K_RETURN, pygame.K_SPACE]:
                    state = "menu"
                elif state == "Snake":
                    handle_snake_event(event)
                elif state == "Pong":
                    handle_pong_event(event)
                elif state == "Tetris":
                    handle_tetris_event(event)
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
    elif state == "SoundSettings":
        draw_sound_settings(screen, FONT)
    elif state == "Birdie":
        draw_birdie(screen, FONT)
    elif state == "Battle":
        draw_battle_menu(screen, FONT)
    elif state == "BattlePractice":
        draw_practice_battle(screen, FONT)
    elif state == "BattleGameLink":
        draw_gamelink(screen, FONT)
    elif state == "Snake":
        update_snake(now)
        draw_snake(screen, FONT)
    elif state == "Pong":
        update_pong(now)
        draw_pong(screen, FONT)
    elif state == "Tetris":
        update_tetris(now)
        draw_tetris(screen, FONT)
    elif state == "Type":
        draw_type(screen, FONT)

    pygame.display.flip()
    clock.tick(30)

pygame.quit()
sys.exit()
