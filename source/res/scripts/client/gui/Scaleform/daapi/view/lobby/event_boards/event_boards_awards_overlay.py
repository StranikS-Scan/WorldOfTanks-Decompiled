# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/event_boards/event_boards_awards_overlay.py
from gui.Scaleform.daapi.view.lobby.event_boards.event_boards_vos import makeFiltersVO
from gui.Scaleform.daapi.view.meta.EventBoardsAwardsOverlayMeta import EventBoardsAwardsOverlayMeta
from gui.Scaleform.locale.TOOLTIPS import TOOLTIPS
from gui.event_boards.event_boards_items import EVENT_TYPE
from gui.server_events.awards_formatters import QuestsBonusComposer, getEventBoardsAwardPacker
from helpers import int2roman
from helpers.i18n import makeString as _ms

class EventBoardsAwardsOverlay(EventBoardsAwardsOverlayMeta):
    __opener = None

    def setOpener(self, view):
        self.__opener = view
        eventData = self.__opener.eventData
        leaderboards = eventData.getLeaderboards()
        leaderboardID = leaderboards[0][0]
        header = {'filters': makeFiltersVO(eventData.getType(), leaderboards, leaderboardID, category='awards')}
        self.as_setHeaderS(header)
        self._setData(leaderboardID)

    def changeFilter(self, lid):
        self._setData(int(lid))

    def _setData(self, lid):
        eventData = self.__opener.eventData
        eventType = eventData.getType()
        leaderboard = eventData.getLeaderboard(lid)
        if eventType == EVENT_TYPE.VEHICLE:
            title = _ms('#event_boards:awards/vehicle')
            bgPath = None
        elif eventType == EVENT_TYPE.NATION:
            title = _ms('#event_boards:awards/nation/{}'.format(leaderboard))
            bgPath = '../maps/icons/eventBoards/flagsOverlay/{}.png'.format(leaderboard)
        elif eventType == EVENT_TYPE.LEVEL:
            title = _ms('#event_boards:awards/level', level=int2roman(leaderboard))
            bgPath = None
        elif eventType == EVENT_TYPE.CLASS:
            title = _ms('#event_boards:awards/class/{}'.format(leaderboard))
            bgPath = None
        else:
            title = None
            bgPath = None
        awardsFormatter = QuestsBonusComposer(getEventBoardsAwardPacker())
        awardsGroups = eventData.getRewardsByRank().getRewardByRank(lid).getRewardGroups()
        awards = []
        categoryNumber = 0
        for group in awardsGroups:
            if categoryNumber == group.getRewardCategoryNumber():
                icon = ''
            else:
                categoryNumber = group.getRewardCategoryNumber()
                icon = '../maps/icons/eventBoards/groups/{}.png'.format(categoryNumber)
            _min, _max = group.getRankMinMax()
            awards.append({'icon': icon,
             'positionDescr': str(_min) if _min == _max else '{} - {}'.format(_min, _max),
             'awards': awardsFormatter.getFormattedBonuses(group.getRewards()),
             'tooltip': _ms(TOOLTIPS.ELEN_AWARDSOVERLAY_GROUP_HEADER, number=int2roman(categoryNumber))})

        data = {'title': title,
         'bgPath': bgPath,
         'awardsData': {'tableData': awards}}
        self.as_setDataS(data)
        return
