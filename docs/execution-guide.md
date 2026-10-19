# Guia de Execução

## Ambiente

No Lovelace, carregar os módulos equivalentes a GCC, MPI e OpenBLAS. Registrar
o ambiente antes de compilar:

```bash
bash scripts/collect_environment.sh
```

Para gerar graficos e o PDF, instalar as dependencias Python disponiveis no
ambiente:

```bash
python3 -m pip install -r scripts/requirements.txt
```

## Compilação

```bash
cmake -S . -B build -DCMAKE_BUILD_TYPE=Release
cmake --build build --parallel
```

Se o OpenBLAS não for encontrado:

```bash
cmake -S . -B build -DOPENBLAS_ROOT=/caminho/do/openblas
```

## Teste pequeno

```bash
./build/serial_mm --n 128 --block 32 --validate
mpirun -np 2 ./build/mpi_mm --n 128 --block 32 --validate
OPENBLAS_NUM_THREADS=1 mpirun -np 2 ./build/mpi_blas_mm --n 128 --block 32 --validate
```

Todos os resultados devem informar `validation=ok`.

## PBS

Compile no cluster com:

```bash
qsub -v PROJECT_ROOT="$PWD" pbs/build.pbs
```

Execute uma campanha menor para teste:

```bash
qsub -v PROJECT_ROOT="$PWD",N_LIST="2000 4000",BLOCK_LIST="64 128",NP_LIST="1 2 4",REPETITIONS=3,OPENBLAS_THREADS=1 pbs/run_experiments.pbs
```

O script salva comandos, parâmetros, ambiente e saídas em `results/raw/`.
Após o job:

```bash
python3 scripts/process_results.py --raw-dir results/raw/benchmark-final
python3 scripts/plot_results.py
python3 scripts/generate_report_pdf.py
```

O launcher pode variar no Lovelace. Se `mpirun` não for o launcher correto,
substitua-o com `MPIEXEC=mpiexec` e registre a alteração no relatório.

## Execução PBS Multinó

No ambiente inventariado, a fila `paralela` aceita a alocação usada pelo
script `pbs/run_multinode.pbs`: dois nós, 128 CPUs e 128 processos MPI por
nó. O script registra o `PBS_NODEFILE`, módulos, versões, comandos completos e
saídas individuais em `results/raw/`.

```bash
qsub -q paralela -v PROJECT_ROOT="$PWD",N_LIST="2000",BLOCK_LIST="128",NP_LIST="1 2 4 8 16 32 48 96",REPETITIONS=3,OPENBLAS_THREADS=1 pbs/run_multinode.pbs
```

Verifique o job e aguarde a conclusão:

```bash
qstat -f <JOBID>
qstat -x <JOBID>
```

Depois processe somente o diretório gerado pelo job, preservando os logs:

```bash
python3 scripts/process_results.py --raw-dir results/raw/<JOBID>-<STAMP>-multinode
python3 scripts/plot_results.py
```
