# Bot de Vendas no WhatsApp — Suplementos

Aplicação Python pronta para execução que implementa a arquitetura que definimos:

```
WhatsApp Cliente → Meta WhatsApp Cloud API → Python (Flask) → Claude (tool use)
                                                    │
                                                    ├── SQLite (clientes/produtos/pedidos/pagamentos)
                                                    ├── Excel (catálogo, editável por você)
                                                    ├── Comprovantes (arquivos locais)
                                                    └── WhatsApp administrativo (aprova/recusa)
```

**Diferença importante em relação ao desenho original:** aqui o **n8n foi substituído
por código Python direto** (este próprio repositório). Isso elimina a necessidade de
Docker/n8n e de expor volumes entre Windows e container — é só rodar `python app.py`.
Toda a lógica que estava nos workflows (WF00 a WF11) está implementada nos módulos
abaixo. Se no futuro você quiser reintroduzir o n8n para alguma parte específica,
dá para fazer isso chamando as mesmas rotas HTTP (`/webhook`, `/sync-produtos`).

## Estrutura do projeto

```
whatsapp_bot/
├── app.py               # Servidor Flask: webhook do WhatsApp, roteamento das mensagens
├── config.py            # Lê o .env e define caminhos/parâmetros
├── db.py                # Schema SQLite + funções de acesso (clientes, pedidos, etc.)
├── status.py             # Constantes da máquina de estados dos pedidos
├── whatsapp_client.py    # Cliente da WhatsApp Cloud API (enviar/receber/baixar mídia)
├── tools.py              # Ferramentas que o Claude pode chamar (nunca inventa dado)
├── tool_schemas.py        # Definição das ferramentas no formato da API do Claude
├── claude_agent.py        # Monta contexto, chama o Claude, executa o loop de tool use
├── media_handler.py       # Processa comprovantes de pagamento (imagens)
├── admin_commands.py      # APROVAR / RECUSAR / STATUS / PRONTO / ENVIAR / CANCELAR
├── excel_sync.py          # Sincroniza produtos.xlsx -> SQLite
├── scripts/
│   ├── seed_admin.py      # Cadastra o número administrativo no banco
│   └── init_tudo.py       # Inicializa banco + Excel de exemplo + admin, tudo de uma vez
├── data/
│   ├── banco/loja.db      # Banco SQLite (criado automaticamente)
│   ├── produtos/produtos.xlsx  # Catálogo (você edita este arquivo)
│   ├── comprovantes/AAAA/MM/DD # Comprovantes recebidos, organizados por data
│   ├── logs/               # Logs da aplicação
│   └── backups/            # Onde você pode copiar backups periódicos
├── requirements.txt
└── .env.example
```

## 1. Pré-requisitos

- Python 3.10+
- Uma conta **Meta for Developers** com um app configurado para **WhatsApp Business
  Cloud API** (Phone Number ID, WhatsApp Business Account ID e um token de acesso).
- Uma **API key da Anthropic** (console.anthropic.com).
- Para testar localmente antes de ter um domínio público, algo como `ngrok` para
  expor a porta 5000 e configurar o webhook da Meta.

## 2. Instalação

```bash
cd whatsapp_bot
python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env
```

Edite o `.env` com:
- `WHATSAPP_TOKEN`, `WHATSAPP_PHONE_NUMBER_ID`: obtidos no painel da Meta.
- `WHATSAPP_VERIFY_TOKEN`: uma frase qualquer, que você também vai colocar na
  configuração do webhook no painel da Meta.
- `ANTHROPIC_API_KEY`: sua chave da API do Claude.
- `ADMIN_WHATSAPP`: o número que vai aprovar pagamentos (formato `55DDDNUMERO`, sem `+`).
- `PIX_CHAVE`, `PIX_NOME`, `PIX_BANCO`: dados do PIX fixo da loja.

## 3. Inicialização (uma vez)

```bash
python scripts/init_tudo.py
```

Isso vai:
1. Criar o banco SQLite com todas as tabelas (`clientes`, `produtos`, `pedidos`,
   `pedido_itens`, `carrinho`, `pagamentos`, `comprovantes`, `conversas`,
   `administradores`, `configuracoes`).
