# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: fort_rush/scripts/client/fort_rush/gui/impl/battle/fort_rush_hud.py
from __future__ import absolute_import
import time
import weakref
from helpers.CallbackDelayer import CallbackDelayer
from typing import Optional, Sequence, Tuple, Callable, TYPE_CHECKING
import GUI
import BigWorld
from PlayerEvents import g_playerEvents
from fort_rush.gui.impl.gen.view_models.views.battle.views.fort_rush_hud_view_model import FortRushHudViewModel, AnnouncementTypeEnum
from frameworks.wulf import WindowFlags, ViewSettings, WindowLayer
from gui.impl.gen import R
from gui.impl.pub import WindowImpl, ViewImpl
from gui.shared import EVENT_BUS_SCOPE
from gui.shared.events import GameEvent
from constants import ARENA_PERIOD
from fort_rush.gui.impl.battle.capture_indicators_ctrl import CaptureIndicatorsCtrl
from fort_rush.gui.impl.battle.team_score_sub_view import TeamScoreSubView
from skeletons.gui.app_loader import IAppLoader, GuiGlobalSpaceID
from skeletons.gui.battle_session import IBattleSessionProvider
from helpers import dependency, time_utils
from aih_constants import CTRL_MODE_NAME
if TYPE_CHECKING:
    import Event

class FortRushHudView(ViewImpl):
    LAYOUT_ID = R.views.fort_rush.mono.battle.fort_rush_hud()
    _sessionProvider = dependency.descriptor(IBattleSessionProvider)
    _appLoader = dependency.descriptor(IAppLoader)

    def __init__(self):
        settings = ViewSettings(self.LAYOUT_ID)
        settings.model = FortRushHudViewModel()
        self.__isBattleLoading = True
        self._callbackDelayer = CallbackDelayer()
        self.markersCtrl = GUI.WGMarkerPositionController()
        self.__captureIndicatorsCtrl = CaptureIndicatorsCtrl(weakref.proxy(self))
        super(FortRushHudView, self).__init__(settings)
        self.__teamScoreSubView = TeamScoreSubView(self.viewModel)

    @property
    def viewModel(self):
        return super(FortRushHudView, self).getViewModel()

    def _onLoading(self, *args, **kwargs):
        self.__setup()
        super(FortRushHudView, self)._onLoading(*args, **kwargs)

    def __setup(self):
        self.__captureIndicatorsCtrl.init()
        self.__teamScoreSubView.init()
        self.__isBattleLoading = self._appLoader.getSpaceID() != GuiGlobalSpaceID.BATTLE
        arenaPeriod = self._sessionProvider.shared.arenaPeriod.getPeriod()
        self._updateHudVisibility(arenaPeriod)
        self._setArenaPeriodTimer(arenaPeriod)

    def showHint(self, text, description, showCountdown, countdown):
        cd = time.time() + countdown if showCountdown else -1
        self.viewModel.setIsAnnouncementVisible(True)
        self._updateHint(text, description, cd)

    def hideHint(self):
        self.viewModel.setIsAnnouncementVisible(False)

    def _updateHint(self, text, description, countdown):
        self.viewModel.setAnnouncementCountdownTargetTime(countdown)
        self.viewModel.setAnnouncementHeading(text)
        self.viewModel.setAnnouncementDescription(description)
        self.viewModel.setAnnouncementType(AnnouncementTypeEnum.TEXT)

    def _startPeriodTimer(self):
        if not self._callbackDelayer.hasDelayedCallback(self._onSecond):
            self._onSecond()
            self._callbackDelayer.delayCallback(time_utils.ONE_SECOND, self._onSecond)

    def _stopPeriodTimer(self):
        self._callbackDelayer.stopCallback(self._onSecond)

    def _onSecond(self):
        periodCtrl = self._sessionProvider.shared.arenaPeriod
        period = periodCtrl.getPeriod()
        if period == ARENA_PERIOD.BATTLE:
            self.viewModel.setTimerSeconds(periodCtrl.getEndTime() - BigWorld.serverTime())
        return time_utils.ONE_SECOND

    def _getListeners(self):
        return ((GameEvent.BATTLE_LOADING, self._onBattleLoading, EVENT_BUS_SCOPE.BATTLE),)

    def _getEvents(self):
        events = []
        events.append((g_playerEvents.onArenaPeriodChange, self._onArenaPeriodChange))
        events.append((g_playerEvents.onRoundFinished, self._onRoundFinished))
        player = BigWorld.player()
        if player is not None and player.inputHandler is not None:
            events.append((player.inputHandler.onCameraChanged, self._onCameraChanged))
        return events

    def _onCameraChanged(self, controlModeName, vehicleID=None):
        self.viewModel.setIsSniperModeOn(controlModeName == CTRL_MODE_NAME.SNIPER)

    def _onBattleLoading(self, event):
        self.__isBattleLoading = bool(event.ctx.get('isShown', False))
        self.applyVisibility()

    def applyVisibility(self):
        window = self.getParentWindow()
        if window is None or not window.isBound():
            return
        else:
            if self.__isBattleLoading:
                if not window.isHidden():
                    window.hide()
            else:
                window.show(focus=False)
            return

    def _updateHudVisibility(self, arenaPeriod):
        model = self.getViewModel()
        with model.transaction() as transaction:
            hudVisibility = transaction.getHudVisibility()
            hudVisibility.set('announcement', True)
            hudVisibility.set('scorePanel', False)
            hudVisibility.set('capturingIndicator', False)
            hudVisibility.set('captureIndicators', False)
            hudVisibility.set('capturePointsMarker', False)
            if arenaPeriod == ARENA_PERIOD.BATTLE:
                hudVisibility.set('scorePanel', True)
                hudVisibility.set('capturingIndicator', True)
                hudVisibility.set('captureIndicators', True)
                hudVisibility.set('capturePointsMarker', True)
            elif arenaPeriod == ARENA_PERIOD.AFTERBATTLE:
                hudVisibility.set('announcement', False)
                hudVisibility.set('scorePanel', True)
                hudVisibility.set('captureIndicators', True)

    def _onRoundFinished(self, *args):
        with self.viewModel.transaction() as transaction:
            transaction.getHudVisibility().set('announcement', False)

    def _onArenaPeriodChange(self, arenaPeriod, *args):
        self._updateHudVisibility(arenaPeriod)
        self._setArenaPeriodTimer(arenaPeriod)

    def _setArenaPeriodTimer(self, arenaPeriod):
        if arenaPeriod in (ARENA_PERIOD.PREBATTLE, ARENA_PERIOD.BATTLE):
            self._startPeriodTimer()
            return
        self._stopPeriodTimer()

    def _finalize(self):
        self._callbackDelayer.destroy()
        self.markersCtrl.clear()
        if self.__captureIndicatorsCtrl:
            self.__captureIndicatorsCtrl.dispose()
            self.__captureIndicatorsCtrl = None
        if self.__teamScoreSubView:
            self.__teamScoreSubView.dispose()
            self.__teamScoreSubView = None
        super(FortRushHudView, self)._finalize()
        return


class FortRushHudWindow(WindowImpl):

    def __init__(self):
        super(FortRushHudWindow, self).__init__(WindowFlags.WINDOW | WindowFlags.WINDOW_FULLSCREEN, content=FortRushHudView(), layer=WindowLayer.MARKER)

    def _onReady(self):
        self.content.applyVisibility()
