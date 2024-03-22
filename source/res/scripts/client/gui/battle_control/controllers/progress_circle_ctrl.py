# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/battle_control/controllers/progress_circle_ctrl.py
from functools import partial
import BigWorld
import Event
from constants import REPAIR_POINT_ACTION, SECTOR_BASE_ACTION
from debug_utils import LOG_WARNING, LOG_ERROR
from gui.Scaleform.genConsts.EPIC_CONSTS import EPIC_CONSTS
from gui.battle_control.battle_constants import BATTLE_CTRL_ID, PROGRESS_CIRCLE_TYPE, VEHICLE_VIEW_STATE
from gui.battle_control.controllers.interfaces import IBattleController
REPAIR_COMPLETE_BLOCKED_DELAY = 2

class ProgressTimerPlugin(object):

    def __init__(self, controller, sessionProvider):
        self._controller = controller
        self._type = -1
        self._callback = None
        self._cooldown = {}
        self._isInPostmortem = False
        self._inCircleIdx = -1
        self._sessionProvider = sessionProvider
        return

    def start(self):
        ctrl = self._sessionProvider.shared.vehicleState
        if ctrl is not None:
            ctrl.onVehicleStateUpdated += self._onVehicleStateUpdated
            ctrl.onPostMortemSwitched += self._onPostMortemSwitched
            if ctrl.isInPostmortem:
                self._onPostMortemSwitched(noRespawnPossible=False, respawnAvailable=False)
        ctrl = self._sessionProvider.dynamic.respawn
        if ctrl is not None:
            ctrl.onRespawnVisibilityChanged += self._onRespawnVisibility
            self._onRespawnVisibility(ctrl.isRespawnVisible())
        return

    def fini(self):
        ctrl = self._sessionProvider.shared.vehicleState
        if ctrl is not None:
            ctrl.onVehicleStateUpdated -= self._onVehicleStateUpdated
            ctrl.onPostMortemSwitched -= self._onPostMortemSwitched
        ctrl = self._sessionProvider.dynamic.respawn
        if ctrl is not None:
            ctrl.onRespawnVisibilityChanged -= self._onRespawnVisibility
        return

    def getPlayerState(self, idx):
        return (self._inCircleIdx == idx, None)

    def _getTime(self, nextTime):
        return max(0, round(nextTime - BigWorld.serverTime()))

    def _cooldownCallback(self):
        delCallbacks = []
        for idx in self._cooldown:
            if self._getTime(self._cooldown[idx]) > 0:
                self._controller.onTimerUpdated(self._type, idx, self._getTime(self._cooldown[idx]))
            delCallbacks.append(idx)

        for i in range(0, len(delCallbacks)):
            del self._cooldown[delCallbacks[i]]

        if self._cooldown.keys():
            self._callback = BigWorld.callback(1, self._cooldownCallback)
        else:
            self._callback = None
        return

    def _startCooldownCallback(self, idx, time):
        self._cooldown[idx] = time
        if self._callback is None:
            self._callback = BigWorld.callback(1, self._cooldownCallback)
        return

    def _onPostMortemSwitched(self, noRespawnPossible, respawnAvailable):
        self._isInPostmortem = True

    def _onRespawnVisibility(self, isVisible, fromTab=False):
        if isVisible and self._isInPostmortem:
            self._isInPostmortem = False
            self._stopTimerCallback()
            self._hideAll()

    def _onVehicleStateUpdated(self, state, value):
        if state == VEHICLE_VIEW_STATE.SWITCHING:
            if self._isInPostmortem:
                self._stopTimerCallback()
            self._hideAll()

    def _stopTimerCallback(self):
        self._cooldown = {}

    def _hideAll(self):
        pass


