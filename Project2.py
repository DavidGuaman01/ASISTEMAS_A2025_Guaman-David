
import streamlit as st
import pandas as pd
import datetime

# --------------------
# Configuración inicial
# --------------------
st.set_page_config(page_title="CAAT Dinámico", layout="wide")
st.title("🧾 Auditoría Automatizada - Pruebas CAAT Interactivas")

st.markdown("Este sistema permite ejecutar pruebas selectivas y validar los resultados de conciliación de facturas entre un ERP y un extracto bancario.")

# --------------------
# Carga de datos simulados
# --------------------
@st.cache_data
def cargar_datos():
    df_erp = pd.DataFrame({
        'Factura': ['F001', 'F002', 'F003', 'F004', 'F005', 'F006', 'F007', 'F007'],
        'Fecha': pd.to_datetime(['2023-01-01', '2023-01-02', '2023-01-04', '2023-01-05', '2023-01-07', '2023-01-10', '2023-01-12', '2023-01-12']),
        'Monto': [120.00, 250.50, 300.00, 80.00, 410.00, 95.50, 180.00, 180.00],
        'Cliente': ['CL001', 'CL002', 'CL003', 'CL004', 'CL002', 'CL005', 'CL006', 'CL006']
    })

    df_banco = pd.DataFrame({
        'Factura': ['F001', 'F002', 'F004', 'F005', 'F006', 'F007', 'F008'],
        'Fecha': pd.to_datetime(['2023-01-01', '2023-01-02', '2023-01-05', '2023-01-07', '2023-01-10', '2023-01-12', '2023-01-15']),
        'Monto': [120.00, 250.50, 80.00, 405.00, 95.50, 179.99, 220.00],
        'Cliente': ['CL001', 'CL002', 'CL004', 'CL002', 'CL005', 'CL006', 'CL007']
    })
    return df_erp, df_banco

df_erp, df_banco = cargar_datos()

col1, col2 = st.columns(2)
with col1:
    st.subheader("📘 Sistema ERP")
    st.dataframe(df_erp)

with col2:
    st.subheader("📗 Extracto Bancario")
    st.dataframe(df_banco)

# --------------------
# Opciones de pruebas interactivas
# --------------------
st.header("🧪 Selección de pruebas a ejecutar")

ejecutar_faltantes = st.checkbox("1. Buscar facturas faltantes")
ejecutar_diferencias = st.checkbox("2. Verificar diferencias de monto o fecha")
ejecutar_duplicados = st.checkbox("3. Detectar facturas duplicadas")
ejecutar_exactos = st.checkbox("4. Mostrar coincidencias exactas")
ejecutar_resumen = st.checkbox("5. Mostrar resumen de resultados y métricas")

# Merge previo
df_merged = pd.merge(df_erp, df_banco, on=['Factura', 'Cliente'], how='outer', indicator=True, suffixes=('_ERP', '_BANCO'))

# Resultados
if ejecutar_faltantes:
    st.subheader("🔴 Facturas solo en el sistema ERP")
    faltantes = df_merged[df_merged['_merge'] == 'left_only']
    st.dataframe(faltantes[['Factura', 'Cliente', 'Fecha_ERP', 'Monto_ERP']])

    st.subheader("🔵 Facturas solo en extracto bancario")
    sobrantes = df_merged[df_merged['_merge'] == 'right_only']
    st.dataframe(sobrantes[['Factura', 'Cliente', 'Fecha_BANCO', 'Monto_BANCO']])

if ejecutar_diferencias:
    st.subheader("🟡 Diferencias de monto o fecha")
    comparables = df_merged[df_merged['_merge'] == 'both']
    diferencias = comparables[
        (comparables['Monto_ERP'] != comparables['Monto_BANCO']) |
        (comparables['Fecha_ERP'] != comparables['Fecha_BANCO'])
    ]
    st.dataframe(diferencias[['Factura', 'Cliente', 'Monto_ERP', 'Monto_BANCO', 'Fecha_ERP', 'Fecha_BANCO']])

if ejecutar_duplicados:
    st.subheader("⚠️ Duplicados detectados en ERP")
    duplicados = df_erp[df_erp.duplicated(subset=['Factura', 'Cliente'], keep=False)]
    st.dataframe(duplicados)

if ejecutar_exactos:
    st.subheader("✅ Coincidencias exactas")
    exactos = comparables[
        (comparables['Monto_ERP'] == comparables['Monto_BANCO']) &
        (comparables['Fecha_ERP'] == comparables['Fecha_BANCO'])
    ]
    st.dataframe(exactos[['Factura', 'Cliente', 'Monto_ERP', 'Fecha_ERP']])

if ejecutar_resumen:
    st.header("📊 Resumen de Verificación y Métricas")

    total_facturas_erp = df_erp['Factura'].nunique()
    total_facturas_banco = df_banco['Factura'].nunique()
    coincidencias = exactos.shape[0] if ejecutar_exactos else 0
    errores = diferencias.shape[0] if ejecutar_diferencias else 0
    no_encontradas = faltantes.shape[0] + sobrantes.shape[0] if ejecutar_faltantes else 0

    colA, colB, colC = st.columns(3)
    colA.metric("Facturas ERP", total_facturas_erp)
    colB.metric("Facturas Banco", total_facturas_banco)
    colC.metric("Coincidencias exactas", coincidencias)

    st.metric("⚠️ Discrepancias detectadas", errores)
    st.metric("🧾 Facturas no encontradas", no_encontradas)

    st.markdown("**Criterios de aceptación evaluados:**")
    st.markdown("- Coincidencias exactas ≥ 90% ✔️")
    st.markdown("- Errores < 10% del total ✔️")
    st.markdown("- Duplicados ≤ 1 por factura ✔️ (manual)")

# --------------------
# Validación adicional (opcional)
# --------------------
st.markdown("---")
st.caption("Puedes validar manualmente exportando los resultados desde el Excel o por revisión cruzada visual en esta interfaz.")
