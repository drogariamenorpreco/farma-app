import streamlit as st
import pandas as pd
import datetime
import urllib.parse

# Configuração da página
st.set_page_config(
    page_title="Farma Lagos - Sistema de Vendas",
    page_icon="💊",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# Número oficial da farmácia fixado
WHATSAPP_FARMACIA = "5522988314812"

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
    <p style="margin:5px 0 0 0; font-weight:bold; color:#555; font-size: 14px;">CNPJ: 68.530.976/0001-00 | WhatsApp: (22) 98831-4812</p>
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
            telefone = st.text_input("WhatsApp do Cliente (com DDD - ex: 21999999999)")
            pagamento = st.selectbox("Forma de Pagamento", ["Pix", "Dinheiro", "Cartão de Crédito", "Cartão de Débito"])
            
            gerar_pedido = st.form_submit_button("Gerar Comprovante para Envio")
            
            if gerar_pedido:
                if cliente and telefone:
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

                    st.session_state.comprovante_gerado = comprovante
                    st.session_state.telefone_cliente = telefone
                    st.success("Comprovante Fiscal gerado com sucesso!")
                else:
                    st.warning("Por favor, preencha o nome do cliente e o WhatsApp.")

        # Exibir botão do WhatsApp se gerado
        if 'comprovante_gerado' in st.session_state and st.session_state.comprovante_gerado:
            st.markdown("---")
            st.subheader("📤 Enviar Comprovante")
            st.info(f"O envio será realizado utilizando o WhatsApp oficial da Farma Lagos: **(22) 98831-4812** para o número do cliente: **{st.session_state.telefone_cliente}**")
            
            tel_limpo = "".join(filter(str.isdigit, st.session_state.telefone_cliente))
            if not tel_limpo.startswith("55"):
                tel_limpo = "55" + tel_limpo
                
            texto_codificado = urllib.parse.quote(st.session_state.comprovante_gerado)
            # Usando o link do WhatsApp com o número do cliente para iniciar a conversa com a mensagem pronta
            link_zap = f"https://wa.me/{tel_limpo}?text={texto_codificado}"
            
            st.markdown(f"""
            <a href="{link_zap}" target="_blank">
                <div style="background-color: #25d366; color: white; padding: 15px; border-radius: 10px; text-align: center; font-weight: bold; font-size: 18px; box-shadow: 0px 4px 10px rgba(37, 211, 102, 0.3);">
                    📲 Enviar Comprovante via WhatsApp (Farma Lagos)
                </div>
            </a>
            """, unsafe_allow_html=True)
            
            st.text_area("Ou copie a mensagem abaixo:", st.session_state.comprovante_gerado, height=180)
    else:
        st.info("Seu carrinho está vazio. Adicione produtos acima para começar.")

elif menu == "Estoque de Medicamentos":
    st.header("📦 Estoque de Medicamentos (Filial 01)")
    st.markdown("Busca inteligente por termos (ex: *amoxi*, *puran*, *gen*, *dermo*).")
    
    dados_estoque = [
        {"Grupo / Medicamento": "Amoxicilina 500mg C/21 cp (Genérico)", "Categoria": "Genéricos", "Unidades": 45, "Preço Venda": "R$ 24,90"},
        {"Grupo / Medicamento": "Amoxicilina + Clavulanato 875mg C/14 cp", "Categoria": "Genéricos", "Unidades": 30, "Preço Venda": "R$ 68,50"},
        {"Grupo / Medicamento": "Puran T4 50mcg C/30 cp", "Categoria": "Éticos / Referência", "Unidades": 120, "Preço Venda": "R$ 18,00"},
        {"Grupo / Medicamento": "Puran T4 25mcg C/30 cp", "Categoria": "Éticos / Referência", "Unidades": 85, "Preço Venda": "R$ 15,50"},
        {"Grupo / Medicamento": "Dipirona Sódica 500mg/ml Gotas", "Categoria": "Similares / OTC", "Unidades": 210, "Preço Venda": "R$ 7,50"},
        {"Grupo / Medicamento": "Dorflex C/10 cp", "Categoria": "Similares / OTC", "Unidades": 350, "Preço Venda": "R$ 6,90"},
        {"Grupo / Medicamento": "Neosaldina C/10 drágeas", "Categoria": "Similares / OTC", "Unidades": 180, "Preço Venda": "R$ 14,20"},
        {"Grupo / Medicamento": "Clonazepam 2.5mg (Controlado)", "Categoria": "Controlados", "Unidades": 45, "Preço Venda": "R$ 11,00"},
        {"Grupo / Medicamento": "Rivotril 2mg C/30 cp", "Categoria": "Controlados", "Unidades": 60, "Preço Venda": "R$ 28,00"},
        {"Grupo / Medicamento": "Losartana Potássica 50mg C/30 cp", "Categoria": "Genéricos", "Unidades": 310, "Preço Venda": "R$ 12,00"},
        {"Grupo / Medicamento": "Sinvastatina 20mg C/30 cp", "Categoria": "Genéricos", "Unidades": 190, "Preço Venda": "R$ 15,00"},
        {"Grupo / Medicamento": "Nimesulida 100mg C/12 cp", "Categoria": "Genéricos", "Unidades": 240, "Preço Venda": "R$ 9,80"},
        {"Grupo / Medicamento": "Vitamina C Redoxon Efervescente", "Categoria": "Vitaminas", "Unidades": 95, "Preço Venda": "R$ 34,90"},
        {"Grupo / Medicamento": "Whey Protein Concentrado 1kg", "Categoria": "Suplementos", "Unidades": 25, "Preço Venda": "R$ 89,90"},
    ]
    
    df_estoque = pd.DataFrame(dados_estoque)
    
    pesquisa = st.text_input("🔍 Digite as primeiras letras (ex: amoxi, pur, dip, neo)")
    
    if pesquisa:
        df_estoque = df_estoque[df_estoque["Grupo / Medicamento"].str.contains(pesquisa, case=False, na=False)]
    
    st.dataframe(df_estoque, use_container_width=True)
    st.caption("Filial 01 - Total Geral de Itens Integrados no Sistema.")
