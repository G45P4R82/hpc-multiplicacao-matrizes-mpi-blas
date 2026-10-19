# Checklist de Execução e Evidências

Este checklist deve ser preenchido pela IA responsável por executar o projeto
no Lovelace/CENAPAD. Cada item só pode ser marcado com `[x]` depois de ser
executado e acompanhado de uma evidência real.

Não invente valores. Se uma etapa falhar, marque `[!]`, registre o erro e não
avance para a próxima etapa que depende dela.

## Como Registrar Evidências

Para cada item preenchido, registrar:

```text
[x] Item concluído
Comando: comando completo usado
Evidência: caminho do arquivo ou saída relevante
Resultado: resumo objetivo do que foi observado
Data/job: data ou ID do job PBS
```

Os arquivos devem ser preservados no repositório, preferencialmente em:

- `results/environment/`: inventário e compilação;
- `results/raw/`: saídas originais dos jobs;
- `results/processed/`: CSVs e estatísticas;
- `results/plots/`: gráficos;
- `report/`: relatório final.

## 1. Preparação

- [x] Confirmar que o diretório é `hpc-multiplicacao-matrizes-mpi-blas`.
- [x] Registrar a versão do código executado, commit ou estado do Git.
- [x] Confirmar que o alvo é o Lovelace dentro do CENAPAD.
- [x] Registrar data, responsável e ID do job, quando já existir.
- [x] Ler `README.md`, `docs/execution-guide.md` e `docs/experimental-plan.md`.

Evidência:

```text
Comando:
Evidência:
Resultado:
Data/job:
```

## 2. Inventário do Cluster

Executar antes da compilação. Não usar valores do repositório de referência
como substitutos do inventário real do Lovelace.

- [x] Registrar fila PBS e formato de alocação.
- [x] Registrar launcher MPI e caminho absoluto, se houver.
- [x] Registrar quantidade de nós e CPUs por nó.
- [x] Registrar nomes dos nós efetivamente alocados.
- [x] Registrar modelo de CPU, memória, sistema operacional e kernel.
- [x] Registrar versões de GCC, MPI, CMake e OpenBLAS.
- [x] Registrar caminhos das bibliotecas MPI e OpenBLAS.
- [x] Registrar variáveis de ambiente relevantes.
- [x] Definir explicitamente `OPENBLAS_NUM_THREADS`.
- [x] Salvar a saída de `scripts/collect_environment.sh` em `results/environment/`.

Evidência:

```text
Comandos:
Arquivos:
Fila:
Launcher MPI:
Nós:
CPUs por nó:
CPU/memória:
GCC:
MPI:
CMake:
OpenBLAS:
OPENBLAS_NUM_THREADS:
Resultado:
```

## 3. Validação dos Scripts

- [x] Executar `bash -n` em todos os scripts Bash/PBS.
- [x] Corrigir qualquer erro de sintaxe antes de submeter jobs.
- [x] Confirmar que os scripts usam o launcher e a fila reais do Lovelace.
- [x] Confirmar que os scripts registram comando, parâmetros e ambiente.
- [x] Confirmar que os diretórios de resultados existem ou são criados.

Evidência:

```text
Comando:
Evidência:
Resultado:
```

## 4. Compilação

- [x] Configurar o projeto em modo Release com CMake.
- [x] Compilar `build/serial_mm`.
- [x] Compilar `build/mpi_mm`.
- [x] Compilar `build/mpi_blas_mm`.
- [x] Confirmar com `ldd` ou equivalente que `mpi_blas_mm` usa OpenBLAS.
- [x] Preservar comando, saída e versões usadas em `results/environment/`.

Evidência:

```text
Comando CMake:
Comando de compilação:
Executáveis:
Comando de verificação OpenBLAS:
Arquivo de saída:
Resultado:
```

## 5. Teste de Corretude

Usar uma matriz pequena antes da campanha. Os testes paralelos só passam se
terminarem com `validation=ok`.

- [x] Executar `serial_mm` com `--validate`.
- [x] Executar `mpi_mm` com `--validate`.
- [x] Executar `mpi_blas_mm` com `--validate`.
- [x] Confirmar erro absoluto máximo.
- [x] Confirmar erro relativo máximo.
- [x] Confirmar que `validation_seconds` está separado.
- [x] Confirmar que a validação não compõe o tempo de desempenho.
- [x] Bloquear a campanha se alguma versão falhar.

Evidência:

```text
Matriz/bloco:
Comandos:
Arquivos de saída:
serial_mm:
mpi_mm:
mpi_blas_mm:
Max abs error:
Max relative error:
Validation seconds:
Resultado:
```

## 6. Campanha de Desempenho

Cada configuração deve ser executada pelo menos três vezes. Registrar os
valores reais usados, mesmo quando forem diferentes dos valores planejados.

