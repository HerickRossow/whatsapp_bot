# Bot de Vendas no WhatsApp — Suplementos

Bot de atendimento e vendas pelo WhatsApp, construído em **Clean Architecture + DDD**,
com **FastAPI**, **MongoDB** e o **Claude (Anthropic)** cuidando da conversa via tool-use.

```
WhatsApp Cliente → Meta WhatsApp Cloud API → FastAPI → Claude (tool-use)
                                                  │
                                                  ├── MongoDB (clientes/produtos/pedidos/pagamentos)
                                                  ├── Excel (catálogo, editável por você)
                                                  ├── Comprovantes (arquivos locais)
                                                  └── WhatsApp administrativo (aprova/recusa)
```

## Arquitetura

O código em `src/` segue Clean Architecture, com a regra de dependência apontando
sempre pra dentro (`interfaces` → `application`/`infra` → `domain`; `domain` não
depende de nada):

```
src/
├── domain/              # Regras de negócio puras, sem framework nem banco
│   ├── entities/         # Cliente, Produto, Carrinho, Pedido, Pagamento, Comprovante...
│   ├── value_objects/    # Dinheiro, Telefone, ItemCarrinho, ItemPedido...
│   ├── enums/             # StatusPedido, StatusPagamento
│   ├── exceptions/        # EstoqueInsuficienteError, CarrinhoVazioError...
│   ├── repositories/      # Contratos (ports) de persistência
│   └── gateways/          # Contratos (ports) de comunicação externa (WhatsApp, IA, storage)
├── application/
│   ├── usecases/           # Uma ação de negócio por classe (CriarPedidoUseCase, ...)
│   ├── services/           # AgenteAtendimentoService (orquestra o loop de tool-use do Claude)
│   └── dto/                 # Objetos de retorno compostos (ResumoCarrinho, ...)
├── infra/
│   ├── config/               # Settings (variáveis de ambiente)
│   ├── database/              # Conexão MongoDB + índices
│   ├── repositories/           # Implementação Mongo dos ports de domain/repositories
│   ├── external/                # Implementação dos gateways (Meta API, Anthropic SDK, disco local)
│   └── Container.py              # Raiz de composição (injeção de dependências)
└── interfaces/
    └── api/
        ├── Main.py                  # App FastAPI (lifespan constrói o Container)
        ├── AdminComandoHandler.py    # APROVAR/RECUSAR/STATUS/PRONTO/ENVIAR/CANCELAR
        └── routers/                   # WebhookRouter, CatalogoRouter
```

## 1. Pré-requisitos

- Python 3.10+
- Uma instância de **MongoDB** (local via Docker, ou Atlas).
- Uma conta **Meta for Developers** com um app configurado para **WhatsApp Business
  Cloud API** (Phone Number ID, WhatsApp Business Account ID e um token de acesso).
- Uma **API key da Anthropic** (console.anthropic.com).
- Para testar localmente antes de ter um domínio público, algo como `ngrok` para
  expor a porta 8000 e configurar o webhook da Meta.

## 2. Instalação

```bash
cd whatsapp_bot
python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate
pip install -r src/requirements.txt
cp .env.example .env
```

Edite o `.env` com:
- `WHATSAPP_TOKEN`, `WHATSAPP_PHONE_NUMBER_ID`: obtidos no painel da Meta.
- `WHATSAPP_VERIFY_TOKEN`: uma frase qualquer, que você também vai colocar na
  configuração do webhook no painel da Meta.
- `ANTHROPIC_API_KEY`: sua chave da API do Claude.
- `ADMIN_WHATSAPP`: o número que vai aprovar pagamentos (formato `55DDDNUMERO`, sem `+`).
- `PIX_CHAVE`, `PIX_NOME`, `PIX_BANCO`: dados do PIX fixo da loja.
- `MONGO_URI`, `MONGO_DB_NAME`: conexão com o MongoDB.

## 3. Rodar o servidor

```bash
uvicorn src.interfaces.api.Main:app --reload --port 8000
```

