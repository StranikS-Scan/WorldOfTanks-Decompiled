# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/paragons/tooltips/reset_branch_tooltip.py
from frameworks.wulf import ViewSettings
from gui.impl.gen import R
from gui.impl.gen.view_models.views.lobby.paragons.tooltips.reset_branch_tooltip_model import ResetBranchTooltipModel
from gui.impl.pub import ViewImpl

class ResetBranchTooltip(ViewImpl):

    def __init__(self, *args, **kwargs):
        settings = ViewSettings(R.views.lobby.paragons.tooltips.ResetBranchTooltip())
        settings.model = ResetBranchTooltipModel()
        settings.args = args
        settings.kwargs = kwargs
        super(ResetBranchTooltip, self).__init__(settings)

    @property
    def viewModel(self):
        return super(ResetBranchTooltip, self).getViewModel()

    def _onLoading(self, *args, **kwargs):
        with self.viewModel.transaction() as tx:
            tx.setHeader(kwargs.get('header', ''))
            tx.setDescription(kwargs.get('description', ''))
            tx.setAdditionalDescription(kwargs.get('additionalDescription', ''))
