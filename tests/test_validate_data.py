import shutil

from PIL import Image

from food11.data import CLASSES, DEFAULT_SPLITS
from food11.validate_data import validate


def test_contract_and_cross_split_leakage(tmp_path):
    for i, split in enumerate(DEFAULT_SPLITS):
        for j, category in enumerate(CLASSES):
            folder = tmp_path / split / category
            folder.mkdir(parents=True)
            Image.new("RGB", (128, 128), (i * 60, j * 20, 0)).save(folder / "image.png")
    assert all(validate(tmp_path, min_per_class=1).values())
    source = tmp_path / "training" / "Bread" / "image.png"
    target = tmp_path / "evaluation" / "Bread" / "leak.png"
    shutil.copy2(source, target)
    assert not validate(tmp_path, min_per_class=1)["no cross-split duplicates"]
    target.unlink()
    Image.new("L", (10, 10)).save(source)
    assert not validate(tmp_path, min_per_class=1)["RGB 128x128 images"]
