import logging
import logging.handlers


gmaster_logger = logging.getLogger('gmaster')


def log_setting(logger, log_file,
                log_level="INFO", backup_cnt=5, formatter=None,
                clear_original_handlers=False):
    if logger is None:
        logger = logging.getLogger()

    if log_file:
        handler = logging.handlers.TimedRotatingFileHandler(
            filename=log_file,
            when="midnight",
            backupCount=backup_cnt)
        default_formatter = logging.Formatter(
            fmt='%(asctime)s %(levelname)s %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S')
        handler.setFormatter(formatter or default_formatter)
        if clear_original_handlers:
            logger.handlers = []
        logger.addHandler(handler)

    logger.setLevel(log_level.upper())