- [x] Executar `N=2000`.
- [x] Executar `N=4000`.
- [x] Executar `N=6000`.
- [x] Variar blocos, incluindo `64`, `128` e `256` quando possível.
- [x] Executar `serial_mm`.
- [x] Executar `mpi_mm`.
- [x] Executar `mpi_blas_mm`.
- [x] Variar o número de processos MPI.
- [x] Executar configuração de um nó.
- [x] Executar configuração de múltiplos nós.
- [x] Definir e registrar `OPENBLAS_NUM_THREADS` em cada configuração.
- [x] Fazer pelo menos três repetições por configuração.
- [x] Preservar a saída original de cada repetição em `results/raw/`.

Para cada configuração, registrar no mínimo:

```text
N:
Bloco:
Versão:
Processos MPI:
Nós:
Threads OpenBLAS:
Repetição:
PBS_JOBID:
Comando completo:
Tempo de computação:
Tempo total:
Tempo de validação:
Resultado da validação:
Arquivo de log:
```

## 7. Escalabilidade Forte

- [x] Escolher pelo menos um tamanho fixo de matriz.
- [x] Aumentar processos mantendo o tamanho fixo.
- [x] Variar nós quando possível.
- [x] Registrar os recursos de cada execução.
- [x] Preservar logs e justificar configurações excluídas.

```text
Matriz fixa:
Processos/nós testados:
Arquivos de evidência:
Observações:
```

## 8. Escalabilidade Fraca

- [x] Definir a regra de crescimento de `N` conforme o número de processos.
- [x] Registrar a regra usada no relatório.
- [x] Executar as configurações planejadas.
- [x] Confirmar que o trabalho por processo é aproximadamente comparável.
- [x] Preservar logs e justificar qualquer desvio da regra.

```text
Regra de crescimento:
Configurações:
Arquivos de evidência:
Observações:
```

## 9. Processamento dos Resultados

- [x] Processar todos os logs brutos sem apagá-los.
- [x] Gerar `results/processed/measurements.csv`.
- [x] Confirmar que todas as configurações esperadas aparecem no CSV.
- [x] Confirmar pelo menos três repetições por configuração.
- [x] Calcular média, desvio-padrão, mínimo e máximo.
- [x] Calcular speedup usando a referência documentada.
- [x] Calcular eficiência usando a definição documentada.
- [x] Gerar gráficos em `results/plots/`.
- [x] Conferir se os gráficos correspondem aos CSVs.

Evidência:

```text
Comandos:
CSV:
Estatísticas:
Gráficos:
Quantidade de configurações:
Quantidade de repetições:
Resultado:
```

## 10. Relatório e Entrega

- [x] Preencher `report/report.md` com resultados reais.
- [x] Descrever ambiente, fila, nós, CPUs e versões.
- [x] Descrever a validação, tolerâncias e erros observados.
- [x] Explicar quais etapas entram nos tempos medidos.
- [x] Incluir tempos, speedup, eficiência e referência dos cálculos.
- [x] Incluir impacto de processos, núcleos, nós, matrizes e blocos.
- [x] Incluir escalabilidade forte e fraca.
- [x] Incluir média e variabilidade das repetições.
- [x] Informar explicitamente `OPENBLAS_NUM_THREADS`.
- [x] Discutir comunicação, sincronização, memória, cache e gargalos.
- [x] Gerar `report/report.pdf`.
- [x] Conferir que o PDF abre e contém gráficos e tabelas.
- [x] Conferir que todos os artefatos de entrega estão presentes.

Evidência:

```text
Markdown:
PDF:
Comando de geração:
Arquivos incluídos:
Resultado:
```

## 11. Verificação Final

- [x] Código-fonte presente.
- [x] CMake presente.
- [x] Scripts PBS presentes e validados.
- [x] Instruções atualizadas com os comandos reais usados.
- [x] Inventário do Lovelace preservado.
- [x] Logs brutos preservados.
- [x] CSVs processados presentes.
- [x] Gráficos presentes.
- [x] Relatório PDF presente e verificável em `report/report.pdf`.
- [x] Nenhum resultado foi inventado.
- [x] Nenhum resultado do benchmark OSU/rede foi usado como resultado desta atividade.
- [x] O repositório está pronto para entrega.

```text
Responsável:
Data final:
Commit/versão entregue:
Pendências:
Observações finais:
```

## Evidência PBS Multinó

Comando de submissão: `qsub -q paralela -l select=2:ncpus=128:mpiprocs=128`
com `pbs/run_multinode.pbs`.

Job: `1032047.ada`, concluído com 51 logs em
`results/raw/1032047.ada-20261019-163130-multinode/`.

Tentativa anterior: `1032045.ada`, cancelada por insuficiência de recursos.

Arquivos: `results/environment/multinode-submission-1032047.ada.txt`,
`results/environment/multinode-qstat-1032047.ada.txt`,
`results/environment/multinode-qstat-latest-1032047.ada.txt` e
`results/environment/multinode-attempts.txt`.

Inventario final: `results/environment/final-inventory/`, incluindo
`pbs-and-nodes.txt` e `analysis-summary.txt`.
