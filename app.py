import streamlit as st
import pandas as pd
import urllib.parse
import re
from datetime import datetime

st.set_page_config(page_title="FARMA BÚZIOS - PDV & Gestão", page_icon="💊", layout="centered")

# ==============================================================================
# 1. MEMÓRIA PERSISTENTE DO SISTEMA (SESSÃO & HISTÓRICO & CLIENTES)
# ==============================================================================
if "carrinho" not in st.session_state:
    st.session_state.carrinho = []

if "historico_vendas" not in st.session_state:
    st.session_state.historico_vendas = []

if "base_clientes" not in st.session_state:
    st.session_state.base_clientes = {}  # Formato: { "whatsapp": {"nome": "...", "endereco": "..."} }

# ==============================================================================
# 2. CARREGAMENTO DO ESTOQUE INICIAL
# ==============================================================================
@st.cache_data
def carregar_estoque_inicial():
    arquivos_possiveis = ["estoque_drogaria (1).csv", "estoque_drogaria.csv", "estoque.csv"]
    for arq in arquivos_possiveis:
        try:
            df = pd.read_csv(arq)
            df.columns = ['nome', 'estoque', 'preco']
            df['nome'] = df['nome'].astype(str).str.strip()
            df['estoque'] = pd.to_numeric(df['estoque'], errors='coerce').fillna(0).astype(int)
            df['preco'] = pd.to_numeric(df['preco'], errors='coerce').fillna(0.0)
            return df
        except Exception:
            continue

    return pd.DataFrame([
        {"nome": "FORXIGA 10MG 30CP", "estoque": 1, "preco": 134.11},
        {"nome": "AMOXICILINA 500MG C/21 CAPS", "estoque": 35, "preco": 18.90},
        {"nome": "DIPIRONA 500MG C/20 COMP", "estoque": 100, "preco": 8.50}
    ])

if "base_produtos" not in st.session_state:
    st.session_state.base_produtos = carregar_estoque_inicial()

# ==============================================================================
# 3. NAVEGAÇÃO POR ABAS
# ==============================================================================
st.title("💊 FARMA BÚZIOS")
aba1, aba2, aba3, aba4 = st.tabs(["🛒 PDV / Vendas", "➕ Cadastrar Produto", "👥 Clientes", "📜 Histórico"])

