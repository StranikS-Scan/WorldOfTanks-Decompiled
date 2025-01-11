# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/paragons/presenters/about_presenter.py
import typing
from frameworks.wulf.view.submodel_presenter import SubModelPresenter
import logging
from gui.impl.gen.view_models.views.lobby.paragons.navigation_view_model import TabId
_logger = logging.getLogger(__name__)
if typing.TYPE_CHECKING:
    from frameworks.wulf import View, ViewModel

class AboutPresenter(SubModelPresenter):
    __slots__ = SubModelPresenter.__slots__ + ('__tooltipData',)

    def __init__(self, viewModel, parentView):
        super(AboutPresenter, self).__init__(viewModel, parentView)
        self.__viewModel = viewModel
        self.__tooltipData = {}

    def initialize(self, *args, **kwargs):
        super(AboutPresenter, self).initialize(*args, **kwargs)
        _logger.info('[Paragons]: about presenter inited')

    def finalize(self):
        super(AboutPresenter, self).finalize()
        _logger.info('[Paragons]: about presenter finalized')
        parentView = self.parentView
        if parentView is not None:
            childView = parentView.getChildView(TabId.ABOUT)
            if childView is not None:
                browser = childView.browser
                if browser is not None:
                    browser.refresh(True)
        return

    def createToolTipContent(self, event, contentID):
        return None

    def getTooltipData(self, event):
        tooltipId = event.getArgument('tooltipId')
        return None if tooltipId is None else self.__tooltipData.get(tooltipId)
