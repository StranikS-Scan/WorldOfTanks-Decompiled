# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/detachment/barrack_detachments_view_model.py
from frameworks.wulf import Array
from gui.impl.gen.view_models.views.lobby.detachment.common.auto_scroll_model import AutoScrollModel
from gui.impl.gen.view_models.views.lobby.detachment.common.detachment_card_model import DetachmentCardModel
from gui.impl.gen.view_models.views.lobby.detachment.common.filter_status_base_model import FilterStatusBaseModel
from gui.impl.gen.view_models.views.lobby.detachment.common.filters_model import FiltersModel
from gui.impl.gen.view_models.views.lobby.detachment.common.navigation_view_model import NavigationViewModel
from gui.impl.gen.view_models.views.lobby.detachment.common.popover_tracker_impl_model import PopoverTrackerImplModel
from gui.impl.gen.view_models.views.lobby.detachment.recruit_banner_model import RecruitBannerModel

class BarrackDetachmentsViewModel(NavigationViewModel):
    __slots__ = ('onDetachmentCardClick', 'onDetachmentDismissClick', 'onDetachmentRecoverClick', 'onBuyDormitoryBtnClick', 'onMobilizeClick')

    def __init__(self, properties=11, commands=8):
        super(BarrackDetachmentsViewModel, self).__init__(properties=properties, commands=commands)

    @property
    def filtersModel(self):
        return self._getViewModel(2)

    @property
    def dormRooms(self):
        return self._getViewModel(3)

    @property
    def autoScroll(self):
        return self._getViewModel(4)

    @property
    def bannerModel(self):
        return self._getViewModel(5)

    @property
    def popover(self):
        return self._getViewModel(6)

    def getIsBuyDormitoryEnable(self):
        return self._getBool(7)

    def setIsBuyDormitoryEnable(self, value):
        self._setBool(7, value)

    def getHasDormitoryDiscount(self):
        return self._getBool(8)

    def setHasDormitoryDiscount(self, value):
        self._setBool(8, value)

    def getDetachmentList(self):
        return self._getArray(9)

    def setDetachmentList(self, value):
        self._setArray(9, value)

    def getIsRecruitsTabEnabled(self):
        return self._getBool(10)

    def setIsRecruitsTabEnabled(self, value):
        self._setBool(10, value)

    def _initialize(self):
        super(BarrackDetachmentsViewModel, self)._initialize()
        self._addViewModelProperty('filtersModel', FiltersModel())
        self._addViewModelProperty('dormRooms', FilterStatusBaseModel())
        self._addViewModelProperty('autoScroll', AutoScrollModel())
        self._addViewModelProperty('bannerModel', RecruitBannerModel())
        self._addViewModelProperty('popover', PopoverTrackerImplModel())
        self._addBoolProperty('isBuyDormitoryEnable', False)
        self._addBoolProperty('hasDormitoryDiscount', False)
        self._addArrayProperty('detachmentList', Array())
        self._addBoolProperty('isRecruitsTabEnabled', False)
        self.onDetachmentCardClick = self._addCommand('onDetachmentCardClick')
        self.onDetachmentDismissClick = self._addCommand('onDetachmentDismissClick')
        self.onDetachmentRecoverClick = self._addCommand('onDetachmentRecoverClick')
        self.onBuyDormitoryBtnClick = self._addCommand('onBuyDormitoryBtnClick')
        self.onMobilizeClick = self._addCommand('onMobilizeClick')
