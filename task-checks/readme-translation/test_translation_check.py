"""Offline fixtures for the translation checker, without BOUNTY_REPO."""
import pytest

from translation_check import check_translation, load_task, parse

ENGLISH = '''# Example

Find useful tasks and read the requirements before contributing.

## Authorization and credentials

Choose work within your human's authorization. Never share your private credentials.

```sh
example tasks --limit 3
```

## Limits

Plain tasks may be unpaid. Site balances cannot be cashed out yet. Submission is not acceptance.

See [documentation](docs/guide.md) and https://example.org/api.
'''
TRANSLATIONS = {
    'ko': '''# 예제

유용한 작업을 찾고 기여하기 전에 요구 사항을 읽으세요.

## 권한과 자격 증명

담당자의 허가 범위 안에서 작업을 선택하세요. 개인 자격 증명을 절대 공유하지 마세요.

```sh
example tasks --limit 3
```

## 제한 사항

일반 작업은 무급일 수 있습니다. 사이트 잔액은 아직 현금으로 인출할 수 없습니다. 제출이 승인을 뜻하지는 않습니다.

[문서](docs/guide.md)와 https://example.org/api 를 참조하세요.
''',
    'ja': '''# 使用例

役に立つ作業を探して、貢献する前に要件を読んでください。

## 許可と認証情報

担当者が許可した範囲内で作業を選んでください。秘密の認証情報は絶対に共有しないでください。

```sh
example tasks --limit 3
```

## 制限事項

通常の作業は無報酬の場合があります。サイトの残高はまだ現金化できません。提出しても承認されるとは限りません。

[説明書](docs/guide.md)と https://example.org/api を参照してください。
''',
    'zh-CN': '''# 使用示例

寻找有用的任务，并在参与之前阅读要求。

## 授权与凭据

请在负责人授权的范围内选择任务。切勿分享您的私密凭据。

```sh
example tasks --limit 3
```

## 限制说明

普通任务可能没有报酬。网站余额目前无法提现。提交并不代表已被接受。

请参阅[文档](docs/guide.md)和 https://example.org/api。
''',
}


def fixture(tmp_path, language='ko'):
    config = {'translation': f'README.{language}.md', 'language': language,
              'navigation': f'English · [Translation](README.{language}.md)'}
    (tmp_path / 'README.md').write_text(ENGLISH.replace('# Example\n', '# Example\n\n' + config['navigation'] + '\n', 1))
    (tmp_path / config['translation']).write_text(TRANSLATIONS[language])
    return config


@pytest.mark.parametrize('language', TRANSLATIONS)
def test_genuine_translations_pass(tmp_path, language):
    config = fixture(tmp_path, language)
    check_translation(tmp_path, config, ENGLISH.encode())


@pytest.mark.parametrize('attack', [
    'missing_file', 'machine_garbage', 'missing_code', 'changed_code', 'latin_only',
    'changed_english', 'missing_caveat', 'english_padding', 'missing_link',
    'hidden_script', 'wrong_language', 'heading_level', 'repeated_filler',
])
def test_invalid_translation_fails(tmp_path, attack):
    config = fixture(tmp_path)
    path = tmp_path / config['translation']
    translated = path.read_text()
    if attack == 'missing_file':
        path.unlink()
    elif attack == 'machine_garbage':
        translated = '\n'.join(kind if kind == 'fence' else '가' * 200 for kind, _ in parse(ENGLISH)[2])
    elif attack == 'missing_code':
        translated = translated.replace('```sh\nexample tasks --limit 3\n```\n', '')
    elif attack == 'changed_code':
        translated = translated.replace('--limit 3', '--limit 4')
    elif attack == 'latin_only':
        translated = ENGLISH
    elif attack == 'changed_english':
        (tmp_path / 'README.md').write_text('changed English')
    elif attack == 'missing_caveat':
        translated = translated.replace('일반 작업은 무급일 수 있습니다. 사이트 잔액은 아직 현금으로 인출할 수 없습니다. 제출이 승인을 뜻하지는 않습니다.\n', '')
    elif attack == 'english_padding':
        translated = translated.replace('유용한 작업을 찾고 기여하기 전에 요구 사항을 읽으세요.', ENGLISH.split('\n\n')[1] + ' 번역된 내용입니다.' * 30)
    elif attack == 'missing_link':
        translated = translated.replace('docs/guide.md', 'docs/wrong.md')
    elif attack == 'hidden_script':
        translated = ENGLISH + '\n<!-- ' + TRANSLATIONS['ko'] * 10 + ' -->\n'
    elif attack == 'wrong_language':
        translated = TRANSLATIONS['ja']
    elif attack == 'heading_level':
        translated = translated.replace('## 제한', '### 제한')
    elif attack == 'repeated_filler':
        translated = translated.replace('유용한 작업을 찾고 기여하기 전에 요구 사항을 읽으세요.', '가나다라마바사' * 100)
    if path.exists():
        path.write_text(translated)
    with pytest.raises(AssertionError):
        check_translation(tmp_path, config, ENGLISH.encode())


@pytest.mark.parametrize('task', ['cli-ko', 'mcp-ja', 'remote-zh-CN', 'cli-ja', 'mcp-ko', 'work-skill-ja'])
def test_pinned_baselines(task):
    config, baseline = load_task(task)
    assert len(config['commit']) == 40
    assert parse(baseline.decode())[0]


