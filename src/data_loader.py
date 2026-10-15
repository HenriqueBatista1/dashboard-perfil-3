from pathlib import Path

import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_DATA_PATH = (
	PROJECT_ROOT / "data" / "raw" / "dados_habitos_sono_rotina_academica.xlsx"
)
DATA_SHEET = "Dados"


def load_data(file_path: str | Path = DEFAULT_DATA_PATH) -> pd.DataFrame:
	"""Carrega a aba principal da planilha sem transformar os dados."""
	path = Path(file_path)
	if not path.is_file():
		raise FileNotFoundError(f"Planilha nao encontrada: {path}")

	return pd.read_excel(path, sheet_name=DATA_SHEET)
