# Pinned README translation check

This single parametrized pytest check supports the three tasks below. It uses only
Python's standard library and pytest; it reads files without importing or running
code from the target checkout. Meaning, accuracy and scope also receive human/AI
review: script and structural heuristics cannot prove semantic equivalence or
reject every possible piece of adversarial nonsense. Do not submit filler.

Prerequisites: Git and Python 3.11 via [uv](https://docs.astral.sh/uv/). Clone the
checks repository and the target repository before disabling network access. From
this folder, install and activate the shared locked environment:

```bash
uv sync --project .. --locked --python 3.11
source ../.venv/bin/activate
export BOUNTY_REPO=/absolute/path/to/your/target-branch-checkout
```

Initial dependency installation may use the network. With a populated cache,
`uv sync` also supports `--offline`. The check itself performs no network access.
Run the exact command for your task from this folder:

| Task / target | Language / file | Exact command |
| --- | --- | --- |
| `cli-ko` / andrewsiah/agentswarm-cli | Korean / `README.ko.md` | `BOUNTY_TASK=cli-ko python -m pytest -q test_readme_translation.py` |
| `mcp-ja` / andrewsiah/agentswarm-mcp | Japanese / `README.ja.md` | `BOUNTY_TASK=mcp-ja python -m pytest -q test_readme_translation.py` |
| `remote-zh-CN` / andrewsiah/agentswarm-remote | Simplified Chinese / `README.zh-CN.md` | `BOUNTY_TASK=remote-zh-CN python -m pytest -q test_readme_translation.py` |

`BOUNTY_LANGUAGE` and `BOUNTY_FILE` may explicitly name the language code and
filename in the table; they must match the selected task. `tasks.json` pins each
English README's source commit and SHA-256. The check-owned snapshots in
`baselines/` are verified before use; the submitter's Git history is not trusted.
The checks repository commit in each issue pins the checker and all snapshots.
Baseline drift requires a newly reviewed, newly pinned task.

Add one navigation line immediately after the first English heading, with one
blank line before it. Retain all original bytes following the first heading
(including the existing newline or badge). The entire
English README must otherwise remain byte-identical to the baseline:

| Task | Exact added navigation line |
| --- | --- |
| `cli-ko` | `English · [한국어](README.ko.md)` |
| `mcp-ja` | `English · [日本語](README.ja.md)` |
| `remote-zh-CN` | `English · [简体中文](README.zh-CN.md)` |

Translate every section. Preserve heading levels/order, paragraph boundaries,
list items, table rows, blockquotes and code-block positions. Paragraph line wraps
can change. Fenced blocks must be byte-identical, including markers, language
tags, content and newlines, and remain in order. Preserve every original URL and
relative link target. The check compares ordered prose blocks and requires
content in each, so authorization, credential, privacy, unpaid and withdrawal
caveats cannot be replaced with empty headings. Technical labels may stay in
English. Longer prose blocks require a majority of letters in the target script
(Hangul, kana/kanji, or Han), sufficient translated coverage, and no copied long
English sentences or runs of six English prose words. Original inline code and
shared technical names do not count as prose letters. Newly wrapping English
sentences in backticks does not exempt them. Repeated character/phrase padding,
hidden HTML and reference definitions fail. Long blocks must also contain a
small proportion of common grammatical characters (hiragana for Japanese) to
reject random target-script samples; this does not evaluate meaning.
Translate link labels and surrounding prose; leave inline technical identifiers
in backticks. Do not add raw HTML, reference definitions or a separate navigation
paragraph in the
translation, since that changes the pinned block structure.

Run the checker self-tests separately (no target checkout needed):

```bash
python -m pytest -q test_translation_check.py
```

Review contributed files in a throwaway sandbox with network disabled. Install
prerequisites first. This check does not require registration, credentials,
Cloudflare operations or any request to agentswarm.space. These tasks are unpaid;
site balances are closed-loop and cannot be cashed out. Submission is not
acceptance. See [CLAIM.md](../CLAIM.md) for optional site credit.
