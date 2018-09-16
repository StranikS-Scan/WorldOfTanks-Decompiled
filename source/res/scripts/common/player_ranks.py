# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/common/player_ranks.py
import ResMgr
from constants import PLAYER_RANK
_CONFIG_FILE = 'scripts/item_defs/player_ranks.xml'

class BasicThresholdRankSettings(object):

    def __init__(self, section, order):
        self.rank = PLAYER_RANK.RANK_BY_NAME[section.name]
        self.order = order
        self.threshold = section.readInt('threshold')


class AlgorithmSettings(object):

    def __init__(self, section):
        self.name = section.name


class BasicThresholdSettings(AlgorithmSettings):

    def __init__(self, section):
        super(BasicThresholdSettings, self).__init__(section)
        self.ranks = []
        order = 1
        for subsection in section.values():
            self.ranks.append(BasicThresholdRankSettings(subsection, order))
            order += 1

        self.byOrder = {settings.order:settings for settings in self.ranks}
        self.byRank = {settings.rank:settings for settings in self.ranks}
        self.orderByRank = {settings.rank:settings.order for settings in self.ranks}


class BonusSettings(object):

    def __init__(self, section):
        self.factor100ByRank = {}
        if not section:
            return
        for rankName in section.keys():
            rank = PLAYER_RANK.RANK_BY_NAME[rankName]
            bonusFactor100 = section.readInt(rankName)
            self.factor100ByRank[rank] = bonusFactor100


class PlayerRanksSettings(object):
    ALGORITHM_SETTINGS = {'BasicThreshold': BasicThresholdSettings}

    def __init__(self, section):
        algorithmKeys = set(section.keys()).intersection(set(self.ALGORITHM_SETTINGS))
        algorithmName = algorithmKeys.__iter__().next()
        self.algorithm = self.ALGORITHM_SETTINGS[algorithmName](section[algorithmName])
        self.bonus = BonusSettings(section['bonus'])


g_cache = None

def init():
    global g_cache
    g_cache = settings = {}
    section = ResMgr.openSection(_CONFIG_FILE)
    for name, subsection in section.items():
        settings[name] = PlayerRanksSettings(subsection)


def getSettings():
    return g_cache['DEFAULT']
