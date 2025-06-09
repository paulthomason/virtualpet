# Virtual Pet for Raspberry Pi Zero 2 W

This project is tailored for the [Waveshare 1.44" LCD HAT](https://www.waveshare.com/wiki/1.44inch_LCD_HAT).
It uses the HAT's 128x128 display and built in five‑way joystick with
three additional buttons as the sole input and output devices.

The application is written with `pygame` and expects to run directly on
the Pi's framebuffer (`/dev/fb1`).  When launched it will open a full
screen window and listen for GPIO events from the joystick and buttons.

Run the main program with:

```bash
python3 main.py
```

Ensure the environment variables `SDL_VIDEODRIVER=fbcon` and
`SDL_FBDEV=/dev/fb1` are available (these are set automatically in
`main.py`).

