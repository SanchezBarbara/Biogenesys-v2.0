# Contenido de src/transform.py 

import pandas as pd
import numpy as np
import os # Añadido os para consistencia, aunque no se usa en transform

# --- FASE 1: FILTRADO ---
def filter_data(df: pd.DataFrame) -> pd.DataFrame:
    """Filtra el DataFrame por países objetivo, fecha de inicio y nivel nacional."""
    
    paises_expansion = ["Colombia", "Argentina", "Chile", "Mexico", "Peru", "Brazil"]
    paises_location_key = ["AR", "CL", "CO", "MX", "PE", "BR"]
    fecha_objetivo = pd.to_datetime('2021-01-01')
    
    # Aplicar filtros 
    df = df[df["country_name"].isin(paises_expansion)].copy()
    df["date"] = pd.to_datetime(df["date"], errors="coerce")
    df = df[df['date'] > fecha_objetivo].copy()
    df = df[df['location_key'].isin(paises_location_key)].copy()

    # Renombrar location_key a iso_code
    # Esto estandariza el esquema y soluciona el KeyError en clean_schema.
    #df = df.rename(columns={'location_key': 'iso_code'})
    return df

# --- FASE 2: LIMPIEZA DE ESQUEMA (CORRECCIÓN CRÍTICA DE MONOTONOCIDAD) ---
def clean_schema(df: pd.DataFrame) -> pd.DataFrame:
    """
    Limpia y estandariza el esquema del DataFrame:
    - Eliminación de NaNs totales.
    - Drop de columnas con alta tasa de NaNs.
    - Corrección de valores atípicos (negativos a absolutos).
    - Imputación de valores faltantes (ffill, media, 0).
    - CORRECCIÓN FORZADA DE MONOTONOCIDAD (NUEVO).
    """
    
    # 1. Eliminación de Filas y Columnas Totalmente Nulas (Celda 11)
    df = df.dropna(axis=0, how="all")
    df = df.dropna(axis=1, how="all")
    
    # 2. Drop de columnas con gran cantidad de NaNs (Celda 19)
    columnas_a_eliminar_por_nan = ['new_recovered', 'cumulative_recovered']
    df = df.drop(columns=columnas_a_eliminar_por_nan, errors='ignore')

    # 3. Corrección de Valores (Negativos a Absolutos) (Celda 24)
    # Nota: También se corrige 'new_deceased' aquí, aunque no estaba en tu código original, es crítico.
    df.loc[:, 'new_confirmed'] = df['new_confirmed'].abs()
    df.loc[:, 'new_deceased'] = df['new_deceased'].abs() # ¡Añadido para asegurar la corrección de críticos!


    # 4. LIMPIEZA Y CORRECCIÓN ROBUSTA DE MONOTONOCIDAD (NUEVO CÓDIGO CLAVE)
    print("   Aplicando corrección robusta de monotonocidad (cummax)...")
    
    cols_cumulative = [
        'cumulative_confirmed', 
        'cumulative_deceased', 
        'cumulative_vaccine_doses_administered'
    ]
    
    # Aseguramos que la corrección solo se aplique dentro de cada país y código ISO
    grouping_cols = ['country_name', 'location_key']
    
    for col in cols_cumulative:
        # 4a. Relleno de NaNs con el valor anterior dentro de cada grupo. 
        # Esto soluciona los saltos causados por registros perdidos.
        df[col] = df.sort_values(['date']).groupby(grouping_cols)[col].ffill()
        
        # 4b. Aplicación de CUMMAX (Máximo Acumulado)
        # Esto fuerza la monotonicidad, asegurando que el valor actual nunca sea menor que el valor anterior.
        df[col] = df.groupby(grouping_cols)[col].cummax()
        
        # 4c. Rellenar cualquier NaN remanente (ej. el primer registro de un país) con 0
        df[col] = df[col].fillna(0)


    # 5. Relleno de NaNs: ffill para temperaturas (Celda 25, 26)
    df["minimum_temperature_celsius"] = df["minimum_temperature_celsius"].ffill()
    df["maximum_temperature_celsius"] = df["maximum_temperature_celsius"].ffill()
    
    # 6. Relleno de NaNs: Imputación por media (Celda 27)
    columnas_por_media = [
        "rainfall_mm", "relative_humidity", "average_temperature_celsius", 
        # 'new_confirmed' y 'new_deceased' ya se corrigieron con .abs() y NaNs con ffill en 4a.
    ]
    for col in columnas_por_media:
        df[col] = df[col].fillna(df[col].mean())
    
    # La lógica específica de vacunas (ffill por país, luego 0) ha sido reemplazada por 4a, 4b, 4c
    
    # 7.Formatos: Aseguramos que todas las columnas de conteo de personas y población sean INT64.
    
    cols_to_int_in_schema = [
        # Conteo de Casos y Vacunas (Corregidos en 4)
        'new_confirmed', 'new_deceased', 'cumulative_confirmed', 'cumulative_deceased', 
        'cumulative_vaccine_doses_administered',
        # Población Base
        'population', 'population_male', 'population_female', 
        'population_rural', 'population_urban', 'population_largest_city',
        # Rangos Etarios Originales (De datos crudos)
        'population_age_00_09', 'population_age_10_19', 'population_age_20_29',
        'population_age_30_39', 'population_age_40_49', 'population_age_50_59',
        'population_age_60_69', 'population_age_70_79', 'population_age_80_and_older'
    ]
    
    for col in [c for c in cols_to_int_in_schema if c in df.columns]:
        try:
            # 1. Rellenar cualquier NaN remanente con 0 (imprescindible para convertir a int)
            # 2. Convertir explícitamente a entero de 64 bits (int64)
            df[col] = df[col].fillna(0).astype('int64')
        except Exception as e:
            # Esto debería ser raro, pero es bueno para la robustez.
            print(f"  ⚠️ Advertencia: No se pudo convertir '{col}' a INT64. Error: {e}")
    return df


