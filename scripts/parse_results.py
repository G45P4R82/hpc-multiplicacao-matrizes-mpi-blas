#!/usr/bin/env python3
"""Converte logs key=value do PBS em CSV, preservando cada repetição."""
import argparse
import csv
from pathlib import Path


def parse_file(path):
    values = {}
    for line in path.read_text(errors="replace").splitlines():
        if "=" in line and not line.startswith("command="):
            key, value = line.split("=", 1)
            if key.isidentifier():
                values[key] = value.strip()
    return values


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--raw-dir", required=True, type=Path)
    parser.add_argument("--output", default=Path("results/processed/measurements.csv"), type=Path)
    args = parser.parse_args()
    rows = [parse_file(path) for path in sorted(args.raw_dir.rglob("*.out"))]
    rows = [row for row in rows if "version" in row and "compute_seconds" in row]
    if not rows:
        raise SystemExit("nenhum log de benchmark encontrado")
    columns = sorted({key for row in rows for key in row})
    args.output.parent.mkdir(parents=True, exist_ok=True)
    with args.output.open("w", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=columns)
        writer.writeheader()
        writer.writerows(rows)
    print(f"rows={len(rows)} output={args.output}")


if __name__ == "__main__":
    main()
