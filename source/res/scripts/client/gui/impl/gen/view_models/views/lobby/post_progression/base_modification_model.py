# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/post_progression/base_modification_model.py
from gui.impl.gen import R
from frameworks.wulf import ViewModel

class BaseModificationModel(ViewModel):
    __slots__ = ()

    def __init__(self, properties=4, commands=0):
        super(BaseModificationModel, self).__init__(properties=properties, commands=commands)

    def getId(self):
        return self._getNumber(0)

    def setId(self, value):
        self._setNumber(0, value)

    def getImageResName(self):
        return self._getString(1)

    def setImageResName(self, value):
        self._setString(1, value)

    def getTitleRes(self):
        return self._getResource(2)

    def setTitleRes(self, value):
        self._setResource(2, value)

    def getTooltipContentId(self):
        return self._getNumber(3)

    def setTooltipContentId(self, value):
        self._setNumber(3, value)

    def _initialize(self):
        super(BaseModificationModel, self)._initialize()
        self._addNumberProperty('id', 0)
        self._addStringProperty('imageResName', '')
        self._addResourceProperty('titleRes', R.invalid())
        self._addNumberProperty('tooltipContentId', 0)
