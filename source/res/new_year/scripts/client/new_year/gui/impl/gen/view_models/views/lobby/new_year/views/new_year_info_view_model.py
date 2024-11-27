# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: new_year/scripts/client/new_year/gui/impl/gen/view_models/views/lobby/new_year/views/new_year_info_view_model.py
from enum import IntEnum
from frameworks.wulf import ViewModel
from new_year.gui.impl.gen.view_models.common.region_model import RegionModel
from new_year.gui.impl.gen.view_models.views.lobby.new_year.components.video_cover_model import VideoCoverModel

class Tabs(IntEnum):
    DEFAULT = 0
    VEHICLES = 1


class NewYearInfoViewModel(ViewModel):
    __slots__ = ('onButtonClick', 'onSlideChanged')
    LEVELS = 'levels'
    STYLES = 'styles'
    SMALLBOXES = 'smallBoxes'
    BIGBOXES = 'bigBoxes'
    GUARANTEED_REWARDS = 'guaranteedRewards'
    STREAM_BOX = 'streamBox'
    PET = 'pet'
    SURPRISE_MACHINE = 'surprise_machine'
    QUESTS = 'quests'
    REWARDS = 'rewards'

    def __init__(self, properties=13, commands=2):
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

    def getStartDate(self):
        return self._getNumber(3)

    def setStartDate(self, value):
        self._setNumber(3, value)

    def getEndDate(self):
        return self._getNumber(4)

    def setEndDate(self, value):
        self._setNumber(4, value)

    def getMaxBonus(self):
        return self._getReal(5)

    def setMaxBonus(self, value):
        self._setReal(5, value)

    def getUsualMaxBonus(self):
        return self._getReal(6)

    def setUsualMaxBonus(self, value):
        self._setReal(6, value)

    def getQuestsToGetExtraSlot(self):
        return self._getNumber(7)

    def setQuestsToGetExtraSlot(self, value):
        self._setNumber(7, value)

    def getMinMultiplier(self):
        return self._getReal(8)

    def setMinMultiplier(self, value):
        self._setReal(8, value)

    def getMaxMultiplier(self):
        return self._getReal(9)

    def setMaxMultiplier(self, value):
        self._setReal(9, value)

    def getIsLootBoxesBuyEnabled(self):
        return self._getBool(10)

    def setIsLootBoxesBuyEnabled(self, value):
        self._setBool(10, value)

    def getIsLootBoxEnabled(self):
        return self._getBool(11)

    def setIsLootBoxEnabled(self, value):
        self._setBool(11, value)

    def getHasSmallBoxes(self):
        return self._getBool(12)

    def setHasSmallBoxes(self, value):
        self._setBool(12, value)

    def _initialize(self):
        super(NewYearInfoViewModel, self)._initialize()
        self._addViewModelProperty('videoCover', VideoCoverModel())
        self._addViewModelProperty('region', RegionModel())
        self._addNumberProperty('startTab')
        self._addNumberProperty('startDate', 0)
        self._addNumberProperty('endDate', 0)
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
