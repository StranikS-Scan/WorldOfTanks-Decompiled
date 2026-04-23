# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/customization/customization_carousel_model.py
from frameworks.wulf import Array
from frameworks.wulf import ViewModel
from gui.impl.gen.view_models.views.lobby.customization.customization_carousel_arrow_model import CustomizationCarouselArrowModel
from gui.impl.gen.view_models.views.lobby.customization.customization_carousel_bookmark_model import CustomizationCarouselBookmarkModel
from gui.impl.gen.view_models.views.lobby.customization.customization_carousel_item_model import CustomizationCarouselItemModel

class CustomizationCarouselModel(ViewModel):
    __slots__ = ()

    def __init__(self, properties=11, commands=0):
        super(CustomizationCarouselModel, self).__init__(properties=properties, commands=commands)

    def getIsProgressionDecalsBannerVisible(self):
        return self._getBool(0)

    def setIsProgressionDecalsBannerVisible(self, value):
        self._setBool(0, value)

    def getIsLeftAvailable(self):
        return self._getBool(1)

    def setIsLeftAvailable(self, value):
        self._setBool(1, value)

    def getIsCarouselArrowsHintVisible(self):
        return self._getBool(2)

    def setIsCarouselArrowsHintVisible(self, value):
        self._setBool(2, value)

    def getIsRightAvailable(self):
        return self._getBool(3)

    def setIsRightAvailable(self, value):
        self._setBool(3, value)

    def getTotalItemsCount(self):
        return self._getNumber(4)

    def setTotalItemsCount(self, value):
        self._setNumber(4, value)

    def getFilteredItemsCount(self):
        return self._getNumber(5)

    def setFilteredItemsCount(self, value):
        self._setNumber(5, value)

    def getShouldShowCounts(self):
        return self._getArray(6)

    def setShouldShowCounts(self, value):
        self._setArray(6, value)

    @staticmethod
    def getShouldShowCountsType():
        return int

    def getCarouselItemsList(self):
        return self._getArray(7)

    def setCarouselItemsList(self, value):
        self._setArray(7, value)

    @staticmethod
    def getCarouselItemsListType():
        return CustomizationCarouselItemModel

    def getBookmarksList(self):
        return self._getArray(8)

    def setBookmarksList(self, value):
        self._setArray(8, value)

    @staticmethod
    def getBookmarksListType():
        return CustomizationCarouselBookmarkModel

    def getArrowsList(self):
        return self._getArray(9)

    def setArrowsList(self, value):
        self._setArray(9, value)

    @staticmethod
    def getArrowsListType():
        return CustomizationCarouselArrowModel

    def getScrollStartItemId(self):
        return self._getNumber(10)

    def setScrollStartItemId(self, value):
        self._setNumber(10, value)

    def _initialize(self):
        super(CustomizationCarouselModel, self)._initialize()
        self._addBoolProperty('isProgressionDecalsBannerVisible', False)
        self._addBoolProperty('isLeftAvailable', False)
        self._addBoolProperty('isCarouselArrowsHintVisible', False)
        self._addBoolProperty('isRightAvailable', False)
        self._addNumberProperty('totalItemsCount', 0)
        self._addNumberProperty('filteredItemsCount', 0)
        self._addArrayProperty('shouldShowCounts', Array())
        self._addArrayProperty('carouselItemsList', Array())
        self._addArrayProperty('bookmarksList', Array())
        self._addArrayProperty('arrowsList', Array())
        self._addNumberProperty('scrollStartItemId', 0)
