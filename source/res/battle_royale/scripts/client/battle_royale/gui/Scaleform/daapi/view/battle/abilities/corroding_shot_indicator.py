# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: battle_royale/scripts/client/battle_royale/gui/Scaleform/daapi/view/battle/abilities/corroding_shot_indicator.py
from helpers import dependency
from gui.battle_control.controllers.period_ctrl import IAbstractPeriodView
from skeletons.gui.battle_session import IBattleSessionProvider
from constants import EQUIPMENT_STAGES
from gui.Scaleform.daapi.view.meta.CorrodingShotIndicatorMeta import CorrodingShotIndicatorMeta
from battle_royale.gui.constants import BattleRoyaleEquipments

class CorrodingShotIndicator(CorrodingShotIndicatorMeta, IAbstractPeriodView):
    __sessionProvider = dependency.descriptor(IBattleSessionProvider)

    def __init__(self):
        super(CorrodingShotIndicator, self).__init__()
        self.__isEnabled = False
        ctrl = self.__sessionProvider.shared.vehicleState
        if ctrl is not None:
            ctrl.onEquipmentComponentUpdated.subscribe(self.__onEquipmentComponentUpdated, BattleRoyaleEquipments.CORRODING_SHOT)
        ctrl = self.__sessionProvider.shared.crosshair
        if ctrl is not None:
            ctrl.onCrosshairPositionChanged += self.__onCrosshairPositionChanged
        return

    def _destroy(self):
        ctrl = self.__sessionProvider.shared.vehicleState
        if ctrl is not None:
            ctrl.onEquipmentComponentUpdated.unsubscribe(self.__onEquipmentComponentUpdated)
        ctrl = self.__sessionProvider.shared.crosshair
        if ctrl is not None:
            ctrl.onCrosshairPositionChanged -= self.__onCrosshairPositionChanged
        self.as_hideS()
        super(CorrodingShotIndicator, self)._destroy()
        return

    def __onEquipmentComponentUpdated(self, equipmentName, vehicleID, abilityInfo):
        if abilityInfo.stage == EQUIPMENT_STAGES.PREPARING:
            self.__isEnabled = True
            self.as_showS()
        else:
            self.__isEnabled = False
            self.as_hideS()

    def __onCrosshairPositionChanged(self, *args):
        crosshairCtrl = self.__sessionProvider.shared.crosshair
        scaledPosition = crosshairCtrl.getScaledPosition()
        self.as_updateLayoutS(*scaledPosition)
