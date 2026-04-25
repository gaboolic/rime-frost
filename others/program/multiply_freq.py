import argparse
from pathlib import Path


DEFAULT_DIRS = ("cn_dicts", "cn_dicts_cell")
DEFAULT_FACTOR = 18000


def iter_dict_files(root: Path, dict_dirs: tuple[str, ...]):
    for dict_dir in dict_dirs:
        target_dir = root / dict_dir
        if not target_dir.exists():
            continue
        yield from sorted(target_dir.glob("*.dict.yaml"))


def multiply_freq_in_line(line: str, factor: int) -> tuple[str, bool]:
    line_body = line.rstrip("\n")
    newline = "\n" if line.endswith("\n") else ""

    if "\t" not in line_body or line_body.startswith("#"):
        return line, False

    parts = line_body.split("\t")
    if len(parts) < 3:
        return line, False

    freq = parts[2]
    if not freq.isdigit():
        return line, False

    parts[2] = str(int(freq) * factor)
    return "\t".join(parts) + newline, True


def multiply_file_freq(file_path: Path, factor: int, dry_run: bool) -> int:
    lines = file_path.read_text(encoding="utf-8").splitlines(keepends=True)
    changed_count = 0
    new_lines = []

    for line in lines:
        new_line, changed = multiply_freq_in_line(line, factor)
        new_lines.append(new_line)
        if changed:
            changed_count += 1

    if changed_count and not dry_run:
        file_path.write_text("".join(new_lines), encoding="utf-8")

    return changed_count


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Multiply frequencies in Rime dictionary files."
    )
    parser.add_argument(
        "--factor",
        type=int,
        default=DEFAULT_FACTOR,
        help=f"frequency multiplier, default: {DEFAULT_FACTOR}",
    )
    parser.add_argument(
        "--dirs",
        nargs="+",
        default=list(DEFAULT_DIRS),
        help="dictionary directories to process",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="only print how many entries would be changed",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    root = Path(__file__).resolve().parents[2]
    total = 0

    for file_path in iter_dict_files(root, tuple(args.dirs)):
        changed_count = multiply_file_freq(file_path, args.factor, args.dry_run)
        total += changed_count
        print(f"{file_path.relative_to(root)}: {changed_count}")

    action = "would update" if args.dry_run else "updated"
    print(f"{action} {total} entries")


if __name__ == "__main__":
    main()