# ------------------------------------------------------------------------------
# ABA 1: PDV / VENDAS
# ------------------------------------------------------------------------------
with aba1:
    st.subheader("🔍 Buscar e Selecionar Produto")

    termo_busca = st.text_input("Digite o nome do produto:", placeholder="Ex: Forxiga, Amoxicilina, Dipirona...")

    df_estoque = st.session_state.base_produtos

    if termo_busca:
        df_filtrado = df_estoque[df_estoque['nome'].str.contains(termo_busca, case=False, na=False)]
    else:
        df_filtrado = df_estoque

    lista_produtos = df_filtrado['nome'].tolist()

    if not lista_produtos:
        st.warning("Nenhum produto encontrado com essa pesquisa.")
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
                format="%.2f",
                key="venda_preco"
            )

        with col_qtd:
            quantidade = st.number_input("Quantidade:", min_value=1, max_value=int(max(1, dados_prod['estoque'])), value=1, step=1, key="venda_qtd")

        preco_de_item = preco_final / 0.80
        st.caption(f"🏷️ **Preço De:** ~R$ {preco_de_item:.2f}~ ➔ **Por:** R$ {preco_final:.2f} (20% OFF) | Estoque: **{dados_prod['estoque']} un.**")

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

    st.subheader("🛒 Itens no Carrinho de Compras")

    if len(st.session_state.carrinho) == 0:
        st.info("O carrinho está vazio.")
    else:
        subtotal_geral = 0.0
        total_desconto_geral = 0.0
        
        for idx, item in enumerate(st.session_state.carrinho):
            total_item = item["preco"] * item["qtd"]
            subtotal_geral += total_item
            preco_de = item["preco"] / 0.80
            economia_item = (preco_de - item["preco"]) * item["qtd"]
            total_desconto_geral += economia_item
            
            c1, c2, c3 = st.columns([3, 1.5, 0.5])
            with c1:
                st.markdown(f"**{item['qtd']}x {item['nome']}**")
                st.caption(f"De: ~R$ {preco_de:.2f}~ por **R$ {item['preco']:.2f} un.**")
            with c2:
                st.markdown(f"**R$ {total_item:.2f}**")
            with c3:
                if st.button("🗑️", key=f"remover_{idx}"):
                    st.session_state.carrinho.pop(idx)
                    st.rerun()
            st.divider()

        # DADOS DE ENTREGA E CLIENTE COM BUSCA AUTOMÁTICA POR TELEFONE
        add_taxa = st.checkbox("🚚 Adicionar taxa de entrega?")
        taxa_entrega = 0.0
        if add_taxa:
            taxa_entrega = st.number_input("Valor da Taxa (R$):", min_value=0.0, value=5.00, step=1.00)

        st.markdown("### 👤 Dados do Cliente")
        whatsapp_input = st.text_input("WhatsApp (Digite o número para buscar cliente salvo):", placeholder="Ex: 24981279222")

        # Limpar número para busca
        tel_limpo = re.sub(r'\D', '', whatsapp_input)
        
        # Verificar se já existe cadastrado na base
        cliente_encontrado = st.session_state.base_clientes.get(tel_limpo, {"nome": "", "endereco": ""})

        nome_cliente = st.text_input("Nome do Cliente:", value=cliente_encontrado["nome"], placeholder="Ex: Claudinei")
        endereco_cliente = st.text_area("Endereço Completo de Entrega:", value=cliente_encontrado["endereco"], placeholder="Rua, Número, Bairro, Ponto de Referência...")

        valor_total_final = subtotal_geral + taxa_entrega
        st.markdown(f"### **TOTAL DO PEDIDO: R$ {valor_total_final:.2f}**")
        st.markdown(f"🎉 **Economia Total do Cliente: R$ {total_desconto_geral:.2f}**")

        if st.button("✅ GERAR NOTA E FINALIZAR PEDIDO", use_container_width=True):
            agora = datetime.now()
            data_formatada = agora.strftime("%d/%m/%Y")
            hora_formatada = agora.strftime("%H:%M:%S")

            # Salvar automaticamente cliente na base de clientes
            if tel_limpo and nome_cliente.strip():
                st.session_state.base_clientes[tel_limpo] = {
                    "nome": nome_cliente.strip().upper(),
                    "endereco": endereco_cliente.strip()
                }

            # Salvar no Histórico de Vendas
            itens_comprados_str = ", ".join([f"{i['qtd']}x {i['nome']} (R$ {i['preco']:.2f} un.)" for i in st.session_state.carrinho])
            
            registro_venda = {
                "Data": data_formatada,
                "Hora": hora_formatada,
                "Cliente": nome_cliente.strip() if nome_cliente.strip() else "Cliente Não Informado",
                "WhatsApp": whatsapp_input.strip(),
                "Endereço": endereco_cliente.strip(),
                "Itens": itens_comprados_str,
                "Subtotal (R$)": f"{subtotal_geral:.2f}",
                "Taxa Entrega (R$)": f"{taxa_entrega:.2f}",
                "Economia (R$)": f"{total_desconto_geral:.2f}",
                "Total Pago (R$)": f"{valor_total_final:.2f}"
            }
            
            st.session_state.historico_vendas.append(registro_venda)
            st.success("✅ Pedido finalizado, cliente salvo e registrado no histórico!")

            # Montar comprovante formatado
            resumo = "*FARMA BÚZIOS*\n-------------------\n"
            resumo += f"📅 *Data:* {data_formatada} às {hora_formatada}\n"
            resumo += f"👤 *Cliente:* {nome_cliente if nome_cliente else 'Cliente'}\n"
            if endereco_cliente.strip():
                resumo += f"📍 *Endereço:* {endereco_cliente.strip()}\n"
            resumo += "-------------------\n*ITENS DO PEDIDO:*\n"
            
            for i in st.session_state.carrinho:
                preco_unit = i['preco']
                preco_de_unit = preco_unit / 0.80
                total_item_venda = preco_unit * i['qtd']
                resumo += f"• {i['qtd']}x {i['nome']} = De ~R$ {preco_de_unit:.2f}~ por *R$ {preco_unit:.2f}* (Total: *R$ {total_item_venda:.2f}*)\n"
            
            if taxa_entrega > 0:
                resumo += f"🛵 *Taxa de Entrega:* R$ {taxa_entrega:.2f}\n"
                
            resumo += f"-------------------\n*TOTAL A PAGAR: R$ {valor_total_final:.2f}*\n"
            resumo += f"🎉 *VOCÊ ECONOMIZOU: R$ {total_desconto_geral:.2f}*"
            
            st.text_area("Comprovante WhatsApp:", value=resumo, height=250)

            # Link direto do WhatsApp
            num_envio = tel_limpo
            if num_envio:
                if len(num_envio) in [10, 11]:
                    num_envio = "55" + num_envio
                
                msg_encoded = urllib.parse.quote(resumo)
                link_whatsapp = f"https://wa.me/{num_envio}?text={msg_encoded}"
                
                st.markdown(f'<a href="{link_whatsapp}" target="_blank" style="text-decoration: none;"><div style="background-color: #25D366; color: white; padding: 12px; border-radius: 8px; text-align: center; font-weight: bold; font-size: 16px; margin-top: 10px;">📲 Abrir e Enviar Pedido no WhatsApp</div></a>', unsafe_allow_html=True)
            else:
                st.info("💡 Digite o número do WhatsApp acima para habilitar o botão de envio direto.")

        st.divider()
        if st.button("🧹 Limpar Carrinho (Novo Pedido)", use_container_width=True):
            st.session_state.carrinho = []
            st.rerun()

