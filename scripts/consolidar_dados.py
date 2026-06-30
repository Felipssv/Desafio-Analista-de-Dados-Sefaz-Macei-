from __future__ import annotations

import re
from pathlib import Path

import pandas as pd


ROOT_DIR = Path(__file__).resolve().parents[1]
EXTRACTED_DIR = ROOT_DIR / "dados_extraidos"
EXPECTED_COLUMNS = [
    "Instituição",
    "Cod.IBGE",
    "UF",
    "População",
    "Coluna",
    "Conta",
    "Identificador da Conta",
    "Valor",
]


def classify_account(account: str) -> str:
    if re.match(r"^\d{2} - ", account):
        return "funcao"
    if re.match(r"^\d{2}\.\d{3} - ", account):
        return "subfuncao"
    if re.match(r"^FU\d{2} - ", account):
        return "demais_subfuncoes"
    return "agregado"


def split_account(account: str) -> tuple[str | None, str]:
    if " - " not in account:
        return None, account

    code, name = account.split(" - ", 1)
    return code, name


def read_finbra_csv(csv_path: Path) -> pd.DataFrame:
    year = int(csv_path.parent.name)

    df = pd.read_csv(
        csv_path,
        sep=";",
        skiprows=3,
        encoding="latin-1",
        decimal=",",
        thousands=".",
        dtype={"Cod.IBGE": "string", "UF": "string"},
    )

    missing_columns = set(EXPECTED_COLUMNS) - set(df.columns)
    if missing_columns:
        missing = ", ".join(sorted(missing_columns))
        raise ValueError(f"{csv_path} nao contem as colunas esperadas: {missing}")

    df = df[EXPECTED_COLUMNS].copy()
    df["ano"] = year
    df["População"] = pd.to_numeric(df["População"], errors="raise").astype("Int64")
    df["Valor"] = pd.to_numeric(df["Valor"], errors="raise")
    df["tipo_conta"] = df["Conta"].map(classify_account)

    account_parts = df["Conta"].map(split_account)
    df["codigo_conta"] = account_parts.map(lambda item: item[0])
    df["nome_conta"] = account_parts.map(lambda item: item[1])
    df["codigo_funcao"] = df["codigo_conta"].str.extract(r"^(\d{2})", expand=False)

    return df


def load_consolidated_data(extracted_dir: Path = EXTRACTED_DIR) -> pd.DataFrame:
    csv_files = sorted(extracted_dir.glob("*/finbra.csv"))

    if not csv_files:
        raise FileNotFoundError(
            f"Nenhum finbra.csv encontrado em {extracted_dir}. "
            "Execute scripts/descompactar_arquivos.py primeiro."
        )

    frames = [read_finbra_csv(csv_path) for csv_path in csv_files]
    return pd.concat(frames, ignore_index=True)


def print_validation_summary(df: pd.DataFrame) -> None:
    capitals_by_year = df.groupby("ano")["Instituição"].nunique().sort_index()
    stages = sorted(df["Coluna"].unique())
    account_types = df["tipo_conta"].value_counts().sort_index()

    print("Capitais por ano:")
    for year, total in capitals_by_year.items():
        status = "incompleto" if total < 26 else "completo"
        print(f"- {year}: {total} capitais ({status})")

    print("\nEstagios de despesa:")
    for stage in stages:
        print(f"- {stage}")

    print("\nTipos de conta:")
    for account_type, total in account_types.items():
        print(f"- {account_type}: {total} linhas")

    print(f"\nLinhas consolidadas: {len(df)}")
    print(f"Valor numerico: {pd.api.types.is_numeric_dtype(df['Valor'])}")
    print(f"Acentos preservados: {'10 - Saúde' in set(df['Conta']) and '12 - Educação' in set(df['Conta'])}")


def main() -> None:
    df = load_consolidated_data()
    print_validation_summary(df)


if __name__ == "__main__":
    main()
