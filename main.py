"""Main entry point for the virtual pet on the 1.44\" LCD HAT."""

import os
import sys
import time
import pygame  # Still used for input events
import settings
from PIL import Image, ImageFont
from luma.core.interface.serial import spi
from luma.core.render import canvas
from luma.lcd.device import st7735
from inventory import handle_inventory_event
from chat import init_chat, chat_lines, handle_chat_event
from settings import (
    handle_settings_event,
    handle_sound_event,
)
from snake import handle_snake_event
from pong import handle_pong_event
from tetris import (
    handle_tetris_event,
    reset_tetris,
    stop_music,
)
from typer import handle_type_event
import remote
import controller
from battle import (
    handle_battle_menu_event,
    start_practice_battle,
    handle_practice_event,
    handle_gamelink_event,
)

# Configure pygame to use the LCD HAT's framebuffer if running on the Pi
# Environment settings for the old pygame framebuffer output are kept
# for reference but are no longer required when using luma.lcd.
# os.environ.setdefault("SDL_VIDEODRIVER", "fbcon")
# os.environ.setdefault("SDL_FBDEV", "/dev/fb1")
# os.environ.setdefault("SDL_NOMOUSE", "1")

pygame.init()  # Still needed for event handling from controller
controller.init()
SIZE = 128

# SPI interface for the LCD; verify the GPIO numbers for your HAT
serial = spi(port=0, device=0, gpio_DC=24, gpio_RST=25, gpio_CS=8)

# Initialize the ST7735 display. h_offset and v_offset may need tuning.
device = st7735(serial, width=SIZE, height=SIZE, h_offset=2, v_offset=1)

# pygame screen no longer used
# screen = pygame.display.set_mode((SIZE, SIZE), pygame.FULLSCREEN)
# pygame.display.set_caption("Virtual Pet")
FONT = ImageFont.truetype(
    "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 12
)
BIGFONT = ImageFont.truetype(
    "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 15
)


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
    "Remote",
    "Type",
]
selected = 0
menu_scroll = 0
MAX_VISIBLE = 6
state = "menu"
prev_state = state

running = True

try:
    while running:
        prev_state = state
        now = time.time()

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
                        elif state == "Remote":
                            remote.start_server()
                        elif state == "Tetris":
                            reset_tetris()
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
                            state = "menu"
                        else:
                            handle_chat_event(event)
                    elif state == "Inventory":
                        if handle_inventory_event(event):
                            state = "menu"
                    elif state == "Remote":
                        if event.key in (pygame.K_RETURN, pygame.K_SPACE, pygame.K_ESCAPE):
                            state = "menu"
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

        # Stop Tetris music when leaving the screen
        if prev_state == "Tetris" and state != "Tetris":
            stop_music()

        # Draw current screen on the SPI LCD
        with canvas(device) as draw:
            draw.rectangle(device.bounding_box, outline="black", fill="black")
            if state == "menu":
                draw.text((10, 5), "Main Menu", font=BIGFONT, fill="white")
                visible = menu_options[menu_scroll:menu_scroll + MAX_VISIBLE]
                for idx, option in enumerate(visible):
                    i = menu_scroll + idx
                    color = "blue" if i == selected else "white"
                    draw.text((20, 28 + idx * 16), option, font=FONT, fill=color)
            else:
                draw.text((10, 54), f"{state} screen", font=FONT, fill="white")

        time.sleep(1/30)

except KeyboardInterrupt:
    pass
finally:
    controller.cleanup()
    pygame.quit()
    sys.exit()
