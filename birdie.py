def draw_birdie(screen, FONT):
    screen.fill((200, 220, 255))
    msg = FONT.render("Birdie (placeholder)", True, (30, 70, 140))
    screen.blit(msg, (12, 54))
    tip = FONT.render("Press joystick to return", True, (80,80,160))
    screen.blit(tip, (6, 114))
