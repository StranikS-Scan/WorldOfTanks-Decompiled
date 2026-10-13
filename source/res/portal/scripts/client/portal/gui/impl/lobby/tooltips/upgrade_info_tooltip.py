# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: portal/scripts/client/portal/gui/impl/lobby/tooltips/upgrade_info_tooltip.py
from frameworks.wulf import ViewSettings
from portal.gui.impl.gen.view_models.views.lobby.tooltips.upgrade_info_tooltip_model import UpgradeInfoTooltipModel
from gui.impl.pub import ViewImpl
from gui.impl.gen import R

class UpgradeInfoTooltip(ViewImpl):
    __slots__ = ()

    def __init__(self):
        settings = ViewSettings(R.views.portal.lobby.tooltips.UpgradeInfoTooltip())
        settings.model = UpgradeInfoTooltipModel()
        super(UpgradeInfoTooltip, self).__init__(settings)

    @property
    def viewModel(self):
        return super(UpgradeInfoTooltip, self).getViewModel()
