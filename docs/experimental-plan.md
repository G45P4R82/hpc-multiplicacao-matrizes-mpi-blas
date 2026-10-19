# Plano Experimental

## Objetivo

Comparar multiplicação de matrizes quadradas `float` nas versões serial, MPI
em blocos e MPI com OpenBLAS, medindo corretude, tempo, speedup, eficiência e
escalabilidade no Lovelace.

## Variáveis

- Matrizes: `N = 2000, 4000, 6000`.
- Blocos: inicialmente `64, 128, 256`; ajustar caso o cluster imponha limites.
- Processos MPI: configurações compatíveis com os nós reservados.
- Nós: pelo menos uma configuração de um nó e outra de múltiplos nós, quando disponível.
- OpenBLAS: `OPENBLAS_NUM_THREADS` definido explicitamente, inicialmente `1`.
- Repetições: pelo menos `3` por configuração.

O tempo de computação é o máximo entre os processos. O tempo total inclui a
distribuição de `A`, o broadcast de `B`, a computação e a coleta de `C`. A
validação é medida separadamente e não entra nesses tempos.

## Métricas

Usaremos a versão serial como referência para speedup entre versões. Para uma
mesma versão, o speedup paralelo será `T(1) / T(p)` e a eficiência será
`speedup / p`. Resultados individuais serão preservados para calcular média,
desvio-padrão, mínimo e máximo.

## Escalabilidade

- Forte: manter `N` fixo e aumentar processos/nós.
- Fraca: aumentar `N` aproximadamente com a raiz cúbica do número de processos,
  mantendo trabalho por processo aproximadamente constante.
