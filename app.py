import streamlit as st
import pandas as pd
import datetime
import urllib.parse

# Configuração da página
st.set_page_config(
    page_title="Farma Lagos - Sistema de Vendas e Estoque",
    page_icon="💊",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# Estilização CSS personalizada
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
    <p style="margin:5px 0 0 0; font-weight:bold; color:#555; font-size: 13px;">CNPJ: 68.530.976/0001-00 | WhatsApp: (22) 98831-4812</p>
    <p style="margin:0; color:#777; font-size: 12px;">Armação dos Búzios - RJ</p>
</div>
""", unsafe_allow_html=True)

# Inicializar Base de Dados de Estoque na Sessão (se não existir, inicia com alguns exemplos)
if 'estoque_produtos' not in st.session_state:
    st.session_state.estoque_produtos = [
        {"Produto": "AAS AD PROTECT 100MG 30CP", "Quantidade": 8, "Preço": 18.35},
        {"Produto": "AMOXICILINA 500MG C/21 CP", "Quantidade": 45, "Preço": 24.90},
        {"Produto": "PURAN T4 50MCG C/30 CP", "Quantidade": 120, "Preço": 18.00},
        {"Produto": "DIPIRONA SÓDICA 500MG/ML GOTAS", "Quantidade": 210, "Preço": 7.50},
        {"Produto": "DORFLEX C/10 CP", "Quantidade": 350, "Preço": 6.90},
    ]

# Inicializar Carrinho de Compras na Sessão
if 'carrinho' not in st.session_state:
    st.session_state.carrinho = []

# Menu de Navegação
menu = st.sidebar.radio("Navegação", ["Emitir Pedido / Carrinho", "Consultar Estoque", "Gerenciar / Importar Estoque"])

if menu == "Emitir Pedido / Carrinho":
    st.header("🛒 Carrinho & Comprovante Fiscal")
    
    # Seção para Adicionar Produtos ao Carrinho com Busca Inteligente
    with st.expander("➕ Adicionar Produto do Estoque", expanded=True):
        
        # Criar lista ordenada de nomes para busca
        lista_nomes = sorted([str(p["Produto"]) for p in st.session_state.estoque_produtos])
        
        selected_prod = st.selectbox("Pesquisar Medicamento (Digite as iniciais):", lista_nomes)
        
        # Achar o preço e estoque correspondente
        prod_obj = next((p for p in st.session_state.estoque_produtos if p["Produto"] == selected_prod), {"Preço": 0.0, "Quantidade": 0})
        preco_sugerido = prod_obj["Preço"]
        qtd_disponivel = prod_obj["Quantidade"]
        
        st.caption(f"📦 Estoque disponível: **{qtd_disponivel} unidades**")
        
        with st.form("form_add_produto"):
            col1, col2 = st.columns(2)
            with col1:
                qtd_prod = st.number_input("Quantidade", min_value=1, value=1, step=1)
            with col2:
                preco_prod = st.number_input("Preço Unitário (R$)", min_value=0.0, value=float(preco_sugerido), format="%.2f")
            
            add_btn = st.form_submit_button("Inserir no Carrinho")
            if add_btn:
                if selected_prod and preco_prod > 0:
                    st.session_state.carrinho.append({
                        "Produto": selected_prod,
                        "Qtd": qtd_prod,
                        "Preço Unit.": preco_prod,
                        "Subtotal": qtd_prod * preco_prod
                    })
                    st.success(f"{selected_prod} adicionado!")
                    st.rerun()
                else:
                    st.warning("Selecione um produto e informe um preço válido.")

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
        
        # Dados do Cliente para Fechamento Fiscal
        st.subheader("Emitir Cupom Fiscal / WhatsApp")
        with st.form("form_finalizar"):
            cliente = st.text_input("Nome do Cliente")
            telefone = st.text_input("WhatsApp do Cliente (com DDD - ex: 22988887777)")
            pagamento = st.selectbox("Forma de Pagamento", ["Pix", "Dinheiro", "Cartão de Crédito", "Cartão de Débito"])
            
            gerar_pedido = st.form_submit_button("Gerar Cupom Fiscal")
            
            if gerar_pedido:
                if cliente and telefone:
                    data_atual = datetime.datetime.now().strftime("%d/%m/%Y %H:%M:%S")
                    
                    itens_texto = ""
                    for i, item in enumerate(st.session_state.carrinho, 1):
                        itens_texto += f"{i:02d} | {item['Qtd']}x {item['Produto']}\n     R$ {item['Preço Unit.']:.2f} un  ->  Subtotal: R$ {item['Subtotal']:.2f}\n"
                    
                    tributos_aprox = total_geral * 0.1345 # Estimativa média de tributos federais/estaduais
                    
                    # Layout Formato Comprovante Fiscal Oficial
                    comprovante = f"""=====================================
          FARMA LAGOS - CUPOM FISCAL          
       DROGARIA MAX RASA - FILIAL 01        
  CNPJ: 68.530.976/0001-00                  
  Endereço: Armação dos Búzios - RJ         
=====================================
DATA: {data_atual}
-------------------------------------
CLIENTE: {cliente}
-------------------------------------
COD | QTD | DESCRIÇÃO | UNIT | TOTAL
{itens_texto}-------------------------------------
TOTAL GERAL                         R$ {total_geral:.2f}
FORMA DE PAGAMENTO: {pagamento}
-------------------------------------
Trib aprox: R$ {tributos_aprox:.2f} (Fonte: IBPT)
Obrigado pela preferência!
Sua saúde em primeiro lugar.
=====================================
Documento Auxiliar de Venda - Farma Lagos"""

                    st.session_state.comprovante_gerado = comprovante
                    st.session_state.telefone_cliente = telefone
                    st.success("Cupom Fiscal gerado com sucesso!")
                else:
                    st.warning("Por favor, preencha o nome e o WhatsApp do cliente.")

        # Exibir botão do WhatsApp se gerado
        if 'comprovante_gerado' in st.session_state and st.session_state.comprovante_gerado:
            st.markdown("---")
            st.subheader("📤 Envio do Cupom via WhatsApp")
            
            tel_limpo = "".join(filter(str.isdigit, st.session_state.telefone_cliente))
            if not tel_limpo.startswith("55"):
                tel_limpo = "55" + tel_limpo
                
            texto_codificado = urllib.parse.quote(st.session_state.comprovante_gerado)
            link_zap = f"https://wa.me/{tel_limpo}?text={texto_codificado}"
            
            st.markdown(f"""
            <a href="{link_zap}" target="_blank">
                <div style="background-color: #25d366; color: white; padding: 16px; border-radius: 10px; text-align: center; font-weight: bold; font-size: 18px; box-shadow: 0px 4px 10px rgba(37, 211, 102, 0.4);">
                    📱 CLIQUE PARA ENVIAR O CUPOM NO WHATSAPP
                </div>
            </a>
            """, unsafe_allow_html=True)
            
            st.text_area("Visualização do Cupom Fiscal:", st.session_state.comprovante_gerado, height=250)
    else:
        st.info("Seu carrinho está vazio. Adicione produtos acima para começar.")

elif menu == "Consultar Estoque":
    st.header("📦 Consulta Geral do Estoque")
    st.markdown(f"Total de itens cadastrados atualmente: **{len(st.session_state.estoque_produtos)}**")
    
    df_estoque = pd.DataFrame(st.session_state.estoque_produtos)
    pesquisa = st.text_input("🔍 Pesquisar medicamento no estoque:")
    
    if pesquisa:
        df_estoque = df_estoque[df_estoque["Produto"].str.contains(pesquisa, case=False, na=False)]
    
    st.dataframe(df_estoque, use_container_width=True)

elif menu == "Gerenciar / Importar Estoque":
    st.header("⚙️ Gerenciamento e Importação de Medicamentos")
    
    tab1, tab2 = st.tabs(["📥 Importar Planilha CSV", "➕ Cadastrar Novo Produto"])
    
    with tab1:
        st.subheader("Importar Lista Completa (CSV)")
        st.markdown("Envie o seu arquivo CSV contendo as colunas de produtos para carregar todos os medicamentos de uma vez para o sistema da farmácia.")
        
        arquivo_csv = st.file_uploader("Escolha o arquivo CSV de estoque", type=["csv"])
        
        if arquivo_csv is not None:
            try:
                # Ler arquivo enviado pelo usuário
                df_upload = pd.read_csv(arquivo_csv, encoding='utf-8', sep=None, engine='python')
                
                st.write("Pré-visualização dos dados enviados:")
                st.dataframe(df_upload.head(), use_container_width=True)
                
                if st.button("Confirmar e Importar para o Estoque da Farmácia"):
                    # Normalizar colunas comuns
                    col_prod = next((c for c in df_upload.columns if 'desc' in c.lower() or 'prod' in c.lower() or 'nome' in c.lower()), df_upload.columns[0])
                    col_qtd = next((c for c in df_upload.columns if 'qtd' in c.lower() or 'quant' in c.lower()), df_upload.columns[1])
                    col_preco = next((c for c in df_upload.columns if 'pre' in c.lower() or 'valor' in c.lower()), df_upload.columns[2])
                    
                    nova_lista = []
                    for _, row in df_upload.iterrows():
                        nova_lista.append({
                            "Produto": str(row[col_prod]).strip().upper(),
                            "Quantidade": int(row[col_qtd]) if pd.notnull(row[col_qtd]) else 0,
                            "Preço": float(row[col_preco]) if pd.notnull(row[col_preco]) else 0.0
                        })
                    
                    st.session_state.estoque_produtos = nova_lista
                    st.success(f"Sucesso! {len(nova_lista)} medicamentos foram importados e carregados para o estoque!")
                    st.rerun()
            except Exception as e:
                st.error(f"Erro ao ler o arquivo CSV. Verifique o formato. Detalhes: {e}")
                
    with tab2:
        st.subheader("Cadastrar Produto Individual")
        with st.form("form_cad_manual"):
            novo_nome = st.text_input("Nome / Descrição do Medicamento")
            c_qtd = st.number_input("Quantidade em Estoque", min_value=0, value=10)
            c_preco = st.number_input("Preço de Venda (R$)", min_value=0.0, value=0.0, format="%.2f")
            
            cadastrar_btn = st.form_submit_button("Salvar no Estoque")
            
            if cadastrar_btn:
                if novo_nome and c_preco > 0:
                    st.session_state.estoque_produtos.append({
                        "Produto": novo_nome.strip().upper(),
                        "Quantidade": c_qtd,
                        "Preço": c_preco
                    })
                    st.success(f"Produto '{novo_nome}' cadastrado com sucesso!")
                    st.rerun()
                else:
                    st.warning("Preencha o nome do medicamento e um preço válido.")
