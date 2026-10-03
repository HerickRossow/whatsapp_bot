from datetime import datetime

from ...domain.entities.Cliente import Cliente
from ...domain.entities.Comprovante import Comprovante
from ...domain.enums.StatusPedido import StatusPedido
from ...domain.gateways.ArmazenamentoArquivos import ArmazenamentoArquivos
from ...domain.gateways.WhatsAppGateway import WhatsAppGateway
from ...domain.repositories.ComprovanteRepository import ComprovanteRepository
from ...domain.repositories.PedidoRepository import PedidoRepository
from ...domain.value_objects.Telefone import Telefone

EXTENSAO_POR_MIME = {
    "image/jpeg": "jpg",
    "image/png": "png",
    "image/webp": "webp",
}


class ProcessarComprovanteUseCase:
    def __init__(self, pedido_repository: PedidoRepository, comprovante_repository: ComprovanteRepository,
                 whatsapp_gateway: WhatsAppGateway, armazenamento: ArmazenamentoArquivos,
                 admin_whatsapp: Telefone):
        self._pedido_repository = pedido_repository
        self._comprovante_repository = comprovante_repository
        self._whatsapp_gateway = whatsapp_gateway
        self._armazenamento = armazenamento
        self._admin_whatsapp = admin_whatsapp

    def executar(self, cliente: Cliente, media_id: str, mime_type: str) -> str:
        pedido = self._pedido_repository.buscar_aberto_por_cliente(cliente.id)
        if pedido is None or pedido.status not in (
            StatusPedido.AGUARDANDO_PAGAMENTO,
            StatusPedido.PAGAMENTO_NAO_CONFIRMADO,
        ):
            return (
                "Recebi sua imagem, mas não encontrei um pedido aguardando pagamento no momento. "
                "Se você já fechou um pedido, me avise o número dele. 🙂"
            )

        conteudo = self._whatsapp_gateway.baixar_midia(media_id)
        nome_arquivo = self._nome_arquivo(pedido.numero_pedido, cliente.nome, cliente.whatsapp.numero, mime_type)
        caminho = self._armazenamento.salvar(nome_arquivo, conteudo)

        self._comprovante_repository.salvar(
            Comprovante(pedido_id=pedido.id, cliente_id=cliente.id, arquivo=caminho, nome_arquivo=nome_arquivo)
        )
        pedido.marcar_comprovante_recebido()
        self._pedido_repository.salvar(pedido)

        self._notificar_admin(pedido, cliente, caminho, mime_type)

        return (
            "Recebi seu comprovante! ✅ Vou encaminhar para conferência e assim que for "
            "aprovado eu te aviso por aqui. 🙌"
        )

    def _notificar_admin(self, pedido, cliente: Cliente, caminho_arquivo: str, mime_type: str) -> None:
        linhas_itens = "\n".join(f"{item.quantidade}x {item.nome}" for item in pedido.itens)
        texto = (
            "🚨 NOVO COMPROVANTE DE PAGAMENTO\n\n"
            f"📋 Pedido: #{pedido.numero_pedido}\n\n"
            f"👤 Cliente: {cliente.nome or 'não informado'}\n"
            f"📱 WhatsApp: {cliente.whatsapp.numero}\n\n"
            f"🛒 PEDIDO:\n{linhas_itens}\n\n"
            f"💰 TOTAL: R$ {pedido.total.valor:.2f}\n"
            "💳 PAGAMENTO: PIX\n"
            "⚠️ STATUS: AGUARDANDO CONFERÊNCIA\n\n"
            f"Responda: APROVAR {pedido.numero_pedido} ou RECUSAR {pedido.numero_pedido}"
        )
        self._whatsapp_gateway.enviar_texto(self._admin_whatsapp, texto)
        self._whatsapp_gateway.enviar_imagem(self._admin_whatsapp, caminho_arquivo, mime_type=mime_type or "image/jpeg")

    @staticmethod
    def _nome_arquivo(numero_pedido: str, nome_cliente: str, telefone: str, mime_type: str) -> str:
        extensao = EXTENSAO_POR_MIME.get(mime_type, "jpg")
        nome_limpo = (nome_cliente or "cliente").strip().replace(" ", "_")
        agora = datetime.now().strftime("%Y%m%d_%H%M%S")
        return f"PEDIDO_{numero_pedido}_{nome_limpo}_{telefone}_{agora}.{extensao}"
