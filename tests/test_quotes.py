import json
import random
from pathlib import Path

import pytest

from pet.quotes import load_quotes, pick

REPO_ROOT = Path(__file__).resolve().parent.parent


def test_load_real_quotes_file():
    quotes = load_quotes(REPO_ROOT / "quotes.json")
    for scene in ["click", "coffee", "cancel_overtime", "refund_salary", "wake", "land_hard"]:
        assert scene in quotes
        assert quotes[scene], f"场景 {scene} 台词为空"


def test_load_rejects_bad_structure(tmp_path):
    bad = tmp_path / "bad.json"
    bad.write_text(json.dumps({"click": "不是列表"}), encoding="utf-8")
    with pytest.raises(ValueError):
        load_quotes(bad)


def test_pick_is_deterministic_with_seeded_rng():
    quotes = {"click": ["a", "b", "c"]}
    assert pick(quotes, "click", random.Random(42)) == pick(quotes, "click", random.Random(42))


def test_pick_unknown_scene_returns_none():
    assert pick({"click": ["a"]}, "nope") is None
