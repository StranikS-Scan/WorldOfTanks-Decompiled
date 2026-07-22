# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/cgf_components/event_state_components.py
import CGF
from cgf_script.component_meta_class import registerComponent

@registerComponent
class EventStateEnabledComponent(object):
    domain = CGF.DomainOption.DomainClient | CGF.DomainOption.DomainEditor
    editorTitle = 'Event State Enabled'
    category = 'Event State'
