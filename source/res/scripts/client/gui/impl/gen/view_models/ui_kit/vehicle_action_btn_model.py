# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/ui_kit/vehicle_action_btn_model.py
from frameworks.wulf import Resource
from frameworks.wulf import ViewModel

class VehicleActionBtnModel(ViewModel):
    __slots__ = ()

    def getImage(self):
        return self._getResource(0)

    def setImage(self, value):
        self._setResource(0, value)

    def getText(self):
        return self._getString(1)

    def setText(self, value):
        self._setString(1, value)

    def getVisible(self):
        return self._getBool(2)

    def setVisible(self, value):
        self._setBool(2, value)

    def _initialize(self):
        super(VehicleActionBtnModel, self)._initialize()
        self._addResourceProperty('image', Resource.INVALID)
        self._addStringProperty('text', '')
        self._addBoolProperty('visible', False)
