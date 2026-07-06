from __future__ import annotations

import html
import os
from pathlib import Path

import pandas as pd

from consolidar_dados import ROOT_DIR
from gerar_base_otimizada import PARQUET_PATH, generate_parquet


REPORT_DIR = ROOT_DIR / "relatorios"
CHART_DIR = REPORT_DIR / "graficos"
REPORT_PATH = REPORT_DIR / "analise_finbra.md"
HTML_REPORT_PATH = REPORT_DIR / "analise_finbra.html"
CSS_PATH = REPORT_DIR / "dashboard.css"
MPL_CACHE_DIR = REPORT_DIR / ".matplotlib-cache"

os.environ.setdefault("MPLBACKEND", "Agg")
os.environ.setdefault("MPLCONFIGDIR", str(MPL_CACHE_DIR))

import matplotlib.pyplot as plt
from matplotlib.ticker import FuncFormatter

STAGE_EMPENHADO = "Despesas Empenhadas"
STAGE_LIQUIDADO = "Despesas Liquidadas"
STAGE_PAGO = "Despesas Pagas"
STAGE_RESTOS_NAO_PROCESSADOS = "Inscrição de Restos a Pagar Não Processados"
STAGE_RESTOS_PROCESSADOS = "Inscrição de Restos a Pagar Processados"
EXPENSE_STAGES = [
    STAGE_EMPENHADO,
    STAGE_LIQUIDADO,
    STAGE_PAGO,
    STAGE_RESTOS_NAO_PROCESSADOS,
    STAGE_RESTOS_PROCESSADOS,
]
MACEIO = "Prefeitura Municipal de Maceió - AL"
MACEIO_IBGE = "2704302"
FOCUS_FUNCTIONS = ["10", "12"]
PREVIEW_YEAR = 2025
PREVIEW_BASELINE_YEAR = 2024
RELEVANT_COMMITMENT_MIN = 1_000_000
LOW_EXECUTION_CSV_PATH = REPORT_DIR / "baixa_execucao_2024.csv"
RESTOS_CSV_PATH = REPORT_DIR / "restos_a_pagar_2024.csv"
SUBFUNCTIONS_CSV_PATH = REPORT_DIR / "subfuncoes_maceio_2024.csv"
MACEIO_DISTRIBUTION_CSV_PATH = REPORT_DIR / "maceio_distribuicao_capitais.csv"
EXECUTION_ABOVE_100_CSV_PATH = REPORT_DIR / "taxas_execucao_acima_100.csv"


def money(value: float) -> str:
    return f"R$ {value:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")


def number(value: float) -> str:
    return f"{value:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")


def integer(value: int) -> str:
    return f"{value:,}".replace(",", ".")


def percent(value: float) -> str:
    if pd.isna(value):
        return "-"
    return f"{value:.1f}%".replace(".", ",")


def millions_axis(value: float, _position: int) -> str:
    return f"R$ {value / 1_000_000:.0f} mi"


def clean_capital_name(series: pd.Series) -> pd.Series:
    return series.str.replace(r"^Prefeitura Municipal (de |do |da )", "", regex=True)


def markdown_table(df: pd.DataFrame) -> str:
    if df.empty:
        return "_Sem dados para exibir._"

    headers = list(df.columns)
    rows = [[str(value) for value in row] for row in df.to_numpy()]
    lines = [
        "| " + " | ".join(headers) + " |",
        "| " + " | ".join(["---"] * len(headers)) + " |",
    ]
    lines.extend("| " + " | ".join(row) + " |" for row in rows)
    return "\n".join(lines)


def html_table(df: pd.DataFrame) -> str:
    if df.empty:
        return '<p class="empty-state">Sem dados para exibir.</p>'

    headers = "".join(f"<th>{html.escape(str(column))}</th>" for column in df.columns)
    body_rows = []

    for row in df.to_numpy():
        cells = "".join(f"<td>{html.escape(str(value))}</td>" for value in row)
        body_rows.append(f"<tr>{cells}</tr>")

    return (
        '<div class="table-wrap">'
        '<table class="data-table">'
        f"<thead><tr>{headers}</tr></thead>"
        f"<tbody>{''.join(body_rows)}</tbody>"
        "</table>"
        "</div>"
    )


def read_optimized_data() -> pd.DataFrame:
    if not PARQUET_PATH.exists():
        generate_parquet()

    return pd.read_parquet(PARQUET_PATH)


def build_function_indicators(df: pd.DataFrame) -> pd.DataFrame:
    functions = df[df["tipo_conta"].eq("funcao")].copy()

    pivot = (
        functions.pivot_table(
            index=[
                "ano",
                "Instituição",
                "Cod.IBGE",
                "UF",
                "População",
                "codigo_funcao",
                "nome_conta",
                "Conta",
            ],
            columns="Coluna",
            values="Valor",
            aggfunc="sum",
            fill_value=0,
        )
        .reset_index()
        .rename_axis(columns=None)
    )

    for stage in EXPENSE_STAGES:
        if stage not in pivot.columns:
            pivot[stage] = 0.0

    pivot["diferenca_empenhado_pago"] = pivot[STAGE_EMPENHADO] - pivot[STAGE_PAGO]
    pivot["taxa_execucao"] = (
        pivot[STAGE_PAGO].div(pivot[STAGE_EMPENHADO]).where(pivot[STAGE_EMPENHADO].gt(0)) * 100
    )
    pivot["restos_a_pagar"] = pivot[STAGE_RESTOS_NAO_PROCESSADOS] + pivot[STAGE_RESTOS_PROCESSADOS]
    pivot["restos_sobre_empenhado"] = (
        pivot["restos_a_pagar"].div(pivot[STAGE_EMPENHADO]).where(pivot[STAGE_EMPENHADO].gt(0))
        * 100
    )
    pivot["pago_per_capita"] = pivot[STAGE_PAGO] / pivot["População"]
    pivot["empenhado_per_capita"] = pivot[STAGE_EMPENHADO] / pivot["População"]

    return pivot


