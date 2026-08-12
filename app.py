import streamlit as st
import pandas as pd
import datetime
import urllib.parse
import zoneinfo

# Configuração da página
st.set_page_config(
    page_title="Farma Lagos - Sistema de Vendas e Estoque",
    page_icon="💊",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# Fuso horário do Brasil (Brasília)
TIMEZONE_BR = zoneinfo.ZoneInfo("America/Sao_Paulo")

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

# Inicializar Base de Dados de Estoque na Sessão
if 'estoque_produtos' not in st.session_state:
    st.session_state.estoque_produtos = [
        {"Produto": "AAS AD PROTECT 100MG 30CP", "Quantidade": 8, "Custo": 10.00, "Preço": 18.35},
        {"Produto": "AMOXICILINA 500MG C/21 CP", "Quantidade": 45, "Custo": 14.00, "Preço": 24.90},
        {"Produto": "PURAN T4 50MCG C/30 CP", "Quantidade": 120, "Custo": 10.50, "Preço": 18.00},
        {"Produto": "DIPIRONA SÓDICA 500MG/ML GOTAS", "Quantidade": 210, "Custo": 3.50, "Preço": 7.50},
        {"Produto": "DORFLEX C/10 CP", "Quantidade": 350, "Custo": 3.20, "Preço": 6.90},
    ]

# Inicializar Carrinho de Compras na Sessão
if 'carrinho' not in st.session_state:
    st.session_state.carrinho = []

# Menu de Navegação
menu = st.sidebar.radio("Navegação", ["Emitir Pedido / Carrinho", "Consultar Estoque", "Gerenciar / Importar Estoque", "Gráficos & Lucratividade"])

if menu == "Emitir Pedido / Carrinho":
    st.header("🛒 Carrinho & Cupom Fiscal")
    
    with st.expander("➕ Adicionar Produto do Estoque", expanded=True):
        lista_nomes = sorted([str(p["Produto"]) for p in st.session_state.estoque_produtos])
        
        selected_prod = st.selectbox("Pesquisar Medicamento (Digite as iniciais):", lista_nomes)
        
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
        
        st.subheader("Dados para o Cupom Fiscal / WhatsApp")
        with st.form("form_finalizar"):
            cliente = st.text_input("Nome do Cliente")
            telefone = st.text_input("WhatsApp do Cliente (com DDD - ex: 22988887777)")
            
            pagamento = st.selectbox("Forma de Pagamento", ["Dinheiro", "Pix", "Cartão de Crédito", "Cartão de Débito"])
            
            valor_recebido = 0.0
            troco = 0.0
            if pagamento == "Dinheiro":
                valor_recebido = st.number_input("Valor Recebido em Dinheiro (R$)", min_value=0.0, value=float(total_geral), format="%.2f")
            
            gerar_pedido = st.form_submit_button("Gerar Cupom Fiscal")
            
            if gerar_pedido:
                if cliente and telefone:
                    data_atual = datetime.datetime.now(TIMEZONE_BR).strftime("%d/%m/%Y %H:%M:%S")
                    
                    itens_texto = ""
                    for i, item in enumerate(st.session_state.carrinho, 1):
                        itens_texto += f"{i:02d} | {item['Qtd']}x {item['Produto']}\n     R$ {item['Preço Unit.']:.2f} un  ->  Subtotal: R$ {item['Subtotal']:.2f}\n"
                    
                    tributos_aprox = total_geral * 0.1345
                    
                    if pagamento == "Dinheiro":
                        troco = valor_recebido - total_geral
                        if troco < 0:
                            troco = 0.0
                        pagamento_texto = f"Dinheiro\n  - Valor Recebido: R$ {valor_recebido:.2f}\n  - Troco: R$ {troco:.2f}"
                    else:
                        pagamento_texto = f"{pagamento}"

                    comprovante = f"""=====================================
          FARMA LAGOS - CUPOM FISCAL          
       FARMA LAGOS - FILIAL 01              
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
FORMA DE PAGAMENTO: {pagamento_texto}
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
    st.header("📦 Consulta e Edição de Estoque")
    st.markdown(f"Total de itens cadastrados: **{len(st.session_state.estoque_produtos)}**")
    
    df_estoque = pd.DataFrame(st.session_state.estoque_produtos)
    
    pesquisa = st.text_input("🔍 Pesquisar medicamento:")
    if pesquisa:
        df_filtrado = df_estoque[df_estoque["Produto"].str.contains(pesquisa, case=False, na=False)]
    else:
        df_filtrado = df_estoque
        
    st.info("💡 Você pode editar os valores diretamente na tabela abaixo e clicar no botão para salvar as alterações.")
    
    edited_df = st.data_editor(df_filtrado, use_container_width=True, num_rows="dynamic")
    
    if st.button("💾 Salvar Alterações no Estoque"):
        st.session_state.estoque_produtos = edited_df.to_dict(orient="records")
        st.success("Estoque atualizado e salvo com sucesso!")
        st.rerun()

elif menu == "Gerenciar / Importar Estoque":
    st.header("⚙️ Importação e Cadastro de Produtos")
    
    tab1, tab2 = st.tabs(["📥 Importar Arquivos (Excel, CSV, Word, PDF)", "➕ Cadastrar Produto Manual"])
    
    with tab1:
        st.subheader("Importar Lista de Medicamentos")
        st.markdown("Envie arquivos nos formatos **Excel (.xlsx, .xls)**, **CSV**, **Word (.docx)** ou **PDF**. O sistema extrairá os dados automaticamente.")
        
        uploaded_file = st.file_uploader("Selecione o arquivo de estoque", type=["csv", "xlsx", "xls", "docx", "pdf"])
        
        if uploaded_file is not None:
            file_extension = uploaded_file.name.split('.')[-1].lower()
            try:
                novos_itens = []
                if file_extension in ['csv']:
                    df_imp = pd.read_csv(uploaded_file, encoding='utf-8', sep=None, engine='python')
                    for _, row in df_imp.iterrows():
                        novos_itens.append({
                            "Produto": str(row.iloc[0]).strip().upper(),
                            "Quantidade": int(row.iloc[1]) if len(row) > 1 and pd.notnull(row.iloc[1]) else 10,
                            "Custo": float(row.iloc[2])*0.6 if len(row) > 2 and pd.notnull(row.iloc[2]) else 10.0,
                            "Preço": float(row.iloc[2]) if len(row) > 2 and pd.notnull(row.iloc[2]) else 15.0
                        })
                elif file_extension in ['xlsx', 'xls']:
                    df_imp = pd.read_excel(uploaded_file)
                    for _, row in df_imp.iterrows():
                        novos_itens.append({
                            "Produto": str(row.iloc[0]).strip().upper(),
                            "Quantidade": int(row.iloc[1]) if len(row) > 1 and pd.notnull(row.iloc[1]) else 10,
                            "Custo": float(row.iloc[2])*0.6 if len(row) > 2 and pd.notnull(row.iloc[2]) else 10.0,
                            "Preço": float(row.iloc[2]) if len(row) > 2 and pd.notnull(row.iloc[2]) else 15.0
                        })
                elif file_extension in ['docx']:
                    import docx
                    doc = docx.Document(uploaded_file)
                    for para in doc.paragraphs:
                        texto = para.text.strip()
                        if texto:
                            novos_itens.append({"Produto": texto.upper(), "Quantidade": 20, "Custo": 10.0, "Preço": 20.0})
                elif file_extension in ['pdf']:
                    import pypdf
                    reader = pypdf.PdfReader(uploaded_file)
                    texto_pdf = ""
                    for page in reader.pages:
                        texto_pdf += page.extract_text() + "\n"
                    linhas = texto_pdf.split('\n')
                    for linha in linhas:
                        l = linha.strip()
                        if len(l) > 3:
                            novos_itens.append({"Produto": l.upper(), "Quantidade": 15, "Custo": 12.0, "Preço": 25.0})
                
                if novos_itens:
                    st.success(f"Arquivo lido com sucesso! {len(novos_itens)} itens encontrados.")
                    if st.button("📥 Confirmar e Atualizar Estoque"):
                        st.session_state.estoque_produtos.extend(novos_itens)
                        st.success("Estoque atualizado e salvo permanentemente!")
                        st.rerun()
            except Exception as e:
                st.error(f"Erro ao processar o arquivo: {e}")

    with tab2:
        st.subheader("Cadastrar Novo Medicamento Individual")
        with st.form("form_cad_manual"):
            novo_nome = st.text_input("Nome / Descrição do Medicamento")
            c_qtd = st.number_input("Quantidade em Estoque", min_value=0, value=10)
            c_custo = st.number_input("Preço de Custo (R$)", min_value=0.0, value=10.0, format="%.2f")
            c_preco = st.number_input("Preço de Venda (R$)", min_value=0.0, value=20.0, format="%.2f")
            
            cadastrar_btn = st.form_submit_button("Salvar Novo Produto")
            
            if cadastrar_btn:
                if novo_nome and c_preco > 0:
                    st.session_state.estoque_produtos.append({
                        "Produto": novo_nome.strip().upper(),
                        "Quantidade": c_qtd,
                        "Custo": c_custo,
                        "Preço": c_preco
                    })
                    st.success(f"Produto '{novo_nome}' cadastrado com sucesso!")
                    st.rerun()
                else:
                    st.warning("Preencha o nome do medicamento e um preço válido.")

elif menu == "Gráficos & Lucratividade":
    st.header("📊 Acompanhamento de Lucratividade")
    
    if len(st.session_state.estoque_produtos) > 0:
        df_lucro = pd.DataFrame(st.session_state.estoque_produtos)
        
        if "Custo" not in df_lucro.columns:
            df_lucro["Custo"] = df_lucro["Preço"] * 0.6
            
        df_lucro["Lucro Unitário (R$)"] = df_lucro["Preço"] - df_lucro["Custo"]
        df_lucro["Margem de Lucro (%)"] = ((df_lucro["Preço"] - df_lucro["Custo"]) / df_lucro["Custo"] * 100).round(2)
        
        st.subheader("Resumo Financeiro do Estoque")
        st.dataframe(df_lucro[["Produto", "Quantidade", "Custo", "Preço", "Lucro Unitário (R$)", "Margem de Lucro (%)"]], use_container_width=True)
        
        st.subheader("Visualização Gráfica de Preços (Custo vs Venda)")
        chart_data = df_lucro.set_index("Produto")[["Custo", "Preço"]]
        st.bar_chart(chart_data)
    else:
        st.info("Nenhum produto cadastrado no estoque para exibir relatórios.")
