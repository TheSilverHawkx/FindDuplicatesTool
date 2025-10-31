#!/usr/bin/env python3
"""
Find duplicate files by MD5 (recursive, multithreaded) and write duplicate groups to a CSV.

- Scans all files under the given root directory (no extension filters).
- Uses file-size pregrouping to avoid hashing files that can't be duplicates.
- Hashing is done in parallel with a ThreadPoolExecutor.
- Outputs only groups with more than one file per checksum.
- CSV columns: checksum,file_path
"""
import argparse
from pathlib import Path
from collections import defaultdict
from src.find_duplicate_files.report_handler import write_report
from src.find_duplicate_files.files_handler import list_files,group_files_by_size, hash_files

def find_duplicates(workdir: Path) -> dict[str, tuple[Path,int]]:
    file_hashes = defaultdict(list)

    print("Looking for all files...", end="")
    files = list_files(workdir)
    print(f"found {len(files)} files")

    print("Grouping by size...")
    # Group by size for efficiency
    files_by_size = group_files_by_size(files)

    # filter files with unique sizes
    filtered_files = [
        (file_size, p)
        for file_size, paths in files_by_size.items()
        if len(paths) > 1
        for p in paths
    ]
    
    # Hash files
    print("Hashing files...")
    file_hashes = hash_files(filtered_files)

    duplicates = { k:v for k,v in file_hashes.items() if len(v) > 0}

    print(f"Found {len(duplicates.keys())} duplicate hashes...")
    return duplicates


def parse_arguments() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Find duplicate files by MD5 and write duplicate groups to CSV.")
    parser.add_argument("workdir", type=Path, help="Root directory to scan recursively.")
    parser.add_argument("--out", type=Path, default=Path("duplicates.csv"),
                        help="Output CSV path (default: duplicates.csv)")
    args = parser.parse_args()

    return args

def main():
    
    args = parse_arguments()

    if not args.workdir.exists():
        raise SystemExit(f"Error: path does not exist: {args.workdir}")
    if not args.workdir.is_dir():
        raise SystemExit(f"Error: not a directory: {args.workdir}")

    duplicates: dict[str, tuple[Path,int]] = find_duplicates(args.workdir)

    if not len(duplicates) > 0:
        print("There are no duplicates in the workdir")
        return

    row_count = write_report(duplicates,args.out)

    print(f"Written {row_count} rows.")
