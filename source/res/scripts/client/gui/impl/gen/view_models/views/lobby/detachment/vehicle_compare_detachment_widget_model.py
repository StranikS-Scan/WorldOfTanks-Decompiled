# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/detachment/vehicle_compare_detachment_widget_model.py
from frameworks.wulf import Array
from frameworks.wulf import ViewModel
from gui.impl.gen.view_models.views.lobby.detachment.common.perk_short_model import PerkShortModel

class VehicleCompareDetachmentWidgetModel(ViewModel):
    __slots__ = ('onEdit', 'onClear')

    def __init__(self, properties=4, commands=2):
        super(VehicleCompareDetachmentWidgetModel, self).__init__(properties=properties, commands=commands)

    def getPoints(self):
        return self._getNumber(0)

    def setPoints(self, value):
        self._setNumber(0, value)

    def getInstructorPoints(self):
        return self._getNumber(1)

    def setInstructorPoints(self, value):
        self._setNumber(1, value)

    def getIsInDevelopment(self):
        return self._getBool(2)

    def setIsInDevelopment(self, value):
        self._setBool(2, value)

    def getPerkList(self):
        return self._getArray(3)

    def setPerkList(self, value):
        self._setArray(3, value)

    def _initialize(self):
        super(VehicleCompareDetachmentWidgetModel, self)._initialize()
        self._addNumberProperty('points', 0)
        self._addNumberProperty('instructorPoints', 0)
        self._addBoolProperty('isInDevelopment', False)
        self._addArrayProperty('perkList', Array())
        self.onEdit = self._addCommand('onEdit')
        self.onClear = self._addCommand('onClear')
