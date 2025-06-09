import pygame
import random
import logging
from dataclasses import dataclass, field
from typing import Optional

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

# Logger used to track sound playback issues
logger = logging.getLogger("sound")
if not logger.handlers:
    handler = logging.FileHandler("soundlog.txt", mode="a")
    handler.setFormatter(
        logging.Formatter("%(asctime)s %(levelname)s: %(message)s")
    )
    logger.addHandler(handler)
logger.setLevel(logging.DEBUG)

# Move names for practice mode
ATTACKS = ["Scratch", "Bite", "Kick", "Headbutt"]
selected_attack = 0


@dataclass
class Move:
    """Simple move representation."""
    name: str
    power: int
    accuracy: int
    max_pp: int
    pp: int = field(init=False)

    def __post_init__(self) -> None:
        self.pp = self.max_pp


@dataclass
class Pokemon:
    """Basic Pokemon stats for the wild battle."""

    name: str
    level: int
    max_hp: int
    attack: int
    defense: int
    speed: int
    moves: list
    sprite: pygame.Surface
    hp: int = field(init=False)

    def __post_init__(self) -> None:
        self.hp = self.max_hp


def _play_sound(path: str) -> None:
    """Play a sound file if available."""
    try:
        pygame.mixer.Sound(path).play()
        logger.debug(f"Played sound: {path}")
    except Exception as exc:
        logger.exception(f"Failed to play {path}: {exc}")


# Constants for wild battle UI
TEXT_SPEED = 33  # ~30 chars/sec
BOTTOM_BOX_Y = 80


class HPBar:
    """Simple animated HP bar."""

    def __init__(self, pos: tuple[int, int]):
        self.pos = pos
        self.width = 48
        self.height = 5

    def draw(self, screen: pygame.Surface, hp: int, max_hp: int) -> None:
        x, y = self.pos
        pygame.draw.rect(screen, (0, 0, 0), (x, y, self.width, self.height), 1)
        ratio = max(0, hp) / max_hp
        fill = int((self.width - 2) * ratio)
        color = (0, 200, 0)
        if ratio <= 0.5:
            color = (220, 220, 0)
        if ratio <= 0.2:
            color = (220, 0, 0)
        pygame.draw.rect(screen, color, (x + 1, y + 1, fill, self.height - 2))
        if fill < self.width - 2:
            pygame.draw.rect(
                screen,
                (60, 60, 60),
                (x + 1 + fill, y + 1, self.width - 2 - fill, self.height - 2),
            )

    def animate(self, screen: pygame.Surface, start: int, end: int, max_hp: int) -> None:
        hp = start
        step = -1 if end < start else 1
        while hp != end:
            hp += step
            self.draw(screen, hp, max_hp)
            pygame.display.flip()
            pygame.time.delay(10)


class Menu:
    """Grid-based menu with keyboard navigation."""

    def __init__(self, options: list[str], cols: int = 2):
        self.options = options
        self.cols = cols
        self.selected = 0

    def handle(self, event: pygame.event.Event) -> Optional[int]:
        if event.type != pygame.KEYDOWN:
            return None
        if event.key == pygame.K_LEFT:
            self.selected = (self.selected - 1) % len(self.options)
        elif event.key == pygame.K_RIGHT:
            self.selected = (self.selected + 1) % len(self.options)
        elif event.key == pygame.K_UP:
            self.selected = (self.selected - self.cols) % len(self.options)
        elif event.key == pygame.K_DOWN:
            self.selected = (self.selected + self.cols) % len(self.options)
        elif event.key in (pygame.K_RETURN, pygame.K_SPACE):
            return self.selected
        elif event.key == pygame.K_ESCAPE:
            return -1
        return None

    def draw(self, screen: pygame.Surface, font: pygame.font.Font, rect: pygame.Rect) -> None:
        rows = (len(self.options) + self.cols - 1) // self.cols
        option_w = rect.width // self.cols
        option_h = rect.height // rows
        for i, option in enumerate(self.options):
            col = i % self.cols
            row = i // self.cols
            x = rect.x + col * option_w + 4
            y = rect.y + row * option_h + 4
            color = (255, 255, 255)
            if i == self.selected:
                color = (50, 150, 255)
            text = font.render(option, True, color)
            screen.blit(text, (x, y))


