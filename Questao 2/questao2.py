import sys
import json
import time
import base64
from http.cookies import SimpleCookie

import scrapy
from scrapy.crawler import CrawlerProcess
from scrapy.exceptions import CloseSpider


class ServimedSpider(scrapy.Spider):
    name = "servimed_pedido"

    handle_httpstatus_list = [400, 401, 403, 404, 500]

    custom_settings = {
        "LOG_LEVEL": "INFO",
        "ROBOTSTXT_OBEY": False,
        "COOKIES_ENABLED": True,
        "DEFAULT_REQUEST_HEADERS": {
            "User-Agent": (
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/142.0.0.0 Safari/537.36"
            ),
            "Accept": "application/json, text/plain, */*",
            "Accept-Language": "pt-BR,pt;q=0.9,en-US;q=0.8,en;q=0.7",
        },
        "RETRY_ENABLED": True,
        "RETRY_TIMES": 1,
    }

    LOGIN_URL = "https://peapi.servimed.com.br/api/usuario/login"
    CLIENTE_FILTER_URL = "https://peapi.servimed.com.br/api/cliente/findByFilter"
    BASE_PEDIDO_URL = "https://peapi.servimed.com.br/api/Pedido"

    def __init__(self, pedido_id=None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if not pedido_id:
            raise CloseSpider("Nenhum número de pedido informado.")
        self.pedido_id = str(pedido_id)

        self.codigo_usuario = None      
        self.access_token_guid = None   

    def _api_headers(
        self,
        referer=None,
        json_body=False,
        loggeduser=None,
        accesstoken=None,
        extra=None,
    ):
        headers = {
            "Accept": "application/json, text/plain, */*",
            "Accept-Language": "pt-BR,pt;q=0.9,en-US;q=0.8,en;q=0.7",
            "Origin": "https://pedidoeletronico.servimed.com.br",
        }
        if referer:
            headers["Referer"] = referer
        if json_body:
            headers["Content-Type"] = "application/json"
            headers["contenttype"] = "application/json"
        if loggeduser is not None:
            headers["loggeduser"] = str(loggeduser)
        if accesstoken:
            headers["accesstoken"] = accesstoken
        if extra:
            headers.update(extra)
        return headers

    @staticmethod
    def _decode_jwt_payload(jwt_token):
        try:
            parts = jwt_token.split(".")
            if len(parts) < 2:
                return {}
            payload_b64 = parts[1] + "=" * (-len(parts[1]) % 4)
            payload_bytes = base64.urlsafe_b64decode(payload_b64.encode("utf-8"))
            return json.loads(payload_bytes.decode("utf-8"))
        except Exception:
            return {}

    def _extract_from_cookies(self, response):
        cookies = {}
        for raw_cookie in response.headers.getlist(b"Set-Cookie"):
            c = SimpleCookie()
            c.load(raw_cookie.decode("utf-8"))
            for k, morsel in c.items():
                cookies[k] = morsel.value

        jwt_cookie = cookies.get("accesstoken") or cookies.get("sessiontoken")
        if not jwt_cookie:
            self.logger.warning("Nenhum cookie JWT 'accesstoken/sessiontoken' encontrado.")
            return

        payload = self._decode_jwt_payload(jwt_cookie)

        self.codigo_usuario = payload.get("codigoUsuario")
        self.access_token_guid = payload.get("token")

        self.logger.info(
            "Dados extraídos do JWT: codigoUsuario=%s, token(accesstoken)=%s",
            self.codigo_usuario,
            self.access_token_guid,
        )


    def start_requests(self):
        payload = {
            "usuario": "juliano@farmaprevonline.com.br",
            "senha": "a007299A",
        }

        yield scrapy.Request(
            self.LOGIN_URL,
            method="POST",
            body=json.dumps(payload),
            headers=self._api_headers(
                referer="https://pedidoeletronico.servimed.com.br/",
                json_body=True,
                loggeduser=0,  
            ),
            callback=self.after_login,
            dont_filter=True,
        )

    def after_login(self, response):
        if response.status != 200:
            self.logger.error(
                "Login HTTP %s. Corpo da resposta:\n%s",
                response.status,
                response.text,
            )
            raise CloseSpider(
                f"Falha ao efetuar login na API da Servimed (HTTP {response.status})."
            )

        self._extract_from_cookies(response)

        if self.codigo_usuario is None:
            self.logger.warning(
                "codigoUsuario não encontrado no JWT. Usando 22850 como fallback."
            )
            self.codigo_usuario = 22850

        self.logger.info(
            "Login efetuado com sucesso. codigoUsuario=%s. Iniciando findByFilter...",
            self.codigo_usuario,
        )

        find_payload = {
            "filtro": "",
            "pagina": 1,
            "registrosPorPagina": 20,
            "codigoExterno": 518565,
            "codigoUsuario": self.codigo_usuario,
            "kindUser": 2,
            "checked": False,
            "master": False,
            "users": [518565, 267511],
        }

        yield scrapy.Request(
            self.CLIENTE_FILTER_URL,
            method="POST",
            body=json.dumps(find_payload),
            headers=self._api_headers(
                referer="https://pedidoeletronico.servimed.com.br/",
                json_body=True,
                loggeduser=self.codigo_usuario,
                accesstoken=self.access_token_guid,
            ),
            callback=self.after_find_by_filter,
            dont_filter=True,
        )

    def after_find_by_filter(self, response):
        if response.status != 200:
            self.logger.error(
                "findByFilter HTTP %s. Corpo:\n%s",
                response.status,
                response.text,
            )
            raise CloseSpider(
                f"Falha ao inicializar contexto do cliente (HTTP {response.status})."
            )

        self.logger.info(
            "findByFilter concluído com sucesso. Procurando pedido %s",
            self.pedido_id,
        )

        url = (
            f"{self.BASE_PEDIDO_URL}/ObterTodasInformacoesPedidoPendentePorId/"
            f"{self.pedido_id}"
        )

        headers = self._api_headers(
            referer="https://pedidoeletronico.servimed.com.br/",
            loggeduser=self.codigo_usuario,
            accesstoken=self.access_token_guid,
            extra={
                "x-peperone": str(int(time.time() * 1000)),
                "x-cart": "scrapy-cart-placeholder",
            },
        )

        yield scrapy.Request(
            url,
            method="GET",
            headers=headers,
            callback=self.parse_pedido,
            dont_filter=True,
        )

    def parse_pedido(self, response):
        if response.status == 404:
            msg = f"Pedido {self.pedido_id} não encontrado."
            sys.stderr.write(msg + "\n")
            raise CloseSpider(msg)

        if response.status != 200:
            self.logger.error(
                "Erro ao buscar pedido (HTTP %s). Corpo:\n%s",
                response.status,
                response.text,
            )
            raise CloseSpider(
                f"Falha ao buscar informações do pedido (HTTP {response.status})."
            )

        try:
            data = json.loads(response.text or "{}")
        except ValueError:
            raise CloseSpider("Resposta inválida ao buscar pedido.")

        motivo = (
            data.get("rejeicao")
            or data.get("motivoRejeicao")
            or data.get("MotivoRejeicao")
            or ""
        )

        raw_itens = data.get("itens") or []

        itens = []
        for it in raw_itens:
            produto = it.get("produto") or {}

            codigo = (
                it.get("produtoCodigoExterno")
                or produto.get("codigoExterno")
                or produto.get("codigo")
            )
            descricao = (
                produto.get("descricao")
                or produto.get("descricaoSintetica")
                or produto.get("descricaoCompleta")
            )
            qtd_faturada = it.get("quantidadeFaturada")
            if qtd_faturada is None:
                qtd_faturada = 0

            itens.append(
                {
                    "codigo_produto": codigo,
                    "descricao": descricao,
                    "quantidade_faturada": qtd_faturada,
                }
            )

        resultado = {
            "motivo": motivo,
            "itens": itens,
        }

        filename = f"pedido_{self.pedido_id}.json"
        with open(filename, "w", encoding="utf-8") as f:
            json.dump(resultado, f, ensure_ascii=False, indent=2)
        self.logger.info("Resultado salvo em %s", filename)

        print(json.dumps(resultado, ensure_ascii=False))


def main():
    if len(sys.argv) != 2:
        print("Uso: python seumodulo.py <numero_pedido>")
        sys.exit(1)

    pedido_id = sys.argv[1]

    process = CrawlerProcess()
    process.crawl(ServimedSpider, pedido_id=pedido_id)
    process.start()


if __name__ == "__main__":
    main()