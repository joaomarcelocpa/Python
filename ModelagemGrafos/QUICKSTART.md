# 🚀 Quick Start Guide - GitHub Graph Analyzer

Guia rápido para começar a usar o GitHub Repository Graph Analyzer em minutos!

---

## 📋 Pré-requisitos

- **Python 3.8+** instalado
- **Git** instalado
- Conta no GitHub (para gerar token)
- Sistema operacional: Windows, Linux ou macOS

---

## ⚡ Instalação Rápida

### 1. Clone o Repositório

```bash
git clone https://github.com/seu-usuario/trabalho_academico_grafos.git
cd ModelagemGrafos
```

### 2. Crie um Ambiente Virtual (Recomendado)

**Windows:**
```bash
python -m venv venv
venv\Scripts\activate
```

**Linux/macOS:**
```bash
python3 -m venv venv
source venv/bin/activate
```

### 3. Instale as Dependências

```bash
pip install -r requirements.txt
```

### 4. Configure seu Token do GitHub

#### Gerar Token:
1. Acesse: https://github.com/settings/tokens
2. Clique em "Generate new token" → "Generate new token (classic)"
3. Dê um nome (ex: "Graph Analyzer")
4. Selecione os escopos:
   - ✅ `repo` (acesso completo a repositórios)
   - ✅ `read:org` (ler dados da organização)
5. Clique em "Generate token"
6. **COPIE O TOKEN** (você não verá novamente!)

#### Configurar Token:
Crie um arquivo `.env` na raiz do projeto:

```bash
# Windows
echo GITHUB_TOKEN=seu_token_aqui > .env

# Linux/macOS
echo "GITHUB_TOKEN=seu_token_aqui" > .env
```

Ou edite manualmente:
```env
# .env
GITHUB_TOKEN=ghp_seu_token_aqui_1234567890
REPO_OWNER=major
REPO_NAME=MySQLTuner-perl
```

---

## 🎯 Uso Básico

### Opção 1: Interface Gráfica (Recomendado)

```bash
python app.py
```

Ou:

```bash
python gui.py
```

**Ambos abrem a mesma interface moderna!**

### Opção 2: Linha de Comando

```bash
python main.py
```

---

## 📊 Primeiro Uso - Passo a Passo

### Interface Gráfica

#### 1️⃣ Configuração Inicial

Ao abrir a aplicação, você verá:

```
╔════════════════════════════════════════╗
║  GitHub Graph Analyzer v2.0            ║
║  Modern Edition                         ║
╚════════════════════════════════════════╝

[Configuração]
┌──────────────────────────────────────┐
│ Owner: major                         │
│ Repo:  MySQLTuner-perl              │
│ Token: ●●●●●●●●●●●●                  │
└──────────────────────────────────────┘
```

- Se quiser analisar outro repositório, altere os campos
- Clique em "💾 Salvar Configuração"

#### 2️⃣ Extrair Dados

1. Clique no botão **"📥 Extrair Dados"** na barra lateral
2. Aguarde a coleta (pode demorar alguns minutos)
3. Você verá o progresso no console:
   ```
   [10:30:45] Extraindo dados do GitHub...
   [10:30:46] ✓ Informações do repositório
   [10:30:50] ✓ Issues (1234 encontradas)
   [10:31:20] ✓ Pull Requests (567 encontrados)
   [10:32:10] ✓ Comentários...
   [10:33:00] [OK] Dados salvos em: data/raw/
   ```

#### 3️⃣ Construir Grafos

1. Clique no botão **"🔨 Construir Grafos"**
2. Aguarde o processamento
3. 4 grafos serão criados:
   - 📊 **Grafo 1:** Comentários em Issues/PRs
   - 📊 **Grafo 2:** Fechamento de Issues
   - 📊 **Grafo 3:** Reviews e Merges
   - 📊 **Grafo 4:** Grafo Integrado (com pesos)

#### 4️⃣ Visualizar Grafos

1. Clique no botão **"📊 Visualizar"**
2. Uma nova janela se abrirá
3. Selecione um grafo (ex: Grafo 1)
4. Clique em **"🎨 Visualizar Grafo"**
5. Use os controles:
   - **Scroll do mouse:** Zoom in/out
   - **Botão Pan (🔀):** Arrastar para mover
   - **Botão Zoom (🔍):** Selecionar área
   - **Botão Home (🏠):** Resetar visualização

#### 5️⃣ Exportar Resultados

- **Exportar Imagem:** Clique em "💾 Exportar Imagem" na janela de visualização
- **Salvar Dados:** Os grafos já foram salvos em `output/gephi/*.gexf`

