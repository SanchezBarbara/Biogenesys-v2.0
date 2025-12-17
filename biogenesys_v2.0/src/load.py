# Contenido de src/load.py

import pandas as pd

def save_data(df: pd.DataFrame, output_path: str):
       df.to_csv(output_path, index=False)