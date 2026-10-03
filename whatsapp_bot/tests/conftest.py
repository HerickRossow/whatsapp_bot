import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import mongomock
import pytest

from src.infra.Container import Container
from src.infra.config.Settings import Settings

from .fakes import AssistenteIAGatewayFake, WhatsAppGatewayFake


@pytest.fixture
def database():
    return mongomock.MongoClient()["whatsapp_bot_test"]


@pytest.fixture
def settings_teste(tmp_path):
    settings = Settings(
        admin_whatsapp="11999998888",
        admin_nome="Admin Teste",
        whatsapp_verify_token="token123",
        nome_loja="Loja Teste",
        anthropic_api_key="x",
        whatsapp_token="x",
        whatsapp_phone_number_id="x",
        comprovantes_dir=tmp_path / "comprovantes",
        produtos_xlsx=tmp_path / "produtos" / "produtos.xlsx",
        logs_dir=tmp_path / "logs",
        backups_dir=tmp_path / "backups",
    )
    settings.ensure_directories()
    return settings


@pytest.fixture
def whatsapp_gateway_fake():
    return WhatsAppGatewayFake()


@pytest.fixture
def assistente_gateway_fake():
    return AssistenteIAGatewayFake()


@pytest.fixture
def container(database, settings_teste, whatsapp_gateway_fake, assistente_gateway_fake):
    return Container(
        settings_teste,
        database=database,
        whatsapp_gateway=whatsapp_gateway_fake,
        assistente_gateway=assistente_gateway_fake,
    )
