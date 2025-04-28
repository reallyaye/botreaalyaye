import os
from pathlib import Path
from dotenv import load_dotenv, set_key, dotenv_values
from pyngrok import ngrok

def main():
    # 1) Загрузить .env
    base = Path(__file__).parent
    env_path = base / ".env"
    load_dotenv(dotenv_path=env_path)

    # 2) Настроить ngrok
    auth = os.getenv("NGROK_AUTH_TOKEN")
    if auth:
        ngrok.set_auth_token(auth)
    tunnel = ngrok.connect(8000, bind_tls=True)
    url = tunnel.public_url

    # 3) Обновить .env
    set_key(env_path, "WEBAPP_URL", url)
    if "DATABASE_URL" not in dotenv_values(env_path):
        set_key(env_path, "DATABASE_URL", "./db.sqlite3")

    print(f"✔️  Обновлено .env: WEBAPP_URL={url}")

if __name__ == "__main__":
    main()
