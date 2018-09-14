# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/prb_control/entities/stronghold/unit/actions_validator.py
from UnitBase import ROSTER_TYPE
from gui.prb_control.entities.base.squad.actions_validator import UnitActionsValidator
from gui.prb_control.entities.base.unit.actions_validator import UnitVehiclesValidator
from gui.prb_control.items import ValidationResult
from gui.prb_control.settings import UNIT_RESTRICTION
from shared_utils import findFirst

class StrongholdVehiclesValidator(UnitVehiclesValidator):

    def _validate(self):
        return super(StrongholdVehiclesValidator, self)._validate()


class StrongholdActionsValidator(UnitActionsValidator):

    def _createVehiclesValidator(self, entity):
        return StrongholdVehiclesValidator(entity)
