"""
Configuracoes do projeto GitHub Graph Analyzer
"""
import os
from pathlib import Path
from dotenv import load_dotenv

# Carrega variaveis de ambiente do arquivo .env
load_dotenv()

# Diretorios base
BASE_DIR = Path(__file__).parent
DATA_DIR = BASE_DIR / os.getenv("DATA_DIR", "data")
OUTPUT_DIR = BASE_DIR / os.getenv("OUTPUT_DIR", "output")

# Subdiretorios
RAW_DATA_DIR = DATA_DIR / "raw"
PROCESSED_DATA_DIR = DATA_DIR / "processed"
GRAPHS_DIR = DATA_DIR / "graphs"
VISUALIZATIONS_DIR = OUTPUT_DIR / "visualizations"
REPORTS_DIR = OUTPUT_DIR / "reports"

# Lista de diretorios que devem ser criados pela aplicacao
# NOTA: Criacao de diretorios movida para entry points (app.py, main.py)
# para evitar efeitos colaterais na importacao de configuracao
REQUIRED_DIRECTORIES = [
    RAW_DATA_DIR,
    PROCESSED_DATA_DIR,
    GRAPHS_DIR,
    VISUALIZATIONS_DIR,
    REPORTS_DIR
]

# Configuracoes do GitHub
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")
REPO_OWNER = os.getenv("REPO_OWNER", "major")
REPO_NAME = os.getenv("REPO_NAME", "MySQLTuner-perl")

# Configuracoes de coleta de dados
FETCH_ALL_ISSUES = os.getenv("FETCH_ALL_ISSUES", "true").lower() == "true"
FETCH_ALL_PRS = os.getenv("FETCH_ALL_PRS", "true").lower() == "true"
FETCH_COMMENTS = os.getenv("FETCH_COMMENTS", "true").lower() == "true"
FETCH_REVIEWS = os.getenv("FETCH_REVIEWS", "true").lower() == "true"

# Configuracoes de output
SAVE_RAW_DATA = os.getenv("SAVE_RAW_DATA", "true").lower() == "true"
SAVE_GRAPHS = os.getenv("SAVE_GRAPHS", "true").lower() == "true"
GENERATE_VISUALIZATIONS = os.getenv("GENERATE_VISUALIZATIONS", "true").lower() == "true"

# Configuracoes de rate limiting
RATE_LIMIT_WAIT = os.getenv("RATE_LIMIT_WAIT", "true").lower() == "true"
REQUEST_DELAY_SECONDS = float(os.getenv("REQUEST_DELAY_SECONDS", "0.5"))

# Pesos das interacoes para o grafo integrado
INTERACTION_WEIGHTS = {
    "comment": int(os.getenv("WEIGHT_COMMENT", "2")),
    "issue_opened": int(os.getenv("WEIGHT_ISSUE_OPENED", "3")),
    "review": int(os.getenv("WEIGHT_REVIEW", "4")),
    "merge": int(os.getenv("WEIGHT_MERGE", "5"))
}

# Configuracoes de visualizacao
VISUALIZATION_CONFIG = {
    "figure_size": (15, 10),
    "dpi": 300,
    "node_color": "lightblue",
    "edge_color": "gray",
    "node_alpha": 0.7,
    "edge_alpha": 0.5,
    "font_size": 8,
    "max_nodes_to_visualize": 100  # Limitar visualizacao para grafos grandes
}

# Configuracoes da API do GitHub
GITHUB_API_BASE_URL = "https://api.github.com"
GITHUB_API_VERSION = "application/vnd.github.v3+json"
ITEMS_PER_PAGE = 100  # Maximo permitido pela API

# NOTA: Prints removidos para evitar output durante importacao de modulo
# Validacao e logging devem ser feitos nos entry points da aplicacao
