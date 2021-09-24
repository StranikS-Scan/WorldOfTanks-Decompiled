# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/wt_event/wt_event_portal_awards_model.py
from frameworks.wulf import Array
from gui.impl.wrappers.user_list_model import UserListModel
from gui.impl.gen.view_models.views.lobby.wt_event.wt_bonus_model import WtBonusModel
from gui.impl.gen.view_models.views.lobby.wt_event.wt_event_guaranteed_award import WtEventGuaranteedAward
from gui.impl.gen.view_models.views.lobby.wt_event.wt_event_multiopen_renderer_model import WtEventMultiopenRendererModel
from gui.impl.gen.view_models.views.lobby.wt_event.wt_event_portal_awards_base_model import WtEventPortalAwardsBaseModel

class WtEventPortalAwardsModel(WtEventPortalAwardsBaseModel):
    __slots__ = ('onOpenMore', 'onAnimationEnded', 'onBackToPortal')

    def __init__(self, properties=11, commands=7):
        super(WtEventPortalAwardsModel, self).__init__(properties=properties, commands=commands)

    @property
    def rewards(self):
        return self._getViewModel(5)

    @property
    def guaranteedAward(self):
        return self._getViewModel(6)

    def getIsBossLootBox(self):
        return self._getBool(7)

    def setIsBossLootBox(self, value):
        self._setBool(7, value)

    def getOpenedBoxesCount(self):
        return self._getNumber(8)

    def setOpenedBoxesCount(self, value):
        self._setNumber(8, value)

    def getIsMultipleOpening(self):
        return self._getBool(9)

    def setIsMultipleOpening(self, value):
        self._setBool(9, value)

    def getMultiRewards(self):
        return self._getArray(10)

    def setMultiRewards(self, value):
        self._setArray(10, value)

    def _initialize(self):
        super(WtEventPortalAwardsModel, self)._initialize()
        self._addViewModelProperty('rewards', UserListModel())
        self._addViewModelProperty('guaranteedAward', WtEventGuaranteedAward())
        self._addBoolProperty('isBossLootBox', False)
        self._addNumberProperty('openedBoxesCount', 0)
        self._addBoolProperty('isMultipleOpening', False)
        self._addArrayProperty('multiRewards', Array())
        self.onOpenMore = self._addCommand('onOpenMore')
        self.onAnimationEnded = self._addCommand('onAnimationEnded')
        self.onBackToPortal = self._addCommand('onBackToPortal')
