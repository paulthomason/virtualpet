import pygame
import os

def draw_dog_park(screen, FONT):
    # Use dog_park.png or a placeholder
    DOG_PARK_IMAGE_PATH = "dog_park.png"
    if os.path.exists(DOG_PARK_IMAGE_PATH):
        img = pygame.image.load(DOG_PARK_IMAGE_PATH).convert()
        screen.blit(img, (0, 0))
    else:
        screen.fill((120, 180, 255))
        msg = FONT.render("Dog Park", True, (80,80,80))
        screen.blit(msg, (28, 56))
    tip = FONT.render("Press joystick to return", True, (180,180,255))
    pygame.draw.rect(screen, (24,28,38), (0, 112, 128, 16))
    screen.blit(tip, (6, 114))
