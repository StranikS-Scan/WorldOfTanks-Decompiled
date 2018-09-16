# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/prb_control/entities/epic/squad/entity.py
from constants import PREBATTLE_TYPE, QUEUE_TYPE
from gui.prb_control.events_dispatcher import g_eventDispatcher
from gui.prb_control.entities.base.squad.entity import SquadEntryPoint, SquadEntity
from gui.prb_control.items import SelectResult
from gui.prb_control.settings import PREBATTLE_ACTION_NAME, FUNCTIONAL_FLAG
from gui.prb_control.entities.base.squad.ctx import SquadSettingsCtx
from .actions_handler import EpicSquadActionsHandler
from .actions_validator import EpicSquadActionsValidator

class EpicSquadEntryPoint(SquadEntryPoint):

    def __init__(self, accountsToInvite=None):
        super(EpicSquadEntryPoint, self).__init__(FUNCTIONAL_FLAG.EPIC, accountsToInvite)

    def makeDefCtx(self):
        return SquadSettingsCtx(PREBATTLE_TYPE.EPIC, waitingID='prebattle/create', accountsToInvite=self._accountsToInvite)

    def _doCreate(self, unitMgr, ctx):
        unitMgr.createEpicSquad()


class EpicSquadEntity(SquadEntity):

    def __init__(self):
        super(EpicSquadEntity, self).__init__(FUNCTIONAL_FLAG.EPIC, PREBATTLE_TYPE.EPIC)

    def getQueueType(self):
        return QUEUE_TYPE.EPIC

    def doSelectAction(self, action):
        name = action.actionName
        if name == PREBATTLE_ACTION_NAME.SQUAD:
            g_eventDispatcher.showUnitWindow(self._prbType)
            if action.accountsToInvite:
                self._actionsHandler.processInvites(action.accountsToInvite)
            return SelectResult(True)
        return super(EpicSquadEntity, self).doSelectAction(action)

    def _createActionsHandler(self):
        return EpicSquadActionsHandler(self)

    def _createActionsValidator(self):
        return EpicSquadActionsValidator(self)
