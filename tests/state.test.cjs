const { test } = require('node:test');
const assert = require('node:assert/strict');
const fs = require('node:fs');
const vm = require('node:vm');
const path = require('node:path');
function store() {
    const saved = new Map();
    const context = { window: {}, localStorage: { getItem: key => saved.get(key) || null, setItem: (key, value) => saved.set(key, value) } };
    vm.runInNewContext(fs.readFileSync(path.join(__dirname, '../web/state.js'), 'utf8'), context);
    return context.window.LudusState;
}
const ids = new Set(['moonlight-meadow', 'pixel-trail']);
test('backup removes unknown IDs and unsupported data', () => {
    const state = store().validate({ version: 1, library: ['moonlight-meadow', 'unknown', 'moonlight-meadow'], favourites: ['pixel-trail'], url: 'https://example.invalid', settings: { accent: 'url(https://example.invalid)', compact: true }, profile: { name: 'A'.repeat(100) }, notes: { 'pixel-trail': 'B'.repeat(1000), unknown: 'private' } }, ids);
    assert.deepEqual(Array.from(state.library), ['moonlight-meadow']);
    assert.equal(state.url, undefined);assert.equal(state.settings.accent, '#9292ff');
    assert.equal(state.profile.name.length, 32);assert.equal(state.notes['pixel-trail'].length, 500);
    assert.equal(state.notes.unknown, undefined);
});
test('unsupported formats fail before changing existing preferences', () => {
    const storage = store();const state = storage.load(ids);state.profile.name = 'Local player';storage.save();
    assert.throws(() => storage.restore({ version: 99, profile: { name: 'Other' } }, ids));
    assert.equal(storage.load(ids).profile.name, 'Local player');
});
test('valid backups restore and reset only local preferences', () => {
    const storage = store();storage.load(ids);
    const restored = storage.restore({ version: 1, library: ['pixel-trail'], progress: { 'pixel-trail': 'finished' }, settings: { theme: 'light', accent: '#123456', motion: false } }, ids);
    assert.equal(restored.progress['pixel-trail'], 'finished');assert.equal(storage.load(ids).settings.theme, 'light');
    assert.equal(storage.reset().library.length, 0);assert.equal(storage.load(ids).profile.name, 'Player');
});
