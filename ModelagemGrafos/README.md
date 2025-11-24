# GitHub Repository Graph Analyzer

Projeto para coleta, extração e construção de grafos de colaboração a partir de repositórios GitHub.

## 📋 Descrição

Este projeto extrai dados de um repositório GitHub, identifica nós (usuários) e arestas (interações), e constrói grafos de colaboração usando uma biblioteca própria desenvolvida em Python. Os grafos podem ser exportados em formato GEXF para visualização no GEPHI.

### Grafos Modelados:

- **Grafo 1**: Comentários em issues ou pull requests
  - Nós: usuários
  - Arestas: autor do comentário → autor da issue/PR
  - Grafo simples e direcionado

- **Grafo 2**: Fechamento de issues por outros usuários
  - Nós: usuários
  - Arestas: quem fechou → autor da issue
  - Grafo simples e direcionado

- **Grafo 3**: Reviews, aprovações e merges de pull requests
  - Nós: usuários
  - Arestas: reviewer/merger → autor do PR
  - Grafo simples e direcionado

- **Grafo Integrado**: Combinação ponderada de todas as interações
  - Nós: usuários
  - Arestas com pesos conforme tipo de interação
  - Para relações bidirecionais, usar arestas anti-paralelas

## 🎨 Interface Gráfica

O projeto agora inclui uma **interface gráfica moderna** desenvolvida com CustomTkinter!

### ✨ Nova Arquitetura v2.0

O sistema foi completamente refatorado com **Clean Architecture**:
- 🏗️ **Service Layer**: Lógica de negócio isolada e reutilizável
- 🧩 **Componentes modulares**: GUI dividida em componentes independentes
- 🔧 **Design Patterns**: Command, Observer, Dependency Injection
- ✅ **Alta testabilidade**: Serviços podem ser testados isoladamente
- 📦 **Baixo acoplamento**: Componentes comunicam-se via interfaces

📖 **[Documentação da Nova Arquitetura](NOVA_ARQUITETURA.md)**

### Recursos da GUI:
- ✅ Interface moderna e intuitiva
- ✅ Tema Dark/Light
- ✅ Extração de dados com um clique
- ✅ Console de logs em tempo real
- ✅ Barra de progresso
- ✅ Configuração visual do repositório
- ✅ Escolha entre Lista ou Matriz de Adjacência
- ✅ Status dos dados em tempo real
- ✅ **Visualização integrada de grafos** (novo!)
- ✅ **Gerenciamento de dados com limpeza** (novo!)
- ✅ **Exportação de imagens** (novo!)

### Como usar:

**Aplicação Principal (Nova Arquitetura):**
```bash
python app.py
```

**Versão Legacy (Referência):**
```bash
python gui.py
```

**Windows (Legacy):**
```bash
launch_gui.bat
```

📖 **[Documentação completa da GUI](GUI_README.md)**

## 📁 Estrutura do Projeto

```
trabalho_academico_grafos/
├── README.md                    # Documentação do projeto
├── NOVA_ARQUITETURA.md          # 🆕 Documentação da nova arquitetura
├── GUI_README.md                # Documentação da interface gráfica
├── requirements.txt             # Dependências Python
├── .env.example                 # Exemplo de arquivo de configuração
├── config.py                    # Configurações do projeto
├── app.py                       # 🆕 Entry point principal (Nova Arquitetura)
├── gui.py                       # Interface gráfica legacy (referência)
├── main.py                      # Script principal CLI
├── launch_gui.bat               # Lançador da GUI (Windows)
├── src/                         # Código fonte
│   ├── __init__.py
│   ├── github_api.py           # Cliente da API do GitHub
│   ├── graph_data_extractor.py # Extrator de nós e arestas
│   ├── data_processor.py       # Processador de dados raw
│   ├── graph_builder.py        # Construtor de grafos
│   │
│   ├── services/               # 🆕 SERVICE LAYER
│   │   ├── __init__.py
│   │   ├── extraction_service.py        # Serviço de extração
│   │   ├── graph_generation_service.py  # Serviço de geração de grafos
│   │   └── file_cleanup_service.py      # Serviço de limpeza
│   │
│   ├── gui/                    # 🆕 GUI MODULAR
│   │   ├── __init__.py
│   │   ├── main_window.py             # Janela principal
│   │   ├── components/                # Componentes reutilizáveis
│   │   │   ├── sidebar.py            # Barra lateral
│   │   │   ├── config_panel.py       # Painel de configuração
│   │   │   └── console_panel.py      # Console de saída
│   │   ├── windows/                   # Janelas secundárias
│   │   │   └── visualization_window.py # Visualização de grafos
│   │   └── utils/                     # Utilitários
│   │       ├── text_redirector.py    # Redirecionamento de stdout
│   │       └── dialog_helper.py      # Helpers para diálogos
│   │
│   └── graph/                  # Implementações de grafos
│       ├── abstract_graph.py   # Classe abstrata base
│       ├── adjacency_list_graph.py   # Lista de adjacência
│       ├── adjacency_matrix_graph.py # Matriz de adjacência
│       └── exporters/          # Exportadores
│           └── gephi_exporter.py # Exportador GEXF
│
├── data/                        # Dados coletados (gitignored)
│   ├── raw/                    # Dados brutos da API
│   ├── processed/              # Dados processados
│   └── graphs/                 # Dados dos grafos (nós e arestas)
└── output/                      # Resultados finais
    ├── gephi/                  # Arquivos GEXF para visualização
    └── reports/                # Relatórios de análise
```

