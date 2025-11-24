import time
import json
from datetime import datetime
from typing import Dict, List, Optional
import requests
from tqdm import tqdm
import config


class GitHubAPIClient:
    
    def __init__(self, repo_owner: str, repo_name: str, token: Optional[str] = None):
        self.repo_owner = repo_owner
        self.repo_name = repo_name
        self.base_url = config.GITHUB_API_BASE_URL
        
        self.headers = {
            "Accept": config.GITHUB_API_VERSION
        }
        
        if token:
            self.headers["Authorization"] = f"token {token}"
        
        self.raw_data = {
            "repository_info": {},
            "issues": [],
            "pull_requests": [],
            "issue_comments": [],
            "pr_comments": [],
            "pr_reviews": []
        }
        
        self.request_count = 0
        self.start_time = datetime.now()
    
    def _make_request(self, endpoint: str, params: Optional[Dict] = None) -> List[Dict]:
        if params is None:
            params = {}
        
        params.setdefault("per_page", config.ITEMS_PER_PAGE)
        params.setdefault("page", 1)
        
        all_results = []
        url = f"{self.base_url}{endpoint}"
        
        with tqdm(desc=f"Coletando {endpoint.split('/')[-1]}", unit=" paginas") as pbar:
            while True:
                try:
                    response = requests.get(url, headers=self.headers, params=params, timeout=30)
                    self.request_count += 1
                    
                    remaining = int(response.headers.get('X-RateLimit-Remaining', 0))
                    
                    if remaining < 10 and config.RATE_LIMIT_WAIT:
                        reset_time = int(response.headers.get('X-RateLimit-Reset', 0))
                        wait_time = max(reset_time - time.time() + 10, 0)
                        
                        if wait_time > 0:
                            print(f"\n Rate limit baixo. Aguardando {wait_time:.0f}s...")
                            time.sleep(wait_time)
                    
                    response.raise_for_status()
                    data = response.json()
                    
                    if not data:
                        break
                    
                    all_results.extend(data)
                    pbar.update(1)
                    pbar.set_postfix({"Total": len(all_results)})
                    
                    if 'Link' not in response.headers:
                        break
                    
                    links = response.headers['Link']
                    if 'rel="next"' not in links:
                        break
                    
                    params['page'] += 1
                    time.sleep(config.REQUEST_DELAY_SECONDS)
                    
                except requests.exceptions.RequestException as e:
                    print(f"\nErro na requisicao: {e}")
                    break
        
        return all_results

    def _make_single_request(self, endpoint: str) -> Optional[Dict]:
        """
        Faz uma requisição que retorna um único item (não paginado).

        Args:
            endpoint: Endpoint da API do GitHub

        Returns:
            Dicionário com os dados ou None em caso de erro
        """
        url = f"{self.base_url}{endpoint}"

        try:
            response = requests.get(url, headers=self.headers, timeout=30)
            self.request_count += 1

            remaining = int(response.headers.get('X-RateLimit-Remaining', 0))

            if remaining < 10 and config.RATE_LIMIT_WAIT:
                reset_time = int(response.headers.get('X-RateLimit-Reset', 0))
                wait_time = max(reset_time - time.time() + 10, 0)

                if wait_time > 0:
                    print(f"\n⏳ Rate limit baixo. Aguardando {wait_time:.0f}s...")
                    time.sleep(wait_time)

            response.raise_for_status()
            return response.json()

        except requests.exceptions.RequestException as e:
            print(f"\n❌ Erro na requisição {endpoint}: {e}")
            return None

    def fetch_repository_info(self) -> Dict:
        endpoint = f"/repos/{self.repo_owner}/{self.repo_name}"
        
        print(f"\n{'='*70}")
        print(f"Coletando informacoes do repositorio")
        print(f"{'='*70}")
        
        try:
            response = requests.get(
                f"{self.base_url}{endpoint}", 
                headers=self.headers,
                timeout=30
            )
            response.raise_for_status()
            self.raw_data["repository_info"] = response.json()
            
            info = self.raw_data["repository_info"]
            print(f"\n[OK] Repositorio: {info['full_name']}")
            print(f"Estrelas: {info['stargazers_count']:,}")
            print(f"Forks: {info['forks_count']:,}")
            print(f"Issues abertas: {info['open_issues_count']:,}")
            print(f"Criado em: {info['created_at'][:10]}")
            print(f"Ultima atualizacao: {info['updated_at'][:10]}")
            
            return self.raw_data["repository_info"]
            
        except requests.exceptions.RequestException as e:
            print(f"Erro ao buscar informacoes do repositorio: {e}")
            return {}
    
    def fetch_issues(self, state: str = "all") -> List[Dict]:
        endpoint = f"/repos/{self.repo_owner}/{self.repo_name}/issues"
        
        print(f"\n{'='*70}")
        print(f"Coletando issues (state={state})")
        print(f"{'='*70}")
        
        params = {"state": state}
        issues = self._make_request(endpoint, params)
        
        self.raw_data["issues"] = [
            issue for issue in issues 
            if "pull_request" not in issue
        ]
        
        print(f"\n[OK] Total de issues coletadas: {len(self.raw_data['issues']):,}")
        
        return self.raw_data["issues"]
    
    def fetch_pull_requests(self, state: str = "all") -> List[Dict]:
        endpoint = f"/repos/{self.repo_owner}/{self.repo_name}/pulls"
        
        print(f"\n{'='*70}")
        print(f"Coletando pull requests (state={state})")
        print(f"{'='*70}")
        
        params = {"state": state}
        self.raw_data["pull_requests"] = self._make_request(endpoint, params)
        
        print(f"\n[OK] Total de pull requests coletados: {len(self.raw_data['pull_requests']):,}")
        
        return self.raw_data["pull_requests"]
    
    def fetch_issue_comments(self) -> List[Dict]:
        print(f"\n{'='*70}")
        print(f"Coletando comentarios de issues")
        print(f"{'='*70}")
        
        total_issues = len(self.raw_data["issues"])
        
        with tqdm(total=total_issues, desc="Processando issues", unit=" issues") as pbar:
            for issue in self.raw_data["issues"]:
                if issue.get("comments", 0) > 0:
                    endpoint = f"/repos/{self.repo_owner}/{self.repo_name}/issues/{issue['number']}/comments"
                    comments = self._make_request(endpoint)

                    for comment in comments:
                        if comment.get("user"):  
                            comment["issue_number"] = issue["number"]
                            comment["issue_user"] = issue.get("user", {}).get("login", "unknown")
                            self.raw_data["issue_comments"].append(comment)
                
                pbar.update(1)
                time.sleep(config.REQUEST_DELAY_SECONDS)
        
        print(f"\nTotal de comentarios em issues: {len(self.raw_data['issue_comments']):,}")
        
        return self.raw_data["issue_comments"]
    
    def fetch_pr_comments_and_reviews(self) -> tuple:
        print(f"\n{'='*70}")
        print(f"Coletando comentarios e reviews de pull requests")
        print(f"{'='*70}")
        
        total_prs = len(self.raw_data["pull_requests"])
        
        with tqdm(total=total_prs, desc="Processando PRs", unit=" PRs") as pbar:
            for pr in self.raw_data["pull_requests"]:
                if pr.get("comments", 0) > 0:
                    endpoint = f"/repos/{self.repo_owner}/{self.repo_name}/issues/{pr['number']}/comments"
                    comments = self._make_request(endpoint)

                    for comment in comments:
                        if comment.get("user"):
                            comment["pr_number"] = pr["number"]
                            comment["pr_user"] = pr.get("user", {}).get("login", "unknown")
                            self.raw_data["pr_comments"].append(comment)

                endpoint = f"/repos/{self.repo_owner}/{self.repo_name}/pulls/{pr['number']}/reviews"
                reviews = self._make_request(endpoint)

                for review in reviews:
                    if review.get("user"): 
                        review["pr_number"] = pr["number"]
                        review["pr_user"] = pr.get("user", {}).get("login", "unknown")
                        self.raw_data["pr_reviews"].append(review)
                
                pbar.update(1)
                time.sleep(config.REQUEST_DELAY_SECONDS)
        
        print(f"\nTotal de comentarios em PRs: {len(self.raw_data['pr_comments']):,}")
        print(f"Total de reviews: {len(self.raw_data['pr_reviews']):,}")

        return self.raw_data["pr_comments"], self.raw_data["pr_reviews"]

    def fetch_pr_merge_info(self) -> int:
        """
        Busca informações detalhadas de PRs merged para capturar merged_by.

        Returns:
            Número de PRs atualizados com informação de merge
        """
        print(f"\n{'='*70}")
        print(f"Coletando informações de merge dos pull requests")
        print(f"{'='*70}")

        # Filtra apenas PRs merged
        merged_prs = [pr for pr in self.raw_data["pull_requests"] if pr.get("merged_at")]
        total_merged = len(merged_prs)
        updated_count = 0

        print(f"PRs merged encontrados: {total_merged}")

        if total_merged == 0:
            print("Nenhum PR merged encontrado. Pulando coleta de merge info.")
            return 0

        with tqdm(total=total_merged, desc="Buscando merge info", unit=" PRs") as pbar:
            for pr in merged_prs:
                endpoint = f"/repos/{self.repo_owner}/{self.repo_name}/pulls/{pr['number']}"
                pr_details = self._make_single_request(endpoint)

                if pr_details and pr_details.get("merged_by"):
                    pr["merged_by"] = pr_details["merged_by"]
                    updated_count += 1

                pbar.update(1)
                time.sleep(config.REQUEST_DELAY_SECONDS)

        print(f"\n[OK] PRs atualizados com merged_by: {updated_count}/{total_merged}")

        return updated_count

    def fetch_all_data(self):
        print(f"\n{'#'*70}")
        print(f"#INICIANDO COLETA DE DADOS DO GITHUB")
        print(f"# Repositorio: {self.repo_owner}/{self.repo_name}")
        print(f"# Horario de inicio: {self.start_time.strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"{'#'*70}")
        
        self.fetch_repository_info()
        
        if config.FETCH_ALL_ISSUES:
            self.fetch_issues()
        
        if config.FETCH_ALL_PRS:
            self.fetch_pull_requests()
        
        if config.FETCH_COMMENTS and self.raw_data["issues"]:
            self.fetch_issue_comments()
        
        if config.FETCH_REVIEWS and self.raw_data["pull_requests"]:
            self.fetch_pr_comments_and_reviews()

        # Busca informações de merge (merged_by) para PRs merged
        if config.FETCH_ALL_PRS and self.raw_data["pull_requests"]:
            self.fetch_pr_merge_info()

        end_time = datetime.now()
        duration = (end_time - self.start_time).total_seconds()
        
        print(f"\n{'='*70}")
        print(f"COLETA CONCLUIDA")
        print(f"{'='*70}")
        print(f"Tempo total: {duration:.2f}s ({duration/60:.2f} minutos)")
        print(f"Total de requisicoes: {self.request_count}")
        print(f"Requisicoes por minuto: {self.request_count / (duration/60):.2f}")
    
    def save_raw_data(self, output_dir: str = None):
        if output_dir is None:
            output_dir = config.RAW_DATA_DIR
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        print(f"\n{'='*70}")
        print(f"Salvando dados raw")
        print(f"{'='*70}")
        
        for data_type, data in self.raw_data.items():
            filename = output_dir / f"{data_type}_{timestamp}.json"
            
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            
            print(f"[OK] {filename.name} ({len(data) if isinstance(data, list) else 1} itens)")
        
        summary = {
            "timestamp": timestamp,
            "repository": f"{self.repo_owner}/{self.repo_name}",
            "collection_duration_seconds": (datetime.now() - self.start_time).total_seconds(),
            "total_requests": self.request_count,
            "data_counts": {
                "issues": len(self.raw_data["issues"]),
                "pull_requests": len(self.raw_data["pull_requests"]),
                "issue_comments": len(self.raw_data["issue_comments"]),
                "pr_comments": len(self.raw_data["pr_comments"]),
                "pr_reviews": len(self.raw_data["pr_reviews"])
            }
        }
        
        summary_file = output_dir / f"summary_{timestamp}.json"
        with open(summary_file, 'w', encoding='utf-8') as f:
            json.dump(summary, f, indent=2, ensure_ascii=False)
        
        print(f"[OK] {summary_file.name}")
        print(f"\nDados salvos em: {output_dir}")
    
    def get_summary(self) -> Dict:
        return {
            "repository": f"{self.repo_owner}/{self.repo_name}",
            "stars": self.raw_data["repository_info"].get("stargazers_count", 0),
            "issues": len(self.raw_data["issues"]),
            "pull_requests": len(self.raw_data["pull_requests"]),
            "issue_comments": len(self.raw_data["issue_comments"]),
            "pr_comments": len(self.raw_data["pr_comments"]),
            "pr_reviews": len(self.raw_data["pr_reviews"]),
            "total_requests": self.request_count
        }
