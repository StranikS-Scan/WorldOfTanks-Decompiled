# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/new_year/views/new_year_info_view_model.py
from enum import Enum
from frameworks.wulf import ViewModel
from gui.impl.gen.view_models.common.region_model import RegionModel
from gui.impl.gen.view_models.views.lobby.new_year.components.video_cover_model import VideoCoverModel

class InformationCategory(Enum):
    RESOURCE = 'resource'
    MINING = 'mining'
    KIT = 'kit'


class NewYearInfoViewModel(ViewModel):
    __slots__ = ('onShowRewardKitStream', 'onShowAboutEvent', 'onShowRewardKitBuyWindow')

    def __init__(self, properties=3, commands=3):
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

    def getIsExternalBuy(self):
        return self._getBool(2)

    def setIsExternalBuy(self, value):
        self._setBool(2, value)

    def _initialize(self):
        super(NewYearInfoViewModel, self)._initialize()
        self._addViewModelProperty('videoCover', VideoCoverModel())
        self._addViewModelProperty('region', RegionModel())
        self._addBoolProperty('isExternalBuy', False)
        self.onShowRewardKitStream = self._addCommand('onShowRewardKitStream')
        self.onShowAboutEvent = self._addCommand('onShowAboutEvent')
        self.onShowRewardKitBuyWindow = self._addCommand('onShowRewardKitBuyWindow')