class StepRepairPlugin(ProgressTimerPlugin):

    def __init__(self, controller, sessionProvider):
        super(StepRepairPlugin, self).__init__(controller, sessionProvider)
        self._type = PROGRESS_CIRCLE_TYPE.RESUPPLY_CIRCLE
        self.__repairPointStates = {}
        self.__delayedCooldownCB = None
        self.__isInFreecam = False
        return

    def start(self):
        super(StepRepairPlugin, self).start()
        componentSystem = self._sessionProvider.arenaVisitor.getComponentSystem()
        stepRepairPointComponent = getattr(componentSystem, 'stepRepairPointComponent', None)
        if stepRepairPointComponent is not None:
            stepRepairPointComponent.onStepRepairPointPlayerAction += self._action
            actions = stepRepairPointComponent.repairPointPlayerActions
            for idx in actions.keys():
                action, time, hphealed = actions[idx]
                if action == REPAIR_POINT_ACTION.COOLDOWN_AFTER_COMPLETE:
                    self._action(idx, REPAIR_POINT_ACTION.COOLDOWN, time, hphealed)
                if action != REPAIR_POINT_ACTION.CANCEL_REPAIR and action != REPAIR_POINT_ACTION.LEAVE_WHILE_CD:
                    self._action(idx, action, time, hphealed)

        else:
            LOG_ERROR('Expected StepRepairPointComponent not present!')
        specCtrl = self._sessionProvider.shared.spectator
        if specCtrl is not None:
            specCtrl.onSpectatorViewModeChanged += self.__onSpectatorModeChanged
        return

    def fini(self):
        super(StepRepairPlugin, self).fini()
        componentSystem = self._sessionProvider.arenaVisitor.getComponentSystem()
        stepRepairPointComponent = getattr(componentSystem, 'stepRepairPointComponent', None)
        if stepRepairPointComponent is not None:
            stepRepairPointComponent.onStepRepairPointPlayerAction -= self._action
        specCtrl = self._sessionProvider.shared.spectator
        if specCtrl is not None:
            specCtrl.onSpectatorViewModeChanged -= self.__onSpectatorModeChanged
        return

    def getPlayerState(self, idx):
        return (self._inCircleIdx == idx, self.__repairPointStates.get(idx, None))

    def _onRespawnVisibility(self, isVisible, fromTab=False):
        super(StepRepairPlugin, self)._onRespawnVisibility(isVisible, fromTab)
        if isVisible:
            self.__isInFreecam = False

    def _action(self, repairPointIndex, action, nextActionTime, percentageHealed):
        if self.__isInFreecam and action not in {REPAIR_POINT_ACTION.START_REPAIR, REPAIR_POINT_ACTION.BECOME_READY}:
            return
        else:
            currentState = EPIC_CONSTS.RESUPPLY_READY
            if repairPointIndex not in self.__repairPointStates:
                self.__repairPointStates[repairPointIndex] = currentState
            if action == REPAIR_POINT_ACTION.START_REPAIR:
                if self._inCircleIdx < 0:
                    self._controller.onVehicleEntered(self._type, repairPointIndex, EPIC_CONSTS.RESUPPLY_READY)
                    self._inCircleIdx = repairPointIndex
                else:
                    self._controller.onCircleStatusChanged(self._type, repairPointIndex, EPIC_CONSTS.RESUPPLY_READY)
                self.__repairPointStates[repairPointIndex] = EPIC_CONSTS.RESUPPLY_READY
            elif action == REPAIR_POINT_ACTION.CANCEL_REPAIR:
                self._controller.onVehicleLeft(self._type, repairPointIndex)
                self._inCircleIdx = -1
                if self.__delayedCooldownCB is not None:
                    BigWorld.cancelCallback(self.__delayedCooldownCB)
                    self.__delayedCooldownCB = None
            elif action == REPAIR_POINT_ACTION.COMPLETE_REPAIR:
                self._controller.onCircleStatusChanged(self._type, repairPointIndex, EPIC_CONSTS.RESUPPLY_FULL)
                self.__repairPointStates[repairPointIndex] = EPIC_CONSTS.RESUPPLY_FULL
            elif action == REPAIR_POINT_ACTION.COOLDOWN:
                if self._inCircleIdx < 0:
                    self._controller.onVehicleEntered(self._type, repairPointIndex, EPIC_CONSTS.RESUPPLY_BLOCKED)
                    self._inCircleIdx = repairPointIndex
                else:
                    self._controller.onCircleStatusChanged(self._type, repairPointIndex, EPIC_CONSTS.RESUPPLY_BLOCKED)
                self.__repairPointStates[repairPointIndex] = EPIC_CONSTS.RESUPPLY_BLOCKED
                self._controller.onTimerUpdated(self._type, repairPointIndex, self._getTime(nextActionTime))
                self._startCooldownCallback(repairPointIndex, nextActionTime)
            elif action == REPAIR_POINT_ACTION.COOLDOWN_AFTER_COMPLETE:
                self._controller.onCircleStatusChanged(self._type, repairPointIndex, EPIC_CONSTS.RESUPPLY_BLOCKED)
                if not self._isInPostmortem:
                    self.__delayedCooldownCB = BigWorld.callback(REPAIR_COMPLETE_BLOCKED_DELAY, partial(self.__delayedCooldown, repairPointIndex, nextActionTime))
                else:
                    self.__delayedCooldown(repairPointIndex, nextActionTime)
            elif action == REPAIR_POINT_ACTION.ENTER_WHILE_CD:
                if self._inCircleIdx < 0:
                    self._controller.onVehicleEntered(self._type, repairPointIndex, EPIC_CONSTS.RESUPPLY_BLOCKED)
                    self._inCircleIdx = repairPointIndex
                else:
                    self._controller.onCircleStatusChanged(self._type, repairPointIndex, EPIC_CONSTS.RESUPPLY_BLOCKED)
                self.__repairPointStates[repairPointIndex] = EPIC_CONSTS.RESUPPLY_BLOCKED
                self._controller.onTimerUpdated(self._type, repairPointIndex, self._getTime(nextActionTime))
                self._startCooldownCallback(repairPointIndex, nextActionTime)
            elif action == REPAIR_POINT_ACTION.LEAVE_WHILE_CD:
                self._controller.onVehicleLeft(self._type, repairPointIndex)
                self._inCircleIdx = -1
                self._controller.onCircleStatusChanged(self._type, repairPointIndex, EPIC_CONSTS.RESUPPLY_BLOCKED)
                self.__repairPointStates[repairPointIndex] = EPIC_CONSTS.RESUPPLY_BLOCKED
                self._controller.onTimerUpdated(self._type, repairPointIndex, self._getTime(nextActionTime))
                self._startCooldownCallback(repairPointIndex, nextActionTime)
                if self.__delayedCooldownCB is not None:
                    BigWorld.cancelCallback(self.__delayedCooldownCB)
                    self.__delayedCooldownCB = None
            elif action == REPAIR_POINT_ACTION.BECOME_READY:
                self._controller.onCircleStatusChanged(self._type, repairPointIndex, EPIC_CONSTS.RESUPPLY_READY)
                self.__repairPointStates[repairPointIndex] = EPIC_CONSTS.RESUPPLY_READY
            elif action == REPAIR_POINT_ACTION.REPAIR_STEP:
                if self._inCircleIdx < 0:
                    self._controller.onVehicleEntered(self._type, repairPointIndex, EPIC_CONSTS.RESUPPLY_READY)
                    self._inCircleIdx = repairPointIndex
                elif self.__repairPointStates[repairPointIndex] != EPIC_CONSTS.RESUPPLY_READY:
                    self._controller.onCircleStatusChanged(self._type, repairPointIndex, EPIC_CONSTS.RESUPPLY_READY)
                self.__repairPointStates[repairPointIndex] = EPIC_CONSTS.RESUPPLY_READY
                self._controller.onProgressUpdate(self._type, repairPointIndex, percentageHealed)
            elif action == REPAIR_POINT_ACTION.ENTER_WHILE_FULL:
                if self._inCircleIdx < 0:
                    self._controller.onVehicleEntered(self._type, repairPointIndex, EPIC_CONSTS.RESUPPLY_FULL)
                    self.__repairPointStates[repairPointIndex] = EPIC_CONSTS.RESUPPLY_FULL
                    self._inCircleIdx = repairPointIndex
                else:
                    self._controller.onCircleStatusChanged(self._type, repairPointIndex, EPIC_CONSTS.RESUPPLY_FULL)
            else:
                LOG_WARNING("STATE: '%d' is not implemented ", action)
            self._sessionProvider.invalidateVehicleState(VEHICLE_VIEW_STATE.PROGRESS_CIRCLE, (self._type, self._inCircleIdx >= 0))
            return

    def _hideAll(self):
        super(StepRepairPlugin, self)._hideAll()
        if self._inCircleIdx != -1:
            self._controller.onVehicleLeft(self._type, self._inCircleIdx)
        if self.__delayedCooldownCB is not None:
            BigWorld.cancelCallback(self.__delayedCooldownCB)
            self.__delayedCooldownCB = None
        self._inCircleIdx = -1
        return

    def _stopTimerCallback(self):
        for idx in self._cooldown:
            self._controller.onCircleStatusChanged(self._type, idx, EPIC_CONSTS.RESUPPLY_READY)

        super(StepRepairPlugin, self)._stopTimerCallback()

    def __onSpectatorModeChanged(self, mode):
        if mode == EPIC_CONSTS.SPECTATOR_MODE_FREECAM:
            self.__isInFreecam = True
            self._hideAll()
        else:
            self.__isInFreecam = False

    def __delayedCooldown(self, repairPointIndex, nextActionTime):
        if self._inCircleIdx >= 0:
            self._controller.onVehicleEntered(self._type, repairPointIndex, EPIC_CONSTS.RESUPPLY_BLOCKED)
            self._inCircleIdx = repairPointIndex
        else:
            self._controller.onCircleStatusChanged(self._type, repairPointIndex, EPIC_CONSTS.RESUPPLY_BLOCKED)
        self.__repairPointStates[repairPointIndex] = EPIC_CONSTS.RESUPPLY_BLOCKED
        self._controller.onTimerUpdated(self._type, repairPointIndex, self._getTime(nextActionTime))
        self._startCooldownCallback(repairPointIndex, nextActionTime)
        self.__delayedCooldownCB = None
        return


