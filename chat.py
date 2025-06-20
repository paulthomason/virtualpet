"""Simple IRC chat viewer for the virtual pet demo."""

import socket
import threading
import logging
import pygame
import queue

# Typing state for composing outgoing messages
keyboard_chars = list("abcdefghijklmnopqrstuvwxyz0123456789.,!? ")
VISIBLE = 10
cursor = 0
scroll = 0
typed_text = ""
shift = False

# Queue used by the IRC thread to send outgoing messages
send_queue: queue.Queue[str] = queue.Queue()

# Nickname used when connecting to the IRC server
NICK = "birdie"

# Mapping of nicknames to unique colors for easy differentiation
nick_colors: dict[str, tuple[int, int, int]] = {}

# Colour palette with high contrast on a black background
PALETTE = [
    (255, 96, 96),  # red
    (96, 255, 96),  # green
    (96, 96, 255),  # blue
    (255, 255, 96),  # yellow
    (255, 96, 255),  # magenta
    (96, 255, 255),  # cyan
    (255, 160, 96),  # orange
    (160, 96, 255),  # purple
]


def get_nick_color(nick: str) -> tuple[int, int, int]:
    """Return a readable colour for ``nick``."""
    if nick == NICK:
        # Highlight our own nick in bright cyan
        return (96, 255, 255)
    if nick not in nick_colors:
        nick_colors[nick] = PALETTE[len(nick_colors) % len(PALETTE)]
    return nick_colors[nick]

# Max number of chat lines to display on screen
MAX_VISIBLE = 5

# Pixel height for each chat line.  This will be updated once the chat
# font is created.
LINE_HEIGHT = 16

# Font used for chat rendering.  It is created lazily after pygame has
# been initialised so that it can be bigger/bolder for improved
# readability on the small display.
CHAT_FONT = None


def get_chat_font():
    """Return the font used for chat rendering, creating it if needed."""
    global CHAT_FONT, LINE_HEIGHT
    if CHAT_FONT is None:
        # Slightly larger bold monospace font for readability
        CHAT_FONT = pygame.font.SysFont("monospace", 14, bold=True)
        LINE_HEIGHT = CHAT_FONT.get_height() + 2
    return CHAT_FONT


def wrap_text(text: str, font: pygame.font.Font, width: int) -> list[str]:
    """Wrap ``text`` into a list of lines no wider than ``width`` pixels."""
    words = text.split(" ")
    lines: list[str] = []
    current = ""
    for word in words:
        candidate = word if not current else f"{current} {word}"
        if font.size(candidate)[0] <= width:
            # Entire candidate fits on the current line
            current = candidate
            continue

        if current:
            # Finalise the current line before handling the long word
            lines.append(current)
            current = ""

        # If the word itself is too wide for a single line, split it
        while word and font.size(word)[0] > width:
            # Find the largest prefix that fits within width
            end = len(word)
            while end > 0 and font.size(word[:end])[0] > width:
                end -= 1
            # Safety check to avoid infinite loops if a single
            # character somehow does not fit
            if end == 0:
                break
            lines.append(word[:end])
            word = word[end:]

        current = word

    if current:
        lines.append(current)

    return lines

chat_lines = []
_init = False
_thread = None

logger = logging.getLogger(__name__)


def _irc_thread(server: str, port: int, channel: str, nick: str) -> None:
    """Background worker that receives messages from the IRC server."""

    def send(msg: str) -> None:
        sock.sendall(msg.encode("utf-8"))

    try:
        sock = socket.socket()
        sock.connect((server, port))
        logger.debug(f"Connected to {server}:{port}, joining {channel} as {nick}")
        send(f"NICK {nick}\r\n")
        send(f"USER {nick} 0 * :{nick}\r\n")
        send(f"JOIN {channel}\r\n")

        buffer = ""
        sock.settimeout(0.1)
        while True:
            # Send any queued outgoing messages
            try:
                while True:
                    out = send_queue.get_nowait()
                    send(f"PRIVMSG {channel} :{out}\r\n")
            except queue.Empty:
                pass

            try:
                data = sock.recv(4096).decode("utf-8", "ignore")
                if not data:
                    break
            except socket.timeout:
                data = ""
            buffer += data
            while "\r\n" in buffer:
                line, buffer = buffer.split("\r\n", 1)
                if line.startswith("PING"):
                    send(f"PONG {line.split()[1]}\r\n")
                    continue
                parts = line.split(" ", 3)
                if len(parts) >= 4 and parts[1] == "PRIVMSG":
                    user = parts[0].split("!")[0][1:]
                    msg = parts[3][1:]
                    chat_lines.append({"user": user, "msg": msg})
                    if len(chat_lines) > 100:
                        chat_lines.pop(0)
    except Exception as exc:  # pragma: no cover - runtime errors shown onscreen
        error_msg = f"IRC connection error: {exc}"
        print(error_msg)
        logger.exception(error_msg)
        chat_lines.append({"user": "error", "msg": str(exc)})


