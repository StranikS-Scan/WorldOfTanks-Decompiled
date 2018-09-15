# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/bootcamp/states/StateInBattle.py
import BattleReplay
import BigWorld
import SoundGroups
from AbstractState import AbstractState
from bootcamp.aop.in_battle import weave
from bootcamp.Assistant import BattleAssistant
from bootcamp.BootCampEvents import g_bootcampEvents
from bootcamp.scenery.Scenery import Scenery
from bootcamp.states import STATE
from bootcamp.BootcampConstants import UI_STATE, BOOTCAMP_BATTLE_RESULT_MESSAGE
from gui.Scaleform.daapi.view.bootcamp.BCBattleSpaceEnv import BCBattleSpaceEnv
from gui.app_loader.settings import GUI_GLOBAL_SPACE_ID as _SPACE_ID
from skeletons.gui.sounds import ISoundsController
from helpers import dependency, aop
from PlayerEvents import g_playerEvents
from bootcamp.Bootcamp import g_bootcamp
from gui.battle_control import event_dispatcher as gui_event_dispatcher
from debug_utils import LOG_DEBUG

class StateInBattle(AbstractState):
    soundController = dependency.instance(ISoundsController)

    def __init__(self, lessonId, avatar, entities, bootcampGui):
        super(StateInBattle, self).__init__(STATE.IN_BATTLE)
        self.__assistant = BattleAssistant(avatar, lessonId, entities, bootcampGui)
        self.__lessonId = lessonId
        self.__avatar = avatar
        self.__scenery = Scenery(lessonId, self.__assistant)
        self.__oldSpaceEnv = None
        self.__weaver = aop.Weaver()
        return

    def handleKeyEvent(self, event):
        return True

    def onKickedFromArena(self, reasonCode):
        arenaID = BigWorld.player().arenaUniqueID
        g_bootcamp.setBattleResults(arenaID, BOOTCAMP_BATTLE_RESULT_MESSAGE.FAILURE, reasonCode)

    def onBattleAction(self, actionId, actionParams):
        self.__assistant.onAction(actionId, actionParams)

    def stopScenery(self):
        if self.__scenery is not None:
            self.__scenery.stop()
            self.__scenery.destroy()
            self.__scenery = None
        return

    def onAvatarReceiveBattleResults(self, isSuccess, data):
        if self.__finishAnimationCompleted:
            return False
        self.__battleResultsData['isSuccess'] = isSuccess
        self.__battleResultsData['data'] = data

    def _onBattleFinishAnimationComplete(self):
        self.__finishAnimationCompleted = True
        if self.__battleResultsData:
            BigWorld.player().receiveBattleResults(isSuccess=self.__battleResultsData['isSuccess'], data=self.__battleResultsData['data'])

    def _doActivate(self):
        weave(self.__weaver, self)
        g_bootcampEvents.onUIStateChanged += self._onUIStateChanged
        g_bootcampEvents.onBattleFinishAnimationComplete += self._onBattleFinishAnimationComplete
        g_playerEvents.onKickedFromArena += self.onKickedFromArena
        g_playerEvents.onRoundFinished += self.__onRoundFinished
        g_playerEvents.onAvatarBecomeNonPlayer += self.__onAvatarBecomeNonPlayer
        self.__assistant.start()
        self.__scenery.start()
        self.__assistant.getMarkers().afterScenery()
        self.__oldSpaceEnv = self.soundController.setEnvForSpace(_SPACE_ID.BATTLE, BCBattleSpaceEnv)
        self.__battleResultsData = {}
        self.__finishAnimationCompleted = True
        player = BigWorld.player()
        if player is not None and player.inputHandler is not None:
            player.inputHandler.onCameraChanged += self.__onCameraChanged
        return

    def _onUIStateChanged(self, state):
        if state == UI_STATE.STOP:
            self.stopScenery()

    def _doDeactivate(self):
        if self.__oldSpaceEnv is not None:
            self.soundController.setEnvForSpace(_SPACE_ID.BATTLE, self.__oldSpaceEnv)
        g_bootcampEvents.onUIStateChanged -= self._onUIStateChanged
        g_bootcampEvents.onBattleFinishAnimationComplete -= self._onBattleFinishAnimationComplete
        g_playerEvents.onKickedFromArena -= self.onKickedFromArena
        g_playerEvents.onRoundFinished -= self.__onRoundFinished
        g_playerEvents.onAvatarBecomeNonPlayer -= self.__onAvatarBecomeNonPlayer
        self._onUIStateChanged(UI_STATE.STOP)
        self.onAvatarBecomeNonPlayer()
        if self.__assistant is not None:
            self.__assistant = None
        self.__battleResultsData.clear()
        self.__weaver.clear()
        return

    def __onCameraChanged(self, cameraName, currentVehicleId):
        if cameraName == 'sniper':
            if not g_bootcamp.isSniperModeUsed():
                camera = BigWorld.player().inputHandler.ctrl.camera
                camera.setMaxZoom()
                g_bootcamp.setSniperModeUsed(True)

    def __onRoundFinished(self, winnerTeam, reason):
        if BattleReplay.g_replayCtrl.isPlaying:
            return
        else:
            g_bootcampEvents.onUIStateChanged(UI_STATE.STOP)
            gui_event_dispatcher.toggleGUIVisibility()
            from gui.Scaleform.daapi.settings.views import VIEW_ALIAS
            from gui.shared import events, g_eventBus, EVENT_BUS_SCOPE
            asBattleResultType = BOOTCAMP_BATTLE_RESULT_MESSAGE.DEFEAT
            if winnerTeam == BigWorld.player().team:
                asBattleResultType = BOOTCAMP_BATTLE_RESULT_MESSAGE.VICTORY
            elif winnerTeam == 0:
                asBattleResultType = BOOTCAMP_BATTLE_RESULT_MESSAGE.DRAW
            g_bootcamp.setBattleResults(BigWorld.player().arenaUniqueID, asBattleResultType, reason)
            LOG_DEBUG('Show battle result final message.')
            g_eventBus.handleEvent(events.LoadViewEvent(VIEW_ALIAS.BOOTCAMP_BATTLE_FINISHED_WINDOW, None), EVENT_BUS_SCOPE.BATTLE)
            if asBattleResultType == BOOTCAMP_BATTLE_RESULT_MESSAGE.VICTORY:
                SoundGroups.g_instance.playSound2D('vo_bc_victory')
            elif asBattleResultType == BOOTCAMP_BATTLE_RESULT_MESSAGE.DEFEAT:
                SoundGroups.g_instance.playSound2D('vo_bc_defeat')
            elif asBattleResultType == BOOTCAMP_BATTLE_RESULT_MESSAGE.DRAW:
                SoundGroups.g_instance.playSound2D('vo_bc_draw')
            return

    def __onAvatarBecomeNonPlayer(self):
        player = BigWorld.player()
        if player is not None and player.inputHandler is not None:
            player.inputHandler.onCameraChanged -= self.__onCameraChanged
        if self.__assistant is not None:
            self.__assistant.stop()
        self.__avatar = None
        self.stopScenery()
        return
