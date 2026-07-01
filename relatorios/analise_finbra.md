# Análise FINBRA - Despesas por Função

## Método

A leitura respeita o formato brasileiro dos CSVs do Siconfi: `latin-1`, separador `;`,
3 linhas iniciais ignoradas e decimal com vírgula. As análises por função usam apenas
linhas classificadas como `funcao`, evitando dupla contagem com totais agregados,
subfunções e `FUxx - Demais Subfunções`.

Foram identificadas 50.334 linhas na base consolidada. Destas, 37.521
linhas não são funções e ficam fora dos rankings por função.

Também foi gerado um dashboard visual em `relatorios/analise_finbra.html`, com estilos em
`relatorios/dashboard.css`, para uma leitura mais confortável dos resultados.

## Completude por ano

| Ano | Capitais | Status |
| --- | --- | --- |
| 2020 | 26 | completo |
| 2021 | 26 | completo |
| 2022 | 26 | completo |
| 2023 | 26 | completo |
| 2024 | 26 | completo |
| 2025 | 11 | incompleto |

Os anos completos para comparação histórica são 2020, 2021, 2022, 2023, 2024. O ano de 2025 está incompleto e não foi usado nas comparações históricas principais.

## Rankings de Saúde e Educação em 2024

| Função | Capital | Pago per capita | Taxa de execução |
| --- | --- | --- | --- |
| 10 - Saúde | Belo Horizonte - MG | R$ 2.253,18 | 89,9% |
| 10 - Saúde | Teresina - PI | R$ 2.003,49 | 96,7% |
| 10 - Saúde | Campo Grande - MS | R$ 1.858,04 | 88,2% |
| 10 - Saúde | São Paulo - SP | R$ 1.791,32 | 96,1% |
| 10 - Saúde | Porto Alegre - RS | R$ 1.739,84 | 87,3% |
| 12 - Educação | Vitória - ES | R$ 2.232,14 | 91,9% |
| 12 - Educação | São Paulo - SP | R$ 1.827,98 | 95,8% |
| 12 - Educação | Palmas - TO | R$ 1.809,99 | 97,9% |
| 12 - Educação | Boa Vista - RR | R$ 1.611,01 | 97,2% |
| 12 - Educação | Florianópolis - SC | R$ 1.464,21 | 96,1% |

## Maiores diferenças entre empenhado e pago em 2024

| Capital | Função | Empenhado | Pago | Diferença | Taxa de execução |
| --- | --- | --- | --- | --- | --- |
| São Paulo - SP | 15 - Urbanismo | R$ 12.071.750.665,81 | R$ 10.203.722.086,42 | R$ 1.868.028.579,39 | 84,5% |
| São Paulo - SP | 12 - Educação | R$ 23.290.435.795,57 | R$ 22.301.640.088,44 | R$ 988.795.707,13 | 95,8% |
| São Paulo - SP | 10 - Saúde | R$ 22.752.837.820,49 | R$ 21.854.464.654,11 | R$ 898.373.166,38 | 96,1% |
| São Paulo - SP | 17 - Saneamento | R$ 2.868.478.794,47 | R$ 2.022.166.546,08 | R$ 846.312.248,39 | 70,5% |
| Curitiba - PR | 15 - Urbanismo | R$ 1.805.830.695,76 | R$ 982.059.804,58 | R$ 823.770.891,18 | 54,4% |
| Rio de Janeiro - RJ | 12 - Educação | R$ 7.151.238.932,58 | R$ 6.475.560.709,52 | R$ 675.678.223,06 | 90,6% |
| Belo Horizonte - MG | 10 - Saúde | R$ 5.993.532.028,34 | R$ 5.391.129.586,40 | R$ 602.402.441,94 | 89,9% |
| Rio de Janeiro - RJ | 10 - Saúde | R$ 7.642.644.288,09 | R$ 7.093.295.406,04 | R$ 549.348.882,05 | 92,8% |
| Rio de Janeiro - RJ | 09 - Previdência Social | R$ 6.789.834.775,46 | R$ 6.260.036.852,91 | R$ 529.797.922,55 | 92,2% |
| São Paulo - SP | 16 - Habitação | R$ 5.281.552.995,13 | R$ 4.760.425.320,14 | R$ 521.127.674,99 | 90,1% |

## Maceió contra média das capitais

| Ano | Função | Maceió execução | Média execução | Maceió pago per capita | Média pago per capita |
| --- | --- | --- | --- | --- | --- |
| 2020 | 10 - Saúde | 98,7% | 92,9% | R$ 766,94 | R$ 881,20 |
| 2020 | 12 - Educação | 89,2% | 93,5% | R$ 313,16 | R$ 617,60 |
| 2021 | 10 - Saúde | 97,7% | 92,7% | R$ 737,29 | R$ 939,08 |
| 2021 | 12 - Educação | 82,9% | 85,5% | R$ 375,40 | R$ 659,03 |
| 2022 | 10 - Saúde | 98,4% | 92,2% | R$ 832,41 | R$ 997,61 |
| 2022 | 12 - Educação | 94,3% | 88,0% | R$ 702,25 | R$ 835,78 |
| 2023 | 10 - Saúde | 97,8% | 93,3% | R$ 1.235,46 | R$ 1.158,78 |
| 2023 | 12 - Educação | 94,4% | 91,3% | R$ 593,80 | R$ 957,60 |
| 2024 | 10 - Saúde | 97,4% | 94,2% | R$ 1.314,67 | R$ 1.348,42 |
| 2024 | 12 - Educação | 85,5% | 92,9% | R$ 715,71 | R$ 1.158,05 |

