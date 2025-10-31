from pathlib import Path
import hashlib
import blake3
import os
from collections import defaultdict

_CHUNK_SIZE = 4 * 1024 * 1024  # 4 MiB – bigger chunks reduce Python overhead

def list_files(root: Path) -> list[Path]:
    """Recursively yield all regular files under root. Skips directories and unreadable entries."""
    paths: list[Path] = []

    for dir_path, _, files in os.walk(root,followlinks=False):
        for file_name in files:
            file = Path(dir_path,file_name)
            try:
                if file.is_file() and os.access(file,os.R_OK):
                    paths.append(file)
            except OSError:
                continue
    return paths

def _get_file_blake3(path: Path,file_size: int) -> tuple[Path, str | None, int|None,str | None]:
    h = blake3.blake3()

    try:
        with path.open("rb") as f:
            while True:
                chunk = f.read(_CHUNK_SIZE)
                if not chunk:
                    break
                h.update(chunk)
        return path,h.hexdigest(),file_size,None
    except Exception as e:
        return path, None, None,str(e)

def group_files_by_size(files: list[Path]):
    by_size: dict[int, list[Path]] = {}
    for p in files:
        try:
            size = p.stat().st_size
        except OSError:
            continue

        by_size.setdefault(size, []).append(p)
    return by_size

def hash_files(
    files: list[tuple[int,Path]],
    max_workers: int | None = None,
) -> dict[str, tuple[Path,int]]:
    from concurrent.futures import ThreadPoolExecutor, as_completed

    """
    Compute MD5 for candidate files in parallel.
    Returns {md5_hex: [paths...]} for files that hashed successfully.
    """
    by_hash = defaultdict(list)
    # Heuristic: I/O-bound workload benefits from more threads than CPUs.
    if max_workers is None:
        cpus = os.cpu_count() or 4
        max_workers = max(8, cpus * 5)

    with ThreadPoolExecutor(max_workers=max_workers) as ex:
        futures = {}

        futures = {ex.submit(_get_file_blake3, p,size): p for size,p in files}
        for fut in as_completed(futures):
            path, digest, size, err = fut.result()
            if err:
                # Write non-fatal issues to stderr-like channel
                print(f"[warn] Skipping {path}: {err}")
                continue
            if digest is None:
                continue
            by_hash[digest].append((path,size))
    return by_hash