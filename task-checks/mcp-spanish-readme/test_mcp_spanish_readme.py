"""Check the requested translation using the trusted shared checker."""
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from readme_translation import check_translation


def test_readme_translation():
    check_translation(Path(__file__).resolve().parent)
