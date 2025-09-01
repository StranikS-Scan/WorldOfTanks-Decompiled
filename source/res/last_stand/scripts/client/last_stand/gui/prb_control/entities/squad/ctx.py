# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: last_stand/scripts/client/last_stand/gui/prb_control/entities/squad/ctx.py
from gui.prb_control.entities.base.squad.ctx import SquadSettingsCtx
from gui.prb_control.entities.base.unit.ctx import UnitRequestCtx
from gui.shared.utils.decorators import ReprInjector
from last_stand.gui.ls_gui_constants import FUNCTIONAL_FLAG
from last_stand_common.last_stand_constants import PREBATTLE_TYPE

@ReprInjector.withParent(('_queueType',))
class SetDifficultyLevelUnitCtx(UnitRequestCtx):
    __slots__ = ('_queueType',)

    def __init__(self, queueType, waitingID=''):
        super(SetDifficultyLevelUnitCtx, self).__init__(waitingID=waitingID)
        self._queueType = queueType

    def getQueueType(self):
        return self._queueType


@ReprInjector.withParent(('getArenaUniqueID', '_arenaUniqueID'))
class LastStandSquadSettingsCtx(SquadSettingsCtx):
    __slots__ = ('_arenaUniqueID',)

    def __init__(self, entityType=PREBATTLE_TYPE.LAST_STAND, waitingID='', flags=FUNCTIONAL_FLAG.LAST_STAND, accountsToInvite=None, isForced=False, arenaUniqueID=None):
        super(LastStandSquadSettingsCtx, self).__init__(entityType=entityType, waitingID=waitingID, flags=flags, accountsToInvite=accountsToInvite, isForced=isForced)
        self._arenaUniqueID = arenaUniqueID

    def getArenaUniqueID(self):
        return self._arenaUniqueID
