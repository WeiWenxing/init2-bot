# 初始 Bot

一个最小化的 Telegram 与 Discord 机器人模板，提供基础命令和定时任务框架，便于按业务扩展。

## 环境要求

- Python 3.8+
- pip
- virtualenv

## 安装步骤

1. 克隆项目
```bash
git clone [项目地址]
cd site-bot
```

2. 创建并激活虚拟环境
```bash
# 创建虚拟环境
python -m venv venv

# Windows激活虚拟环境
venv\Scripts\activate

# Linux/Mac激活虚拟环境
source venv/bin/activate
```

3. 安装依赖
```bash
pip install -r requirements.txt
```

4. 配置环境变量
```bash
# 复制环境变量示例文件
cp env.example .env

# 编辑.env文件，填入必要的配置
```

### 环境变量说明

必填配置:
- `TELEGRAM_BOT_TOKEN`: Telegram机器人token (从@BotFather获取)
可选配置:
- `DISCORD_TOKEN`: Discord机器人token (如需Discord功能则必填)

## 运行方式

1. 直接运行
```bash
python bot.py
```


## 目录结构

```
project/
├── apps/                 # 应用入口层
│   ├── telegram_bot.py   # 基础命令与定时任务占位
│   └── discord_bot.py    # 可选的 Discord 入口
├── core/                 # 核心配置层
│   └── config.py         # 环境变量配置
└── bot.py                # 主程序入口
```

## 注意事项

1. 确保 `.env` 文件配置了正确的 bot token 和发送目标
2. 首次运行前创建虚拟环境并安装依赖
## 命令使用说明

### Telegram
- `/start` - 启动机器人
- `/help` - 显示帮助信息

### 定时任务
- 已内置基础定时任务框架：每小时运行一次，占位无业务逻辑
- 你可以在 `apps/telegram_bot.py` 的 `scheduled_task` 中添加自己的处理