# --- FASE 3: FEATURE ENGINEERING (Sin cambios) --- 
def feature_engineer(df: pd.DataFrame) -> pd.DataFrame:
    """
    Crea características de agrupación (rangos etarios) y todas las tasas 
    proporcionales (muertes, vacunas, casos activos, letalidad, etc.) por 1000 hab.
    """
    print("   Creando Feature Engineering: Agrupaciones y Tasas...")

    # Asegurar que 'population' no sea cero para evitar ZeroDivisionError
    df['population'] = df['population'].replace(0, 1)

    # 1. CÁLCULO DE TASAS BASE POR 1000 HABITANTES
    
    # MUERTES por 1000 habitantes
    df['muertes_por_1000'] = (df['cumulative_deceased'] / df['population']) * 1000
    
    # CASOS por 1000 habitantes (Se asume que esto es 'cumulative_confirmed' / population)
    df['casos_por_1000'] = (df['cumulative_confirmed'] / df['population']) * 1000
    
    # VACUNAS por 1000 habitantes
    df['vacunas_por_1000'] = (df['cumulative_vaccine_doses_administered'] / df['population']) * 1000

    # 2. CÁLCULO DE MÉTRICAS DERIVADAS
    
    # Tasa de letalidad por 1000 (Usando las métricas ya normalizadas)
    # Nota: Usamos np.divide y llenamos NaNs con 0 para manejar divisiones por cero en 'casos_por_1000'
    df['tasa_letalidad_por_1000'] = (
        np.divide(df['muertes_por_1000'], df['casos_por_1000'], out=np.zeros_like(df['muertes_por_1000']), where=df['casos_por_1000']!=0)
    ) * 1000
    
    # Tasa de recuperación por 1000 (Complemento de la letalidad)
    df['tasa_recuperacion_por_1000'] = 1000 - df['tasa_letalidad_por_1000']
    
    # Casos Activos Estimados (Absolutos)
    df['casos_activos_estimados'] = ( df['cumulative_confirmed'] - df['cumulative_deceased'])
    
    # Casos Activos por 1000 habitantes
    df['casos_activos_por_1000'] = ( df['casos_activos_estimados'] / df['population']) * 1000

    # Letalidad Diaria (Absoluta)
    # Usamos np.divide para manejar divisiones por cero si 'new_confirmed' es 0.
    df['letalidad'] = (
        np.divide(df['new_deceased'], df['new_confirmed'], out=np.zeros_like(df['new_deceased']), where=df['new_confirmed']!=0)
    ) * 100

    # 3. AGRUPACIÓN DE RANGOS ETARIOS Y DROP DE COLUMNAS ORIGINALES
    
    # Agrupación de rangos etarios
    df['population_age_10_39'] = (
        df['population_age_10_19'] + df['population_age_20_29'] + df['population_age_30_39']
    )
    df['population_age_40_69'] = (
        df['population_age_40_49'] + df['population_age_50_59'] + df['population_age_60_69']
    )
    df['population_age_70_plus'] = (
        df['population_age_70_79'] + df['population_age_80_and_older']
    )
    
    # Eliminación de columnas originales de población
    columnas_edad_original = [
        'population_age_00_09', 'population_age_10_19', 'population_age_20_29',
        'population_age_30_39', 'population_age_40_49', 'population_age_50_59',
        'population_age_60_69', 'population_age_70_79', 'population_age_80_and_older'
    ]
    df = df.drop(columns=columnas_edad_original, errors='ignore')
    
    # 4. AJUSTE V2.1: CONVERSIÓN FINAL DE COLUMNAS DERIVADAS A INT64
    cols_derived_to_int = [
        'casos_activos_estimados', 
        'population_age_10_39', 
        'population_age_40_69', 
        'population_age_70_plus'
    ]
    
    for col in cols_derived_to_int:
        if col in df.columns:
            # Forzamos la conversión a INT64, ya que provienen de restas y sumas
            df[col] = df[col].astype('int64')
            
    return df