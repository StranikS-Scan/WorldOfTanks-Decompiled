# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/avatar_components/avatar_recovery_mechanic.py
from functools import partial
import BigWorld
from arena_bonus_type_caps import ARENA_BONUS_TYPE_CAPS as BONUS_CAPS
import CommandMapping
from constants import RM_STATE
from gui.battle_control.battle_constants import VEHICLE_VIEW_STATE

class AvatarRecoveryMechanic(object):

    def __init__(self):
        self.__enabled = False
        self.__lastRecoveryArgs = None
        self.__keyCheckCallback = None
        self.__recoveryRequested = False
        return

    def onBecomePlayer(self):
        self.__enabled = BONUS_CAPS.checkAny(self.arenaBonusType, BONUS_CAPS.RECOVERY_MECHANIC)
        if not self.__enabled:
            return
        else:
            self.__lastRecoveryArgs = None
            return

    def handleKey(self, isDown, key, mods):
        if not self.__enabled:
            return
        else:
            cmdMap = CommandMapping.g_instance
            isFired = cmdMap.isFired(CommandMapping.CMD_REQUEST_RECOVERY, key)
            if isFired and self.isVehicleAlive and not self.isObserver():
                if isDown and not self.isForcedGuiControlMode():
                    if self.__currentRevcoveryState() in (None, RM_STATE.NOT_RECOVERING):
                        ownVehicle = BigWorld.entity(self.playerVehicleID)
                        ownVehicle.cell.recoveryMechanic_startRecovering()
                        if not self.__keyCheckCallback:
                            self.__keyCheckCallback = BigWorld.callback(0.1, partial(self.__checkKey, key))
                    if self.__currentRevcoveryState() == RM_STATE.TEMPORARILY_BLOCKED_FROM_RECOVERING:
                        activated, _, timerDuration, endOfTimer = self.__lastRecoveryArgs
                        self.guiSessionProvider.shared.feedback.setVehicleRecoveryState(self.playerVehicleID, activated, RM_STATE.TEMPORARILY_BLOCKED_RECOVER_TRY, timerDuration, endOfTimer)
                elif not isDown:
                    if self.__currentRevcoveryState() == RM_STATE.RECOVERING:
                        ownVehicle = BigWorld.entity(self.playerVehicleID)
                        ownVehicle.cell.recoveryMechanic_stopRecovering()
                        if self.__keyCheckCallback:
                            BigWorld.cancelCallback(self.__keyCheckCallback)
                            self.__keyCheckCallback = None
                self.__recoveryRequested = True
            return

    def onBecomeNonPlayer(self):
        if not self.__enabled:
            return
        else:
            self.__lastRecoveryArgs = None
            return

    def notifyCannotStartRecovering(self):
        pass

    def notifyCancelled(self):
        if self.isVehicleAlive and not self.isObserver():
            self.guiSessionProvider.shared.feedback.setVehicleRecoveryCanceled(self.playerVehicleID)

    def updateState(self, activated, state, timerDuration, endOfTimer):
        if not activated:
            state = RM_STATE.PERMANENTLY_BLOCKED_FROM_RECOVERING
        self.__lastRecoveryArgs = (activated,
         state,
         timerDuration,
         endOfTimer)
        if not self.__recoveryRequested:
            return
        else:
            if activated:
                if state == RM_STATE.RECOVERING:
                    self.guiSessionProvider.invalidateVehicleState(VEHICLE_VIEW_STATE.RECOVERY, (True, timerDuration, endOfTimer))
                elif state in {RM_STATE.NOT_RECOVERING, RM_STATE.TEMPORARILY_BLOCKED_FROM_RECOVERING, RM_STATE.RECOVERING_RESPAWNING}:
                    self.guiSessionProvider.invalidateVehicleState(VEHICLE_VIEW_STATE.RECOVERY, (False, 0, None))
                self.guiSessionProvider.shared.feedback.setVehicleRecoveryState(self.playerVehicleID, activated, state, timerDuration, endOfTimer)
            if state == RM_STATE.RECOVERING_RESPAWNING and BigWorld.player().vehicle.isPlayerVehicle:
                self.inputHandler.activatePostmortem(True)
            return

    def getLastRecoveryArgs(self):
        return self.__lastRecoveryArgs

    def __currentRevcoveryState(self):
        return None if self.__lastRecoveryArgs is None else self.__lastRecoveryArgs[1]

    def __checkKey(self, key):
        if not self.__keyCheckCallback:
            return
        else:
            if BigWorld.isKeyDown(key):
                self.__keyCheckCallback = BigWorld.callback(1, partial(self.__checkKey, key))
            else:
                self.__keyCheckCallback = None
                ownVehicle = BigWorld.entity(self.playerVehicleID)
                ownVehicle.cell.recoveryMechanic_stopRecovering()
            return
