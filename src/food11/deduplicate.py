"""Remove cross-split duplicates from derived datasets, keeping evaluation first."""
import argparse
import hashlib
import json
from pathlib import Path

# Preserve the held-out split, then validation; remove overlap from training.
SPLIT_PRIORITY = ("evaluation", "validation", "training")


def deduplicate_dataset(root: Path, *, apply: bool = False) -> list[dict[str, str]]:
    root = Path(root).resolve()
    if not root.is_dir():
        raise FileNotFoundError(root)
    seen: dict[str, tuple[str, Path]] = {}
    duplicates = []
    for split in SPLIT_PRIORITY:
        folder = root / split
        if folder.is_symlink():
            raise ValueError(f"Unsafe split path: {folder}")
        if not folder.is_dir():
            raise ValueError(f"Missing split: {folder}")
        for path in sorted(folder.rglob("*")):
            if not path.is_file():
                continue
            # Never follow a dataset symlink to remove files outside this root.
            # rglob does not recurse through directory symlinks. The resolved
            # root and non-symlink split keep regular files inside the dataset.
            if path.is_symlink() or not path.is_relative_to(root):
                raise ValueError(f"Unsafe dataset path: {path}")
            digest = hashlib.md5(path.read_bytes()).hexdigest()
            previous = seen.get(digest)
            if previous is not None and previous[0] != split:
                duplicates.append({"removed": str(path.relative_to(root)).replace("\\", "/"),
                                   "kept": str(previous[1].relative_to(root)).replace("\\", "/"),
                                   "md5": digest})
            else:
                seen.setdefault(digest, (split, path))
    # Scan completely before changing anything, so missing splits fail safely.
    if apply:
        for duplicate in duplicates:
            target = (root / duplicate["removed"]).resolve()
            if not target.is_relative_to(root):
                raise ValueError(f"Unsafe removal path: {target}")
            target.unlink()
    return duplicates


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("roots", type=Path, nargs="+")
    parser.add_argument("--apply", action="store_true", help="Remove duplicates; default is a dry run")
    parser.add_argument("--report", type=Path)
    args = parser.parse_args()
    report = {"applied": args.apply, "priority": list(SPLIT_PRIORITY), "datasets": {}}
    for root in args.roots:
        duplicates = deduplicate_dataset(root, apply=args.apply)
        report["datasets"][root.as_posix()] = duplicates
        print(f"{root}: {len(duplicates)} cross-split duplicates {'removed' if args.apply else 'found'}")
    if args.report:
        args.report.parent.mkdir(parents=True, exist_ok=True)
        args.report.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
