import argparse
from pathlib import Path

from food11.data import prepare_food11_data


def main() -> None:
    parser = argparse.ArgumentParser(description="Prepare the Food-11 datasets.")
    parser.add_argument("--raw-root", type=Path, default=Path("data/food11_raw"))
    parser.add_argument("--processed-root", type=Path, default=Path("data/food11_processed"))
    parser.add_argument("--mini-root", type=Path, default=Path("data/food11_processed_mini"))
    parser.add_argument("--max-per-class", type=int, default=100)
    args = parser.parse_args()

    result = prepare_food11_data(
        raw_root=args.raw_root,
        processed_root=args.processed_root,
        mini_root=args.mini_root,
        max_per_class=args.max_per_class,
    )
    print(f"Prepared processed data in {result['processed_root']}")
    print(f"Prepared mini dataset in {result['mini_root']}")
