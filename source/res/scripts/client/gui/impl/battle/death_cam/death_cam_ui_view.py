# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/battle/death_cam/death_cam_ui_view.py
import logging
from AvatarInputHandler.DynamicCameras.kill_cam_camera import CallbackPauseManager
from constants import IMPACT_TYPES
from frameworks.wulf.view.submodel_presenter import SubModelPresenter
from gui.battle_control.controllers.kill_cam_ctrl import KillCamInfoMarkerType, ImpactMarkerData
from gui.impl.gen.view_models.views.battle.death_cam.death_cam_hud_view_model import DeathCamHudViewModel, ImpactMode
from gui.shared.events import DeathCamEvent
from helpers import dependency
from skeletons.gui.battle_session import IBattleSessionProvider
_logger = logging.getLogger(__name__)

class DeathCamUIView(SubModelPresenter):
    __slots__ = ('__isSceneRunning', '__timerSeconds', '__callbackDelayer')
    __guiSessionProvider = dependency.descriptor(IBattleSessionProvider)
    _DISPLAY_DELAY = 0.75
    _UPDATE_TIMER_TICK = 0.1

    def __init__(self, viewModel, parentView):
        self.__isSceneRunning = True
        self.__timerSeconds = 0
        self.__callbackDelayer = CallbackPauseManager()
        super(DeathCamUIView, self).__init__(viewModel, parentView)

    @property
    def viewModel(self):
        return super(DeathCamUIView, self).getViewModel()

    def resetDisplay(self):
        self.__callbackDelayer.clearCallbacks()
        self.__isSceneRunning = False

    def startDisplayTimer(self, seconds):
        self.__timerSeconds = seconds
        self.__callbackDelayer.delayCallback(self._UPDATE_TIMER_TICK, self.updateTimerCallback)

    def updateTimerCallback(self):
        callbackTime = None
        if self.__timerSeconds > 0:
            self.__timerSeconds = round(max(self.__timerSeconds - self._UPDATE_TIMER_TICK, 0), 1)
            callbackTime = min(self._UPDATE_TIMER_TICK, self.__timerSeconds)
        self.updatePauseText()
        return callbackTime

    def updatePauseText(self, seconds=None):
        if seconds is not None:
            self.__timerSeconds = seconds
        self.viewModel.hud.setRemainingTime(self.__timerSeconds)
        return

    def initialize(self):
        super(DeathCamUIView, self).initialize()
        killCamCtrl = self.__guiSessionProvider.shared.killCamCtrl
        if killCamCtrl:
            killCamCtrl.onKillCamModeStateChanged += self.__onKillCamStateChanged
            killCamCtrl.onMarkerDisplayChanged += self.__onMarkerDisplayChanged

    def finalize(self):
        self.__callbackDelayer.clearCallbacks()
        killCamCtrl = self.__guiSessionProvider.shared.killCamCtrl
        if killCamCtrl:
            killCamCtrl.onKillCamModeStateChanged -= self.__onKillCamStateChanged
            killCamCtrl.onMarkerDisplayChanged -= self.__onMarkerDisplayChanged

    def __onKillCamStateChanged(self, killCamState, totalSceneDuration):
        if killCamState is DeathCamEvent.State.PAUSE:
            self.__callbackDelayer.pauseCallbacks()
            self.__barsVisibility(False)
            self.updatePauseText()
        elif killCamState is DeathCamEvent.State.RESUME:
            self.__callbackDelayer.resumeCallbacks()
            self.__barsVisibility(True)
            self.updatePauseText()
        elif killCamState is DeathCamEvent.State.ENDING:
            self.viewModel.hud.setIsFinalPhase(False)
            self.__barsVisibility(False)
        elif killCamState is DeathCamEvent.State.ACTIVE:
            sceneDuration = totalSceneDuration
            self.startDisplayTimer(sceneDuration)
            self.__barsVisibility(True)
        elif killCamState is DeathCamEvent.State.FINISHED:
            self.resetDisplay()

    def __onMarkerDisplayChanged(self, markerType, ctx):
        if markerType is not KillCamInfoMarkerType.IMPACT:
            return
        markerData = ctx['markerData']
        impactType = markerData.impactType
        if impactType == IMPACT_TYPES.PENETRATION:
            self.viewModel.setImpactMode(ImpactMode.PENETRATION)
        elif impactType == IMPACT_TYPES.NON_PENETRATION_DAMAGE:
            self.viewModel.setImpactMode(ImpactMode.NONPENETRATIONDAMAGE)
        elif impactType == IMPACT_TYPES.LEGACY_HE:
            self.viewModel.setImpactMode(ImpactMode.LEGACYHE)
        else:
            self.viewModel.setImpactMode(ImpactMode.MODERNHE)
        self.__callbackDelayer.delayCallback(self._DISPLAY_DELAY, self.__triggerFinalPhase)

    def __triggerFinalPhase(self):
        self.viewModel.hud.setIsFinalPhase(True)

    def __barsVisibility(self, show=True):
        self.__isSceneRunning = show
        self.viewModel.hud.setBarsVisible(self.__isSceneRunning)
