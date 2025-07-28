import streamlit as st
import pandas as pd
import datetime
import logging

# -------------------
# CONFIGURACIÓN INICIAL
# -------------------
st.set_page_config(page_title="CAAT - Conciliación de Facturas", layout="wide")
st.title("🧾 Herramienta CAAT - Conciliación de Facturas entre Sistemas")

# Configuración de logs
logging.basicConfig(filename='logs_caat.txt', level=logging.INFO,
                    format='%(asctime)s - %(levelname)s - %(message)s')

st.markdown("""
Esta herramienta implementa **pruebas CAAT (Computer-Assisted Audit Techniques)** con datos simulados de facturación para comparar registros entre un sistema fuente (ERP) y un sistema destino (extracto bancario).
""")

# ---------------------
# DATOS SIMULADOS - SEMANA 3
# ---------------------

st.header("📥 Datos de entrada (simulados)")

# Simulación de datos con campos clave: número de factura, monto, fecha
df_source = pd.DataFrame({
    'Factura': ['F001', 'F002', 'F003', 'F004', 'F005', 'F006', 'F007', 'F007'],
    'Fecha': pd.to_datetime(['2023-01-01', '2023-01-02', '2023-01-04', '2023-01-05', '2023-01-07', '2023-01-10', '2023-01-12', '2023-01-12']),
    'Monto': [120.00, 250.50, 300.00, 80.00, 410.00, 95.50, 180.00, 180.00],
    'Cliente': ['CL001', 'CL002', 'CL003', 'CL004', 'CL002', 'CL005', 'CL006', 'CL006']
})

df_target = pd.DataFrame({
    'Factura': ['F001', 'F002', 'F004', 'F005', 'F006', 'F007', 'F008'],
    'Fecha': pd.to_datetime(['2023-01-01', '2023-01-02', '2023-01-05', '2023-01-07', '2023-01-10', '2023-01-12', '2023-01-15']),
    'Monto': [120.00, 250.50, 80.00, 405.00, 95.50, 179.99, 220.00],
    'Cliente': ['CL001', 'CL002', 'CL004', 'CL002', 'CL005', 'CL006', 'CL007']
})

st.subheader("Sistema fuente (ERP)")
st.dataframe(df_source)

st.subheader("Sistema destino (Extracto bancario)")
st.dataframe(df_target)

# ---------------------
# PROCESAMIENTO Y PRUEBAS
# ---------------------

st.header("🧪 Pruebas CAAT y Conciliación")

df_merged = pd.merge(df_source, df_target, on=['Factura', 'Cliente'], how='outer', indicator=True, suffixes=('_source', '_target'))

# 1. Facturas solo en sistema fuente
solo_fuente = df_merged[df_merged['_merge'] == 'left_only']
st.subheader("🔴 Facturas solo en el sistema fuente (ERP)")
st.dataframe(solo_fuente[['Factura', 'Cliente', 'Fecha_source', 'Monto_source']])

# 2. Facturas solo en sistema destino
solo_destino = df_merged[df_merged['_merge'] == 'right_only']
st.subheader("🔵 Facturas solo en el sistema destino (banco)")
st.dataframe(solo_destino[['Factura', 'Cliente', 'Fecha_target', 'Monto_target']])

# 3. Diferencias de monto o fecha
diferencias = df_merged[df_merged['_merge'] == 'both'].copy()
discrepancias = diferencias[
    (diferencias['Monto_source'] != diferencias['Monto_target']) |
    (diferencias['Fecha_source'] != diferencias['Fecha_target'])
]
st.subheader("🟡 Discrepancias por monto o fecha")
st.dataframe(discrepancias[['Factura', 'Cliente', 'Monto_source', 'Monto_target', 'Fecha_source', 'Fecha_target']])

# 4. Coincidencias exactas
coinciden = diferencias[
    (diferencias['Monto_source'] == diferencias['Monto_target']) &
    (diferencias['Fecha_source'] == diferencias['Fecha_target'])
]
st.subheader("✅ Coincidencias exactas")
st.dataframe(coinciden[['Factura', 'Cliente', 'Monto_source', 'Fecha_source']])

# 5. Duplicados en el sistema fuente
duplicados = df_source[df_source.duplicated(subset=['Factura', 'Cliente'], keep=False)]
st.subheader("⚠️ Duplicados en el sistema fuente")
st.dataframe(duplicados)

# ---------------------
# VERIFICACIÓN - SEMANA 4
# ---------------------

st.header("🔍 Verificación de funcionamiento")

st.markdown("""
**Escenarios de prueba incluidos:**

- Factura faltante en uno u otro sistema
- Montos distintos
- Fechas desalineadas
- Duplicados

**Criterios de aceptación:**
- Identificación correcta de discrepancias
- Tasa de falsos positivos = 0
- Visualización clara por tipo de hallazgo

**Validación manual posible:** puedes descargar los resultados abajo y revisarlos en Excel.
""")

# ---------------------
# EXPORTACIÓN - SEMANA 5
# ---------------------

st.header("📤 Exportar reportes")

if st.button("📥 Descargar discrepancias como Excel"):
    report = pd.ExcelWriter("reporte_conciliacion.xlsx", engine='xlsxwriter')
    solo_fuente.to_excel(report, sheet_name='Solo en ERP', index=False)
    solo_destino.to_excel(report, sheet_name='Solo en Banco', index=False)
    discrepancias.to_excel(report, sheet_name='Diferencias', index=False)
    duplicados.to_excel(report, sheet_name='Duplicados', index=False)
    report.close()
    st.success("Reporte 'reporte_conciliacion.xlsx' generado con éxito. (Busca en tu carpeta actual)")

# ---------------------
# LOG FINAL
# ---------------------
logging.info("Aplicación ejecutada exitosamente - %s registros fuente, %s destino", len(df_source), len(df_target))
st.success("✅ Pruebas finalizadas con éxito.")