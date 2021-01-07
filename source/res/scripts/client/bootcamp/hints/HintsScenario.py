# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/bootcamp/hints/HintsScenario.py
import time
from bootcamp.BootcampConstants import CONSUMABLE_ERROR_MESSAGES, HINT_TYPE
from HintsBase import HintBase, HINT_COMMAND
from helpers import dependency
from skeletons.gui.battle_session import IBattleSessionProvider
from gui.battle_control.battle_constants import VEHICLE_VIEW_STATE

class HintUselessConsumable(HintBase):
    sessionProvider = dependency.descriptor(IBattleSessionProvider)

    def __init__(self, avatar, params):
        super(HintUselessConsumable, self).__init__(avatar, HINT_TYPE.HINT_USELESS_CONSUMABLE, params['timeout'])
        self.__isUselessConsumable = False

    def start(self):
        ctrl = self.sessionProvider.shared.messages
        if ctrl is not None:
            ctrl.onShowVehicleErrorByKey += self.__onShowVehicleErrorByKey
        self._state = HintBase.STATE_DEFAULT
        return

    def stop(self):
        ctrl = self.sessionProvider.shared.messages
        if ctrl is not None:
            ctrl.onShowVehicleErrorByKey -= self.__onShowVehicleErrorByKey
        self._state = HintBase.STATE_INACTIVE
        return

    def update(self):
        command = None
        if self._state == HintBase.STATE_DEFAULT:
            if self.__isUselessConsumable:
                self._state = HintBase.STATE_HINT
                command = HINT_COMMAND.SHOW
                self._timeStart = time.time()
                self.__isUselessConsumable = False
        elif self._state == HintBase.STATE_HINT:
            if time.time() - self._timeStart > self._timeout:
                self._state = HintBase.STATE_DEFAULT
                command = HINT_COMMAND.HIDE
        return command

    def onAction(self, actionId, actionParams):
        pass

    def __onShowVehicleErrorByKey(self, key, args=None, extra=None):
        if key in CONSUMABLE_ERROR_MESSAGES and self._state == HintBase.STATE_DEFAULT:
            self.__isUselessConsumable = True


class HintExitGameArea(HintBase):

    def __init__(self, avatar, params):
        super(HintExitGameArea, self).__init__(avatar, HINT_TYPE.HINT_EXIT_GAME_AREA, params['timeout'])
        boundingBox = avatar.arena.arenaType.boundingBox
        self.__x_min = boundingBox[0][0]
        self.__x_max = boundingBox[1][0]
        self.__z_min = boundingBox[0][1]
        self.__z_max = boundingBox[1][1]
        self.__criteriaDistance = params.get('distance_to_border', 2.0)
        self.__timeHintAppeared = 0.0

    def start(self):
        self._state = HintBase.STATE_DEFAULT

    def stop(self):
        self._state = HintBase.STATE_INACTIVE

    def __isPlayerNearBorder(self):
        x_pos = self._avatar.position.x
        z_pos = self._avatar.position.z
        return abs(x_pos - self.__x_min) < self.__criteriaDistance or abs(x_pos - self.__x_max) < self.__criteriaDistance or abs(z_pos - self.__z_max) < self.__criteriaDistance or abs(z_pos - self.__z_min) < self.__criteriaDistance

    def update(self):
        if self._state == HintBase.STATE_DEFAULT:
            if self.__isPlayerNearBorder():
                self.__timeHintAppeared = time.time()
                self._state = HintBase.STATE_HINT
                return HINT_COMMAND.SHOW
        elif self._state == HintBase.STATE_HINT:
            if time.time() - self.__timeHintAppeared > self._timeout:
                if not self.__isPlayerNearBorder():
                    self._state = HintBase.STATE_DEFAULT
                    return HINT_COMMAND.HIDE
        return None


class HintLowHP(HintBase):
    sessionProvider = dependency.descriptor(IBattleSessionProvider)

    def __init__(self, avatar, params):
        super(HintLowHP, self).__init__(avatar, HINT_TYPE.HINT_LOW_HP, params['timeout'])
        self.__params = params
        self.__avatarHealth = None
        self.__lowHPFirstValue = None
        self.__lowHPSecondValue = None
        ctrl = self.sessionProvider.shared.vehicleState
        if ctrl is not None:
            ctrl.onVehicleStateUpdated += self.__onVehicleStateUpdated
            vehicle = ctrl.getControllingVehicle()
            if vehicle is not None:
                self.__setHealthValues(vehicle)
            else:
                ctrl.onVehicleControlling += self.__onVehicleControlling
        self.__isFirstWarningAppeared = False
        self.__isSecondWarningAppeared = False
        self.__timeShown = 0.0
        return

    def start(self):
        self._state = HintBase.STATE_DEFAULT

    def stop(self):
        self._state = HintBase.STATE_INACTIVE
        ctrl = self.sessionProvider.shared.vehicleState
        if ctrl is not None:
            ctrl.onVehicleStateUpdated -= self.__onVehicleStateUpdated
            ctrl.onVehicleControlling -= self.__onVehicleControlling
        return

    def update(self):
        if self.__avatarHealth is None:
            return
        else:
            command = None
            if self._state == HintBase.STATE_DEFAULT:
                showHint = False
                if not self.__isFirstWarningAppeared:
                    if self.__avatarHealth < self.__lowHPFirstValue:
                        self.__isFirstWarningAppeared = True
                        showHint = True
                elif self.__avatarHealth < self.__lowHPSecondValue:
                    self.__isSecondWarningAppeared = True
                    showHint = True
                if showHint:
                    self._state = HintBase.STATE_HINT
                    command = HINT_COMMAND.SHOW
                    self.__timeShown = time.time()
            elif self._state == HintBase.STATE_HINT:
                if time.time() - self.__timeShown > self._timeout:
                    if self.__isSecondWarningAppeared:
                        self._state = HintBase.STATE_INACTIVE
                    else:
                        self._state = HintBase.STATE_DEFAULT
                    return HINT_COMMAND.HIDE
            return command

    def __onVehicleStateUpdated(self, state, value):
        if state == VEHICLE_VIEW_STATE.HEALTH:
            self.__avatarHealth = value

    def __onVehicleControlling(self, vehicle):
        if vehicle.isPlayerVehicle:
            self.__setHealthValues(vehicle)

    def __setHealthValues(self, vehicle):
        self.__avatarHealth = vehicle.health
        self.__lowHPFirstValue = self.__params['first_percent'] * self.__avatarHealth
        self.__lowHPSecondValue = self.__params['second_percent'] * self.__avatarHealth
