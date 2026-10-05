#!/usr/bin/env python3
"""Regenerate derived files from the chapter pages.

  assets/chapters.js  - chapter list + reading times (used by every page)
  assets/cards.js     - every self-test question, for flashcards.html
  cheatsheet.html     - every chapter's TL;DR on one page

Run from anywhere:  python3 tools/build.py
"""
import html
import json
import os
import re
from html.parser import HTMLParser

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

CHAPTERS = [
    # n, slug, short title, part
    (1, "01-scale-from-zero-to-millions", "Scale from Zero to Millions", "Foundations"),
    (2, "02-back-of-the-envelope", "Back-of-the-Envelope Estimation", "Foundations"),
    (3, "03-interview-framework", "The 4-Step Interview Framework", "Foundations"),
    (4, "04-rate-limiter", "Rate Limiter", "Building blocks"),
    (5, "05-consistent-hashing", "Consistent Hashing", "Building blocks"),
    (6, "06-key-value-store", "Key-Value Store", "Building blocks"),
    (7, "07-unique-id-generator", "Unique ID Generator", "Building blocks"),
    (8, "08-url-shortener", "URL Shortener", "Real systems"),
    (9, "09-web-crawler", "Web Crawler", "Real systems"),
    (10, "10-notification-system", "Notification System", "Real systems"),
    (11, "11-news-feed", "News Feed", "Real systems"),
    (12, "12-chat-system", "Chat System", "Real systems"),
    (13, "13-search-autocomplete", "Search Autocomplete", "Real systems"),
    (14, "14-youtube", "YouTube", "Real systems"),
    (15, "15-google-drive", "Google Drive", "Real systems"),
    (16, "16-learning-continues", "The Learning Continues", "Next steps"),
]


def read(path):
    with open(path, encoding="utf-8") as f:
        return f.read()


def text_of(fragment):
    return html.unescape(re.sub(r"<[^>]+>", " ", fragment))


def words(fragment):
    return len(text_of(fragment).split())


def first(pattern, s, default=""):
    m = re.search(pattern, s, re.S)
    return m.group(1).strip() if m else default


class SectionGrabber(HTMLParser):
    """Return the inner HTML of the first element matching a predicate (handles nesting)."""

    VOID = {"img", "br", "hr", "meta", "link", "input", "source", "wbr", "col"}

    def __init__(self, src, match):
        super().__init__(convert_charrefs=False)
        self.src, self.match = src, match
        self.depth, self.start, self.result = 0, None, None
        self.lines = [0]
        for line in src.splitlines(keepends=True):
            self.lines.append(self.lines[-1] + len(line))

    def pos(self):
        line, col = self.getpos()
        return self.lines[line - 1] + col

    def handle_starttag(self, tag, attrs):
        if self.result is not None or tag in self.VOID:
            return
        if self.start is None:
            if self.match(tag, dict(attrs)):
                self.start = self.pos() + len(self.get_starttag_text())
                self.depth = 1
        else:
            self.depth += 1

    def handle_endtag(self, tag):
        if self.start is None or self.result is not None or tag in self.VOID:
            return
        self.depth -= 1
        if self.depth == 0:
            self.result = self.src[self.start:self.pos()]


def grab(src, match):
    g = SectionGrabber(src, match)
    g.feed(src)
    return g.result


def rebase(fragment, slug):
    """Rewrite links in a chapter fragment so it works from the site root."""
    fragment = fragment.replace('src="../', 'src="').replace('href="../', 'href="')
    fragment = re.sub(r'href="#', f'href="chapters/{slug}.html#', fragment)
    return re.sub(r'href="(?!https?:|mailto:|chapters/|assets/|[a-z]+\.html)([^"]+\.html[^"]*)"', r'href="chapters/\1"', fragment)


def all_qas(src):
    """Yield (question_html, answer_html) for every <details class="qa">."""
    out = []
    for m in re.finditer(r'<details class="qa"[^>]*>(.*?)</details>', src, re.S):
        inner = m.group(1)
        q = first(r"<summary>(.*?)</summary>", inner)
        a = re.sub(r"^.*?</summary>", "", inner, count=1, flags=re.S).strip()
        a = re.sub(r"^<div>(.*)</div>$", r"\1", a, flags=re.S).strip()
        if q:
            out.append((q, a))
    return out


