# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/common/tooltips/simple_icon_tooltip_view.py
from frameworks.wulf import ViewSettings
from gui.impl.gen.view_models.views.lobby.common.tooltips.simple_icon_tooltip_model import SimpleIconTooltipModel, HeaderType
from gui.impl.gen import R
from gui.impl.pub import ViewImpl

class SimpleIconTooltipView(ViewImpl):
    __slots__ = ('__header', '__body', '__icon', '__headerType')

    def __init__(self, header, body, icon, headerType):
        self.__header = header
        self.__body = body
        self.__icon = icon
        self.__headerType = headerType
        settings = ViewSettings(R.views.lobby.common.tooltips.SimpleIconTooltip(), model=SimpleIconTooltipModel())
        super(SimpleIconTooltipView, self).__init__(settings)

    @property
    def viewModel(self):
        return super(SimpleIconTooltipView, self).getViewModel()

    def _onLoading(self, *args, **kwargs):
        with self.viewModel.transaction() as tx:
            tx.setHeader(self.__header)
            tx.setBody(self.__body)
            tx.setIcon(self.__icon)
            tx.setHeaderType(HeaderType(self.__headerType))
