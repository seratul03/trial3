#!/usr/bin/env python3
"""
Scan a project tree for documents and JSON files, then copy all PDFs and JSON files
into the specified Resources folder under two subfolders: `pdf` and `json`.

Default behavior is a dry-run; use `--execute` to actually copy files.
"""
from pathlib import Path
import shutil
import argparse
import sys

DOCUMENT_EXTS = {'.pdf', '.doc', '.docx', '.txt', '.md', '.rtf', '.odt'}
JSON_EXTS = {'.json', '.jsonl'}
EXCLUDE_DIRS = {'.git', '.venv', 'venv', '__pycache__', 'node_modules'}

DEFAULT_RESOURCES_PATH = Path(r"C:/Users/Seratul Mustakim/Downloads/College_chatbot/College_chatbot/Resources")


def ensure_dir(p: Path):
    p.mkdir(parents=True, exist_ok=True)


def unique_dest(dest: Path) -> Path:
    """Return a unique destination path by adding suffix if needed."""
    if not dest.exists():
        return dest
    stem = dest.stem
    suffix = dest.suffix
    parent = dest.parent
    i = 1
    while True:
        candidate = parent / f"{stem}_{i}{suffix}"
        if not candidate.exists():
            return candidate
        i += 1


def should_exclude(path: Path, root: Path):
    for part in path.relative_to(root).parts:
        if part in EXCLUDE_DIRS:
            return True
    return False


def scan_and_copy(root: Path, resources_dir: Path, execute: bool = False, verbose: bool = False):
    root = root.resolve()
    resources_dir = resources_dir.resolve()

    pdf_dir = resources_dir / 'pdf'
    json_dir = resources_dir / 'json'

    if verbose:
        print(f"Root: {root}")
        print(f"Resources: {resources_dir}")

    ensure_dir(pdf_dir)
    ensure_dir(json_dir)

    found_docs = []
    found_json = []

    for path in root.rglob('*'):
        if path.is_file():
            # skip files inside the target resources directory
            try:
                if resources_dir in path.resolve().parents or path.resolve() == resources_dir:
                    continue
            except Exception:
                pass
            if should_exclude(path, root):
                continue
            ext = path.suffix.lower()
            if ext in DOCUMENT_EXTS:
                found_docs.append(path)
            if ext in JSON_EXTS:
                found_json.append(path)

    # Report
    print(f"Found {len(found_docs)} document files (including PDFs).")
    print(f"Found {len(found_json)} JSON files.")

    # Copy PDFs
    pdfs = [p for p in found_docs if p.suffix.lower() == '.pdf']
    print(f"Planning to copy {len(pdfs)} PDF(s) to '{pdf_dir}'")
    for p in pdfs:
        dest = pdf_dir / p.name
        dest = unique_dest(dest)
        if execute:
            shutil.copy2(p, dest)
            print(f"Copied: {p} -> {dest}")
        else:
            print(f"Would copy: {p} -> {dest}")

    # Copy JSONs
    print(f"Planning to copy {len(found_json)} JSON file(s) to '{json_dir}'")
    for p in found_json:
        dest = json_dir / p.name
        dest = unique_dest(dest)
        if execute:
            shutil.copy2(p, dest)
            print(f"Copied: {p} -> {dest}")
        else:
            print(f"Would copy: {p} -> {dest}")

    print("Done.\nSummary:")
    print(f"  PDFs found: {len(pdfs)}")
    print(f"  JSONs found: {len(found_json)}")
    print(f"  Dry run: {not execute}")


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Scan project and copy PDFs and JSONs to Resources subfolders')
    parser.add_argument('--root', '-r', type=str, default='.', help='Root directory to scan (default: current directory)')
    parser.add_argument('--resources', '-t', type=str, default=str(DEFAULT_RESOURCES_PATH), help='Target Resources directory (default: the provided Resources path)')
    parser.add_argument('--execute', '-x', action='store_true', help='Actually perform copying. Without this flag the script runs in dry-run mode')
    parser.add_argument('--verbose', '-v', action='store_true', help='Verbose output')

    args = parser.parse_args()

    root = Path(args.root)
    resources_dir = Path(args.resources)

    if not root.exists():
        print(f"Error: root folder does not exist: {root}")
        sys.exit(1)

    # Create resources dir if missing when executing; in dry-run we still show plans and will create if execute
    if args.execute:
        ensure_dir(resources_dir)

    scan_and_copy(root, resources_dir, execute=args.execute, verbose=args.verbose)
