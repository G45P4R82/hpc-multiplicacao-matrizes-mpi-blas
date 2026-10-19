#!/usr/bin/env python3
"""Gera graficos publicaveis a partir dos CSVs processados."""
import argparse
import csv
import math
from collections import defaultdict
from pathlib import Path


COLORS = {"serial": "#263238", "mpi": "#1976d2", "mpi_blas": "#e65100"}
LABELS = {"serial": "Serial", "mpi": "MPI", "mpi_blas": "MPI + OpenBLAS"}


def read_rows(path):
    with path.open(newline="") as stream:
        return list(csv.DictReader(stream))


def grouped(rows, key_fields, value_field="compute_seconds"):
    values = defaultdict(list)
    for row in rows:
        key = tuple(row[field] for field in key_fields)
        values[key].append(float(row[value_field]))
    return {key: (sum(items) / len(items),
                  math.sqrt(sum((item - sum(items) / len(items)) ** 2
                                for item in items) / len(items)))
            for key, items in values.items()}


def save(fig, output_dir, name):
    fig.tight_layout()
    fig.savefig(output_dir / name, dpi=220, bbox_inches="tight")
    import matplotlib.pyplot as plt
    plt.close(fig)


def style_axis(axis):
    axis.grid(axis="y", color="#cfd8dc", linewidth=0.8, alpha=0.7)
    axis.set_axisbelow(True)
    for spine in ("top", "right"):
        axis.spines[spine].set_visible(False)


def plot_time(rows, output_dir, plt):
    stats = grouped(rows, ["version", "n", "block", "processes"])
    fig, axes = plt.subplots(1, 3, figsize=(15, 4.8), sharey=False)
    for axis, n in zip(axes, ("2000", "4000", "6000")):
        for version in ("serial", "mpi", "mpi_blas"):
            block = "128"
            points = [(int(process), stats[(version, n, block, process)])
                      for process in ("1", "2", "4")
                      if (version, n, block, process) in stats]
            if not points:
                continue
            x = [item[0] for item in points]
            y = [item[1][0] for item in points]
            error = [item[1][1] for item in points]
            axis.errorbar(x, y, yerr=error, marker="o", linewidth=2,
                          capsize=3, color=COLORS[version], label=LABELS[version])
        axis.set_title("N = " + n, fontweight="bold")
        axis.set_xlabel("Processos MPI")
        axis.set_xticks((1, 2, 4))
        axis.set_yscale("log")
        style_axis(axis)
    axes[0].set_ylabel("Tempo de computacao (s, escala log)")
    axes[-1].legend(frameon=False, loc="upper right")
    fig.suptitle("Tempo de computacao por versao e tamanho da matriz",
                 fontsize=15, fontweight="bold")
    save(fig, output_dir, "report_01_tempo_por_tamanho.png")


def plot_blocks(rows, output_dir, plt):
    stats = grouped(rows, ["version", "n", "block", "processes"])
    fig, axis = plt.subplots(figsize=(8.8, 5.2))
    for process in ("1", "2", "4"):
        points = [(int(block), stats[("mpi_blas", "2000", block, process)])
                  for block in ("64", "128", "256")
                  if ("mpi_blas", "2000", block, process) in stats]
        axis.errorbar([p[0] for p in points], [p[1][0] for p in points],
                      yerr=[p[1][1] for p in points], marker="o", linewidth=2,
                      capsize=3, label="p = " + process)
    axis.set_xlabel("Tamanho do bloco")
    axis.set_ylabel("Tempo de computacao (s)")
    axis.set_xticks((64, 128, 256))
    axis.set_title("Efeito do bloco: MPI + OpenBLAS, N = 2000",
                   fontweight="bold")
    style_axis(axis)
    axis.legend(title="Processos", frameon=False)
    save(fig, output_dir, "report_02_efeito_bloco.png")


def plot_parallel_scaling(rows, output_dir, plt):
    stats = grouped(rows, ["version", "n", "block", "processes"])
    fig, axes = plt.subplots(1, 2, figsize=(12, 4.8))
    for n, marker in (("2000", "o"), ("4000", "s"), ("6000", "^")):
        baseline = stats[("mpi_blas", n, "128", "1")][0]
        values = [(int(p), baseline / stats[("mpi_blas", n, "128", p)][0])
                  for p in ("1", "2", "4")]
        axes[0].plot([p[0] for p in values], [p[1] for p in values],
                     marker=marker, linewidth=2, label="N = " + n)
        axes[1].plot([p[0] for p in values],
                     [p[1] / p[0] for p in values], marker=marker,
                     linewidth=2, label="N = " + n)
    axes[0].plot((1, 2, 4), (1, 2, 4), "--", color="#90a4ae", label="ideal")
    axes[1].axhline(1, linestyle="--", color="#90a4ae", label="ideal")
    for axis, title, ylabel in zip(axes, ("Speedup paralelo", "Eficiencia paralela"),
                                   ("T(1) / T(p)", "Speedup / p")):
        axis.set_title(title, fontweight="bold")
        axis.set_xlabel("Processos MPI")
        axis.set_ylabel(ylabel)
        axis.set_xticks((1, 2, 4))
        axis.set_ylim(bottom=0)
        style_axis(axis)
    axes[-1].legend(frameon=False, fontsize=8)
    fig.suptitle("Escalabilidade forte da versao MPI + OpenBLAS",
                 fontsize=15, fontweight="bold")
    save(fig, output_dir, "report_03_escalabilidade_forte.png")