def init_chat() -> None:
    """Start the IRC background thread with preset connection details."""

    global _init, _thread
    if _init:
        return

    server = "192.168.0.81"
    port = 6667
    channel = "#pet"
    nick = NICK

    logger.debug(
        f"Starting IRC thread for {server}:{port} {channel} as {nick}"
    )

    _thread = threading.Thread(
        target=_irc_thread, args=(server, port, channel, nick), daemon=True
    )
    _thread.start()
    _init = True


def update_chat(_lines, _now):
    """No-op placeholder for compatibility with the main loop."""


def send_chat_message(message: str) -> None:
    """Queue an outgoing chat message to be sent to the IRC server."""
    if message:
        send_queue.put(message)
        # Immediately display our own message locally so it shows up
        chat_lines.append({"user": NICK, "msg": message})
        if len(chat_lines) > 100:
            chat_lines.pop(0)


def handle_chat_event(event) -> None:
    """Handle key events for composing and sending chat messages."""
    global cursor, scroll, typed_text, shift
    if event.key == pygame.K_LEFT:
        cursor = (cursor - 1) % len(keyboard_chars)
    elif event.key == pygame.K_RIGHT:
        cursor = (cursor + 1) % len(keyboard_chars)
    elif event.key == pygame.K_UP:
        ch = keyboard_chars[cursor]
        if shift:
            ch = ch.upper()
            shift = False
        typed_text += ch
        if len(typed_text) > 200:
            typed_text = typed_text[-200:]
    elif event.key == pygame.K_DOWN:
        typed_text = typed_text[:-1]
    elif event.key == pygame.K_TAB:
        shift = not shift
    elif event.key == pygame.K_RETURN:
        send_chat_message(typed_text)
        typed_text = ""

    if cursor < scroll:
        scroll = cursor
    elif cursor >= scroll + VISIBLE:
        scroll = cursor - VISIBLE + 1
def draw_chat(screen, FONT, chat_lines, chat_scroll):
    """Render the received IRC messages with coloured nicknames."""

    font = get_chat_font()
    screen.fill((0, 0, 0))

    max_width = screen.get_width() - 12

    # Expand stored messages into individual wrapped lines with colour info
    rendered_lines: list[
        tuple[str, str, tuple[int, int, int], tuple[int, int, int], int]
    ] = []
    for chat in chat_lines:
        prefix = f"{chat['user']}> "
        prefix_width = font.size(prefix)[0]
        parts = wrap_text(chat["msg"], font, max_width - prefix_width)
        if not parts:
            parts = [""]
        prefix_color = get_nick_color(chat["user"])
        text_color = (96, 255, 255) if chat["user"] == NICK else (255, 255, 255)
        for idx, part in enumerate(parts):
            if idx == 0:
                rendered_lines.append(
                    (prefix, part, prefix_color, text_color, 6)
                )
            else:
                # Start wrapped lines underneath the nickname rather than
                # aligning with the text from the previous line
                rendered_lines.append(
                    ("", part, prefix_color, text_color, 6)
                )

    start = max(0, len(rendered_lines) - MAX_VISIBLE - chat_scroll)
    end = max(0, len(rendered_lines) - chat_scroll)
    visible = rendered_lines[start:end]

    for i, (pref, text, pref_c, txt_c, x) in enumerate(visible):
        y = 15 + i * LINE_HEIGHT
        if pref:
            pref_surf = font.render(pref, True, pref_c)
            screen.blit(pref_surf, (x, y))
            msg_surf = font.render(text, True, txt_c)
            screen.blit(msg_surf, (x + font.size(pref)[0], y))
        else:
            msg_surf = font.render(text, True, txt_c)
            screen.blit(msg_surf, (x, y))

    # Draw the current input line at the bottom
    input_display = typed_text[-16:]
    msg = font.render(f"> {input_display}", True, (255, 255, 255))
    screen.blit(msg, (6, 108))

    # Display on-screen keyboard similar to the typing mini-game
    start_k = scroll
    end_k = scroll + VISIBLE
    for i, ch in enumerate(keyboard_chars[start_k:end_k]):
        idx = start_k + i
        color = (255, 255, 0) if idx == cursor else (230, 230, 230)
        disp_ch = ch.upper() if shift else ch
        text = font.render(disp_ch, True, color)
        x = 6 + i * 12
        screen.blit(text, (x, 88))

    tip = font.render(
        "ARROWS Type TAB=Shift RET=Send ESC=Back PGUP/DN=Scroll",
        True,
        (255, 255, 255),
    )
    screen.blit(tip, (2, 2))
