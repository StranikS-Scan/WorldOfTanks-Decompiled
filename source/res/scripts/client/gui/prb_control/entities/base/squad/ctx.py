# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/prb_control/entities/base/squad/ctx.py
from constants import PREBATTLE_TYPE
from gui.prb_control import settings as prb_settings
from gui.prb_control.entities.base.unit.ctx import UnitRequestCtx
from gui.shared.utils.decorators import ReprInjector

@ReprInjector.withParent(('getWaitingID', 'waitingID'), ('getFlagsToStrings', 'flags'))
class SquadSettingsCtx(UnitRequestCtx):
    __slots__ = ('__accountsToInvite',)

    def __init__(self, entityType=PREBATTLE_TYPE.SQUAD, waitingID='', flags=prb_settings.FUNCTIONAL_FLAG.UNDEFINED, accountsToInvite=None, isForced=False):
        super(SquadSettingsCtx, self).__init__(entityType=entityType, waitingID=waitingID, flags=flags, isForced=isForced)
        self.__accountsToInvite = accountsToInvite or []

    def getRequestType(self):
        return prb_settings.REQUEST_TYPE.CREATE

    def getID(self):
        pass

    def getAccountsToInvite(self):
        return self.__accountsToInvite
