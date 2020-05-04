# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/secret_event/general_tooltip_list_item_model.py
from gui.impl.gen import R
from frameworks.wulf import ViewModel

class GeneralTooltipListItemModel(ViewModel):
    __slots__ = ()

    def __init__(self, properties=5, commands=0):
        super(GeneralTooltipListItemModel, self).__init__(properties=properties, commands=commands)

    def getText(self):
        return self._getString(0)

    def setText(self, value):
        self._setString(0, value)

    def getLevel(self):
        return self._getNumber(1)

    def setLevel(self, value):
        self._setNumber(1, value)

    def getIcon(self):
        return self._getResource(2)

    def setIcon(self, value):
        self._setResource(2, value)

    def getIsLocked(self):
        return self._getBool(3)

    def setIsLocked(self, value):
        self._setBool(3, value)

    def getIsDisabled(self):
        return self._getBool(4)

    def setIsDisabled(self, value):
        self._setBool(4, value)

    def _initialize(self):
        super(GeneralTooltipListItemModel, self)._initialize()
        self._addStringProperty('text', '')
        self._addNumberProperty('level', 0)
        self._addResourceProperty('icon', R.invalid())
        self._addBoolProperty('isLocked', False)
        self._addBoolProperty('isDisabled', False)
