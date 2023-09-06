# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/collection/collection_item_preview_model.py
from enum import Enum
from frameworks.wulf import Array
from frameworks.wulf import ViewModel
from gui.impl.gen.view_models.common.vehicle_info_model import VehicleInfoModel
from gui.impl.gen.view_models.views.lobby.collection.pages_blurred_background_model import PagesBlurredBackgroundModel

class ItemType(Enum):
    PHOTO = 'photo'
    NOTE = 'note'
    TANKMAN = 'tankman'
    MEDAL = 'medal'
    STYLE2D = 'style2d'
    STYLE3D = 'style3d'
    OTHERCUSTOMIZATION = 'otherCustomization'


class CollectionItemPreviewModel(ViewModel):
    __slots__ = ('onClosePreview', 'onOpenPreview')

    def __init__(self, properties=10, commands=2):
        super(CollectionItemPreviewModel, self).__init__(properties=properties, commands=commands)

    @property
    def vehicleInfo(self):
        return self._getViewModel(0)

    @staticmethod
    def getVehicleInfoType():
        return VehicleInfoModel

    def getName(self):
        return self._getString(1)

    def setName(self, value):
        self._setString(1, value)

    def getType(self):
        return ItemType(self._getString(2))

    def setType(self, value):
        self._setString(2, value.value)

    def getDescription(self):
        return self._getString(3)

    def setDescription(self, value):
        self._setString(3, value)

    def getSmallImage(self):
        return self._getString(4)

    def setSmallImage(self, value):
        self._setString(4, value)

    def getMediumImage(self):
        return self._getString(5)

    def setMediumImage(self, value):
        self._setString(5, value)

    def getLargeImage(self):
        return self._getString(6)

    def setLargeImage(self, value):
        self._setString(6, value)

    def getCurrentCollection(self):
        return self._getString(7)

    def setCurrentCollection(self, value):
        self._setString(7, value)

    def getPage(self):
        return self._getNumber(8)

    def setPage(self, value):
        self._setNumber(8, value)

    def getPagesBlurredBackgrounds(self):
        return self._getArray(9)

    def setPagesBlurredBackgrounds(self, value):
        self._setArray(9, value)

    @staticmethod
    def getPagesBlurredBackgroundsType():
        return PagesBlurredBackgroundModel

    def _initialize(self):
        super(CollectionItemPreviewModel, self)._initialize()
        self._addViewModelProperty('vehicleInfo', VehicleInfoModel())
        self._addStringProperty('name', '')
        self._addStringProperty('type')
        self._addStringProperty('description', '')
        self._addStringProperty('smallImage', '')
        self._addStringProperty('mediumImage', '')
        self._addStringProperty('largeImage', '')
        self._addStringProperty('currentCollection', 'defaultConfig')
        self._addNumberProperty('page', 0)
        self._addArrayProperty('pagesBlurredBackgrounds', Array())
        self.onClosePreview = self._addCommand('onClosePreview')
        self.onOpenPreview = self._addCommand('onOpenPreview')
