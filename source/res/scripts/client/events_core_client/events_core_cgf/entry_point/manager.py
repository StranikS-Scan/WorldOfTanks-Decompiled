# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/events_core_client/events_core_cgf/entry_point/manager.py
from functools import partial
import CGF
from cgf_components.hover_component import SelectionComponent
from cgf_script.managers_registrator import autoregister, onAddedQuery, onRemovedQuery
from events_core_client.events_core_cgf.entry_point.component import EventClickedComponent, Event3dEntryPointGoComponent

@autoregister(presentInAllWorlds=True, domain=CGF.DomainOption.DomainClient)
class EntryPoint3dClickManager(CGF.ComponentManager):

    def __init__(self):
        super(EntryPoint3dClickManager, self).__init__()
        self.__handlers = {}

    @onAddedQuery(CGF.GameObject, Event3dEntryPointGoComponent, SelectionComponent)
    def handleClickAdded(self, go, entryPoint, selection):
        eventName = entryPoint.eventName
        handler = partial(self.__handleClick, go, eventName)
        selection.onClickAction += handler
        self.__handlers[go.id] = handler

    @onRemovedQuery(CGF.GameObject, Event3dEntryPointGoComponent, SelectionComponent)
    def handleClickRemoved(self, go, entryPoint, selection):
        handler = self.__handlers.pop(go.id, None)
        if handler is not None:
            selection.onClickAction -= handler
        return

    def __handleClick(self, go, eventName):
        comp = go.findComponentByType(EventClickedComponent)
        if comp is not None:
            go.removeComponent(comp)
        comp = go.createComponent(EventClickedComponent)
        comp.eventName = eventName
        return
