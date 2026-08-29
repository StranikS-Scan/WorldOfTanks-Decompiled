# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: white_tiger/scripts/common/white_tiger_common/common_cgf/barrier/components.py
import CGF
from cgf_script.component_meta_class import registerComponent, registerReplicableComponent

@registerReplicableComponent
class WTBarrierComponent(object):
    editorTitle = 'WT Barrier'
    category = 'White Tiger'


@registerComponent
class WTBarrierHelperComponent(object):
    editorTitle = 'WT Barrier Helper'
    category = 'White Tiger'
    domain = CGF.DomainOption.DomainAll

    def __init__(self, avatarID):
        self.avatarID = avatarID


@registerComponent
class WTBarrierRotatorComponent(object):
    category = 'White Tiger'
    domain = CGF.DomainOption.DomainServer

    def __init__(self, settingDistance):
        self.settingDistance = settingDistance
