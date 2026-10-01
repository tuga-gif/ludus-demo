"""Standalone local demo. It does not connect to Ludus services."""
import argparse
import json
import shutil
import subprocess
import threading
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import urlsplit

ROOT = Path(__file__).resolve().parent
GAMES = json.loads((ROOT / 'data/games.json').read_text(encoding='utf-8'))
GAME_IDS = {game['id'] for game in GAMES}
STATIC = {
    '/': ('web/index.html', 'text/html; charset=utf-8'),
    '/index.html': ('web/index.html', 'text/html; charset=utf-8'),
    '/style.css': ('web/style.css', 'text/css; charset=utf-8'),
    '/app.js': ('web/app.js', 'text/javascript; charset=utf-8'),
    '/state.js': ('web/state.js', 'text/javascript; charset=utf-8'),
    '/logo.png': ('web/logo.png', 'image/png'),
}


def sample_bytes(game_id):
    return (f'Ludus demonstration sample: {game_id}\n' * 128).encode('utf-8')


class DemoServer(ThreadingHTTPServer):
    daemon_threads = True
    block_on_close = False

    def __init__(self, output_dir=None, port=0):
        super().__init__(('127.0.0.1', port), Handler)
        self.origin = f'http://127.0.0.1:{self.server_port}'
        self.output_dir = Path(output_dir) if output_dir else ROOT / '.local/downloads'
        self.jobs = {}
        self.lock = threading.Lock()
        self.download_slot = threading.BoundedSemaphore(1)

    def start_download(self, game_id):
        engine = shutil.which('aria2c')
        if not engine:
            return 503, {'error': 'Install aria2 and make aria2c available on PATH to try downloads.'}
        if not self.download_slot.acquire(blocking=False):
            return 409, {'error': 'A sample download is already running.'}
        with self.lock:
            self.jobs[game_id] = {'gameId': game_id, 'status': 'downloading'}
        threading.Thread(target=self.download, args=(engine, game_id), daemon=True).start()
        return 202, {'gameId': game_id, 'status': 'downloading'}

    def download(self, engine, game_id):
        try:
            self.output_dir.mkdir(parents=True, exist_ok=True)
            result = subprocess.run([
                engine, '--no-conf=true', '--no-netrc=true', '--enable-rpc=false',
                '--all-proxy=', '--allow-overwrite=true', '--auto-file-renaming=false',
                '--split=1', '--max-connection-per-server=1', '--max-tries=1',
                '--timeout=10', '--summary-interval=0', '--console-log-level=error',
                f'--dir={self.output_dir.resolve()}', f'--out={game_id}.txt',
                f'{self.origin}/samples/{game_id}.txt',
            ], capture_output=True, timeout=30, check=False)
            file = self.output_dir / f'{game_id}.txt'
            complete = result.returncode == 0 and file.is_file() and file.read_bytes() == sample_bytes(game_id)
            state = {'gameId': game_id, 'status': 'complete' if complete else 'failed'}
            if not complete:
                state['error'] = 'The sample could not be downloaded.'
        except (OSError, subprocess.TimeoutExpired):
            state = {'gameId': game_id, 'status': 'failed', 'error': 'The sample could not be downloaded.'}
        finally:
            with self.lock:
                self.jobs[game_id] = state
            self.download_slot.release()


class Handler(BaseHTTPRequestHandler):
    def log_message(self, *args):
        pass

    def respond(self, status, data, content_type='application/json; charset=utf-8'):
        body = json.dumps(data).encode() if isinstance(data, (dict, list)) else data
        self.send_response(status)
        self.send_header('Content-Type', content_type)
        self.send_header('Content-Length', str(len(body)))
        self.send_header('Cache-Control', 'no-store')
        self.send_header('X-Content-Type-Options', 'nosniff')
        self.send_header('Referrer-Policy', 'no-referrer')
        self.send_header('Content-Security-Policy', "default-src 'self'; script-src 'self'; style-src 'self'; img-src 'self'; connect-src 'self'; object-src 'none'; base-uri 'none'; frame-ancestors 'none'; form-action 'none'")
        self.end_headers()
        self.wfile.write(body)

    def valid_host(self):
        return self.headers.get('Host') == urlsplit(self.server.origin).netloc

    def do_GET(self):
        if not self.valid_host():
            return self.respond(403, {'error': 'Host not allowed.'})
        path = urlsplit(self.path).path
        if path in STATIC:
            file, content_type = STATIC[path]
            return self.respond(200, (ROOT / file).read_bytes(), content_type)
        if path == '/api/games':
            return self.respond(200, GAMES)
        if path == '/api/downloads':
            with self.server.lock:
                jobs = list(self.server.jobs.values())
            return self.respond(200, jobs)
        if path.startswith('/samples/') and path.endswith('.txt'):
            game_id = path[len('/samples/'):-len('.txt')]
            if game_id in GAME_IDS:
                return self.respond(200, sample_bytes(game_id), 'text/plain; charset=utf-8')
        return self.respond(404, {'error': 'Not found.'})

    def do_POST(self):
        if not self.valid_host() or self.headers.get('Origin') != self.server.origin:
            return self.respond(403, {'error': 'Origin not allowed.'})
        if self.path != '/api/download':
            return self.respond(404, {'error': 'Not found.'})
        if self.headers.get('Transfer-Encoding') or self.headers.get('Content-Type') != 'application/json':
            return self.respond(415, {'error': 'Use a JSON request.'})
        try:
            size = int(self.headers.get('Content-Length', '0'))
            if not 0 < size <= 512:
                return self.respond(413, {'error': 'Invalid request size.'})
            data = json.loads(self.rfile.read(size))
            if not isinstance(data, dict) or set(data) != {'gameId'} or not isinstance(data['gameId'], str) or data['gameId'] not in GAME_IDS:
                return self.respond(400, {'error': 'Choose a sample from the demo catalogue.'})
        except (ValueError, UnicodeError):
            return self.respond(400, {'error': 'Invalid JSON.'})
        status, result = self.server.start_download(data['gameId'])
        return self.respond(status, result)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Run the standalone Ludus demo locally.')
    parser.add_argument('--port', type=int, default=8791, help='Local port (default: 8791; use 0 for an available port).')
    args = parser.parse_args()
    if not 0 <= args.port <= 65535:
        parser.error('The port must be between 0 and 65535.')
    try:
        server = DemoServer(port=args.port)
    except OSError:
        parser.exit(1, 'The local port is unavailable. Stop the other demo instance or choose --port with another port.\n')
    print(json.dumps({'url': server.origin}), flush=True)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()
