"""Interactive settings screen."""

import pygame

# Available settings with default values
settings_options = [
    {"name": "Sound", "type": "bool", "value": True},
    {"name": "Difficulty", "type": ["Easy", "Normal", "Hard"], "value": "Normal"},
    {"name": "Show Tips", "type": "bool", "value": True},
]

# Index of the currently selected setting
selected_option = 0


def handle_settings_event(event):
    """Handle key input when the settings screen is active."""
    global selected_option

    if event.key == pygame.K_UP:
        selected_option = (selected_option - 1) % len(settings_options)
    elif event.key == pygame.K_DOWN:
        selected_option = (selected_option + 1) % len(settings_options)
    elif event.key in (pygame.K_LEFT, pygame.K_RIGHT, pygame.K_SPACE):
        option = settings_options[selected_option]
        if option["type"] == "bool":
            option["value"] = not option["value"]
        else:
            choices = option["type"]
            idx = choices.index(option["value"])
            if event.key == pygame.K_LEFT:
                idx = (idx - 1) % len(choices)
            else:
                idx = (idx + 1) % len(choices)
            option["value"] = choices[idx]


def draw_settings(screen, FONT):
    """Render the settings menu to ``screen`` using ``FONT``."""
    screen.fill((80, 80, 120))

    title = FONT.render("Settings", True, (255, 255, 255))
    screen.blit(title, (6, 4))

    for i, option in enumerate(settings_options):
        color = (200, 255, 200) if i == selected_option else (255, 255, 255)
        text = f"{option['name']}: {option['value']}"
        msg = FONT.render(text, True, color)
        screen.blit(msg, (6, 24 + i * 16))

    tip = FONT.render("Arrows=Change  Enter=Back", True, (200, 220, 255))
    screen.blit(tip, (6, 114))
