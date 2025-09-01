# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/lootbox_system/base/tooltips/box_tooltip.py
from frameworks.wulf import ViewSettings
from gui.impl.gen import R
from gui.impl.gen.view_models.views.lobby.lootbox_system.tooltips.box_compensation_tooltip_model import BoxCompensationTooltipModel
from gui.impl.gen.view_models.views.lobby.lootbox_system.tooltips.box_tooltip_model import BoxTooltipModel
from gui.impl.pub import ViewImpl
from helpers import dependency
from skeletons.gui.game_control import ILootBoxSystemController

class BoxTooltipBase(ViewImpl):
    __slots__ = ('__boxCategory', '__eventName')
    __lootBoxes = dependency.descriptor(ILootBoxSystemController)

    def __init__(self, boxCategory, eventName, layoutID, model):
        settings = ViewSettings(layoutID)
        settings.model = model
        super(BoxTooltipBase, self).__init__(settings)
        self.__boxCategory = boxCategory
        self.__eventName = eventName

    @property
    def viewModel(self):
        return super(BoxTooltipBase, self).getViewModel()

    def _onLoading(self, *args, **kwargs):
        super(BoxTooltipBase, self)._onLoading(*args, **kwargs)
        with self.viewModel.transaction() as vmTx:
            vmTx.setEventName(self.__eventName)
            vmTx.setBoxesCountToGuaranteed(self.__lootBoxes.getBoxesCountToGuaranteed(self.__boxCategory))
            vmTx.setBoxCategory(self.__boxCategory)


class BoxTooltip(BoxTooltipBase):

    def __init__(self, boxCategory, eventName):
        super(BoxTooltip, self).__init__(boxCategory, eventName, R.views.mono.lootbox.tooltips.box_tooltip(), BoxTooltipModel())


class BoxCompensationTooltip(BoxTooltipBase):

    def __init__(self, boxCategory, eventName):
        super(BoxCompensationTooltip, self).__init__(boxCategory, eventName, R.views.mono.lootbox.tooltips.box_compensation(), BoxCompensationTooltipModel())