@pytest.mark.parametrize('task,repository,language', [
    ('cli-ja', 'andrewsiah/agentswarm-cli', 'ja'),
    ('mcp-ko', 'andrewsiah/agentswarm-mcp', 'ko'),
    ('work-skill-ja', 'andrewsiah/agentswarm-work-skill', 'ja'),
])
def test_new_task_genuine_translation_fixture_passes(tmp_path, task, repository, language):
    config, _ = load_task(task)
    assert config['repository'] == repository
    assert config['language'] == language
    assert config['translation'] == f'README.{language}.md'
    english = ENGLISH.replace('# Example\n', '# Example\n\n' + config['navigation'] + '\n', 1)
    (tmp_path / 'README.md').write_text(english)
    (tmp_path / config['translation']).write_text(TRANSLATIONS[language])
    check_translation(tmp_path, config, ENGLISH.encode())


def test_raw_fence_bytes_preserved():
    assert parse('# One\n\n```sh\nhello\r\n```\n')[1] == ['```sh\nhello\r\n```\n']


@pytest.mark.parametrize('language', TRANSLATIONS)
def test_random_script_junk_with_intact_structure_fails(tmp_path, language):
    import random
    config = fixture(tmp_path, language)
    path = tmp_path / config['translation']
    good_paragraph = TRANSLATIONS[language].split('\n\n')[1]
    start, stop = (0xAC00, 0xD7A4) if language == 'ko' else (0x4E00, 0xA000)
    garbage = ''.join(chr(value) for value in random.Random(102).sample(range(start, stop), 200))
    path.write_text(path.read_text().replace(good_paragraph, garbage))
    with pytest.raises(AssertionError, match='random script garbage'):
        check_translation(tmp_path, config, ENGLISH.encode())


@pytest.mark.parametrize('prefix', ['', '> ', '- '])
def test_invisible_reference_definition_cannot_replace_caveat(tmp_path, prefix):
    config = fixture(tmp_path)
    path = tmp_path / config['translation']
    original = ENGLISH.split('\n\n')[3]
    baseline = ENGLISH.replace(original, prefix + original)
    (tmp_path / 'README.md').write_text(baseline.replace('# Example\n', '# Example\n\n' + config['navigation'] + '\n', 1))
    paragraph = TRANSLATIONS['ko'].split('\n\n')[3]
    path.write_text(path.read_text().replace(paragraph, f'{prefix}[hidden]: / "{paragraph}"'))
    with pytest.raises(AssertionError, match='Reference definitions'):
        check_translation(tmp_path, config, baseline.encode())


@pytest.mark.parametrize('wrapper', ['spaces', 'backticks'])
def test_english_cannot_be_hidden_by_formatting(tmp_path, wrapper):
    config = fixture(tmp_path)
    path = tmp_path / config['translation']
    original = ENGLISH.split('\n\n')[1]
    copied = original.replace(' ', '  ') if wrapper == 'spaces' else f'`` {original} ``'
    korean_padding = ('유용한 작업을 찾고 기여하기 전에 요구 사항을 읽으세요. '
                      '담당자의 허가 범위 안에서 작업을 선택하세요. 개인 자격 증명을 절대 공유하지 마세요. '
                      '일반 작업은 무급일 수 있습니다. 사이트 잔액은 아직 현금으로 인출할 수 없습니다. 제출이 승인을 뜻하지는 않습니다.')
    path.write_text(path.read_text().replace(TRANSLATIONS['ko'].split('\n\n')[1], copied + ' ' + korean_padding))
    with pytest.raises(AssertionError, match='untranslated English'):
        check_translation(tmp_path, config, ENGLISH.encode())


def test_natural_short_korean_heading_passes(tmp_path):
    config = fixture(tmp_path)
    baseline = '# The key\n\n' + ENGLISH.split('\n\n', 1)[1]
    path = tmp_path / config['translation']
    path.write_text(path.read_text().replace('# 예제', '# 키'))
    (tmp_path / 'README.md').write_text(baseline.replace('# The key\n', '# The key\n\n' + config['navigation'] + '\n', 1))
    check_translation(tmp_path, config, baseline.encode())


@pytest.mark.parametrize('language,localized', [
    ('ja', '各種フレームワークの使用例（OpenAI Agents SDK、LangGraph、Claude Agent SDK、Pi、通常のPython）はこちらです: https://example.org/frameworks'),
    ('zh-CN', '各类框架的使用示例（OpenAI Agents SDK、LangGraph、Claude Agent SDK、Pi、普通 Python）：https://example.org/frameworks'),
])
def test_technical_names_do_not_cause_false_language_rejection(tmp_path, language, localized):
    config = fixture(tmp_path, language)
    source = ENGLISH.split('\n\n')[1]
    technical = 'Framework examples (OpenAI Agents SDK, LangGraph, Claude Agent SDK, Pi, plain Python): https://example.org/frameworks'
    baseline = ENGLISH.replace(source, technical)
    (tmp_path / 'README.md').write_text(baseline.replace('# Example\n', '# Example\n\n' + config['navigation'] + '\n', 1))
    path = tmp_path / config['translation']
    path.write_text(path.read_text().replace(TRANSLATIONS[language].split('\n\n')[1], localized))
    check_translation(tmp_path, config, baseline.encode())


@pytest.mark.parametrize('target', ['docs/guide.md', 'https://example.org/docs'])
def test_explicit_link_destination_punctuation_is_exact(tmp_path, target):
    config = fixture(tmp_path)
    source = ENGLISH.replace('docs/guide.md', target)
    (tmp_path / 'README.md').write_text(source.replace('# Example\n', '# Example\n\n' + config['navigation'] + '\n', 1))
    path = tmp_path / config['translation']
    path.write_text(path.read_text().replace('docs/guide.md', target + '.'))
    with pytest.raises(AssertionError, match='Missing URLs or relative links'):
        check_translation(tmp_path, config, source.encode())
