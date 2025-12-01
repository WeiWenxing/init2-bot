from dotenv import load_dotenv
import os

load_dotenv()

telegram_config = {
    "token": os.environ.get("TELEGRAM_BOT_TOKEN", ""),
    "default_lang": os.environ.get("DEFAULT_LANG", "en"),
}

discord_config = {
    "token": os.environ.get("DISCORD_TOKEN", ""),
}
