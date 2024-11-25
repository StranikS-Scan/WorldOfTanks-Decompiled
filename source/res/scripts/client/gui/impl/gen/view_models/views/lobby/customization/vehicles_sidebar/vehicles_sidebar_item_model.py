# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/customization/vehicles_sidebar/vehicles_sidebar_item_model.py
from frameworks.wulf import Array
from gui.impl.gen.view_models.views.lobby.common.vehicle_model import VehicleModel
from gui.impl.gen.view_models.views.lobby.customization.vehicles_sidebar.customization_3D_attachments import Customization3DAttachments

class VehiclesSidebarItemModel(VehicleModel):
    __slots__ = ()

    def __init__(self, properties=12, commands=0):
        super(VehiclesSidebarItemModel, self).__init__(properties=properties, commands=commands)

    def getInDepot(self):
        return self._getBool(9)

    def setInDepot(self, value):
        self._setBool(9, value)

    def getNationOrder(self):
        return self._getNumber(10)

    def setNationOrder(self, value):
        self._setNumber(10, value)

    def getCustomization3DAttachments(self):
        return self._getArray(11)

    def setCustomization3DAttachments(self, value):
        self._setArray(11, value)

    @staticmethod
    def getCustomization3DAttachmentsType():
        return Customization3DAttachments

    def _initialize(self):
        super(VehiclesSidebarItemModel, self)._initialize()
        self._addBoolProperty('inDepot', False)
        self._addNumberProperty('nationOrder', 1)
        self._addArrayProperty('customization3DAttachments', Array())