class TextBox:
    """Renders text gradually with pauses and a more prompt."""

    def __init__(self, rect: pygame.Rect, font: pygame.font.Font):
        self.rect = rect
        self.font = font

    def display(self, screen: pygame.Surface, text: str) -> None:
        shown = ""
        idx = 0
        last = pygame.time.get_ticks()
        while idx < len(text):
            now = pygame.time.get_ticks()
            if now - last >= TEXT_SPEED:
                shown += text[idx]
                idx += 1
                last = now
                self._draw(screen, shown)
                pygame.display.flip()
                ch = shown[-1]
                if ch == ",":
                    pygame.time.delay(150)
                elif ch in ".!":
                    pygame.time.delay(350)
            for event in pygame.event.get():
                if event.type == pygame.KEYDOWN and event.key == pygame.K_RETURN:
                    shown = text
                    idx = len(text)
                    self._draw(screen, shown)
                    pygame.display.flip()
        self._wait_more(screen, shown)

    def _draw(self, screen: pygame.Surface, text: str) -> None:
        pygame.draw.rect(screen, (40, 40, 40), self.rect)
        pygame.draw.rect(screen, (0, 0, 0), self.rect, 1)
        lines = []
        while text:
            lines.append(text[:18])
            text = text[18:]
        for i, line in enumerate(lines[:3]):
            img = self.font.render(line, True, (255, 255, 255))
            screen.blit(img, (self.rect.x + 4, self.rect.y + 4 + i * 12))

    def _wait_more(self, screen: pygame.Surface, shown: str) -> None:
        arrow = self.font.render("v", True, (255, 255, 255))
        blink = 0
        while True:
            self._draw(screen, shown)
            if blink // 20 % 2 == 0:
                screen.blit(arrow, (self.rect.right - 10, self.rect.bottom - 12))
            pygame.display.flip()
            blink += 1
            for event in pygame.event.get():
                if event.type == pygame.KEYDOWN:
                    return
            pygame.time.delay(50)


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
    global player_hp, enemy_hp, message, battle_over, selected_attack
    player_hp = PLAYER_MAX_HP
    enemy_hp = random.randint(ENEMY_MIN_HP, ENEMY_MAX_HP)
    message = "A wild pet appeared!"
    battle_over = False
    selected_attack = 0


def handle_practice_event(event):
    """Handle key input during a practice battle.

    Returns True when the battle should exit back to the battle menu.
    """
    global player_hp, enemy_hp, message, battle_over, selected_attack
    if battle_over:
        if event.key in (pygame.K_RETURN, pygame.K_SPACE, pygame.K_ESCAPE):
            return True
        return False
    if event.key == pygame.K_ESCAPE:
        return True
    if event.key == pygame.K_UP:
        selected_attack = (selected_attack - 1) % len(ATTACKS)
    elif event.key == pygame.K_DOWN:
        selected_attack = (selected_attack + 1) % len(ATTACKS)
    elif event.key in (pygame.K_RETURN, pygame.K_SPACE):
        dmg = random.randint(5, 12)
        enemy_hp -= dmg
        move = ATTACKS[selected_attack]
        message = f"You used {move}! {dmg} dmg"
        if enemy_hp <= 0:
            battle_over = True
            message = "You won!"
            return False
        enemy_dmg = random.randint(5, 12)
        player_hp -= enemy_dmg
        message += f" Enemy hits {enemy_dmg}"
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
        screen.blit(tip, (6, 114))
        return

    # Draw attack options
    for i, atk in enumerate(ATTACKS):
        color = (200, 255, 200) if i == selected_attack else (255, 255, 255)
        option = FONT.render(atk, True, color)
        screen.blit(option, (6, 80 + i * 12))

    tip = FONT.render("Up/Down=Select Enter=Attack Esc=Run", True,
                      (200, 220, 255))
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