## 🚀 Instalação

### Pré-requisitos

- Python 3.12+
- Git
- Token de acesso pessoal do GitHub (recomendado)

### Passo a Passo

1. Clone o repositório:
```bash
git clone <seu-repositorio>
cd github_analysis_project
```

2. Crie um ambiente virtual:
```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
# ou
venv\Scripts\activate     # Windows
```

3. Instale as dependências:
```bash
pip install -r requirements.txt
```

4. Configure as variáveis de ambiente:
```bash
cp .env.example .env
# Edite o arquivo .env com suas configurações
```

## 🔑 Configuração do Token GitHub

Para evitar limitações de rate limit da API do GitHub, é recomendado usar um token de acesso pessoal:

1. Acesse: https://github.com/settings/tokens
2. Clique em "Generate new token" → "Generate new token (classic)"
3. Selecione os escopos: `public_repo`, `read:user`
4. Copie o token gerado
5. Adicione ao arquivo `.env`:
```
GITHUB_TOKEN=seu_token_aqui
```

## 💻 Uso

### Modo Interativo (Recomendado)

Execute o script principal para acessar o menu interativo:

```bash
python main.py
```

O menu oferece as seguintes opções:
- **Opção 1**: Extrair novos dados do GitHub
- **Opção 2**: Usar dados existentes e gerar grafos (escolha entre Lista ou Matriz de Adjacência)
- **Opção 3**: Apenas processar dados
- **Opção 0**: Sair

### Modo Automático (Não-Interativo)

Para processar tudo automaticamente:

```bash
python main.py --non-interactive
```

Para usar matriz de adjacência:

```bash
python main.py --non-interactive --use-matrix
```

### Uso Personalizado

```python
from src.github_api import GitHubAPIClient
from src.graph_data_extractor import GraphDataExtractor
from src.graph_builder import GraphBuilder

# Inicializar cliente
client = GitHubAPIClient("major", "MySQLTuner-perl", token="seu_token")

# Coletar dados
client.fetch_all_data()

# Extrair nós e arestas
extractor = GraphDataExtractor(client.raw_data)
extractor.extract_all()
extractor.save_graph_data()

# Construir grafos
builder = GraphBuilder("output")
graphs = builder.build_all_graphs(use_matrix=False)

# Exportar para GEPHI (formato GEXF)
stats = builder.export_all_graphs(graphs)
```

### O que o projeto FAZ:
✅ Coleta dados do GitHub (issues, PRs, comentários, reviews, etc.)
✅ Identifica usuários que serão nós dos grafos
✅ Identifica interações que serão arestas dos grafos
✅ Calcula pesos das arestas conforme especificação
✅ Salva dados estruturados em JSON e CSV
✅ **Constrói os 4 grafos usando biblioteca própria**
✅ **Exporta grafos em formato GEXF para visualização no GEPHI**
✅ **Suporta duas implementações: Lista e Matriz de Adjacência**

### Biblioteca de Grafos

O projeto inclui uma biblioteca de grafos implementada do zero com:
- **AbstractGraph**: Classe base abstrata
- **AdjacencyListGraph**: Implementação com lista de adjacência (O(V+E) espaço)
- **AdjacencyMatrixGraph**: Implementação com matriz de adjacência (O(V²) espaço)
- **GephiExporter**: Exportador para formato GEXF
- 100+ testes unitários garantindo qualidade

## 📊 Pesos das Interações (Conforme Especificação)

O grafo integrado utiliza os seguintes pesos:

