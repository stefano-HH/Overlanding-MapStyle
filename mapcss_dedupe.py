#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
mapcss_dedupe.py

Entfernt aus einer Overlay-MapCSS-Datei alle Definitionen, die identisch
in einer Basis-Datei enthalten sind. Es bleiben nur die abweichenden Definitionen.

Anwendung pro Dateipaar:
    python mapcss_dedupe.py <basis.mapcss> <overlay.mapcss> [--output ausgabe.mapcss] [--report-only] [--clean]

Beispiele:
    python mapcss_dedupe.py Default.style/points.mapcss \\
        Default.style/overlanding/points.mapcss --output out/points.mapcss
    python mapcss_dedupe.py Default.style/lines.mapcss \\
        Default.style/overlanding/lines.mapcss --output out/lines.mapcss
    python mapcss_dedupe.py Default.style/polygons.mapcss \\
        Default.style/overlanding/polygons.mapcss --output out/polygons.mapcss
    python mapcss_dedupe.py Default.style/colors.mapcss \\
        Default.style/overlanding/colors.mapcss --output out/colors.mapcss
    python mapcss_dedupe.py Default.style/points.mapcss \\
        Default.style/overlanding/if-food.mapcss --output out/if-food.mapcss

Ohne --output wird das Ergebnis auf stdout geschrieben.
--report-only zeigt nur an, was entfernt wurde, ohne Datei zu schreiben.
"""

import argparse
import re
import sys
from pathlib import Path


def norm_ws(s):
    return re.sub(r"\s+", " ", s).strip()


def skip_ws_and_comments(s, i):
    n = len(s)
    while i < n:
        if s[i] in " \t\r\n":
            i += 1
            continue
        if s.startswith("//", i):
            j = s.find("\n", i)
            i = n if j == -1 else j
            continue
        if s.startswith("/*", i):
            j = s.find("*/", i + 2)
            i = n if j == -1 else j + 2
            continue
        break
    return i


class Item:
    pass


class Rule(Item):
    def __init__(self, selector, children, start, end):
        self.selector = selector
        self.children = children
        self.start = start
        self.end = end


class Prop(Item):
    def __init__(self, text, start, end):
        self.text = text
        self.start = start
        self.end = end


class Var(Item):
    def __init__(self, name, value, start, end):
        self.name = name
        self.value = value
        self.start = start
        self.end = end


class Cond(Item):
    def __init__(self, header, children, start, end):
        self.header = header
        self.children = children
        self.start = start
        self.end = end


class Import(Item):
    def __init__(self, text, start, end):
        self.text = text
        self.start = start
        self.end = end


class Raw(Item):
    def __init__(self, text, start, end):
        self.text = text
        self.start = start


def read_if_header(s, i, n):
    j = s.find("\n", i)
    if j == -1:
        j = n
    return s[i:j], j


def is_property(s, i, n):
    m = re.match(r"\s*([A-Za-z_][\w-]*)\s*:", s[i:])
    if not m:
        return False
    after_key = i + m.end()
    semi = s.find(";", after_key)
    brace = s.find("{", after_key)
    if semi == -1:
        return False
    if brace != -1 and brace < semi:
        return False
    return True


def parse_sequence(s, i, terminators, n):
    items = []
    while i < n:
        i = skip_ws_and_comments(s, i)
        if i >= n:
            break

        term = None
        for t in terminators:
            if s.startswith(t, i):
                term = t
                break
        if term is not None:
            break

        if s.startswith("@if", i):
            start = i
            header, i = read_if_header(s, i, n)
            inner, i = parse_sequence(s, i, {"@endif"}, n)
            if s.startswith("@endif", i):
                i += len("@endif")
            items.append(Cond(header, inner, start, i))
            continue

        if s[i] == "@":
            start = i
            j = s.find(";", i)
            j = n if j == -1 else j + 1
            stmt = s[i:j]
            if stmt.lstrip().startswith("@import"):
                items.append(Import(stmt, start, j))
            else:
                m = re.match(r"\s*@([\w-]+)\s*:\s*(.*?)\s*;\s*$", stmt, re.S)
                if m:
                    items.append(Var(m.group(1), m.group(2), start, j))
                else:
                    items.append(Raw(stmt, start, j))
            i = j
            continue

        if s[i] == "}":
            if "}" in terminators:
                break
            i += 1
            continue

        if is_property(s, i, n):
            start = i
            j = s.find(";", i)
            j = n if j == -1 else j + 1
            items.append(Prop(s[i:j], start, j))
            i = j
            continue

        start = i
        brace = s.find("{", i)
        if brace == -1:
            items.append(Raw(s[i:n].strip(), i, n))
            i = n
            break
        selector = s[i:brace]
        i = brace + 1
        body, i = parse_sequence(s, i, {"}"}, n)
        if i < n and s[i] == "}":
            i += 1
        items.append(Rule(selector, body, start, i))

    return items, i


def parse_mapcss(text):
    items, _ = parse_sequence(text, 0, set(), len(text))
    return items


def canon_prop(p):
    m = re.match(r"\s*([\w-]+)\s*:\s*(.*?)\s*;\s*$", p.text, re.S)
    if m:
        return ("prop", m.group(1).strip(), norm_ws(m.group(2)))
    return ("prop", "", norm_ws(p.text))


def canon_var(v):
    return ("var", v.name.strip(), norm_ws(v.value))


def canon_rule(r):
    props = tuple(sorted(canon_prop(c) for c in r.children if isinstance(c, Prop)))
    children = tuple(canon_rule(c) for c in r.children if isinstance(c, Rule))
    return ("rule", norm_ws(r.selector), props, children)


def collect_signatures(items, rule_sigs, var_sigs):
    for it in items:
        if isinstance(it, Rule):
            rule_sigs.add(canon_rule(it))
            collect_signatures(it.children, rule_sigs, var_sigs)
        elif isinstance(it, Var):
            var_sigs.add(canon_var(it))
        elif isinstance(it, Cond):
            collect_signatures(it.children, rule_sigs, var_sigs)


def mark_removals(items, base_rule_sigs, base_var_sigs, removals):
    for it in items:
        if isinstance(it, Rule):
            if canon_rule(it) in base_rule_sigs:
                removals.append((it.start, it.end))
                continue
            mark_removals(it.children, base_rule_sigs, base_var_sigs, removals)
        elif isinstance(it, Var):
            if canon_var(it) in base_var_sigs:
                removals.append((it.start, it.end))
        elif isinstance(it, Cond):
            mark_removals(it.children, base_rule_sigs, base_var_sigs, removals)


def apply_removals(text, removals):
    removals.sort()
    out = []
    cur = 0
    for a, b in removals:
        if b <= cur:
            continue
        if a > cur:
            out.append(text[cur:a])
        cur = b
    out.append(text[cur:])
    return "".join(out)


def collapse_blank_lines(text):
    return re.sub(r"\n{3,}", "\n\n", text)


def main():
    ap = argparse.ArgumentParser(
        description="Entfernt aus einer Overlay-MapCSS-Datei alle Definitionen, "
                    "die identisch in der Basis-Datei enthalten sind.")
    ap.add_argument("base", help="Basis-MapCSS-Datei (z. B. Default.style/points.mapcss)")
    ap.add_argument("overlay", nargs="?", default=None,
                    help="Overlay-MapCSS-Datei (z. B. Default.style/overlanding/points.mapcss). "
                         "Wenn nicht angegeben: Default.style/overlanding/<gleichername>")
    ap.add_argument("--output", "-o", help="Ausgabedatei (Default: Default.style/overlanding/<name>-clean.mapcss)")
    ap.add_argument("--report-only", action="store_true",
                    help="Nur melden, was entfernt wurde, ohne Datei zu schreiben")
    ap.add_argument("--clean", action="store_true",
                    help="Mehrere aufeinanderfolgende Leerzeilen zusammenfassen")
    args = ap.parse_args()

    if args.overlay is None:
        args.overlay = str(Path("Default.style/overlanding") / Path(args.base).name)

    base_text = Path(args.base).read_text(encoding="utf-8")
    overlay_text = Path(args.overlay).read_text(encoding="utf-8")

    base_items = parse_mapcss(base_text)
    base_rule_sigs, base_var_sigs = set(), set()
    collect_signatures(base_items, base_rule_sigs, base_var_sigs)

    overlay_items = parse_mapcss(overlay_text)
    removals = []
    mark_removals(overlay_items, base_rule_sigs, base_var_sigs, removals)

    result = apply_removals(overlay_text, removals)
    if args.clean:
        result = collapse_blank_lines(result)

    removed_chars = sum(b - a for a, b in removals)
    print(f"Basis-Regelsignaturen: {len(base_rule_sigs)} | Basis-Variablen: {len(base_var_sigs)}")
    print(f"Entfernte Overlay-Bereiche: {len(removals)} ({removed_chars} Zeichen)")

    if args.report_only:
        print("--- report-only: keine Datei geschrieben ---")
        for a, b in removals:
            snippet = norm_ws(overlay_text[a:b].split("\n")[0])[:80]
            print(f"  entfernen: Pos {a}-{b} | {snippet}")
        return

    if args.output:
        out_path = Path(args.output)
    else:
        out_path = Path(args.overlay).parent / f"{Path(args.overlay).stem}-clean.mapcss"

    out_path.write_text(result, encoding="utf-8")
    print(f"Geschrieben: {out_path}")


if __name__ == "__main__":
    main()