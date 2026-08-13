import json
import requests

# 1. Carrega o arquivo JSON com os dados tratados do inventário
with open('estoque_drogaria_max.json', 'r', encoding='utf-8') as f:
    inventario = json.load(f)

# 2. URL da API do seu aplicativo (substitua pela rota real do seu sistema)
API_URL = "https://seu-aplicativo.com/api/v1/estoque/atualizar"
HEADERS = {"Authorization": "Bearer SEU_TOKEN_DE_AUTENTICACAO"}

# 3. Loop para enviar cada grupo de estoque automaticamente
for item in inventario:
    payload = {
        "codigo_filial": "01",
        "codigo_grupo": item["Código"],
        "nome_grupo": item["Grupo"],
        "quantidade_itens": item["Itens"],
        "quantidade_unidades": item["Unidades"],
        "preco_custo": item["Custo"],
        "preco_venda": item["Venda"]
    }
    
    # Envia os dados para o app
    # resposta = requests.post(API_URL, json=payload, headers=HEADERS)
    # print(f"Grupo {item['Grupo']} sincronizado com sucesso!")
