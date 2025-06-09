import logging
import time

from luma.core.interface.serial import spi
from luma.core.render import canvas
from luma.lcd.device import st7735

logger = logging.getLogger("test")
if not logger.handlers:
    handler = logging.FileHandler("test.txt", mode="a")
    handler.setFormatter(logging.Formatter("%(asctime)s %(levelname)s: %(message)s"))
    logger.addHandler(handler)
logger.setLevel(logging.DEBUG)

logger.info("Starting red screen test")

try:
    logger.debug("Creating SPI interface")
    serial = spi(port=0, device=0, gpio_DC=24, gpio_RST=25, gpio_CS=8)
    logger.info("SPI interface created")
except Exception as exc:
    logger.exception(f"Failed to create SPI interface: {exc}")
    raise

try:
    logger.debug("Initialising ST7735 display")
    device = st7735(serial, width=128, height=128, h_offset=2, v_offset=1)
    logger.info("Display initialised")
except Exception as exc:
    logger.exception(f"Failed to initialise display: {exc}")
    raise

try:
    logger.debug("Drawing red screen")
    with canvas(device) as draw:
        draw.rectangle(device.bounding_box, outline="red", fill="red")
    logger.info("Red screen displayed")
    time.sleep(2)
except Exception as exc:
    logger.exception(f"Failed during drawing: {exc}")
    raise

logger.info("Display test completed")
