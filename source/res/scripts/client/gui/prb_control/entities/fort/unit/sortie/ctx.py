# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/prb_control/entities/fort/unit/sortie/ctx.py
from gui.prb_control.settings import REQUEST_TYPE
from gui.shared.utils.decorators import ReprInjector
from constants import REQUEST_COOLDOWN, PREBATTLE_TYPE
from gui.prb_control import settings as prb_settings
from gui.prb_control.entities.base.ctx import PrbCtrlRequestCtx
from gui.prb_control.prb_getters import getUnitIdx

@ReprInjector.withParent(('__divisionLevel', 'divisionLevel'))
class CreateSortieCtx(PrbCtrlRequestCtx):
    __slots__ = ('__divisionLevel',)

    def __init__(self, divisionLevel=10, waitingID='', flags=prb_settings.FUNCTIONAL_FLAG.UNDEFINED):
        super(CreateSortieCtx, self).__init__(ctrlType=prb_settings.CTRL_ENTITY_TYPE.UNIT, entityType=PREBATTLE_TYPE.SORTIE, waitingID=waitingID, flags=flags, isForced=True)
        self.__divisionLevel = divisionLevel

    def getCooldown(self):
        return REQUEST_COOLDOWN.CALL_FORT_METHOD

    def getUnitIdx(self):
        return getUnitIdx()

    def getRequestType(self):
        return REQUEST_TYPE.CREATE

    def getDivisionLevel(self):
        return self.__divisionLevel
