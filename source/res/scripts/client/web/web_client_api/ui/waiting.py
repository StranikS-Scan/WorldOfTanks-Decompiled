# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/web/web_client_api/ui/waiting.py
from web.web_client_api import w2c, W2CSchema, Field

class _WaitingToggleControlSchema(W2CSchema):
    enabled = Field(required=True, type=bool)


class _WaitingToggleSchema(W2CSchema):
    show = Field(required=True, type=bool)


class WaitingWebApiMixin(object):

    @w2c(_WaitingToggleControlSchema, 'waiting_toggle_control')
    def waitingToggleControl(self, cmd, ctx):
        browserView = ctx['browser_view']
        browserView.browser.setAllowAutoLoadingScreen(not cmd.enabled)

    @w2c(_WaitingToggleSchema, 'waiting_toggle')
    def waitingToggle(self, cmd, ctx):
        browserView = ctx['browser_view']
        browserView.showLoading(cmd.show)
