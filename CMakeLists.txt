cmake_minimum_required(VERSION 3.18)
project(hpc_multiplicacao_matrizes_mpi_blas LANGUAGES CXX)

set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)
set(CMAKE_CXX_EXTENSIONS OFF)
set(CMAKE_CXX_FLAGS_RELEASE "-O3 -DNDEBUG -march=native")

find_package(MPI REQUIRED COMPONENTS CXX)
find_path(OPENBLAS_INCLUDE_DIR cblas.h
    HINTS ENV OPENBLAS_ROOT
    PATH_SUFFIXES include)
find_library(OPENBLAS_LIBRARY NAMES openblas
    HINTS ENV OPENBLAS_ROOT
    PATH_SUFFIXES lib lib64)
if(NOT OPENBLAS_INCLUDE_DIR OR NOT OPENBLAS_LIBRARY)
    message(FATAL_ERROR "OpenBLAS nao encontrado. Defina OPENBLAS_ROOT ou carregue o modulo OpenBLAS.")
endif()

add_library(matmul_common src/matmul_common.cpp)
target_include_directories(matmul_common PUBLIC ${PROJECT_SOURCE_DIR}/include)
target_compile_options(matmul_common PRIVATE -Wall -Wextra -Wpedantic)

add_executable(serial_mm src/serial_mm.cpp)
target_link_libraries(serial_mm PRIVATE matmul_common)

add_library(mpi_matmul_core src/mpi_matmul.cpp)
target_include_directories(mpi_matmul_core PRIVATE ${PROJECT_SOURCE_DIR}/include)
target_link_libraries(mpi_matmul_core PRIVATE matmul_common MPI::MPI_CXX)
target_compile_options(mpi_matmul_core PRIVATE -Wall -Wextra -Wpedantic)

add_library(mpi_blas_core src/mpi_matmul.cpp)
target_include_directories(mpi_blas_core PRIVATE ${PROJECT_SOURCE_DIR}/include ${OPENBLAS_INCLUDE_DIR})
target_compile_definitions(mpi_blas_core PRIVATE USE_OPENBLAS)
target_link_libraries(mpi_blas_core PRIVATE matmul_common MPI::MPI_CXX ${OPENBLAS_LIBRARY})
target_compile_options(mpi_blas_core PRIVATE -Wall -Wextra -Wpedantic)

add_executable(mpi_mm src/mpi_mm.cpp)
target_link_libraries(mpi_mm PRIVATE mpi_matmul_core)

add_executable(mpi_blas_mm src/mpi_blas_mm.cpp)
target_link_libraries(mpi_blas_mm PRIVATE mpi_blas_core)

include(GNUInstallDirs)
install(TARGETS serial_mm mpi_mm mpi_blas_mm RUNTIME DESTINATION ${CMAKE_INSTALL_BINDIR})
