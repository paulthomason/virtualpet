def draw_inventory(screen, FONT):
    screen.fill((50, 120, 80))
    msg = FONT.render("Inventory (placeholder)", True, (255,255,255))
    screen.blit(msg, (6, 54))
    tip = FONT.render("Press joystick to return", True, (200,255,200))
    screen.blit(tip, (6, 114))
