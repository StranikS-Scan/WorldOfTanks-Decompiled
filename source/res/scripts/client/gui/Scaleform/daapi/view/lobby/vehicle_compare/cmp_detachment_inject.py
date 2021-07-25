# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/vehicle_compare/cmp_detachment_inject.py
from gui.Scaleform.framework.entities.inject_component_adaptor import InjectComponentAdaptor
from gui.impl.lobby.vehicle_compare.detachment import CompareDetachmentView

class VehicleDetachmentConfiguratorInject(InjectComponentAdaptor):

    def _makeInjectView(self):
        return CompareDetachmentView()
