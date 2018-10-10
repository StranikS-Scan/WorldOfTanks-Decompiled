# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/event_boards/event_boards_awards_overlay.py
from CurrentVehicle import g_currentVehicle
from gui.Scaleform.daapi.view.lobby.event_boards.event_boards_vos import makeFiltersVO, vehicleValueGetter
from gui.Scaleform.daapi.view.lobby.rally.vo_converters import makeVehicleBasicVO
from gui.Scaleform.daapi.view.meta.EventBoardsAwardsOverlayMeta import EventBoardsAwardsOverlayMeta
from gui.Scaleform.genConsts.EVENTBOARDS_ALIASES import EVENTBOARDS_ALIASES
from gui.Scaleform.locale.RES_ICONS import RES_ICONS
from gui.Scaleform.locale.TOOLTIPS import TOOLTIPS
from gui.event_boards.event_boards_items import EVENT_TYPE
from gui.server_events.awards_formatters import QuestsBonusComposer, getEventBoardsAwardPacker
from gui.shared.utils import sortByFields
from gui.shared.utils.requesters import REQ_CRITERIA
from helpers import int2roman, dependency
from helpers.i18n import makeString as _ms
from skeletons.gui.shared import IItemsCache

class EventBoardsAwardsOverlay(EventBoardsAwardsOverlayMeta):
    itemsCache = dependency.descriptor(IItemsCache)

    def __init__(self):
        super(EventBoardsAwardsOverlay, self).__init__()
        self.__opener = None
        self.__leaderboardID = None
        return

    def setOpener(self, view):
        self.__opener = view
        eventData = self.__opener.eventData
        leaderboards = eventData.getLeaderboards()
        leaderboardID = leaderboards[0][0]
        if eventData.getType() == EVENT_TYPE.VEHICLE:
            currentVehicleCD = g_currentVehicle.item.intCD if g_currentVehicle.item else None
            _leaderboardID = eventData.getLeaderboardID(currentVehicleCD)
            if _leaderboardID is not None:
                leaderboardID = _leaderboardID
            elif leaderboards:
                vehicleIds = [ veh for _, veh in leaderboards ]
                allVehicles = self.itemsCache.items.getVehicles(REQ_CRITERIA.IN_CD_LIST(vehicleIds))
                fields = (('level', False), ('nations', True), ('type', True))
                sortedVehicles = sortByFields(fields, allVehicles.itervalues(), vehicleValueGetter)
                leaderboardID = eventData.getLeaderboardID(sortedVehicles[0].intCD)
        else:
            header = {'filters': makeFiltersVO(eventData.getType(), leaderboards, leaderboardID, category='awards')}
            self.as_setHeaderS(header)
        self._setData(leaderboardID)
        return

    def changeFilter(self, lid):
        lid = int(lid)
        eventData = self.__opener.eventData
        if eventData.getType() == EVENT_TYPE.VEHICLE:
            lid = eventData.getLeaderboardID(lid)
        self._setData(lid)

    def _setData(self, lid):
        eventData = self.__opener.eventData
        eventType = eventData.getType()
        self.__leaderboardID = lid
        leaderboard = eventData.getLeaderboard(lid)
        if eventType == EVENT_TYPE.VEHICLE:
            self._setVehicle(leaderboard)
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
                icon = RES_ICONS.getEventBoardGroup(categoryNumber)
            _min, _max = group.getRankMinMax()
            awards.append({'icon': icon,
             'positionDescr': str(_min) if _min == _max else '{} - {}'.format(_min, _max),
             'awards': awardsFormatter.getFormattedBonuses(group.getRewards()),
             'tooltip': _ms(TOOLTIPS.ELEN_AWARDSOVERLAY_GROUP_HEADER, number=int2roman(categoryNumber))})

        data = {'eventID': eventData.getEventID(),
         'title': title,
         'bgPath': bgPath,
         'awardsData': {'tableData': awards}}
        self.as_setDataS(data)
        return

    def _setVehicle(self, cd):
        vehicleVO = makeVehicleBasicVO(self.itemsCache.items.getItemByCD(cd))
        self.as_setVehicleS(vehicleVO)

    def _populate(self):
        super(EventBoardsAwardsOverlay, self)._populate()
        self.app.loaderManager.onViewLoaded += self.__onViewLoaded

    def _dispose(self):
        self.app.loaderManager.onViewLoaded -= self.__onViewLoaded
        super(EventBoardsAwardsOverlay, self)._dispose()

    def __onViewLoaded(self, view, *args, **kwargs):
        if view.alias == EVENTBOARDS_ALIASES.RESULT_FILTER_POPOVER_VEHICLES_ALIAS:
            if view.caller == 'awards':
                eventData = self.__opener.eventData
                view.setData(eventData, self._setData, self.__leaderboardID)
