import streamlit as st
import pandas as pd
import datetime

# Configuração da página para focar na tela do celular
st.set_page_config(
    page_title="Farma Lagos - Sistema de Vendas",
    page_icon="💊",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# Estilização CSS para visual moderno no celular
st.markdown("""
<style>
    .main { background-color: #f8f9fa; }
    .stButton>button {
        width: 100%;
        background-color: #0066cc;
        color: white;
        border-radius: 10px;
        height: 48px;
        font-weight: bold;
        font-size: 16px;
        border: none;
        box-shadow: 0px 4px 10px rgba(0, 102, 204, 0.2);
    }
    .stButton>button:hover {
        background-color: #004999;
        color: white;
    }
    .header-box {
        text-align: center;
        padding: 20px;
        background-color: white;
        border-radius: 10px;
        margin-bottom: 20px;
        box-shadow: 0px 2px 5px rgba(0,0,0,0.1);
    }
</style>
""", unsafe_allow_html=True)

# Cabeçalho da Farmácia Atualizado
st.markdown("""
<div class="header-box">
    <h1 style="color: #0066cc; margin:0;">FARMA LAGOS</h1>
    <p style="margin:5px 0 0 0; font-weight:bold; color:#555;">CNPJ: 68.530.976/0001-00</p>
</div>
""", unsafe_allow_html=True)

# Menu de Navegação
menu = st.sidebar.radio("Navegação", ["Emitir Pedido", "Estoque & Preços", "Clientes & Alertas"])

if menu == "Emitir Pedido":
    st.header("Emitir Pedido do Cliente")
    
    with st.form("form_pedido"):
        cliente = st.text_input("Nome do Cliente")
        telefone = st.text_input("WhatsApp do Cliente (com DDD)")
        produtos = st.text_area("Produtos / Itens do Pedido")
        valor_total = st.number_input("Valor Total (R$)", min_value=0.0, format="%.2f")
        pagamento = st.selectbox("Forma de Pagamento", ["Pix", "Dinheiro", "Cartão de Crédito", "Cartão de Débito"])
        
        enviar = st.form_submit_button("Gerar Comprovante / Pedido")
        
        if enviar:
            if cliente and produtos:
                data_atual = datetime.datetime.now().strftime("%d/%m/%Y %H:%M")
                
                comprovante = f"""*FARMA LAGOS*
CNPJ: 68.530.976/0001-00
Data: {data_atual}
-----------------------------------
*Cliente:* {cliente}
*Itens:*
{produtos}

*Total:* R$ {valor_total:.2f}
*Pagamento:* {pagamento}
-----------------------------------
Obrigado pela preferência!"""

                st.success("Pedido gerado com sucesso!")
                st.text_area("Copie o comprovante abaixo para enviar no WhatsApp:", comprovante, height=200)
            else:
                st.warning("Por favor, preencha o nome do cliente e os produtos.")

elif menu == "Estoque & Preços":
    st.header("Estoque & Preços")
    st.info("Módulo de controle de preços e estoque em desenvolvimento.")

elif menu == "Clientes & Alertas":
    st.header("Clientes & Alertas")
    st.info("Módulo de gestão de clientes em desenvolvimento.")
