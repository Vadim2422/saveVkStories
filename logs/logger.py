import logging

logger = logging.getLogger("Bot")
logger.setLevel(logging.INFO)

handler = logging.FileHandler("logs/bot.log", mode='a')
formatter = logging.Formatter("%(asctime)s %(name)s: %(levelname)s %(message)s")

handler.setFormatter(formatter)
logger.addHandler(handler)
