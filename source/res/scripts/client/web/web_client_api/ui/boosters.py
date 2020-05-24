# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/web/web_client_api/ui/boosters.py
from web.web_client_api import w2c, W2CSchema, Field
from gui.shared import event_dispatcher as shared_events

class _OpenBoosterActivationWindow(W2CSchema):
    booster_id = Field(required=True, type=int)


class BoostersWindowWebApiMixin(object):

    @w2c(_OpenBoosterActivationWindow, 'booster_activation')
    def openBoosterActivationWindow(self, cmd):
        success = yield shared_events.showBoosterActivateDialog(cmd.booster_id)
        yield {'success': success}
