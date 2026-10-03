"""
Script de inicialização rápida: cria banco, cria produtos.xlsx de exemplo,
sincroniza produtos e cadastra o administrador. Rode uma vez no início.
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import db
import excel_sync
from scripts.seed_admin import main as seed_admin

def main():
    db.init_db()
    excel_sync.criar_exemplo()
    excel_sync.sincronizar()
    seed_admin()
    print("\nTudo pronto! Rode 'python AppRouters.py' para iniciar o servidor.")

if __name__ == "__main__":
    main()
