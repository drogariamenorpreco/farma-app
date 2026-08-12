import pandas as pd
import streamlit as st

# Configuração da Página
st.set_page_config(
    page_title="Gestão de Vendas - Farmácia", layout="wide", initial_sidebar_state="expanded"
)

# ---------------------------------------------------------
# INICIALIZAÇÃO DO ESTADO DA SESSÃO
# ---------------------------------------------------------
if "estoque" not in st.session_state:
    # DataFrame inicial vazio ou estruturado para o estoque
    st.session_state["estoque"] = pd.DataFrame(
        columns=[
            "Código",
            "Produto",
            "Departamento",
            "Estoque",
            "Preço Custo",
            "Preço Venda",
        ]
    )

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
        "Clique no botão abaixo para carregar imediatamente todos os dados oficiais do inventário da **Filial 01** para o seu aplicativo de vendas."
    )

    if st.button("🚀 Carregar Dados Oficiais do Inventário (Filial 01)", type="primary"):
        # Dados oficiais simulados/carregados automaticamente
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
        st.success(
            "Inventário da Filial 01 carregado e salvo automaticamente no estoque com sucesso!"
        )

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
            st.success("Planilha importada e estoque atualizado com sucesso!")
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
            "⚠️ O seu estoque está vazio! Vá até a aba '📦 Importar Inventário & Estoque' e clique em 'Carregar Dados Oficiais' primeiro."
        )
    else:
        with st.expander("➕ Adicionar Produto do Estoque", expanded=True):
            # BUSCA GLOBAL: O campo abaixo busca em TODOS os produtos/departamentos automaticamente
            lista_produtos = df_estoque["Produto"].tolist()
            pesquisa = st.selectbox(
                "Pesquisar Medicamento / Produto (Busca Global em Todos os Departamentos):",
                options=lista_produtos,
            )

            if pesquisa:
                # Localiza as informações do produto selecionado
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
                    # OPÇÃO EXTRA: Editar o preço de venda no ato da venda
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
        "Aqui você pode visualizar e editar diretamente o **preço de custo**, **preço de venda** e quantidades do seu estoque."
    )

    df_estoque = st.session_state["estoque"]

    if df_estoque.empty:
        st.warning("O estoque está vazio no momento.")
    else:
        # Tabela interativa para edição direta de custos, vendas e estoque
        df_editado = st.data_editor(
            df_estoque, num_rows="dynamic", key="tabela_gerenciamento_estoque", use_container_width=True
        )

        if st.button("💾 Salvar Alterações do Estoque", type="primary"):
            st.session_state["estoque"] = df_editado
            st.success("Preços de custo, venda e inventário atualizados com sucesso!")
