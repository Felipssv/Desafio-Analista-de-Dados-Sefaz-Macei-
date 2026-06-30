from __future__ import annotations

from pathlib import Path

import pandas as pd

from consolidar_dados import ROOT_DIR, load_consolidated_data
from descompactar_arquivos import extract_finbra_files


OUTPUT_DIR = ROOT_DIR / "dados_processados"
PARQUET_PATH = OUTPUT_DIR / "finbra_consolidado.parquet"


def ensure_extracted_data() -> None:
    extracted_files = sorted((ROOT_DIR / "dados_extraidos").glob("*/finbra.csv"))
    if extracted_files:
        return

    print("Dados extraidos nao encontrados. Executando descompactacao...")
    extract_finbra_files()


def generate_parquet(parquet_path: Path = PARQUET_PATH) -> Path:
    ensure_extracted_data()
    df = load_consolidated_data()

    parquet_path.parent.mkdir(parents=True, exist_ok=True)
    df.to_parquet(parquet_path, index=False)

    return parquet_path


def main() -> None:
    parquet_path = generate_parquet()
    df = load_consolidated_data()
    df_parquet = pd.read_parquet(parquet_path)

    if len(df) != len(df_parquet):
        raise ValueError(
            f"Divergencia de linhas: consolidado={len(df)} parquet={len(df_parquet)}"
        )

    print(f"Base otimizada gerada em: {parquet_path.relative_to(ROOT_DIR)}")
    print(f"Linhas gravadas: {len(df_parquet)}")
    print(f"Colunas gravadas: {len(df_parquet.columns)}")


if __name__ == "__main__":
    main()
