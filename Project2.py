import streamlit as st
import pandas as pd
import io
from datetime import datetime

# Titulo
st.set_page_config(page_title="Auditoría CAAT", layout="wide")
st.title("🔍 Sistema de Auditoría CAAT - Conciliación de Facturas")
st.markdown("""
Esta aplicación compara registros de facturación entre dos sistemas (ERP vs Banco) para identificar:
- Coincidencias exactas
- Facturas faltantes
- Diferencias en monto o fecha
- Duplicados
""")

# Datos simulados
erp_data = [
    {"Factura": "F001", "Fecha": "2025-07-01", "Monto": 100.00},
    {"Factura": "F002", "Fecha": "2025-07-02", "Monto": 200.00},
    {"Factura": "F003", "Fecha": "2025-07-03", "Monto": 150.00},
    {"Factura": "F004", "Fecha": "2025-07-04", "Monto": 180.00},
    {"Factura": "F005", "Fecha": "2025-07-05", "Monto": 300.00},
    {"Factura": "F005", "Fecha": "2025-07-05", "Monto": 300.00},  # Duplicado
]

banco_data = [
    {"Factura": "F001", "Fecha": "2025-07-01", "Monto": 100.00},
    {"Factura": "F002", "Fecha": "2025-07-02", "Monto": 205.00},  # Diferencia
    {"Factura": "F003", "Fecha": "2025-07-03", "Monto": 150.00},
    {"Factura": "F006", "Fecha": "2025-07-06", "Monto": 120.00},
    {"Factura": "F005", "Fecha": "2025-07-05", "Monto": 300.00},
]

# Cargar en DataFrames
df_erp = pd.DataFrame(erp_data)
df_banco = pd.DataFrame(banco_data)

# Convertir fechas
df_erp['Fecha'] = pd.to_datetime(df_erp['Fecha'])
df_banco['Fecha'] = pd.to_datetime(df_banco['Fecha'])

# Mostrar datos
st.subheader("📂 Datos cargados")
col1, col2 = st.columns(2)
with col1:
    st.write("**Sistema ERP**")
    st.dataframe(df_erp)
with col2:
    st.write("**Sistema Banco**")
    st.dataframe(df_banco)

# Selección de pruebas a ejecutar
st.subheader("⚙️ Selecciona las pruebas a ejecutar")
ejecutar_exactos = st.checkbox("Coincidencias Exactas", value=True)
ejecutar_faltantes = st.checkbox("Facturas faltantes en alguno de los sistemas", value=True)
ejecutar_diferencias = st.checkbox("Diferencias en monto o fecha", value=True)
ejecutar_duplicados = st.checkbox("Facturas duplicadas", value=True)

# Resultados
st.subheader("📌 Resultados del Análisis")

# Coincidencias exactas
if ejecutar_exactos:
    exactos = pd.merge(df_erp, df_banco, on=['Factura', 'Monto', 'Fecha'])
    st.success(f"Coincidencias exactas encontradas: {len(exactos)}")
    st.dataframe(exactos)

# Faltantes
if ejecutar_faltantes:
    faltantes = df_erp[~df_erp['Factura'].isin(df_banco['Factura'])]
    sobrantes = df_banco[~df_banco['Factura'].isin(df_erp['Factura'])]
    st.warning(f"Facturas solo en ERP: {len(faltantes)}")
    st.dataframe(faltantes)
    st.warning(f"Facturas solo en Banco: {len(sobrantes)}")
    st.dataframe(sobrantes)

# Diferencias
if ejecutar_diferencias:
    df_merge = pd.merge(df_erp, df_banco, on='Factura', suffixes=('_erp', '_banco'))
    diferencias = df_merge[(df_merge['Monto_erp'] != df_merge['Monto_banco']) |
                           (df_merge['Fecha_erp'] != df_merge['Fecha_banco'])]
    st.error(f"Facturas con diferencias: {len(diferencias)}")
    st.dataframe(diferencias)

# Duplicados
if ejecutar_duplicados:
    duplicados = df_erp[df_erp.duplicated(['Factura', 'Monto', 'Fecha'], keep=False)]
    st.warning(f"Facturas duplicadas en ERP: {len(duplicados)}")
    st.dataframe(duplicados)

# Métricas de resumen
st.subheader("📊 Métricas Generales")
total_facturas_erp = len(df_erp)
total_facturas_banco = len(df_banco)
coincidencias = len(exactos) if ejecutar_exactos else 0
errores = len(diferencias) if ejecutar_diferencias else 0
no_encontradas = len(faltantes) + len(sobrantes) if ejecutar_faltantes else 0

st.metric("Facturas en ERP", total_facturas_erp)
st.metric("Facturas en Banco", total_facturas_banco)
st.metric("Coincidencias", coincidencias)
st.metric("Errores", errores)
st.metric("No Encontradas", no_encontradas)

# Exportar reporte Excel
st.subheader("📥 Generar Reporte Corporativo")
output = io.BytesIO()
with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
    df_erp.to_excel(writer, sheet_name='ERP', index=False)
    df_banco.to_excel(writer, sheet_name='Banco', index=False)
    if ejecutar_exactos:
        exactos.to_excel(writer, sheet_name='Coincidencias', index=False)
    if ejecutar_faltantes:
        faltantes.to_excel(writer, sheet_name='Solo en ERP', index=False)
        sobrantes.to_excel(writer, sheet_name='Solo en Banco', index=False)
    if ejecutar_diferencias:
        diferencias.to_excel(writer, sheet_name='Diferencias', index=False)
    if ejecutar_duplicados:
        duplicados.to_excel(writer, sheet_name='Duplicados', index=False)

    resumen = pd.DataFrame({
        'Indicador': ['Total ERP', 'Total Banco', 'Coincidencias', 'Errores', 'No Encontradas'],
        'Valor': [total_facturas_erp, total_facturas_banco, coincidencias, errores, no_encontradas]
    })
    resumen.to_excel(writer, sheet_name='Resumen', index=False)

st.download_button(
    label="📊 Descargar Reporte en Excel",
    data=output.getvalue(),
    file_name=f"reporte_auditoria_{datetime.today().date()}.xlsx",
    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
)

# Pie de página
st.markdown("---")
st.markdown("Aplicación desarrollada como parte del proyecto de Auditoría CAAT - Semana 3-5")
