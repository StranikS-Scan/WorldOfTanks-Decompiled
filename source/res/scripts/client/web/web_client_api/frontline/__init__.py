# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/web/web_client_api/frontline/__init__.py
from helpers import dependency
from skeletons.gui.game_control import IEpicBattleMetaGameController
from web.web_client_api import w2c, w2capi, W2CSchema

@w2capi(name='frontline', key='action')
class FrontLineWebApi(W2CSchema):
    __epicController = dependency.descriptor(IEpicBattleMetaGameController)

    @w2c(W2CSchema, name='get_player_discount')
    def handleGetPlayerDiscount(self, _):
        return self.__epicController.getStoredEpicDiscount()

    @w2c(W2CSchema, name='get_calendar_info')
    def handleGetCalendarInfo(self, _):
        calendarData = dict()
        seasons = (self.__epicController.getCurrentSeason(), self.__epicController.getNextSeason(), self.__epicController.getPreviousSeason())
        for season in seasons:
            if season is not None:
                calendarData['season'] = {'id': season.getSeasonID(),
                 'start': season.getStartDate(),
                 'end': season.getEndDate()}
                calendarData['cycles'] = [ {'id': cycle.ID,
                 'start': cycle.startDate,
                 'end': cycle.endDate,
                 'announce_only': cycle.announceOnly} for cycle in season.getAllCycles().values() ]
                break

        return calendarData
