'use strict';
const { app, BrowserWindow, session, dialog } = require('electron');
const { spawn } = require('node:child_process');
const path = require('node:path');
let backend;
let stopping = false;
let startupTimer;
app.setPath('userData', path.join(app.getPath('appData'), 'LudusOpenEdition'));
function fail(message) {
    if (stopping) return;
    stopping = true;
    clearTimeout(startupTimer);
    dialog.showErrorBox('Ludus demo', message);
    app.quit();
}
if (!app.requestSingleInstanceLock()) app.quit();
else app.whenReady().then(() => {
    const python = process.env.LUDUS_DEMO_PYTHON || (process.platform === 'win32' ? 'py' : 'python3');
    backend = spawn(python, ['-u', path.join(__dirname, 'demo.py'), '--port', '8792'], { cwd: __dirname, windowsHide: true, stdio: ['ignore', 'pipe', 'pipe'] });
    let buffer = '';
    let windowOpened = false;
    let startupError = '';
    startupTimer = setTimeout(() => fail('The local demo did not start. Check your Python installation and try again.'), 15000);
    backend.stderr.on('data', chunk => { if (!windowOpened) startupError = (startupError + chunk.toString()).slice(-1500); });
    backend.stdout.on('data', chunk => {
        if (windowOpened || stopping) return;
        buffer += chunk.toString();
        if (buffer.length > 4096) return fail('The local demo returned an invalid startup message.');
        if (!buffer.includes('\n')) return;
        let origin;
        try {
            origin = JSON.parse(buffer.split('\n')[0]).url;
            const url = new URL(origin);
            if (url.origin !== 'http://127.0.0.1:8792' || url.pathname !== '/') throw new Error('Invalid origin');
        } catch { return fail('The local demo returned an invalid address.'); }
        windowOpened = true;clearTimeout(startupTimer);
        const allowed = value => { try { return new URL(value).origin === origin; } catch { return false; } };
        session.defaultSession.webRequest.onBeforeRequest((details, callback) => callback({ cancel: !allowed(details.url) }));
        session.defaultSession.setPermissionRequestHandler((_contents, _permission, callback) => callback(false));
        const window = new BrowserWindow({ width: 1180, height: 800, minWidth: 620, minHeight: 480, backgroundColor: '#101012', title: 'Ludus demo', autoHideMenuBar: true,
            webPreferences: { nodeIntegration: false, contextIsolation: true, sandbox: true, webSecurity: true } });
        window.webContents.setWindowOpenHandler(() => ({ action: 'deny' }));
        window.webContents.on('will-navigate', (event, target) => { if (!allowed(target)) event.preventDefault(); });
        window.loadURL(origin).catch(() => fail('The local demo page could not be opened.'));
    });
    backend.on('error', () => fail('Python could not be started. Install Python or set LUDUS_DEMO_PYTHON to its executable.'));
    backend.on('exit', code => {
        if (!windowOpened && !stopping && code !== 0) fail(startupError.includes('port is unavailable') ? 'Port 8792 is already in use. Stop the other desktop demo and try again.' : 'The local demo could not start. Check your Python installation.');
        else app.quit();
    });
});
app.on('window-all-closed', () => app.quit());
app.on('before-quit', () => { stopping = true;clearTimeout(startupTimer);if (backend && !backend.killed) backend.kill(); });
