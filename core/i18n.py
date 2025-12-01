from core.config import telegram_config

# 简单的内置翻译表
TRANSLATIONS = {
    "en": {
        "start_message": "Hello, {name}",
        "help_message": (
            "Hello, {name}\n"
            "Available commands:\n"
            "/start - Start bot\n"
            "/help - Show help\n"
        ),
    },
    "zh": {
        "start_message": "你好，{name}",
        "help_message": (
            "你好，{name}\n"
            "可用命令：\n"
            "/start - 启动机器人\n"
            "/help - 显示帮助信息\n"
        ),
    },
}

# 聊天维度语言映射（内存）
_chat_lang_map = {}


def get_supported_languages():
    """
    返回支持的语言列表
    """
    return list(TRANSLATIONS.keys())


def detect_lang(chat_id, user_lang_code=None):
    if user_lang_code:
        code = str(user_lang_code).lower()
        if code.startswith("zh"):
            return "zh"
        if code.startswith("en"):
            return "en"
    return "en"


def set_lang(chat_id, lang):
    """
    设置聊天语言，返回是否设置成功
    """
    if lang in TRANSLATIONS:
        _chat_lang_map[chat_id] = lang
        return True
    return False


def t(lang, key, **kwargs):
    """
    翻译函数：返回指定语言的文案，支持变量插值
    """
    table = TRANSLATIONS.get(lang) or TRANSLATIONS.get("en", {})
    text = table.get(key) or key
    try:
        return text.format(**kwargs)
    except Exception:
        return text


def get_help_text(lang, name):
    """
    返回按语言生成的帮助文本
    """
    return t(lang, "help_message", name=name)