def main():
    book = {}
    info_path = os.path.join(ROOT, "source", "chapters", "info.json")
    if os.path.exists(info_path):
        for x in json.load(open(info_path)):
            book[x["ch"]] = x

    meta, cards, sheets = [], [], []
    for n, slug, short, part in CHAPTERS:
        path = os.path.join(ROOT, "chapters", slug + ".html")
        entry = {"n": n, "slug": slug, "short": short, "part": part, "ready": False}
        bsrc = os.path.join(ROOT, "source", "chapters", f"ch{n:02d}.txt")
        if os.path.exists(bsrc):
            btxt = re.sub(r"^=====.*$", "", read(bsrc), flags=re.M).split("Reference materials")[0]
            entry["bookMin"] = max(1, round(len(btxt.split()) / 230))  # same reading speed as the pages
        if os.path.exists(path):
            src = read(path)
            main_html = grab(src, lambda t, a: t == "main") or ""
            for sid in ("skeleton", "self-test", "glossary"):
                main_html = main_html.replace(grab(main_html, lambda t, a, sid=sid: a.get("id") == sid) or "\0", "")
            for cls in ("chapter-hero", "demo"):
                while True:
                    part = grab(main_html, lambda t, a, cls=cls: cls in (a.get("class") or "").split())
                    if not part:
                        break
                    main_html = main_html.replace(part, "", 1)
            entry.update(
                ready=True,
                title=text_of(first(r"<h1[^>]*>(.*?)</h1>", src)).strip(),
                hook=text_of(first(r'<p class="lede">(.*?)</p>', src)).strip(),
                min=max(1, round(words(main_html) / 230)),
            )
            for q, a in all_qas(src):
                cards.append({"ch": n, "q": rebase(q.strip(), slug), "a": rebase(a, slug)})
            tldr = grab(src, lambda t, a: t == "section" and "tldr" in (a.get("class") or "").split())
            if tldr:
                tldr = re.sub(r"<h2[^>]*>.*?</h2>", "", tldr, count=1, flags=re.S)
                tldr = rebase(tldr, slug)
                sheets.append((n, slug, entry.get("title", short), tldr))
        meta.append(entry)

    with open(os.path.join(ROOT, "assets", "chapters.js"), "w", encoding="utf-8") as f:
        f.write("/* Generated by tools/build.py - do not edit by hand. */\n")
        f.write("window.CHAPTERS = " + json.dumps(meta, indent=1, ensure_ascii=False) + ";\n")

    with open(os.path.join(ROOT, "assets", "cards.js"), "w", encoding="utf-8") as f:
        f.write("/* Generated by tools/build.py - do not edit by hand. */\n")
        f.write("window.CARDS = " + json.dumps(cards, ensure_ascii=False) + ";\n")

    blocks = []
    for n, slug, title, tldr in sheets:
        blocks.append(
            f'<section class="cs-block" id="ch{n}"><h2><small>Chapter {n}</small>'
            f'<a href="chapters/{slug}.html">{html.escape(title)}</a></h2>{tldr}</section>'
        )
    sheet = read(os.path.join(ROOT, "tools", "cheatsheet.template.html")).replace("<!--BLOCKS-->", "\n".join(blocks))
    with open(os.path.join(ROOT, "cheatsheet.html"), "w", encoding="utf-8") as f:
        f.write(sheet)

    ready = [m for m in meta if m["ready"]]
    print(f"chapters ready: {len(ready)}/{len(meta)}  cards: {len(cards)}  cheat-sheet blocks: {len(blocks)}")
    for m in meta:
        status = f"{m.get('min', '-'):>3} min (book ~{m.get('bookMin', '?')})" if m["ready"] else "  missing"
        print(f"  {m['n']:>2}. {m['short']:<34} {status}")


if __name__ == "__main__":
    main()
