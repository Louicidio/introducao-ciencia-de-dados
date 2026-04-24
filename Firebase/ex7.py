import os
import firebase_admin
from firebase_admin import credentials, auth
from firebase_admin.exceptions import FirebaseError
#OBS: as senhas sao apenas para teste, portanto, nao tem problema expo-las

def inicializar_firebase():
    caminho_credenciais = os.path.join(
        os.path.dirname(__file__),
        "jotair-3404c-firebase-adminsdk-fbsvc-ca6cc724cc.json",
    )
    cred = credentials.Certificate(caminho_credenciais)
    firebase_admin.initialize_app(cred)


def criar_usuario_com_tratamento(email, senha):
    try:
        usuario = auth.create_user(email=email, password=senha)
        print(f"Usuario criado com UID: {usuario.uid}")
        return usuario.uid
    except FirebaseError as erro:
        print(f"Erro do Firebase ao criar usuario: {erro}")
        return None


def buscar_usuario_por_uid_com_tratamento(uid):
    try:
        usuario = auth.get_user(uid)
        print("Usuario encontrado:")
        print(f"UID: {usuario.uid}")
        print(f"Email: {usuario.email}")
    except FirebaseError as erro:
        print(f"Erro do Firebase ao buscar usuario: {erro}")


if __name__ == "__main__":
    inicializar_firebase()

    uid = criar_usuario_com_tratamento("usuario_b@example.com", "senhanadasegurajaquefoicommitada2")
    if uid:
        buscar_usuario_por_uid_com_tratamento(uid)
