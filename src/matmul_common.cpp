#include "matmul_common.hpp"

#include <algorithm>
#include <chrono>
#include <cmath>
#include <cstdlib>
#include <iomanip>
#include <iostream>
#include <random>
#include <stdexcept>

namespace {
std::size_t parse_size(const char* value, const char* name) {
    try {
        const auto parsed = std::stoull(value);
        if (parsed == 0) throw std::invalid_argument("zero");
        return static_cast<std::size_t>(parsed);
    } catch (...) {
        throw std::invalid_argument(std::string("valor invalido para ") + name);
    }
}
}

Options parse_options(int argc, char** argv) {
    Options options;
    for (int i = 1; i < argc; ++i) {
        const std::string argument(argv[i]);
        if (argument == "--help" || argument == "-h") {
            options.help = true;
        } else if (argument == "--validate") {
            options.validate = true;
        } else if (argument == "--n" && i + 1 < argc) {
            options.n = parse_size(argv[++i], "--n");
        } else if (argument == "--block" && i + 1 < argc) {
            options.block = parse_size(argv[++i], "--block");
        } else if (argument == "--seed" && i + 1 < argc) {
            options.seed = static_cast<std::uint32_t>(parse_size(argv[++i], "--seed"));
        } else {
            throw std::invalid_argument("opcao desconhecida ou sem valor: " + argument);
        }
    }
    return options;
}

void print_usage(const char* program) {
    std::cout << "Uso: " << program
              << " [--n N] [--block B] [--seed S] [--validate]\n";
}

void fill_random(std::vector<float>& matrix, std::uint32_t seed) {
    std::mt19937 generator(seed);
    std::uniform_real_distribution<float> distribution(-1.0f, 1.0f);
    for (float& value : matrix) value = distribution(generator);
}

void serial_matmul_tiled(const float* a, const float* b, float* c,
                         std::size_t n, std::size_t block) {
    std::fill(c, c + n * n, 0.0f);
    for (std::size_t ii = 0; ii < n; ii += block) {
        const std::size_t i_end = std::min(ii + block, n);
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

ValidationResult validate_result(const std::vector<float>& result,
                                 const std::vector<float>& reference,
                                 float abs_tolerance, float relative_tolerance) {
    if (result.size() != reference.size())
        throw std::invalid_argument("resultados com tamanhos diferentes");
    ValidationResult validation;
    for (std::size_t i = 0; i < result.size(); ++i) {
        const float absolute = std::fabs(result[i] - reference[i]);
        const float relative = absolute / std::max(std::fabs(reference[i]), 1.0e-6f);
        if (absolute > validation.max_abs_error) {
            validation.max_abs_error = absolute;
            validation.error_index = i;
        }
        validation.max_relative_error = std::max(validation.max_relative_error, relative);
        if (absolute > abs_tolerance && relative > relative_tolerance)
            validation.ok = false;
    }
    return validation;
}

double wall_time_seconds() {
    using clock = std::chrono::steady_clock;
    return std::chrono::duration<double>(clock::now().time_since_epoch()).count();
}

std::string openblas_threads() {
    const char* value = std::getenv("OPENBLAS_NUM_THREADS");
    return value == nullptr ? "unset" : value;
}
