# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: halloween/scripts/client/halloween/gui/prb_control/entities/squad/ctx.py
from __future__ import absolute_import
from gui.prb_control.entities.base.squad.ctx import SquadSettingsCtx
from gui.prb_control.entities.base.unit.ctx import UnitRequestCtx
from gui.shared.utils.decorators import ReprInjector
from halloween.gui.halloween_gui_constants import FUNCTIONAL_FLAG
from halloween_common.halloween_constants import PREBATTLE_TYPE

@ReprInjector.withParent(('_queueType',))
class SetDifficultyLevelUnitCtx(UnitRequestCtx):
    __slots__ = ('_queueType',)

    def __init__(self, queueType, waitingID=''):
        super(SetDifficultyLevelUnitCtx, self).__init__(waitingID=waitingID)
        self._queueType = queueType

    def getQueueType(self):
        return self._queueType


@ReprInjector.withParent(('getArenaUniqueID', '_arenaUniqueID'))
class HalloweenSquadSettingsCtx(SquadSettingsCtx):
    __slots__ = ('_arenaUniqueID',)

    def __init__(self, entityType=PREBATTLE_TYPE.HALLOWEEN, waitingID='', flags=FUNCTIONAL_FLAG.HALLOWEEN, accountsToInvite=None, isForced=False, arenaUniqueID=None):
        super(HalloweenSquadSettingsCtx, self).__init__(entityType=entityType, waitingID=waitingID, flags=flags, accountsToInvite=accountsToInvite, isForced=isForced)
        self._arenaUniqueID = arenaUniqueID

    def getArenaUniqueID(self):
        return self._arenaUniqueID
