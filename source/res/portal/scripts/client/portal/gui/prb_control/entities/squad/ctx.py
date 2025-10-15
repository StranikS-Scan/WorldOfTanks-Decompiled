# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: portal/scripts/client/portal/gui/prb_control/entities/squad/ctx.py
from gui.prb_control.entities.base.unit.ctx import UnitRequestCtx
from gui.shared.utils.decorators import ReprInjector
from portal.gui.portal_gui_constants import REQUEST_TYPE

@ReprInjector.withParent(('_battleLevel',))
class SetUnitBattleLevelCtx(UnitRequestCtx):
    __slots__ = ('_battleLevel',)

    def __init__(self, battleLevel, waitingID=''):
        super(SetUnitBattleLevelCtx, self).__init__(waitinID=waitingID)
        self._battleLevel = battleLevel

    def getBattleLevel(self):
        return self._battleLevel

    def getRequestType(self):
        return REQUEST_TYPE.PORTAL_SET_BATTLE_LEVEL

    def getCooldown(self):
        pass
