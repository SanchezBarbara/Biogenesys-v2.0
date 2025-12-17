

# Contenido de src/validate.py

import pandas as pd

# --- FUNCIÓN DE UTILIDAD: Validación de Monotonocidad ---
def check_monotonicity(df: pd.DataFrame, cumulative_column: str) -> bool:
    """
    Verifica si una columna acumulativa es estrictamente no decreciente.
    Si encuentra una caída, devuelve False.
    """
    
    # Calculamos la diferencia de un día al anterior. Si es < 0, el valor cayó.
    diffs = df[cumulative_column].diff().dropna()
    fallos_count = (diffs < 0).sum()
    
    if fallos_count > 0:
        print(f"   🚨 FALLO CRÍTICO (Monotonocidad): '{cumulative_column}' no es monótona. Cayó {fallos_count} veces.")
        return False
    
    return True

# --- FUNCIÓN PRINCIPAL DE VALIDACIÓN ---
def validate_data_quality(df: pd.DataFrame, critical_columns: list, cumulative_columns: list) -> bool:
    """
    Verifica la calidad de los datos, incluyendo negativos y monotonocidad.
    
    Args:
        df (pd.DataFrame): DataFrame a validar.
        critical_columns (list): Columnas que NO deben tener valores negativos.
        cumulative_columns (list): Columnas que deben ser siempre crecientes (monótonas).
        
    Returns:
        bool: True si la validación pasa.
    """
    print("\n[VALIDATE] Iniciando la validación de calidad de datos...")
    
    fallos_encontrados = False
    
    # 1. VALIDACIÓN DE VALORES NEGATIVOS
    for col in critical_columns:
        if col in df.columns:
            negativos_count = (df[col] < 0).sum()
            if negativos_count > 0:
                print(f"   🚨 FALLO CRÍTICO (Negativos): La columna '{col}' tiene {negativos_count} valores negativos.")
                fallos_encontrados = True
            
    # 2. VALIDACIÓN DE MONOTONOCIDAD
    for col in cumulative_columns:
        if col in df.columns:
            # Ordenar y agrupar por país es crucial para series de tiempo
            df.sort_values(['country_name', 'date'], inplace=True)
            
            # Aplicamos la comprobación de monotonocidad dentro de cada país
            monotonico_por_pais = df.groupby('country_name').apply(
                lambda x: check_monotonicity(x, col),
                include_groups=False
            )
            
            if not all(monotonico_por_pais):
                fallos_encontrados = True
    
    if fallos_encontrados:
        print("   --- ❌ VALIDACIÓN FALLIDA ---")
        return False
    else:
        print("   ✅ VALIDACIÓN EXITOSA: No se encontraron problemas críticos.")
        return True