from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    whatsapp_token: str = ""
    whatsapp_phone_number_id: str = ""
    whatsapp_verify_token: str = "meu_token_secreto"
    whatsapp_api_version: str = "v21.0"
    whatsapp_app_secret: str = ""

    anthropic_api_key: str = ""
    anthropic_model: str = "claude-sonnet-5"

    admin_whatsapp: str = ""
    admin_nome: str = "Administrador"

    pix_chave: str = ""
    pix_nome: str = ""
    pix_banco: str = ""
    nome_loja: str = "Loja de Suplementos"
    frete_padrao: float = 15.00

    mongo_uri: str = "mongodb://localhost:27017"
    mongo_db_name: str = "whatsapp_bot"

    comprovantes_dir: Path = Path("data/comprovantes")
    produtos_xlsx: Path = Path("data/produtos/produtos.xlsx")
    logs_dir: Path = Path("data/logs")
    backups_dir: Path = Path("data/backups")

    host: str = "0.0.0.0"
    port: int = 8000
    debug: bool = False

    def ensure_directories(self) -> None:
        for directory in (self.comprovantes_dir, self.produtos_xlsx.parent, self.logs_dir, self.backups_dir):
            directory.mkdir(parents=True, exist_ok=True)


settings = Settings()
