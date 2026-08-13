import os
import pandas as pd
import streamlit as st

# Configuração da Página
st.set_page_config(
    page_title="Gestão de Vendas - Farmácia", layout="wide", initial_sidebar_state="expanded"
)

# Arquivo local para persistência permanente do estoque
ARQUIVO_BANCO = "estoque_farmacia_real.csv"

# ---------------------------------------------------------
# FUNÇÕES DE PERSISTÊNCIA (SALVAR/CARREGAR AUTOMÁTICO)
# ---------------------------------------------------------
def carregar_dados():
    if os.path.exists(ARQUIVO_BANCO):
        try:
            return pd.read_csv(ARQUIVO_BANCO)
        except Exception:
            return pd.DataFrame(columns=["Código", "Produto", "Departamento", "Estoque", "Preço Custo", "Preço Venda"])
    else:
        return pd.DataFrame(columns=["Código", "Produto", "Departamento", "Estoque", "Preço Custo", "Preço Venda"])

def salvar_dados(df):
    df.to_csv(ARQUIVO_BANCO, index=False)

# Inicializar o session_state com os dados salvos no disco
if "estoque" not in st.session_state:
    st.session_state["estoque"] = carregar_dados()

if "carrinho" not in st.session_state:
    st.session_state["carrinho"] = []

# ---------------------------------------------------------
# MENU DE NAVEGAÇÃO LATERAL
# ---------------------------------------------------------
st.sidebar.title("📌 Menu de Navegação")
menu = st.sidebar.radio(
    "Escolha a Seção",
    [
        "📦 Importar Inventário & Estoque",
        "🛒 Carrinho & Vendas",
        "⚙️ Gerenciar Preços e Produtos",
    ],
)

# =========================================================
# SEÇÃO 1: IMPORTAR INVENTÁRIO & ESTOQUE
# =========================================================
if menu == "📦 Importar Inventário & Estoque":
    st.title("📦 Inventário Oficial e Importação")

    st.markdown(
        "### 📂 Envie a sua Planilha de Inventário Oficial\n"
        "Faça o upload do seu arquivo contendo os mais de 3 mil produtos (CSV ou Excel). "
        "O sistema vai salvar todos os itens permanentemente no seu estoque."
    )

    arquivo_upload = st.file_uploader(
        "Selecione o arquivo do inventário (CSV ou Excel)", type=["csv", "xlsx", "xls"]
    )
    
    if arquivo_upload is not None:
        try:
            if arquivo_upload.name.endswith(".csv"):
                df_upload = pd.read_csv(arquivo_upload)
            else:
                df_upload = pd.read_excel(arquivo_upload)
            
            # Normaliza os nomes das colunas comuns para evitar erros (caso venham com letras maiúsculas/minúsculas)
            df_upload.columns = [str(col).strip() for col in df_upload.columns]
            
            st.session_state["estoque"] = df_upload
            salvar_dados(df_upload)  # Salva permanentemente
            st.success(f"🎉 Sucesso! {len(df_upload)} produtos foram importados e salvos permanentemente no seu estoque!")
        except Exception as e:
            st.error(f"Erro ao ler o arquivo: {e}")

    df_atual = st.session_state["estoque"]
    if not df_atual.empty:
        st.info(f"📊 Atualmente existem **{len(df_atual)} produtos** salvos no estoque do aplicativo.")
    else:
        st.warning("⚠️ O estoque está vazio. Faça o upload da sua planilha acima para começar.")

