# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/web/web_client_api/ui/event.py
from helpers import dependency
from skeletons.gui.game_control import IGameEventController
from web.web_client_api import W2CSchema, w2c

class EventWebApiMixin(object):
    __gameEventController = dependency.descriptor(IGameEventController)

    @w2c(W2CSchema, 'event_hangar')
    def openEventHangar(self, _):
        self.__gameEventController.showEventHangar()

    @w2c(W2CSchema, 'event_meta_tab')
    def openEventMeta(self, _):
        self.__gameEventController.showEventMetaPage()
