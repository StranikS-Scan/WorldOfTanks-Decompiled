# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/tank_setup/dialogs/sub_views/frontline_confirm_icons_model.py
from frameworks.wulf import Array
from frameworks.wulf import ViewModel

class FrontlineConfirmIconsModel(ViewModel):
    __slots__ = ()

    def __init__(self, properties=2, commands=0):
        super(FrontlineConfirmIconsModel, self).__init__(properties=properties, commands=commands)

    def getIcons(self):
        return self._getArray(0)

    def setIcons(self, value):
        self._setArray(0, value)

    @staticmethod
    def getIconsType():
        return unicode

    def getIsExtendedHeight(self):
        return self._getBool(1)

    def setIsExtendedHeight(self, value):
        self._setBool(1, value)

    def _initialize(self):
        super(FrontlineConfirmIconsModel, self)._initialize()
        self._addArrayProperty('icons', Array())
        self._addBoolProperty('isExtendedHeight', False)
