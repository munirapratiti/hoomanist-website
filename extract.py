#!/usr/bin/env python3
"""One-off: pulls editable text out of the section markup.

The design ships as HTML with styling on every element, which the CMS cannot
edit safely. This walks each section, lifts the text into content/*.json, and
leaves {{key}} placeholders behind so build.py can put it back.

Run once. After that, content/*.json is the source of truth for wording and
src/raw/*.html is the source of truth for layout.
"""

import json
import os
import re
from html.parser import HTMLParser

# Tags that may appear *inside* an editable chunk without splitting it, so a
# heading like "Placed with <span>purpose.</span>" stays one field.
INLINE = {"br", "span", "b", "strong", "i", "em", "u", "sup", "sub", "small"}
VOID = {"br", "img", "input", "hr", "meta", "link"}
# Elements worth offering to the editor.
CANDIDATE = {"h1", "h2", "h3", "h4", "p", "summary", "label", "a", "span",
             "div", "button", "li", "td", "th"}


class Chunker(HTMLParser):
    """Finds the outermost elements whose content is text plus inline markup."""

    def __init__(self):
        super().__init__(convert_charrefs=False)
        self.stack = []      # open elements: [tag, start_offset, has_block_child]
        self.chunks = []     # (start, end, tag) of qualifying elements
        self.skip_depth = 0

    def handle_starttag(self, tag, attrs):
        if tag in ("script", "style"):
            self.skip_depth += 1
            return
        if tag in VOID:
            if self.stack and tag not in INLINE:
                self.stack[-1][2] = True
            return
        # a non-inline child disqualifies the parent from being a single chunk
        if self.stack and tag not in INLINE:
            self.stack[-1][2] = True
        self.stack.append([tag, self.getpos(), False])

    def handle_endtag(self, tag):
        if tag in ("script", "style"):
            self.skip_depth = max(0, self.skip_depth - 1)
            return
        if tag in VOID:
            return
        for i in range(len(self.stack) - 1, -1, -1):
            if self.stack[i][0] == tag:
                el = self.stack.pop(i)
                del self.stack[i:]
                if not el[2] and el[0] in CANDIDATE:
                    self.chunks.append((el[1], self.getpos(), el[0]))
                break


def offset(src_lines, pos):
    line, col = pos
    return sum(len(l) for l in src_lines[:line - 1]) + col


def slug(text, used):
    base = re.sub(r"[^a-z0-9]+", "_", text.lower()).strip("_")[:40] or "text"
    key, n = base, 2
    while key in used:
        key, n = f"{base}_{n}", n + 1
    used.add(key)
    return key


def process(path):
    src = open(path).read()
    lines = src.splitlines(keepends=True)

    p = Chunker()
    p.feed(src)

    # innermost-first so nested candidates do not overlap; keep outermost only
    spans = []
    for start, end, tag in p.chunks:
        s, e = offset(lines, start), offset(lines, end)
        spans.append((s, e, tag))
    spans.sort(key=lambda x: (x[0], -x[1]))

    kept, last_end = [], -1
    for s, e, tag in spans:
        if s >= last_end:
            kept.append((s, e, tag))
            last_end = e

    fields, used, out, cursor = {}, set(), [], 0
    for s, e, tag in kept:
        block = src[s:e]
        inner = block[block.index(">") + 1:]
        text = re.sub(r"<[^>]+>", " ", inner)
        text = re.sub(r"\s+", " ", text).strip()
        if not text or len(text) < 2:
            continue
        key = slug(text, used)
        fields[key] = {"tag": tag, "value": inner.strip(),
                       "label": (text[:60] + "…") if len(text) > 60 else text}
        out.append(src[cursor:s + block.index(">") + 1])
        out.append("{{" + key + "}}")
        cursor = e
    out.append(src[cursor:])

    return "".join(out), fields


if __name__ == "__main__":
    os.makedirs("content", exist_ok=True)
    total = 0
    for name in sorted(os.listdir("src/raw")):
        if not name.endswith(".html"):
            continue
        path = os.path.join("src/raw", name)
        tpl, fields = process(path)
        if not fields:
            continue
        stem = name[:-5]
        open(path, "w").write(tpl)
        with open(f"content/{stem}.json", "w") as fh:
            json.dump(fields, fh, indent=2, ensure_ascii=False)
        total += len(fields)
        print(f"  {stem:14s} {len(fields):3d} ruas teks")
    print(f"total: {total} ruas")
