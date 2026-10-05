/* System Design Interview — Fast Track: shared page behaviour.
   Builds the top bar, chapter TOC, pager, progress tracking, lightbox and resume prompt.
   Relies on window.CHAPTERS from chapters.js. Works over file:// (no fetch). */
(function () {
  "use strict";

  var CH = window.CHAPTERS || [];
  var body = document.body;
  var root = body.dataset.root || ".";
  var chNum = body.dataset.chapter ? parseInt(body.dataset.chapter, 10) : null;
  var main = document.querySelector("main");

  var store = {
    get: function (k, d) { try { var v = localStorage.getItem("sdi:" + k); return v === null ? d : JSON.parse(v); } catch (e) { return d; } },
    set: function (k, v) { try { localStorage.setItem("sdi:" + k, JSON.stringify(v)); } catch (e) {} }
  };
  window.SDI = { store: store, root: root };

  function el(tag, attrs, html) {
    var n = document.createElement(tag);
    if (attrs) for (var k in attrs) { if (k === "class") n.className = attrs[k]; else n.setAttribute(k, attrs[k]); }
    if (html != null) n.innerHTML = html;
    return n;
  }
  function href(c) { return root + "/chapters/" + c.slug + ".html"; }
  function isDone(n) { return !!store.get("done:" + n, false); }
  function slugify(s) { return s.toLowerCase().replace(/<[^>]+>/g, "").replace(/[^a-z0-9]+/g, "-").replace(/^-|-$/g, "").slice(0, 60); }

  /* ---------- Theme ---------- */
  function currentTheme() {
    return document.documentElement.dataset.theme ||
      (window.matchMedia && matchMedia("(prefers-color-scheme: dark)").matches ? "dark" : "light");
  }
  function setTheme(t) { document.documentElement.dataset.theme = t; store.set("theme", t); }
  if (!document.documentElement.dataset.theme) document.documentElement.dataset.theme = currentTheme();

  /* ---------- Top bar ---------- */
  var cur = chNum != null ? CH.filter(function (c) { return c.n === chNum; })[0] : null;
  var topbar = el("header", { class: "topbar" });
  topbar.innerHTML =
    (main && main.classList.contains("chapter") ? '<button class="toc-toggle" aria-label="Contents">☰</button>' : "") +
    '<a class="brand" href="' + root + '/index.html">SDI <span>Fast Track</span></a>' +
    (cur ? '<span class="crumb">Ch ' + cur.n + ' / ' + CH.length + ' · <b>' + cur.short + '</b></span>' : "") +
    '<span class="spacer"></span>' +
    '<a class="tb-link cs" href="' + root + '/cheatsheet.html">Cheat sheet</a>' +
    '<a class="tb-link" href="' + root + '/flashcards.html">Flashcards</a>' +
    '<button class="theme-toggle" title="Toggle theme (t)">◐</button>' +
    '<span class="progress-bar"></span>';
  body.insertBefore(topbar, body.firstChild);
  topbar.querySelector(".theme-toggle").onclick = function () { setTheme(currentTheme() === "dark" ? "light" : "dark"); };

  var bar = topbar.querySelector(".progress-bar");
  function onScrollBar() {
    var h = document.documentElement.scrollHeight - innerHeight;
    bar.style.width = (h > 0 ? Math.min(100, (scrollY / h) * 100) : 0) + "%";
  }
  addEventListener("scroll", onScrollBar, { passive: true });

  /* ---------- Chapter page ---------- */
  if (main && main.classList.contains("chapter")) {
    // Wrap main in a layout grid with the TOC.
    var layout = el("div", { class: "layout" });
    var toc = el("nav", { class: "toc", "aria-label": "Chapter contents" });
    main.parentNode.insertBefore(layout, main);
    layout.appendChild(toc);
    layout.appendChild(main);

    // Give every h2/h3 an anchor (an h2's anchor is its parent section's id when it has one).
    var heads = Array.prototype.slice.call(main.querySelectorAll("h2, h3")).map(function (h) {
      var p = h.parentElement;
      if (!h.id && h.tagName === "H2" && p.tagName === "SECTION" && p.id) return { h: h, id: p.id, target: p };
      if (!h.id) {
        var base = slugify(h.textContent) || "s", id = base, i = 2;
        while (document.getElementById(id)) id = base + "-" + i++;
        h.id = id;
      }
      return { h: h, id: h.id, target: h };
    });

    // Reading-time estimate in the hero: TL;DR + walkthrough (not self-test, glossary or demos).
    function countWords(node) { return node ? (node.innerText || node.textContent || "").split(/\s+/).filter(Boolean).length : 0; }
    var skip = main.querySelectorAll(".chapter-hero, #skeleton, #self-test, #glossary, .demo, .refs");
    var total = countWords(main);
    skip.forEach(function (n) { total -= countWords(n); });
    var mins = Math.max(1, Math.round(total / 230));
    var meta = main.querySelector(".meta-row");
    if (meta && cur) {
      meta.insertAdjacentHTML("afterbegin",
        "<span>⏱ <b>~" + mins + " min</b> read</span>" +
        "<span>" + main.querySelectorAll("details.qa").length + " self-test questions</span>");
    }

    // TOC: this chapter's sections + all chapters.
    function headText(h) {
      var sn = h.querySelector(".step-num");
      var t = h.textContent.trim();
      return sn ? sn.textContent.trim() + " · " + t.slice(sn.textContent.trim().length).trim() : t;
    }
    var tocHtml = "<h4>In this chapter</h4><ol>";
    heads.forEach(function (x) {
      if (x.h.closest(".tldr, .demo") && x.h.tagName === "H3") return;
      tocHtml += '<li class="' + (x.h.tagName === "H3" ? "sub" : "") + '"><a href="#' + x.id + '">' +
        headText(x.h) + "</a></li>";
    });
    tocHtml += "</ol><h4>All chapters</h4><ol class=\"toc-chapters\">";
    CH.forEach(function (c) {
      tocHtml += '<li><a href="' + href(c) + '" class="' + (c.n === chNum ? "active " : "") + (isDone(c.n) ? "done" : "") + '">' +
        c.n + ". " + c.short + "</a></li>";
    });
    toc.innerHTML = tocHtml + "</ol>";
    var tt = topbar.querySelector(".toc-toggle");
    if (tt) {
      tt.onclick = function () { toc.classList.toggle("open"); };
      toc.addEventListener("click", function (e) { if (e.target.tagName === "A") toc.classList.remove("open"); });
    }

    // Scrollspy.
    var links = {};
    toc.querySelectorAll('ol:first-of-type a').forEach(function (a) { links[a.getAttribute("href").slice(1)] = a; });
    function spy() {
      var y = scrollY + 90, best = null;
      heads.forEach(function (x) { if (links[x.id] && x.target.getBoundingClientRect().top + scrollY <= y) best = x.id; });
      Object.keys(links).forEach(function (k) { links[k].classList.toggle("active", k === best); });
    }
    addEventListener("scroll", spy, { passive: true });
    spy();

    // Self-test: reveal/hide all.
    var qas = main.querySelectorAll("details.qa");
    var st = main.querySelector("#self-test, .self-test");
    if (qas.length && st) {
      var first = st.querySelector("details.qa");
      var tools = el("div", { class: "selftest-bar" });
      tools.innerHTML = '<button class="btn" type="button">Reveal all answers</button><span>Answer out loud first, then open each card.</span>';
      first.parentNode.insertBefore(tools, first);
      var open = false;
      tools.querySelector("button").onclick = function () {
        open = !open;
        qas.forEach(function (d) { d.open = open; });
        this.textContent = open ? "Hide all answers" : "Reveal all answers";
      };
    }

    // Chapter end: mark complete + pager.
    var idx = CH.indexOf(cur);
    var prev = CH[idx - 1], next = CH[idx + 1];
    var end = el("footer", { class: "chapter-end" });
    end.innerHTML =
      '<div class="complete-row"><button class="btn mark-done" type="button"></button>' +
      '<span class="hint">Progress is saved in this browser.</span></div>' +
      '<nav class="pager">' +
      (prev ? '<a class="prev" href="' + href(prev) + '"><small>← Previous</small>' + prev.n + ". " + prev.short + "</a>" : "") +
      (next ? '<a class="next" href="' + href(next) + '"><small>Next →</small>' + next.n + ". " + next.short + "</a>" : "") +
      "</nav>" +
      '<p class="kbd-hint"><kbd>←</kbd> <kbd>→</kbd> previous / next chapter · <kbd>t</kbd> theme · <kbd>r</kbd> reveal all answers · <kbd>m</kbd> mark complete</p>';
    main.appendChild(end);
    var md = end.querySelector(".mark-done");
    function paintDone() {
      var d = isDone(chNum);
      md.textContent = d ? "✓ Completed" : "Mark chapter complete";
      md.classList.toggle("done-on", d);
    }
    md.onclick = function () { store.set("done:" + chNum, !isDone(chNum)); paintDone(); };
    paintDone();

    // Remember position; offer to resume.
    var saved = store.get("pos:" + chNum, 0);
    store.set("last", chNum);
    var saveT;
    addEventListener("scroll", function () {
      clearTimeout(saveT);
      saveT = setTimeout(function () { store.set("pos:" + chNum, Math.round(scrollY)); }, 250);
    }, { passive: true });
    if (!location.hash && saved > 600) {
      var toast = el("div", { class: "toast" }, '<span>Continue where you left off?</span><button type="button">Resume</button><button type="button" class="ghost">✕</button>');
      body.appendChild(toast);
      var btns = toast.querySelectorAll("button");
      btns[0].onclick = function () { scrollTo({ top: saved, behavior: "smooth" }); toast.remove(); };
      btns[1].onclick = function () { toast.remove(); };
      setTimeout(function () { if (toast.parentNode) toast.remove(); }, 9000);
    }

    // Keyboard shortcuts.
    addEventListener("keydown", function (e) {
      if (e.metaKey || e.ctrlKey || e.altKey || /input|select|textarea/i.test(e.target.tagName)) return;
      if (e.key === "ArrowLeft" && prev) location.href = href(prev);
      else if (e.key === "ArrowRight" && next) location.href = href(next);
      else if (e.key === "r" && st) st.querySelector(".selftest-bar button").click();
      else if (e.key === "m") md.click();
    });

    // Wrap bare tables for horizontal scroll.
    main.querySelectorAll("table").forEach(function (t) {
      if (!t.parentElement.classList.contains("table-wrap")) {
        var w = el("div", { class: "table-wrap" });
        t.parentNode.insertBefore(w, t); w.appendChild(t);
      }
    });
  }

  /* ---------- Global keys + lightbox ---------- */
  addEventListener("keydown", function (e) {
    if (e.metaKey || e.ctrlKey || e.altKey || /input|select|textarea/i.test(e.target.tagName)) return;
    if (e.key === "t") setTheme(currentTheme() === "dark" ? "light" : "dark");
  });
  var lb = el("div", { class: "lightbox", role: "dialog", "aria-label": "Figure" }, "<img alt=''>");
  body.appendChild(lb);
  document.addEventListener("click", function (e) {
    var img = e.target.closest && e.target.closest("figure.fig img");
    if (img) { lb.firstChild.src = img.src; lb.firstChild.alt = img.alt; lb.classList.add("open"); }
  });
  lb.onclick = function () { lb.classList.remove("open"); };
  addEventListener("keydown", function (e) { if (e.key === "Escape") lb.classList.remove("open"); });
})();
