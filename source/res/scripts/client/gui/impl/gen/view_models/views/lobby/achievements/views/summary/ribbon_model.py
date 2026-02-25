# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/achievements/views/summary/ribbon_model.py
from frameworks.wulf import ViewModel
from gui.impl.gen import R

class RibbonModel(ViewModel):
    __slots__ = ()

    def __init__(self, properties=3, commands=0):
        super(RibbonModel, self).__init__(properties=properties, commands=commands)

    def getSlug(self):
        return self._getString(0)

    def setSlug(self, value):
        self._setString(0, value)

    def getImage(self):
        return self._getResource(1)

    def setImage(self, value):
        self._setResource(1, value)

    def getIcon(self):
        return self._getResource(2)

    def setIcon(self, value):
        self._setResource(2, value)

    def _initialize(self):
        super(RibbonModel, self)._initialize()
        self._addStringProperty('slug', '')
        self._addResourceProperty('image', R.invalid())
        self._addResourceProperty('icon', R.invalid())
