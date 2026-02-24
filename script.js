const searchInput = document.getElementById('searchInput');
const searchBtn = document.getElementById('searchBtn');
const loader = document.getElementById('loader');
const errorDiv = document.getElementById('error');
const resultsDiv = document.getElementById('results');

// Trigger search on Enter key
searchInput.addEventListener('keydown', (e) => {
    if (e.key === 'Enter') performSearch();
});

async function performSearch() {
    const query = searchInput.value.trim();
    if (!query) {
        showError('⚠️ Please enter a search query.');
        return;
    }

    // Reset UI
    errorDiv.classList.add('hidden');
    resultsDiv.innerHTML = '';
    loader.classList.remove('hidden');
    searchBtn.disabled = true;

    try {
        const response = await fetch('/api/search', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ query })
        });

        if (!response.ok) {
            const err = await response.json();
            throw new Error(err.error || 'Search failed');
        }

        const data = await response.json();
        displayResults(data.results);
    } catch (err) {
        showError(`❌ ${err.message}`);
    } finally {
        loader.classList.add('hidden');
        searchBtn.disabled = false;
    }
}

function displayResults(results) {
    if (!results || results.length === 0) {
        resultsDiv.innerHTML = '<p style="text-align:center;color:var(--text-muted);">😕 No results found. Try a different query.</p>';
        return;
    }

    resultsDiv.innerHTML = results.map((r, i) => {
        const authors = formatAuthors(r.authors);
        return `
            <div class="result-card">
                <div class="card-header">
                    <h2 class="card-title">📄 ${escapeHtml(r.title)}</h2>
                    <span class="score-badge">⭐ ${r.score.toFixed(4)}</span>
                </div>
                <div class="card-meta">
                    <span class="meta-item">📅 ${escapeHtml(r.year)}</span>
                    <span class="meta-item">👤 ${escapeHtml(authors)}</span>
                    <span class="meta-item">🏛️ ${escapeHtml(r.venue)}</span>
                </div>
                <div class="card-abstract">
                    ${escapeHtml(r.abstract)}
                </div>
            </div>
        `;
    }).join('');
}

function formatAuthors(authorsStr) {
    try {
        const parsed = JSON.parse(authorsStr.replace(/'/g, '"'));
        if (Array.isArray(parsed)) {
            return parsed.length > 3
                ? parsed.slice(0, 3).join(', ') + ` +${parsed.length - 3} more`
                : parsed.join(', ');
        }
    } catch {}
    return authorsStr;
}

function showError(message) {
    errorDiv.textContent = message;
    errorDiv.classList.remove('hidden');
}

function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text || '';
    return div.innerHTML;
}
