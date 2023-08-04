# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/cgf_components/tooltip_component.py
import CGF
from cgf_components.hover_component import IsHoveredComponent
from cgf_script.component_meta_class import registerComponent, ComponentProperty, CGFMetaTypes
from cgf_script.managers_registrator import onAddedQuery, onRemovedQuery
from constants import IS_CLIENT
if IS_CLIENT:
    from gui.shared.events import LobbySimpleEvent
    from gui.shared import g_eventBus

@registerComponent
class TooltipComponent(object):
    domain = CGF.DomainOption.DomainClient
    editorTitle = 'Tooltip'
    category = 'Common'
    tooltip = ComponentProperty(type=CGFMetaTypes.STRING, editorName='selectionId')


class TooltipManager(CGF.ComponentManager):

    @onAddedQuery(IsHoveredComponent, TooltipComponent)
    def onTooltipAdded(self, _, tooltipComponent):
        g_eventBus.handleEvent(LobbySimpleEvent(LobbySimpleEvent.ENTITY_TOOLTIP_SHOW, ctx={'selectionId': tooltipComponent.tooltip}))

    @onRemovedQuery(IsHoveredComponent, TooltipComponent)
    def onTooltipRemoved(self, *_):
        g_eventBus.handleEvent(LobbySimpleEvent(LobbySimpleEvent.ENTITY_TOOLTIP_HIDE))
