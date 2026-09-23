import streamlit as st
import pandas as pd

# Configuração da página
st.set_page_config(page_title="FARMA BÚZIOS - PDV", page_icon="💊", layout="centered")

st.title("💊 FARMA BÚZIOS - PDV")

# --- MEMÓRIA PERSISTENTE DO CARRINHO ---
# Garante que os itens NÃO apaguem ao clicar em botões ou pesquisar novos produtos
if "carrinho" not in st.session_state:
    st.session_state.carrinho = []

# Base de produtos (Exemplo - substitua ou conecte ao seu CSV se necessário)
@st.cache_data
def carregar_estoque():
    return [
        {"id": 1, "nome": "CHOCOLATE GAROTO CARIBE 28G", "preco": 3.00},
        {"id": 2, "nome": "ENTRESTO 49MG/51MG C/60 COMP", "preco": 318.68},
        {"id": 3, "nome": "DIPIRONA 500MG C/20 COMP", "preco": 8.50},
        {"id": 4, "nome": "DORFLEX C/36 COMP", "preco": 22.90},
        {"id": 5, "nome": "NEOSALDINA C/20 DRÁGEAS", "preco": 26.50}
    ]

produtos = carregar_estoque()
lista_nomes = [p["nome"] for p in produtos]

# --- CAMPO DE SELEÇÃO / PESQUISA ---
st.subheader("Selecione o produto:")

# O selectbox do Streamlit já possui pesquisa por digitação integrada
produto_selecionado = st.selectbox(
    "Selecione:",
    options=lista_nomes,
    index=0
)

# Buscar preço do produto selecionado
dados_prod = next((p for p in produtos if p["nome"] == produto_selecionado), {"preco": 0.00})

col_preco, col_qtd = st.columns(2)
with col_preco:
    preco_final = st.number_input(
        "Preço de Venda Final (R$):", 
        value=float(dados_prod["preco"]), 
        format="%.2f"
    )

with col_qtd:
    quantidade = st.number_input("Quantidade:", min_value=1, value=1, step=1)

# BOTÃO ADICIONAR AO CARRINHO
if st.button("➕ Adicionar ao Carrinho", use_container_width=True):
    # Procura se o produto já está no carrinho acumulado
    item_existente = next((item for item in st.session_state.carrinho if item["nome"] == produto_selecionado), None)
    
    if item_existente:
        item_existente["qtd"] += quantidade
        item_existente["preco"] = preco_final
    else:
        st.session_state.carrinho.append({
            "nome": produto_selecionado,
            "preco": preco_final,
            "qtd": quantidade
        })
    st.success(f"✅ {produto_selecionado} adicionado ao carrinho!")

st.divider()

# --- LISTA VISÍVEL DO CARRINHO ACUMULADO ---
st.subheader("🛒 Itens no Carrinho")

if len(st.session_state.carrinho) == 0:
    st.info("O carrinho está vazio.")
else:
    subtotal_geral = 0.0
    
    # Exibe cada produto que já foi adicionado
    for idx, item in enumerate(st.session_state.carrinho):
        total_item = item["preco"] * item["qtd"]
        subtotal_geral += total_item
        
        c1, c2, c3 = st.columns([3, 1.5, 0.5])
        with c1:
            st.markdown(f"**{item['qtd']}x {item['nome']}**")
            st.caption(f"R$ {item['preco']:.2f} un.")
        with c2:
            st.markdown(f"**R$ {total_item:.2f}**")
        with c3:
            if st.button("🗑️", key=f"remover_{idx}"):
                st.session_state.carrinho.pop(idx)
                st.rerun()
        st.divider()

    # --- TAXA DE ENTREGA E DADOS DO CLIENTE ---
    add_taxa = st.checkbox("🚚 Adicionar taxa de entrega?")
    taxa_entrega = 0.0
    if add_taxa:
        taxa_entrega = st.number_input("Valor da Taxa (R$):", min_value=0.0, value=5.00, step=1.00)

    nome_cliente = st.text_input("Nome do Cliente:")
    whatsapp_cliente = st.text_input("WhatsApp (ex: 22999999999):")

    valor_total_final = subtotal_geral + taxa_entrega
    st.markdown(f"### **TOTAL: R$ {valor_total_final:.2f}**")

    # BOTÃO FINALIZAR
    if st.button("✅ GERAR NOTA E OPÇÕES", use_container_width=True):
        st.success("Nota gerada com sucesso!")
        
        # Montar resumo para o WhatsApp
        resumo = f"*FARMA BÚZIOS*\n-------------------\n"
        resumo += f"👤 Cliente: {nome_cliente if nome_cliente else 'Cliente'}\n"
        resumo += "-------------------\n*ITENS:*\n"
        for i in st.session_state.carrinho:
            resumo += f"• {i['qtd']}x {i['nome']} = R$ {i['preco']*i['qtd']:.2f}\n"
        
        if taxa_entrega > 0:
            resumo += f"🛵 Taxa de Entrega: R$ {taxa_entrega:.2f}\n"
            
        resumo += f"-------------------\n*TOTAL A PAGAR: R$ {valor_total_final:.2f}*"
        
        st.text_area("Comprovante WhatsApp:", value=resumo, height=150)
        
        if st.button("Limpar e Novo Pedido"):
            st.session_state.carrinho = []
            st.rerun()