def build_subfunction_indicators(df: pd.DataFrame) -> pd.DataFrame:
    subfunctions = df[df["tipo_conta"].eq("subfuncao")].copy()

    pivot = (
        subfunctions.pivot_table(
            index=[
                "ano",
                "Instituição",
                "Cod.IBGE",
                "UF",
                "População",
                "codigo_funcao",
                "codigo_conta",
                "nome_conta",
                "Conta",
            ],
            columns="Coluna",
            values="Valor",
            aggfunc="sum",
            fill_value=0,
        )
        .reset_index()
        .rename_axis(columns=None)
    )

    for stage in EXPENSE_STAGES:
        if stage not in pivot.columns:
            pivot[stage] = 0.0

    pivot["diferenca_empenhado_pago"] = pivot[STAGE_EMPENHADO] - pivot[STAGE_PAGO]
    pivot["taxa_execucao"] = (
        pivot[STAGE_PAGO].div(pivot[STAGE_EMPENHADO]).where(pivot[STAGE_EMPENHADO].gt(0)) * 100
    )
    pivot["pago_per_capita"] = pivot[STAGE_PAGO] / pivot["População"]

    return pivot


def completeness_table(df: pd.DataFrame) -> pd.DataFrame:
    completeness = (
        df.groupby("ano")["Instituição"]
        .nunique()
        .reset_index(name="capitais")
        .sort_values("ano")
    )
    completeness["status"] = completeness["capitais"].map(
        lambda total: "completo" if total == 26 else "incompleto"
    )
    return completeness


def format_completeness(df: pd.DataFrame) -> pd.DataFrame:
    formatted = df.copy()
    formatted["ano"] = formatted["ano"].astype(str)
    formatted["capitais"] = formatted["capitais"].astype(str)
    return formatted.rename(columns={"ano": "Ano", "capitais": "Capitais", "status": "Status"})


def latest_complete_year(completeness: pd.DataFrame) -> int:
    complete_years = completeness.loc[completeness["capitais"].eq(26), "ano"]
    return int(complete_years.max())


def preview_capitals(df: pd.DataFrame, year: int = PREVIEW_YEAR) -> pd.DataFrame:
    capitals = (
        df[df["ano"].eq(year)][["Instituição", "UF"]]
        .drop_duplicates()
        .sort_values(["UF", "Instituição"])
        .reset_index(drop=True)
    )

    return pd.DataFrame(
        {
            "UF": capitals["UF"],
            "Capital declarante": clean_capital_name(capitals["Instituição"]),
        }
    )


def ranking_focus_functions(indicators: pd.DataFrame, year: int) -> pd.DataFrame:
    focus = indicators[
        indicators["ano"].eq(year) & indicators["codigo_funcao"].isin(FOCUS_FUNCTIONS)
    ].copy()
    focus = focus.sort_values(["codigo_funcao", "pago_per_capita"], ascending=[True, False])
    focus = focus.groupby("codigo_funcao", group_keys=False).head(5)

    return pd.DataFrame(
        {
            "Função": focus["Conta"],
            "Capital": clean_capital_name(focus["Instituição"]),
            "Pago per capita": focus["pago_per_capita"].map(lambda value: money(value)),
            "Taxa de execução": focus["taxa_execucao"].map(percent),
        }
    )


def biggest_gaps(indicators: pd.DataFrame, year: int) -> pd.DataFrame:
    gaps = indicators[indicators["ano"].eq(year)].nlargest(10, "diferenca_empenhado_pago")

    return pd.DataFrame(
        {
            "Capital": clean_capital_name(gaps["Instituição"]),
            "Função": gaps["Conta"],
            "Empenhado": gaps[STAGE_EMPENHADO].map(money),
            "Pago": gaps[STAGE_PAGO].map(money),
            "Diferença": gaps["diferenca_empenhado_pago"].map(money),
            "Taxa de execução": gaps["taxa_execucao"].map(percent),
        }
    )


def low_execution_ranking(indicators: pd.DataFrame, year: int) -> pd.DataFrame:
    ranking = indicators[
        indicators["ano"].eq(year)
        & indicators["taxa_execucao"].notna()
        & indicators[STAGE_EMPENHADO].ge(RELEVANT_COMMITMENT_MIN)
    ].copy()
    return ranking.sort_values("taxa_execucao").head(10)


def format_low_execution_ranking(df: pd.DataFrame) -> pd.DataFrame:
    return pd.DataFrame(
        {
            "Capital": clean_capital_name(df["Instituição"]),
            "Função": df["Conta"],
            "Empenhado": df[STAGE_EMPENHADO].map(money),
            "Pago": df[STAGE_PAGO].map(money),
            "Taxa de execução": df["taxa_execucao"].map(percent),
        }
    )


def restos_a_pagar_panel(indicators: pd.DataFrame, year: int) -> pd.DataFrame:
    panel = indicators[
        indicators["ano"].eq(year)
        & indicators["restos_sobre_empenhado"].notna()
        & indicators[STAGE_EMPENHADO].ge(RELEVANT_COMMITMENT_MIN)
    ].copy()
    return panel.sort_values("restos_sobre_empenhado", ascending=False).head(10)


def format_restos_a_pagar_panel(df: pd.DataFrame) -> pd.DataFrame:
    return pd.DataFrame(
        {
            "Capital": clean_capital_name(df["Instituição"]),
            "Função": df["Conta"],
            "Empenhado": df[STAGE_EMPENHADO].map(money),
            "Restos a pagar": df["restos_a_pagar"].map(money),
            "Restos sobre empenhado": df["restos_sobre_empenhado"].map(percent),
            "Taxa de execução": df["taxa_execucao"].map(percent),
        }
    )


