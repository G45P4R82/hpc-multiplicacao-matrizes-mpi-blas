# Multiplicação de Matrizes em Blocos com MPI e OpenBLAS

## Resumo

Este relatório compara as versões serial, MPI e MPI + OpenBLAS. Os resultados
numéricos abaixo devem ser preenchidos a partir de `results/processed/` após as
execuções reais no Lovelace.

## Ambiente experimental

Registrar compilador, MPI, OpenBLAS, modelo de CPU, nós, número de núcleos,
versões, fila PBS e valor de `OPENBLAS_NUM_THREADS`. A saída de
`scripts/collect_environment.sh` deve ser preservada.

## Corretude

As versões paralelas são comparadas com a implementação serial usando erro
absoluto máximo e erro relativo máximo. A validação ocorre fora da medição de
desempenho. Registrar tolerâncias e todas as configurações validadas.

## Resultados

Inserir tabelas e gráficos de tempo, speedup, eficiência e variabilidade para
cada tamanho de matriz, bloco, número de processos e número de nós.

## Escalabilidade forte e fraca

Descrever o comportamento ao aumentar recursos com problema fixo e ao aumentar
o problema proporcionalmente aos recursos. Discutir comunicação, distribuição,
localidade, custo de sincronização, tamanho do bloco e threads OpenBLAS.

## Reprodutibilidade

Listar os comandos PBS usados e referenciar os logs brutos, CSVs processados e
gráficos versionados no repositório.