| Tipo de Interação | Peso | Descrição |
|-------------------|------|-----------|
| Comentário em issue/PR | 2 | Usuário comenta em issue ou PR de outro |
| Abertura de issue comentada | 3 | Usuário abre issue que recebe comentário |
| Review/Aprovação de PR | 4 | Usuário faz review em PR de outro |
| Merge de PR | 5 | Usuário faz merge de PR de outro |

Você pode personalizar esses pesos no arquivo `config.py`.

## 📈 Resultados

Após a execução, você encontrará:

### Dados Raw (`data/raw/`)
- `issues_*.json`: Todas as issues do repositório
- `pull_requests_*.json`: Todos os pull requests
- `issue_comments_*.json`: Comentários em issues
- `pr_comments_*.json`: Comentários em PRs
- `pr_reviews_*.json`: Reviews de PRs
- `summary_*.json`: Resumo da coleta

### Dados dos Grafos (`data/graphs/`)

Para cada grafo, são gerados 3 arquivos:

**Grafo 1 - Comentários:**
- `graph_1_comments_data_*.json`: Dados completos (metadados + nós + arestas)
- `graph_1_comments_edges_*.csv`: Lista de arestas (source, target, weight)
- `graph_1_comments_nodes_*.csv`: Lista de nós (usuários)

**Grafo 2 - Fechamentos:**
- `graph_2_closures_data_*.json`: Dados completos
- `graph_2_closures_edges_*.csv`: Lista de arestas
- `graph_2_closures_nodes_*.csv`: Lista de nós

**Grafo 3 - Reviews e Merges:**
- `graph_3_reviews_data_*.json`: Dados completos
- `graph_3_reviews_edges_*.csv`: Lista de arestas
- `graph_3_reviews_nodes_*.csv`: Lista de nós

**Grafo Integrado:**
- `graph_integrated_data_*.json`: Dados completos com pesos
- `graph_integrated_edges_*.csv`: Lista de arestas ponderadas
- `graph_integrated_nodes_*.csv`: Lista de nós

**Arquivos Adicionais:**
- `extraction_statistics_*.json`: Estatísticas da extração
- `README_*.txt`: Documentação dos dados extraídos

### Dados Processados (`data/processed/`)
- `user_stats_*.csv` e `*.xlsx`: Estatísticas por usuário
- `processed_data_*.json`: Análises de timeline e colaboração

## 📊 Como Usar os Dados Extraídos

### Para construção manual de grafos:

1. **Leia os nós** do arquivo `*_nodes_*.csv`
2. **Leia as arestas** do arquivo `*_edges_*.csv`
3. **Use o campo 'weight'** para o peso das arestas
4. **Construa o grafo** usando sua biblioteca manual

### Exemplo de estrutura dos arquivos CSV:

**Nós (nodes):**
```csv
node_id
usuario1
usuario2
usuario3
```

**Arestas (edges):**
```csv
source,target,weight,type
usuario1,usuario2,5,comment
usuario2,usuario3,3,review
```

## 🛠️ Tecnologias Utilizadas

- **Python 3.12**: Linguagem principal
- **Requests**: Cliente HTTP para API do GitHub
- **Pandas**: Manipulação e exportação de dados
- **Python-dotenv**: Gerenciamento de variáveis de ambiente
- **tqdm**: Barras de progresso para coleta de dados

**Nota:** Este projeto NÃO utiliza bibliotecas de grafos (NetworkX, etc.). Os dados são extraídos e salvos para construção manual posterior.

## 📝 Exemplo de Repositório

O projeto está configurado por padrão para analisar:
- **Repositório**: [major/MySQLTuner-perl](https://github.com/major/MySQLTuner-perl)
- **Estrelas**: ~9.2k
- **Comunidade**: Ativa e com muitas interações

## ⚠️ Limitações

- **Rate Limit**: GitHub API limita requisições (60/hora sem token, 5000/hora com token)
- **Tamanho**: Repositórios muito grandes podem demorar horas para processar
- **Memória**: Grafos muito grandes requerem bastante RAM

## 🤝 Contribuindo

Contribuições são bem-vindas! Por favor:

1. Faça um fork do projeto
2. Crie uma branch para sua feature (`git checkout -b feature/MinhaFeature`)
3. Commit suas mudanças (`git commit -m 'Adiciona MinhaFeature'`)
4. Push para a branch (`git push origin feature/MinhaFeature`)
5. Abra um Pull Request

## 📄 Licença

Este projeto é destinado para fins acadêmicos.

## 👥 Autor

Desenvolvido como parte do trabalho de Teoria dos Grafos.

## 📧 Contato

Para dúvidas ou sugestões, abra uma issue no repositório.
