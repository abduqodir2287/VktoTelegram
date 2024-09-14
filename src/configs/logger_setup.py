import logging
from logging.handlers import RotatingFileHandler
from src.configs.config import settings

logger = logging.getLogger("VKtoTelegram")
logger.setLevel(level=settings.LOG_LEVEL)

formatter = logging.Formatter(settings.LOG_FORMAT)

if settings.LOG_WRITE_STATUS:
    filehandler = RotatingFileHandler(
        filename=settings.LOG_FILE,
        backupCount=settings.LOG_BACKUP_COUNT,
        mode='w'
    )
    filehandler.setFormatter(formatter)
    logger.addHandler(filehandler)

handler = logging.StreamHandler()
handler.setFormatter(formatter)
logger.addHandler(handler)
