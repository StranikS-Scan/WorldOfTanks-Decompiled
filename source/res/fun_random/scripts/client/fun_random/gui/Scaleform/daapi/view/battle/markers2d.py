# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: fun_random/scripts/client/fun_random/gui/Scaleform/daapi/view/battle/markers2d.py
import logging
from gui.Scaleform.daapi.view.battle.shared.markers2d import MarkersManager
from gui.Scaleform.daapi.view.battle.shared.markers2d.plugin_items.step_repair_point import StepRepairPointPlugin
from gui.battle_control.battle_constants import PROGRESS_CIRCLE_TYPE
_logger = logging.getLogger(__name__)

class FunRandomMarkersManager(MarkersManager):

    def _setupPlugins(self, arenaVisitor):
        setup = super(FunRandomMarkersManager, self)._setupPlugins(arenaVisitor)
        if arenaVisitor.hasStepRepairPoints():
            setup['step_repairs'] = FunRandomStepRepairPointPlugin
        return setup


class FunRandomStepRepairPointPlugin(StepRepairPointPlugin):

    def start(self):
        progressCtrl = self.sessionProvider.dynamic.progressTimer
        stepRepairPointComponent = getattr(self.sessionProvider.arenaVisitor.getComponentSystem(), 'stepRepairPointComponent', None)
        if stepRepairPointComponent is not None:
            repairPts = stepRepairPointComponent.stepRepairPoints
            for pt in repairPts:
                self._onStepRepairPointAdded(pt)
                inCircle, state = progressCtrl.getPlayerCircleState(PROGRESS_CIRCLE_TYPE.RESUPPLY_CIRCLE, pt.id)
                if inCircle:
                    self._onVehicleEntered(PROGRESS_CIRCLE_TYPE.RESUPPLY_CIRCLE, pt.id, state)

        else:
            _logger.error('Expected StepRepairPointComponent not present!')
        return
