import streamlit as st
import pandas as pd

# Configuração da página
st.set_page_config(page_title="Farma Búzios - Vendas", page_icon="💊", layout="centered")

st.title("💊 Farma Búzios - Gestão & Vendas")

# --- INICIALIZAÇÃO DO ESTADO DA SESSÃO (CARRINHO E DADOS) ---
if "carrinho" not in st.session_state:
    st.session_state.carrinho = []

# Base de dados de exemplo / simulada (Ajuste ou carregue o seu CSV aqui se necessário)
@st.cache_data
def carregar_produtos():
    return pd.DataFrame([
        {"id": 1, "nome": "ENTRESTO 49MG/51MG C/60 COMP", "preco_de": 374.92, "preco_por": 318.68, "estoque": 10},
        {"id": 2, "nome": "DIPIRONA 500MG C/20 COMP", "preco_de": 12.00, "preco_por": 8.50, "estoque": 50},
        {"id": 3, "nome": "DORFLEX C/36 COMP", "preco_de": 28.00, "preco_por": 22.90, "estoque": 30},
        {"id": 4, "nome": "LOSARTANA POTÁSSICA 50MG C/30 COMP", "preco_de": 15.00, "preco_por": 9.90, "estoque": 40},
    ])

df_produtos = carregar_produtos()

# --- ÁREA DE SELEÇÃO E BUSCA DE MEDICAMENTOS ---
st.markdown("### Selecione o Medicamento")

# Seleção do Produto
produto_nome = st.selectbox(
    "Selecione:",
    options=df_produtos["nome"].tolist(),
    index=0
)

# Obter dados do produto selecionado
produto_info = df_produtos[df_produtos["nome"] == produto_nome].iloc[0]

# Campos de Preço e Quantidade
col1, col2 = st.columns(2)
with col1:
    preco_final = st.number_input(
        "Preço de Venda Final (R$):",
        value=float(produto_info["preco_por"]),
        format="%.2f"
    )
with col2:
    quantidade = st.number_input(
        "Quantidade:",
        min_value=1,
        max_value=int(produto_info["estoque"]),
        value=1,
        step=1
    )

# Botão Adicionar ao Carrinho
if st.button("➕ Adicionar ao Carrinho", use_container_width=True):
    # Procura se o item já está no carrinho
    item_existente = next((item for item in st.session_state.carrinho if item["id"] == produto_info["id"]), None)
    
    if item_existente:
        item_existente["quantidade"] += quantidade
        item_existente["preco_unitario"] = preco_final
    else:
        st.session_state.carrinho.append({
            "id": produto_info["id"],
            "nome": produto_info["nome"],
            "preco_de": produto_info["preco_de"],
            "preco_unitario": preco_final,
            "quantidade": quantidade
        })
    
    st.success(f"✅ **{produto_nome}** adicionado ao carrinho!")

st.divider()

# --- EXIBIÇÃO FIXA DO CARRINHO DE COMPRAS ---
st.markdown("### 🛒 Carrinho de Compras (Itens Adicionados)")

if len(st.session_state.carrinho) == 0:
    st.info("Nenhum medicamento no carrinho no momento.")
else:
    subtotal_geral = 0.0
    
    # Lista cada item do carrinho acumulado
    for idx, item in enumerate(st.session_state.carrinho):
        subtotal_item = item["preco_unitario"] * item["quantidade"]
        subtotal_geral += subtotal_item
        
        c1, c2, c3 = st.columns([3, 1, 1])
        with c1:
            st.markdown(f"**{item['quantidade']}x {item['nome']}**")
            st.caption(f"De: R$ {item['preco_de']:.2f} | **Por: R$ {item['preco_unitario']:.2f} un.**")
        with c2:
            st.markdown(f"**R$ {subtotal_item:.2f}**")
        with c3:
            if st.button("🗑️", key=f"del_{idx}"):
                st.session_state.carrinho.pop(idx)
                st.rerun()
        st.divider()

    # --- TAXA DE ENTREGA E DADOS DO CLIENTE ---
    add_taxa = st.checkbox("🚚 Adicionar taxa de entrega?")
    taxa_entrega = 0.0
    if add_taxa:
        taxa_entrega = st.number_input("Valor da taxa (R$):", min_value=0.0, value=5.0, step=1.0)

    nome_cliente = st.text_input("Nome do Cliente:")
    whatsapp_cliente = st.text_input("WhatsApp (ex: 22999999999):")

    total_final = subtotal_geral + taxa_entrega

    st.markdown(f"#### **Total a Pagar: R$ {total_final:.2f}**")

    # Botão para gerar comprovante/nota
    if st.button("✅ GERAR NOTA E OPÇÕES", use_container_width=True):
        st.success("Nota gerada com sucesso!")
        
        # Gerar texto para WhatsApp
        msg_wa = f"*FARMA BÚZIOS*\n------------------------\n"
        msg_wa += f"👤 Cliente: {nome_cliente if nome_cliente else 'Cliente'}\n"
        msg_wa += "------------------------\n*ITENS:*\n"
        for i in st.session_state.carrinho:
            msg_wa += f"• {i['quantidade']}x {i['nome']} - R$ {i['preco_unitario']*i['quantidade']:.2f}\n"
        if taxa_entrega > 0:
            msg_wa += f"🛵 Taxa de Entrega: R$ {taxa_entrega:.2f}\n"
        msg_wa += f"------------------------\n*TOTAL: R$ {total_final:.2f}*"
        
        st.text_area("Comprovante WhatsApp:", value=msg_wa, height=150)
        
        # Limpar carrinho após finalizar
        if st.button("Limpar Carrinho"):
            st.session_state.carrinho = []
            st.rerun()
