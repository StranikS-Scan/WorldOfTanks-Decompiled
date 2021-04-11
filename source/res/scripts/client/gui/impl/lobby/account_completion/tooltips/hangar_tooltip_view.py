# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/account_completion/tooltips/hangar_tooltip_view.py
from frameworks.wulf import ViewSettings
from gui.impl.gen import R
from gui.impl.lobby.account_completion.common import fillRewards
from gui.impl.pub import ViewImpl
from gui.impl.gen.view_models.views.lobby.account_completion.tooltips.hangar_tooltip_model import HangarTooltipModel

class HangarTooltipView(ViewImpl):

    def __init__(self, email):
        settings = ViewSettings(R.views.lobby.account_completion.tooltips.HangarTooltip())
        settings.model = HangarTooltipModel()
        super(HangarTooltipView, self).__init__(settings)
        self.__email = email

    def _onLoading(self, *args, **kwargs):
        with self.getViewModel().transaction() as model:
            self._fillModel(model)

    def _fillModel(self, model):
        if self.__email:
            model.setTitle(R.strings.tooltips.accountCompletionHangar.email.title())
            model.setText(R.strings.tooltips.accountCompletionHangar.email.text())
            model.setEmail(self.__email)
        else:
            model.setTitle(R.strings.tooltips.accountCompletionHangar.title())
            model.setText(R.strings.tooltips.accountCompletionHangar.text())
            model.setTextInner(R.strings.tooltips.accountCompletionHangar.holder())
        fillRewards(model)
