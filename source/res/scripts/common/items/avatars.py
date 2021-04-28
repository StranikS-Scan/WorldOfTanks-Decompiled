# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/common/items/avatars.py
import ResMgr
from items import _xml, common_extras
from constants import IS_CLIENT, IS_CELLAPP, ITEM_DEFS_PATH
g_cache = None

def init():
    global g_cache
    g_cache = Cache()


class Cache(object):

    def __init__(self):
        self.__commonConfig = None
        return

    @property
    def commonConfig(self):
        config = self.__commonConfig
        if config is None:
            configXmlPath = ITEM_DEFS_PATH + 'avatar.xml'
            configXml = ResMgr.openSection(configXmlPath)
            if configXml is None:
                _xml.raiseWrongXml(None, configXmlPath, 'can not open or read')
            if IS_CLIENT or IS_CELLAPP:
                extras, extrasDict = common_extras.readExtras((None, configXmlPath), configXml, 'extras', 'avatar_extras_common')
                config = self.__commonConfig = {'extras': extras,
                 'extrasDict': extrasDict}
            configXml = None
            ResMgr.purge(configXmlPath, True)
        return config
