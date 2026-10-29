"""Validate the processed Food-11 data contract without MLflow or torch."""
import argparse
import hashlib
from pathlib import Path

from PIL import Image

try:
    from .data import CLASSES, DEFAULT_SPLITS
except ImportError:
    from data import CLASSES, DEFAULT_SPLITS


def validate(root: Path, min_per_class: int = 50, tau: float = 0.05) -> dict[str, bool]:
    checks = dict.fromkeys(("class folders", "RGB 128x128 images", "minimum class counts",
                            "no cross-split duplicates", "class balance"), True)
    counts = {}
    seen = {}
    for split in DEFAULT_SPLITS:
        folder = root / split
        actual = {p.name for p in folder.iterdir() if p.is_dir()} if folder.is_dir() else set()
        checks["class folders"] &= actual == set(CLASSES)
        counts[split] = {}
        for category in CLASSES:
            directory = folder / category
            files = sorted(p for p in directory.rglob("*") if p.is_file()) if directory.is_dir() else []
            counts[split][category] = len(files)
            checks["minimum class counts"] &= len(files) >= min_per_class
            for path in files:
                try:
                    digest = hashlib.md5(path.read_bytes()).hexdigest()
                    if digest in seen and seen[digest] != split:
                        checks["no cross-split duplicates"] = False
                    seen.setdefault(digest, split)
                    with Image.open(path) as image:
                        image.load()
                        checks["RGB 128x128 images"] &= image.mode == "RGB" and image.size == (128, 128)
                except (OSError, ValueError, Image.DecompressionBombError):
                    checks["RGB 128x128 images"] = False
    train_total = sum(counts["training"].values())
    val_total = sum(counts["validation"].values())
    checks["class balance"] = bool(train_total and val_total) and all(
        abs(counts["training"][c] / train_total - counts["validation"][c] / val_total) <= tau
        for c in CLASSES
    )
    return checks


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("root", type=Path)
    parser.add_argument("--min-per-class", type=int, default=50)
    parser.add_argument("--tau", type=float, default=0.05)
    args = parser.parse_args()
    if args.min_per_class < 1 or not 0 <= args.tau <= 1:
        parser.error("min-per-class must be positive and tau must be between 0 and 1")
    checks = validate(args.root, args.min_per_class, args.tau)
    for name, passed in checks.items():
        print(f"{'PASS' if passed else 'FAIL'}: {name}")
    raise SystemExit(0 if all(checks.values()) else 1)


if __name__ == "__main__":
    main()