def execution_above_100(indicators: pd.DataFrame, complete_years: list[int]) -> pd.DataFrame:
    outliers = indicators[
        indicators["ano"].isin(complete_years) & indicators["taxa_execucao"].gt(100)
    ].copy()
    return outliers.sort_values("taxa_execucao", ascending=False).head(10)


def format_execution_above_100(df: pd.DataFrame) -> pd.DataFrame:
    return pd.DataFrame(
        {
            "Ano": df["ano"].astype(str),
            "Capital": clean_capital_name(df["Instituição"]),
            "Função": df["Conta"],
            "Empenhado": df[STAGE_EMPENHADO].map(money),
            "Pago": df[STAGE_PAGO].map(money),
            "Taxa de execução": df["taxa_execucao"].map(percent),
        }
    )


def maceio_vs_distribution(indicators: pd.DataFrame, complete_years: list[int]) -> pd.DataFrame:
    focus = indicators[
        indicators["ano"].isin(complete_years) & indicators["codigo_funcao"].isin(FOCUS_FUNCTIONS)
    ].copy()
    focus["rank_pago_pc"] = focus.groupby(["ano", "codigo_funcao"])["pago_per_capita"].rank(
        method="min", ascending=False
    )
    distribution = (
        focus.groupby(["ano", "codigo_funcao", "Conta"], as_index=False)
        .agg(
            media_pago_per_capita=("pago_per_capita", "mean"),
            mediana_pago_per_capita=("pago_per_capita", "median"),
            mediana_taxa_execucao=("taxa_execucao", "median"),
            capitais=("Instituição", "nunique"),
        )
    )
    maceio = focus[focus["Cod.IBGE"].astype(str).eq(MACEIO_IBGE)]
    comparison = maceio.merge(distribution, on=["ano", "codigo_funcao", "Conta"], how="left")

    return comparison.sort_values(["ano", "codigo_funcao"])


def format_maceio_vs_distribution(df: pd.DataFrame) -> pd.DataFrame:
    return pd.DataFrame(
        {
            "Ano": df["ano"].astype(str),
            "Função": df["Conta"],
            "Maceió pago pc": df["pago_per_capita"].map(money),
            "Média pago pc": df["media_pago_per_capita"].map(money),
            "Mediana pago pc": df["mediana_pago_per_capita"].map(money),
            "Posição pago pc": df.apply(
                lambda row: f"{int(row['rank_pago_pc'])}º de {int(row['capitais'])}", axis=1
            ),
            "Maceió execução": df["taxa_execucao"].map(percent),
            "Mediana execução": df["mediana_taxa_execucao"].map(percent),
        }
    )


def maceio_focus_subfunctions(subfunction_indicators: pd.DataFrame, year: int) -> pd.DataFrame:
    subfunctions = subfunction_indicators[
        subfunction_indicators["ano"].eq(year)
        & subfunction_indicators["Cod.IBGE"].astype(str).eq(MACEIO_IBGE)
        & subfunction_indicators["codigo_funcao"].isin(FOCUS_FUNCTIONS)
        & subfunction_indicators[STAGE_PAGO].gt(0)
    ].copy()
    subfunctions["participacao_pago_funcao"] = (
        subfunctions[STAGE_PAGO].div(subfunctions.groupby("codigo_funcao")[STAGE_PAGO].transform("sum"))
        * 100
    )
    return (
        subfunctions.sort_values(["codigo_funcao", STAGE_PAGO], ascending=[True, False])
        .groupby("codigo_funcao", group_keys=False)
        .head(6)
    )


def format_maceio_focus_subfunctions(df: pd.DataFrame) -> pd.DataFrame:
    return pd.DataFrame(
        {
            "Função": df["codigo_funcao"].map({"10": "Saúde", "12": "Educação"}),
            "Subfunção": df["Conta"],
            "Pago": df[STAGE_PAGO].map(money),
            "Pago per capita": df["pago_per_capita"].map(money),
            "Participação na função": df["participacao_pago_funcao"].map(percent),
            "Taxa de execução": df["taxa_execucao"].map(percent),
        }
    )


def maceio_vs_average(indicators: pd.DataFrame, complete_years: list[int]) -> pd.DataFrame:
    focus = indicators[
        indicators["ano"].isin(complete_years) & indicators["codigo_funcao"].isin(FOCUS_FUNCTIONS)
    ].copy()
    maceio = focus[focus["Instituição"].eq(MACEIO)]
    average = (
        focus.groupby(["ano", "codigo_funcao", "Conta"], as_index=False)
        .agg(
            media_taxa_execucao=("taxa_execucao", "mean"),
            media_pago_per_capita=("pago_per_capita", "mean"),
        )
    )
    comparison = maceio.merge(average, on=["ano", "codigo_funcao", "Conta"], how="left")

    return pd.DataFrame(
        {
            "Ano": comparison["ano"].astype(str),
            "Função": comparison["Conta"],
            "Maceió execução": comparison["taxa_execucao"].map(percent),
            "Média execução": comparison["media_taxa_execucao"].map(percent),
            "Maceió pago per capita": comparison["pago_per_capita"].map(money),
            "Média pago per capita": comparison["media_pago_per_capita"].map(money),
        }
    )


def preview_2025_ranking(indicators: pd.DataFrame) -> pd.DataFrame:
    preview = indicators[
        indicators["ano"].eq(PREVIEW_YEAR) & indicators["codigo_funcao"].isin(FOCUS_FUNCTIONS)
    ].copy()
    preview = preview.sort_values(["codigo_funcao", "pago_per_capita"], ascending=[True, False])
    preview = preview.groupby("codigo_funcao", group_keys=False).head(5)

    return pd.DataFrame(
        {
            "Função": preview["Conta"],
            "Capital": clean_capital_name(preview["Instituição"]),
            "Pago per capita": preview["pago_per_capita"].map(money),
            "Taxa de execução": preview["taxa_execucao"].map(percent),
        }
    )


