
import logging
from  logging import handlers


# --- Logging ---
logging.basicConfig(
    format='%(asctime)s %(filename)s %(lineno)s %(levelname)-8s \n%(message)s',
    level=logging.INFO,
    datefmt='%Y-%m-%d %H:%M:%S')

frmter = logging.Formatter('{lineno}**{message}** at{asctime}|{name}',style='{')
logfh = handlers.RotatingFileHandler("logging.log", mode='a', maxBytes=1024*4, backupCount=0, 
    encoding=None, delay=False, errors=None)
logfh.setFormatter(frmter)

log = logging.getLogger(__name__)
log.addHandler(logfh)

