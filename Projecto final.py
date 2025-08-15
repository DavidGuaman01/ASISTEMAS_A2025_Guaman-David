import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

st.set_page_config(page_title="CAAT - Conciliación Financiera", layout="wide")
st.title("📊 CAAT - Conciliación de Reportes Financieros")

PRUEBAS = [
    "1. Transacciones Conciliadas Completas",
    "2. Faltantes en el Destino (Solo en Origen)",
    "3. Inesperadas en el Destino (Solo en Destino)",
    "4. Discrepancias por ID (Monto/Fecha)",
    "5. Duplicados Internos"
]
CAMPOS_CLAVE = ["ID_Transaccion", "Fecha", "Monto", "ID_Entidad"]
CAMPOS_ID = ["ID_Transaccion", "ID_Entidad"]

def validar_columnas(df, nombre, requeridas):
    faltantes = [col for col in requeridas if col not in df.columns]
    if faltantes:
        st.error(f"❌ El archivo '{nombre}' no contiene las columnas necesarias: {', '.join(faltantes)}")
        return False
    return True

def load_data(file):
    if file.name.endswith(".csv"):
        return pd.read_csv(file)
    return pd.read_excel(file, engine="openpyxl")

def generar_conclusion_conteo(conteo):
    conclusion = "🔍 **Conclusión General del Análisis**\n\n"
    conclusion += "Durante el proceso de conciliación se identificaron los siguientes hallazgos:\n\n"
    if conteo["Faltantes en destino"] > 0:
        conclusion += f"- Se detectaron **{conteo['Faltantes en destino']} transacciones** ausentes en el destino.\n"
    if conteo["Inesperadas en destino"] > 0:
        conclusion += f"- Se encontraron **{conteo['Inesperadas en destino']} transacciones inesperadas** en el destino.\n"
    if conteo["Discrepancias de valor"] > 0:
        conclusion += f"- Existen **{conteo['Discrepancias de valor']} registros** con discrepancias en monto o fecha.\n"
    if conteo["Duplicados"] > 0:
        conclusion += f"- Se identificaron **{conteo['Duplicados']} registros duplicados**.\n"
    if all(conteo[k] == 0 for k in ["Faltantes en destino", "Inesperadas en destino", "Discrepancias de valor", "Duplicados"]):
        conclusion += "- No se detectaron anomalías significativas. El sistema de origen y destino están debidamente conciliados.\n"
    conclusion += "\nSe recomienda revisar los hallazgos y priorizar los casos con mayor impacto."
    return conclusion

def generar_recomendacion(nombre, cantidad, umbral, mensaje_ok, mensaje_alerta):
    if cantidad > umbral:
        return f"🔴 Riesgo alto en **{nombre}**: {mensaje_alerta}"
    elif cantidad > 0:
        return f"🟡 Atención en **{nombre}**: {mensaje_alerta}"
    else:
        return f"🟢 **{nombre}** en buen estado: {mensaje_ok}"

# UI principal
opcion = st.sidebar.selectbox("Selecciona la prueba CAAT que deseas ejecutar", PRUEBAS)

if opcion != PRUEBAS[4]:
    file_origen = st.file_uploader("📂 Archivo de Origen", type=["xlsx", "csv"], key="origen")
    file_destino = st.file_uploader("📁 Archivo de Destino", type=["xlsx", "csv"], key="destino")
else:
    file_data = st.file_uploader("📥 Archivo a Analizar", type=["xlsx", "csv"], key="uno")

conteo_resultados = {
    "Conciliadas": 0,
    "Faltantes en destino": 0,
    "Inesperadas en destino": 0,
    "Discrepancias de valor": 0,
    "Duplicados": 0
}

if opcion == PRUEBAS[0] and file_origen and file_destino:
    df1, df2 = load_data(file_origen), load_data(file_destino)
    if validar_columnas(df1, "origen", CAMPOS_CLAVE) and validar_columnas(df2, "destino", CAMPOS_CLAVE):
        df1["Fecha"] = pd.to_datetime(df1["Fecha"])
        df2["Fecha"] = pd.to_datetime(df2["Fecha"])
        conciliadas = pd.merge(df1, df2, how="inner", on=CAMPOS_CLAVE)
        conteo_resultados["Conciliadas"] = len(conciliadas)
        st.success(f"✅ {len(conciliadas)} transacciones conciliadas.")
        st.dataframe(conciliadas)
        st.download_button("⬇ Descargar", conciliadas.to_csv(index=False).encode(), "conciliadas.csv", "text/csv")

