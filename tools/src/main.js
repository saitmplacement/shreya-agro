/* Shreya Agro Foods — site script (source). `python3 tools/build.py` minifies it to assets/js/main.js */
(function () {
  'use strict';

  var CFG = window.SHREYA_CONFIG || {};
  var doc = document;
  var body = doc.body;

  function $(sel, ctx) { return (ctx || doc).querySelector(sel); }
  function $$(sel, ctx) { return Array.prototype.slice.call((ctx || doc).querySelectorAll(sel)); }

  /* ---------- Analytics (GA4, only when an ID is configured) ---------- */
  if (CFG.gaId && /^G-[A-Z0-9]+$/.test(CFG.gaId)) {
    window.dataLayer = window.dataLayer || [];
    window.gtag = function () { window.dataLayer.push(arguments); };
    window.gtag('js', new Date());
    window.gtag('config', CFG.gaId);
    var gs = doc.createElement('script');
    gs.async = true;
    gs.src = 'https://www.googletagmanager.com/gtag/js?id=' + CFG.gaId;
    doc.head.appendChild(gs);
  }
  function track(name, params) {
    if (typeof window.gtag === 'function') { window.gtag('event', name, params || {}); }
  }
  if (body.getAttribute('data-product')) {
    track('view_item', { item_name: body.getAttribute('data-product'), item_category: body.getAttribute('data-category') || '' });
  }
  doc.addEventListener('click', function (e) {
    var a = e.target.closest ? e.target.closest('a[href]') : null;
    if (!a) return;
    var href = a.getAttribute('href') || '';
    if (href.indexOf('tel:') === 0) track('phone_click', { link_url: href });
    else if (href.indexOf('mailto:') === 0) track('email_click', { link_url: href });
    else if (href.indexOf('wa.me') > -1 || href.indexOf('whatsapp') > -1) track('whatsapp_click', { link_url: href });
  });

  /* ---------- Mobile navigation ---------- */
  var navToggle = $('#navToggle');
  var mainNav = $('#mainNav');
  function closeNav() {
    if (!mainNav) return;
    mainNav.classList.remove('open');
    if (navToggle) { navToggle.setAttribute('aria-expanded', 'false'); navToggle.setAttribute('aria-label', 'Open menu'); }
  }
  if (navToggle && mainNav) {
    navToggle.addEventListener('click', function () {
      var open = mainNav.classList.toggle('open');
      navToggle.setAttribute('aria-expanded', open ? 'true' : 'false');
      navToggle.setAttribute('aria-label', open ? 'Close menu' : 'Open menu');
    });
    mainNav.addEventListener('click', function (e) { if (e.target.closest('a, button')) closeNav(); });
    doc.addEventListener('click', function (e) {
      if (!mainNav.classList.contains('open')) return;
      if (!e.target.closest('#mainNav') && !e.target.closest('#navToggle')) closeNav();
    });
    window.addEventListener('resize', function () { if (window.innerWidth > 991) closeNav(); });
  }

  /* ---------- Modals ---------- */
  var activeModal = null;
  var lastFocus = null;
  function focusables(root) {
    return $$('a[href], button:not([disabled]), input:not([disabled]):not([type="hidden"]), select, textarea, [tabindex]:not([tabindex="-1"])', root)
      .filter(function (el) { return el.offsetParent !== null; });
  }
  function openModal(modal) {
    if (!modal) return;
    closeChat();
    closeNav();
    lastFocus = doc.activeElement;
    modal.hidden = false;
    body.classList.add('modal-open');
    activeModal = modal;
    var f = focusables(modal.querySelector('.modal-dialog'));
    var firstField = f.filter(function (el) { return /^(INPUT|SELECT|TEXTAREA)$/.test(el.tagName) && !el.closest('.hp'); })[0];
    (firstField || f[0] || modal).focus({ preventScroll: true });
  }
  function closeModal() {
    if (!activeModal) return;
    activeModal.hidden = true;
    body.classList.remove('modal-open');
    activeModal = null;
    if (lastFocus && lastFocus.focus) lastFocus.focus({ preventScroll: true });
  }
  doc.addEventListener('click', function (e) {
    if (e.target.closest('[data-close-modal]')) closeModal();
  });
  doc.addEventListener('keydown', function (e) {
    if (e.key === 'Escape') {
      if (activeModal) closeModal();
      else { closeChat(); closeNav(); }
    }
    if (e.key === 'Tab' && activeModal) {
      var f = focusables(activeModal.querySelector('.modal-dialog'));
      if (!f.length) return;
      var first = f[0], last = f[f.length - 1];
      if (e.shiftKey && doc.activeElement === first) { e.preventDefault(); last.focus(); }
      else if (!e.shiftKey && doc.activeElement === last) { e.preventDefault(); first.focus(); }
    }
  });

  /* ---------- Enquiry modal ---------- */
  var enquiryModal = $('#enquiryModal');
  function setText(id, text) { var el = $(id); if (el) el.textContent = text || ''; }
  function openEnquiry(opts) {
    if (!enquiryModal) return;
    opts = opts || {};
    var form = $('#enquiryForm');
    var dialog = $('.modal-dialog', enquiryModal);
    form.reset();
    resetFormState(form);
    $('#enquiryFormWrap').hidden = false;
    $('#enquirySuccess').hidden = true;

    var hasProduct = !!opts.product;
    var aside = $('#enquiryAside');
    var productField = $('#enquiryProductField');
    var productInput = $('#enquiryProduct');
    var productSelectWrap = $('#enquiryProductSelectWrap');
    var productSelect = $('#enquiryProductSelect');
    dialog.classList.toggle('no-aside', !hasProduct);
    aside.hidden = !hasProduct;
    productField.hidden = !hasProduct;
    productSelectWrap.hidden = hasProduct;
    productSelect.value = '';

    if (hasProduct) {
      setText('#enquiryTitle', 'Interested in this product?');
      setText('#enquiryProductName', opts.product);
      productInput.value = opts.product;
      var img = $('#enquiryAsideImg');
      if (opts.image) { img.src = opts.image; img.alt = 'Shreya Agro Foods ' + opts.product; img.hidden = false; } else { img.hidden = true; }
      setText('#enquiryAsideName', opts.product);
      setText('#enquiryAsideDesc', opts.desc || '');
      var tags = $('#enquiryAsidePacks');
      tags.innerHTML = '';
      (opts.packs || '').split(',').map(function (s) { return s.trim(); }).filter(Boolean).forEach(function (p) {
        var s = doc.createElement('span'); s.textContent = p; tags.appendChild(s);
      });
      setText('#enquiryIntro', 'Share your details and our B2B team will get in touch with you.');
    } else {
      setText('#enquiryTitle', opts.title || 'B2B Product Enquiry');
      productInput.value = '';
      setText('#enquiryIntro', 'Tell us what you are looking for and our B2B team will get in touch with you shortly.');
    }
    $('#enquiryType').value = opts.type || (hasProduct ? 'Product Enquiry' : 'B2B Enquiry');
    openModal(enquiryModal);
    track('enquiry_click', { item_name: opts.product || '', enquiry_type: opts.type || '' });
  }
  doc.addEventListener('click', function (e) {
    var btn = e.target.closest('[data-enquiry]');
    if (!btn) return;
    e.preventDefault();
    openEnquiry({
      product: btn.getAttribute('data-product') || '',
      image: btn.getAttribute('data-image') || '',
      desc: btn.getAttribute('data-desc') || '',
      packs: btn.getAttribute('data-packs') || '',
      type: btn.getAttribute('data-type') || '',
      title: btn.getAttribute('data-title') || ''
    });
  });

  /* ---------- Job application modal ---------- */
  var applyModal = $('#applyModal');
  doc.addEventListener('click', function (e) {
    var btn = e.target.closest('[data-apply]');
    if (!btn || !applyModal) return;
    e.preventDefault();
    var form = $('#applyForm');
    form.reset();
    resetFormState(form);
    $('#applyFormWrap').hidden = false;
    $('#applySuccess').hidden = true;
    var pos = btn.getAttribute('data-apply') || 'General Application';
    setText('#applyPosition', pos);
    $('#applyPositionInput').value = pos;
    openModal(applyModal);
    track('career_apply_click', { job_title: pos });
  });

  /* ---------- Forms ---------- */
  var MOBILE_RE = /^[+]?[0-9][0-9\s-]{7,16}$/;
  var EMAIL_RE = /^[^\s@]+@[^\s@]+\.[^\s@]{2,}$/;

  function fieldError(input, msg) {
    var wrap = input.closest('.field');
    var err = wrap && $('.field-error', wrap);
    if (msg) {
      input.setAttribute('aria-invalid', 'true');
      if (err) { err.textContent = msg; err.hidden = false; }
    } else {
      input.removeAttribute('aria-invalid');
      if (err) { err.textContent = ''; err.hidden = true; }
    }
  }
  function resetFormState(form) {
    $$('input, select, textarea', form).forEach(function (i) { fieldError(i, ''); });
    var st = $('.form-status', form);
    if (st) { st.hidden = true; st.textContent = ''; }
    var btn = $('button[type="submit"]', form);
    if (btn) { btn.disabled = false; if (btn.getAttribute('data-label')) btn.querySelector('.label').textContent = btn.getAttribute('data-label'); }
  }
  function validateField(input) {
    if (input.type === 'hidden' || input.closest('.hp') || input.hidden || input.closest('[hidden]')) return true;
    var v = (input.value || '').trim();
    var msg = '';
    if (input.required && !v) msg = 'This field is required.';
    else if (v && input.type === 'tel' && !MOBILE_RE.test(v)) msg = 'Enter a valid mobile number.';
    else if (v && input.type === 'email' && !EMAIL_RE.test(v)) msg = 'Enter a valid email address.';
    else if (input.type === 'file' && input.files && input.files[0]) {
      var file = input.files[0];
      if (!/\.(pdf|doc|docx)$/i.test(file.name)) msg = 'Please upload a PDF or DOC file.';
      else if (file.size > 5 * 1024 * 1024) msg = 'File is too large (max 5 MB).';
    }
    fieldError(input, msg);
    return !msg;
  }
  $$('form[data-form]').forEach(function (form) {
    form.setAttribute('novalidate', 'novalidate');
    // Validate on submit (not on blur: an error appearing under a field would shift the layout and swallow the click on Submit).
    form.addEventListener('input', function (e) { if (e.target.getAttribute && e.target.getAttribute('aria-invalid')) validateField(e.target); });
    form.addEventListener('submit', function (e) {
      e.preventDefault();
      var inputs = $$('input, select, textarea', form);
      var firstBad = null;
      inputs.forEach(function (i) { if (!validateField(i) && !firstBad) firstBad = i; });
      if (firstBad) { firstBad.focus(); return; }
      var hp = $('.hp input', form);
      if (hp && hp.value) return; // bot
      submitForm(form);
    });
  });

  function showSuccess(form, fallback) {
    var wrapId = form.getAttribute('data-wrap');
    var succId = form.getAttribute('data-success');
    var wrap = wrapId && $('#' + wrapId);
    var succ = succId && $('#' + succId);
    if (wrap) wrap.hidden = true;
    if (succ) {
      succ.hidden = false;
      var h = $('h3', succ);
      var p = $('p', succ);
      if (h && !succ.getAttribute('data-ok-title')) succ.setAttribute('data-ok-title', h.textContent);
      if (p && !succ.getAttribute('data-ok-text')) succ.setAttribute('data-ok-text', p.textContent);
      // No form service configured yet: be honest that the visitor still has to press Send in their email app.
      if (h) h.textContent = (fallback && succ.getAttribute('data-fallback-title')) || succ.getAttribute('data-ok-title');
      if (p) p.textContent = (fallback && succ.getAttribute('data-fallback-text')) || succ.getAttribute('data-ok-text');
      if (h) { h.setAttribute('tabindex', '-1'); h.focus({ preventScroll: true }); }
      if (succ.scrollIntoView && !succ.closest('.modal')) succ.scrollIntoView({ behavior: 'smooth', block: 'center' });
    }
  }
  function submitForm(form) {
    var btn = $('button[type="submit"]', form);
    var label = btn && btn.querySelector('.label');
    var status = $('.form-status', form);
    var kind = form.getAttribute('data-form');
    var data = new FormData(form);
    data.delete('botcheck');
    data.set('page_url', window.location.href);
    var evt = kind === 'apply' ? 'career_application' : (kind === 'partner' ? 'b2b_partner_enquiry' : 'generate_lead');
    var subject = form.getAttribute('data-subject') || 'New website enquiry';
    var product = data.get('product') || data.get('product_interest') || data.get('position') || '';
    if (product) subject += ' — ' + product;
    data.set('subject', subject);
    data.set('from_name', 'Shreya Agro Foods Website');

    if (btn) { btn.disabled = true; if (label) { btn.setAttribute('data-label', label.textContent); label.textContent = 'Sending…'; } }
    if (status) status.hidden = true;

    if (CFG.web3formsKey) {
      data.set('access_key', CFG.web3formsKey);
      fetch('https://api.web3forms.com/submit', { method: 'POST', body: data, headers: { Accept: 'application/json' } })
        .then(function (r) { return r.json(); })
        .then(function (res) {
          if (res && res.success) { track(evt, { form: kind, item_name: product }); showSuccess(form, false); }
          else { throw new Error((res && res.message) || 'Submission failed'); }
        })
        .catch(function () {
          if (btn) { btn.disabled = false; if (label) label.textContent = btn.getAttribute('data-label') || label.textContent; }
          if (status) { status.textContent = 'Sorry, we could not send your message. Please try again, or call us on ' + (CFG.phoneDisplay || '') + '.'; status.hidden = false; }
        });
      return;
    }

    // No Web3Forms key configured yet: open the visitor's email app with the enquiry pre-filled.
    var lines = [];
    data.forEach(function (v, k) {
      if (k === 'access_key' || k === 'subject' || k === 'from_name' || k === 'page_url' || typeof v !== 'string' || !v.trim()) return;
      lines.push(k.replace(/_/g, ' ').replace(/^./, function (c) { return c.toUpperCase(); }) + ': ' + v.trim());
    });
    var mailto = 'mailto:' + (CFG.email || 'info@shreyaagrofoods.com') + '?subject=' + encodeURIComponent(subject) + '&body=' + encodeURIComponent(lines.join('\n') + '\n\nSent from: ' + window.location.href);
    track(evt, { form: kind, item_name: product });
    showSuccess(form, true);
    window.location.href = mailto;
  }

  /* Preselect enquiry type from ?enquiry= on the contact page */
  (function () {
    var sel = $('#g_type');
    if (!sel) return;
    var preset = new URLSearchParams(window.location.search).get('enquiry');
    if (!preset) return;
    $$('option', sel).forEach(function (o) { if (o.value === preset) sel.value = preset; });
  })();

  /* ---------- Product listing: search + filters ---------- */
  var grid = $('#productGrid');
  if (grid) {
    var cards = $$('.product-card', grid);
    var searchInput = $('#productSearch');
    var subSelect = $('#subcategory');
    var chips = $$('.chip[data-filter]');
    var count = $('#resultCount');
    var noRes = $('#noResults');
    var state = { cat: 'all', sub: 'all', q: '' };

    var subOptions = {};
    cards.forEach(function (c) {
      var cat = c.getAttribute('data-category'), t = c.getAttribute('data-type');
      subOptions[cat] = subOptions[cat] || [];
      if (subOptions[cat].indexOf(t) < 0) subOptions[cat].push(t);
    });
    function fillSub() {
      var list = [];
      if (state.cat === 'all') { Object.keys(subOptions).forEach(function (k) { subOptions[k].forEach(function (t) { if (list.indexOf(t) < 0) list.push(t); }); }); }
      else list = subOptions[state.cat] || [];
      list.sort();
      subSelect.innerHTML = '<option value="all">All sub-categories</option>' + list.map(function (t) { return '<option value="' + t.replace(/"/g, '&quot;') + '">' + t + '</option>'; }).join('');
      subSelect.value = state.sub;
      if (subSelect.value !== state.sub) { state.sub = 'all'; subSelect.value = 'all'; }
    }
    function apply() {
      var shown = 0;
      var q = state.q.trim().toLowerCase();
      cards.forEach(function (c) {
        var ok = (state.cat === 'all' || c.getAttribute('data-category') === state.cat) &&
          (state.sub === 'all' || c.getAttribute('data-type') === state.sub) &&
          (!q || c.getAttribute('data-search').indexOf(q) > -1);
        c.hidden = !ok;
        if (ok) shown++;
      });
      if (count) count.textContent = shown + (shown === 1 ? ' product' : ' products');
      if (noRes) noRes.hidden = shown !== 0;
      grid.hidden = shown === 0;
      chips.forEach(function (ch) { ch.setAttribute('aria-pressed', ch.getAttribute('data-filter') === state.cat ? 'true' : 'false'); });
    }
    chips.forEach(function (ch) {
      ch.addEventListener('click', function () {
        state.cat = ch.getAttribute('data-filter');
        state.sub = 'all';
        fillSub();
        apply();
        if (window.history && history.replaceState) history.replaceState(null, '', state.cat === 'all' ? window.location.pathname : '?category=' + state.cat);
      });
    });
    if (subSelect) subSelect.addEventListener('change', function () { state.sub = subSelect.value; apply(); });
    if (searchInput) searchInput.addEventListener('input', function () { state.q = searchInput.value; apply(); });
    var initial = new URLSearchParams(window.location.search).get('category');
    if (initial && chips.some(function (c) { return c.getAttribute('data-filter') === initial; })) state.cat = initial;
    fillSub();
    apply();
    if (window.location.hash === '#search' && searchInput) { window.setTimeout(function () { searchInput.focus(); }, 300); }
    var reset = $('#resetFilters');
    if (reset) reset.addEventListener('click', function () {
      state = { cat: 'all', sub: 'all', q: '' };
      if (searchInput) searchInput.value = '';
      fillSub(); apply();
    });
  }

  /* ---------- Product gallery ---------- */
  var mainImg = $('#galleryMain');
  if (mainImg) {
    $$('.gallery-thumbs button').forEach(function (b) {
      b.addEventListener('click', function () {
        mainImg.src = b.getAttribute('data-src');
        mainImg.srcset = b.getAttribute('data-srcset') || '';
        mainImg.alt = b.getAttribute('data-alt') || mainImg.alt;
        mainImg.classList.toggle('fit-contain', b.getAttribute('data-fit') === 'contain');
        mainImg.classList.toggle('pos-low', b.getAttribute('data-fit') === 'low');
        $$('.gallery-thumbs button').forEach(function (o) { o.removeAttribute('aria-current'); });
        b.setAttribute('aria-current', 'true');
      });
    });
  }

  /* ---------- Chatbot ---------- */
  var chatFab = $('#chatFab');
  var chatPanel = $('#chatPanel');
  var chatBody = $('#chatBody');
  var chatStarted = false;
  var ICON_ARROW = '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M5 12h14M13 6l6 6-6 6"/></svg>';
  function closeChat() {
    if (!chatPanel || chatPanel.hidden) return;
    chatPanel.hidden = true;
    chatFab.setAttribute('aria-expanded', 'false');
  }
  function addMsg(text, who) {
    var m = doc.createElement('div');
    m.className = 'msg ' + who;
    m.textContent = text;
    chatBody.appendChild(m);
    chatBody.scrollTop = chatBody.scrollHeight;
  }
  function addOptions(opts) {
    var wrap = doc.createElement('div');
    wrap.className = 'chat-options';
    opts.forEach(function (o) {
      var el;
      if (o.href) { el = doc.createElement('a'); el.href = o.href; if (o.external) { el.target = '_blank'; el.rel = 'noopener'; } }
      else { el = doc.createElement('button'); el.type = 'button'; }
      el.innerHTML = ICON_ARROW + '<span></span>';
      el.querySelector('span').textContent = o.label;
      if (o.action) {
        el.addEventListener('click', function () {
          if (o.say) addMsg(o.label, 'user');
          wrap.remove();
          o.action();
        });
      } else if (o.href) {
        el.addEventListener('click', function () { if (!o.external && o.href.charAt(0) !== '#') closeChat(); });
      }
      wrap.appendChild(el);
    });
    chatBody.appendChild(wrap);
    chatBody.scrollTop = chatBody.scrollHeight;
  }
  function chatMenu() {
    addMsg('Hi! How can we help you?', 'bot');
    addOptions([
      { label: 'Product Enquiry', say: true, action: function () { addMsg('Great! Choose a product from our catalogue, or send us a general product enquiry and our B2B team will get back to you.', 'bot'); addOptions([{ label: 'Send a Product Enquiry', action: function () { closeChat(); openEnquiry({ type: 'Product Enquiry', title: 'Product Enquiry' }); } }, { label: 'Browse Products', href: '/products/' }, { label: 'Back to menu', action: chatMenu }]); } },
      { label: 'B2B Partnership', say: true, action: function () { addMsg('We work with distributors, wholesalers and retailers across India. Tell us about your business and we will get in touch.', 'bot'); addOptions([{ label: 'Become a B2B Partner', href: '/vendor/' }, { label: 'Make a B2B Enquiry', action: function () { closeChat(); openEnquiry({ type: 'B2B / Wholesale' }); } }, { label: 'Back to menu', action: chatMenu }]); } },
      { label: 'Become a Distributor', say: true, action: function () { addMsg('Wonderful! Share your details and our team will contact you about distribution opportunities.', 'bot'); addOptions([{ label: 'Apply for Distribution', action: function () { closeChat(); openEnquiry({ type: 'Distribution', title: 'Distribution Enquiry' }); } }, { label: 'Back to menu', action: chatMenu }]); } },
      { label: 'Careers', say: true, action: function () { addMsg('We are always looking for passionate people to join us. See our current openings and apply online.', 'bot'); addOptions([{ label: 'View Current Openings', href: '/contact-us/#careers' }, { label: 'Back to menu', action: chatMenu }]); } },
      { label: 'Talk to Our Team', say: true, action: function () {
        addMsg('You can reach our team directly (Mon–Fri 10am–6pm, Sat 10am–2pm):', 'bot');
        addOptions([
          { label: 'Call ' + (CFG.phoneDisplay || ''), href: 'tel:' + (CFG.phoneTel || '') },
          { label: 'WhatsApp us', href: 'https://wa.me/' + (CFG.whatsapp || ''), external: true },
          { label: 'Email ' + (CFG.email || ''), href: 'mailto:' + (CFG.email || '') },
          { label: 'Contact page', href: '/contact-us/' },
          { label: 'Back to menu', action: chatMenu }
        ]);
      } }
    ]);
  }
  if (chatFab && chatPanel) {
    chatFab.addEventListener('click', function () {
      var open = chatPanel.hidden;
      chatPanel.hidden = !open;
      chatFab.setAttribute('aria-expanded', open ? 'true' : 'false');
      if (open && !chatStarted) { chatStarted = true; chatMenu(); }
    });
    var cc = $('#chatClose');
    if (cc) cc.addEventListener('click', function () { closeChat(); chatFab.focus(); });
  }

  /* ---------- Global presence orbit: highlight the country nearest the top ---------- */
  var orbit = $('#orbit');
  if (orbit) {
    var orbitTrack = $('.orbit-track', orbit);
    var items = $$('li', orbitTrack);
    var tipName = $('#orbitTipName');
    var tipFlag = $('#orbitTipFlag');
    var current = null;
    var updateOrbit = function () {
      var rot = 0;
      var m = /matrix\(([^)]+)\)/.exec(window.getComputedStyle(orbitTrack).transform || '');
      if (m) { var v = m[1].split(','); rot = Math.atan2(parseFloat(v[1]), parseFloat(v[0])) * 180 / Math.PI; }
      var best = items[0], bestDiff = 999;
      items.forEach(function (li) {
        var a = parseFloat(li.style.getPropertyValue('--a')) + rot; // 0deg = 3 o'clock, 270deg = top
        var diff = Math.abs(((a - 270) % 360 + 540) % 360 - 180);
        if (diff < bestDiff) { bestDiff = diff; best = li; }
      });
      if (best === current) return;
      if (current) current.classList.remove('is-active');
      current = best;
      best.classList.add('is-active');
      tipName.textContent = best.getAttribute('data-name');
      tipFlag.src = best.getAttribute('data-flag');
    };
    updateOrbit();
    var timer = null;
    var run = function (on) {
      if (on && !timer) timer = window.setInterval(updateOrbit, 400);
      if (!on && timer) { window.clearInterval(timer); timer = null; }
    };
    if ('IntersectionObserver' in window) {
      new IntersectionObserver(function (entries) { run(entries[0].isIntersecting); }).observe(orbit);
    } else { run(true); }
  }
})();