def preview_2025_balanced_panel(indicators: pd.DataFrame) -> pd.DataFrame:
    capitals_2025 = indicators.loc[indicators["ano"].eq(PREVIEW_YEAR), "Instituição"].unique()
    panel = indicators[
        indicators["Instituição"].isin(capitals_2025)
        & indicators["ano"].isin([PREVIEW_BASELINE_YEAR, PREVIEW_YEAR])
        & indicators["codigo_funcao"].isin(FOCUS_FUNCTIONS)
    ].copy()

    comparable = panel.pivot_table(
        index=["Instituição", "UF", "codigo_funcao", "Conta"],
        columns="ano",
        values=["pago_per_capita", "taxa_execucao"],
        aggfunc="first",
    )
    comparable.columns = [f"{metric}_{year}" for metric, year in comparable.columns]
    comparable = comparable.reset_index()

    required_columns = [
        f"pago_per_capita_{PREVIEW_BASELINE_YEAR}",
        f"pago_per_capita_{PREVIEW_YEAR}",
        f"taxa_execucao_{PREVIEW_BASELINE_YEAR}",
        f"taxa_execucao_{PREVIEW_YEAR}",
    ]
    comparable = comparable.dropna(subset=required_columns)
    comparable["variacao_pago_per_capita"] = (
        comparable[f"pago_per_capita_{PREVIEW_YEAR}"]
        .div(comparable[f"pago_per_capita_{PREVIEW_BASELINE_YEAR}"])
        .sub(1)
        .mul(100)
    )
    comparable["variacao_abs"] = comparable["variacao_pago_per_capita"].abs()
    comparable = comparable.sort_values("variacao_abs", ascending=False).head(10)

    return pd.DataFrame(
        {
            "Capital": clean_capital_name(comparable["Instituição"]),
            "Função": comparable["Conta"],
            f"Pago pc {PREVIEW_BASELINE_YEAR}": comparable[
                f"pago_per_capita_{PREVIEW_BASELINE_YEAR}"
            ].map(money),
            f"Pago pc {PREVIEW_YEAR}": comparable[f"pago_per_capita_{PREVIEW_YEAR}"].map(money),
            "Variação pago pc": comparable["variacao_pago_per_capita"].map(percent),
            f"Execução {PREVIEW_BASELINE_YEAR}": comparable[
                f"taxa_execucao_{PREVIEW_BASELINE_YEAR}"
            ].map(percent),
            f"Execução {PREVIEW_YEAR}": comparable[f"taxa_execucao_{PREVIEW_YEAR}"].map(percent),
        }
    )


def write_auxiliary_tables(
    indicators: pd.DataFrame,
    subfunction_indicators: pd.DataFrame,
    complete_years: list[int],
    latest_year: int,
) -> None:
    REPORT_DIR.mkdir(parents=True, exist_ok=True)

    low_execution_ranking(indicators, latest_year).to_csv(
        LOW_EXECUTION_CSV_PATH, index=False, encoding="utf-8-sig"
    )
    restos_a_pagar_panel(indicators, latest_year).to_csv(
        RESTOS_CSV_PATH, index=False, encoding="utf-8-sig"
    )
    maceio_focus_subfunctions(subfunction_indicators, latest_year).to_csv(
        SUBFUNCTIONS_CSV_PATH, index=False, encoding="utf-8-sig"
    )
    maceio_vs_distribution(indicators, complete_years).to_csv(
        MACEIO_DISTRIBUTION_CSV_PATH, index=False, encoding="utf-8-sig"
    )
    execution_above_100(indicators, complete_years).to_csv(
        EXECUTION_ABOVE_100_CSV_PATH, index=False, encoding="utf-8-sig"
    )


