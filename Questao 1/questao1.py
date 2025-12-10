import json
import math
import sys
import time
from typing import Dict, Any, List

import requests
from nacl.secret import SecretBox
from nacl.encoding import Base64Encoder


GRAPHQL_URL = "https://novo.compra-agora.com/graphql"

CNPJ = "04.502.445/0001-20"
PLAIN_PASSWORD = "85243140"

SECRET_KEY = b"0123456789abcdef0123456789abcdef"

UNBXD_URL = (
    "https://search.unbxd.io/"
    "32e28ae9b107230d0d084a193e9a7898/"
    "ss-unbxd-aus-prod-brazil823111725633283/category"
)

CATEGORIES = [
    {"nome": "Alimentos", "category_path_id": 5963},
    {"nome": "Bazar", "category_path_id": 6033},
    {"nome": "Bomboniere", "category_path_id": 6079},
    {"nome": "Cuidados pessoais e beleza", "category_path_id": 6129},
    {"nome": "Limpeza e lavanderia", "category_path_id": 6347},
    {"nome": "Papelaria", "category_path_id": 6300},
    {"nome": "Pet shop", "category_path_id": 6322},
]

UNBXD_ROWS = 50


def encrypt_password(plain: str) -> str:
    box = SecretBox(SECRET_KEY)
    encrypted = box.encrypt(plain.encode("utf-8"), encoder=Base64Encoder)
    return encrypted.decode("utf-8")


def decrypt_password(cipher_b64: str) -> str:
    box = SecretBox(SECRET_KEY)
    decrypted = box.decrypt(cipher_b64.encode("utf-8"), encoder=Base64Encoder)
    return decrypted.decode("utf-8")



class CompraAgoraClient:
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update(
            {
                "User-Agent": (
                    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                    "AppleWebKit/537.36 (KHTML, like Gecko) "
                    "Chrome/122.0 Safari/537.36"
                ),
                "Accept": "application/json, text/plain, */*",
                "Content-Type": "application/json",
            }
        )
        self.token = None

    def graphql(
        self,
        query: str,
        variables: Dict[str, Any] = None,
        operation_name: str = None,
    ) -> Dict[str, Any]:
        payload: Dict[str, Any] = {"query": query}
        if variables is not None:
            payload["variables"] = variables
        if operation_name is not None:
            payload["operationName"] = operation_name

        resp = self.session.post(GRAPHQL_URL, json=payload, timeout=30)
        resp.raise_for_status()
        data = resp.json()
        if "errors" in data:
            raise RuntimeError(f"Erro GraphQL: {data['errors']}")
        return data.get("data", {})

    def login(self, cnpj: str, password: str, remember_me: int = 0) -> None:
    
        mutation = """
        mutation signIn($cnpj_number: String!, $password: String!, $remember_me: Int!) {
          generateCustomerToken(
            cnpj_number: $cnpj_number
            password: $password
            remember_me: $remember_me
          ) {
            token
            zone_mapping
            status
            message
          }
        }
        """

        variables = {
            "cnpj_number": cnpj,
            "password": password,
            "remember_me": remember_me,
        }

        data = self.graphql(mutation, variables, operation_name="signIn")
        token_info = data.get("generateCustomerToken") or {}

        token = token_info.get("token")
        status = token_info.get("status")
        message = token_info.get("message")

        if not token:
            raise RuntimeError(f"Falha no login. status={status}, message={message}")

        self.token = token
        self.session.headers["Authorization"] = f"Bearer {token}"


def build_unbxd_headers() -> Dict[str, str]:
    return {
        "Accept": "application/json",
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/122.0 Safari/537.36"
        ),
        "Origin": "https://novo.compra-agora.com",
        "Referer": "https://novo.compra-agora.com/",
    }


def fetch_unbxd_page(
    session: requests.Session,
    category_path_id: int,
    page: int,
    rows: int = UNBXD_ROWS,
) -> Dict[str, Any]:
    """
    Faz uma chamada à API 'category' do Unbxd para uma categoria e página específicos.
    Aqui usamos uma versão simplificada dos parâmetros, suficiente para pegar:
    title, brandName e smallImage.
    """
    params = {
        "p-id": f"categoryPathId:{category_path_id}",
        "version": "V2",
        "rows": str(rows),
        "page": str(page),
        "fields": "title,brandName,smallImage,categoryPath1,categoryPath2",
        "variants": "true",
        "variants.count": "20",
        "facet.multiselect": "true",
        "pagetype": "boolean",
        "facet.multilevel": "categoryPath",
        "f.categoryPath.displayName": "Category",
        "f.categoryPath.max.depth": "4",
        "uid": f"uid-{int(time.time()*1000)}-python",
        "pseudorandomnumber": str(int(time.time() * 1000)),
    }

    resp = session.get(
        UNBXD_URL,
        headers=build_unbxd_headers(),
        params=params,
        timeout=30,
    )
    resp.raise_for_status()
    return resp.json()


def get_products(
    session: requests.Session,
    category_name: str,
    category_path_id: int,
) -> List[Dict[str, Any]]:
   
    page = 1
    rows = UNBXD_ROWS
    resultados: List[Dict[str, Any]] = []

    while True:
        data = fetch_unbxd_page(session, category_path_id, page, rows=rows)
        response = data.get("response") or {}
        products = response.get("products") or []
        number_of_products = response.get("numberOfProducts", 0)
        start = response.get("start", (page - 1) * rows)

        for p in products:
            descricao = p.get("title") or p.get("articleName") or p.get("vTitle")
            fabricante = p.get("brandName")
            imagem_url = p.get("smallImage") or p.get("vImageUrl")

            resultados.append(
                {
                    "categoria": category_name,
                    "descricao": descricao,
                    "descricao_fabricante": fabricante,
                    "imagem_url": imagem_url,
                }
            )

        if not products:
            break

        total_pages = math.ceil(number_of_products / float(rows)) if number_of_products else page
        if page >= total_pages:
            break

        page += 1

    return resultados



def main():
    encrypted_pwd = encrypt_password(PLAIN_PASSWORD)
    password_for_login = decrypt_password(encrypted_pwd)

    client = CompraAgoraClient()

    print("[INFO] Fazendo login no Compra Agora...")
    client.login(CNPJ, password_for_login)
    print("[INFO] Login OK.")

    todos_produtos: List[Dict[str, Any]] = []

    for cat in CATEGORIES:
        nome = cat["nome"]
        cid = cat["category_path_id"]
        print(f"[INFO] Buscando produtos da categoria '{nome}' (categoryPathId={cid})...")

        try:
            produtos = get_products(client.session, nome, cid)
            print(f"       -> {len(produtos)} produtos encontrados.")
            todos_produtos.extend(produtos)
        except Exception as e:
            print(f"[WARN] Falha ao buscar categoria {cid} ({nome}): {e}")

    output_file = "produtos_compra_agora.json"
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(todos_produtos, f, ensure_ascii=False, indent=2)

    print(f"[INFO] Total de produtos capturados: {len(todos_produtos)}")
    print(f"[INFO] Resultado salvo em {output_file}")


if __name__ == "__main__":
    try:
        main()
    except requests.HTTPError as e:
        print(f"[ERRO HTTP] {e.response.status_code}: {e.response.text}")
        sys.exit(1)
    except Exception as e:
        print(f"[ERRO] {e}")
        sys.exit(1)