class SectorBasePlugin(ProgressTimerPlugin):

    def __init__(self, controller, sessionProvider):
        super(SectorBasePlugin, self).__init__(controller, sessionProvider)
        self._type = PROGRESS_CIRCLE_TYPE.SECTOR_BASE_CIRCLE
        self.__blockedCB = None
        return

    def start(self):
        super(SectorBasePlugin, self).start()
        componentSystem = self._sessionProvider.arenaVisitor.getComponentSystem()
        sectorBaseComp = getattr(componentSystem, 'sectorBaseComponent', None)
        if sectorBaseComp is not None:
            sectorBaseComp.onSectorBasePlayerAction += self._action
            actions = sectorBaseComp.stepSectorBasePlayerAction
            for idx, action, time in actions.iteritems():
                if action != SECTOR_BASE_ACTION.LEAVE and action != SECTOR_BASE_ACTION.LEAVE_WHILE_CD and action != SECTOR_BASE_ACTION.CAPTURED:
                    self._action(idx, action, time)

        else:
            LOG_ERROR('Expected SectorBaseComponent not present!')
        return

    def fini(self):
        super(SectorBasePlugin, self).fini()
        componentSystem = self._sessionProvider.arenaVisitor.getComponentSystem()
        sectorBaseComp = getattr(componentSystem, 'sectorBaseComponent', None)
        if sectorBaseComp is not None:
            sectorBaseComp.onSectorBasePlayerAction -= self._action
        if self.__blockedCB is not None:
            BigWorld.cancelCallback(self.__blockedCB)
            self.__blockedCB = None
        return

    def _action(self, basePointIndex, action, nextActionTime):
        if action in (SECTOR_BASE_ACTION.ENTER, SECTOR_BASE_ACTION.ENTER_WHILE_CD):
            self._controller.onVehicleEntered(self._type, basePointIndex, None)
            self._inCircleIdx = basePointIndex
        elif action in (SECTOR_BASE_ACTION.LEAVE, SECTOR_BASE_ACTION.LEAVE_WHILE_CD):
            self._controller.onVehicleLeft(self._type, basePointIndex)
            self._inCircleIdx = -1
        elif action == SECTOR_BASE_ACTION.COOLDOWN:
            duration = self._getTime(nextActionTime)
            self._sessionProvider.invalidateVehicleState(VEHICLE_VIEW_STATE.CAPTURE_BLOCKED, duration)
            if self.__blockedCB is not None:
                BigWorld.cancelCallback(self.__blockedCB)
                self.__blockedCB = None
            self.__blockedCB = BigWorld.callback(duration, self.__stopBlockState)
        else:
            if action == SECTOR_BASE_ACTION.CAPTURED:
                return
            LOG_WARNING('SectorBasePlugin: NO SUCH ACTION ', action)
        return

    def _hideAll(self):
        super(SectorBasePlugin, self)._hideAll()
        if self._inCircleIdx != -1:
            self._controller.onVehicleLeft(self._type, self._inCircleIdx)
        self._inCircleIdx = -1

    def __stopBlockState(self):
        self._sessionProvider.invalidateVehicleState(VEHICLE_VIEW_STATE.CAPTURE_BLOCKED, 0)
        self.__blockedCB = None
        return