def create_charts(indicators: pd.DataFrame, complete_years: list[int], latest_year: int) -> list[Path]:
    CHART_DIR.mkdir(parents=True, exist_ok=True)
    chart_paths: list[Path] = []

    maceio = indicators[
        indicators["ano"].isin(complete_years)
        & indicators["Instituição"].eq(MACEIO)
        & indicators["codigo_funcao"].isin(FOCUS_FUNCTIONS)
    ].copy()

    fig, ax = plt.subplots(figsize=(9, 5))
    for account, group in maceio.groupby("Conta"):
        ax.plot(group["ano"], group["taxa_execucao"], marker="o", label=account)
    ax.set_title("Maceió: taxa de execução em Saúde e Educação")
    ax.set_xlabel("Ano")
    ax.set_ylabel("Taxa de execução (%)")
    ax.set_ylim(bottom=0)
    ax.legend()
    ax.grid(axis="y", alpha=0.3)
    fig.tight_layout()
    path = CHART_DIR / "maceio_taxa_execucao_saude_educacao.png"
    fig.savefig(path, dpi=150)
    plt.close(fig)
    chart_paths.append(path)

    maceio_latest = indicators[
        indicators["ano"].eq(latest_year) & indicators["Cod.IBGE"].astype(str).eq(MACEIO_IBGE)
    ].copy()
    maceio_latest = maceio_latest.sort_values("diferenca_empenhado_pago", ascending=False).head(8)

    fig, ax = plt.subplots(figsize=(10, 6))
    labels = maceio_latest["codigo_funcao"] + " " + maceio_latest["nome_conta"]
    bars = ax.barh(labels, maceio_latest["diferenca_empenhado_pago"], color="#9c6b1f")
    ax.set_title(f"Maceió: maiores diferenças entre empenhado e pago ({latest_year})")
    ax.set_xlabel("Diferença entre empenhado e pago")
    ax.xaxis.set_major_formatter(FuncFormatter(millions_axis))
    ax.bar_label(
        bars,
        labels=[f"R$ {value / 1_000_000:.1f} mi".replace(".", ",") for value in maceio_latest["diferenca_empenhado_pago"]],
        padding=4,
        fontsize=9,
    )
    ax.margins(x=0.12)
    ax.invert_yaxis()
    ax.grid(axis="x", alpha=0.3)
    fig.tight_layout()
    path = CHART_DIR / "maceio_diferencas_empenhado_pago.png"
    fig.savefig(path, dpi=150)
    plt.close(fig)
    chart_paths.append(path)

    focus_latest = indicators[
        indicators["ano"].eq(latest_year) & indicators["codigo_funcao"].isin(FOCUS_FUNCTIONS)
    ].copy()
    top_latest = focus_latest.sort_values("pago_per_capita", ascending=False).groupby(
        "codigo_funcao", group_keys=False
    ).head(5)

    fig, ax = plt.subplots(figsize=(10, 6))
    labels = (
        top_latest["UF"]
        + " - "
        + top_latest["codigo_funcao"]
        + " "
        + top_latest["nome_conta"]
    )
    ax.barh(labels, top_latest["pago_per_capita"], color="#2f6f73")
    ax.set_title(f"Maiores gastos pagos per capita em Saúde e Educação ({latest_year})")
    ax.set_xlabel("Pago per capita (R$)")
    ax.xaxis.set_major_formatter(FuncFormatter(lambda value, _position: f"R$ {value:,.0f}".replace(",", ".")))
    ax.invert_yaxis()
    ax.grid(axis="x", alpha=0.3)
    fig.tight_layout()
    path = CHART_DIR / "ranking_pago_per_capita_saude_educacao.png"
    fig.savefig(path, dpi=150)
    plt.close(fig)
    chart_paths.append(path)

    capitals_2025 = indicators.loc[indicators["ano"].eq(PREVIEW_YEAR), "Instituição"].unique()
    preview_panel = indicators[
        indicators["Instituição"].isin(capitals_2025)
        & indicators["ano"].isin([PREVIEW_BASELINE_YEAR, PREVIEW_YEAR])
        & indicators["codigo_funcao"].isin(FOCUS_FUNCTIONS)
    ].copy()
    preview_comparison = preview_panel.pivot_table(
        index=["Instituição", "UF", "codigo_funcao", "nome_conta"],
        columns="ano",
        values="pago_per_capita",
        aggfunc="first",
    ).dropna(subset=[PREVIEW_BASELINE_YEAR, PREVIEW_YEAR])
    preview_comparison["variacao"] = (
        preview_comparison[PREVIEW_YEAR].div(preview_comparison[PREVIEW_BASELINE_YEAR]).sub(1) * 100
    )
    preview_comparison = preview_comparison.reset_index()
    preview_comparison["label"] = (
        preview_comparison["UF"]
        + " - "
        + preview_comparison["codigo_funcao"]
        + " "
        + preview_comparison["nome_conta"]
    )
    preview_comparison = preview_comparison.reindex(
        preview_comparison["variacao"].abs().sort_values(ascending=False).index
    ).head(10)

    fig, ax = plt.subplots(figsize=(10, 6))
    colors = preview_comparison["variacao"].map(lambda value: "#2f6f73" if value >= 0 else "#9c3f3f")
    ax.barh(preview_comparison["label"], preview_comparison["variacao"], color=colors)
    ax.set_title("Prévia 2025: variação do pago per capita nas capitais declarantes")
    ax.set_xlabel(f"Variação {PREVIEW_BASELINE_YEAR}-{PREVIEW_YEAR}")
    ax.xaxis.set_major_formatter(FuncFormatter(lambda value, _position: f"{value:.0f}%".replace(".", ",")))
    ax.axvline(0, color="#333333", linewidth=0.8)
    ax.invert_yaxis()
    ax.grid(axis="x", alpha=0.3)
    fig.tight_layout()
    path = CHART_DIR / "previa_2025_variacao_pago_per_capita.png"
    fig.savefig(path, dpi=150)
    plt.close(fig)
    chart_paths.append(path)

    return chart_paths


