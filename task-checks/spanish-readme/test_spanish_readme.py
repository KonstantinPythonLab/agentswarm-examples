"""Offline Markdown link validation: no external URL is fetched."""
import hashlib
import os
from pathlib import Path
import re
import unicodedata
from urllib.parse import unquote, urlsplit

from markdown_it import MarkdownIt

assert os.environ.get('BOUNTY_REPO'), 'Set BOUNTY_REPO to your agentswarm-work-skill branch checkout.'
REPO = Path(os.environ['BOUNTY_REPO']).resolve()
assert (REPO / 'README.md').is_file(), 'BOUNTY_REPO must contain README.md'
PARSER = MarkdownIt('commonmark')
BASELINE = Path(__file__).with_name('README.en.baseline.md')
BASELINE_SHA256 = Path(__file__).with_name('README.en.baseline.sha256').read_text().split()[0]
NAVIGATION = 'English · [简体中文](README.zh-CN.md)'
SPANISH_NAVIGATION = NAVIGATION + ' · [Español](README.es.md)'

def links(text):
    targets = set()
    for block in PARSER.parse(text):
        for token in block.children or []:
            if token.type in ('link_open', 'image'):
                targets.add(token.attrGet('href' if token.type == 'link_open' else 'src'))
    return targets

def anchors(text):
    tokens = PARSER.parse(text)
    found = set()
    for index, token in enumerate(tokens):
        if token.type == 'heading_open':
            title = tokens[index + 1].content.lower()
            slug = re.sub(r'[^\w\- ]', '', title, flags=re.UNICODE).replace(' ', '-')
            found.add(unicodedata.normalize('NFC', slug))
    return found

def section_prose(tokens):
    # Exclude headings and fences so headings/navigation/examples alone cannot pass.
    sections = []
    in_heading = False
    for token in tokens:
        if token.type == 'heading_open':
            sections.append('')
            in_heading = True
        elif token.type == 'heading_close':
            in_heading = False
        elif token.type == 'inline' and not in_heading and sections:
            sections[-1] += token.content
    return sections


def test_spanish_readme_preserves_links_and_valid_markdown():
    path = REPO / 'README.es.md'
    assert path.is_file(), 'Missing README.es.md; Spanish readers have no translated entry point'
    baseline = BASELINE.read_bytes()
    assert hashlib.sha256(baseline).hexdigest() == BASELINE_SHA256, 'Trusted English baseline hash mismatch'
    english = baseline.decode('utf8')
    submitted_english = (REPO / 'README.md').read_bytes()
    expected_english = english.replace(NAVIGATION, SPANISH_NAVIGATION, 1).encode('utf8')
    assert submitted_english == expected_english, 'Only the requested English language-navigation line may change'
    spanish = path.read_text(encoding='utf8')
    required = links(english)
    actual = links(spanish)
    assert required <= actual, f'Missing original link targets: {sorted(required - actual)}'
    urls = set(re.findall(r'https://[^\s<>`()]+', english))
    assert all(url.rstrip('.,;') in spanish for url in urls), 'A bare URL or pinned command URL changed'
    for target in actual:
        assert target and not re.search(r'\s', target), f'Invalid Markdown target: {target!r}'
        parsed = urlsplit(target)
        if parsed.scheme:
            assert parsed.scheme == 'https' and parsed.hostname and not parsed.username and not parsed.password, f'Invalid external link: {target}'
            continue
        local = (path.parent / unquote(parsed.path)).resolve() if parsed.path else path
        assert local.is_relative_to(REPO), f'Link escapes repository: {target}'
        assert local.is_file(), f'Broken local Markdown link: {target}'
        if parsed.fragment:
            assert unquote(parsed.fragment) in anchors(local.read_text(encoding='utf8')), f'Broken local anchor: {target}'
    english_tokens = PARSER.parse(english)
    spanish_tokens = PARSER.parse(spanish)
    assert [t.content for t in english_tokens if t.type == 'fence'] == [t.content for t in spanish_tokens if t.type == 'fence'], 'Keep all command/prompt blocks unchanged'
    assert sum(t.type == 'heading_open' for t in spanish_tokens) == sum(t.type == 'heading_open' for t in english_tokens), 'Translate every section'
    for index, (original, translated) in enumerate(zip(section_prose(english_tokens), section_prose(spanish_tokens)), 1):
        assert len(translated.strip()) >= 0.6 * len(original.strip()), f'Section {index} needs translated prose, not just headings/navigation'
