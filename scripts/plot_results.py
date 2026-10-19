#!/usr/bin/env python3
import argparse
import csv
from collections import defaultdict
from pathlib import Path


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", type=Path, default=Path("results/processed/measurements.csv"))
    parser.add_argument("--output-dir", type=Path, default=Path("results/plots"))
    args = parser.parse_args()
    try:
        import matplotlib.pyplot as plt
    except ImportError as error:
        raise SystemExit("instale matplotlib para gerar graficos") from error

    groups = defaultdict(list)
    with args.input.open(newline="") as stream:
        for row in csv.DictReader(stream):
            key = (row["version"], int(row["n"]), int(row["block"]), int(row["processes"]))
            groups[key].append(float(row["compute_seconds"]))
    args.output_dir.mkdir(parents=True, exist_ok=True)
    by_n = defaultdict(list)
    for (version, n, block, processes), values in groups.items():
        mean = sum(values) / len(values)
        by_n[n].append((version, block, processes, mean))
    for n, records in by_n.items():
        fig, axis = plt.subplots(figsize=(9, 5))
        for version in sorted({record[0] for record in records}):
            selected = sorted((r[2], r[3]) for r in records if r[0] == version)
            axis.plot([x[0] for x in selected], [x[1] for x in selected], marker="o", label=version)
        axis.set_title(f"Tempo de computacao por processos, N={n}")
        axis.set_xlabel("Processos MPI")
        axis.set_ylabel("Tempo (s)")
        axis.grid(True, alpha=0.3)
        axis.legend()
        fig.tight_layout()
        fig.savefig(args.output_dir / f"compute_time_n{n}.png", dpi=160)
        plt.close(fig)


if __name__ == "__main__":
    main()
