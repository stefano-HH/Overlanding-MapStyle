# mapcss_dedupe.py — Documentation

Removes all definitions from an overlay MapCSS file that are **identical** in a base file. Only the deviating (overlay-specific) definitions are kept.

---

## 1. Background

The base style collection is located directly in `Default.style/` (e.g. `points.mapcss`, `lines.mapcss`, `polygons.mapcss`, `colors.mapcss`).

The folder `Default.style/overlanding/` contains overlay styles that are loaded "on top" (see `Default.style/Style-Overlanding.mapcss`). Often these overlay files contain definitions that already exist 1:1 in the base. The script removes such redundancies so that **only the deviating definitions** remain in the overlay file.

---

## 2. Prerequisites

- Python 3 (no external libraries required)
- The script is located in the repository root directory

---

## 3. Usage

### Recommended simple call

```bash
python3 mapcss_dedupe.py Default.style/points.mapcss --clean
```

- `base`: Base file (e.g. `Default.style/points.mapcss`)
- `overlay` (optional): If omitted, it is automatically resolved to `Default.style/overlanding/<same-name>`.
- `--clean`: Merges multiple consecutive blank lines (recommended).

Result: `Default.style/overlanding/points-clean.mapcss`

---

### Specifying exact file pairs

```bash
python3 mapcss_dedupe.py Default.style/colors.mapcss Default.style/overlanding/colors.mapcss --clean
```

Result: `Default.style/overlanding/colors-clean.mapcss`

---

### Report only (dry-run), write nothing

```bash
python3 mapcss_dedupe.py Default.style/lines.mapcss Default.style/overlanding/lines.mapcss --report-only
```

Shows which areas were detected as redundant without writing a file.

---

### Custom output file

```bash
python3 mapcss_dedupe.py Default.style/polygons.mapcss Default.style/overlanding/polygons.mapcss --output out/polygons-clean.mapcss --clean
```

---

### Processing all files at once (example shell loop)

```bash
# Base files
python3 mapcss_dedupe.py Default.style/colors.mapcss     --clean
python3 mapcss_dedupe.py Default.style/points.mapcss    --clean
python3 mapcss_dedupe.py Default.style/lines.mapcss     --clean
python3 mapcss_dedupe.py Default.style/polygons.mapcss  --clean

# if-*.mapcss files (subsets of points.mapcss)
for f in Default.style/overlanding/if-*.mapcss; do
    python3 mapcss_dedupe.py Default.style/points.mapcss "$f" --clean
done

# brands.mapcss (has no base counterpart, nothing to remove)
python3 mapcss_dedupe.py Default.style/points.mapcss Default.style/overlanding/brands.mapcss --clean
```

---

## 4. Output

By default (without `--output`), the cleaned file is written into the same folder as the overlay file:

```
Default.style/overlanding/<filename>-clean.mapcss
```

Example:
- Input: `Default.style/overlanding/colors.mapcss`
- Output: `Default.style/overlanding/colors-clean.mapcss`

The script never overwrites the original files.

---

## 5. How it works

1. **Parsing**: The base and overlay files are parsed with an own brace-based parser into a tree of rules, properties, variables, and `@if…@endif` blocks.
2. **Signatures**: A signature is built for each rule from selector + direct properties + all nested child rules (recursively). For variables from name + value. Whitespace is normalized.
3. **Comparison**: All signatures from the base file are collected. Each overlay rule whose full signature matches a base rule is marked as redundant.
4. **Removal**: Only outermost, fully redundant blocks are cut out. Partially deviating rules are kept entirely — nothing is lost.
5. **Reconstruction**: The original text of the remaining parts is output exactly as it was (only the removed spans are cut out).

---

## 6. Supported MapCSS constructs

- Rules: `selector { property: value; }` including nested rules
- Properties: `key: value;`
- Variables: `@name: value;`
- `@import` statements (kept unchanged, not checked)
- `@if Condition … @endif` blocks (the wrapper is kept, only redundant content inside is removed)
- Comments (`//` and `/* */`)

---

## 7. Important notes

- **Originals are never modified.** The script never writes to `base` or `overlay`. A separate output file is always created.
- Two rules are considered identical only if selector **and** direct properties **and** all nested child rules match exactly (whitespace-normalized).
- `@import` lines are not considered "definitions" and are not removed.
- `colors.mapcss` consists mostly of variables. Two variables are considered identical if name **and** value match.
- For `if-*.mapcss` files, comparison is done against `Default.style/points.mapcss` (the `@if…@endif` wrapper is kept).

---

## 8. Known limitations

- The parser is not a full MapCSS parser. Rare edge cases (curly braces inside string values) practically do not occur in MapCSS.
- The script does not merge two similar rules *within the same* overlay file. It only removes rules that are identical to the base file. Manual consolidation within a file is not covered.

---

## 9. File pairs in this repository

| Base (`Default.style/`) | Overlay (`Default.style/overlanding/`) |
|---|---|
| `colors.mapcss` | `colors.mapcss` |
| `points.mapcss` | `points.mapcss` |
| `lines.mapcss` | `lines.mapcss` |
| `polygons.mapcss` | `polygons.mapcss` |
| `points.mapcss` | `if-bar.mapcss`, `if-beauty.mapcss`, … (all `if-*.mapcss`) |
| *(none)* | `brands.mapcss` (no base counterpart present) |

---

## 10. License

See `LICENSE.md` in the repository root directory.
