def draw_settings(screen, FONT):
    screen.fill((80, 80, 120))
    msg = FONT.render("Settings (placeholder)", True, (255,255,255))
    screen.blit(msg, (8, 54))
    tip = FONT.render("Press joystick to return", True, (200,220,255))
    screen.blit(tip, (6, 114))
