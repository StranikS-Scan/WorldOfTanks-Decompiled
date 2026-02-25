# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: cosmic_event/scripts/client/cosmic_event_client_cgf/hangar_entry_point/managers.py
import CGF
import SoundGroups
from functools import partial
from helpers import dependency
from shared_utils import nextTick
from cgf_components.highlight_component import IsHighlighted
from cgf_components.hover_component import SelectionComponent
from cgf_script.managers_registrator import onAddedQuery, onRemovedQuery, autoregister
from cosmic_event_client_cgf.hangar_entry_point.components import Event3dEntryPointGoComponent, EventClickedComponent, EventNames

@autoregister(presentInAllWorlds=True, domain=CGF.DomainOption.DomainClient)
class EntryPoint3dClickManager(CGF.ComponentManager):

    def __init__(self):
        super(EntryPoint3dClickManager, self).__init__()
        self.__handlers = {}

    @onAddedQuery(CGF.GameObject, Event3dEntryPointGoComponent, SelectionComponent)
    def handleClickAdded(self, go, entryPoint, selection):
        eventName = entryPoint.eventName
        clickSound = entryPoint.click
        handler = partial(self.__handleClick, go, eventName, clickSound)
        selection.onClickAction += handler
        self.__handlers[go.id] = handler

    @onRemovedQuery(CGF.GameObject, Event3dEntryPointGoComponent, SelectionComponent)
    def handleClickRemoved(self, go, entryPoint, selection):
        handler = self.__handlers.pop(go.id, None)
        if handler is not None:
            selection.onClickAction -= handler
        return

    @onAddedQuery(IsHighlighted, Event3dEntryPointGoComponent)
    def onHoveredOn(self, _, entryPoint):
        if entryPoint.hoverOn:
            SoundGroups.g_instance.playSound2D(entryPoint.hoverOn)

    @onRemovedQuery(IsHighlighted, Event3dEntryPointGoComponent)
    def onHoveredOff(self, _, entryPoint):
        if entryPoint.hoverOff:
            SoundGroups.g_instance.playSound2D(entryPoint.hoverOff)

    def __handleClick(self, go, eventName, clickSound):
        comp = go.findComponentByType(EventClickedComponent)
        if comp is not None:
            go.removeComponent(comp)
        comp = go.createComponent(EventClickedComponent)
        comp.eventName = eventName
        if clickSound:
            SoundGroups.g_instance.playSound2D(clickSound)
        return


@autoregister(presentInAllWorlds=True, domain=CGF.DomainOption.DomainClient)
class Cosmic3dEntryPoint(CGF.ComponentManager):

    @onAddedQuery(CGF.GameObject, EventClickedComponent)
    def onCosmicClicked(self, go, clicked):
        if clicked.eventName == EventNames.COSMIC:
            from skeletons.gui.game_control import ICosmicEventBattleController
            ctrl = dependency.instance(ICosmicEventBattleController)
            nextTick(ctrl.switchPrb)()
            go.removeComponent(clicked)
