# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/cgf_components/view_components.py
import CGF
from cgf_script.component_meta_class import registerComponent, ComponentProperty, CGFMetaTypes
from gui.impl.gen import R

@registerComponent
class ViewComponent(object):
    domain = CGF.DomainOption.DomainClient
    layoutID = ComponentProperty(type=CGFMetaTypes.INT, value=R.invalid())
    uniqueID = ComponentProperty(type=CGFMetaTypes.INT, value=0)
    active = ComponentProperty(type=CGFMetaTypes.BOOL, value=True)

    def __init__(self, view):
        super(ViewComponent, self).__init__()
        self.layoutID = view.layoutID
        self.uniqueID = view.uniqueID
        self.view = view
