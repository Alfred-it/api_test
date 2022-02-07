import time
import logging
import logging.config
logging.basicConfig(format='%(asctime)s - %(levelname)s: %(message)s',
                    level=logging.INFO)
logging.basicConfig(format='%(asctime)s - %(levelname)s: %(message)s',
                    level=logging.ERROR)
logging.basicConfig(format='%(asctime)s - %(levelname)s: %(message)s',
                    level=logging.DEBUG)
def log(func):
    def wrapper(*args, **kw):
        # print(time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()), end=' ')

        if func.__name__ == "debug":
            msg = "debug {}".format(args[0])
        elif func.__name__ == "info":
            msg = "info {}".format(args[0])
        elif func.__name__ == "error":
            msg = "error {}".format(args[0])
        elif func.__name__ == "warning":
            msg = "warning {}".format(args[0])
        else:
            msg = "{}".format(args[0])
        return func(msg, **kw)
    return wrapper

@log
def debug(msg):

    logging.debug(msg)
    print(msg)

@log
def info(msg):
    logging.info(msg)
    print(msg)

@log
def error(msg):
    logging.error(msg)
    print(msg)

@log
def warning(msg):
    logging.warning(msg)
    print(msg)
