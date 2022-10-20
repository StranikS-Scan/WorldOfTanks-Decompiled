# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: halloween/scripts/client/halloween/gui/impl/gen/view_models/views/lobby/slide_model.py
from frameworks.wulf import ViewModel

class SlideModel(ViewModel):
    __slots__ = ()

    def __init__(self, properties=4, commands=0):
        super(SlideModel, self).__init__(properties=properties, commands=commands)

    def getId(self):
        return self._getNumber(0)

    def setId(self, value):
        self._setNumber(0, value)

    def getIsSelected(self):
        return self._getBool(1)

    def setIsSelected(self, value):
        self._setBool(1, value)

    def getIsDisabled(self):
        return self._getBool(2)

    def setIsDisabled(self, value):
        self._setBool(2, value)

    def getIsNew(self):
        return self._getBool(3)

    def setIsNew(self, value):
        self._setBool(3, value)

    def _initialize(self):
        super(SlideModel, self)._initialize()
        self._addNumberProperty('id', 0)
        self._addBoolProperty('isSelected', False)
        self._addBoolProperty('isDisabled', False)
        self._addBoolProperty('isNew', False)
