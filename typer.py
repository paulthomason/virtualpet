import pygame

keyboard_chars = list("abcdefghijklmnopqrstuvwxyz0123456789.,!? ")
VISIBLE = 10
cursor = 0
scroll = 0
typed_text = ""
shift = False


def handle_type_event(event):
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
        if len(typed_text) > 60:
            typed_text = typed_text[-60:]
    elif event.key == pygame.K_DOWN:
        typed_text = typed_text[:-1]
    elif event.key in (pygame.K_RETURN, pygame.K_SPACE):
        shift = not shift

    if cursor < scroll:
        scroll = cursor
    elif cursor >= scroll + VISIBLE:
        scroll = cursor - VISIBLE + 1


def draw_type(screen, FONT):
    screen.fill((30, 30, 30))
    display = typed_text[-16:]
    msg = FONT.render(display, True, (255, 255, 255))
    screen.blit(msg, (4, 40))

    start = scroll
    end = scroll + VISIBLE
    for i, ch in enumerate(keyboard_chars[start:end]):
        idx = start + i
        color = (255, 255, 0) if idx == cursor else (200, 200, 200)
        disp_ch = ch.upper() if shift else ch
        text = FONT.render(disp_ch, True, color)
        x = 6 + i * 12
        screen.blit(text, (x, 92))

    tip = FONT.render("LR Move U=Sel D=Del ENT=Shift ESC=Back", True, (200, 200, 200))
    screen.blit(tip, (2, 114))
