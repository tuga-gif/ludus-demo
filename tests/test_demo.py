import json
import tempfile
import threading
import unittest
from urllib.error import HTTPError
from urllib.request import Request, urlopen
from unittest.mock import patch
from demo import DemoServer


class DemoBoundaryTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.temp = tempfile.TemporaryDirectory()
        cls.server = DemoServer(cls.temp.name)
        cls.thread = threading.Thread(target=cls.server.serve_forever, daemon=True)
        cls.thread.start()

    @classmethod
    def tearDownClass(cls):
        cls.server.shutdown();cls.server.server_close();cls.temp.cleanup()

    def call(self, path, data=None, origin=None, headers=None):
        request_headers = {'Content-Type': 'application/json'}
        if data is not None:
            request_headers['Origin'] = origin or self.server.origin
        request_headers.update(headers or {})
        request = Request(self.server.origin + path, data=json.dumps(data).encode() if data is not None else None, headers=request_headers)
        try:
            with urlopen(request, timeout=3) as response:
                return response.status, response.read()
        except HTTPError as error:
            with error:
                return error.code, error.read()

    def test_fictional_catalogue_only(self):
        code, body = self.call('/api/games')
        self.assertEqual(code, 200)
        self.assertEqual(len(json.loads(body)), 12)

    def test_private_files_and_production_routes_are_absent(self):
        for path in ['/.env', '/.git/config', '/demo.py', '/data/games.json', '/api/login', '/api/cloud-save', '/api/manifests', '/../../demo.py', '/%2e%2e/demo.py']:
            with self.subTest(path=path):
                self.assertEqual(self.call(path)[0], 404)

    def test_other_origin_is_refused(self):
        self.assertEqual(self.call('/api/download', {'gameId': 'pixel-trail'}, origin='https://example.invalid')[0], 403)

    def test_missing_origin_is_refused(self):
        self.assertEqual(self.call('/api/download', {'gameId': 'pixel-trail'}, headers={'Origin': ''})[0], 403)

    def test_other_host_is_refused(self):
        self.assertEqual(self.call('/', headers={'Host': 'example.invalid'})[0], 403)

    def test_arbitrary_urls_and_paths_are_refused(self):
        for data in [{'gameId': '../outside'}, {'gameId': 'pixel-trail', 'url': 'https://example.invalid/file'}, {'url': 'http://127.0.0.1:9/private'}, {'gameId': []}]:
            self.assertEqual(self.call('/api/download', data)[0], 400)

    def test_oversized_request_is_refused(self):
        self.assertEqual(self.call('/api/download', {'gameId': 'a' * 700})[0], 413)

    def test_missing_engine_has_clear_message(self):
        with patch('demo.shutil.which', return_value=None):
            code, body = self.call('/api/download', {'gameId': 'pixel-trail'})
        self.assertEqual(code, 503)
        self.assertIn('Install aria2', json.loads(body)['error'])

    def test_sample_only_serves_known_ids(self):
        self.assertEqual(self.call('/samples/pixel-trail.txt')[0], 200)
        self.assertEqual(self.call('/samples/unknown.txt')[0], 404)


if __name__ == '__main__':
    unittest.main()
