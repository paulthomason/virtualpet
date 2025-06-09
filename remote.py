import http.server
import threading
import urllib.parse
import settings

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
            html = f"""<html><body><h1>Remote Control</h1>
<p>Difficulty: {difficulty}</p>
<p>WiFi: {wifi_status}</p>
<p>Set difficulty:
<a href='/set?option=Difficulty&value=Easy'>Easy</a> |
<a href='/set?option=Difficulty&value=Normal'>Normal</a> |
<a href='/set?option=Difficulty&value=Hard'>Hard</a></p>
<p>Toggle WiFi:
<a href='/set?option=WiFi&value=true'>On</a> |
<a href='/set?option=WiFi&value=false'>Off</a></p>
</body></html>"""
            self.wfile.write(html.encode("utf-8"))
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
        else:
            self.send_error(404)


def start_server(host: str = "0.0.0.0", port: int = 8000) -> None:
    global _server_thread
    if _server_thread:
        return
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

