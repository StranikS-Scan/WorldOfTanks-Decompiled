# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: new_year/scripts/client/new_year/gui/impl/lobby/new_year/tooltips/ny_common_tooltip.py
from frameworks.wulf import ViewSettings
from new_year.gui.impl.gen.view_models.views.lobby.new_year.tooltips.common_tooltip_model import CommonTooltipModel
from gui.impl.gen import R
from gui.impl.pub import ViewImpl

def getCommonTooltipArgsFromEvent(event):
    header = event.getArgument('header') or ''
    description = event.getArgument('description') or ''
    additionalDescription = event.getArgument('additionalDescription') or ''
    return (header, description, additionalDescription)


class NyCommonTooltip(ViewImpl):
    __slots__ = ()

    def __init__(self, *args, **kwargs):
        settings = ViewSettings(R.views.new_year.lobby.new_year.tooltips.CommonTooltip())
        settings.model = CommonTooltipModel()
        settings.args = args
        settings.kwargs = kwargs
        super(NyCommonTooltip, self).__init__(settings)

    @property
    def viewModel(self):
        return super(NyCommonTooltip, self).getViewModel()

    def _onLoading(self, header, description, additionalDescription, *args, **kwargs):
        super(NyCommonTooltip, self)._onLoading(args, kwargs)
        with self.viewModel.transaction() as model:
            model.setHeader(header)
            model.setDescription(description)
            model.setAdditionalDescription(additionalDescription)
