# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/messengerBar/MessengerBar.py
from gui.Scaleform.daapi.view.meta.MessengerBarMeta import MessengerBarMeta
from gui.Scaleform.framework import ViewTypes, g_entitiesFactories
from gui.Scaleform.framework.managers.containers import POP_UP_CRITERIA
from gui.shared import events
from gui.shared.event_bus import EVENT_BUS_SCOPE
from messenger.gui.Scaleform.view import MESSENGER_VIEW_ALIAS

class MessengerBar(MessengerBarMeta):

    def __init__(self):
        super(MessengerBar, self).__init__()

    def channelButtonClick(self):
        if not self.__manageWindow(MESSENGER_VIEW_ALIAS.CHANNEL_MANAGEMENT_WINDOW):
            self.fireEvent(events.LoadViewEvent(MESSENGER_VIEW_ALIAS.CHANNEL_MANAGEMENT_WINDOW), scope=EVENT_BUS_SCOPE.LOBBY)

    def _populate(self):
        super(MessengerBar, self)._populate()
        self.as_setInitDataS({'channelsHtmlIcon': "<img src='img://gui/maps/icons/messenger/iconChannels.png' width='32' height='32'/>",
         'contactsHtmlIcon': "<img src='img://gui/maps/icons/messenger/iconContacts.png' width='16' height='32' vspace='-11'/>"})

    def contactsButtonClick(self):
        pass

    def __manageWindow(self, eventType):
        manager = self.app.containerManager
        window = manager.getView(ViewTypes.WINDOW, {POP_UP_CRITERIA.VIEW_ALIAS: g_entitiesFactories.getAliasByEvent(eventType)})
        result = window is not None
        if result:
            name = window.uniqueName
            isOnTop = manager.as_isOnTopS(ViewTypes.WINDOW, name)
            if not isOnTop:
                manager.as_bringToFrontS(ViewTypes.WINDOW, name)
            else:
                window.onWindowClose()
        return result