def write_report(
    df: pd.DataFrame,
    indicators: pd.DataFrame,
    subfunction_indicators: pd.DataFrame,
    completeness: pd.DataFrame,
    chart_paths: list[Path],
) -> None:
    REPORT_DIR.mkdir(parents=True, exist_ok=True)

    complete_years = completeness.loc[completeness["capitais"].eq(26), "ano"].astype(int).tolist()
    incomplete_years = completeness.loc[completeness["capitais"].ne(26), "ano"].astype(int).tolist()
    latest_year = latest_complete_year(completeness)
    aggregates = int(df["tipo_conta"].ne("funcao").sum())

    report = f"""# Análise FINBRA - Despesas por Função

## Método

A leitura respeita o formato brasileiro dos CSVs do Siconfi: `latin-1`, separador `;`,
3 linhas iniciais ignoradas e decimal com vírgula. As análises por função usam apenas
linhas classificadas como `funcao`, evitando dupla contagem com totais agregados,
subfunções e `FUxx - Demais Subfunções`.

Foram identificadas {integer(len(df))} linhas na base consolidada. Destas, {integer(aggregates)}
linhas não são funções e ficam fora dos rankings por função.

Também foi gerado um dashboard visual em `relatorios/analise_finbra.html`, com estilos em
`relatorios/dashboard.css`, para uma leitura mais confortável dos resultados.
"""

    report += "\n## Completude por ano\n\n"
    report += markdown_table(format_completeness(completeness))
    report += "\n\n"

    report += (
        f"Os anos completos para comparação histórica são {', '.join(map(str, complete_years))}. "
        f"O ano de {', '.join(map(str, incomplete_years))} está incompleto e não foi usado "
        "nas comparações históricas principais.\n\n"
    )

    report += f"## Rankings de Saúde e Educação em {latest_year}\n\n"
    report += markdown_table(ranking_focus_functions(indicators, latest_year))
    report += "\n\n"

    report += f"## Maiores diferenças entre empenhado e pago em {latest_year}\n\n"
    report += markdown_table(biggest_gaps(indicators, latest_year))
    report += "\n\n"

    report += f"## Baixa execução financeira em {latest_year}\n\n"
    report += (
        f"O recorte abaixo considera funções com pelo menos {money(RELEVANT_COMMITMENT_MIN)} "
        "em despesas empenhadas, para evitar que valores residuais dominem a leitura.\n\n"
    )
    report += markdown_table(format_low_execution_ranking(low_execution_ranking(indicators, latest_year)))
    report += f"\n\nTabela auxiliar: `{LOW_EXECUTION_CSV_PATH.relative_to(ROOT_DIR).as_posix()}`.\n\n"

    report += f"## Restos a pagar sobre empenhado em {latest_year}\n\n"
    report += markdown_table(format_restos_a_pagar_panel(restos_a_pagar_panel(indicators, latest_year)))
    report += f"\n\nTabela auxiliar: `{RESTOS_CSV_PATH.relative_to(ROOT_DIR).as_posix()}`.\n\n"

    report += "## Maceió contra distribuição das capitais\n\n"
    report += markdown_table(format_maceio_vs_distribution(maceio_vs_distribution(indicators, complete_years)))
    report += f"\n\nTabela auxiliar: `{MACEIO_DISTRIBUTION_CSV_PATH.relative_to(ROOT_DIR).as_posix()}`.\n\n"

    report += f"## Subfunções de Saúde e Educação em Maceió ({latest_year})\n\n"
    report += markdown_table(
        format_maceio_focus_subfunctions(maceio_focus_subfunctions(subfunction_indicators, latest_year))
    )
    report += f"\n\nTabela auxiliar: `{SUBFUNCTIONS_CSV_PATH.relative_to(ROOT_DIR).as_posix()}`.\n\n"

    report += "## Taxas de execução acima de 100%\n\n"
    report += (
        "Algumas funções aparecem com despesas pagas maiores que as empenhadas no mesmo ano. "
        "Isso não deve ser lido automaticamente como erro: pode refletir pagamentos de restos "
        "de exercícios anteriores ou outras dinâmicas contábeis. O ponto é tratar esses casos "
        "como alerta interpretativo antes de comparar rankings.\n\n"
    )
    report += markdown_table(format_execution_above_100(execution_above_100(indicators, complete_years)))
    report += f"\n\nTabela auxiliar: `{EXECUTION_ABOVE_100_CSV_PATH.relative_to(ROOT_DIR).as_posix()}`.\n\n"

    report += "## Maceió contra média das capitais\n\n"
    report += markdown_table(maceio_vs_average(indicators, complete_years))
    report += "\n\n"

    report += f"## Prévia de {PREVIEW_YEAR}: capitais declarantes\n\n"
    report += (
        f"Como {PREVIEW_YEAR} tem apenas parte das capitais declaradas, este recorte não é "
        "comparado com o conjunto completo de capitais. Para aproveitar o dado sem distorcer "
        f"a leitura, a comparação temporal usa somente as capitais que aparecem em {PREVIEW_YEAR}.\n\n"
    )
    report += markdown_table(preview_capitals(df, PREVIEW_YEAR))
    report += "\n\n"

    report += f"### Ranking preliminar de Saúde e Educação em {PREVIEW_YEAR}\n\n"
    report += markdown_table(preview_2025_ranking(indicators))
    report += "\n\n"

    report += (
        f"### Painel balanceado: {PREVIEW_BASELINE_YEAR} vs {PREVIEW_YEAR} "
        "nas mesmas capitais\n\n"
    )
    report += markdown_table(preview_2025_balanced_panel(indicators))
    report += "\n\n"

    report += "## Gráficos\n\n"
    for path in chart_paths:
        relative = path.relative_to(REPORT_DIR).as_posix()
        report += f"![{path.stem}]({relative})\n\n"

    report += """## Conclusões principais

- A comparação anual deve priorizar 2020 a 2024, pois 2025 tem apenas parte das capitais declaradas.
- A prévia de 2025 só compara capitais declarantes contra elas mesmas em 2024.
- Em 2024, Maceió combina alta execução em Saúde com diferenças mais relevantes entre empenhado e pago em Urbanismo e Educação.
- O detalhamento por subfunção mostra que Saúde se concentra em assistência hospitalar e atenção básica, enquanto Educação se concentra em ensino fundamental, administração geral e educação básica.
- Restos a pagar e taxas acima de 100% precisam ser lidos como sinais de dinâmica orçamentária, não apenas como ranking simples.
- Os rankings por função excluem agregados para evitar dupla contagem.
- A leitura per capita é essencial para comparar capitais de portes muito diferentes.
"""

    REPORT_PATH.write_text(report, encoding="utf-8")


