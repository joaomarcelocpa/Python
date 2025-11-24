"""
Processador de dados coletados do GitHub
"""
import json
from datetime import datetime
from typing import Dict, List
from collections import Counter
import pandas as pd
import config


class DataProcessor:
    """Processa e analisa dados raw do GitHub"""

    def __init__(self, raw_data: Dict):
        """
        Inicializa o processador

        Args:
            raw_data: Dados raw coletados da API
        """
        self.raw_data = raw_data
        self.processed_data = {}

    @staticmethod
    def _get_empty_user_stats() -> Dict:
        """
        Retorna dicionario vazio de estatisticas de usuario.
        Metodo auxiliar para evitar duplicacao.

        Returns:
            Dicionario com estatisticas zeradas
        """
        return {
            "issues_opened": 0,
            "prs_opened": 0,
            "issue_comments": 0,
            "pr_comments": 0,
            "reviews": 0,
            "issues_closed": 0
        }
    
    def analyze_users(self) -> pd.DataFrame:
        """
        Analisa participacao de usuarios
        
        Returns:
            DataFrame com estatisticas por usuario
        """
        print(f"\n{'='*70}")
        print(f" Analisando usuarios")
        print(f"{'='*70}")
        
        user_stats = {}
        
        # Issues abertas
        for issue in self.raw_data.get("issues", []):
            user = issue["user"]["login"]
            if user not in user_stats:
                user_stats[user] = self._get_empty_user_stats()
            user_stats[user]["issues_opened"] += 1

            # Issues fechadas por este usuario
            if issue["state"] == "closed" and issue.get("closed_by"):
                closer = issue["closed_by"]["login"]
                if closer not in user_stats:
                    user_stats[closer] = self._get_empty_user_stats()
                user_stats[closer]["issues_closed"] += 1
        
        # Pull requests
        for pr in self.raw_data.get("pull_requests", []):
            user = pr["user"]["login"]
            if user not in user_stats:
                user_stats[user] = self._get_empty_user_stats()
            user_stats[user]["prs_opened"] += 1
        
        # Comentarios em issues
        for comment in self.raw_data.get("issue_comments", []):
            user = comment["user"]["login"]
            if user not in user_stats:
                user_stats[user] = self._get_empty_user_stats()
            user_stats[user]["issue_comments"] += 1
        
        # Comentarios em PRs
        for comment in self.raw_data.get("pr_comments", []):
            user = comment["user"]["login"]
            if user not in user_stats:
                user_stats[user] = self._get_empty_user_stats()
            user_stats[user]["pr_comments"] += 1
        
        # Reviews
        for review in self.raw_data.get("pr_reviews", []):
            user = review["user"]["login"]
            if user not in user_stats:
                user_stats[user] = self._get_empty_user_stats()
            user_stats[user]["reviews"] += 1
        
        # Converte para DataFrame
        df = pd.DataFrame.from_dict(user_stats, orient='index')
        df.index.name = 'user'
        df = df.reset_index()
        
        # Calcula total de atividades
        df['total_activity'] = (
            df['issues_opened'] + 
            df['prs_opened'] + 
            df['issue_comments'] + 
            df['pr_comments'] + 
            df['reviews'] + 
            df['issues_closed']
        )
        
        # Ordena por atividade total
        df = df.sort_values('total_activity', ascending=False)
        
        self.processed_data['user_stats'] = df
        
        print(f"[OK] Total de usuarios: {len(df)}")
        print(f"\nTop 10 usuarios mais ativos:")
        print(df.head(10)[['user', 'total_activity', 'issues_opened', 'prs_opened', 'reviews']])
        
        return df
    
    def analyze_timeline(self) -> Dict:
        """
        Analisa timeline de atividades
        
        Returns:
            Dicionario com estatisticas temporais
        """
        print(f"\n{'='*70}")
        print(f" Analisando timeline")
        print(f"{'='*70}")
        
        timeline = {
            "issues_by_month": Counter(),
            "prs_by_month": Counter(),
            "comments_by_month": Counter()
        }
        
        # Issues
        for issue in self.raw_data.get("issues", []):
            created = datetime.strptime(issue["created_at"], "%Y-%m-%dT%H:%M:%SZ")
            month = created.strftime("%Y-%m")
            timeline["issues_by_month"][month] += 1
        
        # Pull requests
        for pr in self.raw_data.get("pull_requests", []):
            created = datetime.strptime(pr["created_at"], "%Y-%m-%dT%H:%M:%SZ")
            month = created.strftime("%Y-%m")
            timeline["prs_by_month"][month] += 1
        
        # Comentarios
        for comment in self.raw_data.get("issue_comments", []) + self.raw_data.get("pr_comments", []):
            created = datetime.strptime(comment["created_at"], "%Y-%m-%dT%H:%M:%SZ")
            month = created.strftime("%Y-%m")
            timeline["comments_by_month"][month] += 1
        
        self.processed_data['timeline'] = timeline
        
        print(f"[OK] Periodo de analise:")
        if timeline["issues_by_month"]:
            months = sorted(timeline["issues_by_month"].keys())
            print(f"  De {months[0]} ate {months[-1]}")
        
        return timeline
    
    def analyze_collaboration_patterns(self) -> Dict:
        """
        Analisa padroes de colaboracao
        
        Returns:
            Dicionario com metricas de colaboracao
        """
        print(f"\n{'='*70}")
        print(f" Analisando padroes de colaboracao")
        print(f"{'='*70}")
        
        patterns = {
            "avg_comments_per_issue": 0,
            "avg_comments_per_pr": 0,
            "issues_with_comments": 0,
            "prs_with_reviews": 0,
            "merge_rate": 0
        }
        
        # Issues com comentarios
        issues_with_comments = sum(1 for issue in self.raw_data.get("issues", []) if issue["comments"] > 0)
        total_issues = len(self.raw_data.get("issues", []))
        
        if total_issues > 0:
            patterns["issues_with_comments"] = issues_with_comments / total_issues
            total_issue_comments = len(self.raw_data.get("issue_comments", []))
            patterns["avg_comments_per_issue"] = total_issue_comments / total_issues
        
        # PRs com reviews
        prs_with_reviews = sum(1 for pr in self.raw_data.get("pull_requests", []) 
                              if any(r["pr_number"] == pr["number"] 
                                   for r in self.raw_data.get("pr_reviews", [])))
        total_prs = len(self.raw_data.get("pull_requests", []))
        
        if total_prs > 0:
            patterns["prs_with_reviews"] = prs_with_reviews / total_prs
            total_pr_comments = len(self.raw_data.get("pr_comments", []))
            patterns["avg_comments_per_pr"] = total_pr_comments / total_prs
            
            # Taxa de merge
            merged_prs = sum(1 for pr in self.raw_data.get("pull_requests", []) if pr.get("merged_at"))
            patterns["merge_rate"] = merged_prs / total_prs
        
        self.processed_data['collaboration_patterns'] = patterns
        
        print(f"[OK] Issues com comentarios: {patterns['issues_with_comments']:.1%}")
        print(f"[OK] PRs com reviews: {patterns['prs_with_reviews']:.1%}")
        print(f"[OK] Taxa de merge: {patterns['merge_rate']:.1%}")
        print(f"[OK] Media de comentarios por issue: {patterns['avg_comments_per_issue']:.2f}")
        print(f"[OK] Media de comentarios por PR: {patterns['avg_comments_per_pr']:.2f}")
        
        return patterns
    
    def process_all(self):
        """Executa todo o processamento"""
        print(f"\n{'#'*70}")
        print(f"#  PROCESSANDO DADOS")
        print(f"{'#'*70}")
        
        self.analyze_users()
        self.analyze_timeline()
        self.analyze_collaboration_patterns()
        
        print(f"\n{'='*70}")
        print(f" PROCESSAMENTO CONCLUIDO")
        print(f"{'='*70}")
    
    def save_processed_data(self, output_dir: str = None):
        """
        Salva dados processados
        
        Args:
            output_dir: Diretorio de saida
        """
        if output_dir is None:
            output_dir = config.PROCESSED_DATA_DIR
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        print(f"\n Salvando dados processados...")
        
        if 'user_stats' in self.processed_data:
            df = self.processed_data['user_stats']
            
            csv_file = output_dir / f"user_stats_{timestamp}.csv"
            df.to_csv(csv_file, index=False, encoding='utf-8')
            print(f"[OK] {csv_file.name}")
            
            excel_file = output_dir / f"user_stats_{timestamp}.xlsx"
            df.to_excel(excel_file, index=False, engine='openpyxl')
            print(f"[OK] {excel_file.name}")
        
        json_data = {
            k: v for k, v in self.processed_data.items() 
            if k != 'user_stats'
        }
        
        json_file = output_dir / f"processed_data_{timestamp}.json"
        with open(json_file, 'w', encoding='utf-8') as f:
            json.dump(json_data, f, indent=2, ensure_ascii=False, default=str)
        print(f"[OK] {json_file.name}")
        
        print(f"\n Dados processados salvos em: {output_dir}")
