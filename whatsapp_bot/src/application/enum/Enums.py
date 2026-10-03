import enum

class Status (enum):
    NOVO = "NOVO"
    ATENDIMENTO = "ATENDIMENTO"
    CARRINHO = "CARRINHO"
    AGUARDANDO_CONFIRMACAO = "AGUARDANDO_CONFIRMACAO"
    AGUARDANDO_DADOS = "AGUARDANDO_DADOS"
    AGUARDANDO_PAGAMENTO = "AGUARDANDO_PAGAMENTO"
    COMPROVANTE_RECEBIDO = "COMPROVANTE_RECEBIDO"
    AGUARDANDO_CONFERENCIA = "AGUARDANDO_CONFERENCIA"
    PAGAMENTO_CONFIRMADO = "PAGAMENTO_CONFIRMADO"
    SEPARANDO = "SEPARANDO"
    PRONTO = "PRONTO"
    ENVIADO = "ENVIADO"
    FINALIZADO = "FINALIZADO"
    CANCELADO = "CANCELADO"
    HUMANO = "HUMANO"
    PAGAMENTO_NAO_CONFIRMADO = "PAGAMENTO_NAO_CONFIRMADO"


class Open (enum):
    Novo = "Novo"
    Atendimento = "Atendimento"
    Carrinho = "Carrinho"
    Aguardando_Confirmacao = "Aguardando_Confirmacao"
    Aguardando_Dados = "Aguardando_Dados"
    Aguardando_Pagamento = "Aguardando_Pagamento"
    Comprovante_Recebido = "Comprovante_Recebido"
    Aguardando_Conferencia = "Aguardando_Conferencia"
    Pagamento_Confirmado = "Pagamento_Confirmado"
    Separando = "Separando"
    Pronto = "Pronto"
    Humano = "Humano"


class Pagamento (enum):
    Pagamento_Nao_Confirmado = "Pagamento_Nao_Confirmado"
    Pagamento_Pendente = "Pagamento_Pendente"
    Pagamento_Confirmado_Status = "Pagamento_Confirmado_Status"
    Pagamento_Recusado = "Pagamento_Recusado"