---

## 🎨 Recursos Disponíveis

### 1. Extração de Dados
- ✅ Issues e Pull Requests
- ✅ Comentários (issues e PRs)
- ✅ Reviews de código
- ✅ Informações de fechamento
- ✅ Histórico completo de interações

### 2. Construção de Grafos
- 📊 **Grafo 1 - Comentários:** Quem comenta em issues/PRs de quem
- 📊 **Grafo 2 - Fechamentos:** Quem fecha issues de quem
- 📊 **Grafo 3 - Reviews:** Quem revisa PRs de quem
- 📊 **Grafo 4 - Integrado:** Todos os tipos com pesos diferentes

### 3. Visualização Interativa
- 🔍 **Zoom:** Scroll do mouse ou ferramenta de zoom
- 🔀 **Pan:** Mover o grafo livremente
- 🏠 **Reset:** Voltar à visualização inicial
- ⬅️➡️ **Navegação:** Histórico de zoom/pan
- 💾 **Exportação:** PNG, PDF ou SVG

### 4. Análise de Métricas (Em Desenvolvimento)
- Centralidade (PageRank, Betweenness, Degree)
- Detecção de Comunidades
- Estrutura da Rede (Densidade, Clustering)

---

## 📁 Estrutura de Arquivos

Após executar, você terá:

```
trabalho_academico_grafos/
├── data/
│   ├── raw/                    # Dados brutos da API
│   │   ├── issues_*.json
│   │   ├── pull_requests_*.json
│   │   └── ...
│   ├── processed/              # Dados processados
│   └── graphs/                 # Dados dos grafos
├── output/
│   ├── gephi/                  # Arquivos GEXF
│   │   ├── graph_1_comments.gexf
│   │   ├── graph_2_closures.gexf
│   │   ├── graph_3_reviews.gexf
│   │   └── graph_4_integrated.gexf
│   ├── matrices/               # Matrizes de adjacência
│   ├── visualizations/         # Imagens exportadas
│   └── reports/                # Relatórios gerados
└── logs/                       # Arquivos de log
    └── graph_analyzer.log
```

---

## 🔧 Configurações Avançadas

### Arquivo .env Completo

```env
# API do GitHub
GITHUB_TOKEN=ghp_seu_token_aqui
REPO_OWNER=owner_do_repositorio
REPO_NAME=nome_do_repositorio

# Diretórios (opcional - usa padrões se não especificado)
DATA_DIR=data
OUTPUT_DIR=output

# Coleta de Dados
FETCH_ALL_ISSUES=true
FETCH_ALL_PRS=true
FETCH_COMMENTS=true
FETCH_REVIEWS=true

# Rate Limiting
RATE_LIMIT_WAIT=true
REQUEST_DELAY_SECONDS=0.5

# Pesos das Interações (Grafo 4)
WEIGHT_COMMENT=2
WEIGHT_ISSUE_OPENED=3
WEIGHT_REVIEW=4
WEIGHT_MERGE=5
```

---

## 🐛 Problemas Comuns

### Erro: "GITHUB_TOKEN não configurado"

**Solução:**
```bash
# Verifique se o arquivo .env existe
cat .env  # Linux/macOS
type .env # Windows

# Se não existir, crie:
echo "GITHUB_TOKEN=seu_token_aqui" > .env
```

### Erro: "Rate limit exceeded"

**Problema:** Muitas requisições à API do GitHub

**Soluções:**
1. Configure um token válido (aumenta limite de 60 para 5000 req/hora)
2. Aguarde 1 hora para resetar o limite
3. Use `RATE_LIMIT_WAIT=true` no .env (já é padrão)

### Erro: "Module not found"

**Solução:**
```bash
# Reinstale as dependências
pip install -r requirements.txt

# Verifique se está no ambiente virtual correto
# Windows:
venv\Scripts\activate

# Linux/macOS:
source venv/bin/activate
```

### Visualização muito lenta

**Soluções:**
1. ✅ Desative "Mostrar labels dos nós"
2. ✅ Desative "Mostrar pesos das arestas"
3. ✅ Use um repositório menor para testes
4. ✅ Feche outras aplicações para liberar memória

### Erro: "Arquivo GEXF não encontrado"

**Causa:** Grafos não foram construídos ainda

**Solução:**
1. Clique em "📥 Extrair Dados" primeiro
2. Depois clique em "🔨 Construir Grafos"
3. Só então abra "📊 Visualizar"

