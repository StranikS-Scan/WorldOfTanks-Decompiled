# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/dialogs/sub_views/image_substitution_view_model.py
from gui.impl.gen import R
from frameworks.wulf import ViewModel

class ImageSubstitutionViewModel(ViewModel):
    __slots__ = ()

    def __init__(self, properties=6, commands=0):
        super(ImageSubstitutionViewModel, self).__init__(properties=properties, commands=commands)

    def getPath(self):
        return self._getResource(0)

    def setPath(self, value):
        self._setResource(0, value)

    def getPlaceholder(self):
        return self._getString(1)

    def setPlaceholder(self, value):
        self._setString(1, value)

    def getMarginTop(self):
        return self._getNumber(2)

    def setMarginTop(self, value):
        self._setNumber(2, value)

    def getMarginRight(self):
        return self._getNumber(3)

    def setMarginRight(self, value):
        self._setNumber(3, value)

    def getMarginBottom(self):
        return self._getNumber(4)

    def setMarginBottom(self, value):
        self._setNumber(4, value)

    def getMarginLeft(self):
        return self._getNumber(5)

    def setMarginLeft(self, value):
        self._setNumber(5, value)

    def _initialize(self):
        super(ImageSubstitutionViewModel, self)._initialize()
        self._addResourceProperty('path', R.invalid())
        self._addStringProperty('placeholder', '')
        self._addNumberProperty('marginTop', 0)
        self._addNumberProperty('marginRight', 0)
        self._addNumberProperty('marginBottom', 0)
        self._addNumberProperty('marginLeft', 0)
