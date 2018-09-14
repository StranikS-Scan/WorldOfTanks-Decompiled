# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/skeletons/gui/battle_results.py
from Event import Event

class IBattleResultsService(object):
    """Service to provide access to battle results."""
    __slots__ = ()
    onResultPosted = None

    def init(self):
        """Initialization of service."""
        raise NotImplementedError

    def fini(self):
        """Finalization of service,"""
        raise NotImplementedError

    def clear(self):
        """Clears cached data"""
        raise NotImplementedError

    def requestResults(self, ctx, callback=None):
        """Sends request to account repository (local cache) on receiving battle result.
        :param ctx: request context
        :param callback: callable object
        """
        raise NotImplementedError

    def requestEmblem(self, ctx, callback=None):
        """Sends request to fetch clan/club/etc emblem from local cache if it exists or
            download from web.
        :param ctx: request context
        :param callback: callable object
        """
        raise NotImplementedError

    def postResult(self, result, needToShowUI=True):
        """Posts unpacked battle results to service.
        :param result: dictionary containing unpacked battle result.
            See battle_result_shared.py to get more information.
        :param needToShowUI: if values equals True than window with results is opened,
            otherwise - do nothing.
        :return: True if result is posted, otherwise - False.
        """
        raise NotImplementedError

    def areResultsPosted(self, arenaUniqueID):
        """Are battle result posted by specified arena unique ID.
        :param arenaUniqueID: long containing arena unique ID.
        :return: bool.
        """
        raise NotImplementedError

    def getResultsVO(self, arenaUniqueID):
        """Gets battle results VO by specified arena unique ID.
        :param arenaUniqueID: long containing arena unique ID.
        :return: dictionary containing generated VO to show results in a window.
        """
        raise NotImplementedError

    def popResultsAnimation(self, arenaUniqueID):
        """Gets animation data to play it once if it exists and removes it from service.
        :param arenaUniqueID: long containing arena unique ID.
        :return: dictionary containing animation VO
        """
        raise NotImplementedError

    def saveStatsSorting(self, bonusType, iconType, sortDirection):
        """Stores user selection of sorting in battle result window.
        :param bonusType: integer containing one of ARENA_BONUS_TYPE.*.
        :param iconType: string containing type of icon.
        :param sortDirection: string containing sorting direction.
        """
        raise NotImplementedError
