"""
Definições das ferramentas no formato exigido pela API do Claude (tool use).
Note que 'cliente_id' NUNCA aparece aqui -- é injetado pelo backend, nunca pelo modelo.
"""

TOOLS = [
    {
        "name": "buscar_produtos",
        "description": "Busca produtos ativos e com estoque no catálogo por nome, marca, categoria ou sabor.",
        "input_schema": {
            "type": "object",
            "properties": {
                "consulta": {"type": "string", "description": "Termo de busca, ex: 'creatina', 'whey chocolate'."}
            },
            "required": ["consulta"],
        },
    },
    {
        "name": "buscar_produto",
        "description": "Busca os detalhes completos de um produto específico pelo id.",
        "input_schema": {
            "type": "object",
            "properties": {"produto_id": {"type": "integer"}},
            "required": ["produto_id"],
        },
    },
    {
        "name": "consultar_estoque",
        "description": "Consulta o estoque atual de um produto pelo id.",
        "input_schema": {
            "type": "object",
            "properties": {"produto_id": {"type": "integer"}},
            "required": ["produto_id"],
        },
    },
    {
        "name": "consultar_carrinho",
        "description": "Lista os itens atualmente no carrinho do cliente.",
        "input_schema": {"type": "object", "properties": {}},
    },
    {
        "name": "adicionar_carrinho",
        "description": "Adiciona uma quantidade de um produto ao carrinho do cliente, validando estoque.",
        "input_schema": {
            "type": "object",
            "properties": {
                "produto_id": {"type": "integer"},
                "quantidade": {"type": "integer"},
                "sabor": {"type": "string", "description": "Sabor escolhido, se aplicável."},
            },
            "required": ["produto_id", "quantidade"],
        },
    },
    {
        "name": "remover_carrinho",
        "description": "Remove um produto do carrinho do cliente.",
        "input_schema": {
            "type": "object",
            "properties": {"produto_id": {"type": "integer"}},
            "required": ["produto_id"],
        },
    },
    {
        "name": "calcular_carrinho",
        "description": "Calcula subtotal, frete e total do carrinho atual. Use sempre antes de informar valores ao cliente.",
        "input_schema": {"type": "object", "properties": {}},
    },
    {
        "name": "consultar_frete",
        "description": "Consulta o valor de frete padrão da loja.",
        "input_schema": {"type": "object", "properties": {}},
    },
    {
        "name": "criar_pedido",
        "description": "Fecha o carrinho atual em um pedido oficial, aguardando pagamento via PIX. "
                        "Só chame depois que o cliente confirmar explicitamente que quer fechar o pedido.",
        "input_schema": {"type": "object", "properties": {}},
    },
    {
        "name": "consultar_pedido",
        "description": "Consulta os dados de um pedido do cliente (o mais recente, se numero_pedido não for informado).",
        "input_schema": {
            "type": "object",
            "properties": {"numero_pedido": {"type": "string"}},
        },
    },
    {
        "name": "consultar_status_pedido",
        "description": "Consulta apenas o status atual de um pedido pelo número.",
        "input_schema": {
            "type": "object",
            "properties": {"numero_pedido": {"type": "string"}},
            "required": ["numero_pedido"],
        },
    },
    {
        "name": "transferir_humano",
        "description": "Transfere o atendimento para um humano quando o assunto exigir "
                        "(ex: reclamação complexa, pedido de exceção, dúvida médica).",
        "input_schema": {
            "type": "object",
            "properties": {"motivo": {"type": "string"}},
            "required": ["motivo"],
        },
    },
]
