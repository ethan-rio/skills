/* ==========================================================================
   book-2-site runtime
   Schema-tolerant renderer. Reads window.BOOK and window.QUOTES.
   - Always-on views: Read (if chapters present), Summary, Values, Quotes, Map
   - Conditional: Tips, Quiz, Scenarios (rendered only if data provided)
   Unknown section types render as placeholders with "please regenerate" hints.
   ========================================================================== */
(() => {
  const B = window.BOOK || {};
  const Q = window.QUOTES || [];

  // ---------- Utilities ----------
  const $ = (s, el=document) => el.querySelector(s);
  const $$ = (s, el=document) => [...el.querySelectorAll(s)];
  const esc = s => String(s==null?'':s).replace(/[&<>"']/g, c => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));

  // HTML can be passed in some fields (why, intro, body); allow it.
  const html = s => s==null ? '' : String(s);

  const slug = (B.meta && B.meta.slug) || 'book';
  const STORE_PROGRESS = `b2s-progress-${slug}`;
  const STORE_MAP      = `b2s-map-${slug}`;
  const STORE_USER_Q   = `b2s-user-q-${slug}`;
  const STORE_FAV_Q    = `b2s-fav-q-${slug}`;
  const STORE_OVR_Q    = `b2s-ovr-q-${slug}`;
  const STORE_HIDE_Q   = `b2s-hide-q-${slug}`;
  const STORE_THEME    = 'b2s-theme';

  const loadSet = k => { try { return new Set(JSON.parse(localStorage.getItem(k))||[]); } catch(_){ return new Set(); } };
  const saveSet = (k, s) => localStorage.setItem(k, JSON.stringify([...s]));
  const loadObj = k => { try { return JSON.parse(localStorage.getItem(k))||{}; } catch(_){ return {}; } };
  const saveObj = (k, o) => localStorage.setItem(k, JSON.stringify(o));
  const loadArr = k => { try { return JSON.parse(localStorage.getItem(k))||[]; } catch(_){ return []; } };
  const saveArr = (k, a) => localStorage.setItem(k, JSON.stringify(a));

  const state = { read: loadSet(STORE_PROGRESS), mode: 'summary' };
  const saveProgress = () => saveSet(STORE_PROGRESS, state.read);

  // ---------- Mode buttons (adaptive — only views that have data) ----------
  const VIEW_ORDER = [
    { key:'read',     label:'📖 Read',      cond: () => B.read && Array.isArray(B.read.chapters) && B.read.chapters.length },
    { key:'summary',  label:'📚 Summary',   cond: () => B.summary && Array.isArray(B.summary.sections) },
    { key:'values',   label:'✨ Values',    cond: () => B.values && Array.isArray(B.values.themes) && B.values.themes.length },
    { key:'quotes',   label:'💬 Quotes',    cond: () => Array.isArray(Q) && (Q.length > 0 || true) }, // always on
    { key:'map',      label:'🗺️ Map',       cond: () => B.map && Array.isArray(B.map.archetypes) && B.map.archetypes.length },
    { key:'tips',     label:'💡 Tips',      cond: () => Array.isArray(B.tips) && B.tips.length },
    { key:'quiz',     label:'🎯 Quiz',      cond: () => Array.isArray(B.quiz) && B.quiz.length },
    { key:'sim',      label:'🧪 Scenarios', cond: () => Array.isArray(B.scenarios) && B.scenarios.length },
  ];
  const enabledViews = VIEW_ORDER.filter(v => {
    try { return v.cond(); } catch(_){ return false; }
  });

  // ---------- Hero ----------
  function renderHero() {
    const m = B.meta || {};
    const chapters = B.read?.chapters?.length || 0;
    const topics = B.read?.chapters?.reduce((a,c)=>a+(c.topics?.length||0), 0) || 0;
    const tips = B.tips?.length || 0;
    const stats = [];
    if (chapters) stats.push(`<div><b>${chapters}</b><span>chapters</span></div>`);
    if (topics) stats.push(`<div><b>${topics}</b><span>topics</span></div>`);
    if (tips) stats.push(`<div><b>${tips}</b><span>tips</span></div>`);
    stats.push(`<div><b id="stat-read">${state.read.size}</b><span>read by you</span></div>`);
    const tags = (m.tags || []).slice(0, 10).map(t => `<span>${esc(t)}</span>`).join('');
    $('#hero-content').innerHTML = `
      <div class="hero-eyebrow">${esc(m.genre || 'Interactive Study Guide')} · ${esc(m.authors || '')}${m.year ? `, ${m.year}` : ''}</div>
      <h1>${esc(m.title || 'Book')}</h1>
      ${m.subtitle ? `<p class="hero-lede">${esc(m.subtitle)}</p>` : ''}
      <p class="hero-lede">${html(m.blurb || '')}</p>
      <div class="hero-stats">${stats.join('')}</div>
      ${tags ? `<div class="hero-tags">${tags}</div>` : ''}`;
  }

  // ---------- Mode buttons + TOC ----------
  function renderModeButtons() {
    $('#mode-buttons').innerHTML = enabledViews.map(v =>
      `<button class="mode-btn" data-mode="${v.key}">${v.label}</button>`).join('');
    $$('.mode-btn').forEach(b => b.addEventListener('click', () => setMode(b.dataset.mode)));
  }
  function renderTOC() {
    const chs = B.read?.chapters || [];
    if (!chs.length) { $('#toc').innerHTML = '<div style="font-size:11px;color:var(--text-faint);padding:10px">(No chapter index)</div>'; return; }
    $('#toc').innerHTML = chs.map(c => {
      const total = c.topics?.length || 0;
      const done  = (c.topics||[]).filter(t => state.read.has(t.id)).length;
      return `<div class="toc-chapter" data-ch="${esc(c.id)}">
        <span class="num">${esc(c.num||'')}</span>
        <span>${esc(c.title||'')}</span>
        ${total ? `<span class="check">${done}/${total}</span>` : ''}
      </div>`;
    }).join('');
    $$('.toc-chapter').forEach(el => el.addEventListener('click', () => {
      setMode('read');
      setTimeout(() => {
        const t = document.getElementById('ch-' + el.dataset.ch);
        if (t) t.scrollIntoView({behavior:'smooth', block:'start'});
      }, 30);
    }));
  }
  function renderProgress() {
    const total = (B.read?.chapters||[]).reduce((a,c)=>a+(c.topics?.length||0), 0);
    const done = state.read.size;
    const pct = total ? Math.round(done/total*100) : 0;
    $('#progress-pct').textContent = pct + '%';
    $('#progress-fill').style.width = pct + '%';
    const sr = document.getElementById('stat-read'); if (sr) sr.textContent = done;
    renderTOC();
  }

  // ==========================================================================
  //  READ VIEW
  // ==========================================================================
  function renderRead() {
    const v = $('#view-root');
    const chs = B.read?.chapters || [];
    if (!chs.length) { v.innerHTML = '<p style="color:var(--text-dim)">No chapter data for this book.</p>'; return; }
    v.innerHTML = chs.map(c => `
      <div class="chapter-block" id="ch-${esc(c.id)}">
        <div class="chapter-header">
          <div class="chapter-num" style="${c.color ? `color:${esc(c.color)}` : ''}">${esc(c.num||'')}</div>
          <div class="chapter-meta">
            <h2 class="ch-title">${esc(c.title||'')}</h2>
            <div class="ch-sub">${(c.topics||[]).length} topic${(c.topics||[]).length===1?'':'s'}</div>
          </div>
        </div>
        ${c.intro ? `<p class="chapter-intro">${html(c.intro)}</p>` : ''}
        <div class="topic-grid">
          ${(c.topics||[]).map(t => `
            <div class="topic-card ${state.read.has(t.id)?'read':''}" data-topic="${esc(t.id)}">
              <div class="topic-head"><span class="topic-num">${esc(t.num ? 'TOPIC ' + t.num : '')}</span></div>
              <h3 class="topic-title">${esc(t.title||'')}</h3>
              <p class="topic-hook">${esc(t.hook||'')}</p>
              ${(t.tipRefs||[]).length ? `<div class="topic-tips">${t.tipRefs.map(n => `<span class="tip-pill">Tip ${esc(n)}</span>`).join('')}</div>` : ''}
            </div>`).join('')}
        </div>
      </div>`).join('');
    v.querySelectorAll('.topic-card').forEach(card =>
      card.addEventListener('click', () => openTopic(card.dataset.topic)));
  }

  function findTopic(id) {
    for (const c of B.read?.chapters || []) {
      const t = (c.topics||[]).find(x => x.id === id);
      if (t) return { topic: t, chapter: c };
    }
    return {};
  }

  function openTopic(id) {
    const { topic, chapter } = findTopic(id);
    if (!topic) return;
    const tipBlocks = (topic.tipRefs||[]).map(n => {
      const t = (B.tips||[]).find(x => x.n === n);
      return t ? `<div class="tip-callout"><div class="tip-num">TIP ${esc(n)}</div><div class="tip-text">${esc(t.text)}</div></div>` : '';
    }).join('');
    const cmp = topic.example ? `
      <h3>Before / After</h3>
      <div class="compare">
        <div class="bad"><div class="label">${esc(topic.example.badLabel || 'Anti-pattern')}</div><pre>${esc(topic.example.bad||'')}</pre></div>
        <div class="good"><div class="label">${esc(topic.example.goodLabel || 'Good')}</div><pre>${esc(topic.example.good||'')}</pre></div>
      </div>` : '';
    $('#modal-body').innerHTML = `
      <div class="eyebrow">${esc(chapter.title || '')} · ${esc(topic.num ? 'Topic ' + topic.num : '')}</div>
      <h2>${esc(topic.title||'')}</h2>
      ${topic.hook ? `<p class="one-liner">${esc(topic.hook)}</p>` : ''}
      ${tipBlocks}
      ${topic.why ? `<h3>Why it matters</h3><p>${html(topic.why)}</p>` : ''}
      ${(topic.how||[]).length ? `<h3>How to apply</h3><ul>${topic.how.map(h=>`<li>${html(h)}</li>`).join('')}</ul>` : ''}
      ${cmp}
      ${(topic.antiPatterns||[]).length ? `<h3>Watch out for</h3><ul>${topic.antiPatterns.map(a=>`<li>${esc(a)}</li>`).join('')}</ul>` : ''}
      <div class="mark-read">
        <button id="toggle-read">${state.read.has(topic.id) ? '✓ Marked as read' : 'Mark as understood'}</button>
      </div>`;
    $('#modal').classList.remove('hidden');
    $('#toggle-read')?.addEventListener('click', () => {
      if (state.read.has(topic.id)) state.read.delete(topic.id); else state.read.add(topic.id);
      saveProgress(); renderProgress(); renderRead(); openTopic(topic.id);
    });
  }
  function closeModal(){ $('#modal').classList.add('hidden'); }
  $('#modal-close').addEventListener('click', closeModal);
  $('#modal').addEventListener('click', e => { if (e.target.id === 'modal') closeModal(); });
  document.addEventListener('keydown', e => { if (e.key==='Escape') closeModal(); });

  // ==========================================================================
  //  SUMMARY VIEW — generic section renderers
  // ==========================================================================
  const SECTION_RENDERERS = {
    prose: s => `<div class="sec-prose">${html(s.body||'')}</div>`,
    list: s => {
      const tag = s.ordered ? 'ol' : 'ul';
      return `<div class="sec-list"><${tag}>${(s.items||[]).map(i=>`<li>${html(i)}</li>`).join('')}</${tag}></div>`;
    },
    cards: s => `<div class="sec-cards-grid">${(s.cards||[]).map(c => `
      <div class="sec-card">
        ${c.icon ? `<div class="sec-card-icon">${esc(c.icon)}</div>` : ''}
        <div class="sec-card-name">${esc(c.name||'')}</div>
        <div class="sec-card-desc">${html(c.desc||'')}</div>
      </div>`).join('')}</div>`,
    timeline: s => `<div class="sec-timeline">${(s.events||[]).map(e=>`
      <div class="sec-timeline-event">
        <div class="sec-timeline-date">${esc(e.date||'')}</div>
        <div class="sec-timeline-label">${esc(e.label||'')}</div>
        <div class="sec-timeline-body">${html(e.body||'')}</div>
      </div>`).join('')}</div>`,
    steps: s => `<div class="sec-steps">${(s.steps||[]).map(st=>`
      <div class="sec-step">
        <div class="sec-step-num">${esc(st.num||'')}</div>
        <div>
          <div class="sec-step-title">${esc(st.title||'')}</div>
          <div class="sec-step-body">${html(st.body||'')}</div>
        </div>
      </div>`).join('')}</div>`,
    comparison: s => `<div class="sec-comparison">
      <div><div class="sec-comparison-label">${esc(s.left?.label||'Before')}</div><div class="sec-comparison-body">${html(s.left?.body||'')}</div></div>
      <div><div class="sec-comparison-label">${esc(s.right?.label||'After')}</div><div class="sec-comparison-body">${html(s.right?.body||'')}</div></div>
    </div>`,
    'quote-list': s => `<div class="sec-quote-list">${(s.quotes||[]).map(q=>`
      <div class="sec-quote-list-q"><div class="qt">${esc(q.text||'')}</div>${q.src?`<div class="qs">— ${esc(q.src)}</div>`:''}</div>`).join('')}</div>`,
    definitions: s => `<div class="sec-defs">${(s.items||[]).map(i=>`
      <div class="sec-def"><div class="sec-def-term">${esc(i.term||'')}</div><div class="sec-def-def">${html(i.def||'')}</div></div>`).join('')}</div>`,
    people: s => `<div class="sec-people-grid">${(s.people||[]).map(p=>`
      <div class="sec-person">
        <div class="sec-person-name">${esc(p.name||'')}</div>
        ${p.role?`<div class="sec-person-role">${esc(p.role)}</div>`:''}
        <div class="sec-person-body">${html(p.body||'')}</div>
      </div>`).join('')}</div>`,
    principles: s => `<div class="sec-principles-grid">${(s.items||[]).map(p=>`
      <div class="sec-principle">
        <div class="sec-principle-name">${esc(p.name||'')}</div>
        <div class="sec-principle-line">${html(p.line||'')}</div>
        ${(p.refs||[]).length?`<div class="sec-principle-refs">${p.refs.map(n=>`<span class="sec-principle-ref" data-tipref="${esc(n)}">Tip ${esc(n)}</span>`).join('')}</div>`:''}
      </div>`).join('')}</div>`,
    table: s => `<table class="sec-table">
      <thead><tr>${(s.headers||[]).map(h=>`<th>${esc(h)}</th>`).join('')}</tr></thead>
      <tbody>${(s.rows||[]).map(r=>`<tr>${r.map(c=>`<td>${html(c)}</td>`).join('')}</tr>`).join('')}</tbody>
    </table>`,
    callout: s => `<div class="sec-callout tone-${esc(s.tone||'info')}">
      <div class="sec-callout-title">${esc(s.title||'')}</div>
      <div class="sec-callout-body">${html(s.body||'')}</div>
    </div>`,
  };

  function renderSection(s) {
    const head = s.title ? `<div class="section-head"><h3>${esc(s.title)}</h3>${s.note?`<p>${esc(s.note)}</p>`:''}</div>` : '';
    const r = SECTION_RENDERERS[s.type];
    const body = r ? r(s) : `
      <div class="unknown-section">
        <b>Unknown section type:</b> <code>${esc(s.type)}</code><br>
        The runtime doesn't recognise this section. You may need to regenerate this site with a newer runtime, or update <code>app.js</code>.
        <pre>${esc(JSON.stringify(s, null, 2))}</pre>
      </div>`;
    return `<section class="summary-section">${head}${body}</section>`;
  }

  function renderSummary() {
    const v = $('#view-root');
    const s = B.summary || {};
    const sections = (s.sections || []).map(renderSection).join('');
    const thesis = s.thesis ? `
      <section class="summary-hero">
        <div class="summary-eyebrow">${esc(s.thesis.eyebrow || 'The Summary')}</div>
        <h2>${esc(s.thesis.title || 'Thesis')}</h2>
        <p class="summary-thesis">${html(s.thesis.body || '')}</p>
      </section>` : '';
    v.innerHTML = `${thesis}${sections}`;
    // Tip refs jump to Tips view if present
    v.querySelectorAll('.sec-principle-ref').forEach(el => {
      el.addEventListener('click', () => {
        const n = +el.dataset.tipref;
        const tip = (B.tips||[]).find(t => t.n === n);
        if (tip && tip.topic) openTopic(tip.topic);
      });
    });
  }

  // ==========================================================================
  //  VALUES VIEW
  // ==========================================================================
  function renderValues() {
    const v = $('#view-root');
    const vl = B.values || {};
    const themes = vl.themes || [];
    const nav = themes.map(t => `<button class="values-nav-chip" data-theme="${esc(t.id)}" style="--theme-color:${esc(t.color||'var(--accent)')}"><span class="values-nav-dot"></span><span>${esc(t.title||'')}</span></button>`).join('');
    const body = themes.map(t => `
      <section class="values-theme" id="vtheme-${esc(t.id)}" style="--theme-color:${esc(t.color||'var(--accent)')}">
        <header class="values-theme-head">
          <div class="values-theme-bar"></div>
          <div>
            <h3>${esc(t.title||'')}</h3>
            ${t.subtitle?`<p>${esc(t.subtitle)}</p>`:''}
          </div>
        </header>
        <div class="quote-grid">${(t.quotes||[]).map((q,i)=>`
          <figure class="quote-card ${i===0?'is-lead':''}">
            <div class="quote-mark">"</div>
            <blockquote class="quote-text">${esc(q.text||'')}</blockquote>
            <figcaption class="quote-meta">
              ${q.src?`<span class="quote-src">${esc(q.src)}</span>`:''}
              ${q.context?`<span class="quote-context">${esc(q.context)}</span>`:''}
            </figcaption>
          </figure>`).join('')}</div>
      </section>`).join('');
    v.innerHTML = `
      <section class="values-hero">
        <div class="summary-eyebrow">Values &amp; Wisdom</div>
        <h2>Lines that stay with you</h2>
        ${vl.intro?`<p class="values-intro">${html(vl.intro)}</p>`:''}
      </section>
      <nav class="values-nav">${nav}</nav>
      <div class="values-themes">${body}</div>`;
    v.querySelectorAll('.values-nav-chip').forEach(c => c.addEventListener('click', () => {
      const el = v.querySelector(`#vtheme-${c.dataset.theme}`);
      if (el) el.scrollIntoView({behavior:'smooth', block:'start'});
    }));
  }

  // ==========================================================================
  //  QUOTES VIEW (full CRUD)
  // ==========================================================================
  function renderQuotes() {
    const v = $('#view-root');
    let userQuotes = loadArr(STORE_USER_Q);
    const favs = loadSet(STORE_FAV_Q);
    let overrides = loadObj(STORE_OVR_Q);
    let hidden = loadSet(STORE_HIDE_Q);
    let filter = 'all';
    let featured = null;
    let history = [];

    const qid = q => q.id || 'c:' + (q.text||'').slice(0,60);
    const collect = () => {
      const curated = (Q||[]).map(q => {
        const id = qid(q);
        const ov = overrides[id];
        return { ...q, id, _kind:'curated', _edited:!!ov, _hidden:hidden.has(id),
                 text: ov?ov.text:q.text, src: ov?ov.src:q.src };
      });
      const mine = userQuotes.map(q => ({...q, _kind:'mine'}));
      return [...curated, ...mine];
    };
    const applyFilter = all => {
      if (filter==='hidden') return all.filter(q => q._kind==='curated' && q._hidden);
      const visible = all.filter(q => !q._hidden);
      if (filter==='curated') return visible.filter(q => q._kind==='curated');
      if (filter==='mine')    return visible.filter(q => q._kind==='mine');
      if (filter==='favs')    return visible.filter(q => favs.has(qid(q)));
      return visible;
    };
    const pick = () => {
      const pool = collect();
      if (!pool.length) return null;
      const maxH = Math.max(1, Math.min(12, Math.floor(pool.length/2)));
      history = history.slice(-maxH);
      let cands = pool.filter(q => !history.includes(qid(q)));
      if (!cands.length) { history = []; cands = pool; }
      const c = cands[Math.floor(Math.random()*cands.length)];
      history.push(qid(c));
      return c;
    };

    function paint() {
      const all = collect();
      const shown = applyFilter(all);
      const vis = all.filter(q => !q._hidden);
      const counts = {
        all: vis.length,
        curated: vis.filter(q=>q._kind==='curated').length,
        mine: vis.filter(q=>q._kind==='mine').length,
        favs: vis.filter(q=>favs.has(qid(q))).length,
        hidden: all.filter(q=>q._hidden).length,
      };
      const spot = featured ? `
        <section class="quote-spotlight">
          <div class="spot-eyebrow"><span class="spot-pulse"></span>Featured<button class="spot-dismiss" id="spot-dismiss">×</button></div>
          <blockquote class="spot-text">${esc(featured.text||'')}</blockquote>
          ${featured.src?`<div class="spot-src">— ${esc(featured.src)}</div>`:''}
          <div class="spot-actions">
            <button class="spot-btn" id="spot-next">🎲 Another one</button>
            <button class="spot-btn" id="spot-fav">${favs.has(qid(featured))?'★ Favorited':'☆ Favorite'}</button>
            <button class="spot-btn" id="spot-copy">⧉ Copy</button>
          </div>
        </section>` : '';
      const filters = `
        <div class="quotes-filters">
          <button class="qfilter ${filter==='all'?'active':''}" data-f="all">All <span class="qfilter-count">${counts.all}</span></button>
          <button class="qfilter ${filter==='curated'?'active':''}" data-f="curated">Curated <span class="qfilter-count">${counts.curated}</span></button>
          <button class="qfilter ${filter==='mine'?'active':''}" data-f="mine">Mine <span class="qfilter-count">${counts.mine}</span></button>
          <button class="qfilter ${filter==='favs'?'active':''}" data-f="favs">★ Favorites <span class="qfilter-count">${counts.favs}</span></button>
          ${counts.hidden?`<button class="qfilter ${filter==='hidden'?'active':''}" data-f="hidden">🗑 Hidden <span class="qfilter-count">${counts.hidden}</span></button>`:''}
          <div class="qfilter-actions">
            <button class="qf-action" id="q-shuffle">🎲 Shuffle</button>
            <button class="qf-action" id="q-add-toggle">+ Add your own</button>
          </div>
        </div>`;
      const form = `
        <form class="quote-add-form hidden" id="q-add-form">
          <div class="qf-form-title" id="qf-form-title">Add a new quote</div>
          <div class="qf-field"><label>Quote</label><textarea id="qf-text" rows="3" maxlength="500" required placeholder="The line worth remembering…"></textarea></div>
          <div class="qf-field"><label>Source (optional)</label><input id="qf-src" type="text" maxlength="120" placeholder="Author, book, year, or leave blank"/></div>
          <div class="qf-actions"><button type="button" class="qf-cancel" id="qf-cancel">Cancel</button><button type="submit" class="qf-save" id="qf-save">Save quote</button></div>
        </form>`;
      const cards = shown.length === 0
        ? `<div class="quotes-empty"><div class="quotes-empty-icon">"</div><div class="quotes-empty-title">No quotes ${filter!=='all'?'in this filter':'yet'}</div><small>${filter==='mine'?'Click "Add your own" to save a line you love.':filter==='favs'?'Hit the ★ on any quote to pin it here.':filter==='hidden'?'Hidden curated quotes can be restored here.':''}</small></div>`
        : shown.map(q => {
            const id = qid(q);
            const isFav = favs.has(id), isMine = q._kind==='mine', isEd = q._edited, isHid = q._hidden;
            const cls = ['qcard', isMine&&'is-mine', isEd&&'is-edited', isHid&&'is-hidden-card'].filter(Boolean).join(' ');
            return `<figure class="${cls}" data-id="${esc(id)}">
              <div class="qcard-mark">"</div>
              <blockquote class="qcard-text">${esc(q.text||'')}</blockquote>
              ${q.src?`<figcaption class="qcard-src">— ${esc(q.src)}</figcaption>`:''}
              <div class="qcard-actions">
                ${isHid ? `<button class="qcard-btn qcard-restore" data-a="restore">↺ Restore</button>` : `
                  <button class="qcard-btn qcard-fav ${isFav?'active':''}" data-a="fav">${isFav?'★':'☆'}</button>
                  <button class="qcard-btn" data-a="copy">⧉</button>
                  <button class="qcard-btn" data-a="edit">✎</button>
                  ${isEd?`<button class="qcard-btn" data-a="revert" title="Revert to original">↺</button>`:''}
                  <button class="qcard-btn qcard-del" data-a="delete">✕</button>`}
              </div>
              ${isMine?'<span class="qcard-badge badge-mine">Yours</span>':''}
              ${isEd?'<span class="qcard-badge badge-edited">Edited</span>':''}
            </figure>`;
          }).join('');
      v.innerHTML = `
        <section class="quotes-hero">
          <div class="summary-eyebrow">Quotes</div>
          <h2>Lines worth keeping</h2>
          <p class="values-intro">A gallery of the book's most memorable lines — plus yours. ★ to favorite, ⧉ to copy, or add your own.</p>
        </section>
        ${spot}${filters}${form}
        <div class="quotes-grid">${cards}</div>`;
      bind();
    }

    function bind() {
      v.querySelectorAll('.qfilter').forEach(b => b.addEventListener('click', () => { filter = b.dataset.f; paint(); }));
      const form = $('#q-add-form'), title = $('#qf-form-title'), saveBtn = $('#qf-save');
      const resetForm = () => { form.reset(); form.classList.add('hidden'); delete form.dataset.editingId; delete form.dataset.editingKind; title.textContent = 'Add a new quote'; saveBtn.textContent='Save quote'; };
      $('#q-add-toggle').addEventListener('click', () => {
        const willOpen = form.classList.contains('hidden');
        if (willOpen) { resetForm(); form.classList.remove('hidden'); $('#qf-text').focus(); }
        else form.classList.add('hidden');
      });
      $('#qf-cancel').addEventListener('click', resetForm);
      form.addEventListener('submit', e => {
        e.preventDefault();
        const text = $('#qf-text').value.trim(), src = $('#qf-src').value.trim();
        if (!text) return;
        const editId = form.dataset.editingId, kind = form.dataset.editingKind;
        if (editId && kind==='mine') { userQuotes = userQuotes.map(q => q.id===editId?{...q,text,src}:q); saveArr(STORE_USER_Q, userQuotes); }
        else if (editId && kind==='curated') { overrides[editId] = {text,src}; saveObj(STORE_OVR_Q, overrides); }
        else { userQuotes.push({id:'u:'+Date.now()+':'+Math.random().toString(36).slice(2,6), text, src}); saveArr(STORE_USER_Q, userQuotes); filter='mine'; }
        resetForm(); paint();
      });
      $('#q-shuffle').addEventListener('click', () => { const n = pick(); if (n) { featured = n; paint(); } });
      v.querySelector('#spot-next')?.addEventListener('click', () => { const n = pick(); if (n) { featured = n; paint(); } });
      v.querySelector('#spot-dismiss')?.addEventListener('click', () => { featured = null; paint(); });
      v.querySelector('#spot-fav')?.addEventListener('click', () => {
        if (!featured) return;
        const id = qid(featured);
        if (favs.has(id)) favs.delete(id); else favs.add(id);
        saveSet(STORE_FAV_Q, favs); paint();
      });
      v.querySelector('#spot-copy')?.addEventListener('click', () => {
        if (!featured) return;
        const s = featured.src ? `"${featured.text}"\n— ${featured.src}` : `"${featured.text}"`;
        navigator.clipboard.writeText(s).catch(()=>{});
      });
      v.querySelectorAll('.qcard').forEach(card => {
        const id = card.dataset.id;
        card.querySelectorAll('.qcard-btn').forEach(b => b.addEventListener('click', e => {
          e.stopPropagation();
          const a = b.dataset.a;
          const q = collect().find(x => qid(x)===id);
          if (!q) return;
          const isMine = q._kind==='mine';
          if (a==='fav') { if (favs.has(id)) favs.delete(id); else favs.add(id); saveSet(STORE_FAV_Q, favs); paint(); }
          if (a==='copy') { const s=q.src?`"${q.text}"\n— ${q.src}`:`"${q.text}"`; navigator.clipboard.writeText(s).then(()=>{b.textContent='✓';setTimeout(()=>b.textContent='⧉',1200);}).catch(()=>{}); }
          if (a==='edit') { $('#qf-text').value=q.text; $('#qf-src').value=q.src||''; form.dataset.editingId=id; form.dataset.editingKind=isMine?'mine':'curated'; title.textContent=isMine?'Edit your quote':'Edit curated quote (revertible)'; saveBtn.textContent='Save changes'; form.classList.remove('hidden'); $('#qf-text').focus(); }
          if (a==='revert') { if (!confirm('Revert to the original?')) return; delete overrides[id]; saveObj(STORE_OVR_Q, overrides); paint(); }
          if (a==='delete') { if (isMine) { if (!confirm('Delete permanently?')) return; userQuotes = userQuotes.filter(x=>x.id!==id); saveArr(STORE_USER_Q, userQuotes); favs.delete(id); saveSet(STORE_FAV_Q, favs); } else { hidden.add(id); saveSet(STORE_HIDE_Q, hidden); } paint(); }
          if (a==='restore') { hidden.delete(id); saveSet(STORE_HIDE_Q, hidden); paint(); }
        }));
      });
    }
    paint();
  }

  // ==========================================================================
  //  MAP VIEW
  // ==========================================================================
  function renderMap() {
    const v = $('#view-root');
    const m = B.map || {};
    const archetypes = m.archetypes || [];
    if (!archetypes.length) { v.innerHTML = '<p style="color:var(--text-dim)">No map data.</p>'; return; }

    const stored = loadObj(STORE_MAP);
    let currentArche = stored.archetype && archetypes.find(a=>a.id===stored.archetype) ? stored.archetype : (m.primary || archetypes[0].id);
    let currentLayout = stored.layout || 'constellation';
    let positions = {}; // { id -> {x,y} }
    let activeArche = null;
    let selectedId = null;
    let hoverId = null;
    let isDragging = false;

    const W = 1200, H = 780;
    const LAYOUTS = {
      constellation: 'Constellation',
      chapter: 'By Group',
      flow: 'Dependency Flow',
      radial: 'Radial Rings',
    };

    function computeLayout(arche, layout) {
      const nodes = arche.nodes || [], edges = arche.edges || [];
      const adj = {}; nodes.forEach(n => adj[n.id] = new Set());
      edges.forEach(e => { if (adj[e.from]) adj[e.from].add(e.to); if (adj[e.to]) adj[e.to].add(e.from); });
      const out = {};
      if (layout === 'constellation') {
        // Use stored positions on nodes if present; else force-ish distribution
        nodes.forEach((n, i) => {
          if (typeof n.x === 'number' && typeof n.y === 'number') { out[n.id] = {x:n.x, y:n.y}; return; }
          const core = nodes.find(x => x.core);
          const isCore = n.core;
          if (isCore) {
            const coreNodes = nodes.filter(x => x.core);
            const ci = coreNodes.indexOf(n);
            out[n.id] = { x: W/2 + (ci - (coreNodes.length-1)/2) * 140, y: H/2 };
          } else {
            const ring = 0.8 * Math.min(W, H) / 2;
            const angle = (i / Math.max(1, nodes.length)) * 2 * Math.PI;
            out[n.id] = { x: W/2 + Math.cos(angle) * ring, y: H/2 + Math.sin(angle) * ring * 0.72 };
          }
        });
      } else if (layout === 'chapter') {
        const groups = {};
        nodes.forEach(n => { const g = n.group ?? 0; (groups[g] = groups[g] || []).push(n); });
        const keys = Object.keys(groups).map(Number).sort((a,b)=>a-b);
        const colW = (W - 180) / Math.max(1, keys.length - 1 || 1);
        keys.forEach((g, gi) => {
          const gn = groups[g];
          const x = 90 + gi * colW;
          const step = gn.length > 1 ? (H - 140) / (gn.length - 1) : 0;
          gn.forEach((n, i) => out[n.id] = { x, y: gn.length===1 ? H/2 : 70 + i*step });
        });
      } else if (layout === 'flow' || layout === 'radial') {
        // BFS from core(s), else from first node
        const dist = {};
        const roots = nodes.filter(n => n.core).map(n => n.id);
        const q = (roots.length ? roots : [nodes[0].id]).map(id => [id, 0]);
        while (q.length) {
          const [id, d] = q.shift();
          if (dist[id] != null) continue;
          dist[id] = d;
          (adj[id] || new Set()).forEach(nb => { if (dist[nb] == null) q.push([nb, d+1]); });
        }
        nodes.forEach(n => { if (dist[n.id] == null) dist[n.id] = 3; });
        if (layout === 'flow') {
          const cols = {};
          nodes.forEach(n => { (cols[dist[n.id]] = cols[dist[n.id]]||[]).push(n); });
          const depths = Object.keys(cols).map(Number).sort((a,b)=>a-b);
          const maxD = depths[depths.length-1];
          const colW = (W - 240) / Math.max(1, maxD || 1);
          depths.forEach(d => {
            const cn = cols[d];
            const x = 120 + d * colW;
            const step = cn.length > 1 ? (H - 140) / (cn.length - 1) : 0;
            cn.forEach((n, i) => out[n.id] = { x, y: cn.length===1 ? H/2 : 70 + i*step });
          });
        } else {
          const rings = {};
          nodes.forEach(n => { (rings[dist[n.id]] = rings[dist[n.id]]||[]).push(n); });
          const depths = Object.keys(rings).map(Number).sort((a,b)=>a-b);
          const cx = W/2, cy = H/2;
          const ringGap = Math.min(W, H) * 0.28;
          depths.forEach((d, di) => {
            if (d === 0) {
              rings[d].forEach((n, i) => out[n.id] = { x: cx + (i - (rings[d].length-1)/2) * 140, y: cy });
            } else {
              const R = ringGap * di * 0.95;
              rings[d].forEach((n, i) => {
                const theta = (i / rings[d].length) * 2*Math.PI - Math.PI/2 + di * 0.2;
                out[n.id] = {
                  x: Math.max(70, Math.min(W-70, cx + Math.cos(theta) * R)),
                  y: Math.max(60, Math.min(H-60, cy + Math.sin(theta) * R * 0.78)),
                };
              });
            }
          });
        }
      }
      // Apply user overrides from storage
      const saved = (stored.positions && stored.positions[arche.id] && stored.positions[arche.id][layout]) || {};
      return { ...out, ...saved };
    }

    function getArche(id) { return archetypes.find(a => a.id === id) || archetypes[0]; }

    function paint() {
      activeArche = getArche(currentArche);
      positions = computeLayout(activeArche, currentLayout);
      const arcBtns = archetypes.map(a => `<button class="toolbar-btn ${a.id===currentArche?'active':''}" data-arche="${esc(a.id)}">${esc(a.label||a.id)}</button>`).join('');
      const layoutBtns = Object.entries(LAYOUTS).map(([k,l]) => `<button class="toolbar-btn ${k===currentLayout?'active':''}" data-layout="${k}">${l}</button>`).join('');
      const groups = activeArche.groups || [];
      const legend = groups.length ? groups.map(g => `<button class="legend-chip" data-group="${esc(g.id)}" style="color:${esc(g.color||'var(--accent)')}"><span class="legend-dot"></span>${esc(g.label||g.id)}</button>`).join('') : '';
      v.innerHTML = `
        <div class="map-header">
          <div>
            <h2>Concept Map</h2>
            <p class="map-intro">${esc(activeArche.description || 'Drag nodes · click to pin details · switch archetypes and layouts.')}</p>
          </div>
        </div>
        <div class="map-toolbar">
          <div class="toolbar-group"><span class="toolbar-label">Map</span>${arcBtns}</div>
          <div class="toolbar-group"><span class="toolbar-label">Layout</span>${layoutBtns}</div>
          <div class="map-toolbar-right">
            ${legend?`<div class="map-legend">${legend}</div>`:''}
            <button class="map-reset-btn" id="map-reset">↺ Reset</button>
          </div>
        </div>
        <div class="map-canvas">
          <svg class="concept-map" viewBox="0 0 ${W} ${H}" preserveAspectRatio="xMidYMid meet">
            <defs>
              <marker id="arrow-weak" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse">
                <path d="M 0 0 L 10 5 L 0 10 z" class="arrow arrow-weak"/>
              </marker>
              <marker id="arrow-strong" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse">
                <path d="M 0 0 L 10 5 L 0 10 z" class="arrow arrow-strong"/>
              </marker>
            </defs>
            <g class="layer-edges"></g>
            <g class="layer-nodes"></g>
          </svg>
          <aside class="map-inspector" id="map-inspector"></aside>
        </div>`;

      const svg = v.querySelector('svg.concept-map');
      const layerEdges = svg.querySelector('.layer-edges');
      const layerNodes = svg.querySelector('.layer-nodes');
      const inspector = v.querySelector('#map-inspector');

      function nodeW(n){ return Math.max(110, (n.label||'').length * 8.2 + 30); }
      function nodeH(n){ return n.core ? 52 : 42; }
      function edgePath(a, b, pa, pb) {
        const aw = nodeW(a)/2, ah = nodeH(a)/2;
        const bw = nodeW(b)/2, bh = nodeH(b)/2;
        const dx = pb.x-pa.x, dy = pb.y-pa.y;
        const ta = Math.min(aw / Math.abs(dx||1), ah / Math.abs(dy||1));
        const tb = Math.min(bw / Math.abs(dx||1), bh / Math.abs(dy||1));
        const x1 = pa.x + dx*ta, y1 = pa.y + dy*ta, x2 = pb.x - dx*tb, y2 = pb.y - dy*tb;
        const mx = (x1+x2)/2, my = (y1+y2)/2;
        const len = Math.hypot(x2-x1, y2-y1) || 1;
        const curve = Math.min(28, len * 0.12);
        const nx = -(y2-y1)/len, ny = (x2-x1)/len;
        const cx = mx + nx*curve, cy = my + ny*curve;
        return { d: `M ${x1} ${y1} Q ${cx} ${cy} ${x2} ${y2}`, mx: cx, my: cy };
      }
      const getNode = id => (activeArche.nodes||[]).find(n => n.id === id);
      const adjacencyFor = id => {
        const out = new Set();
        (activeArche.edges||[]).forEach(e => { if (e.from===id) out.add(e.to); if (e.to===id) out.add(e.from); });
        return out;
      };

      function drawEdges() {
        layerEdges.innerHTML = (activeArche.edges||[]).map(e => {
          const a = getNode(e.from), b = getNode(e.to);
          if (!a || !b) return '';
          const pa = positions[e.from], pb = positions[e.to];
          if (!pa || !pb) return '';
          const { d, mx, my } = edgePath(a, b, pa, pb);
          const cls = `edge ${e.strong?'edge-strong':'edge-weak'}`;
          const marker = e.strong ? 'arrow-strong' : 'arrow-weak';
          const labelLen = (e.label||'').length * 6.2 + 12;
          return `<g class="edge-group" data-from="${esc(e.from)}" data-to="${esc(e.to)}">
            <path class="${cls}" d="${d}" fill="none" marker-end="url(#${marker})"/>
            ${e.label?`<rect class="edge-label-bg" x="${mx-labelLen/2}" y="${my-9}" width="${labelLen}" height="16" rx="8"/>
            <text class="edge-label" x="${mx}" y="${my+2}" text-anchor="middle">${esc(e.label)}</text>`:''}
          </g>`;
        }).join('');
      }
      function drawNodes() {
        layerNodes.innerHTML = (activeArche.nodes||[]).map(n => {
          const w = nodeW(n), h = nodeH(n);
          const p = positions[n.id] || {x:W/2, y:H/2};
          const gColor = (activeArche.groups||[]).find(g => g.id === n.group)?.color;
          const strokeStyle = gColor ? `stroke:${gColor}` : '';
          return `<g class="node ${n.core?'node-core':''}" data-id="${esc(n.id)}" transform="translate(${p.x-w/2},${p.y-h/2})" tabindex="0">
            <rect class="node-rect" width="${w}" height="${h}" rx="${n.core?14:12}" style="${strokeStyle}"/>
            <text class="node-label" x="${w/2}" y="${h/2+1}">${esc(n.label||'')}</text>
          </g>`;
        }).join('');
        bindNodes();
      }

      function applyHL() {
        const active = hoverId || selectedId;
        svg.classList.toggle('is-highlighting', !!active);
        if (!active) {
          svg.querySelectorAll('.is-active,.is-neighbour,.is-selected').forEach(el => el.classList.remove('is-active','is-neighbour','is-selected'));
          if (selectedId) svg.querySelector(`.node[data-id="${selectedId}"]`)?.classList.add('is-selected');
          return;
        }
        const nbs = adjacencyFor(active);
        svg.querySelectorAll('.node').forEach(g => {
          const id = g.dataset.id;
          g.classList.toggle('is-active', id===active);
          g.classList.toggle('is-neighbour', nbs.has(id));
          g.classList.toggle('is-selected', id===selectedId);
        });
        svg.querySelectorAll('.edge-group').forEach(g => {
          g.classList.toggle('is-active', g.dataset.from===active || g.dataset.to===active);
        });
      }

      function showInspector(node, pinned) {
        const nbs = [...adjacencyFor(node.id)].map(nid => {
          const nb = getNode(nid);
          if (!nb) return '';
          return `<button class="neighbour-chip" data-id="${esc(nid)}">${esc(nb.label||'')}</button>`;
        }).join('');
        inspector.innerHTML = `
          <div class="inspector-card">
            <div class="inspector-head">
              <div class="inspector-tag">${esc(node.tag || '')}</div>
              ${pinned?`<button class="inspector-unpin" id="unpin">×</button>`:''}
            </div>
            <div class="inspector-title">${esc(node.label||'')}</div>
            ${node.tagline?`<div class="inspector-tagline">${esc(node.tagline)}</div>`:''}
            ${nbs?`<div class="inspector-section-title">Connected</div><div class="inspector-neighbours">${nbs}</div>`:''}
            ${node.topic?`<button class="inspector-open" data-topic="${esc(node.topic)}">Read full topic →</button>`:''}
          </div>`;
        inspector.querySelector('.inspector-open')?.addEventListener('click', e => openTopic(e.currentTarget.dataset.topic));
        inspector.querySelector('#unpin')?.addEventListener('click', () => { selectedId = null; emptyInspector(); applyHL(); });
        inspector.querySelectorAll('.neighbour-chip').forEach(b => b.addEventListener('click', () => selectNode(b.dataset.id)));
      }
      function emptyInspector() {
        inspector.innerHTML = `<div class="inspector-empty">
          <div class="inspector-empty-icon">◈</div>
          <div class="inspector-empty-title">Explore the map</div>
          <small>Hover a concept for a quick look. Click to pin its details here.</small>
          <div class="inspector-hints">
            <div><b>Drag</b> nodes to rearrange</div>
            <div><b>Switch maps &amp; layouts</b> above</div>
          </div>
        </div>`;
      }
      function selectNode(id) { selectedId = id; const n = getNode(id); if (n) showInspector(n, true); applyHL(); }

      function savePositions() {
        const all = stored.positions || {};
        all[activeArche.id] = all[activeArche.id] || {};
        all[activeArche.id][currentLayout] = positions;
        saveObj(STORE_MAP, { archetype: currentArche, layout: currentLayout, positions: all });
      }
      function ptInSvg(e) {
        const pt = svg.createSVGPoint(); pt.x = e.clientX; pt.y = e.clientY;
        return pt.matrixTransform(svg.getScreenCTM().inverse());
      }

      function bindNodes() {
        svg.querySelectorAll('.node').forEach(g => {
          const id = g.dataset.id;
          const node = getNode(id);
          g.addEventListener('pointerenter', () => {
            if (isDragging) return;
            hoverId = id;
            if (!selectedId) showInspector(node, false);
            applyHL();
          });
          g.addEventListener('pointerleave', () => {
            if (isDragging) return;
            hoverId = null;
            if (!selectedId) emptyInspector();
            applyHL();
          });
          g.addEventListener('pointerdown', e => {
            if (e.button !== 0) return;
            e.preventDefault();
            const start = ptInSvg(e), origin = { ...positions[id] };
            let moved = false;
            g.setPointerCapture(e.pointerId);
            g.classList.add('is-dragging');
            isDragging = true;
            const move = ev => {
              const p = ptInSvg(ev);
              const dx = p.x-start.x, dy = p.y-start.y;
              if (Math.abs(dx)+Math.abs(dy) > 3) moved = true;
              positions[id] = { x: Math.max(60, Math.min(W-60, origin.x+dx)), y: Math.max(45, Math.min(H-45, origin.y+dy)) };
              const w = nodeW(node), h = nodeH(node);
              g.setAttribute('transform', `translate(${positions[id].x-w/2},${positions[id].y-h/2})`);
              drawEdges();
            };
            const up = () => {
              g.releasePointerCapture(e.pointerId);
              g.removeEventListener('pointermove', move); g.removeEventListener('pointerup', up); g.removeEventListener('pointercancel', up);
              g.classList.remove('is-dragging'); isDragging = false;
              if (moved) savePositions();
              else selectNode(id);
            };
            g.addEventListener('pointermove', move);
            g.addEventListener('pointerup', up);
            g.addEventListener('pointercancel', up);
          });
        });
        svg.addEventListener('pointerdown', e => {
          if (e.target === svg || e.target.closest('.layer-edges')) {
            selectedId = null; hoverId = null; emptyInspector(); applyHL();
          }
        });
      }

      // Toolbar
      v.querySelectorAll('.toolbar-btn[data-arche]').forEach(b => b.addEventListener('click', () => {
        currentArche = b.dataset.arche;
        stored.archetype = currentArche; saveObj(STORE_MAP, stored);
        selectedId = null; paint();
      }));
      v.querySelectorAll('.toolbar-btn[data-layout]').forEach(b => b.addEventListener('click', () => {
        currentLayout = b.dataset.layout;
        stored.layout = currentLayout; saveObj(STORE_MAP, stored);
        paint();
      }));
      $('#map-reset').addEventListener('click', () => {
        const all = stored.positions || {};
        if (all[activeArche.id]) delete all[activeArche.id][currentLayout];
        saveObj(STORE_MAP, { ...stored, positions: all });
        paint();
      });
      v.querySelectorAll('.legend-chip').forEach(c => c.addEventListener('click', () => {
        const gid = c.dataset.group;
        const active = c.classList.toggle('active');
        v.querySelectorAll('.legend-chip').forEach(o => { if (o!==c) o.classList.remove('active'); });
        if (!active) { svg.classList.remove('is-filtering'); svg.querySelectorAll('.is-dim').forEach(el=>el.classList.remove('is-dim')); return; }
        svg.classList.add('is-filtering');
        svg.querySelectorAll('.node').forEach(g => {
          const n = getNode(g.dataset.id);
          g.classList.toggle('is-dim', String(n?.group) !== gid);
        });
        svg.querySelectorAll('.edge-group').forEach(g => {
          const a = getNode(g.dataset.from), b = getNode(g.dataset.to);
          g.classList.toggle('is-dim', String(a?.group)!==gid && String(b?.group)!==gid);
        });
      }));

      drawEdges(); drawNodes(); emptyInspector();
    }

    paint();
  }

  // ==========================================================================
  //  TIPS VIEW
  // ==========================================================================
  function renderTips() {
    const v = $('#view-root');
    const tips = B.tips || [];
    v.innerHTML = `
      <h2>💡 Tips</h2>
      <p class="map-intro" style="margin-bottom:16px">Every enumerated tip in the book. Click to jump to its topic.</p>
      <div class="tips-filter">
        <input id="tip-search" placeholder="Search tips…"/>
      </div>
      <div class="tips-grid" id="tips-grid"></div>`;
    const paint = () => {
      const q = $('#tip-search').value.toLowerCase();
      $('#tips-grid').innerHTML = tips.filter(t => !q || t.text.toLowerCase().includes(q) || String(t.n).includes(q)).map(t => `
        <div class="tip-card" data-topic="${esc(t.topic||'')}">
          <div class="tip-id">TIP ${esc(t.n)}</div>
          <div class="tip-title">${esc(t.text)}</div>
        </div>`).join('') || '<div style="color:var(--text-dim)">No matches.</div>';
      v.querySelectorAll('.tip-card').forEach(c => c.addEventListener('click', () => {
        if (c.dataset.topic) openTopic(c.dataset.topic);
      }));
    };
    $('#tip-search').addEventListener('input', paint);
    paint();
  }

  // ==========================================================================
  //  QUIZ VIEW
  // ==========================================================================
  const qstate = { i: 0, score: 0, answered: false };
  function renderQuiz() {
    const v = $('#view-root');
    const quiz = B.quiz || [];
    if (qstate.i >= quiz.length) {
      v.innerHTML = `
        <h2>🎯 Quiz complete</h2>
        <div class="quiz-box">
          <div class="quiz-score">${qstate.score} / ${quiz.length}</div>
          <div class="quiz-controls" style="justify-content:center">
            <button id="quiz-restart">Try again</button>
          </div>
        </div>`;
      $('#quiz-restart').addEventListener('click', () => { qstate.i=0; qstate.score=0; qstate.answered=false; renderQuiz(); });
      return;
    }
    const q = quiz[qstate.i];
    v.innerHTML = `
      <h2>🎯 Quiz</h2>
      <div class="quiz-box">
        <div class="quiz-progress"><span>Question ${qstate.i+1} of ${quiz.length}</span><span>Score ${qstate.score}</span></div>
        <div class="quiz-q">${esc(q.q)}</div>
        <div class="quiz-opts">${(q.opts||[]).map((o,i)=>`<button class="quiz-opt" data-i="${i}">${esc(o)}</button>`).join('')}</div>
        <div id="quiz-explain" style="display:none"></div>
        <div class="quiz-controls" id="quiz-controls" style="display:none"><button id="quiz-next">Next →</button></div>
      </div>`;
    v.querySelectorAll('.quiz-opt').forEach(b => b.addEventListener('click', () => {
      if (qstate.answered) return;
      qstate.answered = true;
      const i = +b.dataset.i;
      v.querySelectorAll('.quiz-opt').forEach((o, idx) => {
        if (idx === q.correct) o.classList.add('correct');
        else if (idx === i) o.classList.add('wrong');
        o.disabled = true;
      });
      if (i === q.correct) qstate.score++;
      const ex = $('#quiz-explain');
      ex.className = 'quiz-explain'; ex.style.display = 'block'; ex.innerHTML = esc(q.explain||'');
      $('#quiz-controls').style.display = 'flex';
    }));
    v.querySelector('#quiz-next')?.addEventListener('click', () => { qstate.i++; qstate.answered = false; renderQuiz(); });
  }

  // ==========================================================================
  //  SCENARIOS VIEW
  // ==========================================================================
  function renderSim() {
    const v = $('#view-root');
    const sc = B.scenarios || [];
    v.innerHTML = `
      <h2>🧪 Scenarios</h2>
      <p class="map-intro" style="margin-bottom:18px">Click a scenario to see how this book's ideas apply.</p>
      <div class="sim-grid">${sc.map((s,i)=>`
        <div class="sim-card" data-i="${i}">
          <h4>${esc(s.title||'')}</h4>
          <p>${esc(s.desc||'')}</p>
        </div>`).join('')}</div>
      <div id="sim-result"></div>`;
    v.querySelectorAll('.sim-card').forEach(c => c.addEventListener('click', () => {
      const s = sc[+c.dataset.i];
      const applies = (s.applies||[]).map(id => {
        const { topic } = findTopic(id);
        return topic ? `<span data-topic="${esc(id)}">${esc(topic.title||'')}</span>` : '';
      }).join('');
      const r = $('#sim-result');
      r.innerHTML = `<div class="sim-result">
        <h3>${esc(s.title||'')}</h3>
        <p style="color:var(--text-dim)">${esc(s.desc||'')}</p>
        <div style="margin-top:16px"><b>Verdict</b></div>
        <p>${html(s.verdict||'')}</p>
        ${applies?`<div class="applies">${applies}</div>`:''}
      </div>`;
      r.scrollIntoView({behavior:'smooth', block:'start'});
      r.querySelectorAll('span[data-topic]').forEach(el => el.addEventListener('click', () => openTopic(el.dataset.topic)));
    }));
  }

  // ==========================================================================
  //  Mode dispatch
  // ==========================================================================
  const RENDERERS = {
    read: renderRead, summary: renderSummary, values: renderValues,
    quotes: renderQuotes, map: renderMap, tips: renderTips,
    quiz: renderQuiz, sim: renderSim,
  };
  function setMode(m) {
    if (!enabledViews.find(v => v.key === m)) m = enabledViews[0]?.key || 'summary';
    state.mode = m;
    $$('.mode-btn').forEach(b => b.classList.toggle('active', b.dataset.mode===m));
    const fn = RENDERERS[m];
    if (fn) fn(); else $('#view-root').innerHTML = `<p>No renderer for "${esc(m)}".</p>`;
    window.scrollTo({top:0, behavior:'smooth'});
  }

  // Theme toggle
  function applyTheme(t) {
    document.documentElement.setAttribute('data-theme', t);
    localStorage.setItem(STORE_THEME, t);
    const dark = t === 'dark';
    $('#theme-icon').textContent = dark ? '☀️' : '🌙';
    $('#theme-label').textContent = dark ? 'Light' : 'Dark';
  }
  applyTheme(document.documentElement.getAttribute('data-theme') || 'dark');
  $('#theme-toggle').addEventListener('click', () => applyTheme(document.documentElement.getAttribute('data-theme') === 'dark' ? 'light' : 'dark'));

  $('#reset-progress').addEventListener('click', () => {
    if (!confirm('Reset reading progress?')) return;
    state.read.clear(); saveProgress(); renderProgress();
    if (state.mode === 'read') renderRead();
  });

  // ---------- Init ----------
  renderHero();
  renderModeButtons();
  renderTOC();
  renderProgress();
  // Open the book on Summary by default (Read is second only if chapters exist)
  const initial = enabledViews.find(v => v.key === 'summary')?.key || enabledViews[0]?.key;
  if (initial) setMode(initial);
})();
