# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/hangar/event/event_items_for_tokens_adaptor.py
from gui.Scaleform.daapi import LobbySubView
from gui.Scaleform.framework.entities.inject_component_adaptor import InjectComponentAdaptor
from gui.Scaleform.daapi.view.lobby.hangar.event.event_items_for_tokens import EventItemsForTokensWindow
from gui.shared import EVENT_BUS_SCOPE, events

class EventItemsForTokensAdaptor(LobbySubView, InjectComponentAdaptor):

    def __init__(self, ctx=None):
        super(EventItemsForTokensAdaptor, self).__init__()

    def _populate(self):
        super(EventItemsForTokensAdaptor, self)._populate()
        self.fireEvent(events.HangarVehicleEvent(events.HangarVehicleEvent.HERO_TANK_MARKER, ctx={'isDisable': True}), EVENT_BUS_SCOPE.LOBBY)

    def _dispose(self):
        super(EventItemsForTokensAdaptor, self)._dispose()
        self.fireEvent(events.HangarVehicleEvent(events.HangarVehicleEvent.HERO_TANK_MARKER, ctx={'isDisable': False}), EVENT_BUS_SCOPE.LOBBY)

    def _makeInjectView(self):
        return EventItemsForTokensWindow()
