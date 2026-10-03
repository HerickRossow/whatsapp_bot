from typing import Optional

from pymongo.database import Database

from ..application.services.AgenteAtendimentoService import AgenteAtendimentoService
from ..application.usecases.AdicionarItemCarrinhoUseCase import AdicionarItemCarrinhoUseCase
from ..application.usecases.BuscarProdutosUseCase import BuscarProdutosUseCase
from ..application.usecases.CalcularCarrinhoUseCase import CalcularCarrinhoUseCase
from ..application.usecases.CancelarPedidoUseCase import CancelarPedidoUseCase
from ..application.usecases.ConfirmarPagamentoUseCase import ConfirmarPagamentoUseCase
from ..application.usecases.ConsultarCarrinhoUseCase import ConsultarCarrinhoUseCase
from ..application.usecases.ConsultarFreteUseCase import ConsultarFreteUseCase
from ..application.usecases.ConsultarPedidoUseCase import ConsultarPedidoUseCase
from ..application.usecases.ConsultarStatusPedidoUseCase import ConsultarStatusPedidoUseCase
from ..application.usecases.CriarPedidoUseCase import CriarPedidoUseCase
from ..application.usecases.MarcarPedidoEnviadoUseCase import MarcarPedidoEnviadoUseCase
from ..application.usecases.MarcarPedidoProntoUseCase import MarcarPedidoProntoUseCase
from ..application.usecases.ObterDetalhesProdutoUseCase import ObterDetalhesProdutoUseCase
from ..application.usecases.ObterOuCriarClienteUseCase import ObterOuCriarClienteUseCase
from ..application.usecases.ObterPedidoParaAdminUseCase import ObterPedidoParaAdminUseCase
from ..application.usecases.ProcessarComprovanteUseCase import ProcessarComprovanteUseCase
from ..application.usecases.RecusarPagamentoUseCase import RecusarPagamentoUseCase
from ..application.usecases.RemoverItemCarrinhoUseCase import RemoverItemCarrinhoUseCase
from ..application.usecases.SincronizarCatalogoUseCase import SincronizarCatalogoUseCase
from ..application.usecases.TransferirParaHumanoUseCase import TransferirParaHumanoUseCase
from ..domain.gateways.ArmazenamentoArquivos import ArmazenamentoArquivos
from ..domain.gateways.AssistenteIAGateway import AssistenteIAGateway
from ..domain.gateways.WhatsAppGateway import WhatsAppGateway
from ..domain.value_objects.Dinheiro import Dinheiro
from ..domain.value_objects.Telefone import Telefone
from .config.Settings import Settings
from .database.MongoConnection import criar_indices, obter_database
from .external.AnthropicAssistenteGateway import AnthropicAssistenteGateway
from .external.ArmazenamentoLocalArquivos import ArmazenamentoLocalArquivos
from .external.MetaWhatsAppGateway import MetaWhatsAppGateway
from .repositories.MongoAdministradorRepository import MongoAdministradorRepository
from .repositories.MongoCarrinhoRepository import MongoCarrinhoRepository
from .repositories.MongoClienteRepository import MongoClienteRepository
from .repositories.MongoComprovanteRepository import MongoComprovanteRepository
from .repositories.MongoConfiguracaoRepository import MongoConfiguracaoRepository
from .repositories.MongoConversaRepository import MongoConversaRepository
from .repositories.MongoPagamentoRepository import MongoPagamentoRepository
from .repositories.MongoPedidoRepository import MongoPedidoRepository
from .repositories.MongoProdutoRepository import MongoProdutoRepository


