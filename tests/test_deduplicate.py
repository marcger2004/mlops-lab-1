from pathlib import Path
import shutil

from PIL import Image

from food11.data import prepare_food11_data
from food11.deduplicate import deduplicate_dataset
from food11.validate_data import validate


def test_dry_run_then_cleanup_preserves_evaluation(tmp_path):
    for split in ("training", "validation", "evaluation"):
        folder = tmp_path / split / "Bread"
        folder.mkdir(parents=True)
        Image.new("RGB", (128, 128), (10, 20, 30)).save(folder / "duplicate.png")
    plan = deduplicate_dataset(tmp_path)
    assert len(plan) == 2
    assert (tmp_path / "training/Bread/duplicate.png").exists()
    assert all(row["kept"] == "evaluation/Bread/duplicate.png" for row in plan)
    assert deduplicate_dataset(tmp_path, apply=True) == plan
    assert (tmp_path / "evaluation/Bread/duplicate.png").exists()
    assert not (tmp_path / "training/Bread/duplicate.png").exists()
    assert not (tmp_path / "validation/Bread/duplicate.png").exists()
    assert deduplicate_dataset(tmp_path, apply=True) == []
    assert validate(tmp_path, min_per_class=1)["no cross-split duplicates"]


def test_preparation_deduplicates_outputs_and_keeps_raw(tmp_path):
    raw = tmp_path / "raw"
    for split in ("training", "validation", "evaluation"):
        (raw / split).mkdir(parents=True)
    original = raw / "evaluation/0_0.png"
    Image.new("RGB", (128, 128), (50, 60, 70)).save(original)
    shutil.copy2(original, raw / "training/0_1.png")
    result = prepare_food11_data(raw, tmp_path / "processed", tmp_path / "mini")
    for key in ("processed_root", "mini_root"):
        root = Path(result[key])
        assert (root / "evaluation/Bread/0_0.png").exists()
        assert not (root / "training/Bread/0_1.png").exists()
    assert (raw / "training/0_1.png").exists()
    assert original.exists()
