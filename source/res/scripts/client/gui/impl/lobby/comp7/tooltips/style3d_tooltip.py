# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/comp7/tooltips/style3d_tooltip.py
from frameworks.wulf import ViewSettings
from gui.Scaleform.daapi.view.lobby.customization.shared import getSuitableText
from gui.impl.gen import R
from gui.impl.gen.view_models.views.lobby.comp7.tooltips.style3d_tooltip_model import Style3dTooltipModel
from gui.impl.pub import ViewImpl
from gui.shared.gui_items import GUI_ITEM_TYPE
from helpers import dependency
from skeletons.gui.customization import ICustomizationService

class Style3dTooltip(ViewImpl):
    __slots__ = ()
    __c11nService = dependency.descriptor(ICustomizationService)

    def __init__(self, styleId, vehiclesStr=None, layoutID=R.views.lobby.comp7.tooltips.Style3dTooltip()):
        settings = ViewSettings(layoutID)
        settings.model = Style3dTooltipModel()
        settings.args = [styleId, vehiclesStr]
        super(Style3dTooltip, self).__init__(settings)

    @property
    def viewModel(self):
        return super(Style3dTooltip, self).getViewModel()

    def _onLoading(self, styleId, vehiclesStr, **kwargs):
        with self.viewModel.transaction() as model:
            model.setStyleId(styleId)
            if vehiclesStr is None:
                customizationItem = self.__c11nService.getItemByID(GUI_ITEM_TYPE.STYLE, styleId)
                vehiclesStr = getSuitableText(customizationItem, formatVehicle=False)
            model.setVehicles(vehiclesStr)
        return
