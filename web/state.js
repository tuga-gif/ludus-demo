
'use strict';
window.LudusState = (() => {
    const key = 'ludus-open-edition';
    const fresh = () => ({ version: 1, library: [], favourites: [], progress: {}, notes: {}, profile: { name: 'Player', bio: '' }, settings: { theme: 'dark', accent: '#9292ff', compact: false, motion: true } });
    function validate(value, ids) {
        if (!value || typeof value !== 'object' || Array.isArray(value) || value.version !== 1) throw new Error('Choose a Ludus Open Edition backup.');
        const clean = fresh();
        for (const field of ['library', 'favourites']) if (Array.isArray(value[field])) clean[field] = [...new Set(value[field].filter(id => typeof id === 'string' && ids.has(id)))];
        for (const id of ids) {
            if (['planned', 'playing', 'finished'].includes(value.progress?.[id])) clean.progress[id] = value.progress[id];
            if (typeof value.notes?.[id] === 'string') clean.notes[id] = value.notes[id].slice(0, 500);
        }
        if (typeof value.profile?.name === 'string') clean.profile.name = value.profile.name.slice(0, 32).trim() || 'Player';
        if (typeof value.profile?.bio === 'string') clean.profile.bio = value.profile.bio.slice(0, 160);
        clean.settings.theme = value.settings?.theme === 'light' ? 'light' : 'dark';
        if (/^#[a-f0-9]{6}$/i.test(value.settings?.accent || '')) clean.settings.accent = value.settings.accent;
        clean.settings.compact = value.settings?.compact === true;
        clean.settings.motion = value.settings?.motion !== false;
        return clean;
    }
    let current = fresh();
    function load(ids) {
        try {
            const raw = localStorage.getItem(key);
            if (raw && raw.length <= 65536) current = validate(JSON.parse(raw), ids);
            else {
                const legacy = JSON.parse(localStorage.getItem('ludus-demo-library') || '[]');
                if (Array.isArray(legacy)) current.library = legacy.filter(id => ids.has(id));
                current.settings.theme = localStorage.getItem('ludus-demo-theme') === 'light' ? 'light' : 'dark';
            }
        } catch { current = fresh(); }
        return current;
    }
    function save() { try { localStorage.setItem(key, JSON.stringify(current));return true; } catch { return false; } }
    function restore(value, ids) { current = validate(value, ids);save();return current; }
    function reset() { current = fresh();save();return current; }
    return { load, save, restore, reset, validate };
})();
