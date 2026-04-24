import os
import firebase_admin
from firebase_admin import credentials, auth


def inicializar_firebase():
    caminho_credenciais = os.path.join(
        os.path.dirname(__file__),
        "jotair-3404c-firebase-adminsdk-fbsvc-ca6cc724cc.json",
    )
    cred = credentials.Certificate(caminho_credenciais)
    firebase_admin.initialize_app(cred)


def criar_usuario(email, senha):
    usuario = auth.create_user(email=email, password=senha)
    return usuario.uid


def buscar_usuario_por_uid(uid):
    return auth.get_user(uid)


def imprimir_usuario(usuario):
    print(f"UID: {usuario.uid}")
    print(f"Email: {usuario.email}")


if __name__ == "__main__":
    inicializar_firebase()

    uid = criar_usuario("usuario_teste@example.com", "senhanadasegurajaquefoicommitada")
    print(f"Usuario criado com UID: {uid}")

    usuario = buscar_usuario_por_uid(uid)
    print("Dados do usuario buscado por UID:")
    imprimir_usuario(usuario)
