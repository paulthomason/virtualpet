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


def set_volume(volume: int) -> None:
    """Attempt to set system volume using ``amixer``."""
    level = max(0, min(100, volume))
    try:
        subprocess.check_call(["amixer", "set", "Master", f"{level}%"])
    except Exception:
        pass


def toggle_bluetooth(on: bool) -> None:
    """Placeholder for connecting or disconnecting a Bluetooth speaker."""
    cmd = ["bluetoothctl", "power", "on" if on else "off"]
    try:
        subprocess.check_call(cmd)
    except Exception:
        pass


def available_sinks() -> list:
    """Return a list of available sound output sinks."""
    try:
        out = subprocess.check_output(["pactl", "list", "short", "sinks"]).decode()
        return [line.split("\t")[1] for line in out.splitlines() if line]
    except Exception:
        return ["default"]


def current_sink() -> str:
    """Return the name of the current default sound sink."""
    try:
        out = subprocess.check_output(["pactl", "info"]).decode()
        for line in out.splitlines():
            if line.lower().startswith("default sink:"):
                return line.split(":", 1)[1].strip()
    except Exception:
        pass
    return "default"


def set_default_sink(sink: str) -> None:
    """Set the system default sound sink."""
    try:
        subprocess.check_call(["pactl", "set-default-sink", sink])
    except Exception:
        pass


# Cached list of sinks and current default
_SINKS = available_sinks()
_CURRENT_SINK = current_sink()
if _CURRENT_SINK not in _SINKS:
    _SINKS.append(_CURRENT_SINK)

# Available settings with default values
settings_options = [
    {"name": "Sound", "type": "submenu"},
    {"name": "Difficulty", "type": ["Easy", "Normal", "Hard"], "value": "Normal"},
    {"name": "Show Tips", "type": "bool", "value": True},
    {"name": "WiFi", "type": "bool", "value": wifi_enabled()},
]

# Index of the currently selected setting
selected_option = 0

# Options within the sound submenu
sound_options = [
    {"name": "Volume", "type": "range", "value": 50},
    {"name": "Bluetooth", "type": "bool", "value": False},
    {
        "name": "Output",
        "type": _SINKS,
        "value": _CURRENT_SINK,
    },
]
# Currently selected option in the sound menu
selected_sound = 0


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
        elif isinstance(option["type"], list):
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
        text_value = option.get("value")
        if option["type"] == "submenu":
            text = option["name"]
        else:
            if option['name'] == 'WiFi':
                status = 'On' if option['value'] else 'Off'
                text_value = f"{status} ({current_ssid()})"
            text = f"{option['name']}: {text_value}"
        msg = FONT.render(text, True, color)
        screen.blit(msg, (6, 24 + i * 16))

    tip = FONT.render("Arrows=Change  Enter=Back", True, (200, 220, 255))
    screen.blit(tip, (6, 114))


def handle_sound_event(event):
    """Handle key input on the sound settings screen."""
    global selected_sound

    if event.key == pygame.K_UP:
        selected_sound = (selected_sound - 1) % len(sound_options)
    elif event.key == pygame.K_DOWN:
        selected_sound = (selected_sound + 1) % len(sound_options)
    elif event.key in (pygame.K_LEFT, pygame.K_RIGHT, pygame.K_SPACE):
        option = sound_options[selected_sound]
        if option["name"] == "Volume":
            delta = -10 if event.key == pygame.K_LEFT else 10
            option["value"] = max(0, min(100, option["value"] + delta))
            set_volume(option["value"])
        elif option["name"] == "Bluetooth":
            option["value"] = not option["value"]
            toggle_bluetooth(option["value"])
        elif option["name"] == "Output":
            choices = option["type"]
            idx = choices.index(option["value"]) if option["value"] in choices else 0
            if event.key == pygame.K_LEFT:
                idx = (idx - 1) % len(choices)
            else:
                idx = (idx + 1) % len(choices)
            option["value"] = choices[idx]
            set_default_sink(option["value"])


def draw_sound_settings(screen, FONT):
    """Render the sound settings menu."""
    screen.fill((60, 60, 100))

    title = FONT.render("Sound Settings", True, (255, 255, 255))
    screen.blit(title, (6, 4))

    for i, option in enumerate(sound_options):
        color = (200, 255, 200) if i == selected_sound else (255, 255, 255)
        value = option["value"]
        if option["name"] == "Bluetooth":
            value = "On" if option["value"] else "Off"
        text = f"{option['name']}: {value}"
        msg = FONT.render(text, True, color)
        screen.blit(msg, (6, 24 + i * 16))

    tip = FONT.render("Arrows=Change  Enter=Back", True, (200, 220, 255))
    screen.blit(tip, (6, 114))
