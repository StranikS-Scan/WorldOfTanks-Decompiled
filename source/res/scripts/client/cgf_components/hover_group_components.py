# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/cgf_components/hover_group_components.py
import CGF
import SoundGroups
from cgf_script.component_meta_class import registerComponent, ComponentProperty, CGFMetaTypes
from cgf_script.managers_registrator import onAddedQuery, onRemovedQuery
from hover_component import IsHoveredComponent, HoverGroupTrackerComponent

@registerComponent
class HoverableComponent(object):
    domain = CGF.DomainOption.DomainClient | CGF.DomainOption.DomainEditor
    editorTitle = 'Hoverable'
    category = 'Common'
    groupTracker = ComponentProperty(type=CGFMetaTypes.LINK, editorName='Group tracker', value=HoverGroupTrackerComponent)


@registerComponent
class HoverSoundComponent(object):
    domain = CGF.DomainOption.DomainClient | CGF.DomainOption.DomainEditor
    editorTitle = 'Hover group sound'
    category = 'Common'
    hoverAddingSound = ComponentProperty(type=CGFMetaTypes.STRING, editorName='Hover adding sound', value='')
    hoverRemovingSound = ComponentProperty(type=CGFMetaTypes.STRING, editorName='Hover removing sound', value='')


class HoverGroupManager(CGF.ComponentManager):

    @onAddedQuery(IsHoveredComponent, HoverableComponent, CGF.GameObject, tickGroup='preInitGroup')
    def onHoverAdded(self, _, hoverableComponent, gameObject):
        if hoverableComponent.groupTracker:
            hoverableComponent.groupTracker().addHoveredGO(gameObject)

    @onRemovedQuery(IsHoveredComponent, HoverableComponent, CGF.GameObject)
    def onHoverRemoved(self, _, hoverableComponent, gameObject):
        if hoverableComponent.groupTracker:
            hoverableComponent.groupTracker().removeHoveredGO(gameObject)

    @onAddedQuery(IsHoveredComponent, HoverSoundComponent, CGF.GameObject)
    def onHoverSoundAdded(self, _, hoverSound, __):
        if hoverSound.hoverAddingSound:
            SoundGroups.g_instance.playSound2D(hoverSound.hoverAddingSound)

    @onRemovedQuery(IsHoveredComponent, HoverSoundComponent, CGF.GameObject)
    def onHoverSoundRemoved(self, _, hoverSound, __):
        if hoverSound.hoverRemovingSound:
            SoundGroups.g_instance.playSound2D(hoverSound.hoverRemovingSound)
