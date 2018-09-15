# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/event_boards/event_boards_vehicles_overlay.py
from gui.Scaleform.daapi.view.lobby.event_boards.event_boards_vos import makeFiltersVO, makeVehiclesVO
from gui.Scaleform.daapi.view.meta.EventBoardsVehiclesOverlayMeta import EventBoardsVehiclesOverlayMeta
from gui.Scaleform.locale.EVENT_BOARDS import EVENT_BOARDS
from gui.event_boards.event_boards_items import EVENT_TYPE
from helpers import int2roman
from helpers.i18n import makeString as _ms

class EventBoardsVehiclesOverlay(EventBoardsVehiclesOverlayMeta):
    __opener = None

    def setOpener(self, view):
        self.__opener = view
        eventData = self.__opener.eventData
        leaderboards = eventData.getLeaderboards()
        leaderboardID = leaderboards[0][0]
        header = {'filters': makeFiltersVO(eventData.getType(), leaderboards, leaderboardID, category='vehicles')}
        self.as_setHeaderS(header)
        self._setData(leaderboardID)

    def changeFilter(self, lid):
        self._setData(int(lid))

    def _setData(self, lid):
        eventData = self.__opener.eventData
        eventType = eventData.getType()
        leaderboard = eventData.getLeaderboard(lid)
        if eventType == EVENT_TYPE.VEHICLE:
            title = _ms(EVENT_BOARDS.VEHICLES_VEHICLE)
            bgPath = None
        elif eventType == EVENT_TYPE.NATION:
            title = _ms('#menu:nation_tree/title/{}'.format(leaderboard))
            bgPath = '../maps/icons/eventBoards/flagsOverlay/{}.png'.format(leaderboard)
        elif eventType == EVENT_TYPE.LEVEL:
            title = _ms(EVENT_BOARDS.VEHICLES_LEVEL, level=int2roman(leaderboard))
            bgPath = None
        elif eventType == EVENT_TYPE.CLASS:
            title = _ms('#quests:classes/{}'.format(leaderboard))
            bgPath = None
        else:
            title = None
            bgPath = None
        data = {'title': title,
         'bgPath': bgPath,
         'vehicles': makeVehiclesVO(eventData.getLimits().getVehicles(lid))}
        self.as_setVehiclesS(data)
        return
