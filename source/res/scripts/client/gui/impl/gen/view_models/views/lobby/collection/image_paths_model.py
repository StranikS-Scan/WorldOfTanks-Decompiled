# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/collection/image_paths_model.py
from frameworks.wulf import ViewModel

class ImagePathsModel(ViewModel):
    __slots__ = ()

    def __init__(self, properties=5, commands=0):
        super(ImagePathsModel, self).__init__(properties=properties, commands=commands)

    def getExtraSmall(self):
        return self._getString(0)

    def setExtraSmall(self, value):
        self._setString(0, value)

    def getSmall(self):
        return self._getString(1)

    def setSmall(self, value):
        self._setString(1, value)

    def getMedium(self):
        return self._getString(2)

    def setMedium(self, value):
        self._setString(2, value)

    def getLarge(self):
        return self._getString(3)

    def setLarge(self, value):
        self._setString(3, value)

    def getExtraLarge(self):
        return self._getString(4)

    def setExtraLarge(self, value):
        self._setString(4, value)

    def _initialize(self):
        super(ImagePathsModel, self)._initialize()
        self._addStringProperty('extraSmall', '')
        self._addStringProperty('small', '')
        self._addStringProperty('medium', '')
        self._addStringProperty('large', '')
        self._addStringProperty('extraLarge', '')