def write_dashboard_css() -> None:
    CSS_PATH.write_text(
        """* {
  box-sizing: border-box;
}

:root {
  color-scheme: light;
  --bg: #f5f7f8;
  --surface: #ffffff;
  --ink: #1f2933;
  --muted: #5f6c7b;
  --line: #d8e0e5;
  --accent: #2f6f73;
  --accent-dark: #24595c;
  --warn: #9c6b1f;
  --warn-bg: #fff7e6;
}

body {
  margin: 0;
  background: var(--bg);
  color: var(--ink);
  font-family: Arial, Helvetica, sans-serif;
  line-height: 1.55;
}

.page {
  max-width: 1180px;
  margin: 0 auto;
  padding: 32px 20px 56px;
}

.hero {
  display: grid;
  gap: 16px;
  padding-bottom: 24px;
  border-bottom: 1px solid var(--line);
}

.eyebrow {
  margin: 0;
  color: var(--accent-dark);
  font-size: 0.85rem;
  font-weight: 700;
  letter-spacing: 0;
  text-transform: uppercase;
}

h1,
h2,
h3 {
  margin: 0;
  line-height: 1.2;
}

h1 {
  max-width: 900px;
  font-size: clamp(2rem, 5vw, 4rem);
}

h2 {
  margin-bottom: 12px;
  font-size: 1.45rem;
}

h3 {
  margin: 20px 0 10px;
  font-size: 1.05rem;
}

p {
  margin: 0 0 12px;
}

.lead {
  max-width: 880px;
  color: var(--muted);
  font-size: 1.05rem;
}

.notice {
  border: 1px solid #e8c77d;
  border-left: 5px solid var(--warn);
  background: var(--warn-bg);
  padding: 14px 16px;
  color: #4f3b14;
}

.cards {
  display: grid;
  grid-template-columns: repeat(4, minmax(0, 1fr));
  gap: 12px;
  margin: 24px 0;
}

.metric {
  min-height: 112px;
  padding: 16px;
  background: var(--surface);
  border: 1px solid var(--line);
  border-radius: 8px;
}

.metric span {
  display: block;
  color: var(--muted);
  font-size: 0.85rem;
}

.metric strong {
  display: block;
  margin-top: 8px;
  font-size: 1.8rem;
}

.section {
  margin-top: 28px;
  padding: 22px;
  background: var(--surface);
  border: 1px solid var(--line);
  border-radius: 8px;
}

.table-wrap {
  width: 100%;
  overflow-x: auto;
}

.data-table {
  width: 100%;
  border-collapse: collapse;
  font-size: 0.92rem;
}

.data-table th,
.data-table td {
  padding: 10px 12px;
  border-bottom: 1px solid var(--line);
  text-align: left;
  vertical-align: top;
  white-space: nowrap;
}

.data-table th {
  background: #eef4f5;
  color: #263b40;
  font-weight: 700;
}

.charts {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 16px;
}

.chart {
  margin: 0;
  padding: 12px;
  border: 1px solid var(--line);
  border-radius: 8px;
  background: #fbfcfc;
}

.chart img {
  display: block;
  width: 100%;
  height: auto;
}

.chart figcaption {
  margin-top: 8px;
  color: var(--muted);
  font-size: 0.9rem;
}

.footer {
  margin-top: 28px;
  color: var(--muted);
  font-size: 0.9rem;
}

@media (max-width: 900px) {
  .cards,
  .charts {
    grid-template-columns: 1fr;
  }

  .page {
    padding: 24px 14px 40px;
  }

  .section {
    padding: 16px;
  }
}
""",
        encoding="utf-8",
    )


