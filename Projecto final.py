import streamlit as st
import pandas as pd
import io

# -------------------------
# Configuración inicial
# -------------------------
st.set_page_config(page_title="CAAT Dinámico", layout="wide")
st.title("📤 Auditoría Automatizada - Comparación de Archivos (ERP vs Banco)")

st.markdown("Carga tus archivos de ERP y Banco (Excel o CSV) para ejecutar pruebas automatizadas de conciliación de facturas.")

# -------------------------
# Carga de archivos del usuario
# -------------------------
st.sidebar.header("📁 Subir Archivos de Datos")

archivo_erp = st.sidebar.file_uploader("Sube archivo ERP", type=["csv", "xlsx", "xls"])
archivo_banco = st.sidebar.file_uploader("Sube archivo Banco", type=["csv", "xlsx", "xls"])

@st.cache_data
def leer_archivo(file):
    if file.name.endswith('.csv'):
        return pd.read_csv(file)
    elif file.name.endswith(('.xlsx', '.xls')):
        return pd.read_excel(file)
    else:
        return None

# Ejecutar solo si hay archivos cargados
if archivo_erp and archivo_banco:
    df_erp = leer_archivo(archivo_erp)
    df_banco = leer_archivo(archivo_banco)

    # Validación mínima de columnas
    columnas_requeridas = {'Factura', 'Fecha', 'Monto', 'Cliente'}
    if not columnas_requeridas.issubset(df_erp.columns) or not columnas_requeridas.issubset(df_banco.columns):
        st.error(f"❌ Ambos archivos deben contener las columnas: {columnas_requeridas}")
        st.stop()

    # Conversión segura de fecha solo si es necesario
    if df_erp['Fecha'].dtype == object:
        df_erp['Fecha'] = pd.to_datetime(df_erp['Fecha'], errors='coerce')
    if df_banco['Fecha'].dtype == object:
        df_banco['Fecha'] = pd.to_datetime(df_banco['Fecha'], errors='coerce')

    # Mostrar tablas
    col1, col2 = st.columns(2)
    with col1:
        st.subheader("📘 Sistema ERP")
        st.dataframe(df_erp, use_container_width=True)
    with col2:
        st.subheader("📗 Extracto Bancario")
        st.dataframe(df_banco, use_container_width=True)

    # Merge principal (solo una vez)
    df_merged = pd.merge(df_erp, df_banco, on=['Factura', 'Cliente'], how='outer', indicator=True, suffixes=('_ERP', '_BANCO'))
    comparables = df_merged[df_merged['_merge'] == 'both']

    # Checkboxes
    st.header("🧪 Selección de pruebas a ejecutar")

    ejecutar_faltantes = st.checkbox("1. Buscar facturas faltantes")
    ejecutar_diferencias = st.checkbox("2. Verificar diferencias de monto o fecha")
    ejecutar_duplicados = st.checkbox("3. Detectar facturas duplicadas")
    ejecutar_exactos = st.checkbox("4. Mostrar coincidencias exactas")
    ejecutar_resumen = st.checkbox("5. Mostrar resumen de resultados y métricas")

    # -------------------
    # Resultados
    # -------------------
    if ejecutar_faltantes:
        st.subheader("🔴 Facturas solo en el sistema ERP")
        faltantes = df_merged[df_merged['_merge'] == 'left_only']
        st.dataframe(faltantes[['Factura', 'Cliente', 'Fecha_ERP', 'Monto_ERP']], use_container_width=True)

        st.subheader("🔵 Facturas solo en extracto bancario")
        sobrantes = df_merged[df_merged['_merge'] == 'right_only']
        st.dataframe(sobrantes[['Factura', 'Cliente', 'Fecha_BANCO', 'Monto_BANCO']], use_container_width=True)
    else:
        faltantes = sobrantes = pd.DataFrame()

    if ejecutar_diferencias:
        st.subheader("🟡 Diferencias de monto o fecha")
        diferencias = comparables[
            (comparables['Monto_ERP'] != comparables['Monto_BANCO']) |
            (comparables['Fecha_ERP'] != comparables['Fecha_BANCO'])
        ]
        st.dataframe(diferencias[['Factura', 'Cliente', 'Monto_ERP', 'Monto_BANCO', 'Fecha_ERP', 'Fecha_BANCO']], use_container_width=True)
    else:
        diferencias = pd.DataFrame()

    if ejecutar_duplicados:
        st.subheader("⚠️ Duplicados detectados en ERP")
        duplicados = df_erp[df_erp.duplicated(subset=['Factura', 'Cliente'], keep=False)]
        st.dataframe(duplicados, use_container_width=True)
    else:
        duplicados = pd.DataFrame()

    if ejecutar_exactos:
        st.subheader("✅ Coincidencias exactas")
        exactos = comparables[
            (comparables['Monto_ERP'] == comparables['Monto_BANCO']) &
            (comparables['Fecha_ERP'] == comparables['Fecha_BANCO'])
        ]
        st.dataframe(exactos[['Factura', 'Cliente', 'Monto_ERP', 'Fecha_ERP']], use_container_width=True)
    else:
        exactos = pd.DataFrame()

    if ejecutar_resumen:
        st.header("📊 Resumen de Verificación y Métricas")
        total_facturas_erp = df_erp['Factura'].nunique()
        total_facturas_banco = df_banco['Factura'].nunique()
        coincidencias = exactos.shape[0]
        errores = diferencias.shape[0]
        no_encontradas = faltantes.shape[0] + sobrantes.shape[0]

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

    # Exportar Excel
    st.markdown("---")
    st.header("📁 Exportar Reporte Corporativo")

    if st.button("📥 Generar y Descargar Reporte Excel"):
        output = io.BytesIO()
        with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
            df_erp.to_excel(writer, index=False, sheet_name='ERP')
            df_banco.to_excel(writer, index=False, sheet_name='Banco')

            if not faltantes.empty:
                faltantes.to_excel(writer, index=False, sheet_name='Solo en ERP')
            if not sobrantes.empty:
                sobrantes.to_excel(writer, index=False, sheet_name='Solo en Banco')
            if not diferencias.empty:
                diferencias.to_excel(writer, index=False, sheet_name='Diferencias')
            if not duplicados.empty:
                duplicados.to_excel(writer, index=False, sheet_name='Duplicados ERP')
            if not exactos.empty:
                exactos.to_excel(writer, index=False, sheet_name='Coincidencias Exactas')

            resumen = pd.DataFrame({
                'Métrica': ['Facturas ERP', 'Facturas Banco', 'Coincidencias exactas', 'Discrepancias detectadas', 'Facturas no encontradas'],
                'Valor': [total_facturas_erp, total_facturas_banco, coincidencias, errores, no_encontradas]
            })
            resumen.to_excel(writer, index=False, sheet_name='Resumen')

        st.download_button(
            label="📄 Descargar Reporte Excel",
            data=output.getvalue(),
            file_name="Reporte_Auditoria_Caat.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )

else:
    st.warning("⬅️ Por favor, sube ambos archivos para comenzar.")
