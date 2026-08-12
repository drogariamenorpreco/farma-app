import os
import pandas as pd
import streamlit as st

# Configuração da Página
st.set_page_config(
    page_title="Gestão de Vendas - Farmácia", layout="wide", initial_sidebar_state="expanded"
)

# Arquivo local para persistência de dados (salva para não perder ao sair)
ARQUIVO_BANCO = "estoque_farmacia.csv"

# ---------------------------------------------------------
# FUNÇÕES DE PERSISTÊNCIA (SALVAR/CARREGAR AUTOMÁTICO)
# ---------------------------------------------------------
def carregar_dados():
    if os.path.exists(ARQUIVO_BANCO):
        return pd.read_csv(ARQUIVO_BANCO)
    else:
        # Retorna DataFrame vazio estruturado caso não exista arquivo salvo
        return pd.DataFrame(
            columns=[
                "Código",
                "Produto",
                "Departamento",
                "Estoque",
                "Preço Custo",
                "Preço Venda",
            ]
        )

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
        "### 📋 Importação Automática do Inventário Oficial\n"
        "Clique no botão abaixo para carregar imediatamente e **salvar permanentemente** todos os dados oficiais do inventário da **Filial 01**."
    )

    if st.button("🚀 Carregar e Salvar Dados Oficiais (Filial 01)", type="primary"):
        dados_oficiais = pd.DataFrame(
            {
                "Código": ["7891", "7892", "7893", "7894"],
                "Produto": [
                    "Dipirona Sódica 500mg",
                    "Paracetamol 750mg",
                    "Vitamina C 1g",
                    "BONIF 10%",
                ],
                "Departamento": ["Medicamentos", "Medicamentos", "Vitaminas", "Similares"],
                "Estoque": [3221, 1500, 800, 450],
                "Preço Custo": [10.00, 12.00, 20.00, 15.00],
                "Preço Venda": [28.67, 35.00, 49.90, 39.90],
            }
        )
        st.session_state["estoque"] = dados_oficiais
        salvar_dados(dados_oficiais)  # Salva definitivamente no disco
        st.success("Inventário oficial carregado e salvo permanentemente com sucesso!")

    st.markdown("---")
    st.markdown("### 📂 Importar Planilhas Externas (CSV ou Excel)")
    arquivo_upload = st.file_uploader(
        "Selecione arquivo CSV ou Excel", type=["csv", "xlsx", "xls"]
    )
    if arquivo_upload is not None:
        try:
            if arquivo_upload.name.endswith(".csv"):
                df_upload = pd.read_csv(arquivo_upload)
            else:
                df_upload = pd.read_excel(arquivo_upload)
            
            st.session_state["estoque"] = df_upload
            salvar_dados(df_upload)  # Salva definitivamente no disco
            st.success("Planilha importada e salva permanentemente com sucesso!")
        except Exception as e:
            st.error(f"Erro ao ler o arquivo: {e}")

# =========================================================
# SEÇÃO 2: CARRINHO & VENDAS
# =========================================================
elif menu == "🛒 Carrinho & Vendas":
    st.title("🛒 Carrinho & Cupom Fiscal")

    df_estoque = st.session_state["estoque"]

    if df_estoque.empty:
        st.warning(
            "⚠️ O seu estoque está vazio! Vá até a aba '📦 Importar Inventário & Estocar' e carregue os dados oficiais."
        )
    else:
        with st.expander("➕ Adicionar Produto do Estoque", expanded=True):
            st.markdown("🔍 **Digite o nome do produto abaixo (o sistema busca e sugere em tempo real):**")
            
            # Campo de busca otimizado com sugestões automáticas baseadas na digitação
            lista_produtos = df_estoque["Produto"].tolist()
            pesquisa = st.selectbox(
                "Pesquisa de produtos:",
                options=["Selecione ou digite para buscar..."] + lista_produtos,
                label_visibility="collapsed"
            )

            if pesquisa and pesquisa != "Selecione ou digite para buscar...":
                produto_info = df_estoque[df_estoque["Produto"] == pesquisa].iloc[0]
                estoque_disp = produto_info["Estoque"]
                depto = produto_info["Departamento"]
                preco_sugerido = float(produto_info["Preço Venda"])

                st.info(
                    f"📦 Departamento: **{depto}** | Estoque Disponível: **{estoque_disp} unidades**"
                )

                col1, col2 = st.columns(2)
                with col1:
                    quantidade = st.number_input(
                        "Quantidade", min_value=1, max_value=int(estoque_disp), value=1
                    )
                with col2:
                    # Preço de venda editável no ato da venda
                    preco_venda_ato = st.number_input(
                        "Preço Unitário de Venda (R$) [Editável no Ato]",
                        value=preco_sugerido,
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
            salvar_dados(df_editado)  # Salva permanentemente no arquivo local
            st.success("Alterações salvas permanentemente no estoque com sucesso!")
