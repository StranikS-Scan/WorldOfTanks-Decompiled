# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/battle_results/context.py
from constants import ARENA_BONUS_TYPE
from gui.shared.utils.decorators import ReprInjector

@ReprInjector.simple(('getArenaUniqueID', 'arenaUniqueID'), ('needToShowImmediately', 'showImmediately'), ('needToShowIfPosted', 'showIfPosted'), ('resetCache', 'resetCache'))
class RequestResultsContext(object):
    __slots__ = ('__arenaUniqueID', '__arenaBonusType', '__showImmediately', '__showIfPosted', '__resetCache')

    def __init__(self, arenaUniqueID, arenaBonusType=None, showImmediately=True, showIfPosted=False, resetCache=False):
        super(RequestResultsContext, self).__init__()
        self.__arenaUniqueID = arenaUniqueID
        self.__arenaBonusType = arenaBonusType
        self.__showImmediately = showImmediately
        self.__showIfPosted = showIfPosted
        self.__resetCache = resetCache

    def getArenaUniqueID(self):
        return self.__arenaUniqueID

    def getArenaBonusType(self):
        return self.__arenaBonusType

    def needToShowImmediately(self):
        return self.__showImmediately and self.__arenaBonusType not in (ARENA_BONUS_TYPE.EVENT_BATTLES,)

    def needToShowIfPosted(self):
        return self.__showIfPosted

    def resetCache(self):
        return self.__resetCache


@ReprInjector.simple(('getEmblemType', 'type'), ('getUniqueID', 'ids'))
class RequestEmblemContext(object):
    __slots__ = ('__emblemType', '__formationDBID', '__textureID')

    def __init__(self, emblemType, formationDBID, textureID=0):
        super(RequestEmblemContext, self).__init__()
        self.__emblemType = emblemType
        self.__formationDBID = formationDBID
        self.__textureID = textureID

    def getEmblemType(self):
        return self.__emblemType

    def getFormationDBID(self):
        return self.__formationDBID

    def getTextureID(self):
        return self.__textureID

    def getUniqueID(self):
        return (self.getEmblemType(), self.__formationDBID)
