#include "mpi_matmul.hpp"

#include <mpi.h>

#ifdef USE_OPENBLAS
#include <cblas.h>
#endif

#include <algorithm>
#include <exception>
#include <iomanip>
#include <iostream>
#include <vector>

namespace {
void distribution(std::size_t n, int processes, std::vector<int>& counts,
                  std::vector<int>& displacements) {
    counts.resize(processes);
    displacements.resize(processes);
    const std::size_t base = n / static_cast<std::size_t>(processes);
    const std::size_t remainder = n % static_cast<std::size_t>(processes);
    int displacement = 0;
    for (int rank = 0; rank < processes; ++rank) {
        const std::size_t rows = base + (static_cast<std::size_t>(rank) < remainder ? 1 : 0);
        counts[rank] = static_cast<int>(rows * n);
        displacements[rank] = displacement;
        displacement += counts[rank];
    }
}

void local_tiled(const float* a, const float* b, float* c, std::size_t rows,
                 std::size_t n, std::size_t block) {
    std::fill(c, c + rows * n, 0.0f);
    for (std::size_t ii = 0; ii < rows; ii += block) {
        const std::size_t i_end = std::min(ii + block, rows);
        for (std::size_t kk = 0; kk < n; kk += block) {
            const std::size_t k_end = std::min(kk + block, n);
            for (std::size_t jj = 0; jj < n; jj += block) {
                const std::size_t j_end = std::min(jj + block, n);
                for (std::size_t i = ii; i < i_end; ++i) {
                    for (std::size_t k = kk; k < k_end; ++k) {
                        const float aik = a[i * n + k];
                        for (std::size_t j = jj; j < j_end; ++j)
                            c[i * n + j] += aik * b[k * n + j];
                    }
                }
            }
        }
    }
}

#ifdef USE_OPENBLAS
void local_blas(const float* a, const float* b, float* c, std::size_t rows,
                std::size_t n, std::size_t block) {
    std::fill(c, c + rows * n, 0.0f);
    for (std::size_t kk = 0; kk < n; kk += block) {
        const int k_size = static_cast<int>(std::min(kk + block, n) - kk);
        for (std::size_t jj = 0; jj < n; jj += block) {
            const int j_size = static_cast<int>(std::min(jj + block, n) - jj);
            for (std::size_t ii = 0; ii < rows; ii += block) {
                const int i_size = static_cast<int>(std::min(ii + block, rows) - ii);
                cblas_sgemm(CblasRowMajor, CblasNoTrans, CblasNoTrans,
                            i_size, j_size, k_size, 1.0f,
                            a + ii * n + kk, static_cast<int>(n),
                            b + kk * n + jj, static_cast<int>(n), 1.0f,
                            c + ii * n + jj, static_cast<int>(n));
            }
        }
    }
}
#endif
}

int run_mpi_matmul(int argc, char** argv, bool use_blas) {
    MPI_Init(&argc, &argv);
    int rank = 0;
    int processes = 0;
    MPI_Comm_rank(MPI_COMM_WORLD, &rank);
    MPI_Comm_size(MPI_COMM_WORLD, &processes);
    try {
        const Options options = parse_options(argc, argv);
        if (options.help) {
            if (rank == 0) print_usage(argv[0]);
            MPI_Finalize();
            return 0;
        }
#ifndef USE_OPENBLAS
        if (use_blas) throw std::runtime_error("executavel MPI+BLAS compilado sem OpenBLAS");
#endif
        const std::size_t elements = options.n * options.n;
        std::vector<int> counts, displacements;
        distribution(options.n, processes, counts, displacements);
        const std::size_t local_elements = static_cast<std::size_t>(counts[rank]);
        const std::size_t local_rows = local_elements / options.n;
        std::vector<float> a, b, c, gathered;
        if (rank == 0) {
            a.resize(elements);
            b.resize(elements);
            gathered.resize(elements);
            fill_random(a, options.seed);
            fill_random(b, options.seed + 1);
        } else {
            b.resize(elements);
        }
        std::vector<float> local_a(local_elements), local_c(local_elements);

        MPI_Barrier(MPI_COMM_WORLD);
        const double total_start = MPI_Wtime();
        MPI_Bcast(b.data(), static_cast<int>(elements), MPI_FLOAT, 0, MPI_COMM_WORLD);
        MPI_Scatterv(rank == 0 ? a.data() : nullptr, counts.data(), displacements.data(),
                     MPI_FLOAT, local_a.data(), counts[rank], MPI_FLOAT, 0, MPI_COMM_WORLD);
        const double compute_start = MPI_Wtime();
#ifdef USE_OPENBLAS
        if (use_blas) local_blas(local_a.data(), b.data(), local_c.data(), local_rows, options.n, options.block);
        else local_tiled(local_a.data(), b.data(), local_c.data(), local_rows, options.n, options.block);
#else
        local_tiled(local_a.data(), b.data(), local_c.data(), local_rows, options.n, options.block);
#endif
        const double local_compute = MPI_Wtime() - compute_start;
        double compute_seconds = 0.0;
        MPI_Reduce(&local_compute, &compute_seconds, 1, MPI_DOUBLE, MPI_MAX, 0, MPI_COMM_WORLD);
        MPI_Gatherv(local_c.data(), counts[rank], MPI_FLOAT,
                    rank == 0 ? gathered.data() : nullptr, counts.data(), displacements.data(),
                    MPI_FLOAT, 0, MPI_COMM_WORLD);
        const double total_seconds = MPI_Wtime() - total_start;

        if (rank == 0) {
            ValidationResult validation;
            double validation_seconds = 0.0;
            if (options.validate) {
                std::vector<float> reference(elements);
                const double validation_start = MPI_Wtime();
                serial_matmul_reference(a.data(), b.data(), reference.data(), options.n);
                validation = validate_result(gathered, reference);
                validation_seconds = MPI_Wtime() - validation_start;
            }
            std::cout << std::setprecision(9)
                      << "version=" << (use_blas ? "mpi_blas" : "mpi") << '\n'
                      << "n=" << options.n << '\n'
                      << "block=" << options.block << '\n'
                      << "processes=" << processes << '\n'
                      << "openblas_threads=" << (use_blas ? openblas_threads() : "not_used") << '\n'
                      << "compute_seconds=" << compute_seconds << '\n'
                      << "total_seconds=" << total_seconds << '\n'
                      << "validation_seconds=" << validation_seconds << '\n'
                      << "validation=" << (options.validate ? (validation.ok ? "ok" : "failed") : "not_requested") << '\n'
                      << "max_abs_error=" << validation.max_abs_error << '\n'
                      << "max_relative_error=" << validation.max_relative_error << '\n';
        }
    } catch (const std::exception& error) {
        if (rank == 0) std::cerr << "erro: " << error.what() << '\n';
        MPI_Abort(MPI_COMM_WORLD, 1);
        return 1;
    }
    MPI_Finalize();
    return 0;
}
