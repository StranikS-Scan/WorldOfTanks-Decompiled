# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: white_tiger/scripts/client/white_tiger/client_cgf/barrier/components.py
import CGF
from cgf_script.component_meta_class import ComponentProperty, CGFMetaTypes, registerComponent

@registerComponent
class WTBarrierEffectComponent(object):
    domain = CGF.DomainOption.DomainEditor | CGF.DomainOption.DomainClient
    category = 'White Tiger'
    editorTitle = 'WT Effect On Shot Component'
    effectPath = ComponentProperty(type=CGFMetaTypes.STRING, editorName='Effect Prefab', annotations={'path': '*.prefab'})


@registerComponent
class WTBarrierClientComponent(object):
    domain = CGF.DomainOption.DomainClient
    category = 'White Tiger'

    def __init__(self):
        self.isVisible = False


@registerComponent
class WTBarrierDynamicComponent(object):
    domain = CGF.DomainOption.DomainClient
    category = 'White Tiger'


@registerComponent
class WTBarrierStaticComponent(object):
    domain = CGF.DomainOption.DomainClient
    category = 'White Tiger'
