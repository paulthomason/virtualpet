# New York Times Top Stories viewer for the virtual pet

import os
import requests
import pygame
import webbrowser

# Placeholder for your NYT API key
# Attempt to load the API key from the environment but fall back to a
# placeholder value that users should replace with their own key.
NYT_API_KEY = os.getenv("NYT_API_KEY", "YOUR_NYT_API_KEY_HERE")

# Visible lines for listing stories
MAX_VISIBLE = 6

# Fetched list of stories
stories = []

# Current selection and scroll position in the list
selected = 0
scroll = 0

# Mode is either 'list' or 'story'
mode = "list"

# Scroll offset when viewing a story
story_scroll = 0


def wrap_text(text: str, font, width: int) -> list[str]:
    """Wrap text to fit within a given pixel width."""
    words = text.split(" ")
    lines: list[str] = []
    current = ""
    for word in words:
        candidate = word if not current else f"{current} {word}"
        if font.getsize(candidate)[0] <= width:
            current = candidate
            continue
        if current:
            lines.append(current)
            current = ""
        while word and font.getsize(word)[0] > width:
            end = len(word)
            while end > 0 and font.getsize(word[:end])[0] > width:
                end -= 1
            if end == 0:
                break
            lines.append(word[:end])
            word = word[end:]
        current = word
    if current:
        lines.append(current)
    return lines


def init_news() -> None:
    """Fetch the top stories from the NYT API."""
    global stories, selected, scroll
    url = (
        "https://api.nytimes.com/svc/topstories/v2/home.json"
        f"?api-key={NYT_API_KEY}"
    )
    try:
        if NYT_API_KEY == "YOUR_NYT_API_KEY_HERE":
            raise ValueError("Set NYT_API_KEY in the environment or news.py")
        resp = requests.get(url, timeout=5)
        data = resp.json()
        stories = [
            {
                "title": item.get("title", ""),
                "abstract": item.get("abstract", ""),
                "url": item.get("url", ""),
            }
            for item in data.get("results", [])
        ]
    except Exception as exc:  # pragma: no cover - network issues shown onscreen
        stories = [{"title": f"Error: {exc}", "abstract": "", "url": ""}]
    selected = 0
    scroll = 0


def handle_news_event(event) -> bool:
    """Handle key events for the news screen.

    Returns ``True`` when the caller should exit to the main menu.
    """
    global selected, scroll, mode, story_scroll
    if mode == "list":
        if event.key == pygame.K_UP:
            if stories:
                selected = (selected - 1) % len(stories)
        elif event.key == pygame.K_DOWN:
            if stories:
                selected = (selected + 1) % len(stories)
        elif event.key == pygame.K_SPACE:  # button 1
            if stories:
                mode = "story"
                story_scroll = 0
        elif event.key == pygame.K_TAB:  # button 3
            return True
        if stories:
            if selected < scroll:
                scroll = selected
            elif selected >= scroll + MAX_VISIBLE:
                scroll = selected - MAX_VISIBLE + 1
    else:  # viewing a story
        if event.key == pygame.K_UP:
            if story_scroll > 0:
                story_scroll -= 1
        elif event.key == pygame.K_DOWN:
            story_scroll += 1
        elif event.key == pygame.K_SPACE:
            story = stories[selected]
            url = story.get("url")
            if url:
                webbrowser.open(url)
        elif event.key == pygame.K_TAB:  # back to list
            mode = "list"
    return False


def draw_news(draw, font, width: int, height: int) -> None:
    """Render the news screen using ``draw`` from Pillow."""
    global story_scroll
    draw.rectangle((0, 0, width, height), outline="black", fill="black")
    if mode == "list":
        draw.text((2, 2), "Top Stories", font=font, fill="white")
        visible = stories[scroll:scroll + MAX_VISIBLE]
        for idx, story in enumerate(visible):
            i = scroll + idx
            color = "yellow" if i == selected else "white"
            title = story.get("title", "")
            parts = wrap_text(title, font, width - 4)
            line = parts[0] if parts else ""
            draw.text((2, 18 + idx * 16), line, font=font, fill=color)
        draw.text((2, height - 14), "SPACE=Open TAB=Back", font=font, fill="cyan")
    else:
        story = stories[selected]
        text = f"{story.get('title', '')}\n\n{story.get('abstract', '')}"
        lines = wrap_text(text, font, width - 4)
        visible_lines = height // 16 - 1
        if story_scroll > len(lines) - visible_lines:
            story_scroll = max(0, len(lines) - visible_lines)
        start = story_scroll
        end = start + visible_lines
        y = 2
        for line in lines[start:end]:
            draw.text((2, y), line, font=font, fill="white")
            y += 16
        draw.text((2, height - 14), "SPACE=Browser TAB=Back", font=font, fill="cyan")

