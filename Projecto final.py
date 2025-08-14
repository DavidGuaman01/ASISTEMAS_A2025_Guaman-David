import streamlit as st
import pandas as pd

st.set_page_config(page_title="CAAT - Conciliación Financiera", layout="wide")

st.title("📊 CAAT - Conciliación de Reportes Financieros")

opcion = st.sidebar.selectbox(
    "Selecciona la prueba CAAT que deseas ejecutar",
    [
        "1. Transacciones Conciliadas Completas",
        "2. Faltantes en el Destino (Solo en Origen)",
        "3. Inesperadas en el Destino (Solo en Destino)",
        "4. Discrepancias por ID (Monto/Fecha)",
        "5. Duplicados Internos"
    ]
)

# Cargar archivo (xlsx o csv)
def load_data(file):
    if file.name.endswith(".csv"):
        return pd.read_csv(file)
    return pd.read_excel(file, engine="openpyxl")

# Comparación con dos archivos
if opcion != "5. Duplicados Internos":
    file_origen = st.file_uploader("📂 Archivo de Origen", type=["xlsx", "csv"], key="origen")
    file_destino = st.file_uploader("📁 Archivo de Destino", type=["xlsx", "csv"], key="destino")
else:
    file_data = st.file_uploader("📥 Archivo a Analizar (Origen o Destino)", type=["xlsx", "csv"], key="uno")

# Campos clave
campos_clave = ["ID_Transaccion", "Fecha", "Monto", "ID_Entidad"]
campos_id = ["ID_Transaccion", "ID_Entidad"]

# Funcionalidades por prueba
if opcion == "1. Transacciones Conciliadas Completas" and file_origen and file_destino:
    df_origen = load_data(file_origen)
    df_destino = load_data(file_destino)
    df_origen["Fecha"] = pd.to_datetime(df_origen["Fecha"])
    df_destino["Fecha"] = pd.to_datetime(df_destino["Fecha"])

    conciliadas = pd.merge(df_origen, df_destino, how="inner", on=campos_clave)
    st.success(f"✅ {len(conciliadas)} transacciones completamente conciliadas.")
    st.dataframe(conciliadas, use_container_width=True)

    st.download_button("⬇ Descargar", conciliadas.to_csv(index=False).encode(), "conciliadas.csv", "text/csv")

elif opcion == "2. Faltantes en el Destino (Solo en Origen)" and file_origen and file_destino:
    df_origen = load_data(file_origen)
    df_destino = load_data(file_destino)
    df_origen["Fecha"] = pd.to_datetime(df_origen["Fecha"])
    df_destino["Fecha"] = pd.to_datetime(df_destino["Fecha"])

    merge = pd.merge(df_origen, df_destino, how="left", on=campos_clave, indicator=True)
    solo_origen = merge[merge["_merge"] == "left_only"].drop(columns="_merge")
    st.warning(f"❗ {len(solo_origen)} transacciones solo en el origen.")
    st.dataframe(solo_origen, use_container_width=True)

    st.download_button("⬇ Descargar", solo_origen.to_csv(index=False).encode(), "solo_origen.csv", "text/csv")

elif opcion == "3. Inesperadas en el Destino (Solo en Destino)" and file_origen and file_destino:
    df_origen = load_data(file_origen)
    df_destino = load_data(file_destino)
    df_origen["Fecha"] = pd.to_datetime(df_origen["Fecha"])
    df_destino["Fecha"] = pd.to_datetime(df_destino["Fecha"])

    merge = pd.merge(df_destino, df_origen, how="left", on=campos_clave, indicator=True)
    solo_destino = merge[merge["_merge"] == "left_only"].drop(columns="_merge")
    st.warning(f"🚨 {len(solo_destino)} transacciones inesperadas solo en el destino.")
    st.dataframe(solo_destino, use_container_width=True)

    st.download_button("⬇ Descargar", solo_destino.to_csv(index=False).encode(), "solo_destino.csv", "text/csv")

elif opcion == "4. Discrepancias por ID (Monto/Fecha)" and file_origen and file_destino:
    df_origen = load_data(file_origen)
    df_destino = load_data(file_destino)
    df_origen["Fecha"] = pd.to_datetime(df_origen["Fecha"])
    df_destino["Fecha"] = pd.to_datetime(df_destino["Fecha"])

    merged = pd.merge(df_origen, df_destino, on=campos_id, how="inner", suffixes=("_origen", "_destino"))
    discrepancias = merged[
        (merged["Monto_origen"] != merged["Monto_destino"]) |
        (merged["Fecha_origen"] != merged["Fecha_destino"])
    ]
    st.warning(f"⚠️ {len(discrepancias)} discrepancias encontradas en Monto o Fecha.")
    st.dataframe(discrepancias, use_container_width=True)

    st.download_button("⬇ Descargar", discrepancias.to_csv(index=False).encode(), "discrepancias.csv", "text/csv")

elif opcion == "5. Duplicados Internos" and file_data:
    df = load_data(file_data)
    df["Fecha"] = pd.to_datetime(df["Fecha"])
    duplicados = df[df.duplicated(subset=campos_clave, keep=False)]
    st.warning(f"🔁 {len(duplicados)} transacciones duplicadas internas encontradas.")
    st.dataframe(duplicados, use_container_width=True)

    st.download_button("⬇ Descargar", duplicados.to_csv(index=False).encode(), "duplicados.csv", "text/csv")
