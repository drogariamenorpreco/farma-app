import streamlit as st
import pandas as pd
import datetime

# Configuração da página
st.set_page_config(
    page_title="Farma Lagos - Sistema de Vendas",
    page_icon="💊",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# Estilização CSS
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
        padding: 15px;
        background-color: white;
        border-radius: 10px;
        margin-bottom: 15px;
        box-shadow: 0px 2px 5px rgba(0,0,0,0.1);
    }
</style>
""", unsafe_allow_html=True)

# Cabeçalho
st.markdown("""
<div class="header-box">
    <h1 style="color: #0066cc; margin:0; font-size: 24px;">FARMA LAGOS</h1>
    <p style="margin:5px 0 0 0; font-weight:bold; color:#555; font-size: 14px;">CNPJ: 68.530.976/0001-00</p>
</div>
""", unsafe_allow_html=True)

# Inicializar Carrinho de Compras na Sessão
if 'carrinho' not in st.session_state:
    st.session_state.carrinho = []

# Menu de Navegação
menu = st.sidebar.radio("Navegação", ["Emitir Pedido / Carrinho", "Estoque de Medicamentos"])

if menu == "Emitir Pedido / Carrinho":
    st.header("🛒 Carrinho & Pedido")
    
    # Seção para Adicionar Produtos ao Carrinho
    with st.expander("➕ Adicionar Produto ao Carrinho", expanded=True):
        with st.form("form_add_produto"):
            nome_prod = st.text_input("Nome do Medicamento / Produto")
            col1, col2 = st.columns(2)
            with col1:
                qtd_prod = st.number_input("Quantidade", min_value=1, value=1, step=1)
            with col2:
                preco_prod = st.number_input("Preço Unitário (R$)", min_value=0.0, value=0.0, format="%.2f")
            
            add_btn = st.form_submit_button("Inserir no Carrinho")
            if add_btn:
                if nome_prod and preco_prod > 0:
                    st.session_state.carrinho.append({
                        "Produto": nome_prod,
                        "Qtd": qtd_prod,
                        "Preço Unit.": preco_prod,
                        "Subtotal": qtd_prod * preco_prod
                    })
                    st.success(f"{nome_prod} adicionado!")
                    st.rerun()
                else:
                    st.warning("Informe o nome e um preço válido para o produto.")

    # Exibição do Carrinho
    if len(st.session_state.carrinho) > 0:
        st.subheader("Itens no Carrinho")
        df_carrinho = pd.DataFrame(st.session_state.carrinho)
        st.dataframe(df_carrinho, use_container_width=True)
        
        total_geral = df_carrinho["Subtotal"].sum()
        st.markdown(f"### **Total Geral: R$ {total_geral:.2f}**")
        
        if st.button("🗑️ Limpar Carrinho"):
            st.session_state.carrinho = []
            st.rerun()
        
        st.divider()
        
        # Dados do Cliente para Fechamento
        st.subheader("Dados para o Comprovante Fiscal / WhatsApp")
        with st.form("form_finalizar"):
            cliente = st.text_input("Nome do Cliente")
            telefone = st.text_input("WhatsApp do Cliente (com DDD)")
            pagamento = st.selectbox("Forma de Pagamento", ["Pix", "Dinheiro", "Cartão de Crédito", "Cartão de Débito"])
            
            gerar_pedido = st.form_submit_button("Gerar Comprovante para Envio")
            
            if gerar_pedido:
                if cliente:
                    data_atual = datetime.datetime.now().strftime("%d/%m/%Y %H:%M")
                    
                    itens_texto = ""
                    for item in st.session_state.carrinho:
                        itens_texto += f"- {item['Qtd']}x {item['Produto']} (R$ {item['Subtotal']:.2f})\n"
                    
                    comprovante = f"""*FARMA LAGOS - COMPROVANTE DE PEDIDO*
CNPJ: 68.530.976/0001-00
Data: {data_atual}
-----------------------------------
*Cliente:* {cliente}
*Itens:*
{itens_texto}
*Valor Total:* R$ {total_geral:.2f}
*Forma de Pagamento:* {pagamento}
-----------------------------------
Obrigado pela preferência! Sua saúde em primeiro lugar."""

                    st.success("Comprovante Fiscal gerado com sucesso!")
                    st.text_area("Copie a mensagem abaixo para enviar via WhatsApp:", comprovante, height=220)
                else:
                    st.warning("Por favor, preencha o nome do cliente.")
    else:
        st.info("Seu carrinho está vazio. Adicione produtos acima para começar.")

elif menu == "Estoque de Medicamentos":
    st.header("📦 Estoque de Medicamentos (Filial 01)")
    st.markdown("Consulta rápida baseada no inventário geral cadastrado.")
    
    # Base de dados simulada com base no inventário oficial da Filial 01
    dados_estoque = [
        {"Grupo": "GENERIC *7", "Itens Cadastrados": 435, "Unidades": 4131, "Valor Venda Médio": "R$ 149.962,92"},
        {"Grupo": "GEN/CON 7%", "Itens Cadastrados": 148, "Unidades": 568, "Valor Venda Médio": "R$ 43.935,05"},
        {"Grupo": "GENERIC 7%", "Itens Cadastrados": 40, "Unidades": 175, "Valor Venda Médio": "R$ 8.956,70"},
        {"Grupo": "GENERIC/ET", "Itens Cadastrados": 79, "Unidades": 1969, "Valor Venda Médio": "R$ 31.312,08"},
        {"Grupo": "ET+ (Similares/Éticos)", "Itens Cadastrados": 1199, "Unidades": 3217, "Valor Venda Médio": "R$ 150.121,41"},
        {"Grupo": "ET/DERMO", "Itens Cadastrados": 385, "Unidades": 731, "Valor Venda Médio": "R$ 48.750,04"},
        {"Grupo": "ET0 (Éticos)", "Itens Cadastrados": 321, "Unidades": 1204, "Valor Venda Médio": "R$ 49.586,46"},
        {"Grupo": "CONTROLADOS (-)", "Itens Cadastrados": 189, "Unidades": 355, "Valor Venda Médio": "R$ 31.492,16"},
        {"Grupo": "BONIF 10%", "Itens Cadastrados": 254, "Unidades": 3221, "Valor Venda Médio": "R$ 92.336,51"},
        {"Grupo": "NATURAL / FITOTÉRPICOS", "Itens Cadastrados": 103, "Unidades": 458, "Valor Venda Médio": "R$ 6.900,69"},
        {"Grupo": "OFICINAIS", "Itens Cadastrados": 42, "Unidades": 394, "Valor Venda Médio": "R$ 3.218,50"},
    ]
    
    df_estoque = pd.DataFrame(dados_estoque)
    
    pesquisa = st.text_input("🔍 Pesquisar Grupo de Medicamento")
    if pesquisa:
        df_estoque = df_estoque[df_estoque["Grupo"].str.contains(pesquisa, case=False, na=False)]
    
    st.dataframe(df_estoque, use_container_width=True)
    st.caption("Total Geral de Itens Cadastrados na Filial: 40.242[span_0](start_span)[span_0](end_span)")
