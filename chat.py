"""Simple IRC chat viewer for the virtual pet demo."""

import socket
import threading

MAX_VISIBLE = 6
chat_lines = []
_init = False
_thread = None


def _irc_thread(server: str, port: int, channel: str, nick: str) -> None:
    """Background worker that receives messages from the IRC server."""

    def send(msg: str) -> None:
        sock.sendall(msg.encode("utf-8"))

    try:
        sock = socket.socket()
        sock.connect((server, port))
        send(f"NICK {nick}\r\n")
        send(f"USER {nick} 0 * :{nick}\r\n")
        send(f"JOIN {channel}\r\n")

        buffer = ""
        while True:
            data = sock.recv(4096).decode("utf-8", "ignore")
            if not data:
                break
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
        chat_lines.append({"user": "error", "msg": str(exc)})


def init_chat() -> None:
    """Prompt the user for IRC details and start the background thread."""

    global _init, _thread
    if _init:
        return

    server = input("IRC server: ") or "irc.libera.chat"
    port = input("Port (default 6667): ")
    channel = input("Channel (include #): ")
    nick = input("Nickname: ") or "virtualpet"

    port = int(port) if port else 6667
    _thread = threading.Thread(
        target=_irc_thread, args=(server, port, channel, nick), daemon=True
    )
    _thread.start()
    _init = True


def update_chat(_lines, _now):
    """No-op placeholder for compatibility with the main loop."""

def draw_chat(screen, FONT, chat_lines, chat_scroll):
    """Render the received IRC messages."""

    screen.fill((0, 0, 0))
    start = max(0, len(chat_lines) - MAX_VISIBLE - chat_scroll)
    end = max(0, len(chat_lines) - chat_scroll)
    visible = chat_lines[start:end]
    for i, chat in enumerate(visible):
        y = 15 + i * 18
        msg = FONT.render(f"{chat['user']}> {chat['msg']}", True, (255, 255, 255))
        screen.blit(msg, (6, y))
