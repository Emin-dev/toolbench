// Toolbench hub — renders the live tools from the catalog. Static store front
// with zero network calls; the list grows as the loop ships each tool.
import { TOOLS } from './products.js';

const esc = (s) => String(s).replace(/[&<>"]/g, (c) => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;' }[c]));

function card(t) {
  return `<a class="tool-card" href="${esc(t.liveUrl)}" rel="noopener">
    <span class="tool-emoji" aria-hidden="true">${esc(t.emoji || '🛠️')}</span>
    <span class="tool-body">
      <span class="tool-title-row">
        <span class="tool-name">${esc(t.name)}</span>
        <span class="tool-cat">${esc(t.category)}</span>
      </span>
      <span class="tool-tagline">${esc(t.tagline)}</span>
      <span class="tool-what">${esc(t.what)}</span>
      <span class="tool-meta">
        <span class="tool-price">${esc(t.price || 'Free')}</span>
        <span class="tool-open">Open →</span>
      </span>
    </span>
  </a>`;
}

const live = TOOLS.filter((t) => t.status === 'live');
const catalog = document.getElementById('catalog');

if (live.length === 0) {
  catalog.innerHTML = `<p class="empty">The first tools are being built right now — check back shortly.</p>`;
} else {
  catalog.innerHTML = live.map(card).join('');
}

const count = document.getElementById('tool-count');
count.textContent = live.length === 1
  ? '1 tool on the bench — more on the way.'
  : `${live.length} tools on the bench — more on the way.`;
