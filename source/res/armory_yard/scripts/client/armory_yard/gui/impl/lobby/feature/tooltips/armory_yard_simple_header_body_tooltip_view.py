# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: armory_yard/scripts/client/armory_yard/gui/impl/lobby/feature/tooltips/armory_yard_simple_header_body_tooltip_view.py
from frameworks.wulf import ViewSettings
from gui.impl.gen import R
from gui.impl.gen.view_models.windows.simple_tooltip_content_model import SimpleTooltipContentModel
from gui.impl.pub import ViewImpl

class ArmoryYardSimpleHeaderBodyTooltipView(ViewImpl):
    __slots__ = ('__header', '__body')

    def __init__(self, header, body):
        settings = ViewSettings(R.views.armory_yard.lobby.feature.tooltips.ArmoryYardSimpleTooltipView())
        settings.model = SimpleTooltipContentModel()
        self.__header = header
        self.__body = body or ''
        super(ArmoryYardSimpleHeaderBodyTooltipView, self).__init__(settings)

    @property
    def viewModel(self):
        return super(ArmoryYardSimpleHeaderBodyTooltipView, self).getViewModel()

    def _onLoading(self, *args, **kwargs):
        super(ArmoryYardSimpleHeaderBodyTooltipView, self)._onLoading(*args, **kwargs)
        with self.viewModel.transaction() as tx:
            tx.setHeader(self.__header)
            tx.setBody(self.__body)
