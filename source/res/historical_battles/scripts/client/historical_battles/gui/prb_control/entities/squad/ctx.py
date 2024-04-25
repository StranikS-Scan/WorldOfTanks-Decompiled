# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: historical_battles/scripts/client/historical_battles/gui/prb_control/entities/squad/ctx.py
from gui.prb_control.entities.base.unit.ctx import SetVehicleUnitCtx, UnitRequestCtx
from gui.shared.utils.decorators import ReprInjector

@ReprInjector.withParent(('_frontmanID',))
class SetFrontmanUnitCtx(SetVehicleUnitCtx):
    __slots__ = ('_frontmanID',)

    def __init__(self, frontmanID=0, vTypeCD=0, waitingID='', vehInvID=0):
        super(SetFrontmanUnitCtx, self).__init__(vTypeCD=vTypeCD, vehInvID=vehInvID, waitingID=waitingID)
        self._frontmanID = frontmanID

    def getFrontmanID(self):
        return self._frontmanID


@ReprInjector.withParent(('_frontID',))
class SetFrontUnitCtx(UnitRequestCtx):
    __slots__ = ('_frontID',)

    def __init__(self, frontID=0, waitingID=''):
        super(SetFrontUnitCtx, self).__init__(waitingID=waitingID)
        self._frontID = frontID

    def getFrontID(self):
        return self._frontID
