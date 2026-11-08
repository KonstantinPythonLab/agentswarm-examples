"""Offline translation checks against check-owned, pinned English baselines."""
import hashlib
import json
import os
from difflib import SequenceMatcher
from pathlib import Path
import re
import unicodedata
from urllib.parse import unquote, urlsplit

from markdown_it import MarkdownIt

PARSER = MarkdownIt('commonmark')


def links(text):
    return {token.attrGet('href' if token.type == 'link_open' else 'src')
            for block in PARSER.parse(text) for token in block.children or []
            if token.type in ('link_open', 'image')}


def anchors(text):
    tokens = PARSER.parse(text)
    return {unicodedata.normalize('NFC', re.sub(r'[^\w\- ]', '', tokens[i + 1].content.lower()).replace(' ', '-'))
            for i, token in enumerate(tokens) if token.type == 'heading_open'}


def section_prose(tokens):
    sections = []
    in_heading = False
    for token in tokens:
        if token.type == 'heading_open':
            sections.append('')
            in_heading = True
        elif token.type == 'heading_close':
            in_heading = False
        elif token.type == 'inline' and not in_heading and sections:
            sections[-1] += token.content + '\n'
    return sections


def check_translation(folder):
    config = json.loads((folder / 'baseline.json').read_text(encoding='utf8'))
    assert os.environ.get('BOUNTY_REPO'), f"Set BOUNTY_REPO to your {config['repository']} branch checkout"
    repo = Path(os.environ['BOUNTY_REPO']).resolve()
    path = repo / config['translation']
    assert path.is_file(), f"Missing {config['translation']}; {config['language']} readers have no translated entry point"
    baseline = (folder / 'README.en.baseline.md').read_bytes()
    assert hashlib.sha256(baseline).hexdigest() == config['sha256'], 'Trusted English baseline hash mismatch'
    english = baseline.decode('utf8')
    assert english.count(config['navigationBefore']) == 1, 'Baseline navigation marker must be unique'
    expected = english.replace(config['navigationBefore'], config['navigationAfter'], 1).encode('utf8')
    assert (repo / 'README.md').read_bytes() == expected, 'Only the requested English language-navigation line may change'
    translated = path.read_text(encoding='utf8')
    required, actual = links(english), links(translated)
    assert required <= actual, f'Missing original link targets: {sorted(required - actual)}'
    urls = set(re.findall(r'https://[^\s<>`()]+', english))
    assert all(url.rstrip('.,;') in translated for url in urls), 'A bare URL or pinned command URL changed'
    for target in actual:
        assert target and not re.search(r'\s', target), f'Invalid Markdown target: {target!r}'
        parsed = urlsplit(target)
        if parsed.scheme:
            assert parsed.scheme == 'https' and parsed.hostname and not parsed.username and not parsed.password, f'Invalid external link: {target}'
            continue
        local = (path.parent / unquote(parsed.path)).resolve() if parsed.path else path
        assert local.is_relative_to(repo), f'Link escapes repository: {target}'
        assert local.is_file(), f'Broken local Markdown link: {target}'
        if parsed.fragment:
            assert unquote(parsed.fragment) in anchors(local.read_text(encoding='utf8')), f'Broken local anchor: {target}'
    original_tokens, translated_tokens = PARSER.parse(english), PARSER.parse(translated)
    fences = lambda tokens: [(t.info, t.content) for t in tokens if t.type == 'fence']
    assert fences(original_tokens) == fences(translated_tokens), 'Keep all fenced commands/prompts unchanged'
    headings = lambda tokens: [t.tag for t in tokens if t.type == 'heading_open']
    assert headings(original_tokens) == headings(translated_tokens), 'Translate every section with the same heading hierarchy'
    for index, (original, localized) in enumerate(zip(section_prose(original_tokens), section_prose(translated_tokens)), 1):
        assert len(localized.strip()) >= 0.6 * len(original.strip()), f'Section {index} needs translated prose, not just headings/navigation'
        if len(original.strip()) >= 80:
            normalized = lambda value: re.sub(r'\s+', ' ', value).strip().casefold()
            assert SequenceMatcher(None, normalized(original), normalized(localized), autojunk=False).ratio() < 0.85, f'Section {index} still copies English prose; translate the full section'
