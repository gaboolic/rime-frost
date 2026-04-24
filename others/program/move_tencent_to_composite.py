import argparse
from dataclasses import dataclass
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_TENCENT_PATH = PROJECT_ROOT / "cn_dicts" / "tencent.dict.yaml"
DEFAULT_COMPOSITE_PATH = PROJECT_ROOT / "cn_dicts_cell" / "composite.dict.yaml"


@dataclass
class DictEntry:
    raw: str
    word: str
    code: str
    freq: int

    @property
    def key(self) -> tuple[str, str]:
        return self.word, self.code


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Move Tencent dictionary entries above a frequency threshold into composite."
    )
    parser.add_argument(
        "--tencent",
        default=str(DEFAULT_TENCENT_PATH),
        help="Path to tencent.dict.yaml",
    )
    parser.add_argument(
        "--composite",
        default=str(DEFAULT_COMPOSITE_PATH),
        help="Path to composite.dict.yaml",
    )
    parser.add_argument(
        "--threshold",
        type=int,
        default=1,
        help="Move entries whose frequency is greater than this value. Default: 1",
    )
    return parser.parse_args()


def read_dict_file(path: Path) -> tuple[list[str], list[DictEntry]]:
    header: list[str] = []
    entries: list[DictEntry] = []
    in_entries = False

    with path.open("r", encoding="utf-8") as file:
        for line in file:
            stripped = line.rstrip("\n")
            if not in_entries:
                header.append(stripped)
                if stripped == "...":
                    in_entries = True
                continue

            if not stripped or stripped.startswith("#") or "\t" not in stripped:
                continue

            parts = stripped.split("\t")
            if len(parts) < 3:
                continue

            word, code, freq = parts[0], parts[1], parts[2]
            entries.append(DictEntry(raw=stripped, word=word, code=code, freq=int(freq)))

    return header, entries


def write_dict_file(path: Path, header: list[str], entries: list[DictEntry]) -> None:
    with path.open("w", encoding="utf-8", newline="\n") as file:
        for line in header:
            file.write(f"{line}\n")
        for entry in entries:
            file.write(f"{entry.word}\t{entry.code}\t{entry.freq}\n")


def move_entries(
    tencent_entries: list[DictEntry], composite_entries: list[DictEntry], threshold: int
) -> tuple[list[DictEntry], list[DictEntry], int, int]:
    moved_entries: list[DictEntry] = []
    kept_tencent_entries: list[DictEntry] = []

    for entry in tencent_entries:
        if entry.freq > threshold:
            moved_entries.append(entry)
        else:
            kept_tencent_entries.append(entry)

    composite_index = {entry.key: idx for idx, entry in enumerate(composite_entries)}
    updated_count = 0
    appended_count = 0

    for entry in moved_entries:
        idx = composite_index.get(entry.key)
        if idx is None:
            composite_index[entry.key] = len(composite_entries)
            composite_entries.append(entry)
            appended_count += 1
            continue

        if entry.freq > composite_entries[idx].freq:
            composite_entries[idx] = entry
            updated_count += 1

    return kept_tencent_entries, composite_entries, appended_count, updated_count


def main() -> None:
    args = parse_args()
    tencent_path = Path(args.tencent)
    composite_path = Path(args.composite)

    tencent_header, tencent_entries = read_dict_file(tencent_path)
    composite_header, composite_entries = read_dict_file(composite_path)

    kept_tencent_entries, merged_composite_entries, appended_count, updated_count = move_entries(
        tencent_entries, composite_entries, args.threshold
    )

    moved_count = len(tencent_entries) - len(kept_tencent_entries)

    write_dict_file(tencent_path, tencent_header, kept_tencent_entries)
    write_dict_file(composite_path, composite_header, merged_composite_entries)

    print(f"tencent moved: {moved_count}")
    print(f"composite appended: {appended_count}")
    print(f"composite updated: {updated_count}")
    print(f"threshold: freq > {args.threshold}")


if __name__ == "__main__":
    main()
