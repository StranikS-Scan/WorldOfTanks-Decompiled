# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/new_year/tooltips/ny_menu_gift_tooltip.py
from frameworks.wulf import ViewSettings
from gifts.gifts_common import GiftEventID
from gui.gift_system.constants import NY_STAMP_CODE
from gui.impl.gen.view_models.views.lobby.new_year.tooltips.ny_menu_gift_tooltip_model import NyMenuGiftTooltipModel
from gui.impl.pub import ViewImpl
from gui.impl.gen import R
from helpers import dependency
from skeletons.gui.game_control import IGiftSystemController

class NyMenuGiftTooltip(ViewImpl):
    __slots__ = ()
    __giftsController = dependency.descriptor(IGiftSystemController)

    def __init__(self):
        settings = ViewSettings(R.views.lobby.new_year.tooltips.NyMenuGiftTooltip(), model=NyMenuGiftTooltipModel())
        super(NyMenuGiftTooltip, self).__init__(settings)

    @property
    def viewModel(self):
        return super(NyMenuGiftTooltip, self).getViewModel()

    def _onLoading(self, *args, **kwargs):
        eventHub = self.__giftsController.getEventHub(GiftEventID.NY_HOLIDAYS)
        with self.viewModel.transaction() as model:
            model.setIsBalanceAllowed(eventHub.getStamper().isBalanceAvailable() if eventHub else False)
            model.setPostStampsCount(eventHub.getStamper().getStampCount(NY_STAMP_CODE) if eventHub else 0)
