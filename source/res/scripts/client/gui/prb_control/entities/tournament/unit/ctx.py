# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/prb_control/entities/tournament/unit/ctx.py
from gui.prb_control import settings
from gui.prb_control.entities.base.unit.ctx import UnitRequestCtx
from gui.shared.utils.decorators import ReprInjector
_REQUEST_TYPE = settings.REQUEST_TYPE
_UNDEFINED = settings.FUNCTIONAL_FLAG.UNDEFINED

class TimeoutCtx(UnitRequestCtx):
    __slots__ = ('__onTimeoutCallback',)

    def __init__(self, prbType, flags=_UNDEFINED, waitingID='', onTimeoutCallback=None):
        super(TimeoutCtx, self).__init__(entityType=prbType, waitingID=waitingID, flags=flags)
        self.__onTimeoutCallback = onTimeoutCallback

    def callTimeoutCallback(self):
        onTimeoutCallback = self.__onTimeoutCallback
        if onTimeoutCallback and callable(onTimeoutCallback):
            onTimeoutCallback()


@ReprInjector.withParent(('__rosterID', 'rosterID'))
class CreateUnitCtx(TimeoutCtx):
    __slots__ = ('__rosterID',)

    def __init__(self, prbType, flags=_UNDEFINED, waitingID='', rosterID=0, onTimeoutCallback=None):
        super(CreateUnitCtx, self).__init__(prbType=prbType, waitingID=waitingID, flags=flags, onTimeoutCallback=onTimeoutCallback)
        self.__rosterID = rosterID

    def getRequestType(self):
        return _REQUEST_TYPE.CREATE

    def getRosterID(self):
        return self.__rosterID
