# Embedded file name: scripts/common/clubs_settings.py
import ResMgr
import time
from debug_utils import LOG_NOTE, LOG_SVAN_DEV
import BigWorld
_CONFIG_FILE = 'scripts/item_defs/clubs_settings.xml'

class ClubsCache:

    def __getSeasonSuspended(self):
        return self.__seasonSuspended

    def __setSeasonSuspended(self, value):
        self.__seasonSuspended = True if value else False

    seasonSuspended = property(__getSeasonSuspended, __setSeasonSuspended)

    def __init__(self):
        self.currentSeason = 0
        self.currentSeasonStart = 0
        self.currentSeasonFinish = 0
        self.prearenaWaitTime = 180
        self.maxLegionariesCount = 6
        self.__seasonSuspended = False

    def seasonInProgress(self):
        LOG_SVAN_DEV('call seasonInProgress. seasonSuspended={}', self.seasonSuspended)
        return not self.seasonSuspended and self.currentSeasonStart <= time.time() <= self.currentSeasonFinish


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
