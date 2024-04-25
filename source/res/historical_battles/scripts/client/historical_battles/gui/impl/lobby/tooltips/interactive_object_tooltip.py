# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: historical_battles/scripts/client/historical_battles/gui/impl/lobby/tooltips/interactive_object_tooltip.py
from frameworks.wulf import ViewSettings
from gui.impl.gen import R
from gui.impl.pub import ViewImpl
from gui.impl.backport.backport_tooltip import DecoratedTooltipWindow
from gui.Scaleform.genConsts.TOOLTIPS_CONSTANTS import TOOLTIPS_CONSTANTS
from gui.shared.tooltips import ToolTipBaseData
from historical_battles.gui.impl.gen.view_models.views.lobby.tooltips.interactive_object_tooltip_model import InteractiveObjectTooltipModel

class InteractiveObjectTooltip(ViewImpl):

    def __init__(self, itemId):
        settings = ViewSettings(R.views.historical_battles.lobby.tooltips.InteractiveObjectTooltip())
        settings.model = InteractiveObjectTooltipModel()
        self.__itemId = itemId
        super(InteractiveObjectTooltip, self).__init__(settings)

    @property
    def viewModel(self):
        return super(InteractiveObjectTooltip, self).getViewModel()

    def _onLoading(self):
        super(InteractiveObjectTooltip, self)._onLoading()
        self.viewModel.setItemID(self.__itemId)


class HangarInteractiveObjectTooltipContentWindowData(ToolTipBaseData):

    def __init__(self, context):
        super(HangarInteractiveObjectTooltipContentWindowData, self).__init__(context, TOOLTIPS_CONSTANTS.HANGAR_INTERACTIVE_OBJECT)

    def getDisplayableData(self, itemId, *args, **kwargs):
        return DecoratedTooltipWindow(InteractiveObjectTooltip(itemId), useDecorator=False)
