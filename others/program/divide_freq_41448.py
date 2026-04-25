import argparse
from pathlib import Path


DEFAULT_FILE = Path("cn_dicts") / "41448.dict.yaml"
DEFAULT_DIVISOR = 10


def divide_freq_in_line(line: str, divisor: int) -> tuple[str, bool]:
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

    parts[2] = str(int(freq) // divisor)
    return "\t".join(parts) + newline, True


def divide_file_freq(file_path: Path, divisor: int, dry_run: bool) -> int:
    lines = file_path.read_text(encoding="utf-8").splitlines(keepends=True)
    changed_count = 0
    new_lines = []

    for line in lines:
        new_line, changed = divide_freq_in_line(line, divisor)
        new_lines.append(new_line)
        if changed:
            changed_count += 1

    if changed_count and not dry_run:
        file_path.write_text("".join(new_lines), encoding="utf-8")

    return changed_count


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Divide frequencies in cn_dicts/41448.dict.yaml."
    )
    parser.add_argument(
        "--file",
        default=str(DEFAULT_FILE),
        help=f"dictionary file to process, default: {DEFAULT_FILE}",
    )
    parser.add_argument(
        "--divisor",
        type=int,
        default=DEFAULT_DIVISOR,
        help=f"frequency divisor, default: {DEFAULT_DIVISOR}",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="only print how many entries would be changed",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    if args.divisor <= 0:
        raise ValueError("--divisor must be greater than 0")

    root = Path(__file__).resolve().parents[2]
    file_path = root / args.file
    changed_count = divide_file_freq(file_path, args.divisor, args.dry_run)
    action = "would update" if args.dry_run else "updated"

    print(f"{file_path.relative_to(root)}: {changed_count}")
    print(f"{action} {changed_count} entries")


if __name__ == "__main__":
    main()
