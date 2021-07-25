# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/detachment/tooltips/list_category_tooltip.py
from frameworks.wulf import ViewSettings
from gui.impl.gen import R
from gui.impl.gen.view_models.views.lobby.detachment.tooltips.detachment_info_tooltip_model import DetachmentInfoTooltipModel
from gui.impl.gen.view_models.views.lobby.detachment.tooltips.list_category_tooltip_model import ListCategoryTooltipModel
from gui.impl.pub import ViewImpl
from uilogging.detachment.loggers import DynamicGroupTooltipLogger

class ListCategoryTooltip(ViewImpl):
    __slots__ = ('_grade',)
    uiLogger = DynamicGroupTooltipLogger()

    def __init__(self, _grade=None):
        settings = ViewSettings(R.views.lobby.detachment.tooltips.ListCategoryTooltip())
        settings.model = ListCategoryTooltipModel()
        super(ListCategoryTooltip, self).__init__(settings)
        self._grade = _grade

    @property
    def viewModel(self):
        return super(ListCategoryTooltip, self).getViewModel()

    def _initialize(self, *args, **kwargs):
        super(ListCategoryTooltip, self)._initialize()
        self.uiLogger.tooltipOpened()

    def _finalize(self):
        self.uiLogger.tooltipClosed(self.__class__.__name__)
        self.uiLogger.reset()
        super(ListCategoryTooltip, self)._finalize()

    def _onLoading(self):
        super(ListCategoryTooltip, self)._onLoading()
        with self.viewModel.transaction() as tx:
            tx.setGrade(self._grade)
