#!/usr/bin/env python3
"""Processa logs key=value e gera medidas, estatisticas e metricas derivadas."""
import argparse
import csv
import math
from collections import defaultdict
from pathlib import Path


def parse_file(path):
    values = {"source_file": str(path)}
    for line in path.read_text(errors="replace").splitlines():
        if "=" not in line or line.startswith("command="):
            continue
        key, value = line.split("=", 1)
        if key.isidentifier():
            values[key] = value.strip()
    return values


def read_measurements(raw_dir):
    rows = [parse_file(path) for path in sorted(raw_dir.rglob("*.out"))]
    return [row for row in rows if "version" in row and "compute_seconds" in row]


def write_csv(path, rows, fields):
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=fields, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(rows)


def statistics(rows):
    groups = defaultdict(list)
    for row in rows:
        key = (row["version"], row["n"], row["block"], row["processes"])
        groups[key].append(float(row["compute_seconds"]))
    fields = ["version", "n", "block", "processes", "repetitions",
              "mean_compute_seconds", "stddev_compute_seconds",
              "min_compute_seconds", "max_compute_seconds"]
    output = []
    for key, values in sorted(groups.items()):
        mean = sum(values) / len(values)
        variance = sum((value - mean) ** 2 for value in values) / len(values)
        output.append(dict(zip(fields, [*key, len(values), mean,
                                        math.sqrt(variance), min(values), max(values)])))
    return output, fields


def speedups(rows):
    groups = defaultdict(list)
    for row in rows:
        key = (row["version"], row["n"], row["block"], row["processes"])
        groups[key].append(float(row["compute_seconds"]))
    means = {key: sum(values) / len(values) for key, values in groups.items()}
    references = {(n, block): value for (version, n, block, process), value in means.items()
                  if version == "serial"}
    parallel_references = {(version, n, block): value
                           for (version, n, block, process), value in means.items()
                           if process == "1"}
    fields = ["version", "n", "block", "processes", "mean_compute_seconds",
              "reference_serial_seconds", "speedup", "efficiency",
              "parallel_reference_seconds", "parallel_speedup",
              "parallel_efficiency"]
    output = []
    for (version, n, block, process), value in sorted(means.items()):
        if version == "serial" or (n, block) not in references:
            continue
        reference = references[(n, block)]
        speedup = reference / value
        parallel_reference = parallel_references[(version, n, block)]
        parallel_speedup = parallel_reference / value
        output.append({"version": version, "n": n, "block": block,
                       "processes": process, "mean_compute_seconds": value,
                       "reference_serial_seconds": reference, "speedup": speedup,
                       "efficiency": speedup / int(process),
                       "parallel_reference_seconds": parallel_reference,
                       "parallel_speedup": parallel_speedup,
                       "parallel_efficiency": parallel_speedup / int(process)})
    return output, fields


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--raw-dir", required=True, type=Path)
    parser.add_argument("--output-dir", default=Path("results/processed"), type=Path)
    parser.add_argument("--prefix", default="", help="prefixo dos arquivos gerados")
    args = parser.parse_args()
    rows = read_measurements(args.raw_dir)
    if not rows:
        raise SystemExit("nenhum log de benchmark encontrado")
    prefix = f"{args.prefix}_" if args.prefix else ""
    measurement_fields = sorted({key for row in rows for key in row})
    write_csv(args.output_dir / f"{prefix}measurements.csv", rows, measurement_fields)
    stat_rows, stat_fields = statistics(rows)
    write_csv(args.output_dir / f"{prefix}statistics.csv", stat_rows, stat_fields)
    speedup_rows, speedup_fields = speedups(rows)
    write_csv(args.output_dir / f"{prefix}speedup_efficiency.csv", speedup_rows, speedup_fields)
    print(f"measurements={len(rows)} statistics={len(stat_rows)} speedups={len(speedup_rows)}")


if __name__ == "__main__":
    main()
