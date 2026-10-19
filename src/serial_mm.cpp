#include "matmul_common.hpp"

#include <exception>
#include <iomanip>
#include <iostream>
#include <vector>

int main(int argc, char** argv) {
    try {
        const Options options = parse_options(argc, argv);
        if (options.help) {
            print_usage(argv[0]);
            return 0;
        }
        const std::size_t elements = options.n * options.n;
        std::vector<float> a(elements), b(elements), c(elements), reference;
        fill_random(a, options.seed);
        fill_random(b, options.seed + 1);

        const double start = wall_time_seconds();
        serial_matmul_tiled(a.data(), b.data(), c.data(), options.n, options.block);
        const double elapsed = wall_time_seconds() - start;

        ValidationResult validation;
        double validation_time = 0.0;
        if (options.validate) {
            reference = c;
            const double validation_start = wall_time_seconds();
            validation = validate_result(c, reference);
            validation_time = wall_time_seconds() - validation_start;
        }
        std::cout << std::setprecision(9)
                  << "version=serial\n"
                  << "n=" << options.n << "\n"
                  << "block=" << options.block << "\n"
                  << "processes=1\n"
                  << "openblas_threads=not_used\n"
                  << "compute_seconds=" << elapsed << "\n"
                  << "total_seconds=" << elapsed << "\n"
                  << "validation_seconds=" << validation_time << "\n"
                  << "validation=" << (options.validate ? (validation.ok ? "ok" : "failed") : "not_requested") << "\n"
                  << "max_abs_error=" << validation.max_abs_error << "\n"
                  << "max_relative_error=" << validation.max_relative_error << "\n";
    } catch (const std::exception& error) {
        std::cerr << "erro: " << error.what() << '\n';
        print_usage(argv[0]);
        return 1;
    }
    return 0;
}