def write_html_dashboard(
    df: pd.DataFrame,
    indicators: pd.DataFrame,
    subfunction_indicators: pd.DataFrame,
    completeness: pd.DataFrame,
    chart_paths: list[Path],
) -> None:
    write_dashboard_css()

    complete_years = completeness.loc[completeness["capitais"].eq(26), "ano"].astype(int).tolist()
    incomplete_years = completeness.loc[completeness["capitais"].ne(26), "ano"].astype(int).tolist()
    latest_year = latest_complete_year(completeness)
    aggregates = int(df["tipo_conta"].ne("funcao").sum())
    total_capitals = int(df["Instituição"].nunique())
    total_functions = int(df[df["tipo_conta"].eq("funcao")]["Conta"].nunique())

    charts_html = []
    for path in chart_paths:
        relative = path.relative_to(REPORT_DIR).as_posix()
        caption = path.stem.replace("_", " ").capitalize()
        charts_html.append(
            '<figure class="chart">'
            f'<img src="{html.escape(relative)}" alt="{html.escape(caption)}">'
            f"<figcaption>{html.escape(caption)}</figcaption>"
            "</figure>"
        )

    html_content = f"""<!doctype html>
<html lang="pt-BR">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Análise FINBRA - Despesas por Função</title>
  <link rel="stylesheet" href="dashboard.css">
</head>
<body>
  <main class="page">
    <header class="hero">
      <p class="eyebrow">Dashboard visual gerado automaticamente</p>
      <h1>Análise FINBRA - Despesas por Função</h1>
      <p class="lead">
        Visão consolidada das despesas das capitais brasileiras por função, com foco
        na relação entre despesas empenhadas e pagas.
      </p>
      <div class="notice">
        Este dashboard visual complementa o relatório técnico em Markdown
        <strong>analise_finbra.md</strong>. A versão Markdown foi mantida para auditoria,
        diff em Git e rastreabilidade do processo.
      </div>
    </header>

    <section class="cards" aria-label="Indicadores gerais">
      <div class="metric"><span>Linhas consolidadas</span><strong>{integer(len(df))}</strong></div>
      <div class="metric"><span>Capitais identificadas</span><strong>{total_capitals}</strong></div>
      <div class="metric"><span>Funções analisáveis</span><strong>{total_functions}</strong></div>
      <div class="metric"><span>Linhas fora dos rankings por função</span><strong>{integer(aggregates)}</strong></div>
    </section>

    <section class="section">
      <h2>Método</h2>
      <p>
        A leitura respeita o formato brasileiro dos CSVs do Siconfi: encoding
        <strong>latin-1</strong>, separador <strong>;</strong>, três linhas iniciais
        ignoradas e decimal com vírgula. As análises por função usam apenas linhas
        classificadas como <strong>funcao</strong>, evitando dupla contagem com totais,
        subfunções e demais agregações.
      </p>
    </section>

    <section class="section">
      <h2>Completude por ano</h2>
      {html_table(format_completeness(completeness))}
      <p>
        Anos completos para comparação histórica: {html.escape(", ".join(map(str, complete_years)))}.
        Ano(s) incompleto(s): {html.escape(", ".join(map(str, incomplete_years)))}.
      </p>
    </section>

    <section class="section">
      <h2>Rankings de Saúde e Educação em {latest_year}</h2>
      {html_table(ranking_focus_functions(indicators, latest_year))}
    </section>

    <section class="section">
      <h2>Maiores diferenças entre empenhado e pago em {latest_year}</h2>
      {html_table(biggest_gaps(indicators, latest_year))}
    </section>

    <section class="section">
      <h2>Baixa execução financeira em {latest_year}</h2>
      <p>
        O recorte considera funções com pelo menos {html.escape(money(RELEVANT_COMMITMENT_MIN))}
        em despesas empenhadas, reduzindo o ruído de valores residuais.
      </p>
      {html_table(format_low_execution_ranking(low_execution_ranking(indicators, latest_year)))}
    </section>

    <section class="section">
      <h2>Restos a pagar sobre empenhado em {latest_year}</h2>
      {html_table(format_restos_a_pagar_panel(restos_a_pagar_panel(indicators, latest_year)))}
    </section>

    <section class="section">
      <h2>Maceió contra distribuição das capitais</h2>
      {html_table(format_maceio_vs_distribution(maceio_vs_distribution(indicators, complete_years)))}
    </section>

    <section class="section">
      <h2>Subfunções de Saúde e Educação em Maceió ({latest_year})</h2>
      {html_table(format_maceio_focus_subfunctions(maceio_focus_subfunctions(subfunction_indicators, latest_year)))}
    </section>

    <section class="section">
      <h2>Taxas de execução acima de 100%</h2>
      <p>
        Casos em que despesas pagas superam empenhadas no mesmo ano devem ser tratados como
        alerta interpretativo, pois podem refletir pagamentos de restos de exercícios anteriores
        ou outras dinâmicas contábeis.
      </p>
      {html_table(format_execution_above_100(execution_above_100(indicators, complete_years)))}
    </section>

    <section class="section">
      <h2>Maceió contra média das capitais</h2>
      {html_table(maceio_vs_average(indicators, complete_years))}
    </section>

    <section class="section">
      <h2>Prévia de {PREVIEW_YEAR}: capitais declarantes</h2>
      <p>
        Como {PREVIEW_YEAR} tem apenas parte das capitais declaradas, este recorte não é
        comparado com o conjunto completo de capitais. A comparação temporal usa somente
        as capitais que aparecem em {PREVIEW_YEAR}.
      </p>
      {html_table(preview_capitals(df, PREVIEW_YEAR))}

      <h3>Ranking preliminar de Saúde e Educação em {PREVIEW_YEAR}</h3>
      {html_table(preview_2025_ranking(indicators))}

      <h3>Painel balanceado: {PREVIEW_BASELINE_YEAR} vs {PREVIEW_YEAR}</h3>
      {html_table(preview_2025_balanced_panel(indicators))}
    </section>

    <section class="section">
      <h2>Gráficos</h2>
      <div class="charts">
        {''.join(charts_html)}
      </div>
    </section>

    <section class="section">
      <h2>Conclusões principais</h2>
      <ul>
        <li>A comparação anual deve priorizar 2020 a 2024, pois 2025 tem apenas parte das capitais declaradas.</li>
        <li>A prévia de 2025 compara capitais declarantes contra elas mesmas em 2024.</li>
        <li>Em 2024, Maceió combina alta execução em Saúde com diferenças mais relevantes entre empenhado e pago em Urbanismo e Educação.</li>
        <li>O detalhamento por subfunção mostra concentração em assistência hospitalar, atenção básica, ensino fundamental e administração geral.</li>
        <li>Restos a pagar e taxas acima de 100% precisam ser lidos como sinais de dinâmica orçamentária, não apenas como ranking simples.</li>
        <li>Os rankings por função excluem agregados para evitar dupla contagem.</li>
        <li>A leitura per capita é essencial para comparar capitais de portes diferentes.</li>
      </ul>
    </section>

    <footer class="footer">
      Gerado por <code>scripts/analisar_indicadores.py</code>.
    </footer>
  </main>
</body>
</html>
"""

    HTML_REPORT_PATH.write_text(html_content, encoding="utf-8")


def main() -> None:
    df = read_optimized_data()
    completeness = completeness_table(df)
    indicators = build_function_indicators(df)
    subfunction_indicators = build_subfunction_indicators(df)
    complete_years = completeness.loc[completeness["capitais"].eq(26), "ano"].astype(int).tolist()
    latest_year = latest_complete_year(completeness)
    write_auxiliary_tables(indicators, subfunction_indicators, complete_years, latest_year)
    chart_paths = create_charts(indicators, complete_years, latest_year)
    write_report(df, indicators, subfunction_indicators, completeness, chart_paths)
    write_html_dashboard(df, indicators, subfunction_indicators, completeness, chart_paths)

    print(f"Relatorio gerado em: {REPORT_PATH.relative_to(ROOT_DIR)}")
    print(f"Dashboard visual gerado em: {HTML_REPORT_PATH.relative_to(ROOT_DIR)}")
    print(f"Estilos do dashboard gerados em: {CSS_PATH.relative_to(ROOT_DIR)}")
    print("Tabelas auxiliares geradas em: relatorios/*.csv")
    for path in chart_paths:
        print(f"Grafico gerado em: {path.relative_to(ROOT_DIR)}")


if __name__ == "__main__":
    main()
