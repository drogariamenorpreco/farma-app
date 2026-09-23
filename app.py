import streamlit as st
import pandas as pd

st.set_page_config(page_title="FARMA BÚZIOS - PDV", page_icon="💊", layout="centered")

st.title("💊 FARMA BÚZIOS - PDV")

# ==============================================================================
# 1. MEMÓRIA PERSISTENTE DO CARRINHO
# ==============================================================================
if "carrinho" not in st.session_state:
    st.session_state.carrinho = []

# ==============================================================================
# 2. CARREGAMENTO DO ESTOQUE DEDICADO DO CSV
# ==============================================================================
@st.cache_data
def carregar_estoque():
    # Tenta carregar do CSV do repositório
    for nome_arq in ["estoque_drogaria (1).csv", "estoque_drogaria.csv", "estoque.csv"]:
        try:
            df = pd.read_csv(nome_arq)
            df.columns = ['nome', 'estoque', 'preco']
            df['nome'] = df['nome'].astype(str).str.strip()
            df['estoque'] = pd.to_numeric(df['estoque'], errors='coerce').fillna(0).astype(int)
            df['preco'] = pd.to_numeric(df['preco'], errors='coerce').fillna(0.0)
            return df
        except Exception:
            continue
            
    # Base fallback completa caso o arquivo não seja encontrado
    data = [
        {"nome": "AMOXICILINA 500MG C/21 CAPS", "estoque": 35, "preco": 18.90},
        {"nome": "AMOXICILINA + CLAVULANATO 875MG C/14 COMP", "estoque": 20, "preco": 54.50},
        {"nome": "ENTRESTO 49MG/51MG C/60 COMP", "estoque": 10, "preco": 318.68},
        {"nome": "CHOCOLATE GAROTO CARIBE 28G", "estoque": 50, "preco": 3.00},
        {"nome": "DIPIRONA 500MG C/20 COMP", "estoque": 100, "preco": 8.50},
        {"nome": "DORFLEX C/36 COMP", "estoque": 80, "preco": 22.90},
        {"nome": "NEOSALDINA C/20 DRÁGEAS", "estoque": 60, "preco": 26.50}
    ]
    return pd.DataFrame(data)

df_estoque = carregar_estoque()

# ==============================================================================
# 3. CAMPO DE PESQUISA E SELEÇÃO
# ==============================================================================
st.subheader("🔍 Pesquisar e Selecionar Produto")

termo_busca = st.text_input("Digite o nome do produto:", placeholder="Ex: Amoxicilina, Dipirona, Dorflex...")

if termo_busca:
    df_filtrado = df_estoque[df_estoque['nome'].str.contains(termo_busca, case=False, na=False)]
else:
    df_filtrado = df_estoque

lista_produtos = df_filtrado['nome'].tolist()

if not lista_produtos:
    st.warning("Nenhum produto encontrado na busca.")
    produto_selecionado = None
else:
    produto_selecionado = st.selectbox("Produtos encontrados na busca:", options=lista_produtos, index=0)

if produto_selecionado:
    dados_prod = df_estoque[df_estoque['nome'] == produto_selecionado].iloc[0]
    
    col_preco, col_qtd = st.columns(2)
    with col_preco:
        preco_final = st.number_input(
            "Preço de Venda Final (R$):", 
            value=float(dados_prod['preco']), 
            format="%.2f"
        )

    with col_qtd:
        quantidade = st.number_input("Quantidade:", min_value=1, max_value=int(max(1, dados_prod['estoque'])), value=1, step=1)

    st.caption(f"Estoque disponível: **{dados_prod['estoque']} un.**")

    if st.button("➕ Adicionar ao Carrinho", use_container_width=True):
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
        st.success(f"✅ **{produto_selecionado}** adicionado ao carrinho!")

st.divider()

# ==============================================================================
# 4. CARRINHO DE COMPRAS FIXO
# ==============================================================================
st.subheader("🛒 Itens no Carrinho de Compras")

if len(st.session_state.carrinho) == 0:
    st.info("O carrinho está vazio.")
else:
    subtotal_geral = 0.0
    
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

    add_taxa = st.checkbox("🚚 Adicionar taxa de entrega?")
    taxa_entrega = 0.0
    if add_taxa:
        taxa_entrega = st.number_input("Valor da Taxa (R$):", min_value=0.0, value=5.00, step=1.00)

    nome_cliente = st.text_input("Nome do Cliente:")
    whatsapp_cliente = st.text_input("WhatsApp (ex: 22999999999):")

    valor_total_final = subtotal_geral + taxa_entrega
    st.markdown(f"### **TOTAL DO PEDIDO: R$ {valor_total_final:.2f}**")

    if st.button("✅ GERAR NOTA E OPÇÕES", use_container_width=True):
        st.success("Nota gerada com sucesso!")
        
        resumo = f"*FARMA BÚZIOS*\n-------------------\n"
        resumo += f"👤 Cliente: {nome_cliente if nome_cliente else 'Cliente'}\n"
        resumo += "-------------------\n*ITENS DO PEDIDO:*\n"
        for i in st.session_state.carrinho:
            resumo += f"• {i['qtd']}x {i['nome']} = R$ {i['preco']*i['qtd']:.2f}\n"
        
        if taxa_entrega > 0:
            resumo += f"🛵 Taxa de Entrega: R$ {taxa_entrega:.2f}\n"
            
        resumo += f"-------------------\n*TOTAL A PAGAR: R$ {valor_total_final:.2f}*"
        
        st.text_area("Comprovante WhatsApp:", value=resumo, height=150)
        
        if st.button("Limpar Carrinho (Novo Pedido)"):
            st.session_state.carrinho = []
            st.rerun()
