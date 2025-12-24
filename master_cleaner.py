import pandas as pd
import glob
import os
import time
import warnings

# Configuración inicial
warnings.simplefilter(action='ignore', category=UserWarning)
print("--- 🧹 INICIANDO PROTOCOLO DE LIMPIEZA DE DATOS V2.0 🧹 ---")

carpeta_entrada = 'archivos_sucios'
archivo_salida = 'REPORTE_MAESTRO_2025.xlsx'

archivos_csv = glob.glob(os.path.join(carpeta_entrada, "*.csv"))
archivos_excel = glob.glob(os.path.join(carpeta_entrada, "*.xlsx"))
todos_los_archivos = archivos_csv + archivos_excel

print(f"📂 Archivos detectados: {len(todos_los_archivos)}")

lista_dfs = []

# Diccionario de normalización
mapa_columnas = {
    'Ventas_Totales': 'Sales',
    'monto': 'Sales',
    'Ganancia': 'Profit',
    'cant': 'Quantity',
}

for archivo in todos_los_archivos:
    nombre_archivo = os.path.basename(archivo)
    print(f"Processing: {nombre_archivo}...", end=" ")
    
    try:
        # Leer archivo
        if archivo.endswith('.csv'):
            df_temp = pd.read_csv(archivo)
        else:
            df_temp = pd.read_excel(archivo)
            
        # 1. Normalizar nombres de columnas
        df_temp.rename(columns=mapa_columnas, inplace=True)
        
        # 2. Convertir TODAS las columnas de fecha a objetos de tiempo real
        # Esto permite que Python entienda las fechas matemáticamente primero
        cols_fechas = ['Order Date', 'Ship Date']
        
        for col in cols_fechas:
            if col in df_temp.columns:
                # 'dayfirst=True' ayuda con formatos latinos (15/01/2023)
                df_temp[col] = pd.to_datetime(df_temp[col], dayfirst=True, errors='coerce')
        
        # 3. Etiquetar origen
        df_temp['Archivo_Origen'] = nombre_archivo
        
        lista_dfs.append(df_temp)
        print("✅ [OK]")
        
    except Exception as e:
        print(f"❌ [ERROR]: {e}")

# FUSIÓN
if lista_dfs:
    print("\nFusionando datos...", end=" ")
    df_maestro = pd.concat(lista_dfs, ignore_index=True)
    
    # --- ✨ SECCIÓN NUEVA: MAQUILLAJE FINAL ✨ ---
    # Aquí le damos el formato visual bonito para Excel (sin horas)
    print("\nAplicando formato visual a fechas...", end=" ")
    
    cols_fechas = ['Order Date', 'Ship Date']
    for col in cols_fechas:
        if col in df_maestro.columns:
            # Opción A: Formato Latino (DD-MM-AAAA) -> Recomendado para clientes locales
            df_maestro[col] = df_maestro[col].dt.strftime('%d-%m-%Y')
            
            # Opción B: Formato Internacional (AAAA-MM-DD) -> Descomenta si prefieres este
            # df_maestro[col] = df_maestro[col].dt.strftime('%Y-%m-%d')

    # Limpieza final
    df_maestro.drop_duplicates(inplace=True)
    
    # Exportar
    df_maestro.to_excel(archivo_salida, index=False)
    print("✅ ¡HECHO!")
    
    print("\n" + "="*50)
    print(f"🏆 REPORTE GENERADO: {archivo_salida}")
    print(f"📊 Filas procesadas: {len(df_maestro)}")
    print(f"📅 Fechas formateadas: DD-MM-AAAA (Sin horas)")
    print("="*50)

else:
    print("No se encontraron archivos.")