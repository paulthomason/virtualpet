import http.server
import threading
import urllib.parse
import html
import settings
import chat
import inventory

_server_thread = None

class RemoteHandler(http.server.BaseHTTPRequestHandler):
    def do_GET(self):
        parsed = urllib.parse.urlparse(self.path)
        if parsed.path == "/":
            self.send_response(200)
            self.send_header("Content-Type", "text/html")
            self.end_headers()
            difficulty = next((o["value"] for o in settings.settings_options if o["name"] == "Difficulty"), "?")
            wifi = next((o["value"] for o in settings.settings_options if o["name"] == "WiFi"), False)
            wifi_status = "on" if wifi else "off"
            chat_html = "".join(
                f"<p><b>{html.escape(c['user'])}</b>: {html.escape(c['msg'])}</p>"
                for c in chat.chat_lines[-10:]
            )
            inv_html = "".join(
                f"<li>{html.escape(item)} <a href='/remove_item?idx={i}'>remove</a></li>"
                for i, item in enumerate(inventory.inventory_items)
            )
            html_doc = f"""<html><body><h1>Remote Control</h1>
<p>Difficulty: {difficulty}</p>
<p>WiFi: {wifi_status}</p>
<p>Set difficulty:
<a href='/set?option=Difficulty&value=Easy'>Easy</a> |
<a href='/set?option=Difficulty&value=Normal'>Normal</a> |
<a href='/set?option=Difficulty&value=Hard'>Hard</a></p>
<p>Toggle WiFi:
<a href='/set?option=WiFi&value=true'>On</a> |
<a href='/set?option=WiFi&value=false'>Off</a></p>
<h2>Inventory</h2>
<ul>{inv_html}</ul>
<form action='/add_item' method='get'>
<input type='text' name='item' />
<input type='submit' value='Add' />
</form>
<h2>Chat</h2>
{chat_html}
<form action='/send' method='get'>
<input type='text' name='msg' />
<input type='submit' value='Send' />
</form>
</body></html>"""
            self.wfile.write(html_doc.encode("utf-8"))
        elif parsed.path == "/set":
            params = urllib.parse.parse_qs(parsed.query)
            option = params.get("option", [None])[0]
            value = params.get("value", [None])[0]
            if option and value is not None:
                for opt in settings.settings_options:
                    if opt["name"] == option:
                        if opt["type"] == "bool":
                            opt["value"] = value.lower() == "true"
                            if opt["name"] == "WiFi":
                                settings.set_wifi_enabled(opt["value"])
                        elif isinstance(opt["type"], list) and value in opt["type"]:
                            opt["value"] = value
                self.send_response(303)
                self.send_header("Location", "/")
                self.end_headers()
            else:
                self.send_error(400, "Invalid option")
        elif parsed.path == "/send":
            params = urllib.parse.parse_qs(parsed.query)
            msg = params.get("msg", [""])[0]
            if msg:
                chat.send_chat_message(msg)
            self.send_response(303)
            self.send_header("Location", "/")
            self.end_headers()
        elif parsed.path == "/add_item":
            params = urllib.parse.parse_qs(parsed.query)
            item = params.get("item", [""])[0]
            if item:
                inventory.inventory_items.append(item)
            self.send_response(303)
            self.send_header("Location", "/")
            self.end_headers()
        elif parsed.path == "/remove_item":
            params = urllib.parse.parse_qs(parsed.query)
            try:
                idx = int(params.get("idx", ["-1"])[0])
            except ValueError:
                idx = -1
            if 0 <= idx < len(inventory.inventory_items):
                del inventory.inventory_items[idx]
            self.send_response(303)
            self.send_header("Location", "/")
            self.end_headers()
        else:
            self.send_error(404)


def start_server(host: str = "0.0.0.0", port: int = 8000) -> None:
    global _server_thread
    if _server_thread:
        return
    chat.init_chat()
    server = http.server.ThreadingHTTPServer((host, port), RemoteHandler)
    _server_thread = threading.Thread(target=server.serve_forever, daemon=True)
    _server_thread.start()


def draw_remote(screen, FONT) -> None:
    """Render placeholder screen for the remote menu."""
    screen.fill((30, 40, 80))
    msg = FONT.render("Remote server running", True, (255, 255, 255))
    screen.blit(msg, (6, 54))
    tip = FONT.render("Press joystick to return", True, (200, 220, 255))
    screen.blit(tip, (6, 114))

