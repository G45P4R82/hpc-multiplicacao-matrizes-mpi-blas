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

- [ ] Confirmar que o diretório é `hpc-multiplicacao-matrizes-mpi-blas`.
- [ ] Registrar a versão do código executado, commit ou estado do Git.
- [ ] Confirmar que o alvo é o Lovelace dentro do CENAPAD.
- [ ] Registrar data, responsável e ID do job, quando já existir.
- [ ] Ler `README.md`, `docs/execution-guide.md` e `docs/experimental-plan.md`.

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

- [ ] Registrar fila PBS e formato de alocação.
- [ ] Registrar launcher MPI e caminho absoluto, se houver.
- [ ] Registrar quantidade de nós e CPUs por nó.
- [ ] Registrar nomes dos nós efetivamente alocados.
- [ ] Registrar modelo de CPU, memória, sistema operacional e kernel.
- [ ] Registrar versões de GCC, MPI, CMake e OpenBLAS.
- [ ] Registrar caminhos das bibliotecas MPI e OpenBLAS.
- [ ] Registrar variáveis de ambiente relevantes.
- [ ] Definir explicitamente `OPENBLAS_NUM_THREADS`.
- [ ] Salvar a saída de `scripts/collect_environment.sh` em `results/environment/`.

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

- [ ] Executar `bash -n` em todos os scripts Bash/PBS.
- [ ] Corrigir qualquer erro de sintaxe antes de submeter jobs.
- [ ] Confirmar que os scripts usam o launcher e a fila reais do Lovelace.
- [ ] Confirmar que os scripts registram comando, parâmetros e ambiente.
- [ ] Confirmar que os diretórios de resultados existem ou são criados.

Evidência:

```text
Comando:
Evidência:
Resultado:
```

## 4. Compilação

- [ ] Configurar o projeto em modo Release com CMake.
- [ ] Compilar `build/serial_mm`.
- [ ] Compilar `build/mpi_mm`.
- [ ] Compilar `build/mpi_blas_mm`.
- [ ] Confirmar com `ldd` ou equivalente que `mpi_blas_mm` usa OpenBLAS.
- [ ] Preservar comando, saída e versões usadas em `results/environment/`.

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

- [ ] Executar `serial_mm` com `--validate`.
- [ ] Executar `mpi_mm` com `--validate`.
- [ ] Executar `mpi_blas_mm` com `--validate`.
- [ ] Confirmar erro absoluto máximo.
- [ ] Confirmar erro relativo máximo.
- [ ] Confirmar que `validation_seconds` está separado.
- [ ] Confirmar que a validação não compõe o tempo de desempenho.
- [ ] Bloquear a campanha se alguma versão falhar.

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

- [ ] Executar `N=2000`.
- [ ] Executar `N=4000`.
- [ ] Executar `N=6000`.
- [ ] Variar blocos, incluindo `64`, `128` e `256` quando possível.
- [ ] Executar `serial_mm`.
- [ ] Executar `mpi_mm`.
- [ ] Executar `mpi_blas_mm`.
- [ ] Variar o número de processos MPI.
- [ ] Executar configuração de um nó.
- [ ] Executar configuração de múltiplos nós, se permitida.
- [ ] Definir e registrar `OPENBLAS_NUM_THREADS` em cada configuração.
- [ ] Fazer pelo menos três repetições por configuração.
- [ ] Preservar a saída original de cada repetição em `results/raw/`.

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

- [ ] Escolher pelo menos um tamanho fixo de matriz.
- [ ] Aumentar processos mantendo o tamanho fixo.
- [ ] Variar nós quando possível.
- [ ] Registrar os recursos de cada execução.
- [ ] Preservar logs e justificar configurações excluídas.

```text
Matriz fixa:
Processos/nós testados:
Arquivos de evidência:
Observações:
```

## 8. Escalabilidade Fraca

- [ ] Definir a regra de crescimento de `N` conforme o número de processos.
- [ ] Registrar a regra usada no relatório.
- [ ] Executar as configurações planejadas.
- [ ] Confirmar que o trabalho por processo é aproximadamente comparável.
- [ ] Preservar logs e justificar qualquer desvio da regra.

```text
Regra de crescimento:
Configurações:
Arquivos de evidência:
Observações:
```

## 9. Processamento dos Resultados

- [ ] Processar todos os logs brutos sem apagá-los.
- [ ] Gerar `results/processed/measurements.csv`.
- [ ] Confirmar que todas as configurações esperadas aparecem no CSV.
- [ ] Confirmar pelo menos três repetições por configuração.
- [ ] Calcular média, desvio-padrão, mínimo e máximo.
- [ ] Calcular speedup usando a referência documentada.
- [ ] Calcular eficiência usando a definição documentada.
- [ ] Gerar gráficos em `results/plots/`.
- [ ] Conferir se os gráficos correspondem aos CSVs.

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

- [ ] Preencher `report/report.md` com resultados reais.
- [ ] Descrever ambiente, fila, nós, CPUs e versões.
- [ ] Descrever a validação, tolerâncias e erros observados.
- [ ] Explicar quais etapas entram nos tempos medidos.
- [ ] Incluir tempos, speedup, eficiência e referência dos cálculos.
- [ ] Incluir impacto de processos, núcleos, nós, matrizes e blocos.
- [ ] Incluir escalabilidade forte e fraca.
- [ ] Incluir média e variabilidade das repetições.
- [ ] Informar explicitamente `OPENBLAS_NUM_THREADS`.
- [ ] Discutir comunicação, sincronização, memória, cache e gargalos.
- [ ] Gerar `report/report.pdf`.
- [ ] Conferir que o PDF abre e contém gráficos e tabelas.
- [ ] Conferir que todos os artefatos de entrega estão presentes.

Evidência:

```text
Markdown:
PDF:
Comando de geração:
Arquivos incluídos:
Resultado:
```

## 11. Verificação Final

- [ ] Código-fonte presente.
- [ ] CMake presente.
- [ ] Scripts PBS presentes e validados.
- [ ] Instruções atualizadas com os comandos reais usados.
- [ ] Inventário do Lovelace preservado.
- [ ] Logs brutos preservados.
- [ ] CSVs processados presentes.
- [ ] Gráficos presentes.
- [ ] Relatório PDF presente.
- [ ] Nenhum resultado foi inventado.
- [ ] Nenhum resultado do benchmark OSU/rede foi usado como resultado desta atividade.
- [ ] O repositório está pronto para entrega.

```text
Responsável:
Data final:
Commit/versão entregue:
Pendências:
Observações finais:
```
