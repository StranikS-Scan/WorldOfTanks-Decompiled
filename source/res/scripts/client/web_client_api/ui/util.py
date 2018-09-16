# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/web_client_api/ui/util.py
from gui.shared.utils import showInvitationInWindowsBar
from gui.shared.event_dispatcher import runSalesChain
from web_client_api import w2c, W2CSchema, Field

class _RunTriggerChainSchema(W2CSchema):
    trigger_chain_id = Field(required=True, type=basestring)


class UtilWebApiMixin(object):

    @w2c(W2CSchema, 'blink_taskbar')
    def blinkTaskbar(self, cmd):
        showInvitationInWindowsBar()

    @w2c(_RunTriggerChainSchema, 'run_trigger_chain')
    def runTriggerChain(self, cmd):
        chainID = cmd.trigger_chain_id
        runSalesChain(chainID)
