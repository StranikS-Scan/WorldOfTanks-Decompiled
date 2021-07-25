# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/detachment/dialogs/restore_recruit_view_model.py
from gui.impl.gen.view_models.views.lobby.detachment.common.price_model import PriceModel
from gui.impl.gen.view_models.views.lobby.detachment.common.recruit_model import RecruitModel
from gui.impl.gen.view_models.windows.full_screen_dialog_window_model import FullScreenDialogWindowModel

class RestoreRecruitViewModel(FullScreenDialogWindowModel):
    __slots__ = ()

    def __init__(self, properties=15, commands=3):
        super(RestoreRecruitViewModel, self).__init__(properties=properties, commands=commands)

    @property
    def priceModel(self):
        return self._getViewModel(11)

    @property
    def recruitModel(self):
        return self._getViewModel(12)

    def getIsShowPrice(self):
        return self._getBool(13)

    def setIsShowPrice(self, value):
        self._setBool(13, value)

    def getTimeLeft(self):
        return self._getString(14)

    def setTimeLeft(self, value):
        self._setString(14, value)

    def _initialize(self):
        super(RestoreRecruitViewModel, self)._initialize()
        self._addViewModelProperty('priceModel', PriceModel())
        self._addViewModelProperty('recruitModel', RecruitModel())
        self._addBoolProperty('isShowPrice', False)
        self._addStringProperty('timeLeft', '')