class Container:
    """Raiz de composição: constrói e conecta repositórios, gateways, usecases e serviços."""

    def __init__(self, settings: Settings, database: Optional[Database] = None,
                 whatsapp_gateway: Optional[WhatsAppGateway] = None,
                 assistente_gateway: Optional[AssistenteIAGateway] = None,
                 armazenamento: Optional[ArmazenamentoArquivos] = None):
        self.settings = settings
        self.database = database or obter_database()
        criar_indices(self.database)

        self.cliente_repository = MongoClienteRepository(self.database)
        self.produto_repository = MongoProdutoRepository(self.database)
        self.carrinho_repository = MongoCarrinhoRepository(self.database)
        self.pedido_repository = MongoPedidoRepository(self.database)
        self.pagamento_repository = MongoPagamentoRepository(self.database)
        self.comprovante_repository = MongoComprovanteRepository(self.database)
        self.conversa_repository = MongoConversaRepository(self.database)
        self.administrador_repository = MongoAdministradorRepository(self.database)
        self.configuracao_repository = MongoConfiguracaoRepository(self.database)

        self.whatsapp_gateway = whatsapp_gateway or MetaWhatsAppGateway(settings)
        self.armazenamento = armazenamento or ArmazenamentoLocalArquivos(settings.comprovantes_dir)
        self.assistente_gateway = assistente_gateway or AnthropicAssistenteGateway(
            settings.anthropic_api_key, settings.anthropic_model
        )

        self.obter_ou_criar_cliente_usecase = ObterOuCriarClienteUseCase(self.cliente_repository)
        self.buscar_produtos_usecase = BuscarProdutosUseCase(self.produto_repository)
        self.obter_detalhes_produto_usecase = ObterDetalhesProdutoUseCase(self.produto_repository)
        self.sincronizar_catalogo_usecase = SincronizarCatalogoUseCase(self.produto_repository)

        self.consultar_carrinho_usecase = ConsultarCarrinhoUseCase(self.carrinho_repository)
        self.adicionar_item_carrinho_usecase = AdicionarItemCarrinhoUseCase(
            self.carrinho_repository, self.produto_repository
        )
        self.remover_item_carrinho_usecase = RemoverItemCarrinhoUseCase(self.carrinho_repository)
        self.consultar_frete_usecase = ConsultarFreteUseCase(
            self.configuracao_repository, Dinheiro(settings.frete_padrao)
        )
        self.calcular_carrinho_usecase = CalcularCarrinhoUseCase(
            self.carrinho_repository, self.consultar_frete_usecase
        )
        self.criar_pedido_usecase = CriarPedidoUseCase(
            self.carrinho_repository, self.pedido_repository, self.pagamento_repository, self.consultar_frete_usecase
        )
        self.consultar_pedido_usecase = ConsultarPedidoUseCase(self.pedido_repository)
        self.consultar_status_pedido_usecase = ConsultarStatusPedidoUseCase(self.pedido_repository)
        self.transferir_para_humano_usecase = TransferirParaHumanoUseCase(self.pedido_repository)

        self.confirmar_pagamento_usecase = ConfirmarPagamentoUseCase(
            self.pedido_repository, self.cliente_repository, self.whatsapp_gateway,
            self.pagamento_repository, self.produto_repository,
        )
        self.recusar_pagamento_usecase = RecusarPagamentoUseCase(
            self.pedido_repository, self.cliente_repository, self.whatsapp_gateway, self.pagamento_repository
        )
        self.marcar_pedido_pronto_usecase = MarcarPedidoProntoUseCase(
            self.pedido_repository, self.cliente_repository, self.whatsapp_gateway
        )
        self.marcar_pedido_enviado_usecase = MarcarPedidoEnviadoUseCase(
            self.pedido_repository, self.cliente_repository, self.whatsapp_gateway
        )
        self.cancelar_pedido_usecase = CancelarPedidoUseCase(
            self.pedido_repository, self.cliente_repository, self.whatsapp_gateway
        )
        self.obter_pedido_para_admin_usecase = ObterPedidoParaAdminUseCase(
            self.pedido_repository, self.cliente_repository
        )
        self.processar_comprovante_usecase = ProcessarComprovanteUseCase(
            self.pedido_repository, self.comprovante_repository, self.whatsapp_gateway,
            self.armazenamento, Telefone(settings.admin_whatsapp),
        )

        self.agente_atendimento_service = AgenteAtendimentoService(
            assistente_gateway=self.assistente_gateway,
            pedido_repository=self.pedido_repository,
            conversa_repository=self.conversa_repository,
            configuracao_repository=self.configuracao_repository,
            buscar_produtos_usecase=self.buscar_produtos_usecase,
            obter_detalhes_produto_usecase=self.obter_detalhes_produto_usecase,
            consultar_carrinho_usecase=self.consultar_carrinho_usecase,
            adicionar_item_carrinho_usecase=self.adicionar_item_carrinho_usecase,
            remover_item_carrinho_usecase=self.remover_item_carrinho_usecase,
            calcular_carrinho_usecase=self.calcular_carrinho_usecase,
            consultar_frete_usecase=self.consultar_frete_usecase,
            criar_pedido_usecase=self.criar_pedido_usecase,
            consultar_pedido_usecase=self.consultar_pedido_usecase,
            consultar_status_pedido_usecase=self.consultar_status_pedido_usecase,
            transferir_para_humano_usecase=self.transferir_para_humano_usecase,
            nome_loja_padrao=settings.nome_loja,
        )