elif opcion == PRUEBAS[1] and file_origen and file_destino:
    df1, df2 = load_data(file_origen), load_data(file_destino)
    if validar_columnas(df1, "origen", CAMPOS_CLAVE) and validar_columnas(df2, "destino", CAMPOS_CLAVE):
        df1["Fecha"] = pd.to_datetime(df1["Fecha"])
        df2["Fecha"] = pd.to_datetime(df2["Fecha"])
        merge = pd.merge(df1, df2, how="left", on=CAMPOS_CLAVE, indicator=True)
        solo_origen = merge[merge["_merge"] == "left_only"].drop(columns="_merge")
        conteo_resultados["Faltantes en destino"] = len(solo_origen)
        st.warning(f"❗ {len(solo_origen)} transacciones solo en el origen.")
        st.dataframe(solo_origen)
        st.download_button("⬇ Descargar", solo_origen.to_csv(index=False).encode(), "solo_origen.csv", "text/csv")

elif opcion == PRUEBAS[2] and file_origen and file_destino:
    df1, df2 = load_data(file_origen), load_data(file_destino)
    if validar_columnas(df1, "origen", CAMPOS_CLAVE) and validar_columnas(df2, "destino", CAMPOS_CLAVE):
        df1["Fecha"] = pd.to_datetime(df1["Fecha"])
        df2["Fecha"] = pd.to_datetime(df2["Fecha"])
        merge = pd.merge(df2, df1, how="left", on=CAMPOS_CLAVE, indicator=True)
        solo_destino = merge[merge["_merge"] == "left_only"].drop(columns="_merge")
        conteo_resultados["Inesperadas en destino"] = len(solo_destino)
        st.warning(f"🚨 {len(solo_destino)} transacciones inesperadas en el destino.")
        st.dataframe(solo_destino)
        st.download_button("⬇ Descargar", solo_destino.to_csv(index=False).encode(), "solo_destino.csv", "text/csv")

elif opcion == PRUEBAS[3] and file_origen and file_destino:
    df1, df2 = load_data(file_origen), load_data(file_destino)
    if validar_columnas(df1, "origen", CAMPOS_CLAVE) and validar_columnas(df2, "destino", CAMPOS_CLAVE):
        df1["Fecha"] = pd.to_datetime(df1["Fecha"])
        df2["Fecha"] = pd.to_datetime(df2["Fecha"])
        merged = pd.merge(df1, df2, on=CAMPOS_ID, how="inner", suffixes=("_origen", "_destino"))
        discrepancias = merged[
            (merged["Monto_origen"] != merged["Monto_destino"]) |
            (merged["Fecha_origen"] != merged["Fecha_destino"])
        ]
        conteo_resultados["Discrepancias de valor"] = len(discrepancias)
        st.warning(f"⚠️ {len(discrepancias)} discrepancias encontradas.")
        st.dataframe(discrepancias)
        st.download_button("⬇ Descargar", discrepancias.to_csv(index=False).encode(), "discrepancias.csv", "text/csv")

elif opcion == PRUEBAS[4] and file_data:
    df = load_data(file_data)
    if validar_columnas(df, "archivo único", CAMPOS_CLAVE):
        df["Fecha"] = pd.to_datetime(df["Fecha"])
        duplicados = df[df.duplicated(subset=CAMPOS_CLAVE, keep=False)]
        conteo_resultados["Duplicados"] = len(duplicados)
        st.warning(f"🔁 {len(duplicados)} duplicados encontrados.")
        st.dataframe(duplicados)
        st.download_button("⬇ Descargar", duplicados.to_csv(index=False).encode(), "duplicados.csv", "text/csv")

# Mostrar resumen si se cargaron datos y hay resultados
if sum(conteo_resultados.values()) > 0:
    st.subheader("📊 Resumen gráfico de pruebas CAAT")
    fig, ax = plt.subplots(figsize=(8, 4))
    ax.barh(list(conteo_resultados.keys()), list(conteo_resultados.values()), color="steelblue")
    ax.set_xlabel("Cantidad")
    ax.set_title("Resultados Detectados")
    st.pyplot(fig)

    st.subheader("🧠 Recomendaciones Automáticas")
    recomendaciones = [
        generar_recomendacion("Transacciones Conciliadas", conteo_resultados["Conciliadas"], 0,
                              "Conciliación correcta.",
                              "Verifica registros coincidentes."),
        generar_recomendacion("Transacciones Faltantes", conteo_resultados["Faltantes en destino"], 2,
                              "No se detectaron omisiones.",
                              "Posibles errores u omisiones en registro."),
        generar_recomendacion("Transacciones Inesperadas", conteo_resultados["Inesperadas en destino"], 2,
                              "No se detectaron ingresos inesperados.",
                              "Revisar ingresos no respaldados por origen."),
        generar_recomendacion("Discrepancias de Valor", conteo_resultados["Discrepancias de valor"], 2,
                              "Fechas y montos están alineados.",
                              "Existen valores que no coinciden."),
        generar_recomendacion("Duplicados Internos", conteo_resultados["Duplicados"], 2,
                              "No se encontraron duplicaciones.",
                              "Registros repetidos requieren revisión.")
    ]
    for reco in recomendaciones:
        st.markdown(reco)

    st.subheader("🧾 Conclusión del Análisis")
    st.markdown(generar_conclusion_conteo(conteo_resultados))
