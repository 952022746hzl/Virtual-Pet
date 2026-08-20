"""台词加载与随机抽取。纯逻辑，不依赖 Qt。"""
import json
import random
from pathlib import Path


def load_quotes(path):
    data = json.loads(Path(path).read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise ValueError("quotes.json 顶层必须是对象")
    for scene, lines in data.items():
        if not isinstance(lines, list) or not lines or not all(isinstance(x, str) for x in lines):
            raise ValueError(f"场景 {scene!r} 必须是非空字符串列表")
    return data


def pick(quotes, scene, rng=None):
    lines = quotes.get(scene)
    if not lines:
        return None
    return (rng or random).choice(lines)
