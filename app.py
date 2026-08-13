import streamlit as st
import pandas as pd
import urllib.parse

st.set_page_config(page_title="Gestão Drogaria Max - Filial 01", layout="wide")

st.title("💊 Drogaria Max - Gestão Filial 01")
st.write("Painel completo de estoque, vendas, dados de entrega e envio via WhatsApp.")

# Dados oficiais do inventário e vendas
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

# Abas de Navegação
aba1, aba2, aba3 = st.tabs(["📦 Estoque & Vendas", "🚚 Dados de Entrega", "📱 Envio WhatsApp"])

with aba1:
    st.subheader("🔍 Pesquisa e Dados de Estoque/Vendas")
    
    # Lupa de pesquisa
    pesquisa = st.text_input("Pesquisar por Código, Produto ou Departamento", "")
    
    df_filtrado = df.copy()
    if pesquisa:
        pesquisa_lower = pesquisa.lower()
        df_filtrado = df[
            df['Produto'].str.lower().str.contains(pesquisa_lower) |
            df['Departamento'].str.lower().str.contains(pesquisa_lower) |
            df['Codigo'].astype(str).str.contains(pesquisa_lower)
        ]
    
    # Métricas de resumo de vendas e custo
    total_custo = df_filtrado['Custo'].sum()
    total_venda = df_filtrado['Venda'].sum()
    
    col1, col2 = st.columns(2)
    col1.metric("Custo Total", f"R$ {total_custo:,.2f}")
    col2.metric("Valor de Venda Total", f"R$ {total_venda:,.2f}")
    
    st.dataframe(df_filtrado, use_container_width=True)
    
    # Botão para baixar CSV
    csv_data = df_filtrado.to_csv(sep=';', index=False).encode('utf-8-sig')
    st.download_button(
        label="📥 Baixar Dados Filtrados em CSV",
        data=csv_data,
        file_name="inventario_vendas_filial01.csv",
        mime="text/csv",
    )

with aba2:
    st.subheader("🚚 Controle de Dados de Entrega")
    st.write("Registre e verifique o status das entregas da filial:")
    
    dados_entrega = [
        {"Pedido": "#101", "Cliente": "Mariane", "Endereço": "Praia Rasa, Búzios", "Status": "Entregue", "Valor": "R$ 150,00"},
        {"Pedido": "#102", "Cliente": "João Silva", "Endereço": "Centro, Búzios", "Status": "Em Rota", "Valor": "R$ 89,90"},
        {"Pedido": "#103", "Cliente": "Ana Souza", "Endereço": "Manguinhos, Búzios", "Status": "Separando", "Valor": "R$ 210,50"}
    ]
    df_entrega = pd.DataFrame(dados_entrega)
    st.dataframe(df_entrega, use_container_width=True)

with aba3:
    st.subheader("📱 Enviar Comprovante / Resumo via WhatsApp")
    
    telefone = st.text_input("Número do WhatsApp (com DDD, ex: 22999999999)", "")
    nome_cliente = st.text_input("Nome do Cliente", "")
    detalhes_pedido = st.text_area("Detalhes / Comprovante do Pedido", "Olá! Segue o resumo do seu pedido na Drogaria Max - Filial 01.")
    
    if st.button("Gerar Link do WhatsApp"):
        if telefone and nome_cliente:
            mensagem = f"Olá {nome_cliente},\n\n{detalhes_pedido}\n\nObrigado pela preferência!"
            mensagem_codificada = urllib.parse.quote(mensagem)
            link_zap = f"https://wa.me/55{telefone}?text={mensagem_codificada}"
            st.success("Link gerado com sucesso! Clique abaixo para enviar:")
            st.markdown(f"[📲 Clique aqui para abrir no WhatsApp]({link_zap})", unsafe_allow_html=True)
        else:
            st.warning("Por favor, preencha o número do WhatsApp e o nome do cliente.")
