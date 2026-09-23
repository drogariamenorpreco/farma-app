<!DOCTYPE html>
<html lang="pt-BR">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Farma Búzios - Gestão & Vendas</title>
    <!-- Tailwind CSS -->
    <script src="https://cdn.tailwindcss.com"></script>
    <!-- FontAwesome Icons -->
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
</head>
<body class="bg-slate-900 text-slate-100 min-h-screen">

    <!-- CABEÇALHO -->
    <header class="bg-slate-800 border-b border-slate-700 p-4 sticky top-0 z-50">
        <div class="max-w-md mx-auto flex justify-between items-center">
            <h1 class="text-xl font-bold text-sky-400 flex items-center gap-2">
                💊 Farma Búzios
            </h1>
            <div class="relative bg-slate-700 px-3 py-1 rounded-full text-sm font-semibold flex items-center gap-2">
                <i class="fa-solid fa-cart-shopping text-emerald-400"></i>
                <span id="cartBadge">0</span>
            </div>
        </div>
    </header>

    <main class="max-w-md mx-auto p-4 space-y-5">

        <!-- CAMPO DE PESQUISA COM LUPA -->
        <div class="bg-slate-800 p-4 rounded-xl border border-slate-700 space-y-3">
            <label class="block text-sm font-semibold text-slate-300">Buscar Medicamento:</label>
            <div class="relative">
                <i class="fa-solid fa-magnifying-glass absolute left-3 top-3.5 text-slate-400"></i>
                <input 
                    type="text" 
                    id="searchInput" 
                    oninput="buscarProduto()" 
                    placeholder="Digite o nome do medicamento..." 
                    class="w-full bg-slate-900 border border-slate-700 text-white rounded-lg pl-10 pr-3 py-2.5 focus:outline-none focus:border-sky-500 text-sm"
                />
            </div>

            <!-- RESULTADOS DA PESQUISA -->
            <div id="searchResults" class="space-y-2 max-h-48 overflow-y-auto hidden"></div>
        </div>

        <!-- FORMULÁRIO DE ADIÇÃO (PRODUTO SELECIONADO) -->
        <div id="selectedProdCard" class="bg-slate-800 p-4 rounded-xl border border-slate-700 space-y-3 hidden">
            <h3 id="selectedName" class="font-bold text-sky-300 text-sm"></h3>
            <div class="grid grid-cols-2 gap-3 text-xs">
                <div>
                    <label class="text-slate-400">Preço Final (R$):</label>
                    <input type="number" id="selectedPrice" step="0.01" class="w-full bg-slate-900 border border-slate-700 p-2 rounded text-white font-bold mt-1">
                </div>
                <div>
                    <label class="text-slate-400">Quantidade:</label>
                    <input type="number" id="selectedQty" value="1" min="1" class="w-full bg-slate-900 border border-slate-700 p-2 rounded text-white font-bold mt-1">
                </div>
            </div>
            <button onclick="confirmarAdicao()" class="w-full bg-emerald-600 hover:bg-emerald-500 text-white font-bold py-2.5 rounded-lg text-sm flex items-center justify-center gap-2">
                <i class="fa-solid fa-cart-plus"></i> Adicionar ao Carrinho
            </button>
        </div>

        <!-- CARRINHO ACUMULADO (MANTÉM TODOS OS MEDICAMENTOS) -->
        <div class="bg-slate-800 p-4 rounded-xl border border-slate-700 space-y-3">
            <h2 class="text-md font-bold text-slate-200 border-b border-slate-700 pb-2 flex justify-between items-center">
                <span>🛒 Carrinho de Compras</span>
                <span id="cartCountTotal" class="text-xs bg-slate-700 px-2 py-0.5 rounded text-emerald-400">0 itens</span>
            </h2>

            <div id="cartItemsList" class="space-y-2 max-h-56 overflow-y-auto">
                <p class="text-xs text-slate-400 text-center py-4">O carrinho está vazio.</p>
            </div>

            <div class="border-t border-slate-700 pt-3 space-y-2 text-sm">
                <div class="flex justify-between font-bold text-base">
                    <span>Total a Pagar:</span>
                    <span id="cartTotal" class="text-emerald-400">R$ 0,00</span>
                </div>
            </div>
        </div>

    </main>

    <script>
        // BASE DE DADOS SIMULADA
        const produtos = [
            { id: 1, nome: "ENTRESTO 49MG/51MG C/60 COMP", precoDe: 374.92, precoPor: 318.68 },
            { id: 2, nome: "DIPIRONA 500MG C/20 COMP", precoDe: 12.00, precoPor: 8.50 },
            { id: 3, nome: "DORFLEX C/36 COMP", precoDe: 28.00, precoPor: 22.90 },
            { id: 4, nome: "LOSARTANA POTÁSSICA 50MG C/30 COMP", precoDe: 15.00, precoPor: 9.90 },
            { id: 5, nome: "NEOSALDINA C/20 DRÁGEAS", precoDe: 32.00, precoPor: 26.50 }
        ];

        let carrinho = [];
        let produtoSelecionadoAtual = null;

        function buscarProduto() {
            const query = document.getElementById('searchInput').value.toLowerCase().trim();
            const resultsDiv = document.getElementById('searchResults');
            resultsDiv.innerHTML = '';

            if (!query) {
                resultsDiv.classList.add('hidden');
                return;
            }

            const filtrados = produtos.filter(p => p.nome.toLowerCase().includes(query));

            if (filtrados.length === 0) {
                resultsDiv.innerHTML = `<p class="text-xs text-slate-400 p-2">Nenhum medicamento encontrado.</p>`;
            } else {
                filtrados.forEach(p => {
                    const item = document.createElement('div');
                    item.className = "p-2 bg-slate-900 hover:bg-slate-700 rounded cursor-pointer text-xs flex justify-between items-center";
                    item.innerHTML = `
                        <span class="font-semibold text-slate-200">${p.nome}</span>
                        <span class="text-emerald-400 font-bold">R$ ${p.precoPor.toFixed(2)}</span>
                    `;
                    item.onclick = () => selecionarProduto(p);
                    resultsDiv.appendChild(item);
                });
            }

            resultsDiv.classList.remove('hidden');
        }

        function selecionarProduto(prod) {
            produtoSelecionadoAtual = prod;
            document.getElementById('searchResults').classList.add('hidden');
            document.getElementById('selectedName').innerText = prod.nome;
            document.getElementById('selectedPrice').value = prod.precoPor.toFixed(2);
            document.getElementById('selectedQty').value = 1;
            document.getElementById('selectedProdCard').classList.remove('hidden');
        }

        function confirmarAdicao() {
            if (!produtoSelecionadoAtual) return;

            const preco = parseFloat(document.getElementById('selectedPrice').value) || produtoSelecionadoAtual.precoPor;
            const qty = parseInt(document.getElementById('selectedQty').value) || 1;

            const itemExistente = carrinho.find(i => i.id === produtoSelecionadoAtual.id);
            if (itemExistente) {
                itemExistente.qty += qty;
                itemExistente.preco = preco;
            } else {
                carrinho.push({
                    id: produtoSelecionadoAtual.id,
                    nome: produtoSelecionadoAtual.nome,
                    precoDe: produtoSelecionadoAtual.precoDe,
                    preco: preco,
                    qty: qty
                });
            }

            // Ocultar card de seleção e limpar campo de busca
            document.getElementById('selectedProdCard').classList.add('hidden');
            document.getElementById('searchInput').value = '';
            produtoSelecionadoAtual = null;

            renderCarrinho();
        }

        function renderCarrinho() {
            const container = document.getElementById('cartItemsList');
            container.innerHTML = '';

            if (carrinho.length === 0) {
                container.innerHTML = `<p class="text-xs text-slate-400 text-center py-4">O carrinho está vazio.</p>`;
                document.getElementById('cartTotal').innerText = 'R$ 0,00';
                document.getElementById('cartBadge').innerText = '0';
                document.getElementById('cartCountTotal').innerText = '0 itens';
                return;
            }

            let totalGeral = 0;
            let totalQtd = 0;

            carrinho.forEach((item, index) => {
                const subtotal = item.preco * item.qty;
                totalGeral += subtotal;
                totalQtd += item.qty;

                const div = document.createElement('div');
                div.className = "p-2.5 bg-slate-900 rounded-lg flex justify-between items-center text-xs";
                div.innerHTML = `
                    <div>
                        <p class="font-bold text-slate-200">${item.nome}</p>
                        <p class="text-[11px] text-slate-400">
                            ${item.qty}x R$ ${item.preco.toFixed(2)} = <strong class="text-emerald-400">R$ ${subtotal.toFixed(2)}</strong>
                        </p>
                    </div>
                    <button onclick="removerItem(${index})" class="text-red-400 hover:text-red-300 p-1">
                        <i class="fa-solid fa-trash"></i>
                    </button>
                `;
                container.appendChild(div);
            });

            document.getElementById('cartTotal').innerText = `R$ ${totalGeral.toFixed(2)}`;
            document.getElementById('cartBadge').innerText = totalQtd;
            document.getElementById('cartCountTotal').innerText = `${totalQtd} itens`;
        }

        function removerItem(index) {
            carrinho.splice(index, 1);
            renderCarrinho();
        }
    </script>
</body>
</html>
