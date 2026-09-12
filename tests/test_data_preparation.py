from pathlib import Path

import sys

from PIL import Image

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from food11.data import prepare_food11_data


def test_prepare_food11_data_rejects_negative_limit(tmp_path):
    raw_root = tmp_path / "food11_raw"
    raw_root.mkdir()

    try:
        prepare_food11_data(raw_root=raw_root, max_per_class=-1)
    except ValueError as error:
        assert str(error) == "max_per_class must be non-negative or None"
    else:
        raise AssertionError("negative max_per_class should be rejected")


def test_prepare_food11_data_creates_processed_folders_and_limits_mini_dataset(tmp_path):
    raw_root = tmp_path / "food11_raw"
    for split in ["training", "evaluation", "validation"]:
        (raw_root / split).mkdir(parents=True)

    categories = [
        "Bread",
        "Dairy product",
        "Dessert",
    ]


    for idx, category in enumerate(categories):
        for split in ["training", "evaluation", "validation"]:
            for i in range(120):
                image = Image.new("RGB", (512, 512), color=(idx * 40, i, 0))
                image.save(raw_root / split / f"{idx}_{i}.jpg")

    processed_root = tmp_path / "food11_processed"
    mini_root = tmp_path / "food11_processed_mini"

    prepare_food11_data(raw_root=raw_root, processed_root=processed_root, mini_root=mini_root, max_per_class=100)

    for split in ["training", "evaluation", "validation"]:
        for category in categories:
            output_dir = processed_root / split / category
            assert output_dir.exists()
            assert len(list(output_dir.iterdir())) == 120
            assert Image.open(next(output_dir.iterdir())).size == (128, 128)

            mini_dir = mini_root / split / category
            assert mini_dir.exists()
            assert len(list(mini_dir.iterdir())) == 100
