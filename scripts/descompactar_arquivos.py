from __future__ import annotations

import shutil
import zipfile
from pathlib import Path


ROOT_DIR = Path(__file__).resolve().parents[1]
INPUT_DIR = ROOT_DIR / "dados_compactos"
OUTPUT_DIR = ROOT_DIR / "dados_extraidos"
CSV_NAME = "finbra.csv"


def extract_finbra_files(input_dir: Path = INPUT_DIR, output_dir: Path = OUTPUT_DIR) -> list[Path]:
    zip_files = sorted(input_dir.glob("*/*.zip"))

    if not zip_files:
        raise FileNotFoundError(f"Nenhum arquivo .zip encontrado em {input_dir}")

    extracted_files: list[Path] = []

    for zip_path in zip_files:
        year = zip_path.parent.name
        target_dir = output_dir / year
        target_path = target_dir / CSV_NAME

        target_dir.mkdir(parents=True, exist_ok=True)

        with zipfile.ZipFile(zip_path) as archive:
            try:
                csv_info = archive.getinfo(CSV_NAME)
            except KeyError as exc:
                raise FileNotFoundError(f"{zip_path} nao contem {CSV_NAME}") from exc

            with archive.open(csv_info) as source, target_path.open("wb") as target:
                shutil.copyfileobj(source, target)

        extracted_files.append(target_path)

    return extracted_files


def main() -> None:
    extracted_files = extract_finbra_files()

    print(f"{len(extracted_files)} arquivo(s) extraido(s):")
    for path in extracted_files:
        print(f"- {path.relative_to(ROOT_DIR)}")


if __name__ == "__main__":
    main()
