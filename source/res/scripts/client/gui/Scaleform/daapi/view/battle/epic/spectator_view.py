# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/battle/epic/spectator_view.py
import BigWorld
from gui.Scaleform.daapi.view.meta.EpicSpectatorViewMeta import EpicSpectatorViewMeta
from helpers import dependency
from skeletons.gui.battle_session import IBattleSessionProvider
from debug_utils import LOG_ERROR
from gui.battle_control import avatar_getter
from gui.Scaleform.genConsts.EPIC_CONSTS import EPIC_CONSTS
from helpers import time_utils
from gui.Scaleform.locale.EPIC_BATTLE import EPIC_BATTLE
from helpers.i18n import makeString
from gui.sounds.epic_sound_constants import EPIC_SOUND

class EpicSpectatorView(EpicSpectatorViewMeta):
    sessionProvider = dependency.descriptor(IBattleSessionProvider)

    def __init__(self):
        super(EpicSpectatorView, self).__init__()
        self.isInPostmortem = False
        self.isTankFocused = False
        self.__isInRespawn = False
        self.__timestamp = 0
        self.__timeCB = None
        return

    def _populate(self):
        super(EpicSpectatorView, self)._populate()
        self.sessionProvider.onBattleSessionStart += self.__onBattleSessionStart
        self.sessionProvider.onBattleSessionStop += self.__onBattleSessionStop
        self.as_setFollowInfoTextS(makeString(EPIC_BATTLE.SPECTATOR_MODE_FOLLOW_TEXT))
        self.as_focusOnVehicleS(False)
        self.isTankFocused = False

    def _dispose(self):
        self.sessionProvider.onBattleSessionStart -= self.__onBattleSessionStart
        self.sessionProvider.onBattleSessionStop -= self.__onBattleSessionStop
        super(EpicSpectatorView, self)._dispose()

    def _addGameListeners(self):
        super(EpicSpectatorView, self)._addGameListeners()
        ctrl = self.sessionProvider.shared.vehicleState
        if ctrl is not None:
            ctrl.onPostMortemSwitched += self.__onPostMortemSwitched
            ctrl.onRespawnBaseMoving += self.__onRespawnBaseMoving
            self.isInPostmortem = ctrl.isInPostmortem
        specCtrl = self.sessionProvider.dynamic.spectator
        if specCtrl is not None:
            specCtrl.onSpectatorViewModeChanged += self.__onSpectatorModeChanged
            specCtrl.onSpectatedVehicleChanged += self.__onSpectatedVehicleChanged
            self.__onSpectatorModeChanged(specCtrl.spectatorViewMode)
            self.__onSpectatedVehicleChanged(specCtrl.spectatedVehicle)
        ctrl = self.sessionProvider.dynamic.respawn
        if ctrl is not None:
            ctrl.onRespawnVisibilityChanged += self.__onRespawnVisibility
            self.__onRespawnVisibility(ctrl.isRespawnVisible())
        playerComp = getattr(self.sessionProvider.arenaVisitor.getComponentSystem(), 'playerDataComponent', None)
        if playerComp is not None:
            playerComp.onReinforcementTimerUpdated += self.__onReinforcementTimerUpdated
            self.__onReinforcementTimerUpdated(playerComp.reinforcementTimer)
        else:
            LOG_ERROR('Expected PayerDataComponent not present!')
        return

    def _removeGameListeners(self):
        playerComp = getattr(self.sessionProvider.arenaVisitor.getComponentSystem(), 'playerDataComponent', None)
        if playerComp is not None:
            playerComp.onReinforcementTimerUpdated -= self.__onReinforcementTimerUpdated
        ctrl = self.sessionProvider.shared.vehicleState
        if ctrl is not None:
            ctrl.onPostMortemSwitched -= self.__onPostMortemSwitched
            ctrl.onRespawnBaseMoving -= self.__onRespawnBaseMoving
        ctrl = self.sessionProvider.dynamic.spectator
        if ctrl is not None:
            ctrl.onSpectatorViewModeChanged -= self.__onSpectatorModeChanged
            ctrl.onSpectatedVehicleChanged -= self.__onSpectatedVehicleChanged
        ctrl = self.sessionProvider.dynamic.respawn
        if ctrl is not None:
            ctrl.onRespawnVisibilityChanged -= self.__onRespawnVisibility
        super(EpicSpectatorView, self)._removeGameListeners()
        return

    def _updateVehicleInfo(self):
        if self.__isInRespawn:
            return
        self._deathAlreadySet = False
        if self._isPlayerVehicle and not avatar_getter.isVehicleAlive():
            self._showOwnDeathInfo()
        else:
            self._showPlayerInfo()

    def __onBattleSessionStart(self):
        self._addGameListeners()

    def __onBattleSessionStop(self):
        self._removeGameListeners()
        if self.__timeCB:
            BigWorld.cancelCallback(self.__timeCB)
            self.__timeCB = None
        return

    def __onPostMortemSwitched(self, noRespawnPossible, respawnAvailable):
        self.isInPostmortem = True

    def __onRespawnBaseMoving(self):
        if not self.isInPostmortem:
            return
        self.isInPostmortem = False

    def __onSpectatorModeChanged(self, mode):
        self.as_changeModeS(mode)
        if mode == EPIC_CONSTS.SPECTATOR_MODE_FOLLOW:
            self.__playSound(EPIC_SOUND.BF_EB_SPECTATOR_MODE_FOLLOW_TANK)
        elif mode == EPIC_CONSTS.SPECTATOR_MODE_FREECAM:
            self.as_setPlayerInfoS('')
        elif mode == EPIC_CONSTS.SPECTATOR_MODE_DEATHCAM:
            pass

    def __onSpectatedVehicleChanged(self, vehicleID):
        if vehicleID is not None:
            self.as_focusOnVehicleS(True)
            if self.isTankFocused is False:
                self.__playSound(EPIC_SOUND.BF_EB_LEFT_CLICK_TO_FOLLOW)
                self.isTankFocused = True
        else:
            self.as_focusOnVehicleS(False)
            self.isTankFocused = False
        return

    def __playSound(self, eventName):
        if not EPIC_SOUND.EPIC_MSG_SOUNDS_ENABLED:
            return
        soundNotifications = avatar_getter.getSoundNotifications()
        if soundNotifications and hasattr(soundNotifications, 'play'):
            soundNotifications.play(eventName)

    def __onRespawnVisibility(self, isVisible):
        self.__isInRespawn = isVisible
        self.as_setPlayerInfoS('')
        if isVisible:
            self._deathAlreadySet = False

    def __onReinforcementTimerUpdated(self, time):
        self.__timestamp = time
        if time is None:
            if self.__timeCB:
                BigWorld.cancelCallback(self.__timeCB)
                self.__timeCB = None
        elif not self.__timeCB:
            self.__timeCB = BigWorld.callback(1, self.__tick)
        return

    def __tick(self):
        diffTime = self.__timestamp - BigWorld.serverTime()
        if diffTime <= 0:
            self.__timeCB = None
            self.as_setTimerS('0:00')
        else:
            timeStr = time_utils.getTimeLeftFormat(diffTime)
            self.as_setTimerS(timeStr)
            if self.__timeCB is not None:
                self.__timeCB = BigWorld.callback(1, self.__tick)
        return
