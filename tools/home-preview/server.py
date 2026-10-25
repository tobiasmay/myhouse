#!/usr/bin/env python3
"""
A local stand-in for GlassHouse's TV-side server, just enough to open
server/assets/home.html in an ordinary desktop browser and see real layout,
real glass/blur rendering and a real (generated) wallpaper, without
deploying anything to the TV.

Usage:
    python3 tools/home-preview/server.py [port]

Then open http://localhost:<port>/assets/home.html
Optional query params the page itself understands:
    ?wall=morning|afternoon|evening|night   force a wallpaper slot
    ?hour=19                                force the hour used to pick a slot

Mouse works: click a tile to "open" it (logged to this terminal, nothing
really launches); arrow keys and Enter work like the remote would.

This mock is intentionally dumb: fixed catalogue, no persistence across
restarts, no auth. It exists purely for visual iteration on home.html's
CSS/markup, not for testing real layout-save/wallpaper-upload logic (that
still needs the real server on the TV or a full dev checkout).
"""
import http.server
import json
import os
import socketserver
import sys
import urllib.parse

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', 'server'))
WALL_DIR = os.path.join(os.path.dirname(__file__), '_generated-wallpapers')

APP_ID = {
    'netflix': 'netflix', 'youtube': 'youtube.leanback.v4', 'spotify': 'com.spotify.tv.webos',
    'disneyplus': 'com.disney.disneyplus-prod', 'prime': 'amazon', 'appletv': 'com.apple.appletv',
    'arte': 'com.arte.tv', 'ard': 'ard.mediathek', 'zdf': 'de.zdf.app.zdfm3',
    'jellyfin': 'org.jellyfin.webos', 'plex': 'cdp-30', 'twitch': 'tv.twitch.tv.starshot.lg',
}

# A mix of apps WITH a curated override (no icon/native-icon-less, so the
# override is obviously doing the work) and plain apps with only a
# low-res-simulated native icon, so both code paths show on screen at once.
CATALOGUE = {
    'ok': True,
    'apps': [
        {'id': APP_ID['netflix'], 'title': 'Netflix'},
        {'id': APP_ID['youtube'], 'title': 'YouTube'},
        {'id': APP_ID['disneyplus'], 'title': 'Disney+'},
        {'id': APP_ID['prime'], 'title': 'Prime Video'},
        {'id': APP_ID['appletv'], 'title': 'Apple TV'},
        {'id': APP_ID['ard'], 'title': 'ARD Mediathek'},
        {'id': APP_ID['zdf'], 'title': 'ZDF'},
        {'id': APP_ID['arte'], 'title': 'ARTE'},
        {'id': APP_ID['spotify'], 'title': 'Spotify'},
        {'id': APP_ID['jellyfin'], 'title': 'Jellyfin'},
        # No override for these two: they fall back to a native-style
        # low-res icon (generated below) so you can compare against the
        # curated ones side by side.
        {'id': APP_ID['plex'], 'title': 'Plex', 'icon': '/preview/native-icon.png'},
        {'id': APP_ID['twitch'], 'title': 'Twitch', 'icon': '/preview/native-icon.png'},
    ],
    'devices': [
        {'id': 'com.webos.app.hdmi1', 'name': 'PlayStation 5', 'port': '1', 'via': None, 'unused': False, 'address': '4.0'},
        {'id': 'com.webos.app.hdmi2', 'name': 'Apple TV', 'port': '2', 'via': None, 'unused': False, 'address': None},
        {'id': 'com.webos.app.hdmi3', 'name': 'HDMI 3', 'port': '3', 'via': None, 'unused': True, 'address': None},
    ],
    'channels': [],
    'order': {
        'app': [a['id'] for a in [
            {'id': APP_ID['netflix']}, {'id': APP_ID['youtube']}, {'id': APP_ID['disneyplus']},
            {'id': APP_ID['prime']}, {'id': APP_ID['appletv']}, {'id': APP_ID['ard']},
            {'id': APP_ID['zdf']}, {'id': APP_ID['arte']}, {'id': APP_ID['spotify']},
            {'id': APP_ID['jellyfin']}, {'id': APP_ID['plex']}, {'id': APP_ID['twitch']},
        ]],
        'dev': ['com.webos.app.hdmi1', 'com.webos.app.hdmi2', 'com.webos.app.hdmi3'],
        'ch': [],
    },
    'sources': {'channels': 0},
    'layout': {
        'rows': ['app', 'dev', 'ch'],
        'colours': None,
        'hidden': {'app': [], 'dev': [], 'ch': []},
        'sort': {},
        'hintSeen': True,
        'channels': [],
        'picture': False,
    },
    'wallpapers': {'available': True, 'slots': {'night': True, 'morning': True, 'afternoon': True, 'evening': True}, 'revision': 'preview1'},
}