2. Criar um `data/produtos/produtos.xlsx` de exemplo (se ainda não existir).
3. Sincronizar esse Excel para o SQLite.
4. Cadastrar o `ADMIN_WHATSAPP` do `.env` como administrador ativo.

Depois de editar o catálogo no Excel, sincronize de novo com:

```bash
python excel_sync.py
```

ou chamando `POST /sync-produtos` no servidor rodando.

## 4. Rodar o servidor

```bash
python AppRouters.py
```

O servidor sobe em `http://0.0.0.0:5000`. Para produção, use `gunicorn`:

```bash
gunicorn -w 2 -b 0.0.0.0:5000 app:app
```

## 5. Expor o webhook para a Meta (teste local)

```bash
ngrok http 5000
```

No painel da Meta (WhatsApp > Configuration > Webhook):
- **Callback URL**: `https://SEU-DOMINIO-NGROK/webhook`
- **Verify token**: o mesmo valor de `WHATSAPP_VERIFY_TOKEN` no `.env`
- Assine (subscribe) o campo `messages`.

## 6. Fluxo de teste ponta a ponta

1. Cliente manda "Oi" → bot responde naturalmente (Claude).
2. Cliente pergunta "Tem creatina?" → bot chama `buscar_produtos`, responde com
   preço real do banco.
3. Cliente: "Quero 2" → bot chama `adicionar_carrinho`.
4. Cliente: "Pode fechar" → bot chama `criar_pedido`, envia dados do PIX.
5. Cliente envia a foto do comprovante → sistema salva o arquivo em
   `data/comprovantes/AAAA/MM/DD/`, registra no banco e **envia automaticamente
   para o número administrativo** com os dados do pedido + a imagem.
6. Você (admin) responde `APROVAR 000001` → pagamento confirmado, estoque baixado
   em transação atômica, cliente avisado automaticamente.
   Se mandar `RECUSAR 000001`, o cliente é avisado para reenviar o comprovante.
7. Você manda `PRONTO 000001` quando separar o pedido, e
   `ENVIAR 000001 ABC123456BR` quando despachar — o cliente recebe cada
   atualização automaticamente.
8. A qualquer momento você pode mandar `STATUS 000001` para ver os detalhes.

## 7. Regras de segurança já implementadas

- **Somente o `ADMIN_WHATSAPP` cadastrado na tabela `administradores`** pode
  executar `APROVAR`, `RECUSAR`, `STATUS`, `PRONTO`, `ENVIAR` ou `CANCELAR`
  (`db.is_admin`, checado em `src/infra/router/AppRouters.py` antes de rotear para `old_project/admin_commands.py`).
- O **Claude nunca recebe `cliente_id` como parâmetro de ferramenta** — ele é
  sempre injetado pelo backend (`old_project/claude_agent.py`), então não é possível a IA
  (ou uma injeção de prompt) manipular o pedido de outro cliente.
- **Preço, estoque e status de pagamento nunca são decididos pelo modelo** —
  toda essa informação vem de consultas SQL em `old_project/tools.py`.
- A baixa de estoque e a confirmação de pagamento acontecem **na mesma
  transação SQLite** (`admin_commands._aprovar`), evitando o cenário de
  "pagamento confirmado mas estoque não baixou".
- Erros de processamento são registrados na tabela `erros` e, quando possível,
  um alerta é enviado automaticamente para o WhatsApp administrativo.

## 8. Próximos passos sugeridos

- Adicionar um cron/agendador (ex: `cron`, Task Scheduler do Windows, ou
  `APScheduler`) para rodar backups diários de `data/banco/loja.db`,
  `data/produtos/produtos.xlsx` e `data/comprovantes/` para `data/backups/`.
- Se o catálogo crescer muito, trocar o SQLite por Postgres é uma troca simples
  (as consultas em `old_project/tools.py`/`old_project/db.py` usam SQL padrão).
- Se quiser um painel web além dos comandos por WhatsApp, dá para expor rotas
  Flask adicionais lendo as mesmas tabelas.
