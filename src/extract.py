# Contenido de src/extract.py

import pandas as pd

def load_data(file_path: str) -> pd.DataFrame:
    """Carga el DataFrame desde la ruta especificada."""
    df = pd.read_csv(file_path, low_memory=False)
    return df