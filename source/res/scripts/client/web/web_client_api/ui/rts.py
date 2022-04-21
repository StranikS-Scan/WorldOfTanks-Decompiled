# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/web/web_client_api/ui/rts.py
from web.web_client_api import w2c, W2CSchema
from gui.shared import event_dispatcher as shared_events

class RtsMetaViewsWebApiMixin(object):

    @w2c(W2CSchema, 'rts_collection')
    def openRTSCollectionView(self, _):
        shared_events.showRTSMetaRootWindow()