Na subida, o `lifespan` do FastAPI constrói o `Container` (conecta no Mongo e cria
os índices necessários automaticamente). Para produção:

```bash
gunicorn -k uvicorn.workers.UvicornWorker -w 2 -b 0.0.0.0:8000 src.interfaces.api.Main:app
```

## 4. Catálogo de produtos

Edite `data/produtos/produtos.xlsx` (colunas: `ID, SKU, Produto, Marca, Categoria,
Peso, Sabor, Preço, Estoque, Descricao, Imagem, Ativo`) e sincronize com:

```bash
curl -X POST http://localhost:8000/sync-produtos
```

A sincronização faz upsert por `SKU` (chave de negócio do produto).

## 5. Expor o webhook para a Meta (teste local)

```bash
ngrok http 8000
```

No painel da Meta (WhatsApp > Configuration > Webhook):
- **Callback URL**: `https://SEU-DOMINIO-NGROK/webhook`
- **Verify token**: o mesmo valor de `WHATSAPP_VERIFY_TOKEN` no `.env`
- Assine (subscribe) o campo `messages`.

## 6. Fluxo de teste ponta a ponta

1. Cliente manda "Oi" → bot responde naturalmente (Claude).
2. Cliente pergunta "Tem creatina?" → bot chama a ferramenta `buscar_produtos`,
   responde com preço real do banco.
3. Cliente: "Quero 2" → bot chama `adicionar_carrinho`.
4. Cliente: "Pode fechar" → bot chama `criar_pedido`, envia dados do PIX.
5. Cliente envia a foto do comprovante → o sistema salva o arquivo em
   `data/comprovantes/AAAA/MM/DD/`, registra no Mongo e **envia automaticamente
   para o número administrativo** com os dados do pedido + a imagem.
6. Você (admin) responde `APROVAR 000001` → pagamento confirmado, estoque baixado,
   cliente avisado automaticamente. `RECUSAR 000001` avisa o cliente pra reenviar o comprovante.
7. Você manda `PRONTO 000001` quando separar o pedido, e
   `ENVIAR 000001 ABC123456BR` quando despachar — o cliente recebe cada
   atualização automaticamente.
8. A qualquer momento você pode mandar `STATUS 000001` para ver os detalhes.

## 7. Regras de segurança já implementadas

- **Somente administradores cadastrados na coleção `administradores`** podem
  executar `APROVAR`, `RECUSAR`, `STATUS`, `PRONTO`, `ENVIAR` ou `CANCELAR`
  (checado em `interfaces/api/routers/WebhookRouter.py` antes de rotear pro `AdminComandoHandler`).
- O **Claude nunca recebe `cliente_id` como parâmetro de ferramenta** — ele é
  sempre injetado pelo backend (`AgenteAtendimentoService`), então não é possível a IA
  (ou uma injeção de prompt) manipular o pedido de outro cliente.
- **Preço, estoque e status de pagamento nunca são decididos pelo modelo** —
  toda essa informação vem dos usecases em `application/usecases/`, que consultam o Mongo.
- A baixa de estoque e a confirmação de pagamento acontecem dentro do mesmo
  usecase (`ConfirmarPagamentoUseCase`), evitando o cenário de "pagamento
  confirmado mas estoque não baixou".

## 8. Testes

```bash
pip install -r src/requirements-dev.txt
pytest
```

Os testes rodam inteiramente em memória (`mongomock` no lugar do Mongo real, e
fakes dos gateways de WhatsApp/Claude), cobrindo entidades de domínio, usecases,
o serviço do agente e a aplicação FastAPI de ponta a ponta.

## 9. Próximos passos sugeridos

- Adicionar um cron/agendador (ex: `cron`, Task Scheduler do Windows, ou
  `APScheduler`) para rodar backups diários do MongoDB e de `data/comprovantes/`.
- Se quiser um painel web além dos comandos por WhatsApp, dá para expor rotas
  FastAPI adicionais lendo as mesmas coleções.
