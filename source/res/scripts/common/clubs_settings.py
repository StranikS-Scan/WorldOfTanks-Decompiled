# Embedded file name: scripts/common/clubs_settings.py
import ResMgr
import time
from debug_utils import LOG_NOTE
_CONFIG_FILE = 'scripts/item_defs/clubs_settings.xml'

class ClubsCache:

    def __init__(self):
        self.currentSeason = 0
        self.currentSeasonStart = 0
        self.currentSeasonFinish = 0
        self.prearenaWaitTime = 180
        self.maxLegionariesCount = 3

    def seasonInProgress(self):
        return self.currentSeasonStart <= time.time() <= self.currentSeasonFinish


g_cache = None

def __asDate(date):
    try:
        return int(time.mktime(time.strptime(date, '%d.%m.%Y %H:%M')))
    except:
        raise Exception, 'Bad date format of %s' % (date,)


def init():
    global g_cache
    LOG_NOTE('clubs.init()')
    g_cache = ClubsCache()
    section = ResMgr.openSection(_CONFIG_FILE)
    subsection = section['current_season']
    g_cache.currentSeason = subsection['id'].asInt
    g_cache.currentSeasonStart = __asDate(subsection['start'].asString)
    g_cache.currentSeasonFinish = __asDate(subsection['finish'].asString)
    g_cache.prearenaWaitTime = section['prearena_wait_time'].asInt
    g_cache.maxLegionariesCount = section['max_legionaries_count'].asInt
