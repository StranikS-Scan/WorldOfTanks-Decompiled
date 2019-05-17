# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/web_client_api/ui/squad.py
from gui.prb_control import prbDispatcherProperty
from gui.prb_control.entities.base.ctx import PrbAction
from gui.prb_control.settings import PREBATTLE_ACTION_NAME
from web_client_api import w2c, W2CSchema, Field

class _CreateSquadSchema(W2CSchema):
    spa_id = Field(required=True, type=(int, long, basestring))


class SquadWebApiMixin(object):

    @prbDispatcherProperty
    def prbDispatcher(self):
        return None

    @w2c(_CreateSquadSchema, 'squad_window')
    def createSquad(self, usersIds):
        yield self.prbDispatcher.doSelectAction(PrbAction(PREBATTLE_ACTION_NAME.SQUAD, accountsToInvite=(usersIds.spa_id,)))
