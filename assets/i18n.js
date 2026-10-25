/* Tiny static i18n: ?lang=xx > saved choice > browser languages > English. */
(function () {
  var S = window.I18N_STRINGS || {};
  var LANGS = [
    { code: "en", html: "en", label: "English", locale: "en_US" },
    { code: "zh", html: "zh-Hans", label: "简体中文", locale: "zh_CN" },
    { code: "ja", html: "ja", label: "日本語", locale: "ja_JP" },
    { code: "ko", html: "ko", label: "한국어", locale: "ko_KR" },
    { code: "ru", html: "ru", label: "Русский", locale: "ru_RU" },
    { code: "es", html: "es", label: "Español", locale: "es_ES" },
    { code: "de", html: "de", label: "Deutsch", locale: "de_DE" }
  ];
  var KEY = "bq_lang";
  var missing = (window.__i18nMissing = []);
  function valid(c) { return LANGS.some(function (l) { return l.code === c; }); }
  function norm(c) { return (c || "").toLowerCase().split(/[-_]/)[0]; }
  function store(c) { try { localStorage.setItem(KEY, c); } catch (e) {} }
  function saved() { try { return localStorage.getItem(KEY); } catch (e) { return null; } }

  function detect() {
    var p = norm(new URLSearchParams(location.search).get("lang"));
    if (valid(p)) { store(p); return p; }
    var s = saved(); if (valid(s)) return s;
    var nav = navigator.languages && navigator.languages.length ? navigator.languages : [navigator.language];
    for (var i = 0; i < nav.length; i++) { var c = norm(nav[i]); if (valid(c)) return c; }
    return "en";
  }

  var current = "en";
  function t(key, vars) {
    var d = S[current] || {}, s = d[key];
    if (s === undefined) {
      if (missing.indexOf(current + ":" + key) < 0) { missing.push(current + ":" + key); console.warn("i18n missing", current, key); }
      s = (S.en || {})[key]; if (s === undefined) s = key;
    }
    if (vars) for (var k in vars) s = s.split("{" + k + "}").join(vars[k]);
    return s;
  }
  var dec = document.createElement("textarea");
  function plain(html) { dec.innerHTML = html; return dec.value; }
  function vars(el) { var v = el.getAttribute("data-i18n-vars"); return v ? JSON.parse(v) : null; }

  function localizeLinks(lang) {
    document.querySelectorAll("a[href]").forEach(function (a) {
      var h = a.getAttribute("href");
      if (/^[a-z]+:|^\/\/|^#/i.test(h) || !/\.html(\?|#|$)/.test(h)) return;
      var hash = h.indexOf("#") >= 0 ? h.slice(h.indexOf("#")) : "";
      var base = h.replace(/#.*$/, "").replace(/\?.*$/, "");
      a.setAttribute("href", base + (lang === "en" ? "" : "?lang=" + lang) + hash);
    });
  }

  function apply(lang) {
    current = valid(lang) ? lang : "en";
    var meta = LANGS.filter(function (l) { return l.code === current; })[0];
    document.documentElement.lang = meta.html;
    document.querySelectorAll("[data-i18n]").forEach(function (el) {
      var v = t(el.getAttribute("data-i18n"), vars(el));
      if (el.tagName === "TITLE") el.textContent = plain(v); else el.innerHTML = v;
    });
    document.querySelectorAll("[data-i18n-attr]").forEach(function (el) {
      el.getAttribute("data-i18n-attr").split(";").forEach(function (pair) {
        var i = pair.indexOf(":"); if (i < 0) return;
        el.setAttribute(pair.slice(0, i).trim(), plain(t(pair.slice(i + 1).trim(), vars(el))));
      });
    });
    var og = document.querySelector('meta[property="og:locale"]'); if (og) og.setAttribute("content", meta.locale);
    document.querySelectorAll("select[data-lang-switch]").forEach(function (s) { s.value = current; });
    localizeLinks(current);
    document.dispatchEvent(new CustomEvent("i18n:change", { detail: { lang: current } }));
  }

  function setLang(lang) {
    store(lang);
    var u = new URL(location.href);
    if (lang === "en") u.searchParams.delete("lang"); else u.searchParams.set("lang", lang);
    try { history.replaceState(null, "", u.toString()); } catch (e) {}
    apply(lang);
  }

  function buildSwitchers() {
    document.querySelectorAll("[data-lang-switch]").forEach(function (host) {
      var sel = host.tagName === "SELECT" ? host : document.createElement("select");
      if (sel !== host) { sel.setAttribute("data-lang-switch", ""); host.removeAttribute("data-lang-switch"); host.appendChild(sel); }
      sel.className = (sel.className + " lang-switch").trim();
      sel.setAttribute("data-i18n-attr", "aria-label:nav.lang;title:nav.lang");
      LANGS.forEach(function (l) { var o = document.createElement("option"); o.value = l.code; o.textContent = l.label; o.lang = l.html; sel.appendChild(o); });
      sel.addEventListener("change", function () { setLang(sel.value); });
    });
  }

  window.I18N = { t: t, setLang: setLang, langs: LANGS, get lang() { return current; } };
  buildSwitchers();
  apply(detect());
})();
