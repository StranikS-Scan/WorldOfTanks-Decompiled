# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/customization/customization_carousel_bookmark_model.py
from frameworks.wulf import ViewModel

class CustomizationCarouselBookmarkModel(ViewModel):
    __slots__ = ()

    def __init__(self, properties=3, commands=0):
        super(CustomizationCarouselBookmarkModel, self).__init__(properties=properties, commands=commands)

    def getBookmarkIndex(self):
        return self._getNumber(0)

    def setBookmarkIndex(self, value):
        self._setNumber(0, value)

    def getBookmarkName(self):
        return self._getString(1)

    def setBookmarkName(self, value):
        self._setString(1, value)

    def getIsProgressive(self):
        return self._getBool(2)

    def setIsProgressive(self, value):
        self._setBool(2, value)

    def _initialize(self):
        super(CustomizationCarouselBookmarkModel, self)._initialize()
        self._addNumberProperty('bookmarkIndex', 0)
        self._addStringProperty('bookmarkName', '')
        self._addBoolProperty('isProgressive', False)
