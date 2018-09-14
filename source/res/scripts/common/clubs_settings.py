# Embedded file name: scripts/common/clubs_settings.py
import time
import ResMgr
from debug_utils import LOG_NOTE, LOG_ERROR
_CONFIG_FILE = 'scripts/item_defs/clubs_settings.xml'

class ClubsSettings:
    prearenaWaitTime = property(lambda self: self.__prearenaWaitTime)
    maxLegionariesCount = property(lambda self: self.__maxLegionariesCount)

    def __init__(self, prearenaWaitTime, maxLegionariesCount):
        self.__prearenaWaitTime = prearenaWaitTime
        self.__maxLegionariesCount = maxLegionariesCount

    @classmethod
    def default(cls):
        return cls(180, 6)


g_cache = None

def __asDate(date):
    try:
        return int(time.mktime(time.strptime(date, '%d.%m.%Y %H:%M')))
    except:
        raise Exception, 'Bad date format of %s' % (date,)


def init():
    global g_cache
    LOG_NOTE('clubs.init()')
    try:
        section = ResMgr.openSection(_CONFIG_FILE)
        prearenaWaitTime = section['prearena_wait_time'].asInt
        maxLegionariesCount = section['max_legionaries_count'].asInt
        g_cache = ClubsSettings(prearenaWaitTime, maxLegionariesCount)
    except Exception as e:
        LOG_ERROR('Wrong config :{}. Error: {}'.format(_CONFIG_FILE, repr(e)))
        g_cache = ClubsSettings.default()
