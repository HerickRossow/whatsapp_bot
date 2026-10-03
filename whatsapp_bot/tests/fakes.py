from src.domain.value_objects.RespostaAssistente import RespostaAssistente


class WhatsAppGatewayFake:
    def __init__(self):
        self.mensagens = []
        self.imagens = []

    def enviar_texto(self, telefone, mensagem):
        self.mensagens.append((telefone.numero, mensagem))

    def enviar_imagem(self, telefone, caminho_arquivo, legenda=None, mime_type="image/jpeg"):
        self.imagens.append((telefone.numero, caminho_arquivo, mime_type))

    def baixar_midia(self, media_id):
        return b"conteudo-fake-da-imagem"


class ArmazenamentoArquivosFake:
    def __init__(self):
        self.arquivos = {}

    def salvar(self, nome_arquivo, conteudo):
        self.arquivos[nome_arquivo] = conteudo
        return f"/fake/{nome_arquivo}"


class AssistenteIAGatewayFake:
    def __init__(self, roteiro=None):
        self._roteiro = roteiro or []
        self._indice = 0
        self.chamadas_recebidas = []

    def obter_proxima_resposta(self, system, mensagens, ferramentas):
        self.chamadas_recebidas.append((system, list(mensagens), ferramentas))
        if self._indice < len(self._roteiro):
            resposta = self._roteiro[self._indice]
            self._indice += 1
        else:
            resposta = RespostaAssistente(mensagens=[], texto_final="ok")
        resposta.mensagens = mensagens + [{"role": "assistant", "content": "fake-assistant-turn"}]
        return resposta