NOW = {'kind': 'app', 'title': 'Netflix', 'appId': APP_ID['netflix']}


def ensure_wallpapers():
    """Generate one soft gradient JPEG per time-of-day slot, purely so the
    wallpaper cross-fade and scrim have something real to render. Not meant
    to look like a real photo; just a stand-in with believable colour and
    luminance for each slot."""
    from PIL import Image, ImageDraw, ImageFilter

    os.makedirs(WALL_DIR, exist_ok=True)
    slots = {
        'night': [(10, 14, 28), (4, 6, 14)],
        'morning': [(255, 200, 140), (120, 150, 190)],
        'afternoon': [(140, 190, 230), (90, 130, 180)],
        'evening': [(255, 140, 90), (60, 40, 70)],
    }
    for key, (top, bottom) in slots.items():
        path = os.path.join(WALL_DIR, key + '.jpg')
        if os.path.exists(path):
            continue
        w, h = 960, 540
        img = Image.new('RGB', (w, h), top)
        draw = ImageDraw.Draw(img)
        for y in range(h):
            t = y / h
            col = tuple(int(top[i] * (1 - t) + bottom[i] * t) for i in range(3))
            draw.line([(0, y), (w, y)], fill=col)
        img = img.filter(ImageFilter.GaussianBlur(40))
        img.save(path, quality=85)


def ensure_native_icon():
    """A small, slightly-soft PNG standing in for a real low-res webOS app
    icon (the kind ICON_OVERRIDES is meant to improve on)."""
    from PIL import Image, ImageDraw, ImageFilter

    os.makedirs(WALL_DIR, exist_ok=True)
    path = os.path.join(WALL_DIR, 'native-icon.png')
    if os.path.exists(path):
        return
    img = Image.new('RGBA', (80, 80), (60, 60, 65, 255))
    draw = ImageDraw.Draw(img)
    draw.ellipse((14, 14, 66, 66), fill=(210, 90, 60, 255))
    img = img.filter(ImageFilter.GaussianBlur(0.6))  # a hint of native softness
    img.save(path)


class Handler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *a, **kw):
        super().__init__(*a, directory=ROOT, **kw)

    def log_message(self, fmt, *args):
        sys.stderr.write('[preview] ' + (fmt % args) + '\n')

    def _json(self, obj, status=200):
        body = json.dumps(obj).encode('utf-8')
        self.send_response(status)
        self.send_header('Content-Type', 'application/json')
        self.send_header('Content-Length', str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def _file(self, path, content_type):
        with open(path, 'rb') as f:
            body = f.read()
        self.send_response(200)
        self.send_header('Content-Type', content_type)
        self.send_header('Content-Length', str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self):
        parsed = urllib.parse.urlsplit(self.path)
        path, query = parsed.path, urllib.parse.parse_qs(parsed.query)

        if path == '/api/home':
            return self._json({'ok': True, 'available': True, 'enabled': True,
                                'supported': {'ok': True}, 'writable': True,
                                'restorePending': False, 'layout': CATALOGUE['layout']})
        if path == '/api/home/catalogue':
            return self._json(CATALOGUE)
        if path == '/api/home/now':
            return self._json(NOW)
        if path == '/api/home/guide':
            return self._json({'ok': True, 'guide': {}})
        if path == '/api/home/recents':
            return self._json({'ok': True, 'apps': [], 'stamp': 0})
        if path == '/api/home/picture':
            return self._json({'ok': True, 'picture': None})
        if path == '/api/home/wallpaper':
            slot = (query.get('slot') or ['night'])[0]
            return self._file(os.path.join(WALL_DIR, slot + '.jpg'), 'image/jpeg')
        if path == '/preview/native-icon.png':
            return self._file(os.path.join(WALL_DIR, 'native-icon.png'), 'image/png')

        return super().do_GET()

    def do_POST(self):
        length = int(self.headers.get('Content-Length') or 0)
        raw = self.rfile.read(length) if length else b''
        try:
            body = json.loads(raw) if raw else {}
        except ValueError:
            body = {}
        print('[preview] POST %s %s' % (self.path, body))
        if self.path == '/api/home/beat':
            return self._json({'ok': True, 'wallpapers': CATALOGUE['wallpapers']})
        return self._json({'ok': True})


def main():
    port = int(sys.argv[1]) if len(sys.argv) > 1 else 8765
    ensure_wallpapers()
    ensure_native_icon()
    with socketserver.TCPServer(('127.0.0.1', port), Handler) as httpd:
        print('Glasshouse Home preview: http://localhost:%d/assets/home.html' % port)
        print('(Ctrl+C to stop)')
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            pass


if __name__ == '__main__':
    main()
