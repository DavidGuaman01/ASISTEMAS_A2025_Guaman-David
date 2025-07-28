

import pandas as pd

# 1. Cargar Datos (Simulados para demostración)
#    Asumimos dos DataFrames de Pandas:
#    - df_source: Datos del sistema fuente (ej. Reporte de Ventas del ERP)
#    - df_target: Datos del sistema destino (ej. Extracto de Banco para ingresos)

data_source = {
    'ID_Transaccion': [101, 102, 103, 104, 105, 106, 109, 109],
    'Fecha': ['2023-01-01', '2023-01-02', '2023-01-03', '2023-01-04', '2023-01-05', '2023-01-07', '2023-01-09', '2023-01-09'],
    'Monto': [100.00, 250.50, 50.00, 120.75, 300.00, 400.00, 150.00, 150.00],
    'ID_Entidad': ['CLI001', 'CLI002', 'CLI001', 'CLI003', 'CLI002', 'CLI005', 'CLI007', 'CLI007']
}
df_source = pd.DataFrame(data_source)

data_target = {
    'ID_Transaccion': [101, 102, 104, 107, 105, 108, 109, 110],
    'Fecha': ['2023-01-01', '2023-01-02', '2023-01-04', '2023-01-06', '2023-01-05', '2023-01-08', '2023-01-09', '2023-01-11'],
    'Monto': [100.00, 250.50, 120.75, 80.00, 300.00, 500.00, 149.99, 200.00],
    'ID_Entidad': ['CLI001', 'CLI002', 'CLI003', 'CLI004', 'CLI002', 'CLI006', 'CLI007', 'CLI008']
}
df_target = pd.DataFrame(data_target)

print("DataFrame Origen (df_source):")
print(df_source)
print("\nDataFrame Destino (df_target):")
print(df_target)

# 2. Pre-procesamiento (limpieza, estandarización de formatos)
#    - Asegurar que las columnas clave tengan el mismo tipo de dato en ambos DataFrames.
#    - Convertir columnas de fecha a formato datetime si no lo están.
df_source['Fecha'] = pd.to_datetime(df_source['Fecha'])
df_target['Fecha'] = pd.to_datetime(df_target['Fecha'])

# 3. Realizar la Conciliación base utilizando un 'outer merge' con indicador
#    Para identificar transacciones que existen en un lado pero no en el otro,
#    se realiza un merge basado en 'ID_Transaccion' y 'ID_Entidad'.
df_reconciled_base = pd.merge(df_source, df_target, on=['ID_Transaccion', 'ID_Entidad'],
                              how='outer', indicator=True, suffixes=('_source', '_target'))

# 4. Identificar y Categorizar Discrepancias

# 4.1. Transacciones solo en el sistema fuente ('left_only')
unmatched_source = df_reconciled_base[df_reconciled_base['_merge'] == 'left_only'].copy()
# Limpiar columnas para mejor visualización, manteniendo solo las relevantes del origen
unmatched_source = unmatched_source.filter(regex='_source$|ID_Transaccion|ID_Entidad|_merge', axis=1)
unmatched_source.columns = unmatched_source.columns.str.replace('_source', '')
print("\n--- Transacciones solo en el Origen (df_source) ---")
print(unmatched_source)

# 4.2. Transacciones solo en el sistema destino ('right_only')
unmatched_target = df_reconciled_base[df_reconciled_base['_merge'] == 'right_only'].copy()
# Limpiar columnas para mejor visualización, manteniendo solo las relevantes del destino
unmatched_target = unmatched_target.filter(regex='_target$|ID_Transaccion|ID_Entidad|_merge', axis=1)
unmatched_target.columns = unmatched_target.columns.str.replace('_target', '')
print("\n--- Transacciones solo en el Destino (df_target) ---")
print(unmatched_target)

# 4.3. Transacciones que coinciden por ID pero pueden tener discrepancias de Monto/Fecha
potential_matches = df_reconciled_base[df_reconciled_base['_merge'] == 'both'].copy()

# Identificar discrepancias de Monto o Fecha
discrepancies_value = potential_matches[
    (potential_matches['Monto_source'] != potential_matches['Monto_target']) |
    (potential_matches['Fecha_source'] != potential_matches['Fecha_target'])
].copy()
print("\n--- Discrepancias de Monto/Fecha (ID_Transaccion e ID_Entidad coinciden) ---")
print(discrepancies_value)

# 4.4. Transacciones perfectamente conciliadas (ID, Entidad, Monto y Fecha coinciden)
# Se excluyen las que tenían discrepancias de valor
perfect_matches = potential_matches[
    (potential_matches['Monto_source'] == potential_matches['Monto_target']) &
    (potential_matches['Fecha_source'] == potential_matches['Fecha_target'])
].copy()
print("\n--- Transacciones Perfectamente Conciliadas ---")
print(perfect_matches)

# 4.5. Detección de duplicados dentro de un solo DataFrame (ej. df_source)
duplicates_source = df_source[df_source.duplicated(subset=['ID_Transaccion', 'ID_Entidad'], keep=False)].copy()
if not duplicates_source.empty:
    print("\n--- Duplicados detectados en el Origen (df_source) ---")
    print(duplicates_source.sort_values(by=['ID_Transaccion', 'ID_Entidad']))
else:
    print("\n--- No se encontraron duplicados en el Origen (df_source) ---")

duplicates_target = df_target[df_target.duplicated(subset=['ID_Transaccion', 'ID_Entidad'], keep=False)].copy()
if not duplicates_target.empty:
    print("\n--- Duplicados detectados en el Destino (df_target) ---")
    print(duplicates_target.sort_values(by=['ID_Transaccion', 'ID_Entidad']))
else:
    print("\n--- No se encontraron duplicados en el Destino (df_target) ---")