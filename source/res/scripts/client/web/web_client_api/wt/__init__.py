# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/web/web_client_api/wt/__init__.py
from typing import TYPE_CHECKING
from gui.impl.gen.view_models.views.lobby.wt_event.wt_event_portal_model import PortalType
from gui.shared.event_dispatcher import showEventPortalWindow
from web.web_client_api import w2c, w2capi, W2CSchema, WebCommandSchema
if TYPE_CHECKING:
    from web.web_client_api import Schema2Command

@w2capi(name='wt', key='action')
class WTWebApi(WebCommandSchema):

    @w2c(W2CSchema, 'show_event_storage_window')
    def goToEventPortalWindow(self, _):
        showEventPortalWindow(portalType=PortalType.BOSS)
