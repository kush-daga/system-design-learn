# System Design Interview — Fast Track

Study pages for Alex Xu's *System Design Interview – An Insider's Guide* (Vol. 1). All 16 chapters are condensed into step-by-step pages so you can get through the book quickly without losing the parts that matter.

**Live site: https://system-design-learn.vercel.app**

## How to read it

1. **Open the home page** and press **Start with Chapter 1**. Read the chapters in order; later chapters build on 1–7.
2. **On each chapter page, work top to bottom:**
   - **TL;DR**: the whole chapter in about 2 minutes. Read it first so you know where the details are heading.
   - **Interview skeleton**: the answer you'd give in an interview, using the 4-step framework.
   - **Walkthrough**: the book's content in its original order, condensed, with the original diagrams. Click a figure to zoom. Some chapters have interactive demos (rate limiter, hash ring, ID generator and others); try them.
   - **Self-test**: answer each question out loud **before** opening it. This step is what makes the material stick.
   - **Terms**: a quick glossary and references.
3. **Press "Mark chapter complete"** at the end. Progress and your scroll position are saved in your browser, and the home page shows a **Continue** button.
4. **Drill the [Flashcards](flashcards.html)** (all 226 self-test questions) at the start of each session. Cards you miss come back first.
5. **Before an interview, read the [Cheat sheet](cheatsheet.html)**: every chapter's TL;DR on one printable page.

The home page has a suggested plan of about one hour per session (roughly 3 hours of reading for the whole book).

### Keyboard shortcuts (chapter pages)

| Key | Action |
| --- | --- |
| `←` / `→` | Previous / next chapter |
| `r` | Reveal or hide all self-test answers |
| `m` | Mark the chapter complete |
| `t` | Toggle light/dark theme |
| `Space` / `1` / `2` | Flashcards: flip / missed it / got it |

## Run locally

No build step and no server needed. Clone the repo and open `index.html` in a browser; it works offline over `file://`.

```sh
git clone https://github.com/kush-daga/system-design-learn.git
open system-design-learn/index.html
```

## Layout

- `chapters/`: one page per chapter.
- `flashcards.html`: spaced-repetition deck built from every self-test.
- `cheatsheet.html`: all TL;DRs on one page.
- `assets/`: styles, scripts, generated data (`chapters.js`, `cards.js`) and the book's figures.
- `tools/`: `check.py` validates pages, `build.py` regenerates the generated files and the cheat sheet after edits, and `AUTHORING.md` describes the page format.

## Note

These are personal study notes. The diagrams and source material are © Alex Xu / ByteByteGo. If you find this useful, [buy the book](https://www.amazon.com/dp/B08CMF2CQF) or subscribe at [bytebytego.com](https://bytebytego.com).
