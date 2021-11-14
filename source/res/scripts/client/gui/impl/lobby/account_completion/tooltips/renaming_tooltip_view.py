# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/account_completion/tooltips/renaming_tooltip_view.py
from frameworks.wulf import ViewSettings
from gui.impl.gen import R
from gui.impl.gen.view_models.views.lobby.account_completion.tooltips.renaming_hangar_tooltip_model import RenamingHangarTooltipModel
from gui.impl.pub import ViewImpl

class DemoAccountRenamingTooltipView(ViewImpl):

    def __init__(self):
        settings = ViewSettings(R.views.lobby.account_completion.tooltips.RenamingHangarTooltip())
        settings.model = RenamingHangarTooltipModel()
        super(DemoAccountRenamingTooltipView, self).__init__(settings)

    def _onLoading(self, *args, **kwargs):
        with self.getViewModel().transaction() as model:
            self._fillModel(model)

    def _fillModel(self, model):
        model.setTitle(R.strings.tooltips.demoAccountRenamingHangar.title())
        model.setText(R.strings.tooltips.demoAccountRenamingHangar.text())
        model.setTextInner(R.strings.tooltips.demoAccountRenamingHangar.holder())
