"""GPIO input handler for the Waveshare 1.44" LCD HAT."""

import logging
import pygame
try:
    import RPi.GPIO as GPIO
except ImportError:  # Allow running on non-RPi platforms
    GPIO = None

# Shared logger for HAT-related activity
logger = logging.getLogger("hat")
if not logger.handlers:
    handler = logging.FileHandler("hatlog.txt", mode="a")
    handler.setFormatter(
        logging.Formatter("%(asctime)s %(levelname)s: %(message)s")
    )
    logger.addHandler(handler)
logger.setLevel(logging.DEBUG)

# GPIO pin definitions for the 1.44" LCD HAT
PIN_JOY_UP = 6
PIN_JOY_DOWN = 19
PIN_JOY_LEFT = 5
PIN_JOY_RIGHT = 26
PIN_JOY_PRESS = 13
PIN_KEY1 = 21
PIN_KEY2 = 20
PIN_KEY3 = 16

# Mapping of GPIO pins to pygame key constants
PIN_KEY_MAP = {
    PIN_JOY_UP: pygame.K_UP,
    PIN_JOY_DOWN: pygame.K_DOWN,
    PIN_JOY_LEFT: pygame.K_LEFT,
    PIN_JOY_RIGHT: pygame.K_RIGHT,
    PIN_JOY_PRESS: pygame.K_RETURN,
    PIN_KEY1: pygame.K_SPACE,
    PIN_KEY2: pygame.K_ESCAPE,
    PIN_KEY3: pygame.K_TAB,
}


def init() -> None:
    """Initialise GPIO handling and register callbacks."""
    if GPIO is None:
        # If GPIO is unavailable we fall back to keyboard controls.
        logger.warning("GPIO not available; using keyboard input")
        return

    # Clear any previous GPIO configuration that might remain if the
    # application exited unexpectedly.  This helps avoid "Failed to add edge
    # detection" errors when rerunning the program.
    logger.debug("Configuring GPIO pins")
    GPIO.cleanup()
    GPIO.setmode(GPIO.BCM)
    for pin in PIN_KEY_MAP:
        GPIO.setup(pin, GPIO.IN, pull_up_down=GPIO.PUD_UP)
        try:
            GPIO.add_event_detect(
                pin, GPIO.BOTH, callback=_handle, bouncetime=50
            )
            logger.debug(f"Added event detection for pin {pin}")
        except RuntimeError:
            # If event detection is already in place for this pin, remove and
            # try again so that reruns work without manual cleanup.
            try:
                GPIO.remove_event_detect(pin)
                GPIO.add_event_detect(
                    pin, GPIO.BOTH, callback=_handle, bouncetime=50
                )
                logger.debug(f"Re-added event detection for pin {pin}")
            except RuntimeError as exc:
                logger.exception(f"Failed to add edge detection for pin {pin}: {exc}")


def cleanup() -> None:
    """Clean up GPIO resources."""
    if GPIO is not None:
        GPIO.cleanup()
        logger.debug("GPIO cleanup complete")


def _handle(pin: int) -> None:
    """Internal callback translating GPIO changes into pygame events."""
    key = PIN_KEY_MAP.get(pin)
    if key is None:
        return
    pressed = GPIO.input(pin) == GPIO.LOW
    event_type = pygame.KEYDOWN if pressed else pygame.KEYUP
    pygame.event.post(pygame.event.Event(event_type, key=key))
    state = "pressed" if pressed else "released"
    logger.debug(f"Pin {pin} {state}")
