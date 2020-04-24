# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/web/web_client_api/ui/ten_years_event.py
from gui.shared.event_dispatcher import showTenYearsCountdownOverlay
from web.web_client_api import w2c, W2CSchema, Field

class _OpenTenYearsEventHubSchema(W2CSchema):
    path = Field(required=False, type=basestring, default=None)


class OpenTenYearsEventHubWebApiMixin(object):

    @w2c(_OpenTenYearsEventHubSchema, 'ten_years_event_hub')
    def tenYearsEventHub(self, cmd):
        showTenYearsCountdownOverlay(path=cmd.path)
