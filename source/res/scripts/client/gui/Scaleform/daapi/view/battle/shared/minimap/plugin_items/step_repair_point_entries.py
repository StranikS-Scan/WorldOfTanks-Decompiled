# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/battle/shared/minimap/plugin_items/step_repair_point_entries.py
import logging
from gui.battle_control.battle_constants import PROGRESS_CIRCLE_TYPE
from gui.Scaleform.genConsts.BATTLE_MINIMAP_CONSTS import BATTLE_MINIMAP_CONSTS
from gui.Scaleform.daapi.view.battle.shared.minimap.common import SimplePlugin
from gui.Scaleform.daapi.view.battle.shared.minimap import settings
import Math
_logger = logging.getLogger(__name__)

class StepRepairPointEntriesPlugin(SimplePlugin):
    __slots__ = ('__ptDict',)

    def __init__(self, parentObj):
        super(StepRepairPointEntriesPlugin, self).__init__(parentObj)
        self.__ptDict = {}

    def start(self):
        super(StepRepairPointEntriesPlugin, self).start()
        stepRepairPointComponent = getattr(self.sessionProvider.arenaVisitor.getComponentSystem(), 'stepRepairPointComponent', None)
        if stepRepairPointComponent is not None:
            stepRepairPointComponent.onStepRepairPointAdded += self.__onStepRepairPointAdded
            stepRepairPointComponent.onStepRepairPointActiveStateChanged += self.__onStepRepairPointActiveStateChanged
            repairPts = stepRepairPointComponent.stepRepairPoints
            for pt in repairPts:
                self.__onStepRepairPointAdded(pt)

        else:
            _logger.error('Expected StepRepairPointComponent not present!')
        ctrl = self.sessionProvider.dynamic.progressTimer
        ctrl.onCircleStatusChanged += self.__onCircleStatusChanged
        return

    def fini(self):
        super(StepRepairPointEntriesPlugin, self).fini()
        stepRepairPointComponent = getattr(self.sessionProvider.arenaVisitor.getComponentSystem(), 'stepRepairPointComponent', None)
        if stepRepairPointComponent is not None:
            stepRepairPointComponent.onStepRepairPointAdded -= self.__onStepRepairPointAdded
            stepRepairPointComponent.onStepRepairPointActiveStateChanged -= self.__onStepRepairPointActiveStateChanged
        ctrl = self.sessionProvider.dynamic.progressTimer
        if ctrl is not None:
            ctrl.onCircleStatusChanged -= self.__onCircleStatusChanged
        return

    def __onCircleStatusChanged(self, type_, pointId, state):
        if type_ is not PROGRESS_CIRCLE_TYPE.RESUPPLY_CIRCLE:
            return
        entryID = self.__ptDict[pointId]
        self._parentObj.invoke(entryID, BATTLE_MINIMAP_CONSTS.SET_STATE, state)

    def __onStepRepairPointAdded(self, stepRepairPoint):
        symbol = settings.ENTRY_SYMBOL_NAME.EPIC_REPAIR
        entryID = self.__ptDict[stepRepairPoint.id] = self.__addRPEntry(symbol, stepRepairPoint.position)
        self._parentObj.invoke(entryID, 'setActive', stepRepairPoint.isActiveForPlayerTeam())

    def __onStepRepairPointActiveStateChanged(self, pointId, isActive):
        entryID = self.__ptDict[pointId]
        if entryID is not None:
            self._parentObj.invoke(entryID, 'setActive', isActive)
        return

    def __addRPEntry(self, symbol, position):
        matrix = Math.Matrix()
        matrix.setTranslate(position)
        entryID = self._addEntry(symbol, settings.CONTAINER_NAME.ICONS, matrix=matrix, active=True)
        return entryID
