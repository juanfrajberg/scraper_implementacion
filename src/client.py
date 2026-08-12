import os

from dotenv import load_dotenv
from twikit import Client

from .config import COOKIES_FILE


load_dotenv()


def create_client() -> Client:
    client = Client(language="es-ES")

    username = os.environ["TWITTER_USERNAME"]
    email = os.environ["TWITTER_EMAIL"]
    password = os.environ["TWITTER_PASSWORD"]

    if COOKIES_FILE.exists():
        print("Cargando cookies...")
        client.load_cookies(str(COOKIES_FILE))

    else:
        print("Iniciando sesión...")

        client.login(
            auth_info_1=username,
            auth_info_2=email,
            password=password,
        )

        client.save_cookies(
            str(COOKIES_FILE)
        )

        print("Cookies guardadas.")

    return client