def plot_multinode(rows, output_dir, plt):
    stats = grouped(rows, ["version", "n", "block", "processes"])
    fig, axes = plt.subplots(1, 2, figsize=(13, 4.8))
    for version in ("mpi", "mpi_blas"):
        points = [(int(p), stats[(version, "2000", "128", p)])
                  for p in ("1", "2", "4", "8", "16", "32", "48", "96")]
        axes[0].errorbar([p[0] for p in points], [p[1][0] for p in points],
                         yerr=[p[1][1] for p in points], marker="o", linewidth=2,
                         capsize=3, color=COLORS[version], label=LABELS[version])
    axes[0].set_title("Tempo de computacao", fontweight="bold")
    axes[0].set_ylabel("Segundos (escala log)")
    axes[0].set_yscale("log")
    axes[0].set_xscale("log", base=2)
    axes[0].set_xticks((1, 2, 4, 8, 16, 32, 48, 96))
    axes[0].set_xticklabels(("1", "2", "4", "8", "16", "32", "48", "96"))
    axes[0].legend(frameon=False)
    overhead = grouped(rows, ["version", "n", "block", "processes"], "total_seconds")
    compute = grouped(rows, ["version", "n", "block", "processes"], "compute_seconds")
    for version in ("mpi", "mpi_blas"):
        points = [(int(p), overhead[(version, "2000", "128", p)][0] -
                  compute[(version, "2000", "128", p)][0])
                  for p in ("1", "2", "4", "8", "16", "32", "48", "96")]
        axes[1].plot([p[0] for p in points], [p[1] for p in points], marker="o",
                     linewidth=2, color=COLORS[version], label=LABELS[version])
    axes[1].set_title("Overhead: total - computacao", fontweight="bold")
    axes[1].set_ylabel("Segundos")
    axes[1].set_xscale("log", base=2)
    axes[1].set_xticks((1, 2, 4, 8, 16, 32, 48, 96))
    axes[1].set_xticklabels(("1", "2", "4", "8", "16", "32", "48", "96"))
    for axis in axes:
        axis.set_xlabel("Processos MPI")
        style_axis(axis)
    fig.suptitle("Campanha PBS multinode: N = 2000, bloco = 128",
                 fontsize=15, fontweight="bold")
    save(fig, output_dir, "report_04_multinode.png")


def plot_weak(rows, output_dir, plt):
    stats = grouped(rows, ["version", "n", "block", "processes"])
    points = [(int(p), stats[("mpi_blas", n, "128", p)])
              for n, p in (("2000", "1"), ("2520", "2"), ("3175", "4"))]
    fig, axis = plt.subplots(figsize=(8.8, 5.2))
    axis.errorbar([p[0] for p in points], [p[1][0] for p in points],
                  yerr=[p[1][1] for p in points], marker="o", linewidth=2.5,
                  capsize=4, color="#00897b")
    for process, value in points:
        axis.annotate("p=" + str(process), (process, value[0]),
                      textcoords="offset points", xytext=(0, 10), ha="center")
    axis.set_xlabel("Processos MPI")
    axis.set_ylabel("Tempo de computacao (s)")
    axis.set_xticks((1, 2, 4))
    axis.set_title("Escalabilidade fraca: MPI + OpenBLAS, bloco = 128",
                   fontweight="bold")
    style_axis(axis)
    save(fig, output_dir, "report_05_escalabilidade_fraca.png")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", type=Path, default=Path("results/processed/measurements.csv"))
    parser.add_argument("--multinode-input", type=Path,
                        default=Path("results/processed/multinode_measurements.csv"))
    parser.add_argument("--weak-input", type=Path,
                        default=Path("results/processed/weak_measurements.csv"))
    parser.add_argument("--output-dir", type=Path, default=Path("results/plots"))
    args = parser.parse_args()
    try:
        import matplotlib.pyplot as plt
    except ImportError as error:
        raise SystemExit("instale matplotlib para gerar graficos") from error

    args.output_dir.mkdir(parents=True, exist_ok=True)
    plot_time(read_rows(args.input), args.output_dir, plt)
    plot_blocks(read_rows(args.input), args.output_dir, plt)
    plot_parallel_scaling(read_rows(args.input), args.output_dir, plt)
    plot_multinode(read_rows(args.multinode_input), args.output_dir, plt)
    plot_weak(read_rows(args.weak_input), args.output_dir, plt)
    print("plots=5 output_dir=" + str(args.output_dir))


if __name__ == "__main__":
    main()
