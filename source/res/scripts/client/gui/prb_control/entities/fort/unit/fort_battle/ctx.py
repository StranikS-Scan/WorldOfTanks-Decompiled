# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/prb_control/entities/fort/unit/fort_battle/ctx.py
from gui.prb_control.settings import REQUEST_TYPE
from gui.shared.utils.decorators import ReprInjector
from constants import REQUEST_COOLDOWN, PREBATTLE_TYPE
from gui.prb_control import settings as prb_settings
from gui.prb_control.entities.base.ctx import PrbCtrlRequestCtx
from gui.prb_control.prb_getters import getUnitIdx

@ReprInjector.withParent(('__battleID', 'battleID'), ('__slotIdx', 'slotIdx'))
class CreateOrJoinFortBattleCtx(PrbCtrlRequestCtx):
    __slots__ = ('__battleID', '__slotIdx', '__isUpdateExpected')

    def __init__(self, battleID, slotIdx=-1, waitingID='', isUpdateExpected=False, flags=prb_settings.FUNCTIONAL_FLAG.UNDEFINED):
        super(CreateOrJoinFortBattleCtx, self).__init__(ctrlType=prb_settings.CTRL_ENTITY_TYPE.UNIT, entityType=PREBATTLE_TYPE.FORT_BATTLE, waitingID=waitingID, flags=flags, isForced=True)
        self.__battleID = battleID
        self.__slotIdx = slotIdx
        self.__isUpdateExpected = isUpdateExpected

    def isUpdateExpected(self):
        return self.__isUpdateExpected

    def getCooldown(self):
        return REQUEST_COOLDOWN.CALL_FORT_METHOD

    def getUnitIdx(self):
        return getUnitIdx()

    def getRequestType(self):
        return REQUEST_TYPE.JOIN

    def getID(self):
        return self.__battleID

    def getSlotIdx(self):
        return self.__slotIdx

    def _setUpdateExpected(self, value):
        self.__isUpdateExpected = value
