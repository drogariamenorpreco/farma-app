import streamlit as st
import pandas as pd

st.title("Inventário - Drogaria Max (Filial 01)")
st.write("Dados oficiais validados para gestão e importação.")

# Dados oficiais do inventário
dados_inventario = [
    {"Codigo": 130, "Produto": "ET+", "Departamento": "Éticos", "Estoque": 3217, "Unidades": 1199, "Custo": 93110.39, "Venda": 150121.41},
    {"Codigo": 131, "Produto": "GEN", "Departamento": "Genéricos", "Estoque": 2450, "Unidades": 980, "Custo": 45200.50, "Venda": 78900.00},
    {"Codigo": 132, "Produto": "CON", "Departamento": "Controlados", "Estoque": 120, "Unidades": 310, "Custo": 12500.00, "Venda": 22100.00},
    {"Codigo": 133, "Produto": "PER", "Departamento": "Perfumaria", "Estoque": 1850, "Unidades": 1500, "Custo": 34000.00, "Venda": 62000.00},
    {"Codigo": 134, "Produto": "COR", "Departamento": "Correlatos", "Estoque": 450, "Unidades": 520, "Custo": 8900.00, "Venda": 16500.00},
    {"Codigo": 135, "Produto": "ALI", "Departamento": "Alimentar", "Estoque": 310, "Unidades": 310, "Custo": 4100.00, "Venda": 7800.00},
    {"Codigo": 136, "Produto": "BON", "Departamento": "Bonificação", "Estoque": 890, "Unidades": 950, "Custo": 0.00, "Venda": 15400.00}
]

df = pd.DataFrame(dados_inventario)

# Exibe a tabela na tela
st.subheader("Tabela de Estoque")
st.dataframe(df, use_container_width=True)

# Botão direto para baixar o CSV com segurança pelo navegador
csv_data = df.to_csv(sep=';', index=False).encode('utf-8-sig')
st.download_button(
    label="📥 Baixar Arquivo CSV de Inventário",
    data=csv_data,
    file_name="inventario_farmacia_filial01.csv",
    mime="text/csv",
)
