/* Kelley Library Science Fiction and Fantasy Bookclub — reading-list page.
   Plain JavaScript, no libraries. Reads data/books.json and images/images.json. */
(function () {
  "use strict";

  var MONTHS = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"];
  var STATUS_LABEL = { "no-meeting": "No meeting", "unknown": "Unknown",
                       "planning": "Meeting, no book (planning)", "upcoming": "Upcoming" };

  /* ---------- Pure helpers (also used by tests in Node) ---------- */

  // Lower-case and strip accents, keeping a map from each normalized
  // character back to its position in the original string.
  function fold(str) {
    var out = "", map = [];
    for (var i = 0; i < str.length; i++) {
      var base = str[i].normalize("NFD").replace(/[̀-ͯ]/g, "").toLowerCase();
      for (var j = 0; j < base.length; j++) { out += base[j]; map.push(i); }
    }
    return { text: out, map: map };
  }
  function simple(str) { return fold(str || "").text; }

  function sortTitle(t) { return simple(t).replace(/^(the|a|an)\s+/, ""); }

  function prepare(rows) {
    return rows.map(function (r, i) {
      return Object.assign({}, r, {
        order: i,
        isBook: r.status === "read" || r.status === "undated",
        dateKey: r.year ? r.year * 100 + r.month : null,
        dateText: r.year ? MONTHS[r.month - 1] + " " + r.year : (r.status === "undated" ? "Undated" : ""),
        displayTitle: r.status === "read" || r.status === "undated" ? r.title : (STATUS_LABEL[r.status] || r.title),
        titleFold: fold(r.title || ""),
        authorFold: fold(r.author || ""),
        titleSort: sortTitle(r.title || ""),
        authorSort: simple(r.author || ""),
        seriesSort: simple(r.series || "")
      });
    });
  }

  function matches(row, q) {
    if (!q) return true;
    if (!row.isBook) return false;
    return row.titleFold.text.indexOf(q) !== -1 || row.authorFold.text.indexOf(q) !== -1;
  }

  // Dates: newest/oldest by year+month; undated always last; within a month keep
  // master-list order. Ties on other columns break by date, newest first.
  function compare(key, dir) {
    var sign = dir === "asc" ? 1 : -1;
    function byDate(a, b, s) {
      if (a.dateKey === null && b.dateKey === null) return a.order - b.order;
      if (a.dateKey === null) return 1;
      if (b.dateKey === null) return -1;
      if (a.dateKey !== b.dateKey) return s * (a.dateKey - b.dateKey);
      return a.order - b.order;   // same month: keep master-list order
    }
    return function (a, b) {
      if (key === "date") return byDate(a, b, sign);
      var field = key === "title" ? "titleSort" : key === "author" ? "authorSort" : "seriesSort";
      var x = a[field], y = b[field];
      // Rows with no text in this column (status rows) go last.
      if (!x && y) return 1;
      if (x && !y) return -1;
      var c = x < y ? -1 : x > y ? 1 : 0;
      if (c !== 0) return sign * c;
      return byDate(a, b, -1);
    };
  }

  function view(rows, opts) {
    var q = simple((opts.query || "").trim());
    return rows
      .filter(function (r) { return (r.isBook || (opts.showAll && !q)) && matches(r, q); })
      .sort(compare(opts.key, opts.dir));
  }

  function escapeHtml(s) {
    return String(s).replace(/[&<>"']/g, function (c) {
      return { "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c];
    });
  }

  // Wrap every match of q (already folded) in <mark>, using the fold map.
  function highlight(original, folded, q) {
    if (!q) return escapeHtml(original);
    var out = "", last = 0, from = 0, idx;
    while ((idx = folded.text.indexOf(q, from)) !== -1) {
      var start = folded.map[idx];
      var end = folded.map[idx + q.length - 1] + 1;
      out += escapeHtml(original.slice(last, start)) + "<mark>" + escapeHtml(original.slice(start, end)) + "</mark>";
      last = end; from = idx + q.length;
    }
    return out + escapeHtml(original.slice(last));
  }

  if (typeof module !== "undefined" && module.exports) {
    module.exports = { fold: fold, simple: simple, sortTitle: sortTitle, prepare: prepare,
                       view: view, highlight: highlight };
    return;
  }

  /* ---------- Page ---------- */

  var $ = function (id) { return document.getElementById(id); };
  var state = { key: "date", dir: "desc", query: "", showAll: false };
  var ROWS = [], BOOK_COUNT = 0;

  function storeGet(k) { try { return localStorage.getItem(k); } catch (e) { return null; } }
  function storeSet(k, v) { try { localStorage.setItem(k, v); } catch (e) {} }

  function render() {
    var q = simple(state.query.trim());
    var list = view(ROWS, state);
    var html = list.map(function (r) {
      if (!r.isBook) {
        return '<tr class="status"><td class="col-date">' + r.dateText + '</td><td class="col-title">' +
          escapeHtml(r.displayTitle) + '</td><td class="col-author"></td><td class="col-series"></td></tr>';
      }
      var part = r.part ? ' <span class="part">(' + escapeHtml(r.part) + ")</span>" : "";
      return "<tr><td class=\"col-date\">" + r.dateText + '</td><td class="col-title">' +
        highlight(r.title, r.titleFold, q) + part + '</td><td class="col-author">' +
        highlight(r.author, r.authorFold, q) + '</td><td class="col-series">' + escapeHtml(r.series) + "</td></tr>";
    }).join("");
    $("rows").innerHTML = html;

    var shown = list.filter(function (r) { return r.isBook; }).length;
    $("count").textContent = q ? "Showing " + shown + " of " + BOOK_COUNT + " books" : BOOK_COUNT + " books";
    var empty = $("empty");
    if (q && shown === 0) { empty.textContent = "No books match ‘" + state.query.trim() + "’"; empty.hidden = false; }
    else { empty.hidden = true; }
    $("clear").hidden = state.query === "";

    document.querySelectorAll("thead th").forEach(function (th) {
      var key = th.querySelector("button").dataset.key;
      var on = key === state.key;
      th.setAttribute("aria-sort", on ? (state.dir === "asc" ? "ascending" : "descending") : "none");
      th.querySelector(".arrow").textContent = on ? (state.dir === "asc" ? "▲" : "▼") : "";
    });
  }

  function wireTable() {
    var search = $("search");
    search.addEventListener("input", function () { state.query = search.value; render(); });
    search.addEventListener("keydown", function (e) {
      if (e.key === "Escape") { search.value = ""; state.query = ""; render(); }
    });
    $("clear").addEventListener("click", function () {
      search.value = ""; state.query = ""; render(); search.focus();
    });
    $("showAll").addEventListener("change", function (e) { state.showAll = e.target.checked; render(); });
    document.querySelectorAll("thead button").forEach(function (b) {
      b.addEventListener("click", function () {
        var key = b.dataset.key;
        if (state.key === key) state.dir = state.dir === "asc" ? "desc" : "asc";
        else { state.key = key; state.dir = key === "date" ? "desc" : "asc"; }
        render();
      });
    });
  }

  /* ---------- Themes and banners ---------- */

  var POOLS = {}, lastImage = {}, activeLayer = "bannerA";
  var reduceMotion = window.matchMedia && matchMedia("(prefers-reduced-motion: reduce)").matches;

  function currentTheme() { return document.documentElement.getAttribute("data-theme"); }

  function pickImage(theme) {
    var pool = POOLS[theme] || [];
    if (!pool.length) return null;
    if (pool.length === 1) return pool[0];
    var choices = pool.filter(function (img) { return img.file !== lastImage[theme]; });
    var img = choices[Math.floor(Math.random() * choices.length)];
    lastImage[theme] = img.file;
    return img;
  }

  function showBanner(theme) {
    var img = pickImage(theme);
    var credit = $("bannerCredit");
    if (!img) { credit.hidden = true; return; }
    var url = "images/" + img.file;
    var probe = new Image();
    probe.onload = function () {
      if (currentTheme() !== theme) return;           // theme changed while loading
      var next = activeLayer === "bannerA" ? "bannerB" : "bannerA";
      var nextEl = $(next), prevEl = $(activeLayer);
      nextEl.style.backgroundImage = 'url("' + url + '")';
      nextEl.style.backgroundPosition = img.focus || "center";
      if (reduceMotion) { prevEl.style.transition = nextEl.style.transition = "none"; }
      nextEl.classList.add("on");
      prevEl.classList.remove("on");
      activeLayer = next;
      credit.innerHTML = "Banner: <i>" + escapeHtml(img.title) + "</i>, " + escapeHtml(img.creator) +
        (img.date ? ", " + escapeHtml(img.date) : "");
      credit.hidden = false;
    };
    probe.onerror = function () {
      // Image not downloaded yet: keep the theme's color background.
      if (currentTheme() !== theme) return;
      $("bannerA").classList.remove("on"); $("bannerB").classList.remove("on");
      credit.hidden = true;
    };
    probe.src = url;
  }

  function setTheme(theme, save) {
    document.documentElement.setAttribute("data-theme", theme);
    $("themeSelect").value = theme;
    if (save) storeSet("sff-theme", theme);
    showBanner(theme);
  }

  function wireThemes() {
    var select = $("themeSelect");
    select.value = currentTheme();
    select.addEventListener("change", function () { setTheme(select.value, true); });
    // A fresh picture from the same theme's pool.
    $("shuffle").addEventListener("click", function () { showBanner(currentTheme()); });
  }

  function buildCredits(data) {
    var names = { "deep-space": "Deep Space", "enchanted-forest": "Enchanted Forest",
                  "retro-pulp": "Retro Pulp", "library-classic": "Library Classic" };
    var html = "";
    Object.keys(data.pools).forEach(function (theme) {
      html += '<li class="theme-name">' + escapeHtml(names[theme] || theme) + "</li>";
      data.pools[theme].forEach(function (img) {
        html += "<li><i>" + escapeHtml(img.title) + "</i>, " + escapeHtml(img.creator) +
          (img.date ? " (" + escapeHtml(img.date) + ")" : "") + ". " + escapeHtml(img.licence) +
          '. <a href="' + escapeHtml(img.source) + '" rel="noopener noreferrer">Source</a></li>';
      });
    });
    $("creditList").innerHTML = html;
  }

  function formatDate(iso) {
    var d = new Date(iso);
    if (isNaN(d)) return "";
    return d.getDate() + " " + MONTHS[d.getMonth()] + " " + d.getFullYear();
  }

  /* ---------- Start ---------- */

  wireTable();
  wireThemes();

  // Data comes from data/books.js and images/images.js (written by build.py),
  // which load even when the page is opened straight from the disk.
  // books.json / images.json are only a fallback.
  function load(globalName, url) {
    if (window[globalName]) return Promise.resolve(window[globalName]);
    return fetch(url, { cache: "no-cache" })
      .then(function (r) { if (!r.ok) throw new Error(r.status); return r.json(); });
  }

  load("SFF_BOOKS", "data/books.json")
    .then(function (data) {
      ROWS = prepare(data.rows);
      BOOK_COUNT = ROWS.filter(function (r) { return r.isBook; }).length;
      var when = formatDate(data.generated);
      $("updated").textContent = when ? "Last updated " + when : "";
      $("built").textContent = when ? "List last updated " + when + "." : "";
      render();
    })
    .catch(function () {
      $("count").textContent = "Sorry, the reading list couldn't be loaded.";
    });

  load("SFF_IMAGES", "images/images.json")
    .then(function (data) {
      POOLS = data.pools || {};
      buildCredits(data);
      showBanner(currentTheme());
    })
    .catch(function () {});
})();
