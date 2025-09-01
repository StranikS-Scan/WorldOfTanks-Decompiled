# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: white_tiger/scripts/client/WTBattleStateComponent.py
from functools import partial
import Event
import BigWorld
from helpers import dependency
from skeletons.gui.battle_session import IBattleSessionProvider
from constants import IS_VS_EDITOR
from script_component.DynamicScriptComponent import DynamicScriptComponent
from white_tiger_common.wt_constants import WTGeneratorState
if not IS_VS_EDITOR:
    from white_tiger.gui.white_tiger_gui_constants import FEEDBACK_EVENT_ID
_PERIOD = 0.1

class WTBattleStateComponent(DynamicScriptComponent):
    __sessionProvider = dependency.descriptor(IBattleSessionProvider)

    def __init__(self):
        super(WTBattleStateComponent, self).__init__()
        from helpers.CallbackDelayer import CallbackDelayer
        self.__cd = CallbackDelayer()
        self.__previousRemainingTime = 0
        self.onPublicHealthChange = Event.Event()
        self.onHyperionCharge = Event.Event()
        self.onShieldStatusChange = Event.Event()
        self.onGeneratorDestroyed = Event.Event()
        self.onShieldDowntime = Event.Event()
        self.onGeneratorCapture = Event.Event()
        self.onGeneratorStopCapture = Event.Event()
        self.onGeneratorsLeftInitialize = Event.Event()
        self.onUpdateCamp = Event.Event()
        self.onGeneratorLocked = Event.Event()

    def onDestroy(self):
        super(WTBattleStateComponent, self).onDestroy()
        self.onPublicHealthChange.clear()
        self.onHyperionCharge.clear()
        self.onShieldStatusChange.clear()
        self.onGeneratorDestroyed.clear()
        self.onShieldDowntime.clear()
        self.onGeneratorCapture.clear()
        self.onGeneratorStopCapture.clear()
        self.onGeneratorLocked.clear()
        self.onUpdateCamp.clear()
        self.onGeneratorsLeftInitialize.clear()
        self.__cd.destroy()
        self.__cd = None
        return

    def _onAvatarReady(self):
        for healthInfo in self.healthInfoList:
            self.__notifyHealthChange(healthInfo)

        self.__notifyHyperionChargeChange(self.hyperionCharge)
        self.__notifyShieldStatus(self.isShieldDown)
        self.__onGeneratorsLeftInitialize(self.generatorsLeft)
        if self.isShieldDown and self.generatorsLeft > 0:
            self.__cd.delayCallback(_PERIOD, self.__notifyShieldDowntime)

    def setNested_healthInfoList(self, path, prev):
        self.__notifyHealthChange(self.healthInfoList[path[0]])

    def setSlice_healthInfoList(self, path, prev):
        self.__notifyHealthChange(self.healthInfoList[path[0][0]])

    def set_plasmaDamageDict(self, _):
        if not self.plasmaDamageDict:
            return
        self.__notifyPlasmaDamage(self.plasmaDamageDict)

    def set_hyperionCharge(self, _=0):
        self.__notifyHyperionChargeChange(self.hyperionCharge)

    def set_isShieldDown(self, _=True):
        self.__notifyShieldStatus(self.isShieldDown)

    def set_generatorsLeft(self, _):
        if self.generatorsLeft < 0:
            return
        self.__notifyGeneratorDestroyed(self.generatorsLeft)

    def set_shieldDowntime(self, _):
        if not self.isShieldDown or self.generatorsLeft <= 0:
            return
        self.__cd.destroy()
        self.__previousRemainingTime = 0
        self.__cd.delayCallback(_PERIOD, self.__notifyShieldDowntime)

    def receiveSentinelData(self, generatorID, sentinelData):
        self.onUpdateCamp(generatorID, sentinelData)

    def receiveGeneratorStatus(self, generatorID, status, entityID, blockedByMiniboss=False, isInit=False):
        wasCaptured = status == WTGeneratorState.CAPTURED
        if status == WTGeneratorState.BLOCKED:
            if blockedByMiniboss:
                self.onGeneratorLocked(generatorID, True, entityID, isInit, self.isCaptureBlocked)
            if self.isCaptureBlocked:
                self.receiveGeneratorStopCaptureProgress(generatorID, wasCaptured)
            return
        self.onGeneratorLocked(generatorID, False, entityID, isInit, self.isCaptureBlocked)
        self.onGeneratorStopCapture(generatorID, wasCaptured)

    def receiveGeneratorCaptureInProgress(self, generatorID, activationProgress, status):
        if self.isCaptureBlocked:
            return
        isBlocked = status == WTGeneratorState.BLOCKED
        numInvaders = len(activationProgress.invadersVehicleIDs)
        self.onGeneratorCapture(generatorID, activationProgress.progress, activationProgress.timeLeft, numInvaders, isBlocked)

    def receiveGeneratorStopCaptureProgress(self, generatorID, state):
        wasCaptured = state == WTGeneratorState.CAPTURED
        self.onGeneratorStopCapture(generatorID, wasCaptured)

    def __notifyHealthChange(self, healthInfo):
        self.onPublicHealthChange(healthInfo.vehicleID, healthInfo.health)

    def __notifyHyperionChargeChange(self, hyperionCharge):
        self.onHyperionCharge(hyperionCharge)

    def __notifyShieldStatus(self, isShieldDown):
        self.onShieldStatusChange(isShieldDown)
        if not isShieldDown:
            self.__cd.destroy()

    def __notifyGeneratorDestroyed(self, generatorsLeft):
        BigWorld.callback(0, partial(self.onGeneratorDestroyed, generatorsLeft))

    def __onGeneratorsLeftInitialize(self, generatorsLeft):
        if generatorsLeft < 0:
            return
        self.onGeneratorsLeftInitialize(generatorsLeft)

    def __notifyShieldDowntime(self):
        remainingTime = max(0, self.shieldDowntime[1] - BigWorld.serverTime())
        if remainingTime == self.__previousRemainingTime:
            return _PERIOD
        else:
            self.onShieldDowntime(self.shieldDowntime[0], max(0, remainingTime))
            self.__previousRemainingTime = remainingTime
            return None if remainingTime <= 0 else _PERIOD

    def __notifyPlasmaDamage(self, plasmaDamageDict):
        feedback = self.__sessionProvider.shared.feedback
        if feedback:
            feedback.onVehicleFeedbackReceived(FEEDBACK_EVENT_ID.WT_VEHICLE_DISCRETE_DAMAGE_RECEIVED, plasmaDamageDict['targetID'], (plasmaDamageDict['attackerID'], plasmaDamageDict['plasmaDamage']))