class ProgressTimerController(IBattleController):

    def __init__(self, setup):
        super(ProgressTimerController, self).__init__()
        self.__sessionProvider = setup.sessionProvider
        self.__plugins = {}
        self.__eManager = Event.EventManager()
        self.onTimerUpdated = Event.Event(self.__eManager)
        self.onVehicleEntered = Event.Event(self.__eManager)
        self.onVehicleLeft = Event.Event(self.__eManager)
        self.onCircleStatusChanged = Event.Event(self.__eManager)
        self.onProgressUpdate = Event.Event(self.__eManager)

    def getControllerID(self):
        return BATTLE_CTRL_ID.PROGRESS_TIMER

    def startControl(self):
        visitor = self.__sessionProvider.arenaVisitor
        if visitor.hasStepRepairPoints():
            self.__plugins[PROGRESS_CIRCLE_TYPE.RESUPPLY_CIRCLE] = StepRepairPlugin(self, self.__sessionProvider)
        if visitor.hasSectors():
            self.__plugins[PROGRESS_CIRCLE_TYPE.SECTOR_BASE_CIRCLE] = SectorBasePlugin(self, self.__sessionProvider)
        for p in self.__plugins:
            self.__plugins[p].start()

    def stopControl(self):
        self.__eManager.clear()
        self.__eManager = None
        for p in self.__plugins:
            self.__plugins[p].fini()

        self.__plugins = {}
        return

    def getPlayerCircleState(self, type_, idx):
        return self.__plugins[type_].getPlayerState(idx) if type_ in self.__plugins else None