def start_wild_battle(
    screen: pygame.Surface,
    font: pygame.font.Font,
    player: Pokemon,
    wild: Pokemon,
) -> None:
    """Runs a simple Game Boy style wild battle."""

    clock = pygame.time.Clock()
    text_box = TextBox(pygame.Rect(0, BOTTOM_BOX_Y, 128, 48), font)
    menu = Menu(["Fight", "Bag", "Pok\u00e9mon", "Run"], 2)
    fight_menu = Menu([m.name for m in player.moves], 1)

    # create background tile
    tile = pygame.Surface((8, 8))
    tile.fill((96, 160, 96))
    pygame.draw.rect(tile, (80, 144, 80), (0, 4, 8, 4))

    def draw_base() -> None:
        for y in range(0, BOTTOM_BOX_Y, 8):
            for x in range(0, 128, 8):
                screen.blit(tile, (x, y))
        pygame.draw.rect(screen, (60, 60, 60), (0, BOTTOM_BOX_Y, 128, 48))
        pygame.draw.rect(screen, (0, 0, 0), (0, BOTTOM_BOX_Y, 128, 48), 1)

    enemy_hp = HPBar((4, 4))
    player_hp = HPBar((76, 44))

    enemy_pos = [-32, 20]
    player_pos = [128, 56]

    _play_sound("sfx/encounter.wav")
    start = pygame.time.get_ticks()
    while pygame.time.get_ticks() - start < 400:
        draw_base()
        enemy_pos[0] = -32 + (32 * (pygame.time.get_ticks() - start) // 400)
        screen.blit(wild.sprite, enemy_pos)
        pygame.display.flip()
        clock.tick(60)

    start = pygame.time.get_ticks()
    while pygame.time.get_ticks() - start < 300:
        draw_base()
        screen.blit(wild.sprite, (0, 20))
        player_pos[0] = 128 - 32 * (pygame.time.get_ticks() - start) // 300 - 32
        screen.blit(player.sprite, player_pos)
        pygame.display.flip()
        clock.tick(60)

    draw_base()
    screen.blit(wild.sprite, (0, 20))
    screen.blit(player.sprite, (96, 56))
    enemy_hp.draw(screen, wild.hp, wild.max_hp)
    player_hp.draw(screen, player.hp, player.max_hp)
    pygame.display.flip()
    text_box.display(screen, f"Wild {wild.name} appeared!")

    running = True
    state = "menu"
    while running:
        draw_base()
        screen.blit(wild.sprite, (0, 20))
        screen.blit(player.sprite, (96, 56))
        enemy_hp.draw(screen, wild.hp, wild.max_hp)
        player_hp.draw(screen, player.hp, player.max_hp)

        if state == "menu":
            menu.draw(screen, font, pygame.Rect(4, BOTTOM_BOX_Y + 4, 120, 40))
        elif state == "fight":
            fight_menu.draw(screen, font, pygame.Rect(4, BOTTOM_BOX_Y + 4, 120, 40))

        pygame.display.flip()

        for event in pygame.event.get():
            if event.type == pygame.KEYDOWN:
                if state == "menu":
                    res = menu.handle(event)
                    if res is not None:
                        if res == -1:
                            running = False
                            break
                        choice = menu.options[res]
                        if choice == "Fight":
                            state = "fight"
                        elif choice == "Run":
                            text_box.display(screen, "Got away safely!")
                            running = False
                        else:
                            text_box.display(screen, f"{choice} not implemented")
                        menu.selected = 0
                elif state == "fight":
                    res = fight_menu.handle(event)
                    if res is not None:
                        if res == -1:
                            state = "menu"
                        else:
                            move = player.moves[res]
                            text_box.display(screen, f"{player.name} used {move.name}!")
                            _play_sound("sfx/move.wav")
                            if move.pp > 0:
                                move.pp -= 1
                                if random.randint(1, 100) <= move.accuracy:
                                    dmg = max(
                                        1,
                                        ((2 * player.level / 5 + 2)
                                         * move.power
                                         * player.attack
                                         / wild.defense)
                                        // 50
                                        + random.randint(-2, 2),
                                    )
                                    new_hp = max(0, wild.hp - int(dmg))
                                    enemy_hp.animate(screen, wild.hp, new_hp, wild.max_hp)
                                    wild.hp = new_hp
                                    _play_sound("sfx/hit.wav")
                                    if wild.hp == 0:
                                        for i in range(4):
                                            draw_base()
                                            if i % 2 == 0:
                                                screen.blit(player.sprite, (96, 56))
                                            enemy_hp.draw(screen, wild.hp, wild.max_hp)
                                            player_hp.draw(screen, player.hp, player.max_hp)
                                            pygame.display.flip()
                                            pygame.time.delay(150)
                                        text_box.display(screen, f"{wild.name} fainted!")
                                        _play_sound("sfx/faint.wav")
                                        running = False
                                else:
                                    text_box.display(screen, "It missed!")
                            else:
                                text_box.display(screen, "No PP left!")
                            state = "menu"
                            fight_menu.selected = 0
                            menu.selected = 0
                else:
                    if event.key == pygame.K_ESCAPE:
                        running = False
        clock.tick(60)


# Example integration in a main loop:
#   player = Pokemon("Pikachu", 12, 35, 15, 10, 14,
#                    [Move("Tackle", 35, 95, 35)], pygame.Surface((32, 32)))
#   player.sprite.fill((200, 200, 200))
#   wild = Pokemon("Birdie", 8, 30, 12, 8, 10,
#                  [Move("Peck", 30, 95, 35)], pygame.Surface((32, 32)))
#   wild.sprite.fill((180, 180, 180))
#   start_wild_battle(screen, FONT, player, wild)
