'use strict';
let games = [], state, selected;
const byId = id => document.getElementById(id);
const status = message => { byId('status').textContent = message; };
function element(tag, text, className) {
    const node = document.createElement(tag);
    if (text !== undefined) node.textContent = text;
    if (className) node.className = className;
    return node;
}
function persist() { if (!LudusState.save()) status('Your browser could not save these preferences.'); }
async function request(path, options) {
    const response = await fetch(path, options);
    const result = await response.json();
    if (!response.ok) throw new Error(result.error || 'This action is unavailable.');
    return result;
}
function appearance() {
    const settings = state.settings;
    document.documentElement.classList.toggle('light', settings.theme === 'light');
    document.documentElement.classList.toggle('compact', settings.compact);
    document.documentElement.classList.toggle('no-motion', !settings.motion);
    document.documentElement.style.setProperty('--accent', settings.accent);
    byId('theme').textContent = settings.theme === 'light' ? 'Dark theme' : 'Light theme';
    byId('theme-select').value = settings.theme;
    byId('accent').value = settings.accent;
    byId('compact').checked = settings.compact;
    byId('motion').checked = settings.motion;
}
function toggle(list, id) {
    const index = state[list].indexOf(id);
    if (index >= 0) state[list].splice(index, 1);else state[list].push(id);
    persist();render();
}
function button(label, callback, className) {
    const node = element('button', label, className);
    node.type = 'button';node.addEventListener('click', callback);return node;
}
async function download(game) {
    try {
        await request('/api/download', { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ gameId: game.id }) });
        byId('details').close();location.hash = 'downloads';status('Sample download started.');
    } catch (error) { status(error.message); }
}
function card(game) {
    const article = element('article', undefined, 'game');
    const cover = element('div', game.name.charAt(0), `cover ${game.colour}`);
    cover.setAttribute('aria-hidden', 'true');
    const body = element('div', undefined, 'game-body');
    body.append(element('h2', game.name), element('span', `${game.genre} / ${game.year}`, 'genre'), element('p', game.description));
    const actions = element('div', undefined, 'actions');
    actions.append(button('View details', () => showDetails(game), 'primary'), button(state.library.includes(game.id) ? 'Remove from library' : 'Add to library', () => toggle('library', game.id)));
    body.append(actions);article.append(cover, body);return article;
}
function cards(target, list, message) {
    target.replaceChildren(...list.map(card));
    if (!list.length) target.append(element('p', message, 'empty'));
}
function statistics(target) {
    target.replaceChildren();
    for (const [label, count] of [['In your library', state.library.length], ['Favourites', state.favourites.length], ['Finished', state.library.filter(id => state.progress[id] === 'finished').length]]) {
        const item = element('div', undefined, 'stat');item.append(element('strong', String(count)), element('span', label));target.append(item);
    }
}
function render() {
    const query = byId('search').value.trim().toLowerCase(), genre = byId('genre').value;
    const matches = games.filter(game => (!genre || game.genre === genre) && `${game.name} ${game.genre}`.toLowerCase().includes(query));
    const sort = byId('sort').value;
    matches.sort((a, b) => sort === 'year' ? b.year - a.year || a.name.localeCompare(b.name) : (sort === 'genre' ? a.genre.localeCompare(b.genre) : 0) || a.name.localeCompare(b.name));
    cards(byId('games'), matches, 'No sample games match your search.');
    byId('result-count').textContent = `${matches.length} of ${games.length} sample games`;
    const filter = byId('library-filter').value;
    const owned = games.filter(game => state.library.includes(game.id) && (filter === 'all' || (filter === 'favourites' ? state.favourites.includes(game.id) : state.progress[game.id] === filter)));
    cards(byId('library-games'), owned, 'No games on this shelf yet. Pick a sample game from the Store.');
    statistics(byId('library-stats'));statistics(byId('profile-stats'));
    byId('profile-name').textContent = state.profile.name;byId('profile-bio').textContent = state.profile.bio;
    byId('avatar').textContent = state.profile.name.charAt(0).toUpperCase();byId('profile-link').textContent = state.profile.name;
    byId('name-input').value = state.profile.name;byId('bio-input').value = state.profile.bio;
    if (selected && byId('details').open) detailActions();
}
function detailActions() {
    const game = selected;
    byId('detail-actions').replaceChildren(
        button(state.library.includes(game.id) ? 'Remove from library' : 'Add to library', () => toggle('library', game.id)),
        button(state.favourites.includes(game.id) ? 'Remove favourite' : 'Favourite', () => toggle('favourites', game.id)),
        button('Download sample', () => download(game), 'primary'));
}
function showDetails(game) {
    selected = game;
    byId('detail-cover').className = `cover ${game.colour}`;byId('detail-cover').textContent = game.name.charAt(0);
    byId('detail-title').textContent = game.name;byId('detail-meta').textContent = `${game.year} / ${game.tags.join(' / ')}`;
    byId('detail-description').textContent = game.description;
    byId('progress').value = state.progress[game.id] || 'planned';byId('notes').value = state.notes[game.id] || '';
    detailActions();byId('details').showModal();
}
function collections() {
    byId('collection-list').replaceChildren();
    for (const name of [...new Set(games.map(game => game.collection))]) {
        const section = element('section', undefined, 'collection'), grid = element('div', undefined, 'grid');
        section.append(element('h2', name));cards(grid, games.filter(game => game.collection === name), '');section.append(grid);byId('collection-list').append(section);
    }
}
async function downloads() {
    if (byId('downloads').hidden) return;
    try {
        const jobs = await request('/api/downloads');
        const rows = jobs.map(job => {
            const row = element('div', undefined, 'download-row'), game = games.find(game => game.id === job.gameId);
            row.append(element('strong', game?.name || 'Sample'), element('span', job.error || ({ complete: 'Downloaded', downloading: 'Downloading', failed: 'Failed' }[job.status] || 'Waiting')));return row;
        });
        byId('download-list').replaceChildren(...rows);
        if (!rows.length) byId('download-list').append(element('p', 'Open game details in the Store to download a sample.', 'empty'));
    } catch (error) { status(error.message); }
}
function navigate() {
    const name = location.hash.slice(1);
    const active = ['store', 'library', 'downloads', 'collections', 'profile', 'settings', 'about'].includes(name) ? name : 'store';
    document.querySelectorAll('.view').forEach(view => { view.hidden = view.id !== active; });
    document.querySelectorAll('nav a').forEach(link => { if (link.hash === `#${active}`) link.setAttribute('aria-current', 'page');else link.removeAttribute('aria-current'); });
    downloads();
}
byId('close-details').addEventListener('click', () => byId('details').close());
byId('save-notes').addEventListener('click', () => {
    state.notes[selected.id] = byId('notes').value.slice(0, 500);state.progress[selected.id] = byId('progress').value;
    if (!state.library.includes(selected.id)) state.library.push(selected.id);
    persist();render();status('Notes and play status saved.');byId('details').close();
});
for (const id of ['search', 'genre', 'sort', 'library-filter']) byId(id).addEventListener(id === 'search' ? 'input' : 'change', render);
byId('theme').addEventListener('click', () => { state.settings.theme = state.settings.theme === 'dark' ? 'light' : 'dark';appearance();persist(); });
byId('theme-select').addEventListener('change', event => { state.settings.theme = event.target.value;appearance();persist(); });
for (const [id, setting] of [['accent', 'accent'], ['compact', 'compact'], ['motion', 'motion']]) byId(id).addEventListener('change', event => {
    state.settings[setting] = id === 'accent' ? event.target.value : event.target.checked;appearance();persist();
});
byId('profile-form').addEventListener('submit', event => { event.preventDefault();state.profile = { name: byId('name-input').value.trim().slice(0, 32) || 'Player', bio: byId('bio-input').value.slice(0, 160) };persist();render();status('Local profile saved.'); });
byId('export').addEventListener('click', () => {
    const url = URL.createObjectURL(new Blob([JSON.stringify(state, null, 2)], { type: 'application/json' }));
    const link = element('a');link.href = url;link.download = 'ludus-open-edition-backup.json';link.click();setTimeout(() => URL.revokeObjectURL(url), 1000);status('Local backup exported.');
});
byId('import').addEventListener('change', async event => {
    const file = event.target.files[0];if (!file) return;
    try {
        if (file.size > 65536) throw new Error('Choose a backup smaller than 64 KB.');
        state = LudusState.restore(JSON.parse(await file.text()), new Set(games.map(game => game.id)));appearance();render();status('Local backup restored.');
    } catch (error) { status(error instanceof SyntaxError ? 'This file is not valid JSON.' : error.message); }
    finally { event.target.value = ''; }
});
byId('reset').addEventListener('click', () => byId('reset-dialog').showModal());
byId('cancel-reset').addEventListener('click', () => byId('reset-dialog').close());
byId('confirm-reset').addEventListener('click', () => { state = LudusState.reset();appearance();render();byId('reset-dialog').close();status('Local preferences reset.'); });
document.addEventListener('keydown', event => {
    if (event.key === '/' && !event.ctrlKey && !event.metaKey && !event.altKey && !byId('details').open && !byId('reset-dialog').open && !['INPUT', 'TEXTAREA', 'SELECT'].includes(event.target.tagName)) {
        event.preventDefault();location.hash = 'store';byId('search').focus();
    }
});
window.addEventListener('hashchange', navigate);
request('/api/games').then(result => {
    games = result;state = LudusState.load(new Set(games.map(game => game.id)));
    for (const genre of [...new Set(games.map(game => game.genre))].sort()) { const option = element('option', genre);option.value = genre;byId('genre').append(option); }
    const featured = games[0];byId('featured').append(element('span', 'FEATURED SAMPLE', 'eyebrow'), element('h2', featured.name), element('p', featured.description), button('Explore game', () => showDetails(featured), 'primary'));
    appearance();render();collections();navigate();setInterval(downloads, 1500);
}).catch(error => status(error.message));
