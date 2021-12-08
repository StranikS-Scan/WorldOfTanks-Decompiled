# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/new_year/views/new_year_info_view_model.py
from enum import IntEnum
from frameworks.wulf import ViewModel
from gui.impl.gen.view_models.common.region_model import RegionModel
from gui.impl.gen.view_models.views.lobby.new_year.components.video_cover_model import VideoCoverModel

class GiftSystemState(IntEnum):
    ENABLED = 0
    SUSPENDED = 1
    DISABLED = 2


class Tabs(IntEnum):
    DEFAULT = 0
    VEHICLES = 1


class NewYearInfoViewModel(ViewModel):
    __slots__ = ('onButtonClick', 'onSlideChanged')
    LEVELS = 'levels'
    STYLES = 'styles'
    SMALLBOXES = 'smallBoxes'
    CELEBRITY = 'celebrity'
    BIGBOXES = 'bigBoxes'
    GUARANTEED_REWARDS = 'guaranteedRewards'
    STREAM_BOX = 'streamBox'
    GIFT = 'gift'

    def __init__(self, properties=14, commands=2):
        super(NewYearInfoViewModel, self).__init__(properties=properties, commands=commands)

    @property
    def videoCover(self):
        return self._getViewModel(0)

    @property
    def region(self):
        return self._getViewModel(1)

    def getGiftSystemState(self):
        return GiftSystemState(self._getNumber(2))

    def setGiftSystemState(self, value):
        self._setNumber(2, value.value)

    def getStartTab(self):
        return Tabs(self._getNumber(3))

    def setStartTab(self, value):
        self._setNumber(3, value.value)

    def getMaxBonus(self):
        return self._getReal(4)

    def setMaxBonus(self, value):
        self._setReal(4, value)

    def getUsualMaxBonus(self):
        return self._getReal(5)

    def setUsualMaxBonus(self, value):
        self._setReal(5, value)

    def getSingleMegaBonus(self):
        return self._getReal(6)

    def setSingleMegaBonus(self, value):
        self._setReal(6, value)

    def getMaxMegaBonus(self):
        return self._getReal(7)

    def setMaxMegaBonus(self, value):
        self._setReal(7, value)

    def getQuestsToGetExtraSlot(self):
        return self._getNumber(8)

    def setQuestsToGetExtraSlot(self, value):
        self._setNumber(8, value)

    def getQuestsToGetCommander(self):
        return self._getNumber(9)

    def setQuestsToGetCommander(self, value):
        self._setNumber(9, value)

    def getMinMultiplier(self):
        return self._getReal(10)

    def setMinMultiplier(self, value):
        self._setReal(10, value)

    def getMaxMultiplier(self):
        return self._getReal(11)

    def setMaxMultiplier(self, value):
        self._setReal(11, value)

    def getIsExternalBuyBox(self):
        return self._getBool(12)

    def setIsExternalBuyBox(self, value):
        self._setBool(12, value)

    def getIsLootBoxEnabled(self):
        return self._getBool(13)

    def setIsLootBoxEnabled(self, value):
        self._setBool(13, value)

    def _initialize(self):
        super(NewYearInfoViewModel, self)._initialize()
        self._addViewModelProperty('videoCover', VideoCoverModel())
        self._addViewModelProperty('region', RegionModel())
        self._addNumberProperty('giftSystemState')
        self._addNumberProperty('startTab')
        self._addRealProperty('maxBonus', 0.0)
        self._addRealProperty('usualMaxBonus', 0.0)
        self._addRealProperty('singleMegaBonus', 0.0)
        self._addRealProperty('maxMegaBonus', 0.0)
        self._addNumberProperty('questsToGetExtraSlot', 0)
        self._addNumberProperty('questsToGetCommander', 0)
        self._addRealProperty('minMultiplier', 0.0)
        self._addRealProperty('maxMultiplier', 0.0)
        self._addBoolProperty('isExternalBuyBox', False)
        self._addBoolProperty('isLootBoxEnabled', False)
        self.onButtonClick = self._addCommand('onButtonClick')
        self.onSlideChanged = self._addCommand('onSlideChanged')
