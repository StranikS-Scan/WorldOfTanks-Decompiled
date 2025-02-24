# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: comp7/scripts/client/comp7/gui/event_boards/event_boards_items.py
from gui.event_boards.event_boards_items import LeaderBoard

class Comp7LeaderBoard(LeaderBoard):
    __CUSTOM_EXPECTED_FIELDS_META = ['elite_rank_position_threshold', 'elite_rank_points_threshold', 'master_rank_position_threshold']
    EXPECTED_FIELDS_META = LeaderBoard.EXPECTED_FIELDS_META + __CUSTOM_EXPECTED_FIELDS_META

    def __init__(self):
        super(Comp7LeaderBoard, self).__init__()
        self.__lastEliteUserPosition = None
        self.__lastEliteUserRating = None
        self.__lastMasterRankPositionThreshold = None
        return

    def setData(self, rawData, leaderboardID, infoType, leaderboardType):
        result = super(Comp7LeaderBoard, self).setData(rawData, leaderboardID, infoType, leaderboardType)
        meta = rawData['meta']
        self.__lastEliteUserPosition = meta['elite_rank_position_threshold']
        self.__lastEliteUserRating = meta['elite_rank_points_threshold']
        self.__lastMasterRankPositionThreshold = meta['master_rank_position_threshold'] or 0
        return result

    def getRecordsCount(self):
        return self.__lastMasterRankPositionThreshold

    def getLastEliteUserPosition(self):
        return self.__lastEliteUserPosition

    def getLastEliteUserRating(self):
        return self.__lastEliteUserRating
