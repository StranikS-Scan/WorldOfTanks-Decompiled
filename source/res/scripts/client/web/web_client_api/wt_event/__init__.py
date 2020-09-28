# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/web/web_client_api/wt_event/__init__.py
from gui.shared import event_dispatcher
from web.web_client_api import w2capi, w2c, W2CSchema, Field

class _LootBoxOpenSchema(W2CSchema):
    category = Field(required=True, type=basestring)


@w2capi(name='wt2020', key='action')
class WtEventWebApi(object):

    @w2c(_LootBoxOpenSchema, 'open_loot_box_view')
    def openLootBoxView(self, cmd):
        event_dispatcher.showHangar()
        event_dispatcher.hideWebBrowserOverlay()
        event_dispatcher.showWtEventLootboxOpenWindow(boxType=cmd.category)
