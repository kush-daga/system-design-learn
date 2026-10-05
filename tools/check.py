#!/usr/bin/env python3
"""Validate chapter pages.  Usage: python3 tools/check.py [chapters/07-unique-id-generator.html ...]
With no arguments, checks every chapter in chapters/."""
import glob
import os
import re
import sys
from html.parser import HTMLParser

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
VOID = {"img", "br", "hr", "meta", "link", "input", "source", "wbr", "col", "area", "base", "embed", "param", "track"}
OPTIONAL_CLOSE = {"p", "li", "dt", "dd", "tr", "td", "th", "thead", "tbody", "option"}


class Balance(HTMLParser):
    def __init__(self):
        super().__init__()
        self.stack, self.errors = [], []

    def handle_starttag(self, tag, attrs):
        if tag not in VOID:
            self.stack.append((tag, self.getpos()[0]))

    def handle_endtag(self, tag):
        if tag in VOID:
            return
        while self.stack and self.stack[-1][0] != tag and self.stack[-1][0] in OPTIONAL_CLOSE:
            self.stack.pop()
        if self.stack and self.stack[-1][0] == tag:
            self.stack.pop()
        else:
            self.errors.append(f"line {self.getpos()[0]}: unexpected </{tag}> (open: {[t for t, _ in self.stack[-3:]]})")


def check(path):
    src = open(path, encoding="utf-8").read()
    problems, notes = [], []
    b = Balance()
    b.feed(src)
    leftovers = [f"<{t}> from line {l}" for t, l in b.stack if t not in OPTIONAL_CLOSE]
    problems += b.errors[:10]
    if leftovers:
        problems.append("unclosed: " + ", ".join(leftovers[:6]))

    m = re.search(r'data-chapter="(\d+)"', src)
    if not m:
        problems.append('missing <body data-root=".." data-chapter="N">')
    for needle, label in [
        ('<main id="content" class="chapter">', "main.chapter"),
        ('class="chapter-hero"', "hero header"),
        ('<p class="lede">', "lede paragraph"),
        ('class="meta-row"', "meta-row div"),
        ('id="tldr" class="tldr"', "TL;DR section"),
        ('id="skeleton"', "interview skeleton section"),
        ('id="self-test"', "self-test section"),
        ('src="../assets/chapters.js"', "chapters.js script"),
        ('src="../assets/app.js"', "app.js script"),
        ('href="../assets/style.css"', "stylesheet"),
    ]:
        if needle not in src:
            problems.append(f"missing {label}  ({needle})")

    qas = re.findall(r'<details class="qa"><summary>.*?</summary><div>.*?</div></details>', src, re.S)
    allqa = src.count('<details class="qa"')
    if allqa != len(qas):
        problems.append(f"{allqa - len(qas)} self-test item(s) not in the exact format "
                        '<details class="qa"><summary>Q</summary><div>A</div></details>')
    if len(qas) < 8:
        problems.append(f"only {len(qas)} self-test questions (want 8-15)")

    imgs = re.findall(r'<img[^>]+src="([^"]+)"', src)
    for s in imgs:
        p = os.path.normpath(os.path.join(os.path.dirname(path), s))
        if not os.path.exists(p):
            problems.append(f"image not found: {s}")
    for s in re.findall(r'<img(?![^>]*\balt=")[^>]*>', src):
        problems.append(f"img without alt: {s[:80]}")
    if re.search(r'(src|href)="https?://(?!en\.wikipedia|)', src) and "<script src=\"http" in src:
        problems.append("external script/resource")
    if re.search(r"<(script|link)[^>]+(src|href)=\"https?://", src):
        problems.append("external script/stylesheet - pages must work offline")

    main = re.search(r"<main.*?</main>", src, re.S)
    words = len(re.sub(r"<[^>]+>", " ", main.group(0)).split()) if main else 0
    figs = len(set(imgs))
    notes.append(f"{words} words · {len(qas)} questions · {figs} figures · ~{max(1, round(words / 230))} min")
    return problems, notes


def main():
    paths = sys.argv[1:] or sorted(glob.glob(os.path.join(ROOT, "chapters", "*.html")))
    bad = 0
    for p in paths:
        problems, notes = check(p)
        name = os.path.relpath(p, ROOT)
        print(("FAIL " if problems else "ok   ") + name + "  —  " + "; ".join(notes))
        for x in problems:
            print("     - " + x)
        bad += bool(problems)
    sys.exit(1 if bad else 0)


if __name__ == "__main__":
    main()
