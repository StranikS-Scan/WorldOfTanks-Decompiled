# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/battle_control/controllers/prebattle_comp7_skill_ctrl.py
import logging
import BigWorld
from Event import EventManager, Event
from constants import ARENA_PERIOD
from gui.battle_control.arena_info.interfaces import IPrebattleComp7SkillController
from gui.battle_control.battle_constants import BATTLE_CTRL_ID
from gui.shared.utils.MethodsRules import MethodsRules
from gui.veh_post_progression.battle_cooldown_manager import BattleCooldownManager
from helpers import dependency
from shared_utils import CONST_CONTAINER
from skeletons.gui.battle_session import IBattleSessionProvider
_logger = logging.getLogger(__name__)
_SWITCH_COMP7_SKILL_ACTION = 0

class _States(CONST_CONTAINER):
    IDLE = 0
    SELECTION_STARTED = 1
    SELECTION_STOPPED = 2
    SELECTION_ENDED = 3


class PrebattleComp7SkillController(MethodsRules, IPrebattleComp7SkillController):
    __sessionProvider = dependency.descriptor(IBattleSessionProvider)
    __slots__ = ('onVehicleSkillUpdated', 'onSwitchStopped', '__state', '__playerVehicleID', '__em', '__invData', '__extData', '__hasValidCaps', '__cooldown', '__arenaLoaded')

    def __init__(self):
        super(PrebattleComp7SkillController, self).__init__()
        self.__em = EventManager()
        self.__state = _States.IDLE
        self.__playerVehicleID = None
        self.__hasValidCaps = False
        self.__cooldown = BattleCooldownManager()
        self.__arenaLoaded = False
        self.onVehicleSkillUpdated = Event(self.__em)
        self.onSwitchStopped = Event(self.__em)
        return

    def getControllerID(self):
        return BATTLE_CTRL_ID.COMP7_PREBATTLE_SKILL_CTRL

    def getPrebattleVehicleID(self):
        return self.__playerVehicleID if self.isSelectionStarted() else 0

    def startControl(self, battleCtx, arenaVisitor):
        self.__hasValidCaps = arenaVisitor.bonus.hasComp7SkillSwitch()

    def stopControl(self):
        self.clear(reset=True)
        self.__state = _States.IDLE
        self.__playerVehicleID = None
        self.__hasValidCaps = False
        self.__arenaLoaded = False
        self.__cooldown.reset(_SWITCH_COMP7_SKILL_ACTION)
        self.__em.clear()
        return

    def canSwitch(self):
        return self.__hasValidCaps and self.isSelectionStarted()

    def isArenaLoaded(self):
        return self.__arenaLoaded

    def isSelectionStarted(self):
        return self.__state == _States.SELECTION_STARTED

    def isSelectionEnded(self):
        return self.__state in (_States.SELECTION_ENDED, _States.SELECTION_STOPPED)

    @MethodsRules.delayable()
    def setPlayerVehicle(self, vehicleID):
        if self.__state != _States.IDLE:
            return
        self.__playerVehicleID = vehicleID
        if self.__arenaLoaded:
            self.__state = _States.SELECTION_STARTED
            prbController = self.__sessionProvider.dynamic.comp7PrebattleSetup
            if prbController:
                prbController.onSelectionConfirmed += self.__onSelectionConfirmed

    def setPeriodInfo(self, period, endTime, length, additionalInfo):
        self.__updatePeriod(period)

    def stopSelection(self):
        prbController = self.__sessionProvider.dynamic.comp7PrebattleSetup
        if prbController:
            prbController.onSelectionConfirmed -= self.__onSelectionConfirmed
        if self.__state != _States.SELECTION_STOPPED:
            self.__state = _States.SELECTION_STOPPED
            self.__onFiniStepCompleted()
        self.onSwitchStopped()

    def arenaLoadCompleted(self):
        self.__arenaLoaded = True
        if self.__playerVehicleID:
            self.__state = _States.SELECTION_STARTED
            prbController = self.__sessionProvider.dynamic.comp7PrebattleSetup
            if prbController:
                prbController.onSelectionConfirmed += self.__onSelectionConfirmed

    def invalidatePeriodInfo(self, period, endTime, length, additionalInfo):
        if self.__state != _States.SELECTION_STOPPED:
            self.__updatePeriod(period)

    def switchComp7Skill(self, equipmentID):
        if self.__sessionProvider.isReplayPlaying:
            return
        elif not self.isSelectionStarted():
            return
        elif self.__cooldown.isInProcess(_SWITCH_COMP7_SKILL_ACTION):
            return
        else:
            playerVehicle = BigWorld.entities.get(self.__playerVehicleID)
            if playerVehicle is None:
                return
            elif playerVehicle.selectedComp7Skill == equipmentID:
                return
            self.__cooldown.process(_SWITCH_COMP7_SKILL_ACTION)
            playerVehicle.cell.switchComp7Skill(equipmentID)
            return

    def __onFiniStepCompleted(self):
        if self.__state == _States.SELECTION_ENDED:
            return
        if self.__arenaLoaded and self.__state == _States.SELECTION_STOPPED:
            self.__state = _States.SELECTION_ENDED

    def __updatePeriod(self, period):
        if period >= ARENA_PERIOD.BATTLE:
            self.stopSelection()

    def __onSelectionConfirmed(self):
        self.stopSelection()
