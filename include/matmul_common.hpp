#ifndef MATMUL_COMMON_HPP
#define MATMUL_COMMON_HPP

#include <cstddef>
#include <cstdint>
#include <string>
#include <vector>

struct Options {
    std::size_t n = 512;
    std::size_t block = 64;
    std::uint32_t seed = 42;
    bool validate = false;
    bool help = false;
};

struct ValidationResult {
    bool ok = true;
    float max_abs_error = 0.0f;
    float max_relative_error = 0.0f;
    std::size_t error_index = 0;
};

Options parse_options(int argc, char** argv);
void print_usage(const char* program);
void fill_random(std::vector<float>& matrix, std::uint32_t seed);
void serial_matmul_tiled(const float* a, const float* b, float* c,
                         std::size_t n, std::size_t block);
ValidationResult validate_result(const std::vector<float>& result,
                                 const std::vector<float>& reference,
                                 float abs_tolerance = 1.0e-3f,
                                 float relative_tolerance = 1.0e-4f);
double wall_time_seconds();
std::string openblas_threads();

#endif
