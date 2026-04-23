# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/customization/customization_carousel_seasons_model.py
from frameworks.wulf import Array
from frameworks.wulf import ViewModel
from gui.impl.gen.view_models.views.lobby.customization.customization_carousel_bookmark_model import CustomizationCarouselBookmarkModel

class CustomizationCarouselSeasonsModel(ViewModel):
    __slots__ = ()

    def __init__(self, properties=2, commands=0):
        super(CustomizationCarouselSeasonsModel, self).__init__(properties=properties, commands=commands)

    def getIsHidden(self):
        return self._getBool(0)

    def setIsHidden(self, value):
        self._setBool(0, value)

    def getSeasonsList(self):
        return self._getArray(1)

    def setSeasonsList(self, value):
        self._setArray(1, value)

    @staticmethod
    def getSeasonsListType():
        return CustomizationCarouselBookmarkModel

    def _initialize(self):
        super(CustomizationCarouselSeasonsModel, self)._initialize()
        self._addBoolProperty('isHidden', False)
        self._addArrayProperty('seasonsList', Array())
