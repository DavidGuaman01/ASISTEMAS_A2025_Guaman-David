import streamlit as st
import pandas as pd

# TÍTULO DE LA APP
st.title("🔍 Herramienta CAAT: Conciliación de Transacciones")

st.markdown("""
Esta herramienta implementa **pruebas computarizadas de auditoría (CAAT)** para identificar discrepancias entre registros del sistema fuente (ERP) y sistema destino (extractos bancarios).
""")

# ----------------------------
# 1. CARGA DE DATOS DE PRUEBA
# ----------------------------

st.header("1️⃣ Datos Simulados")

# Sistema fuente (ejemplo: reporte ERP)
data_source = {
    'ID_Transaccion': [101, 102, 103, 104, 105, 106, 109, 109],
    'Fecha': ['2023-01-01', '2023-01-02', '2023-01-03', '2023-01-04', '2023-01-05', '2023-01-07', '2023-01-09', '2023-01-09'],
    'Monto': [100.00, 250.50, 50.00, 120.75, 300.00, 400.00, 150.00, 150.00],
    'ID_Entidad': ['CLI001', 'CLI002', 'CLI001', 'CLI003', 'CLI002', 'CLI005', 'CLI007', 'CLI007']
}
df_source = pd.DataFrame(data_source)

# Sistema destino (ejemplo: extracto bancario)
data_target = {
    'ID_Transaccion': [101, 102, 104, 107, 105, 108, 109, 110],
    'Fecha': ['2023-01-01', '2023-01-02', '2023-01-04', '2023-01-06', '2023-01-05', '2023-01-08', '2023-01-09', '2023-01-11'],
    'Monto': [100.00, 250.50, 120.75, 80.00, 300.00, 500.00, 149.99, 200.00],
    'ID_Entidad': ['CLI001', 'CLI002', 'CLI003', 'CLI004', 'CLI002', 'CLI006', 'CLI007', 'CLI008']
}
df_target = pd.DataFrame(data_target)

# Conversión de fechas
df_source['Fecha'] = pd.to_datetime(df_source['Fecha'])
df_target['Fecha'] = pd.to_datetime(df_target['Fecha'])

# Mostrar datos
st.subheader("📄 Sistema Fuente (ERP)")
st.dataframe(df_source)

st.subheader("🏦 Sistema Destino (Extracto Bancario)")
st.dataframe(df_target)

# ----------------------------------
# 2. CONCILIACIÓN Y DETECCIÓN CAAT
# ----------------------------------

st.header("2️⃣ Ejecución de Pruebas CAAT")

# Outer merge con indicador
df_merged = pd.merge(df_source, df_target, on=['ID_Transaccion', 'ID_Entidad'],
                     how='outer', indicator=True, suffixes=('_source', '_target'))

# 1. Transacciones solo en el sistema fuente
st.subheader("🟥 Prueba 1: Transacciones solo en el sistema fuente")
left_only = df_merged[df_merged['_merge'] == 'left_only']
st.dataframe(left_only[['ID_Transaccion', 'ID_Entidad', 'Fecha_source', 'Monto_source']])

# 2. Transacciones solo en el sistema destino
st.subheader("🟦 Prueba 2: Transacciones solo en el sistema destino")
right_only = df_merged[df_merged['_merge'] == 'right_only']
st.dataframe(right_only[['ID_Transaccion', 'ID_Entidad', 'Fecha_target', 'Monto_target']])

# 3. Discrepancias en monto o fecha (cuando ID y entidad coinciden)
st.subheader("🟨 Prueba 3: Discrepancias en monto o fecha")
both = df_merged[df_merged['_merge'] == 'both']
discrepancias = both[
    (both['Monto_source'] != both['Monto_target']) |
    (both['Fecha_source'] != both['Fecha_target'])
]
st.dataframe(discrepancias[['ID_Transaccion', 'ID_Entidad', 'Fecha_source', 'Monto_source', 'Fecha_target', 'Monto_target']])

# 4. Transacciones perfectamente conciliadas
st.subheader("✅ Prueba 4: Coincidencias exactas")
exactas = both[
    (both['Monto_source'] == both['Monto_target']) &
    (both['Fecha_source'] == both['Fecha_target'])
]
st.dataframe(exactas[['ID_Transaccion', 'ID_Entidad', 'Fecha_source', 'Monto_source']])

# 5. Duplicados en el sistema fuente
st.subheader("⚠️ Prueba 5: Duplicados en el sistema fuente")
duplicados = df_source[df_source.duplicated(subset=['ID_Transaccion', 'ID_Entidad'], keep=False)]
st.dataframe(duplicados)

# ----------------------------
# 3. RESULTADOS Y ANÁLISIS
# ----------------------------

st.header("📊 3️⃣ Resultados Esperados")
st.markdown("""
- Las transacciones en rojo indican posibles **omisiones en el banco**.
- Las azules muestran **registros no contabilizados en el ERP**.
- Las amarillas señalan **errores de digitación o inconsistencias**.
- Las verdes muestran registros conciliados correctamente.
- Los duplicados podrían indicar errores contables o fraudes.
""")

st.success("✅ Pruebas CAAT ejecutadas correctamente.")