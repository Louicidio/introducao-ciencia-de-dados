import os
import firebase_admin
from firebase_admin import credentials, messaging


def inicializar_firebase():
    caminho_credenciais = os.path.join(
        os.path.dirname(__file__),
        "jotair-3404c-firebase-adminsdk-fbsvc-ca6cc724cc.json",
    )
    cred = credentials.Certificate(caminho_credenciais)
    firebase_admin.initialize_app(cred)


def simular_envio_notificacao_para_topico(topico):
    mensagem = messaging.Message(
        notification=messaging.Notification(
            title="Notificacao de teste",
            body="Esta e uma notificacao simples via Firebase Cloud Messaging.",
        ),
        topic=topico,
    )

    message_id = messaging.send(mensagem)
    print(f"Notificacao enviada com sucesso. Message ID: {message_id}")


if __name__ == "__main__":
    inicializar_firebase()
    simular_envio_notificacao_para_topico("topico_teste")
