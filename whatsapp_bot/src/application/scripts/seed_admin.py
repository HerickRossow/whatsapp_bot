"""Cadastra/atualiza o administrador definido no .env no banco de dados."""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import config
import db

def main():
    if not config.ADMIN_WHATSAPP:
        print("Defina ADMIN_WHATSAPP no arquivo .env antes de rodar este script.")
        return
    db.init_db()
    conn = db.get_conn()
    conn.execute(
        "INSERT INTO administradores (whatsapp, nome, ativo) VALUES (?, ?, 1) "
        "ON CONFLICT(whatsapp) DO UPDATE SET nome=excluded.nome, ativo=1",
        (config.ADMIN_WHATSAPP, config.ADMIN_NOME),
    )
    conn.commit()
    print(f"Administrador {config.ADMIN_WHATSAPP} ({config.ADMIN_NOME}) cadastrado/ativado.")

if __name__ == "__main__":
    main()
