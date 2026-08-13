import streamlit as st
import pandas as pd
import urllib.parse

st.set_page_config(page_title="Gestão Drogaria Max - Filial 01", layout="wide")

st.title("💊 Drogaria Max - Gestão Filial 01")

# Base de dados de produtos detalhada com miligramas e variações para busca inteligente
produtos_cadastrados = [
    {"Codigo": 1301, "Produto": "Amoxicilina 500mg 21 caps", "Departamento": "Éticos", "Estoque": 120, "Custo": 18.50, "Venda": 35.90},
    {"Codigo": 1302, "Produto": "Amoxicilina + Clavulanato 875mg", "Departamento": "Éticos", "Estoque": 85, "Custo": 42.00, "Venda": 79.90},
    {"Codigo": 1303, "Produto": "Amoxicilina Suspensão 250mg", "Departamento": "Éticos", "Estoque": 60, "Custo": 15.00, "Venda": 28.50},
    {"Codigo": 1311, "Produto": "Pantoprazol 20mg 28 comp", "Departamento": "Genéricos", "Estoque": 200, "Custo": 12.00, "Venda": 24.90},
    {"Codigo": 1312, "Produto": "Pantoprazol 40mg 28 comp", "Departamento": "Genéricos", "Estoque": 150, "Custo": 22.00, "Venda": 44.90},
    {"Codigo": 1321, "Produto": "Rivotril 2mg (Controlado)", "Departamento": "Controlados", "Estoque": 40, "Custo": 8.00, "Venda": 18.00},
    {"Codigo": 1331, "Produto": "Perfume Desodorante Kaiak", "Departamento": "Perfumaria", "Estoque": 30, "Custo": 65.00, "Venda": 129.90},
    {"Codigo": 1341, "Produto": "Gliclazida 30mg", "Departamento": "Éticos", "Estoque": 90, "Custo": 25.00, "Venda": 49.90}
]

df_produtos = pd.DataFrame(produtos_cadastrados)

# Abas de Navegação do App
aba1, aba2, aba3, aba4 = st.tabs(["🛒 Fazer Pedido / Venda", "📦 Estoque Geral", "🚚 Entregas", "📱 WhatsApp"])

with aba1:
    st.subheader("🛒 Balcão de Vendas - Pedido do Cliente")
    st.write("Digite ou selecione o medicamento (ex: *Amoxicilina* ou *Pantoprazol*) para puxar automaticamente do estoque:")

    # Caixa de seleção com busca inteligente
    lista_nomes = df_produtos['Produto'].tolist()
    produto_selecionado = st.selectbox("Pesquisar Produto / Medicamento:", options=["Selecione o produto..."] + lista_nomes)

    if produto_selecionado and produto_selecionado != "Selecione o produto...":
        # Puxa as informações exatas do estoque do produto selecionado
        info_prod = df_produtos[df_produtos['Produto'] == produto_selecionado].iloc[0]
        
        st.info(f"**Produto:** {info_prod['Produto']} | **Estoque Atual:** {info_prod['Estoque']} unidades | **Preço de Venda:** R$ {info_prod['Venda']:.2f}")
        
        quantidade_pedido = st.number_input("Quantidade desejada:", min_value=1, max_value=int(info_prod['Estoque']), value=1)
        
        nome_cliente_pedido = st.text_input("Nome do Cliente:", "")
        telefone_pedido = st.text_input("WhatsApp do Cliente (com DDD, ex: 22999999999):", "")
        
        total_item = quantidade_pedido * info_prod['Venda']
        st.write(f"### **Total do Pedido: R$ {total_item:.2f}**")
        
        if st.button("Finalizar Pedido e Enviar Comprovante"):
            if nome_cliente_pedido and telefone_pedido:
                resumo_texto = f"*PEDIDO - DROGARIA MAX (FILIAL 01)*\n\n*Cliente:* {nome_cliente_pedido}\n*Item:* {info_prod['Produto']}\n*Quantidade:* {quantidade_pedido}\n*Valor Total:* R$ {total_item:.2f}\n\nObrigado pela preferência!"
                encoded_msg = urllib.parse.quote(resumo_texto)
                link_wpp = f"https://wa.me/55{telefone_pedido}?text={encoded_msg}"
                
                st.success("Pedido gerado com sucesso!")
                st.markdown(f"[📲 Clique aqui para enviar o comprovante via WhatsApp]({link_wpp})", unsafe_allow_html=True)
            else:
                st.warning("Por favor, preencha o Nome e o WhatsApp do cliente antes de finalizar.")

with aba2:
    st.subheader("📦 Consulta de Estoque Geral")
    pesquisa = st.text_input("Pesquisar por nome ou departamento:", "")
    
    df_filtrado = df_produtos.copy()
    if pesquisa:
        p_lower = pesquisa.lower()
        df_filtrado = df_produtos[
            df_produtos['Produto'].str.lower().str.contains(p_lower) |
            df_produtos['Departamento'].str.lower().str.contains(p_lower)
        ]
    
    st.dataframe(df_filtrado, use_container_width=True)
    
    csv_bytes = df_filtrado.to_csv(sep=';', index=False).encode('utf-8-sig')
    st.download_button("📥 Baixar Estoque em CSV", data=csv_bytes, file_name="estoque_drogaria_max.csv", mime="text/csv")

with aba3:
    st.subheader("🚚 Controle de Entregas")
    dados_entrega = [
        {"Pedido": "#201", "Cliente": "Mariane", "Endereço": "Praia Rasa, Búzios", "Status": "A Caminho", "Valor": "R$ 79,90"}
    ]
    st.dataframe(pd.DataFrame(dados_entrega), use_container_width=True)

with aba4:
    st.subheader("📱 Envio Geral de Mensagens")
    fone = st.text_input("Número do WhatsApp (com DDD):", "")
    msg = st.text_area("Mensagem:", "Olá da Drogaria Max - Filial 01!")
    if st.button("Gerar Link WhatsApp"):
        if fone:
            link = f"https://wa.me/55{fone}?text={urllib.parse.quote(msg)}"
            st.markdown(f"[📲 Abrir no WhatsApp]({link})", unsafe_allow_html=True)