# ------------------------------------------------------------------------------
# ABA 2: CADASTRAR PRODUTO MANUALMENTE
# ------------------------------------------------------------------------------
with aba2:
    st.subheader("📝 Cadastrar Novo Produto")
    
    with st.form("form_novo_produto", clear_on_submit=True):
        novo_nome = st.text_input("Nome / Descrição do Produto:")
        c_preco, c_estoque = st.columns(2)
        
        with c_preco:
            novo_preco = st.number_input("Preço de Venda (R$):", min_value=0.0, value=0.0, format="%.2f")
        with c_estoque:
            novo_estoque = st.number_input("Estoque Inicial:", min_value=1, value=10, step=1)
            
        btn_salvar = st.form_submit_button("💾 Salvar e Cadastrar Produto", use_container_width=True)
        
        if btn_salvar:
            if not novo_nome.strip():
                st.error("Por favor, digite o nome do produto.")
            else:
                novo_item = pd.DataFrame([{
                    "nome": novo_nome.strip().upper(),
                    "estoque": int(novo_estoque),
                    "preco": float(novo_preco)
                }])
                
                st.session_state.base_produtos = pd.concat([novo_item, st.session_state.base_produtos], ignore_index=True)
                st.success(f"🎉 **{novo_nome.strip().upper()}** cadastrado com sucesso e salvo no sistema!")

# ------------------------------------------------------------------------------
# ABA 3: CLIENTES CADASTRADOS
# ------------------------------------------------------------------------------
with aba3:
    st.subheader("👥 Clientes Cadastrados no Sistema")
    
    if len(st.session_state.base_clientes) == 0:
        st.info("Nenhum cliente cadastrado ainda. Os clientes são salvos automaticamente ao finalizar um pedido!")
    else:
        lista_cli_exibicao = []
        for tel, dados in st.session_state.base_clientes.items():
            lista_cli_exibicao.append({
                "WhatsApp": tel,
                "Nome": dados["nome"],
                "Endereço": dados["endereco"]
            })
        
        df_clientes = pd.DataFrame(lista_cli_exibicao)
        st.dataframe(df_clientes, use_container_width=True)
        
        st.markdown("### ✏️ Cadastrar ou Atualizar Cliente Manualmente")
        with st.form("form_cliente_manual"):
            m_tel = st.text_input("WhatsApp (com DDD):")
            m_nome = st.text_input("Nome do Cliente:")
            m_end = st.text_area("Endereço Completo:")
            btn_salvar_cli = st.form_submit_button("💾 Salvar Cliente", use_container_width=True)
            
            if btn_salvar_cli:
                t_limpo = re.sub(r'\D', '', m_tel)
                if t_limpo and m_nome.strip():
                    st.session_state.base_clientes[t_limpo] = {
                        "nome": m_nome.strip().upper(),
                        "endereco": m_end.strip()
                    }
                    st.success(f"✅ Cliente {m_nome.strip().upper()} salvo com sucesso!")
                    st.rerun()
                else:
                    st.error("Preencha o WhatsApp e o Nome do cliente.")

# ------------------------------------------------------------------------------
# ABA 4: HISTÓRICO DE VENDAS
# ------------------------------------------------------------------------------
with aba4:
    st.subheader("📜 Histórico de Compras e Vendas")
    
    if len(st.session_state.historico_vendas) == 0:
        st.info("Nenhuma venda registrada até o momento.")
    else:
        df_hist = pd.DataFrame(st.session_state.historico_vendas)
        
        st.dataframe(df_hist, use_container_width=True)
        
        csv_hist = df_hist.to_csv(index=False).encode('utf-8')
        st.download_button(
            label="📥 Baixar Histórico Completo em CSV",
            data=csv_hist,
            file_name="historico_vendas_farma_buzios.csv",
            mime="text/csv",
            use_container_width=True
        )
