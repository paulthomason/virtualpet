import pygame
import random

# Options for the initial battle menu
BATTLE_OPTIONS = ["Practice", "GameLink"]
selected_option = 0

# Battle state variables for practice battles
PLAYER_MAX_HP = 50
ENEMY_MIN_HP = 30
ENEMY_MAX_HP = 60
player_hp = PLAYER_MAX_HP
enemy_hp = ENEMY_MAX_HP
message = ""
battle_over = False


def handle_battle_menu_event(event):
    """Handle up/down/select events in the battle menu."""
    global selected_option
    if event.key == pygame.K_UP:
        selected_option = (selected_option - 1) % len(BATTLE_OPTIONS)
    elif event.key == pygame.K_DOWN:
        selected_option = (selected_option + 1) % len(BATTLE_OPTIONS)
    elif event.key in (pygame.K_RETURN, pygame.K_SPACE):
        return BATTLE_OPTIONS[selected_option]
    return None


def draw_battle_menu(screen, FONT):
    """Draw the battle selection menu."""
    screen.fill((40, 60, 90))
    title = FONT.render("Battle", True, (255, 255, 255))
    screen.blit(title, (6, 4))
    for i, option in enumerate(BATTLE_OPTIONS):
        color = (200, 255, 200) if i == selected_option else (255, 255, 255)
        msg = FONT.render(option, True, color)
        screen.blit(msg, (6, 24 + i * 16))
    tip = FONT.render("Enter=Select Esc=Back", True, (200, 220, 255))
    screen.blit(tip, (6, 114))


def start_practice_battle():
    """Initialise practice battle state."""
    global player_hp, enemy_hp, message, battle_over
    player_hp = PLAYER_MAX_HP
    enemy_hp = random.randint(ENEMY_MIN_HP, ENEMY_MAX_HP)
    message = "A wild pet appeared!"
    battle_over = False


def handle_practice_event(event):
    """Handle key input during a practice battle.

    Returns True when the battle should exit back to the battle menu.
    """
    global player_hp, enemy_hp, message, battle_over
    if battle_over:
        if event.key in (pygame.K_RETURN, pygame.K_SPACE, pygame.K_ESCAPE):
            return True
        return False
    if event.key == pygame.K_ESCAPE:
        return True
    if event.key in (pygame.K_RETURN, pygame.K_SPACE):
        damage = random.randint(5, 12)
        enemy_hp -= damage
        message = f"You hit! {damage} dmg"
        if enemy_hp <= 0:
            battle_over = True
            message = "You won!"
            return False
        enemy_damage = random.randint(5, 12)
        player_hp -= enemy_damage
        message += f" Enemy hits {enemy_damage}"
        if player_hp <= 0:
            battle_over = True
            message += " - You lost!"
    return False


def draw_practice_battle(screen, FONT):
    """Render the practice battle to ``screen`` using ``FONT``."""
    screen.fill((0, 0, 0))
    ph = FONT.render(f"Your HP: {player_hp}", True, (255, 255, 255))
    eh = FONT.render(f"Enemy HP: {enemy_hp}", True, (255, 255, 255))
    screen.blit(ph, (6, 20))
    screen.blit(eh, (6, 36))
    msg = FONT.render(message, True, (255, 255, 0))
    screen.blit(msg, (6, 60))
    if battle_over:
        tip = FONT.render("Enter=Back", True, (200, 220, 255))
    else:
        tip = FONT.render("Enter=Attack Esc=Run", True, (200, 220, 255))
    screen.blit(tip, (6, 114))


def handle_gamelink_event(event):
    """Handle input for the GameLink placeholder screen."""
    if event.key in (pygame.K_RETURN, pygame.K_SPACE, pygame.K_ESCAPE):
        return True
    return False


def draw_gamelink(screen, FONT):
    """Draw placeholder GameLink screen."""
    screen.fill((20, 30, 50))
    msg1 = FONT.render("GameLink (Bluetooth)", True, (255, 255, 255))
    msg2 = FONT.render("Not implemented", True, (255, 255, 255))
    screen.blit(msg1, (6, 50))
    screen.blit(msg2, (6, 66))
    tip = FONT.render("Enter=Back", True, (200, 220, 255))
    screen.blit(tip, (6, 114))
