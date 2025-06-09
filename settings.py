"""Interactive settings screen."""

import pygame
import subprocess


def wifi_enabled():
    """Return True if WiFi radio is enabled."""
    try:
        out = subprocess.check_output(["nmcli", "radio", "wifi"]).decode().strip()
        return out.lower() == "enabled"
    except Exception:
        return True


def set_wifi_enabled(enabled: bool) -> None:
    """Enable or disable WiFi radio using nmcli."""
    cmd = ["nmcli", "radio", "wifi", "on" if enabled else "off"]
    try:
        subprocess.check_call(cmd)
    except Exception:
        pass


def current_ssid() -> str:
    """Return the SSID of the currently connected network, if any."""
    try:
        out = subprocess.check_output([
            "nmcli",
            "-t",
            "-f",
            "active,ssid",
            "device",
            "wifi",
        ]).decode()
        for line in out.splitlines():
            if line.startswith("yes:"):
                return line.split(":", 1)[1] or "unknown"
    except Exception:
        pass
    return "unknown"

# Available settings with default values
settings_options = [
    {"name": "Sound", "type": "bool", "value": True},
    {"name": "Difficulty", "type": ["Easy", "Normal", "Hard"], "value": "Normal"},
    {"name": "Show Tips", "type": "bool", "value": True},
    {"name": "WiFi", "type": "bool", "value": wifi_enabled()},
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
            if option["name"] == "WiFi":
                set_wifi_enabled(option["value"])
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
        text_value = option['value']
        if option['name'] == 'WiFi':
            status = 'On' if option['value'] else 'Off'
            text_value = f"{status} ({current_ssid()})"
        text = f"{option['name']}: {text_value}"
        msg = FONT.render(text, True, color)
        screen.blit(msg, (6, 24 + i * 16))

    tip = FONT.render("Arrows=Change  Enter=Back", True, (200, 220, 255))
    screen.blit(tip, (6, 114))