---

## 💡 Dicas e Truques

### 1. Análise de Repositório Grande

Para repositórios com muitos issues/PRs:

1. **Primeira vez:** Execute em horários de menos uso
2. **Performance:** Desative labels na visualização
3. **Memória:** Feche outras aplicações
4. **Paciência:** Pode levar 10-30 minutos para repositórios grandes

### 2. Exportação de Dados

Os arquivos GEXF podem ser abertos em:
- **Gephi** (software de visualização profissional)
- **Cytoscape** (análise de redes complexas)
- **NetworkX** (Python)

### 3. Atalhos Úteis

| Ação | Atalho |
|------|--------|
| Zoom In | Scroll ⬆️ |
| Zoom Out | Scroll ⬇️ |
| Pan | Botão Pan + Arrastar |
| Reset | Botão Home |

### 4. Melhores Práticas

✅ **DO:**
- Configure o token do GitHub antes de começar
- Extraia dados em horários de menos uso
- Salve configurações antes de fechar
- Use visualização interativa para explorar

❌ **DON'T:**
- Não compartilhe seu token do GitHub
- Não execute extração múltiplas vezes seguidas (rate limit!)
- Não tente visualizar grafos com 10000+ nós sem desativar labels

---

## 📚 Próximos Passos

Após dominar o básico, explore:

1. **Análise de Métricas** (em desenvolvimento)
   - Identificar colaboradores chave
   - Detectar comunidades
   - Analisar estrutura da rede

2. **Comparação de Repositórios**
   - Analise múltiplos repos
   - Compare estruturas de colaboração
   - Identifique padrões

3. **Exportação Avançada**
   - Gere relatórios em PDF
   - Exporte dados para análise estatística
   - Crie apresentações

4. **Documentação Completa**
   - Leia `README.md` para detalhes técnicos
   - Veja `ANALISE_CODIGO_PROBLEMAS.md` para arquitetura
   - Confira `MELHORIAS_VISUALIZACAO.md` para recursos de UI

---

## 🆘 Precisa de Ajuda?

### Documentação
- 📖 **README.md** - Documentação completa
- 🐛 **ANALISE_CODIGO_PROBLEMAS.md** - Problemas conhecidos
- 🎨 **MELHORIAS_VISUALIZACAO.md** - Guia de visualização
- ✅ **CORRECOES_REALIZADAS.md** - Histórico de correções

### Logs
Verifique os logs para diagnóstico:
```bash
# Windows
type logs\graph_analyzer.log

# Linux/macOS
cat logs/graph_analyzer.log
```

### Suporte
- 📧 Email: [seu-email]
- 🐛 Issues: https://github.com/[seu-repo]/issues
- 📝 Discussões: https://github.com/[seu-repo]/discussions

---

## 🎓 Exemplo Completo

Vamos analisar o repositório **MySQLTuner-perl** do início ao fim:

```bash
# 1. Ativar ambiente virtual
venv\Scripts\activate  # Windows
source venv/bin/activate  # Linux/macOS

# 2. Configurar .env
echo "GITHUB_TOKEN=ghp_seu_token" > .env
echo "REPO_OWNER=major" >> .env
echo "REPO_NAME=MySQLTuner-perl" >> .env

# 3. Executar aplicação
python app.py

# 4. Na GUI:
# - Clique em "📥 Extrair Dados" (aguarde ~5-10 min)
# - Clique em "🔨 Construir Grafos" (aguarde ~1-2 min)
# - Clique em "📊 Visualizar"
# - Selecione "Grafo 1: Comentários"
# - Clique em "🎨 Visualizar Grafo"
# - Use scroll do mouse para zoom!
# - Clique em botão Pan para mover o grafo
# - Clique em "💾 Exportar Imagem" para salvar

# 5. Resultado:
# - Grafos salvos em: output/gephi/
# - Imagens em: output/visualizations/
# - Dados em: data/
```

---

## ✨ Recursos Futuros

🚧 **Em Desenvolvimento:**
- [ ] Análise de métricas de rede
- [ ] Detecção automática de comunidades
- [ ] Comparação entre múltiplos repositórios
- [ ] Exportação de relatórios em PDF
- [ ] Dashboard web interativo
- [ ] API REST para integração

---

## 🎉 Pronto para Começar!

Agora você está pronto para analisar redes de colaboração no GitHub!

```bash
# Comando mágico ✨
python app.py
```

**Boa análise! 🚀**

---

**Última atualização:** 2025-11-23
**Versão:** 2.0
**Licença:** MIT
