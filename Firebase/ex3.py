import os
import firebase_admin
from firebase_admin import credentials, firestore


def inicializar_firebase():
    caminho_credenciais = os.path.join(
        os.path.dirname(__file__),
        "jotair-3404c-firebase-adminsdk-fbsvc-ca6cc724cc.json",
    )
    cred = credentials.Certificate(caminho_credenciais)
    firebase_admin.initialize_app(cred)


def atualizar_preco_produto(produto_id, novo_preco):
    db = firestore.client()
    db.collection("produtos_mysql").document(produto_id).update({"preco": float(novo_preco)})


if __name__ == "__main__":
    inicializar_firebase()

    id_produto = "ID_DO_PRODUTO"
    novo_preco = 19.90

    atualizar_preco_produto(id_produto, novo_preco)
    print(f"Preco do produto {id_produto} atualizado para R$ {novo_preco:.2f}.")
