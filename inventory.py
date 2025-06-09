"""Simple interactive inventory for the virtual pet."""

import pygame


# Items that a cat might have
inventory_items = [
    "Ball of Yarn",
    "Catnip",
    "Canned Tuna",
    "Feather Toy",
    "Laser Pointer",
]

# Index of the currently selected item
selected_index = 0

# Currently selected action when viewing the action menu
action_index = 0
ACTION_OPTIONS = ["Select", "Discard", "Inspect"]

# Which sub-mode the inventory screen is in
#  - "browse"   : user is scrolling through items
#  - "actions"  : user is choosing Select/Discard/Inspect
#  - "inspect"  : show placeholder image
mode = "browse"

# Last item "selected" (no effect beyond displaying a message)
current_item: str | None = None


def handle_inventory_event(event) -> bool:
    """Handle key input on the inventory screen.

    Returns ``True`` if the caller should exit the inventory screen.
    """
    global selected_index, action_index, mode, current_item, inventory_items

    if mode == "inspect":
        if event.key in (pygame.K_RETURN, pygame.K_SPACE, pygame.K_ESCAPE):
            mode = "actions"
        return False

    if mode == "actions":
        if event.key == pygame.K_UP:
            action_index = (action_index - 1) % len(ACTION_OPTIONS)
        elif event.key == pygame.K_DOWN:
            action_index = (action_index + 1) % len(ACTION_OPTIONS)
        elif event.key in (pygame.K_ESCAPE, pygame.K_BACKSPACE):
            mode = "browse"
        elif event.key in (pygame.K_RETURN, pygame.K_SPACE):
            if not inventory_items:
                mode = "browse"
            else:
                item = inventory_items[selected_index]
                action = ACTION_OPTIONS[action_index]
                if action == "Discard":
                    del inventory_items[selected_index]
                    if selected_index >= len(inventory_items):
                        selected_index = max(0, len(inventory_items) - 1)
                    mode = "browse"
                elif action == "Inspect":
                    mode = "inspect"
                else:  # Select
                    current_item = item
                    mode = "browse"
        return False

    # browse mode
    if event.key == pygame.K_UP:
        if inventory_items:
            selected_index = (selected_index - 1) % len(inventory_items)
    elif event.key == pygame.K_DOWN:
        if inventory_items:
            selected_index = (selected_index + 1) % len(inventory_items)
    elif event.key in (pygame.K_RETURN, pygame.K_SPACE):
        if inventory_items:
            mode = "actions"
            action_index = 0
    elif event.key == pygame.K_ESCAPE:
        return True
    return False


def draw_inventory(screen, FONT):
    """Render the inventory screen based on the current ``mode``."""
    screen.fill((50, 120, 80))

    title = FONT.render("Inventory", True, (255, 255, 255))
    screen.blit(title, (6, 4))

    if mode == "browse":
        if not inventory_items:
            empty = FONT.render("(empty)", True, (255, 255, 255))
            screen.blit(empty, (6, 40))
        else:
            for i, item in enumerate(inventory_items):
                color = (255, 255, 0) if i == selected_index else (255, 255, 255)
                msg = FONT.render(item, True, color)
                screen.blit(msg, (6, 24 + i * 16))
        tip = FONT.render("Enter=Actions Esc=Back", True, (200, 255, 200))
        screen.blit(tip, (6, 114))
        if current_item:
            sel = FONT.render(f"Selected: {current_item}", True, (255, 255, 255))
            screen.blit(sel, (6, 100))

    elif mode == "actions":
        if inventory_items:
            item = inventory_items[selected_index]
        else:
            item = ""
        item_msg = FONT.render(item, True, (255, 255, 255))
        screen.blit(item_msg, (6, 24))
        for i, action in enumerate(ACTION_OPTIONS):
            color = (255, 255, 0) if i == action_index else (255, 255, 255)
            msg = FONT.render(action, True, color)
            screen.blit(msg, (6, 44 + i * 16))
        tip = FONT.render("Enter=Choose Esc=Back", True, (200, 255, 200))
        screen.blit(tip, (6, 114))

    elif mode == "inspect":
        item = inventory_items[selected_index] if inventory_items else ""
        placeholder = pygame.Rect(32, 32, 64, 64)
        pygame.draw.rect(screen, (80, 80, 80), placeholder)
        label = FONT.render(item, True, (255, 255, 255))
        screen.blit(label, (6, 24))
        msg = FONT.render("[image coming soon]", True, (255, 255, 0))
        screen.blit(msg, (14, 60))
        tip = FONT.render("Press key to return", True, (200, 255, 200))
        screen.blit(tip, (6, 114))
