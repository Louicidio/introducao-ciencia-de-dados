import os
import firebase_admin
from firebase_admin import credentials, storage


def inicializar_firebase():
    caminho_credenciais = os.path.join(
        os.path.dirname(__file__),
        "jotair-3404c-firebase-adminsdk-fbsvc-ca6cc724cc.json",
    )
    cred = credentials.Certificate(caminho_credenciais)
    firebase_admin.initialize_app(cred, {"storageBucket": "SEU_BUCKET.appspot.com"})


def upload_arquivo_texto_simples():
    caminho_local = os.path.join(os.path.dirname(__file__), "meu_arquivo.txt")
    with open(caminho_local, "w", encoding="utf-8") as arquivo:
        arquivo.write("Olá, Firebase Storage!")

    bucket = storage.bucket()
    blob = bucket.blob("meu_arquivo.txt")
    blob.upload_from_filename(caminho_local)

    print("Upload concluido: meu_arquivo.txt")


if __name__ == "__main__":
    inicializar_firebase()
    upload_arquivo_texto_simples()
