# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/cgf_components/trigger_vse_component.py
import CGF
import Event
from GenericComponents import VSEComponent
from cgf_script.component_meta_class import ComponentProperty, CGFMetaTypes, registerComponent
from cgf_script.managers_registrator import autoregister, onAddedQuery, onRemovedQuery

@registerComponent
class TriggerVSEComponent(object):
    domain = CGF.DomainOption.DomainClient | CGF.DomainOption.DomainEditor
    eventName = ComponentProperty(type=CGFMetaTypes.STRING, editorName='event name', value='event')

    def __init__(self):
        super(TriggerVSEComponent, self).__init__()
        self.triggerEvent = Event.Event()


@autoregister(presentInAllWorlds=False, category='lobby')
class TriggerVSEComponentsManager(CGF.ComponentManager):

    @onAddedQuery(TriggerVSEComponent, VSEComponent)
    def handleComponentAdded(self, triggerVseComponent, vseComponent):
        self.doAction(triggerVseComponent.eventName)
        triggerVseComponent.triggerEvent += vseComponent.context.onTriggerEvent

    @onRemovedQuery(TriggerVSEComponent, VSEComponent)
    def handleComponentRemoved(self, triggerVseComponent, vseComponent):
        triggerVseComponent.triggerEvent -= vseComponent.context.onTriggerEvent
