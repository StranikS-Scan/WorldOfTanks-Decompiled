# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/tooltips/newbie_restrictions_tooltip.py
from frameworks.wulf import ViewSettings
from gui.impl.gen import R
from gui.impl.gen.view_models.views.lobby.tooltips.newbie_restrictions_tooltip_model import NewbieRestrictionsTooltipModel
from gui.impl.lobby.tooltips.newbie_restrictions_tooltip_adapters import NewbieRestrictionsTooltipAdapter
from gui.impl.pub import ViewImpl

class NewbieRestrictionsTooltip(ViewImpl):

    def __init__(self, adapter):
        settings = ViewSettings(R.views.lobby.tooltips.NewbieRestrictionsTooltip())
        settings.model = NewbieRestrictionsTooltipModel()
        super(NewbieRestrictionsTooltip, self).__init__(settings)
        self.__adapter = adapter

    @property
    def viewModel(self):
        return super(NewbieRestrictionsTooltip, self).getViewModel()

    def _onLoading(self, *args, **kwargs):
        super(NewbieRestrictionsTooltip, self)._onLoading(*args, **kwargs)
        self.__updateModel()

    def __updateModel(self):
        with self.viewModel.transaction() as model:
            self.__adapter.fillConditionGroups(model.getConditionGroups())
            self.__adapter.fillFooter(model)
