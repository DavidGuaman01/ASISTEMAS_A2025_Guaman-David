import streamlit as st
import pandas as pd
from io import BytesIO

st.set_page_config(page_title="Conciliación CAAT", layout="wide")

st.title("🧾 Conciliación de Reportes Financieros - CAAT")

st.write("Sube los archivos de Origen y Destino (formato Excel o CSV) para iniciar la conciliación.")

file1 = st.file_uploader("📁 Archivo de Origen", type=["csv", "xlsx"], key="origen")
file2 = st.file_uploader("📂 Archivo de Destino", type=["csv", "xlsx"], key="destino")

def load_data(file):
    if file.name.endswith(".csv"):
        return pd.read_csv(file)
    else:
        return pd.read_excel(file)

if file1 and file2:
    df_source = load_data(file1)
    df_target = load_data(file2)

    st.success("Datos cargados correctamente.")

    # Estandarización
    df_source['Fecha'] = pd.to_datetime(df_source['Fecha'])
    df_target['Fecha'] = pd.to_datetime(df_target['Fecha'])

    merge_keys = ["ID_Transaccion", "ID_Entidad"]
    df_merged = pd.merge(df_source, df_target, on=merge_keys, how="outer", indicator=True, suffixes=('_origen', '_destino'))

    # 1. Transacciones solo en Origen
    only_source = df_merged[df_merged['_merge'] == 'left_only']

    # 2. Transacciones solo en Destino
    only_target = df_merged[df_merged['_merge'] == 'right_only']

    # 3. Transacciones en ambos pero con discrepancias en Fecha o Monto
    both = df_merged[df_merged['_merge'] == 'both']
    discrepancias = both[
        (both['Monto_origen'] != both['Monto_destino']) |
        (both['Fecha_origen'] != both['Fecha_destino'])
    ]

    # 4. Perfectamente conciliadas
    perfect = both[
        (both['Monto_origen'] == both['Monto_destino']) &
        (both['Fecha_origen'] == both['Fecha_destino'])
    ]

    # 5. Duplicados
    duplicates_source = df_source[df_source.duplicated(subset=merge_keys, keep=False)]
    duplicates_target = df_target[df_target.duplicated(subset=merge_keys, keep=False)]

    # Resultados
    st.subheader("📌 Resumen General")
    st.write(f"- Transacciones solo en Origen: {len(only_source)}")
    st.write(f"- Transacciones solo en Destino: {len(only_target)}")
    st.write(f"- Discrepancias en Monto o Fecha: {len(discrepancias)}")
    st.write(f"- Conciliadas completamente: {len(perfect)}")
    st.write(f"- Duplicados en Origen: {len(duplicates_source)}")
    st.write(f"- Duplicados en Destino: {len(duplicates_target)}")

    # Tablas interactivas
    def show_df(name, df):
        st.markdown(f"### 📊 {name}")
        st.dataframe(df, use_container_width=True)
        to_excel = BytesIO()
        df.to_excel(to_excel, index=False)
        to_excel.seek(0)
        st.download_button("⬇ Descargar", to_excel, file_name=f"{name}.xlsx")

    show_df("Solo en Origen", only_source)
    show_df("Solo en Destino", only_target)
    show_df("Discrepancias", discrepancias)
    show_df("Conciliadas", perfect)
    show_df("Duplicados en Origen", duplicates_source)
    show_df("Duplicados en Destino", duplicates_target)
