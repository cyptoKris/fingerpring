import sys
from loguru import logger

# 自定义日志格式
custom_format = (
    "<g>{time:MM-DD HH:mm:ss}</g> "
    "[<lvl>{level}</lvl>] "
    "<c><u>{file}</u></c> | "
    "<c>{function}:{line}</c>| "
    "{message}"
)


# 添加自定义格式的日志处理器
logger.remove()
logger.add(sys.stdout, format=custom_format, colorize=True)
logger.opt(colors=True, exception=True)
