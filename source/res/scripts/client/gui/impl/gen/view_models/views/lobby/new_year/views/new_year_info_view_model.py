# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/new_year/views/new_year_info_view_model.py
from enum import IntEnum
from frameworks.wulf import ViewModel
from gui.impl.gen.view_models.common.region_model import RegionModel
from gui.impl.gen.view_models.views.lobby.new_year.components.video_cover_model import VideoCoverModel

class Tabs(IntEnum):
    DEFAULT = 0
    VEHICLES = 1


class NewYearInfoViewModel(ViewModel):
    __slots__ = ('onButtonClick', 'onSlideChanged')
    LEVELS = 'levels'
    STYLES = 'styles'
    SMALLBOXES = 'smallBoxes'
    BIGBOXES = 'bigBoxes'

    def __init__(self, properties=11, commands=2):
        super(NewYearInfoViewModel, self).__init__(properties=properties, commands=commands)

    @property
    def videoCover(self):
        return self._getViewModel(0)

    @staticmethod
    def getVideoCoverType():
        return VideoCoverModel

    @property
    def region(self):
        return self._getViewModel(1)

    @staticmethod
    def getRegionType():
        return RegionModel

    def getStartTab(self):
        return Tabs(self._getNumber(2))

    def setStartTab(self, value):
        self._setNumber(2, value.value)

    def getMaxBonus(self):
        return self._getReal(3)

    def setMaxBonus(self, value):
        self._setReal(3, value)

    def getUsualMaxBonus(self):
        return self._getReal(4)

    def setUsualMaxBonus(self, value):
        self._setReal(4, value)

    def getQuestsToGetExtraSlot(self):
        return self._getNumber(5)

    def setQuestsToGetExtraSlot(self, value):
        self._setNumber(5, value)

    def getMinMultiplier(self):
        return self._getReal(6)

    def setMinMultiplier(self, value):
        self._setReal(6, value)

    def getMaxMultiplier(self):
        return self._getReal(7)

    def setMaxMultiplier(self, value):
        self._setReal(7, value)

    def getIsLootBoxesBuyEnabled(self):
        return self._getBool(8)

    def setIsLootBoxesBuyEnabled(self, value):
        self._setBool(8, value)

    def getIsLootBoxEnabled(self):
        return self._getBool(9)

    def setIsLootBoxEnabled(self, value):
        self._setBool(9, value)

    def getHasSmallBoxes(self):
        return self._getBool(10)

    def setHasSmallBoxes(self, value):
        self._setBool(10, value)

    def _initialize(self):
        super(NewYearInfoViewModel, self)._initialize()
        self._addViewModelProperty('videoCover', VideoCoverModel())
        self._addViewModelProperty('region', RegionModel())
        self._addNumberProperty('startTab')
        self._addRealProperty('maxBonus', 0.0)
        self._addRealProperty('usualMaxBonus', 0.0)
        self._addNumberProperty('questsToGetExtraSlot', 0)
        self._addRealProperty('minMultiplier', 0.0)
        self._addRealProperty('maxMultiplier', 0.0)
        self._addBoolProperty('isLootBoxesBuyEnabled', False)
        self._addBoolProperty('isLootBoxEnabled', False)
        self._addBoolProperty('hasSmallBoxes', False)
        self.onButtonClick = self._addCommand('onButtonClick')
        self.onSlideChanged = self._addCommand('onSlideChanged')
