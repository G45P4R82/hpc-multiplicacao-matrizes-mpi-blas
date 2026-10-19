#!/bin/bash
set -u
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
OUT="${1:-$ROOT/results/environment/$(hostname)-$(date +%Y%m%d-%H%M%S)}"
mkdir -p "$OUT"
{
    date
    hostname
    uname -a
    lscpu 2>&1
    free -h 2>&1
    printf '\nEnvironment:\n'
    env | sort
    printf '\nModules:\n'
    module list 2>&1 || true
    printf '\nCompiler/MPI/OpenBLAS:\n'
    c++ --version 2>&1 || true
    mpirun --version 2>&1 || true
    pkg-config --modversion openblas 2>&1 || true
} >"$OUT/system.txt"
ldconfig -p 2>/dev/null | grep -i blas >"$OUT/blas-libraries.txt" || true
printf 'environment_dir=%s\n' "$OUT"