# =========================================================
# SEÇÃO 2: CARRINHO & VENDAS
# =========================================================
elif menu == "🛒 Carrinho & Vendas":
    st.title("🛒 Carrinho & Cupom Fiscal")

    df_estoque = st.session_state["estoque"]

    if df_estoque.empty:
        st.warning(
            "⚠️ O seu estoque está vazio! Vá até a aba '📦 Importar Inventário & Estoque' e faça o upload da sua planilha de produtos."
        )
    else:
        with st.expander("➕ Adicionar Produto do Estoque", expanded=True):
            
            # 🔍 LUPA DE PESQUISA LIVRE POR DIGITAÇÃO
            termo_busca = st.text_input("🔍 Digite o nome do produto para pesquisar:", placeholder="Ex: Omeprazol, Puravit, Dipirona...")

            if termo_busca:
                # Procura o termo digitado em qualquer coluna de texto do DataFrame (focado na coluna de produtos)
                coluna_produto = [c for c in df_estoque.columns if 'prod' in c.lower() or 'desc' in c.lower() or 'nome' in c.lower()]
                col_alvo = coluna_produto[0] if coluna_produto else df_estoque.columns[1]

                df_filtrado = df_estoque[df_estoque[col_alvo].astype(str).str.contains(termo_busca, case=False, na=False)]

                if not df_filtrado.empty:
                    lista_encontrados = df_filtrado[col_alvo].tolist()
                    
                    pesquisa = st.selectbox("Selecione o produto encontrado:", options=lista_encontrados)

                    if pesquisa:
                        produto_info = df_estoque[df_estoque[col_alvo] == pesquisa].iloc[0]
                        
                        # Tenta identificar colunas de estoque, departamento e preço de forma inteligente
                        cols_lower = {c.lower(): c for c in df_estoque.columns}
                        
                        col_est = next((cols_lower[k] for k in cols_lower if 'estq' in k or 'qtde' in k or 'saldo' in k or 'estoque' in k), df_estoque.columns[3] if len(df_estoque.columns) > 3 else None)
                        col_dep = next((cols_lower[k] for k in cols_lower if 'dept' in k or 'grupo' in k or 'secao' in k or 'departamento' in k), df_estoque.columns[2] if len(df_estoque.columns) > 2 else None)
                        col_venda = next((cols_lower[k] for k in cols_lower if 'venda' in k or 'preco' in k or 'pv' in k), df_estoque.columns[-1])

                        estoque_disp = produto_info[col_est] if col_est else 9999
                        depto = produto_info[col_dep] if col_dep else "Geral"
                        preco_sugerido = float(produto_info[col_venda]) if col_venda else 0.0

                        st.info(
                            f"📦 Departamento: **{depto}** | Estoque Disponível: **{estoque_disp} unidades**"
                        )

                        col1, col2 = st.columns(2)
                        with col1:
                            quantidade = st.number_input(
                                "Quantidade", min_value=1, max_value=int(estoque_disp) if pd.notna(estoque_disp) and estoque_disp > 0 else 9999, value=1
                            )
                        with col2:
                            preco_venda_ato = st.number_input(
                                "Preço Unitário de Venda (R$) [Editável no Ato]",
                                value=float(preco_sugerido),
                                format="%.2f",
                            )

                        if st.button("Inserir no Carrinho", type="primary"):
                            st.session_state["carrinho"].append(
                                {
                                    "Produto": pesquisa,
                                    "Departamento": depto,
                                    "Quantidade": quantidade,
                                    "Preço Unitário": preco_venda_ato,
                                    "Total": quantidade * preco_venda_ato,
                                }
                            )
                            st.success(f"'{pesquisa}' adicionado ao carrinho com sucesso!")
                else:
                    st.warning("Nenhum produto encontrado com esse termo no seu estoque.")
            else:
                st.info("Digite algo no campo de cima para iniciar a busca no estoque.")

        st.markdown("---")
        st.subheader("🛍️ Itens no Carrinho")
        if len(st.session_state["carrinho"]) > 0:
            df_carrinho = pd.DataFrame(st.session_state["carrinho"])
            st.dataframe(df_carrinho, use_container_width=True)

            val_total_geral = df_carrinho["Total"].sum()
            st.markdown(f"### 💰 **Total Geral da Venda: R$ {val_total_geral:.2f}**")

            if st.button("🗑️ Limpar Carrinho"):
                st.session_state["carrinho"] = []
                st.rerun()
        else:
            st.info("Seu carrinho está vazio. Adicione produtos acima para começar.")

# =========================================================
# SEÇÃO 3: GERENCIAR PREÇOS E PRODUTOS
# =========================================================
elif menu == "⚙️ Gerenciar Preços e Produtos":
    st.title("⚙️ Gerenciamento de Estoque e Preços")
    st.markdown(
        "Edite diretamente o preço de custo, preço de venda ou quantidades. As alterações ficam salvas permanentemente."
    )

    df_estoque = st.session_state["estoque"]

    if df_estoque.empty:
        st.warning("O estoque está vazio no momento.")
    else:
        df_editado = st.data_editor(
            df_estoque, num_rows="dynamic", key="tabela_gerenciamento_estoque", use_container_width=True
        )

        if st.button("💾 Salvar Alterações do Estoque", type="primary"):
            st.session_state["estoque"] = df_editado
            salvar_dados(df_editado)
            st.success("Alterações salvas permanentemente no estoque com sucesso!")
