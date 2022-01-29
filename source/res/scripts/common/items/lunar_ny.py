# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/common/items/lunar_ny.py
from wotdecorators import singleton
from debug_utils import LOG_CURRENT_EXCEPTION
from items.readers.lunar_ny_readers import readCharm
from constants import ITEM_DEFS_PATH
LUNAR_NY_XML_PATH = ITEM_DEFS_PATH + 'lunar_ny/'

@singleton
class g_cache(object):

    def __init__(self):
        self.__cfg = {}

    def __getattr__(self, attr):
        return self.__cfg[attr]

    def init(self, nofail=True):
        cfg = self.__cfg
        try:
            cfg['charms'] = readCharm(LUNAR_NY_XML_PATH + 'charm.xml')
        except Exception:
            self.fini()
            if nofail:
                raise
            LOG_CURRENT_EXCEPTION()

    def fini(self):
        self.__cfg.clear()

    def __nonzero__(self):
        return bool(self.__cfg)


def init(nofail=True):
    if not g_cache:
        g_cache.init(nofail)
