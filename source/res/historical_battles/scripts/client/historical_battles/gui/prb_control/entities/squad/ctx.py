# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: historical_battles/scripts/client/historical_battles/gui/prb_control/entities/squad/ctx.py
from gui.prb_control.entities.base.unit.ctx import UnitRequestCtx, SetVehicleUnitCtx
from gui.shared.utils.decorators import ReprInjector

@ReprInjector.withParent(('_divisionID',))
class SetDivisionUnitCtx(SetVehicleUnitCtx):
    __slots__ = ('_divisionID',)

    def __init__(self, divisionID=0, vTypeCD=0, waitingID='', vehInvID=0):
        super(SetDivisionUnitCtx, self).__init__(vTypeCD=vTypeCD, vehInvID=vehInvID, waitingID=waitingID)
        self._divisionID = divisionID

    def getDivisionID(self):
        return self._divisionID


@ReprInjector.withParent(('_frontID',))
class SetFrontUnitCtx(UnitRequestCtx):
    __slots__ = ('_frontID',)

    def __init__(self, frontID=0, waitingID=''):
        super(SetFrontUnitCtx, self).__init__(waitingID=waitingID)
        self._frontID = frontID

    def getFrontID(self):
        return self._frontID
