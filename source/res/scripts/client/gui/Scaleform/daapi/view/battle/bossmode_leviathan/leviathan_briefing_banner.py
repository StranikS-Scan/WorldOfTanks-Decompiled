# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/battle/bossmode_leviathan/leviathan_briefing_banner.py
from gui.Scaleform.daapi.view.meta.HalloweenBriefingBannerMeta import HalloweenBriefingBannerMeta
from gui.battle_control.battle_constants import COUNTDOWN_STATE
from gui.battle_control.controllers.period_ctrl import IAbstractPeriodView
from gui.shared import EVENT_BUS_SCOPE, events

class HalloweenBriefingBanner(HalloweenBriefingBannerMeta, IAbstractPeriodView):

    def __init__(self):
        super(HalloweenBriefingBanner, self).__init__()
        self.__isHiddenByCountdown = False
        self.__isShownByCountdown = False
        self.__isFinishedBattleLoading = False

    def _populate(self):
        super(HalloweenBriefingBanner, self)._populate()
        self.addListener(events.GameEvent.BATTLE_LOADING, self.__handleBattleLoading, EVENT_BUS_SCOPE.BATTLE)

    def _dispose(self):
        self.removeListener(events.GameEvent.BATTLE_LOADING, self.__handleBattleLoading, scope=EVENT_BUS_SCOPE.BATTLE)
        super(HalloweenBriefingBanner, self)._dispose()

    def setCountdown(self, state, timeLeft):
        if not self.__isShownByCountdown and state == COUNTDOWN_STATE.START and timeLeft > 4:
            self.__isShownByCountdown = True
            self.__updateShownState()
        elif not self.__isHiddenByCountdown and state == COUNTDOWN_STATE.START and timeLeft <= 4:
            self.__isHiddenByCountdown = True
            self.__updateShownState()

    def __updateShownState(self):
        if self.__isHiddenByCountdown:
            self.as_hideS()
        elif self.__isShownByCountdown and self.__isFinishedBattleLoading:
            self.as_showS()

    def __handleBattleLoading(self, event):
        if not event.ctx['isShown']:
            self.__isFinishedBattleLoading = True
            self.__updateShownState()
