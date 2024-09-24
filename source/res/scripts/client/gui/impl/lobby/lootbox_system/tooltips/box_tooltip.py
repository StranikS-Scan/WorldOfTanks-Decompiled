# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/lootbox_system/tooltips/box_tooltip.py
from frameworks.wulf import ViewSettings
from gui.impl.gen import R
from gui.impl.gen.view_models.views.lobby.lootbox_system.tooltips.box_tooltip_model import BoxTooltipModel
from gui.impl.pub import ViewImpl
from helpers import dependency
from skeletons.gui.game_control import ILootBoxSystemController

class BoxTooltip(ViewImpl):
    __slots__ = ('__boxCategory',)
    __lootBoxes = dependency.descriptor(ILootBoxSystemController)

    def __init__(self, boxCategory):
        settings = ViewSettings(R.views.lobby.lootbox_system.tooltips.BoxTooltip())
        settings.model = BoxTooltipModel()
        super(BoxTooltip, self).__init__(settings)
        self.__boxCategory = boxCategory

    @property
    def viewModel(self):
        return super(BoxTooltip, self).getViewModel()

    def _onLoading(self, *args, **kwargs):
        super(BoxTooltip, self)._onLoading(*args, **kwargs)
        with self.viewModel.transaction() as vmTx:
            vmTx.setEventName(self.__lootBoxes.eventName)
            vmTx.setBoxesCountToGuaranteed(self.__lootBoxes.getBoxesCountToGuaranteed(self.__boxCategory))
            vmTx.setBoxCategory(self.__boxCategory)
