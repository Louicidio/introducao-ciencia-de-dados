import os
import firebase_admin
from firebase_admin import credentials


def main():
    caminho_credenciais = os.path.join(
        os.path.dirname(__file__),
        "jotair-3404c-firebase-adminsdk-fbsvc-ca6cc724cc.json",
    )

    cred = credentials.Certificate(caminho_credenciais)
    app = firebase_admin.initialize_app(cred)

    print("Firebase inicializado com sucesso.")
    print(f"aplicativo inicializado: {app.name}")


if __name__ == "__main__":
    main()
