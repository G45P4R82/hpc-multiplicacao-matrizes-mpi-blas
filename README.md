# Multiplicação de Matrizes em Blocos com MPI e OpenBLAS

Projeto da atividade de MO652/MC960. A execução definitiva deve ocorrer no
cluster Lovelace, dentro da infraestrutura do CENAPAD. Este repositório deve
ser usado por outra IA ou pessoa para compilar, executar, analisar e preparar
a entrega completa.

## Objetivo

Comparar corretude, desempenho e escalabilidade de três implementações de
multiplicação de matrizes quadradas `float` em blocos:

- `serial_mm`: um processo, sem BLAS;
- `mpi_mm`: distribuição MPI, sem BLAS;
- `mpi_blas_mm`: distribuição MPI e `cblas_sgemm` do OpenBLAS nos blocos locais.

Os tamanhos da matriz e do bloco devem ser configuráveis. A implementação MPI
deve ser validada contra a referência serial usando tolerância numérica para
precisão simples.

## O Que Deve Ser Executado

A IA executora deve realizar todas as etapas abaixo no Lovelace. Não deve
preencher resultados com valores inventados nem assumir que fila, launcher,
módulos ou caminhos do Lovelace são iguais aos do repositório de referência.

### 1. Inventário do cluster

Antes de compilar, registrar:

- fila PBS e formato de alocação;
- número de nós e CPUs disponíveis;
- launcher MPI (`mpiexec`, `mpirun` ou outro);
- compilador, MPI, CMake e OpenBLAS;
- modelo de CPU, memória e sistema operacional;
- variáveis relevantes do ambiente;
- valor efetivo de `OPENBLAS_NUM_THREADS`.

Preservar a saída em `results/environment/`.

### 2. Compilação

Compilar os três executáveis em modo Release usando CMake e verificar que
`mpi_blas_mm` está realmente ligado ao OpenBLAS:

```bash
cmake -S . -B build -DCMAKE_BUILD_TYPE=Release
cmake --build build --parallel
```

### 3. Teste de corretude

Executar primeiro matrizes pequenas. Cada teste paralelo deve terminar com
`validation=ok`. Se algum teste falhar, corrigir o problema e não iniciar a
campanha de desempenho.

```bash
./build/serial_mm --n 128 --block 32 --validate
<MPIEXEC> -np 2 ./build/mpi_mm --n 128 --block 32 --validate
OPENBLAS_NUM_THREADS=1 <MPIEXEC> -np 2 ./build/mpi_blas_mm --n 128 --block 32 --validate
```

O erro absoluto máximo, erro relativo máximo e tempo de validação devem ser
registrados. O tempo de validação não pode entrar no tempo de desempenho.

### 4. Campanha de desempenho

Executar cada configuração pelo menos três vezes, preservando todos os logs:

- matrizes `N = 2000, 4000, 6000`;
- blocos `64, 128, 256`, ajustando somente se o cluster exigir;
- versão serial, MPI e MPI + OpenBLAS;
- diferentes números de processos MPI;
- uma configuração de um nó e outra de múltiplos nós, se permitido;
- `OPENBLAS_NUM_THREADS` definido explicitamente.

O script PBS deve registrar o comando completo, parâmetros, nó, processo,
threads OpenBLAS e saída do programa em `results/raw/`.

### 5. Escalabilidade

Executar e analisar:

- **Escalabilidade forte:** manter `N` fixo e aumentar processos/nós.
- **Escalabilidade fraca:** aumentar `N` conforme os recursos aumentam,
  mantendo aproximadamente constante o trabalho por processo.

Depois processar os logs e gerar CSVs, estatísticas e gráficos.

## O Que Deve Ser Entregue

A entrega final deve conter todos os itens abaixo:

- código-fonte das três versões;
- arquivos de configuração CMake;
- scripts PBS usados para compilar e executar;
- instruções completas de compilação e execução;
- script de coleta do ambiente;
- logs brutos das execuções reais;
- CSVs processados;
- gráficos de desempenho;
- relatório final em PDF.

O relatório PDF deve comparar as três versões e incluir:

- ambiente experimental, fila, nós, CPUs e versões das bibliotecas;
- procedimento e tolerância usados na validação;
- tempos de execução e etapas incluídas na medição;
- speedup, eficiência e referência usada nos cálculos;
- impacto de processos, núcleos, nós, tamanho da matriz e tamanho do bloco;
- escalabilidade forte e fraca;
- média, variabilidade, mínimo e máximo das repetições;
- número de threads OpenBLAS;
- discussão dos ganhos, custos de comunicação e gargalos.

## Critérios De Sucesso

Antes de finalizar, confirmar que:

- os três executáveis compilam no Lovelace;
- os testes pequenos terminam com `validation=ok`;
- as versões MPI foram comparadas com a referência serial;
- os tempos de validação estão separados;
- cada configuração de desempenho tem pelo menos três repetições;
- os logs e resultados são de execuções reais;
- a campanha inclui matrizes, blocos, processos e nós variados;
- os scripts PBS passam em `bash -n`;
- os CSVs e gráficos foram gerados a partir dos logs;
- o relatório PDF está completo e reproduz os resultados;
- nenhum resultado foi inventado ou copiado do benchmark de rede.

## Arquivos Principais

- [`docs/execution-checklist.md`](docs/execution-checklist.md): checklist
  obrigatório para a IA executora registrar cada etapa e sua evidência;
- [`docs/execution-guide.md`](docs/execution-guide.md): procedimento operacional;
- [`docs/experimental-plan.md`](docs/experimental-plan.md): plano e métricas;
- [`pbs/build.pbs`](pbs/build.pbs): compilação no cluster;
- [`pbs/run_experiments.pbs`](pbs/run_experiments.pbs): campanha de desempenho;
- [`scripts/parse_results.py`](scripts/parse_results.py): processamento dos logs;
- [`scripts/plot_results.py`](scripts/plot_results.py): geração de gráficos;
- [`report/report.md`](report/report.md): modelo do relatório.

O repositório `hpc-benchmark-cenapad` fornecido anteriormente serve apenas
como referência de organização, reprodutibilidade e uso de PBS. Ele não é a
atividade atual e seus resultados de OSU, rede, UCX ou contêiner não devem ser
usados como resultados desta multiplicação de matrizes.
