import anthropic

from ...domain.gateways.AssistenteIAGateway import AssistenteIAGateway
from ...domain.value_objects.ChamadaFerramenta import ChamadaFerramenta
from ...domain.value_objects.RespostaAssistente import RespostaAssistente


class AnthropicAssistenteGateway(AssistenteIAGateway):
    def __init__(self, api_key: str, modelo: str, max_tokens: int = 1024):
        self._cliente = anthropic.Anthropic(api_key=api_key)
        self._modelo = modelo
        self._max_tokens = max_tokens

    def obter_proxima_resposta(self, system: str, mensagens: list, ferramentas: list) -> RespostaAssistente:
        resposta = self._cliente.messages.create(
            model=self._modelo,
            max_tokens=self._max_tokens,
            system=system,
            tools=ferramentas,
            messages=mensagens,
        )

        mensagens_atualizadas = mensagens + [{"role": "assistant", "content": resposta.content}]

        if resposta.stop_reason != "tool_use":
            textos = [bloco.text for bloco in resposta.content if bloco.type == "text"]
            return RespostaAssistente(mensagens=mensagens_atualizadas, texto_final="\n".join(textos).strip())

        chamadas = [
            ChamadaFerramenta(id=bloco.id, nome=bloco.name, argumentos=bloco.input)
            for bloco in resposta.content
            if bloco.type == "tool_use"
        ]
        return RespostaAssistente(mensagens=mensagens_atualizadas, chamadas_ferramenta=chamadas)
