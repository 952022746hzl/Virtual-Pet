from pathlib import Path

from pet.sprite import ACTIONS, discover_frames


def make_png(path: Path):
    path.write_bytes(b"\x89PNG\r\n\x1a\n")  # 只测发现逻辑，内容无需合法


def test_discover_groups_and_sorts_frames(tmp_path):
    for name in ["walk_0.png", "walk_2.png", "walk_1.png", "idle_0.png",
                 "cover.jpg", "walk_x.png", "notes.txt"]:
        make_png(tmp_path / name)
    frames = discover_frames(tmp_path)
    assert list(frames["walk"]) == [tmp_path / "walk_0.png", tmp_path / "walk_1.png", tmp_path / "walk_2.png"]
    assert "idle" in frames
    assert set(frames) == {"walk", "idle"}


def test_discover_missing_dir_returns_empty(tmp_path):
    assert discover_frames(tmp_path / "nope") == {}


def test_actions_match_spec():
    assert ACTIONS == ["idle", "walk", "bow", "sleep", "dragged", "land", "coffee", "special"]
