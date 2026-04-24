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


def listar_produtos_com_preco_acima(valor_minimo):
    db = firestore.client()
    consulta = db.collection("produtos_mysql").where("preco", ">", float(valor_minimo))

    for doc in consulta.stream():
        produto = doc.to_dict()
        nome = produto.get("nome", "(sem nome)")
        preco = float(produto.get("preco", 0))
        print(f"Nome: {nome} | Preco: R$ {preco:.2f}")


if __name__ == "__main__":
    inicializar_firebase()
    listar_produtos_com_preco_acima(15.00)
