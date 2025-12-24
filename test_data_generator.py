import pandas as pd
import os
import warnings

# Ignorar advertencias molestas de pandas
warnings.filterwarnings("ignore")

print("--- Iniciando proceso ---")

# 1. Cargar el dataset como texto puro primero para evitar confusiones
df = pd.read_csv('datos_limpios.csv', encoding='ISO-8859-1')
print("Archivo cargado correctamente.")

# 2. CONVERSIÓN GLOBAL BLINDADA
# Convertimos toda la columna de fechas de una sola vez.
# dayfirst=True le dice a Python: "El primer número es el DÍA, no el mes".
print("Normalizando fechas...")
df['Order Date'] = pd.to_datetime(df['Order Date'], dayfirst=True)

# Crear carpeta para los archivos de prueba
os.makedirs('archivos_sucios', exist_ok=True)

# Vamos a separar por Región
column_split = 'Region' 
unique_values = df[column_split].unique()[:5] 

print(f"Generando archivos corruptos para: {unique_values}")

for i, val in enumerate(unique_values):
    # Filtrar datos por esa región
    subset = df[df[column_split] == val].copy()
    
    # --- AQUI EMPIEZA EL CAOS ---
    
    # Error 1: Nombres de columnas inconsistentes
    if i == 1:
        subset.rename(columns={'Sales': 'Ventas_Totales', 'Profit': 'Ganancia'}, inplace=True)
    elif i == 2:
        subset.rename(columns={'Sales': 'monto', 'Quantity': 'cant'}, inplace=True)
        
    # Error 2: Fechas en formatos diferentes (Como texto)
    # Como ya son objetos datetime, usamos .dt.strftime directamente
    if 'Order Date' in subset.columns:
        if i == 0:
            # Formato DD-MM-YYYY (con guiones)
            subset['Order Date'] = subset['Order Date'].dt.strftime('%d-%m-%Y')
        elif i == 3:
             # Formato YYYY/MM/DD (estilo base de datos)
            subset['Order Date'] = subset['Order Date'].dt.strftime('%Y/%m/%d')
        # Los demás se quedan con el formato por defecto YYYY-MM-DD

    # Error 3: Guardar en diferentes formatos (CSV vs Excel)
    filename = f"archivos_sucios/reporte_{val.replace(' ', '_')}"
    
    try:
        if i % 2 == 0:
            subset.to_csv(f"{filename}.csv", index=False)
            print(f" -> Generado: {filename}.csv")
        else:
            subset.to_excel(f"{filename}.xlsx", index=False)
            print(f" -> Generado: {filename}.xlsx")
    except Exception as e:
        print(f"Hubo un error guardando el archivo {filename}: {e}")

print("\n¡Misión Cumplida! Revisa la carpeta 'archivos_sucios'.")