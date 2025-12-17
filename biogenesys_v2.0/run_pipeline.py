# Contenido COMPLETO de run_pipeline.py (V2.0: Foco en Arquitectura Modular y Validación)

import pandas as pd
import os
from src.extract import load_data
from src.transform import filter_data, clean_schema, feature_engineer 
from src.load import save_data
from src.validate import validate_data_quality # Importación de la Capa de Validación


# --- CONFIGURACIÓN DE RUTAS Y ARCHIVOS ---
# NOTA: Busca el archivo DENTRO de la carpeta 'data/' para portabilidad
INPUT_FILE = os.path.join(os.getcwd(), 'data_latinoamerica.csv') 
OUTPUT_FILE = os.path.join(os.getcwd(), 'data_procesada_biogenesys_v2.csv')

# --- CONFIGURACIÓN DE CALIDAD DE DATOS (Validation Layer) ---
# Columnas que no deben ser negativas (diarias)
COLUMNAS_CRITICAS = ['new_confirmed', 'new_deceased'] 
# Columnas que deben ser monótonas (acumulativas)
COLUMNAS_ACUMULADAS = ['cumulative_confirmed', 'cumulative_deceased', 'cumulative_vaccine_doses_administered'] 


def run_pipeline():
    """Orquesta el proceso ETL y la Capa de Validación para Biogenesys v2.0."""
    
    print("==================================================")
    print("      Iniciando Pipeline Biogenesys v2.0")
    print("   (Foco: Arquitectura Modular y Validación)")
    print("==================================================")
    
    # 1. EXTRACT: Carga de Datos
    try:
        print(f"\n1. EXTRACT: Cargando datos desde {INPUT_FILE}...")
        df_raw = load_data(INPUT_FILE)
        print(f"   Datos cargados exitosamente. Filas: {len(df_raw)}")
    except FileNotFoundError:
        print(f"   ERROR: Archivo no encontrado en {INPUT_FILE}. Terminando pipeline.")
        return

    # 1.5. VALIDACIÓN INICIAL (PRUEBA DE FUEGO)
    # 🚨 Se espera que FALLE (demostrando que el error de la V1.0 está en el origen).
    print("\n--- 🚨 PRUEBA DE FUEGO: Validando datos CRUDOS (ESPERAMOS FALLO) ---")
    validate_data_quality(df_raw, COLUMNAS_CRITICAS, COLUMNAS_ACUMULADAS) 
    
    # 2. TRANSFORM: Aplicando Limpieza y Feature Engineering
    print("\n2. TRANSFORM: Aplicando limpieza, correcciones y feature engineering...")
    
    # a. Filtrado
    df_filtered = filter_data(df_raw)
    
    # b. Limpieza (Aquí clean_schema CORRIGE los Negativos con .abs() y la Monotonocidad con .ffill())
    df_clean = clean_schema(df_filtered)
    
    # c. Feature Engineering
    df_final_transformed = feature_engineer(df_clean)
    print(f"   Transformación completada. Filas finales: {len(df_final_transformed)}")

    # 2.5. VALIDACIÓN FINAL (DEMOSTRACIÓN DE AISLAMIENTO)
    # ✅ Debe pasar, probando que la fase de TRANSFORM corrigió los errores.
    print("\n--- ✅ DEMOSTRACIÓN: Validando datos DESPUÉS de la limpieza (DEBE PASAR) ---")
    
    # Detenemos el pipeline si la limpieza NO corrigió los errores.
    if not validate_data_quality(df_clean, COLUMNAS_CRITICAS, COLUMNAS_ACUMULADAS):
        print("\nPIPELINE DETENIDO: La fase de TRANSFORMACIÓN no pudo aislar los errores de calidad.")
        return
        
    # 3. LOAD: Guardamos el dataset procesado y enriquecido (SÓLO si la validación final PASÓ)
    print(f"\n3. LOAD: Guardando datos limpios en {OUTPUT_FILE}...")
    save_data(df_final_transformed, OUTPUT_FILE)
    print("   Datos guardados exitosamente.")
    
    print("==================================================")
    print("      Pipeline v2.0 Finalizado con Éxito.")
    print("==================================================")


if __name__ == "__main__":
    run_pipeline()