## Prévia de 2025: capitais declarantes

Como 2025 tem apenas parte das capitais declaradas, este recorte não é comparado com o conjunto completo de capitais. Para aproveitar o dado sem distorcer a leitura, a comparação temporal usa somente as capitais que aparecem em 2025.

| UF | Capital declarante |
| --- | --- |
| AC | Rio Branco - AC |
| AM | Manaus - AM |
| BA | Salvador - BA |
| CE | Fortaleza - CE |
| GO | Goiânia - GO |
| MA | São Luís - MA |
| MG | Belo Horizonte - MG |
| PA | Belém - PA |
| RJ | Rio de Janeiro - RJ |
| RO | Porto Velho - RO |
| SC | Florianópolis - SC |

### Ranking preliminar de Saúde e Educação em 2025

| Função | Capital | Pago per capita | Taxa de execução |
| --- | --- | --- | --- |
| 10 - Saúde | Belo Horizonte - MG | R$ 2.445,94 | 88,6% |
| 10 - Saúde | Goiânia - GO | R$ 1.476,87 | 98,4% |
| 10 - Saúde | São Luís - MA | R$ 1.392,67 | 92,5% |
| 10 - Saúde | Fortaleza - CE | R$ 1.370,73 | 98,7% |
| 10 - Saúde | Porto Velho - RO | R$ 1.263,68 | 94,9% |
| 12 - Educação | Florianópolis - SC | R$ 1.437,60 | 93,1% |
| 12 - Educação | Belo Horizonte - MG | R$ 1.416,70 | 91,6% |
| 12 - Educação | Manaus - AM | R$ 1.378,62 | 98,5% |
| 12 - Educação | Goiânia - GO | R$ 1.334,41 | 94,6% |
| 12 - Educação | Porto Velho - RO | R$ 1.286,46 | 97,2% |

### Painel balanceado: 2024 vs 2025 nas mesmas capitais

| Capital | Função | Pago pc 2024 | Pago pc 2025 | Variação pago pc | Execução 2024 | Execução 2025 |
| --- | --- | --- | --- | --- | --- | --- |
| São Luís - MA | 10 - Saúde | R$ 1.216,39 | R$ 1.392,67 | 14,5% | 89,5% | 92,5% |
| Belém - PA | 12 - Educação | R$ 629,19 | R$ 717,03 | 14,0% | 95,1% | 89,0% |
| São Luís - MA | 12 - Educação | R$ 958,68 | R$ 1.080,91 | 12,7% | 78,6% | 77,4% |
| Belo Horizonte - MG | 12 - Educação | R$ 1.263,57 | R$ 1.416,70 | 12,1% | 90,3% | 91,6% |
| Rio Branco - AC | 10 - Saúde | R$ 864,56 | R$ 772,66 | -10,6% | 97,1% | 93,4% |
| Goiânia - GO | 12 - Educação | R$ 1.213,97 | R$ 1.334,41 | 9,9% | 94,0% | 94,6% |
| Florianópolis - SC | 10 - Saúde | R$ 958,08 | R$ 1.045,20 | 9,1% | 91,9% | 91,7% |
| Belo Horizonte - MG | 10 - Saúde | R$ 2.253,18 | R$ 2.445,94 | 8,6% | 89,9% | 88,6% |
| Manaus - AM | 10 - Saúde | R$ 797,01 | R$ 854,07 | 7,2% | 95,4% | 97,0% |
| Manaus - AM | 12 - Educação | R$ 1.296,83 | R$ 1.378,62 | 6,3% | 98,4% | 98,5% |

## Gráficos

![maceio_taxa_execucao_saude_educacao](graficos/maceio_taxa_execucao_saude_educacao.png)

![ranking_pago_per_capita_saude_educacao](graficos/ranking_pago_per_capita_saude_educacao.png)

![previa_2025_variacao_pago_per_capita](graficos/previa_2025_variacao_pago_per_capita.png)

## Conclusões principais

- A comparação anual deve priorizar 2020 a 2024, pois 2025 tem apenas parte das capitais declaradas.
- A prévia de 2025 só compara capitais declarantes contra elas mesmas em 2024.
- A taxa de execução financeira mostra a distância entre o gasto comprometido e o efetivamente pago.
- Os rankings por função excluem agregados para evitar dupla contagem.
- A leitura per capita é essencial para comparar capitais de portes muito diferentes.
