from __future__ import annotations

import shutil
from collections import defaultdict
from pathlib import Path

from PIL import Image

DEFAULT_SPLITS = ("training", "evaluation", "validation")
FOOD11_CLASSES = [
    "Bread",
    "Dairy product",
    "Dessert",
    "Egg",
    "Fried food",
    "Meat",
    "Noodles/Pasta",
    "Rice",
    "Seafood",
    "Soup",
    "Vegetable/Fruit",
]


def _extract_label(file_name: str) -> int | None:
    stem = Path(file_name).stem
    if "_" not in stem:
        return None
    label_part, _ = stem.split("_", 1)
    try:
        return int(label_part)
    except ValueError:
        return None


def _label_to_class_name(label: int) -> str:
    if 0 <= label < len(FOOD11_CLASSES):
        return FOOD11_CLASSES[label]
    raise ValueError(f"Unsupported Food-11 label: {label}")


def _copy_resized_image(source_file: Path, target_file: Path) -> None:
    with Image.open(source_file) as image:
        resized_image = image.resize((128, 128), Image.Resampling.LANCZOS)
        resized_image.save(target_file)


def prepare_food11_data(
    raw_root: str | Path = "data/food11_raw",
    processed_root: str | Path = "data/food11_processed",
    mini_root: str | Path = "data/food11_processed_mini",
    max_per_class: int | None = 100,
) -> dict[str, Path]:
    if max_per_class is not None and max_per_class < 0:
        raise ValueError("max_per_class must be non-negative or None")

    raw_root = Path(raw_root)
    processed_root = Path(processed_root)
    mini_root = Path(mini_root)

    if not raw_root.exists():
        raise FileNotFoundError(f"Raw dataset not found at: {raw_root}")

    for target_root in (processed_root, mini_root):
        if target_root.exists():
            shutil.rmtree(target_root)

    files_by_split_and_class: dict[str, dict[int, list[Path]]] = {
        split: defaultdict(list) for split in DEFAULT_SPLITS
    }

    for split in DEFAULT_SPLITS:
        split_dir = raw_root / split
        if not split_dir.exists():
            continue

        for image_path in sorted(split_dir.iterdir()):
            if not image_path.is_file():
                continue
            if image_path.suffix.lower() not in {".jpg", ".jpeg", ".png"}:
                continue

            label = _extract_label(image_path.name)
            if label is None:
                continue

            files_by_split_and_class[split][label].append(image_path)

    for split in DEFAULT_SPLITS:
        for label, class_name in enumerate(FOOD11_CLASSES):
            source_files = files_by_split_and_class.get(split, {}).get(label, [])
            target_dir = processed_root / split / class_name
            target_dir.mkdir(parents=True, exist_ok=True)

            for source_file in source_files:
                _copy_resized_image(source_file, target_dir / source_file.name)

            mini_dir = mini_root / split / class_name
            mini_dir.mkdir(parents=True, exist_ok=True)

            if max_per_class is None:
                files_to_copy = source_files
            else:
                files_to_copy = source_files[:max_per_class]

            for source_file in files_to_copy:
                _copy_resized_image(source_file, mini_dir / source_file.name)

    return {"raw_root": raw_root, "processed_root": processed_root, "mini_root": mini_root}


if __name__ == "__main__":
    result = prepare_food11_data()
    print(f"Prepared processed data in {result['processed_root']}")
    print(f"Prepared mini dataset in {result['mini_root']}")
