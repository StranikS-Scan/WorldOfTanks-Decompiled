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
from skeletons.gui.app_loader import GuiGlobalSpaceID
from skeletons.gui.sounds import ISoundsController
from helpers import dependency, aop
from PlayerEvents import g_playerEvents
from bootcamp.Bootcamp import g_bootcamp

class StateInBattle(AbstractState):
    soundController = dependency.descriptor(ISoundsController)

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
        g_bootcampEvents.onUIStateChanged(UI_STATE.STOP)

    def onBattleAction(self, actionId, actionParams):
        self.__assistant.onAction(actionId, actionParams)

    def stopScenery(self):
        if self.__scenery is not None:
            self.__scenery.stop()
            self.__scenery.destroy()
            self.__scenery = None
        return

    def _doActivate(self):
        weave(self.__weaver)
        g_bootcampEvents.onUIStateChanged += self._onUIStateChanged
        g_playerEvents.onKickedFromArena += self.onKickedFromArena
        g_playerEvents.onRoundFinished += self.__onRoundFinished
        g_playerEvents.onAvatarBecomeNonPlayer += self.__onAvatarBecomeNonPlayer
        self.__assistant.start()
        self.__scenery.start()
        self.__assistant.getMarkers().afterScenery()
        self.__oldSpaceEnv = self.soundController.setEnvForSpace(GuiGlobalSpaceID.BATTLE, BCBattleSpaceEnv)
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
            self.soundController.setEnvForSpace(GuiGlobalSpaceID.BATTLE, self.__oldSpaceEnv)
        g_bootcampEvents.onUIStateChanged -= self._onUIStateChanged
        g_playerEvents.onKickedFromArena -= self.onKickedFromArena
        g_playerEvents.onRoundFinished -= self.__onRoundFinished
        g_playerEvents.onAvatarBecomeNonPlayer -= self.__onAvatarBecomeNonPlayer
        self._onUIStateChanged(UI_STATE.STOP)
        self.onAvatarBecomeNonPlayer()
        if self.__assistant is not None:
            self.__assistant = None
        self.__weaver.clear()
        return

    def __onCameraChanged(self, cameraName, currentVehicleId=None):
        if cameraName == 'sniper':
            if not g_bootcamp.isSniperModeUsed():
                camera = BigWorld.player().inputHandler.ctrl.camera
                camera.setMaxZoom()
                g_bootcamp.setSniperModeUsed(True)
        elif cameraName == 'postmortem':
            g_bootcampEvents.onUIStateChanged(UI_STATE.STOP)

    def __onRoundFinished(self, winnerTeam, reason):
        if BattleReplay.g_replayCtrl.isPlaying:
            return
        g_bootcampEvents.onUIStateChanged(UI_STATE.STOP)
        g_bootcampEvents.hideGUIForWinMessage()
        asBattleResultType = BOOTCAMP_BATTLE_RESULT_MESSAGE.DEFEAT
        if winnerTeam == BigWorld.player().team:
            asBattleResultType = BOOTCAMP_BATTLE_RESULT_MESSAGE.VICTORY
        elif winnerTeam == 0:
            asBattleResultType = BOOTCAMP_BATTLE_RESULT_MESSAGE.DRAW
        g_bootcamp.setBattleResults(BigWorld.player().arenaUniqueID, asBattleResultType, reason)
        if asBattleResultType == BOOTCAMP_BATTLE_RESULT_MESSAGE.VICTORY:
            SoundGroups.g_instance.playSound2D('vo_bc_victory')
        elif asBattleResultType == BOOTCAMP_BATTLE_RESULT_MESSAGE.DEFEAT:
            SoundGroups.g_instance.playSound2D('vo_bc_defeat')
        elif asBattleResultType == BOOTCAMP_BATTLE_RESULT_MESSAGE.DRAW:
            SoundGroups.g_instance.playSound2D('vo_bc_draw')

    def __onAvatarBecomeNonPlayer(self):
        player = BigWorld.player()
        if player is not None and player.inputHandler is not None:
            player.inputHandler.onCameraChanged -= self.__onCameraChanged
        g_bootcampEvents.onUIStateChanged(UI_STATE.STOP)
        self.__avatar = None
        self.stopScenery()
        return
