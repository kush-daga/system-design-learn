# Authoring a chapter page

The goal is to turn one chapter of *System Design Interview – An Insider's Guide* (Alex Xu) into a single HTML page. The reader should **never need to open the book**: every useful fact stays, everything else goes, and the structure makes it fast to read, review and recall. Readers are engineers preparing for interviews who find the book slow going.

**Reference implementation: `chapters/07-unique-id-generator.html`.** Read it fully before writing. Copy its `<head>`, `<body>` attributes and closing `<script>` tags exactly. Change only the `<title>`, `data-chapter` and the content of `<main>`.

## Inputs

- `source/chapters/chNN.txt` — the chapter's text, extracted from the PDF. `===== [PDF PAGE n] images on this page (in order): ... =====` markers show which figure images sit on each page.
- `source/img/p-PPP-NNN.jpg` — the figures. **Look at every image for your chapter** with the Read tool; the figure number ("Figure 4-7") is printed inside the image. In the page, reference figures as `../assets/img/p-PPP-NNN.jpg` (same filenames).
- The text often says "as shown in Figure X" followed by blank lines. That gap is where the image sits.

## Page structure (in this order)

1. **Hero** — `header.chapter-hero` containing `p.eyebrow` ("Chapter N · Design problem" / "Foundations"), `h1` (the book's chapter title, in title case), `p.lede` (1–2 sentences: what you'll learn), an empty `div.meta-row` (JS fills it in), and `ul.pace` with the four jump links (TL;DR / Interview answer / Full walkthrough → first walkthrough section id / Self-test).
2. **`<section id="tldr" class="tldr">`** — `h2` "TL;DR", 5–9 bullets (≤ 180 words), plus the single most important figure (usually the final architecture). It must stand on its own: it is copied verbatim into the one-page cheat sheet.
3. **`<section id="skeleton">`** — `h2` "Interview answer skeleton", a `p.one-liner`, then `ol.framework`: four items for design problems (Clarify / High-level / Deep dive / Wrap up, each with a ≈time budget and the concrete points to say). Non-design chapters adapt the idea, e.g. "How to use this in an interview" with 3–5 items. ≤ 170 words.
4. **Walkthrough** — one `<section>` per major part of the chapter. Design-problem chapters use `id="step-1"` … `id="step-4"` with `<h2><span class="step-num">Step N</span>Title</h2>`. Other chapters use descriptive ids. Use `h3` for the book's subsections and `h4` for small labels. Begin each `h2` section with `p.one-liner` (one sentence: the point of the section).
5. **`<section id="self-test">`** — `h2` "Self-test" followed by **8–15** questions in exactly this format (a build script parses it into flashcards):
   `<details class="qa"><summary>Question?</summary><div><p>Answer.</p></div></details>`
   Questions test what an interviewer would probe: requirements, numbers, trade-offs, "why X over Y", flow steps, failure handling. Answers are 1–3 sentences, may contain `<code>`/`<b>`/`<ul>`, and must be answerable from the page.
6. **`<section id="glossary">`** — `h2` "Terms to know", a `dl.glossary` with 5–12 terms, then the book's reference list as `<details class="more refs"><summary>Book references (go deeper)</summary><div><ol>…</ol></div></details>` with working `<a href>` links (rejoin URLs that were broken across lines in the extraction).

## Content rules

**Coverage — nothing useful dropped.** Every section and subsection of the book chapter must appear. Keep every:
requirement and clarifying Q&A · number, estimate and its arithmetic · formula · algorithm and its steps · API endpoint/signature · data model/schema/table · step of every request flow · option considered, with its pros/cons · named technology and why it was chosen · edge case/failure mode and its fix · wrap-up talking point.
Keep the interviewer dialogue as a `table.qa-table` ("You ask" / "Interviewer says").

**Cut.** Filler, repetition, throat-clearing ("Let us now look at…"), motivational lines, and figures re-shown "to refresh your memory" (unless the deep dive needs them nearby).

**Length.** Aim for the walkthrough to be roughly 50–70% of the book chapter's word count; denser chapters can go lower. Never drop a fact to hit a number. Prefer structure over prose: a 6-row table beats 3 paragraphs.

**Style.**
- Plain, direct English, written to the reader as "you". No gendered pronouns for the candidate.
- Paragraphs of 1–3 sentences. Bold the key term the first time it appears, and define jargon on first use.
- Comparisons → `table` (use `<td class="yes">✓</td>` / `<td class="no">✗</td>`). Sequential flows → `ol.flow`. Options → `div.pros-cons`. Key numbers → `div.stats`. Requirements → `ul.checklist`.
- Callouts (all optional, used sparingly, ≤ ~6 per chapter):
  - `aside.callout.key` + `<span class="callout-label">Key idea</span>`: the one insight to remember
  - `aside.callout.tip` + `Say this in the interview`: a phrasing or point that scores
  - `aside.callout.warn` + `Pitfall` or `Trade-off`
  - `aside.callout.note` + `Beyond the book`: at most 2 per chapter, only for high-value, well-established facts an interviewer is likely to ask about. Everything not labeled this way must come from the book.
- **Accuracy matters more than anything.** Don't invent numbers, components or claims. Derived arithmetic is fine if correct (check it). Where the book has an error, gently note the correct version.

**Figures.**
- Include every figure that carries information. Skip pure duplicates and decorative images.
- `<figure class="fig"><img src="../assets/img/p-PPP-NNN.jpg" alt="what the diagram shows"><figcaption><b>Figure X-Y</b> · what to notice</figcaption></figure>`. Add `small` (≤440px) or `medium` (≤600px) to the figure class for narrow or low-detail images so they aren't blown up. Use `div.fig-row` to set two small related figures side by side.
- Place each figure next to the text that explains it, and make the caption say *what to look at*, not just repeat the title.
- If an image is just **text, code, JSON or a table** (not a diagram), transcribe it into `<pre><code>` or a `<table>` instead of embedding the image. Text is faster to read and searchable.

**Interactive demo (optional, at most one per chapter).** Only add one when interacting makes a mechanism click (e.g. a token bucket filling, a hash ring, base-62 conversion). Put it in `div.demo` with `span.demo-title` "Try it · …", inside the walkthrough section it illustrates. Write vanilla JS in one inline `<script>` IIFE placed **before** the `chapters.js` script tag. No libraries, no network, must work over `file://`. Use CSS variables (`var(--accent)`, `var(--ink-3)`, …) for any colors. Keep it small (< ~120 lines), and run its logic through `node` to check it before you finish.

**HTML hygiene.** Valid, properly closed tags. Escape `<`, `>` and `&` in text. No external resources. Inline `style` only for small layout tweaks inside a demo.

## Before you finish

1. `python3 tools/check.py chapters/NN-slug.html` must print `ok` (it checks structure, image paths, self-test format and tag balance).
2. Re-read the source chapter section by section and confirm each fact is on your page.
3. Do **not** run `tools/build.py` (other writers are working in parallel; it gets run at the end).
