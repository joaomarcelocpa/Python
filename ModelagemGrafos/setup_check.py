import sys
import subprocess
from pathlib import Path


def check_python_version():
    version = sys.version_info
    
    if version < (3, 10):
        print(f"Python {version.major}.{version.minor} detectado")
        print("   Este projeto requer Python 3.10+")
        return False
    
    print(f"[OK] Python {version.major}.{version.minor}.{version.micro}")
    return True


def check_venv():
    """Verifica se esta em um ambiente virtual"""
    print("\n Verificando ambiente virtual...")
    
    in_venv = hasattr(sys, 'real_prefix') or (
        hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix
    )
    
    if in_venv:
        print("[OK] Ambiente virtual ativo")
        return True
    else:
        print("Nao esta em um ambiente virtual")
        print("   Recomendamos usar: python -m venv venv")
        print("   E ativar com: source venv/bin/activate")
        return False


def check_dependencies():
    """Verifica se as dependencias estao instaladas"""
    print("\n Verificando dependencias...")
    
    required = [
        'requests',
        'matplotlib',
        'pandas',
        'python-dotenv',
        'customtkinter'
    ]
    
    missing = []
    
    for package in required:
        try:
            __import__(package.replace('-', '_'))
            print(f"[OK] {package}")
        except ImportError:
            print(f" {package}")
            missing.append(package)
    
    if missing:
        print(f"\n Dependencias faltando: {', '.join(missing)}")
        print("   Execute: pip install -r requirements.txt")
        return False
    
    print("\n[OK] Todas as dependencias instaladas")
    return True


def check_env_file():
    """Verifica arquivo .env"""
    print("\n Verificando configuracao...")
    
    env_file = Path('.env')
    
    if not env_file.exists():
        print(" Arquivo .env nao encontrado")
        print("   Execute: cp .env.example .env")
        print("   E configure seu GITHUB_TOKEN")
        return False
    
    with open(env_file) as f:
        content = f.read()
    
    if 'GITHUB_TOKEN=' in content and 'your_github_token_here' not in content:
        for line in content.split('\n'):
            if line.startswith('GITHUB_TOKEN=') and len(line.split('=')[1].strip()) > 10:
                print("[OK] Arquivo .env configurado")
                print("[OK] GITHUB_TOKEN encontrado")
                return True
    
    print("  Arquivo .env existe mas GITHUB_TOKEN nao esta configurado")
    print("   Adicione seu token do GitHub no arquivo .env")
    print("   Obtenha em: https://github.com/settings/tokens")
    return False


def check_directories():
    """Verifica estrutura de diretorios"""
    print("\n Verificando estrutura de diretorios...")
    
    required_dirs = [
        'src',
        'data',
        'data/raw',
        'data/processed',
        'data/graphs',
        'output',
        'output/visualizations',
        'output/reports',
        'notebooks',
        'tests'
    ]
    
    all_exist = True
    for dir_path in required_dirs:
        path = Path(dir_path)
        if path.exists():
            print(f"[OK] {dir_path}/")
        else:
            print(f"  {dir_path}/ nao existe (sera criado)")
            path.mkdir(parents=True, exist_ok=True)
            all_exist = False
    
    return True


def run_tests():
    """Executa testes basicos"""
    print("\n Executando testes...")
    
    try:
        result = subprocess.run(
            ['pytest', 'tests/', '-v'],
            capture_output=True,
            text=True,
            timeout=30
        )
        
        if result.returncode == 0:
            print("[OK] Todos os testes passaram")
            return True
        else:
            print(" Alguns testes falharam")
            print(result.stdout)
            return False
    except FileNotFoundError:
        print("  pytest nao encontrado")
        print("   Execute: pip install pytest")
        return False
    except subprocess.TimeoutExpired:
        print("  Testes demoraram muito")
        return False


def main():
    """Funcao principal"""
    print("=" * 70)
    print("  GitHub Repository Graph Analyzer - Setup Verification")
    print("=" * 70)
    
    checks = [
        ("Python Version", check_python_version),
        ("Virtual Environment", check_venv),
        ("Dependencies", check_dependencies),
        ("Configuration", check_env_file),
        ("Directory Structure", check_directories),
    ]
    
    results = []
    
    for name, check_func in checks:
        try:
            result = check_func()
            results.append((name, result))
        except Exception as e:
            print(f"\n Erro ao verificar {name}: {e}")
            results.append((name, False))
    
    print("\n" + "=" * 70)
    response = input("Executar testes unitarios? (s/N): ").strip().lower()
    if response == 's':
        results.append(("Unit Tests", run_tests()))
    

    print("\n" + "=" * 70)
    print("RESUMO DA VERIFICACAO")
    print("=" * 70)
    
    all_passed = True
    for name, result in results:
        status = "[OK] PASS" if result else " FAIL"
        print(f"{status:10s} {name}")
        if not result:
            all_passed = False
    
    print("=" * 70)
    
    if all_passed:
        print("\n Tudo pronto! Voce pode executar:")
        print("   python main.py")
    else:
        print("\n  Algumas verificacoes falharam.")
        print("   Corrija os problemas acima antes de continuar.")
        print("\n Consulte QUICKSTART.md para mais ajuda.")
    
    return 0 if all_passed else 1


if __name__ == "__main__":
    sys.exit(main())
