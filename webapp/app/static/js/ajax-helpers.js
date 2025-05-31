// AJAX HELPERS MODULE
async function fetchHtml(url) {
    const resp = await fetch(url);
    if (resp.ok) return await resp.text();
    throw new Error('Ошибка загрузки');
}
async function fetchJson(url) {
    const resp = await fetch(url);
    if (resp.ok) return await resp.json();
    throw new Error('Ошибка загрузки');
}

export { fetchHtml, fetchJson };
