"""One parametrized acceptance check, selected with BOUNTY_TASK."""
import os

import pytest

from translation_check import check_translation, load_task


@pytest.mark.parametrize('task', [os.environ.get('BOUNTY_TASK', '')])
def test_readme_translation(task):
    assert task, 'Set BOUNTY_TASK to cli-ko, mcp-ja or remote-zh-CN (see README.md)'
    assert os.environ.get('BOUNTY_REPO'), 'Set BOUNTY_REPO to the target branch checkout'
    config, baseline = load_task(task)
    assert os.environ.get('BOUNTY_LANGUAGE', config['language']) == config['language'], 'Language must match the pinned task'
    assert os.environ.get('BOUNTY_FILE', config['translation']) == config['translation'], 'Target file must match the pinned task'
    check_translation(os.environ['BOUNTY_REPO'], config, baseline)
