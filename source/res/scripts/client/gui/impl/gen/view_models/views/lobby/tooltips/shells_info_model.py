# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/tooltips/shells_info_model.py
from frameworks.wulf import Array
from frameworks.wulf import ViewModel
from gui.impl.gen.view_models.views.lobby.tooltips.shell_info_model import ShellInfoModel
from gui.impl.gen.view_models.views.lobby.tooltips.shells_specification_model import ShellsSpecificationModel

class ShellsInfoModel(ViewModel):
    __slots__ = ()

    def __init__(self, properties=6, commands=0):
        super(ShellsInfoModel, self).__init__(properties=properties, commands=commands)

    def getTitle(self):
        return self._getString(0)

    def setTitle(self, value):
        self._setString(0, value)

    def getShells(self):
        return self._getArray(1)

    def setShells(self, value):
        self._setArray(1, value)

    def getInstalledCount(self):
        return self._getNumber(2)

    def setInstalledCount(self, value):
        self._setNumber(2, value)

    def getMaxCount(self):
        return self._getNumber(3)

    def setMaxCount(self, value):
        self._setNumber(3, value)

    def getIsAutoRenewalEnabled(self):
        return self._getBool(4)

    def setIsAutoRenewalEnabled(self, value):
        self._setBool(4, value)

    def getSpecifications(self):
        return self._getArray(5)

    def setSpecifications(self, value):
        self._setArray(5, value)

    def _initialize(self):
        super(ShellsInfoModel, self)._initialize()
        self._addStringProperty('title', '')
        self._addArrayProperty('shells', Array())
        self._addNumberProperty('installedCount', 0)
        self._addNumberProperty('maxCount', 0)
        self._addBoolProperty('isAutoRenewalEnabled', False)
        self._addArrayProperty('specifications', Array())
