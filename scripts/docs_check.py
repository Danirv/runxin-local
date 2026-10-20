#!/usr/bin/env python3
"""Check the repository's Markdown links, fragments, navigation and locales.

Only local links are checked; historical external sources need human review.
The parser handles the inline links and fenced code used by this repository.
"""

from __future__ import annotations

from collections import defaultdict
from pathlib import Path
import re
from urllib.parse import unquote, urlsplit

ROOT = Path(__file__).resolve().parents[1]
LINK = re.compile(r'!?\[[^\]\n]*\]\((?:<([^>]+)>|([^\s)]+))(?:\s+"[^"]*")?\)')
HEADING = re.compile(r"^ {0,3}#{1,6}\s+(.+?)(?:\s+#+)?$")
HTML_ID = re.compile(r'<a\s+(?:id|name)=[\"\']([^\"\']+)[\"\']', re.I)


def prose(text: str) -> str:
    """Ignore fenced examples when collecting links and heading anchors."""
    result = []
    fence: str | None = None
    for line in text.splitlines():
        marker = re.match(r"^ {0,3}(`{3,}|~{3,})", line)
        if marker:
            token = marker[1]
            if fence is None:
                fence = token
            elif token[0] == fence[0] and len(token) >= len(fence):
                fence = None
            result.append("")
        else:
            result.append(line if fence is None else "")
    return "\n".join(result)


def anchors(text: str) -> set[str]:
    """GitHub-style Unicode heading slugs, duplicates and explicit anchors."""
    text = prose(text)
    result = set(HTML_ID.findall(text))
    counts: dict[str, int] = defaultdict(int)
    for line in text.splitlines():
        match = HEADING.match(line)
        if not match:
            continue
        heading = re.sub(r"<[^>]+>", "", match[1])
        base = re.sub(r"[^\w -]", "", heading.lower()).replace(" ", "-")
        count = counts[base]
        candidate = base if count == 0 else f"{base}-{count}"
        # An earlier generated heading can already occupy a suffixed slug.
        while candidate in result:
            count += 1
            candidate = f"{base}-{count}"
        counts[base] = count + 1
        result.add(candidate)
    return result


def check(root: Path) -> list[str]:
    root = root.resolve()
    pages = {
        p.resolve(): p.read_text()
        for p in root.rglob("*.md")
        if not any(part.startswith(".") and part != ".github" for part in p.relative_to(root).parts)
    }
    ids = {p: anchors(text) for p, text in pages.items()}
    edges: dict[Path, set[Path]] = defaultdict(set)
    errors = []
    for page, text in pages.items():
        label = page.relative_to(root)
        for match in LINK.finditer(prose(text)):
            link = urlsplit(match[1] or match[2])
            if link.scheme or link.netloc:
                continue
            raw = unquote(link.path)
            target = (root / raw.lstrip("/") if raw.startswith("/") else page.parent / raw).resolve() if raw else page
            if not target.is_relative_to(root):
                errors.append(f"{label}: link leaves repository: {raw}")
            elif not target.exists():
                errors.append(f"{label}: missing target: {raw}")
            elif target in pages:
                edges[page].add(target)
                fragment = unquote(link.fragment)
                if fragment and fragment not in ids[target]:
                    errors.append(f"{label}: missing fragment: {raw}#{fragment}")
        if page.name.endswith((".ca.md", ".es.md")):
            base = re.sub(r"\.(ca|es)\.md$", "", page.name)
            english = root / "README.md" if page.parent == root / "docs" and base == "README" else page.with_name(base + ".md")
            siblings = (english, page.with_name(base + ".ca.md"), page.with_name(base + ".es.md"))
            for sibling in siblings:
                if not sibling.exists():
                    errors.append(f"{label}: missing language counterpart: {sibling.relative_to(root)}")

    seen: set[Path] = set()
    pending = [root / "README.md"]
    while pending:
        page = pending.pop()
        if page in seen:
            continue
        seen.add(page)
        pending.extend(edges[page] - seen)
    for page, text in pages.items():
        if page.is_relative_to(root / "docs") and page not in seen and "<!-- compatibility-page -->" not in text:
            errors.append(f"{page.relative_to(root)}: not reachable from README/documentation index")
    return sorted(set(errors))


def main() -> int:
    errors = check(ROOT)
    if errors:
        print("DOCUMENTATION CHECK FAILED\n" + "\n".join(errors))
        return 1
    print("Documentation check OK: local links, fragments, navigation and language counterparts.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
