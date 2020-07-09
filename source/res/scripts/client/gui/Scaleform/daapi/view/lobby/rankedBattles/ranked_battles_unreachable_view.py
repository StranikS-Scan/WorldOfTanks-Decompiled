# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/rankedBattles/ranked_battles_unreachable_view.py
from gui.ranked_battles.ranked_helpers.sound_manager import RANKED_SUBVIEW_SOUND_SPACE
from gui.ranked_battles.ranked_builders.unreachable_vos import getUnreachableVO
from gui.Scaleform.daapi import LobbySubView
from gui.Scaleform.daapi.settings.views import VIEW_ALIAS
from gui.Scaleform.daapi.view.meta.RankedBattlesUnreachableViewMeta import RankedBattlesUnreachableViewMeta
from gui.shared import events, EVENT_BUS_SCOPE
from gui.shared.utils.scheduled_notifications import PeriodicNotifier
from helpers import dependency, time_utils
from skeletons.gui.game_control import IRankedBattlesController

class RankedBattlesUnreachableView(LobbySubView, RankedBattlesUnreachableViewMeta):
    __rankedController = dependency.descriptor(IRankedBattlesController)
    _COMMON_SOUND_SPACE = RANKED_SUBVIEW_SOUND_SPACE
    __background_alpha__ = 0.5

    def __init__(self, _):
        super(RankedBattlesUnreachableView, self).__init__()
        self.__currentSeason = None
        self.__periodicNotifier = PeriodicNotifier(self.__timeTillCurrentSeasonEnd, self.__updateData)
        return

    def onEscapePress(self):
        self.__close()

    def onCloseBtnClick(self):
        self.__close()

    def _populate(self):
        super(RankedBattlesUnreachableView, self)._populate()
        self.__rankedController.onUpdated += self.__update
        self.__update()

    def _dispose(self):
        self.__periodicNotifier.stopNotification()
        self.__periodicNotifier.clear()
        self.__rankedController.onUpdated -= self.__update
        super(RankedBattlesUnreachableView, self)._dispose()

    def __close(self):
        self.fireEvent(events.LoadViewEvent(VIEW_ALIAS.LOBBY_HANGAR), scope=EVENT_BUS_SCOPE.LOBBY)
        self.destroy()

    def __checkDestroy(self):
        if self.__currentSeason is None:
            self.__close()
        return

    def __timeTillCurrentSeasonEnd(self):
        if self.__currentSeason:
            seasonEnd = time_utils.makeLocalServerTime(self.__currentSeason.getEndDate())
            return time_utils.getTimeDeltaFromNowInLocal(seasonEnd)
        return time_utils.ONE_MINUTE

    def __update(self):
        self.__currentSeason = self.__rankedController.getCurrentSeason()
        self.__checkDestroy()
        self.__periodicNotifier.startNotification()
        self.__updateData()

    def __updateData(self):
        minLvl, maxLvl = self.__rankedController.getSuitableVehicleLevels()
        self.as_setDataS(getUnreachableVO(self.__currentSeason, minLvl, maxLvl))
