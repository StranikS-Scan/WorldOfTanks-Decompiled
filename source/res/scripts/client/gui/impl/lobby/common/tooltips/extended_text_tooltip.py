# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/common/tooltips/extended_text_tooltip.py
from frameworks.wulf import ViewSettings
from gui.impl.gen import R
from gui.impl.gen.view_models.views.lobby.common.extended_text_tooltip_model import ExtendedTextTooltipModel
from gui.impl.pub import ViewImpl

class ExtendedTextTooltip(ViewImpl):
    __slots__ = ('__text', '__stringifyKwargs')

    def __init__(self, text, stringifyKwargs):
        settings = ViewSettings(R.views.lobby.common.tooltips.ExtendedTextTooltip())
        settings.model = ExtendedTextTooltipModel()
        self.__text = text
        self.__stringifyKwargs = stringifyKwargs
        super(ExtendedTextTooltip, self).__init__(settings)

    @property
    def viewModel(self):
        return super(ExtendedTextTooltip, self).getViewModel()

    def _onLoading(self, *args, **kwargs):
        with self.viewModel.transaction() as tx:
            tx.setText(self.__text)
            tx.setStringifyKwargs(self.__stringifyKwargs)
