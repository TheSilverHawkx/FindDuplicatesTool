# 🧮 Find Duplicate Files

A **multithreaded Python utility** to scan directories recursively and find **duplicate files** efficiently based on their content using **BLAKE3 hashing**.
The results are exported into an Excel `.xlsx` report listing duplicate groups with file paths and sizes.

---

## 🚀 Features

* **Recursive scanning** — Traverses all subdirectories to find every regular file.
* **Size-based pre-grouping** — Skips hashing files that cannot be duplicates.
* **Fast hashing** — Uses the [BLAKE3](https://github.com/BLAKE3-team/BLAKE3) algorithm for high performance.
* **Parallel execution** — Multithreaded hashing with automatic worker scaling.
* **Detailed reporting** — Exports duplicates into an Excel file with checksum, file path, and size columns.
* **Robust I/O handling** — Gracefully skips unreadable or inaccessible files.

---

## 🧰 Installation

### Requirements

* Python **3.12+**
* Dependencies:

  * `blake3 >=1.0.8,<2.0.0`
  * `openpyxl >=3.1.5,<4.0.0`

### Install via Poetry

```bash
poetry install
```

Alternatively, install manually:

```bash
pip install blake3 openpyxl
```

---

## 🏗️ Usage

### Command-Line Interface

After installation, you can use the provided CLI script:

```bash
find-duplicates /path/to/scan --out duplicates.xlsx
```

**Arguments:**

| Argument  | Description                        | Default           |
| --------- | ---------------------------------- | ----------------- |
| `workdir` | Root directory to scan recursively | Required          |
| `--out`   | Path to output Excel report        | `duplicates.xlsx` |

**Example:**

```bash
find-duplicates ~/Downloads --out ~/Documents/duplicate_report.xlsx
```

---

## 📄 Output

The script generates an Excel report with the following columns:

| checksum           | file_path                 | size            |
| ------------------ | ------------------------- | --------------- |
| Unique BLAKE3 hash | Absolute path to the file | File size in MB |

Each checksum may appear multiple times for duplicate files.
Columns are **auto-sized**, and the header row is **bolded** for readability.

---

## 🧩 Code Structure

```
src/find_duplicate_files/
├── main.py           # CLI entry point, orchestrates the scanning and report generation
├── files_handler.py  # File listing, grouping, and hashing logic
└── report_handler.py # Excel report generation using openpyxl
```

---

## 🧪 Example Output

```
Looking for all files...found 5421 files
Grouping by size...
Hashing files...
Found 37 duplicate hashes...
Written 128 rows.
```

---

## ⚙️ Project Configuration

Defined in **pyproject.toml**:

```toml
[project]
name = "find-duplicate-files"
version = "0.1.0"
requires-python = ">=3.12"

[tool.poetry.scripts]
find-duplicates = "src.find_duplicate_files.main:main"
```

---

## 🛡️ Error Handling

* Skips unreadable files or permission errors with warnings.
* Automatically adjusts thread pool size for optimal performance.
* Validates input paths (must exist and be a directory).

