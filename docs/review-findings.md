# Revisao dos Requisitos

Este documento registra os pontos encontrados na comparacao do repositorio com
`instrucoe.txt` (arquivo de instrucoes da atividade). Ele deve ser usado como
lista de trabalho pela IA que executa os experimentos no cluster.

## Prioridade Alta

### 1. Uniformizar a campanha multinode

Ha informacoes conflitantes entre o script, o guia e o relatorio:

- `pbs/run_multinode.pbs:3` usa a fila `parexp`.
- `docs/execution-guide.md:62` tambem documenta `parexp`.
- `report/report.md:140` afirma que a fila usada foi `paralela`.
- O script solicita `select=2:ncpus=48:mpiprocs=48`, enquanto o relatorio
  afirma dois nos com 128 CPUs por no.

Acao: confirmar no Lovelace a fila e a alocacao efetivamente usadas, ajustar
script, guia, evidencias e relatorio para os mesmos valores e preservar o
comando completo de submissao e o `PBS_NODEFILE` do job final.

Criterio de aceite: uma pessoa consegue reproduzir a submissao documentada e
os recursos do relatorio coincidem com `environment.txt`, `nodefile` e os
arquivos de submissao preservados.

### 2. Tornar o processamento totalmente reproduzivel

`scripts/parse_results.py` gera `measurements.csv` e
`scripts/plot_results.py` gera graficos, mas nao existe script versionado que
gere, a partir dos logs, todos os seguintes artefatos ja presentes:

- `statistics.csv`;
- `speedup_efficiency.csv`;
- `multinode_statistics.csv`;
- `multinode_speedup_efficiency.csv`;
- `weak_measurements.csv`.

Acao: adicionar ou integrar scripts para gerar esses arquivos a partir de um
diretorio de logs, incluindo media, desvio-padrao, minimo, maximo, speedup,
eficiencia e a referencia usada. Atualizar o guia com os comandos exatos.

Criterio de aceite: apagar os CSVs processados e recria-los apenas executando
os comandos documentados sobre os logs preservados, sem codigo manual externo.

### 3. Corrigir as evidencias do inventario

`results/environment/inventory/commands.txt` registra `cmake` e MPI ausentes e
`OPENBLAS_THREADS=unset`, enquanto os arquivos de compilacao e o relatorio
indicam outro ambiente, com modulos carregados e OpenBLAS efetivamente usado.

Acao: preservar um inventario final coletado depois do carregamento dos
modulos, contendo fila, launcher, nos, CPUs, caminhos das bibliotecas,
versoes e `OPENBLAS_NUM_THREADS` efetivo. Identificar explicitamente qualquer
inventario preliminar para nao confundi-lo com o ambiente da campanha final.

Criterio de aceite: os valores do inventario final, dos logs PBS e do
relatorio sao consistentes.

## Prioridade Media

### 4. Completar a discussao do relatorio

O relatorio apresenta resultados de blocos, processos e escalabilidade, mas a
discussao precisa ser explicitamente ampliada para cobrir todos os requisitos:

- influencia dos blocos 64, 128 e 256;
- impacto de processos, nucleos e nos;
- comunicacao e sincronizacao MPI;
- memoria, cache e gargalos;
- justificativa para configuracoes nao executadas;
- variabilidade das repeticoes em cada conjunto relevante.

Acao: atualizar `report/report.md` e regenerar `report/report.pdf` usando os
CSVs reais. Manter a ressalva quando uma execucao medir oversubscription ou
quando nao permitir conclusoes sobre escalabilidade fisica.

Criterio de aceite: cada item acima possui dados, interpretacao e limitacao
experimental no Markdown e no PDF.

### 5. Atualizar o checklist

`docs/execution-checklist.md` ainda possui itens marcados como `[ ]`, apesar de
a secao final afirmar que o repositorio esta pronto. Em particular, ha
pendencias em inventario, scripts, campanha forte/fraca, relatorio e artefatos.

Acao: marcar somente itens realmente comprovados com `[x]`, manter `[!]` para
falhas e preencher os blocos de evidencia com comandos, arquivos, resultado,
data e job PBS.

Criterio de aceite: nenhuma afirmacao de entrega pronta contradiz itens
pendentes do checklist.

### 6. Corrigir o nome do arquivo de instrucoes ou documentar a diferenca

A atividade se refere a `instrucoes.txt`, mas o repositorio contem
`instrucoe.txt`. Acao: confirmar o nome oficial e renomear ou registrar a
justificativa, evitando que a IA ou o avaliador procure o arquivo errado.

## Observacao de Qualidade do Codigo

Em `src/serial_mm.cpp:27-30`, quando `--validate` e usado, a referencia e uma
copia do proprio resultado serial. Isso produz necessariamente erro zero e
nao constitui uma verificacao independente. A exigencia principal de comparar
as versoes paralelas com uma referencia serial ja esta implementada em
`src/mpi_matmul.cpp`, mas o teste serial pode ser removido, esclarecido no
relatorio ou comparado com uma implementacao de referencia independente.

## Estado Verificado

- As tres versoes existem e usam `float`.
- CMake configura serial, MPI e MPI + OpenBLAS.
- Os testes pequenos registrados terminam com `validation=ok`.
- Os tempos de validacao aparecem separadamente.
- Ha logs reais, CSVs, graficos e PDF.
- Ha campanhas forte e fraca com pelo menos tres repeticoes nas configuracoes
  registradas.

Este documento registra pendencias de conformidade e nao substitui a
execucao de novos testes no Lovelace.
