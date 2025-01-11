# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/new_year/views/new_year_info_view_model.py
from frameworks.wulf import ViewModel
from gui.impl.gen.view_models.common.region_model import RegionModel
from gui.impl.gen.view_models.views.lobby.new_year.components.video_cover_model import VideoCoverModel

class NewYearInfoViewModel(ViewModel):
    __slots__ = ('onShowAboutEvent', 'onShowRewardKitBuyWindow')

    def __init__(self, properties=5, commands=2):
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

    def getEventStartDate(self):
        return self._getNumber(3)

    def setEventStartDate(self, value):
        self._setNumber(3, value)

    def getEventEndDate(self):
        return self._getNumber(4)

    def setEventEndDate(self, value):
        self._setNumber(4, value)

    def _initialize(self):
        super(NewYearInfoViewModel, self)._initialize()
        self._addViewModelProperty('videoCover', VideoCoverModel())
        self._addViewModelProperty('region', RegionModel())
        self._addBoolProperty('isExternalBuy', False)
        self._addNumberProperty('eventStartDate', 0)
        self._addNumberProperty('eventEndDate', 0)
        self.onShowAboutEvent = self._addCommand('onShowAboutEvent')
        self.onShowRewardKitBuyWindow = self._addCommand('onShowRewardKitBuyWindow')
