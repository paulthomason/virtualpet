import random
import time

chat_templates = [
    {"user": "syl", "msg": "hey what's up"},
    {"user": "george", "msg": "yo"},
    {"user": "syl", "msg": "not much"},
    {"user": "george", "msg": "want to play fetch?"},
    {"user": "syl", "msg": "maybe later"},
    {"user": "george", "msg": "k see u"},
    {"user": "syl", "msg": "see ya!"},
    {"user": "george", "msg": "did you eat?"},
    {"user": "syl", "msg": "i found a stick"},
    {"user": "george", "msg": "same park tomorrow?"},
]
MSG_INTERVAL = 15
MAX_VISIBLE = 6

def update_chat(chat_lines, now, _last=[0]):
    # _last stores last update time between calls
    if now - _last[0] > MSG_INTERVAL:
        while True:
            new_msg = random.choice(chat_templates)
            if not (chat_lines and chat_lines[-1]["user"] == new_msg["user"] and chat_lines[-1]["msg"] == new_msg["msg"]):
                break
        chat_lines.append(new_msg)
        _last[0] = now

def draw_chat(screen, FONT, chat_lines, chat_scroll):
    screen.fill((0,0,0))
    title = FONT.render("Chat", True, (255,255,255))
    screen.blit(title, (4, 1))
    start = max(0, len(chat_lines) - MAX_VISIBLE - chat_scroll)
    end = max(0, len(chat_lines) - chat_scroll)
    visible = chat_lines[start:end]
    for i, chat in enumerate(visible):
        y = 15 + i * 18
        msg = FONT.render(f"{chat['user']}> {chat['msg']}", True, (255,255,255))
        screen.blit(msg, (6, y))
    tip = FONT.render("UP/DOWN=Scroll  Enter=Back", True, (255,255,255))
    screen.blit(tip, (4, 114))
